import pytest
from pydantic import ValidationError
from ai_api.evals import (
    AIAgentExecutionRecord,
    AIAgentExecutionRecordRequest,
    AIAgentExecutionSummaryRequest,
    AIAgentExecutionTelemetryService,
)


def test_agent_execution_service_should_record_passed_execution_metrics() -> None:
    service = AIAgentExecutionTelemetryService()

    record = service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=1200.0,
            step_count=4,
            successful_step_count=4,
            failed_step_count=0,
            tool_call_count=3,
            successful_tool_call_count=3,
            failed_tool_call_count=0,
            retry_count=0,
            fallback_count=0,
            error_count=0,
            human_approval_request_count=1,
            human_approval_granted_count=1,
            max_duration_ms=2000.0,
            run_id="agent-run-001",
            metadata={
                "source": "unit-test",
            },
        )
    )

    assert record.record_id
    assert record.status == "passed"
    assert record.run_status == "completed"
    assert record.agent_name == "qa-agent-v1"
    assert record.duration_ms == 1200.0
    assert record.step_success_rate == 1.0
    assert record.tool_success_rate == 1.0
    assert record.human_approval_rate == 1.0
    assert record.quality_score == 1.0
    assert record.risks == [
        "No agent execution risks detected.",
    ]
    assert record.metadata["agent_execution_schema_version"] == "0.1.0"
    assert record.metadata["source"] == "unit-test"


def test_agent_execution_service_should_warn_when_duration_exceeds_limit() -> None:
    service = AIAgentExecutionTelemetryService()

    record = service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=3500.0,
            step_count=2,
            successful_step_count=2,
            tool_call_count=1,
            successful_tool_call_count=1,
            max_duration_ms=1000.0,
        )
    )

    assert record.status == "warning"
    assert record.quality_score == 1.0
    assert record.risks == [
        "Agent execution duration exceeded the configured maximum.",
    ]


def test_agent_execution_service_should_warn_when_retry_or_fallback_is_used() -> None:
    service = AIAgentExecutionTelemetryService()

    record = service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=900.0,
            step_count=2,
            successful_step_count=2,
            retry_count=1,
            fallback_count=1,
        )
    )

    assert record.status == "warning"
    assert record.risks == [
        "Agent execution required retries.",
        "Agent execution used fallback behavior.",
    ]


def test_agent_execution_service_should_fail_when_run_status_failed() -> None:
    service = AIAgentExecutionTelemetryService()

    record = service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="failed",
            duration_ms=500.0,
            step_count=3,
            successful_step_count=1,
            failed_step_count=2,
            max_failed_steps=0,
            error_count=1,
            max_error_count=0,
        )
    )

    assert record.status == "failed"
    assert record.quality_score < 0.7
    assert record.risks == [
        "Agent run ended with a non-success terminal status.",
        "Failed step count exceeded the configured maximum.",
        "Error count exceeded the configured maximum.",
        "Agent execution quality score is below the configured minimum.",
    ]


def test_agent_execution_service_should_fail_when_tool_failures_exceed_limit() -> None:
    service = AIAgentExecutionTelemetryService()

    record = service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=800.0,
            step_count=2,
            successful_step_count=2,
            tool_call_count=3,
            successful_tool_call_count=1,
            failed_tool_call_count=2,
            max_failed_tool_calls=0,
        )
    )

    assert record.status == "failed"
    assert "Failed tool call count exceeded the configured maximum." in record.risks


def test_agent_execution_service_should_list_records_with_filters() -> None:
    service = AIAgentExecutionTelemetryService()

    service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=500.0,
        )
    )
    service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="data_agent_run",
            agent_name="data-analyst-agent-v1",
            run_status="failed",
            duration_ms=300.0,
        )
    )

    response = service.list_records(
        agent_name="data-analyst-agent-v1",
    )

    assert response.count == 1
    assert response.records[0].agent_name == "data-analyst-agent-v1"
    assert response.records[0].run_status == "failed"
    assert response.metadata["total_stored_records"] == 2


def test_agent_execution_service_should_summarize_stored_records() -> None:
    service = AIAgentExecutionTelemetryService()

    service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=1000.0,
            step_count=4,
            successful_step_count=4,
            failed_step_count=0,
            tool_call_count=2,
            successful_tool_call_count=2,
            failed_tool_call_count=0,
            human_approval_request_count=1,
            human_approval_granted_count=1,
        )
    )
    service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=2000.0,
            step_count=4,
            successful_step_count=3,
            failed_step_count=1,
            tool_call_count=2,
            successful_tool_call_count=1,
            failed_tool_call_count=1,
            max_failed_steps=1,
            max_failed_tool_calls=1,
            min_quality_score=0.6,
            retry_count=1,
        )
    )

    response = service.summarize(AIAgentExecutionSummaryRequest())

    assert response.record_count == 2
    assert response.passed_count == 1
    assert response.warning_count == 1
    assert response.failed_count == 0
    assert response.total_steps == 8
    assert response.total_successful_steps == 7
    assert response.total_failed_steps == 1
    assert response.total_tool_calls == 4
    assert response.total_successful_tool_calls == 3
    assert response.total_failed_tool_calls == 1
    assert response.total_retries == 1
    assert response.total_fallbacks == 0
    assert response.total_errors == 0
    assert response.total_human_approval_requests == 1
    assert response.total_human_approvals_granted == 1
    assert response.average_duration_ms == 1500.0
    assert response.average_step_success_rate == 0.875
    assert response.average_tool_success_rate == 0.75
    assert response.average_human_approval_rate == 1.0
    assert response.average_quality_score == 0.875
    assert response.agent_coverage["qa-agent-v1"] == 2
    assert response.operation_coverage["qa_agent_run"] == 2
    assert response.run_status_coverage["completed"] == 2
    assert response.risks == [
        "1 agent execution record(s) returned warning.",
    ]


def test_agent_execution_service_should_summarize_request_records() -> None:
    service = AIAgentExecutionTelemetryService()

    record = AIAgentExecutionRecord(
        record_id="agent-execution-record-001",
        component="agent",
        operation="qa_agent_run",
        agent_name="qa-agent-v1",
        run_status="completed",
        status="passed",
        duration_ms=1000.0,
        step_count=1,
        successful_step_count=1,
        failed_step_count=0,
        tool_call_count=1,
        successful_tool_call_count=1,
        failed_tool_call_count=0,
        retry_count=0,
        fallback_count=0,
        error_count=0,
        human_approval_request_count=0,
        human_approval_granted_count=0,
        step_success_rate=1.0,
        tool_success_rate=1.0,
        quality_score=1.0,
        max_failed_steps=0,
        max_failed_tool_calls=0,
        max_error_count=0,
        min_quality_score=0.7,
        risks=[
            "No agent execution risks detected.",
        ],
        recorded_at="2026-07-30T20:00:00+00:00",
    )

    response = service.summarize(
        AIAgentExecutionSummaryRequest(
            records=[
                record,
            ],
            metadata={
                "source": "request-summary-test",
            },
        )
    )

    assert response.record_count == 1
    assert response.passed_count == 1
    assert response.average_quality_score == 1.0
    assert response.metadata["source"] == "request-summary-test"


def test_agent_execution_request_should_reject_blank_agent_name() -> None:
    with pytest.raises(ValidationError):
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="   ",
            run_status="completed",
        )


def test_agent_execution_request_should_reject_negative_step_count() -> None:
    with pytest.raises(ValidationError):
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            step_count=-1,
        )
