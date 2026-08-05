import pytest
from ai_api.agents.exceptions import ToolExecutionError
from ai_api.agents.tool_executor import ToolExecutionService
from ai_api.security.audit_logs import AuditLogService
from ai_api.security.blocked_tool_call_telemetry import (
    BlockedToolCallTelemetryService,
)


def test_tool_execution_should_record_audit_event_when_authorization_blocks_tool() -> None:
    audit_log_service = AuditLogService()
    blocked_tool_call_telemetry_service = BlockedToolCallTelemetryService()

    service = ToolExecutionService(
        audit_log_service=audit_log_service,
        blocked_tool_call_telemetry_service=blocked_tool_call_telemetry_service,
    )

    with pytest.raises(
        ToolExecutionError,
        match="Tool execution blocked by authorization policy",
    ):
        service.execute(
            tool_name="requirements.analyze",
            arguments={
                "requirement_text": "The user should be able to login.",
                "language": "en",
            },
            metadata={
                "caller_type": "future_admin_user",
                "environment": "local",
                "run_id": "run-001",
                "trace_id": "trace-001",
                "request_id": "request-001",
            },
        )

    audit_response = audit_log_service.list_events(
        event_type="tool_authorization_blocked",
    )

    assert audit_response.count == 1

    event = audit_response.events[0]

    assert event.event_type == "tool_authorization_blocked"
    assert event.status == "blocked"
    assert event.severity in {"warning", "high", "critical"}
    assert event.component == "tool_execution_service"
    assert event.operation == "execute_tool"
    assert event.environment == "local"
    assert event.actor.actor_type == "backend_service"
    assert event.actor.actor_id == "tool-execution-service"
    assert event.caller.caller_type == "future_admin_user"
    assert event.target.target_type == "tool"
    assert event.target.target_id == "requirements.analyze"
    assert event.target.target_name == "requirements.analyze"
    assert event.run_context.run_id == "run-001"
    assert event.run_context.trace_id == "trace-001"
    assert event.run_context.request_id == "request-001"
    assert event.policy.policy_name == "tool-authorization-policy-v1"
    assert event.policy.decision == "blocked"
    assert event.policy.violations
    assert event.risk.risk_level == "low"
    assert event.metadata["source"] == "tool_execution_service"
    assert event.metadata["audit_bridge"] == "blocked_tool_call_authorization"
    assert event.metadata["raw_arguments_stored"] is False
    assert event.metadata["sensitive_payload_stored"] is False


def test_blocked_tool_call_audit_event_should_not_store_raw_tool_arguments() -> None:
    audit_log_service = AuditLogService()

    service = ToolExecutionService(
        audit_log_service=audit_log_service,
        blocked_tool_call_telemetry_service=BlockedToolCallTelemetryService(),
    )

    with pytest.raises(ToolExecutionError):
        service.execute(
            tool_name="requirements.analyze",
            arguments={
                "requirement_text": "secret requirement text should not be stored",
                "language": "en",
            },
            metadata={
                "caller_type": "future_admin_user",
                "environment": "local",
            },
        )

    serialized_events = audit_log_service.list_events().model_dump_json()

    assert "secret requirement text should not be stored" not in serialized_events
    assert '"arguments"' not in serialized_events
    assert '"requirement_text"' not in serialized_events
    assert "raw_arguments_stored" in serialized_events


def test_blocked_tool_call_should_record_telemetry_and_audit_event() -> None:
    audit_log_service = AuditLogService()
    blocked_tool_call_telemetry_service = BlockedToolCallTelemetryService()

    service = ToolExecutionService(
        audit_log_service=audit_log_service,
        blocked_tool_call_telemetry_service=blocked_tool_call_telemetry_service,
    )

    with pytest.raises(ToolExecutionError):
        service.execute(
            tool_name="requirements.analyze",
            arguments={
                "requirement_text": "The user should be able to login.",
                "language": "en",
            },
            metadata={
                "caller_type": "future_admin_user",
                "environment": "local",
            },
        )

    telemetry_response = blocked_tool_call_telemetry_service.list_records()
    audit_response = audit_log_service.list_events()

    assert telemetry_response.count == 1
    assert audit_response.count == 1
    assert telemetry_response.records[0].tool_name == "requirements.analyze"
    assert audit_response.events[0].target.target_id == "requirements.analyze"
