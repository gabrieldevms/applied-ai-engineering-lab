from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    EvaluationScenarioRunResult,
    EvaluationTelemetryInstrumentationService,
    GoldenEvaluationDatasetRunResponse,
    get_evaluation_telemetry_instrumentation_service,
    get_golden_evaluation_dataset_runner_service,
)
from ai_api.main import app


class StubGoldenEvaluationDatasetRunnerService:
    def run(self, request: Any) -> GoldenEvaluationDatasetRunResponse:
        return GoldenEvaluationDatasetRunResponse(
            status="passed",
            dataset_name="stub-dataset",
            dataset_version="0.1.0",
            scenario_count=1,
            executed_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            skipped_count=0,
            results=[
                EvaluationScenarioRunResult(
                    scenario_id="MCP-001",
                    scenario_name="MCP project status discovery",
                    scenario_type="mcp_tool",
                    priority="smoke",
                    status="passed",
                )
            ],
            metadata={
                "source": "stub-runner-service",
            },
        )


class StubEvaluationTelemetryInstrumentationService:
    def __init__(self) -> None:
        self.last_event_type: str | None = None
        self.last_component: str | None = None
        self.last_source: str | None = None
        self.last_run_id: str | None = None
        self.last_metadata: dict[str, Any] | None = None

    def instrument(
        self,
        event_type: str,
        component: str,
        source: str,
        operation: Any,
        run_id: str | None = None,
        scenario_id: str | None = None,
        case_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        self.last_event_type = event_type
        self.last_component = component
        self.last_source = source
        self.last_run_id = run_id
        self.last_metadata = metadata

        return operation()


def test_golden_dataset_run_endpoint_should_use_telemetry_instrumentation() -> None:
    instrumentation_service = StubEvaluationTelemetryInstrumentationService()

    app.dependency_overrides[
        get_golden_evaluation_dataset_runner_service
    ] = lambda: StubGoldenEvaluationDatasetRunnerService()
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/golden-dataset/run",
            json={
                "scenario_ids": [
                    "MCP-001",
                ],
                "metadata": {
                    "source": "api-test",
                    "run_id": "run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["dataset_name"] == "stub-dataset"

        assert instrumentation_service.last_event_type == "golden_dataset_run"
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == (
            "api:/evals/golden-dataset/run"
        )
        assert instrumentation_service.last_run_id == "run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_golden_evaluation_dataset"
        )
        assert instrumentation_service.last_metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()
