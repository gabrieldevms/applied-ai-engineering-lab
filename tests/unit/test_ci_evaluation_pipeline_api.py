from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    CIEvaluationPipelineRunResponse,
    CIEvaluationPipelineStageResult,
    get_ci_evaluation_pipeline_service,
    get_evaluation_telemetry_instrumentation_service,
)
from ai_api.main import app


class StubInstrumentationService:
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


class StubCIEvaluationPipelineService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> CIEvaluationPipelineRunResponse:
        self.last_request = request

        return CIEvaluationPipelineRunResponse(
            status="passed",
            score=1.0,
            stage_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            should_fail_ci=False,
            stages=[
                CIEvaluationPipelineStageResult(
                    name="prompt_regression",
                    status="passed",
                    score=1.0,
                    summary="Prompt regression passed.",
                    output={
                        "status": "passed",
                    },
                )
            ],
            metadata={
                "source": "stub-ci-pipeline-service",
            },
        )


def test_run_ci_evaluation_pipeline_endpoint_should_return_result_and_use_instrumentation() -> None:
    service = StubCIEvaluationPipelineService()
    instrumentation_service = StubInstrumentationService()

    app.dependency_overrides[
        get_ci_evaluation_pipeline_service
    ] = lambda: service
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/ci/pipeline/run",
            json={
                "include_golden_dataset_smoke": False,
                "metadata": {
                    "source": "api-test",
                    "run_id": "ci-run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["score"] == 1.0
        assert body["stage_count"] == 1
        assert body["should_fail_ci"] is False

        assert service.last_request is not None
        assert service.last_request.include_golden_dataset_smoke is False

        assert instrumentation_service.last_event_type == "ci_evaluation_pipeline_run"
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == "api:/evals/ci/pipeline/run"
        assert instrumentation_service.last_run_id == "ci-run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_ci_evaluation_pipeline"
        )
    finally:
        app.dependency_overrides.clear()


def test_run_ci_evaluation_pipeline_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/ci/pipeline/run",
        json={
            "fail_on_warning": "not-a-boolean",
        },
    )

    assert response.status_code == 422
