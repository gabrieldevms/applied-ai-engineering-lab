from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    PromptRegressionCaseResult,
    PromptRegressionRunResponse,
    PromptRegressionSuite,
    get_prompt_regression_evaluation_service,
    get_prompt_regression_suite_service,
)
from ai_api.main import app


class StubPromptRegressionSuiteService:
    def get_default_suite(self) -> PromptRegressionSuite:
        return PromptRegressionSuite(
            name="stub-prompt-regression-suite",
            version="0.1.0",
            description="Stub prompt regression suite.",
            cases=[],
            metadata={
                "source": "stub-suite-service",
            },
        )


class StubPromptRegressionEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> PromptRegressionRunResponse:
        self.last_request = request

        return PromptRegressionRunResponse(
            status="passed",
            suite_name="stub-prompt-regression-suite",
            suite_version="0.1.0",
            case_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            results=[
                PromptRegressionCaseResult(
                    case_id="PROMPT-REQ-001",
                    case_name="Requirement prompt case",
                    prompt_name="requirement_analysis_prompt",
                    status="passed",
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-evaluation-service",
            },
        )


def test_get_prompt_regression_suite_endpoint_should_return_suite() -> None:
    app.dependency_overrides[
        get_prompt_regression_suite_service
    ] = lambda: StubPromptRegressionSuiteService()

    try:
        client = TestClient(app)

        response = client.get("/evals/prompt-regression/suite")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-prompt-regression-suite"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-suite-service"
    finally:
        app.dependency_overrides.clear()


def test_run_prompt_regression_suite_endpoint_should_return_result() -> None:
    service = StubPromptRegressionEvaluationService()
    app.dependency_overrides[
        get_prompt_regression_evaluation_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/prompt-regression/run",
            json={
                "case_ids": [
                    "PROMPT-REQ-001",
                ],
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["suite_name"] == "stub-prompt-regression-suite"
        assert body["case_count"] == 1
        assert body["passed_count"] == 1
        assert body["metadata"]["source"] == "stub-evaluation-service"

        assert service.last_request is not None
        assert service.last_request.case_ids == [
            "PROMPT-REQ-001",
        ]
        assert service.last_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_run_prompt_regression_suite_endpoint_should_reject_invalid_case_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/prompt-regression/run",
        json={
            "suite": {
                "name": "invalid-suite",
                "version": "0.1.0",
                "description": "Invalid suite.",
                "cases": [
                    {
                        "id": "",
                        "name": "Invalid case",
                        "prompt_name": "invalid_prompt",
                        "input_payload": {
                            "value": "test"
                        },
                        "actual_output": {
                            "status": "completed"
                        }
                    }
                ]
            }
        },
    )

    assert response.status_code == 422
