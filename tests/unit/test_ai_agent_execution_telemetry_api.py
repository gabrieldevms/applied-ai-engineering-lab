from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    AIAgentExecutionRecord,
    AIAgentExecutionRecordsResponse,
    AIAgentExecutionSummaryResponse,
    get_ai_agent_execution_telemetry_service,
)
from ai_api.main import app


class StubAIAgentExecutionTelemetryService:
    def __init__(self) -> None:
        self.last_record_request: Any | None = None
        self.last_summary_request: Any | None = None

    def record(self, request: Any) -> AIAgentExecutionRecord:
        self.last_record_request = request

        return AIAgentExecutionRecord(
            record_id="agent-execution-record-001",
            component=request.component,
            operation=request.operation,
            agent_name=request.agent_name,
            run_status=request.run_status,
            status="passed",
            duration_ms=request.duration_ms,
            step_count=request.step_count,
            successful_step_count=request.successful_step_count,
            failed_step_count=request.failed_step_count,
            tool_call_count=request.tool_call_count,
            successful_tool_call_count=request.successful_tool_call_count,
            failed_tool_call_count=request.failed_tool_call_count,
            retry_count=request.retry_count,
            fallback_count=request.fallback_count,
            error_count=request.error_count,
            human_approval_request_count=request.human_approval_request_count,
            human_approval_granted_count=request.human_approval_granted_count,
            step_success_rate=1.0,
            tool_success_rate=1.0,
            human_approval_rate=1.0,
            quality_score=1.0,
            max_duration_ms=request.max_duration_ms,
            max_failed_steps=request.max_failed_steps,
            max_failed_tool_calls=request.max_failed_tool_calls,
            max_error_count=request.max_error_count,
            min_quality_score=request.min_quality_score,
            risks=[
                "No agent execution risks detected.",
            ],
            recorded_at="2026-07-30T20:00:00+00:00",
            metadata={
                "source": "stub-agent-execution-service",
            },
        )

    def list_records(
        self,
        component: str | None = None,
        agent_name: str | None = None,
        operation: str | None = None,
        status: str | None = None,
        run_status: str | None = None,
        limit: int = 100,
    ) -> AIAgentExecutionRecordsResponse:
        return AIAgentExecutionRecordsResponse(
            records=[
                AIAgentExecutionRecord(
                    record_id="agent-execution-record-001",
                    component="agent",
                    operation="qa_agent_run",
                    agent_name="qa-agent-v1",
                    run_status="completed",
                    status="passed",
                    duration_ms=1000.0,
                    step_count=2,
                    successful_step_count=2,
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
            ],
            count=1,
            metadata={
                "component": component,
                "agent_name": agent_name,
                "operation": operation,
                "status": status,
                "run_status": run_status,
                "limit": limit,
            },
        )

    def summarize(self, request: Any) -> AIAgentExecutionSummaryResponse:
        self.last_summary_request = request

        return AIAgentExecutionSummaryResponse(
            record_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            total_steps=2,
            total_successful_steps=2,
            total_failed_steps=0,
            total_tool_calls=1,
            total_successful_tool_calls=1,
            total_failed_tool_calls=0,
            total_retries=0,
            total_fallbacks=0,
            total_errors=0,
            total_human_approval_requests=0,
            total_human_approvals_granted=0,
            average_duration_ms=1000.0,
            average_step_success_rate=1.0,
            average_tool_success_rate=1.0,
            average_quality_score=1.0,
            component_coverage={
                "agent": 1,
            },
            agent_coverage={
                "qa-agent-v1": 1,
            },
            operation_coverage={
                "qa_agent_run": 1,
            },
            run_status_coverage={
                "completed": 1,
            },
            risks=[
                "No agent execution risks detected.",
            ],
            metadata={
                "source": "stub-agent-execution-service",
            },
        )


def test_record_agent_execution_endpoint_should_return_record() -> None:
    service = StubAIAgentExecutionTelemetryService()
    app.dependency_overrides[
        get_ai_agent_execution_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/agent-execution/records",
            json={
                "component": "agent",
                "operation": "qa_agent_run",
                "agent_name": "qa-agent-v1",
                "run_status": "completed",
                "duration_ms": 1000.0,
                "step_count": 2,
                "successful_step_count": 2,
                "failed_step_count": 0,
                "tool_call_count": 1,
                "successful_tool_call_count": 1,
                "failed_tool_call_count": 0,
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_id"] == "agent-execution-record-001"
        assert body["component"] == "agent"
        assert body["operation"] == "qa_agent_run"
        assert body["agent_name"] == "qa-agent-v1"
        assert body["run_status"] == "completed"
        assert body["status"] == "passed"
        assert body["quality_score"] == 1.0

        assert service.last_record_request is not None
        assert service.last_record_request.agent_name == "qa-agent-v1"
    finally:
        app.dependency_overrides.clear()


def test_list_agent_execution_records_endpoint_should_return_records() -> None:
    app.dependency_overrides[
        get_ai_agent_execution_telemetry_service
    ] = lambda: StubAIAgentExecutionTelemetryService()

    try:
        client = TestClient(app)

        response = client.get(
            "/observability/agent-execution/records?agent_name=qa-agent-v1&status=passed&limit=10"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["count"] == 1
        assert body["records"][0]["agent_name"] == "qa-agent-v1"
        assert body["metadata"]["agent_name"] == "qa-agent-v1"
        assert body["metadata"]["status"] == "passed"
        assert body["metadata"]["limit"] == 10
    finally:
        app.dependency_overrides.clear()


def test_summarize_agent_execution_endpoint_should_return_summary() -> None:
    service = StubAIAgentExecutionTelemetryService()
    app.dependency_overrides[
        get_ai_agent_execution_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/agent-execution/summary",
            json={
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["passed_count"] == 1
        assert body["average_quality_score"] == 1.0
        assert body["agent_coverage"]["qa-agent-v1"] == 1

        assert service.last_summary_request is not None
        assert service.last_summary_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_summarize_stored_agent_execution_endpoint_should_return_summary() -> None:
    app.dependency_overrides[
        get_ai_agent_execution_telemetry_service
    ] = lambda: StubAIAgentExecutionTelemetryService()

    try:
        client = TestClient(app)

        response = client.get("/observability/agent-execution/summary")

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["total_steps"] == 2
        assert body["average_step_success_rate"] == 1.0
    finally:
        app.dependency_overrides.clear()


def test_record_agent_execution_endpoint_should_reject_invalid_run_status() -> None:
    client = TestClient(app)

    response = client.post(
        "/observability/agent-execution/records",
        json={
            "component": "agent",
            "operation": "qa_agent_run",
            "agent_name": "qa-agent-v1",
            "run_status": "invalid-status",
        },
    )

    assert response.status_code == 422
