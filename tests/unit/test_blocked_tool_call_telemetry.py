import pytest
from ai_api.agents.exceptions import ToolExecutionError
from ai_api.agents.tool_executor import ToolExecutionService
from ai_api.security import (
    BlockedToolCallTelemetryRequest,
    BlockedToolCallTelemetryService,
)


def test_blocked_tool_call_telemetry_service_should_record_safe_event() -> None:
    service = BlockedToolCallTelemetryService()

    record = service.record(
        BlockedToolCallTelemetryRequest(
            tool_name="requirements.analyze",
            caller_type="future_admin_user",
            environment="local",
            risk_level="low",
            authorization_policy="tool-authorization-policy-v1",
            reason="Tool execution is blocked by authorization policy.",
            violations=[
                "Tool is not allowed for caller_type=future_admin_user.",
            ],
            prompt_injection_risk_level="none",
            run_id="run-001",
            metadata={
                "source": "unit_test",
                "raw_arguments_stored": False,
            },
        )
    )

    assert record.tool_name == "requirements.analyze"
    assert record.authorization_status == "blocked"
    assert record.authorization_policy == "tool-authorization-policy-v1"
    assert record.caller_type == "future_admin_user"
    assert record.environment == "local"
    assert record.risk_level == "low"
    assert record.prompt_injection_risk_level == "none"
    assert record.metadata["raw_arguments_stored"] is False
    assert service.count() == 1


def test_blocked_tool_call_telemetry_service_should_filter_records() -> None:
    service = BlockedToolCallTelemetryService()

    service.record(
        BlockedToolCallTelemetryRequest(
            tool_name="requirements.analyze",
            caller_type="future_admin_user",
            environment="local",
            risk_level="low",
            authorization_policy="tool-authorization-policy-v1",
            reason="Blocked.",
            violations=["blocked"],
        )
    )
    service.record(
        BlockedToolCallTelemetryRequest(
            tool_name="data_analysis.agent.run",
            caller_type="backend_service",
            environment="production",
            risk_level="medium",
            authorization_policy="tool-authorization-policy-v1",
            reason="Blocked.",
            violations=["blocked"],
        )
    )

    response = service.list_records(tool_name="data_analysis.agent.run")

    assert response.count == 1
    assert response.records[0].tool_name == "data_analysis.agent.run"
    assert response.metadata["total_stored_records"] == 2
    assert response.metadata["total_filtered_records"] == 1


def test_blocked_tool_call_telemetry_service_should_reject_invalid_limit() -> None:
    service = BlockedToolCallTelemetryService()

    with pytest.raises(ValueError, match="limit must be greater"):
        service.list_records(limit=0)


def test_tool_execution_should_record_blocked_tool_call_telemetry() -> None:
    telemetry_service = BlockedToolCallTelemetryService()

    service = ToolExecutionService(
        blocked_tool_call_telemetry_service=telemetry_service,
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
                "run_id": "agent-run-001",
                "trace_id": "trace-001",
                "request_id": "request-001",
            },
        )

    response = telemetry_service.list_records()

    assert response.count == 1

    record = response.records[0]

    assert record.tool_name == "requirements.analyze"
    assert record.authorization_status == "blocked"
    assert record.authorization_policy == "tool-authorization-policy-v1"
    assert record.caller_type == "future_admin_user"
    assert record.environment == "local"
    assert record.run_id == "agent-run-001"
    assert record.trace_id == "trace-001"
    assert record.request_id == "request-001"
    assert any(
        "caller_type=future_admin_user" in violation
        for violation in record.violations
    )


def test_blocked_tool_call_telemetry_should_not_store_raw_tool_arguments() -> None:
    telemetry_service = BlockedToolCallTelemetryService()

    service = ToolExecutionService(
        blocked_tool_call_telemetry_service=telemetry_service,
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

    serialized_records = telemetry_service.list_records().model_dump_json()

    assert "secret requirement text should not be stored" not in serialized_records
    assert '"arguments"' not in serialized_records
    assert '"requirement_text"' not in serialized_records
