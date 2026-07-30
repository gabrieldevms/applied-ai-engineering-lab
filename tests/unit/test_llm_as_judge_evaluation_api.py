from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    LLMAsJudgeEvaluationCaseResult,
    LLMAsJudgeEvaluationRunResponse,
    LLMAsJudgeEvaluationSuite,
    get_evaluation_telemetry_instrumentation_service,
    get_llm_as_judge_evaluation_service,
    get_llm_as_judge_evaluation_suite_service,
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


class StubLLMAsJudgeEvaluationSuiteService:
    def get_default_suite(self) -> LLMAsJudgeEvaluationSuite:
        return LLMAsJudgeEvaluationSuite(
            name="stub-llm-as-judge-suite",
            version="0.1.0",
            description="Stub LLM-as-judge suite.",
            cases=[],
            metadata={
                "source": "stub-suite-service",
            },
        )


class StubLLMAsJudgeEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> LLMAsJudgeEvaluationRunResponse:
        self.last_request = request

        return LLMAsJudgeEvaluationRunResponse(
            status="passed",
            suite_name="stub-llm-as-judge-suite",
            suite_version="0.1.0",
            case_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            average_score=1.0,
            results=[
                LLMAsJudgeEvaluationCaseResult(
                    case_id="JUDGE-REQ-001",
                    case_name="Judge requirement analysis quality",
                    evaluation_target="requirement_analysis",
                    status="passed",
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-llm-as-judge-service",
            },
        )


def test_get_llm_as_judge_evaluation_suite_endpoint_should_return_suite() -> None:
    app.dependency_overrides[
        get_llm_as_judge_evaluation_suite_service
    ] = lambda: StubLLMAsJudgeEvaluationSuiteService()

    try:
        client = TestClient(app)

        response = client.get("/evals/llm-as-judge/suite")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-llm-as-judge-suite"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-suite-service"
    finally:
        app.dependency_overrides.clear()


def test_run_llm_as_judge_evaluation_endpoint_should_return_result_and_use_instrumentation() -> None:
    service = StubLLMAsJudgeEvaluationService()
    instrumentation_service = StubInstrumentationService()

    app.dependency_overrides[
        get_llm_as_judge_evaluation_service
    ] = lambda: service
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/llm-as-judge/run",
            json={
                "case_ids": [
                    "JUDGE-REQ-001",
                ],
                "metadata": {
                    "source": "api-test",
                    "run_id": "judge-run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["suite_name"] == "stub-llm-as-judge-suite"
        assert body["case_count"] == 1
        assert body["average_score"] == 1.0

        assert service.last_request is not None
        assert service.last_request.case_ids == [
            "JUDGE-REQ-001",
        ]

        assert instrumentation_service.last_event_type == (
            "llm_as_judge_evaluation_run"
        )
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == (
            "api:/evals/llm-as-judge/run"
        )
        assert instrumentation_service.last_run_id == "judge-run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_llm_as_judge_evaluation_suite"
        )
    finally:
        app.dependency_overrides.clear()


def test_run_llm_as_judge_evaluation_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/llm-as-judge/run",
        json={
            "suite": {
                "name": "invalid-suite",
                "version": "0.1.0",
                "description": "Invalid suite.",
                "cases": [
                    {
                        "id": "",
                        "name": "Invalid case",
                        "evaluation_target": "requirement_analysis",
                        "input_payload": {
                            "value": "test"
                        },
                        "candidate_output": {
                            "status": "completed"
                        }
                    }
                ]
            }
        },
    )

    assert response.status_code == 422
