from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals.dependencies import get_ai_execution_history_service
from ai_api.evals.execution_history import (
    AIExecutionHistoryRecord,
    AIExecutionHistoryResponse,
)
from ai_api.main import app


class StubAIExecutionHistoryService:
    def __init__(self) -> None:
        self.last_execution_type: str | None = None
        self.last_status: str | None = None
        self.last_component: str | None = None
        self.last_run_id: str | None = None
        self.last_limit: int | None = None

    def list_history(
        self,
        execution_type: str | None = None,
        status: str | None = None,
        component: str | None = None,
        run_id: str | None = None,
        limit: int = 100,
    ) -> AIExecutionHistoryResponse:
        self.last_execution_type = execution_type
        self.last_status = status
        self.last_component = component
        self.last_run_id = run_id
        self.last_limit = limit

        return AIExecutionHistoryResponse(
            records=[
                AIExecutionHistoryRecord(
                    execution_id="agent_execution:record-001",
                    execution_type="agent_execution",
                    title="Agent execution: qa-agent-v1",
                    status="passed",
                    component="agent",
                    operation="qa_agent_run",
                    run_id="agent-run-001",
                    recorded_at="2026-08-02T20:00:00+00:00",
                    duration_ms=1000.0,
                    quality_score=1.0,
                    summary="qa-agent-v1 finished successfully.",
                    source_record_id="record-001",
                    metadata={
                        "source": "stub-execution-history-service",
                    },
                )
            ],
            count=1,
            metadata={
                "source": "stub-execution-history-service",
            },
        )


def test_execution_history_endpoint_should_return_history_records() -> None:
    service = StubAIExecutionHistoryService()
    app.dependency_overrides[
        get_ai_execution_history_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.get(
            "/observability/execution-history?"
            "execution_type=agent_execution&"
            "status=passed&"
            "component=agent&"
            "run_id=agent-run-001&"
            "limit=10"
        )

        assert response.status_code == 200

        body: dict[str, Any] = response.json()

        assert body["count"] == 1
        assert body["records"][0]["execution_type"] == "agent_execution"
        assert body["records"][0]["status"] == "passed"
        assert body["records"][0]["component"] == "agent"
        assert body["records"][0]["run_id"] == "agent-run-001"

        assert service.last_execution_type == "agent_execution"
        assert service.last_status == "passed"
        assert service.last_component == "agent"
        assert service.last_run_id == "agent-run-001"
        assert service.last_limit == 10
    finally:
        app.dependency_overrides.clear()
