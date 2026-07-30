from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    EvaluationScenarioRunResult,
    GoldenEvaluationDatasetRunResponse,
    get_golden_evaluation_dataset_runner_service,
)
from ai_api.main import app


class StubGoldenEvaluationDatasetRunnerService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> GoldenEvaluationDatasetRunResponse:
        self.last_request = request

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
                    scenario_id="REQ-001",
                    scenario_name="Requirement scenario",
                    scenario_type="requirement_analysis",
                    priority="smoke",
                    status="passed",
                    output={
                        "status": "completed",
                        "summary": "Requirement analyzed.",
                    },
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-runner-service",
            },
        )


def test_run_golden_evaluation_dataset_endpoint_should_return_run_result() -> None:
    service = StubGoldenEvaluationDatasetRunnerService()
    app.dependency_overrides[
        get_golden_evaluation_dataset_runner_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/golden-dataset/run",
            json={
                "scenario_ids": [
                    "REQ-001",
                ],
                "dry_run": False,
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["dataset_name"] == "stub-dataset"
        assert body["scenario_count"] == 1
        assert body["passed_count"] == 1
        assert body["metadata"]["source"] == "stub-runner-service"

        assert service.last_request is not None
        assert service.last_request.scenario_ids == [
            "REQ-001",
        ]
        assert service.last_request.dry_run is False
        assert service.last_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_run_golden_evaluation_dataset_endpoint_should_reject_invalid_scenario_type() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/golden-dataset/run",
        json={
            "scenario_types": [
                "invalid_type",
            ],
        },
    )

    assert response.status_code == 422
