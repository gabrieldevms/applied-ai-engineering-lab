from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    MultiAgentCopilotRegressionCaseResult,
    MultiAgentCopilotRegressionRunResponse,
    MultiAgentCopilotRegressionSuite,
    get_evaluation_telemetry_instrumentation_service,
    get_multi_agent_copilot_regression_evaluation_service,
    get_multi_agent_copilot_regression_suite_service,
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


class StubMultiAgentCopilotRegressionSuiteService:
    def get_default_suite(self) -> MultiAgentCopilotRegressionSuite:
        return MultiAgentCopilotRegressionSuite(
            name="stub-multi-agent-copilot-regression-suite",
            version="0.1.0",
            description="Stub Multi-Agent QA Copilot regression suite.",
            cases=[],
            metadata={
                "source": "stub-suite-service",
            },
        )


class StubMultiAgentCopilotRegressionEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> MultiAgentCopilotRegressionRunResponse:
        self.last_request = request

        return MultiAgentCopilotRegressionRunResponse(
            status="passed",
            suite_name="stub-multi-agent-copilot-regression-suite",
            suite_version="0.1.0",
            case_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            results=[
                MultiAgentCopilotRegressionCaseResult(
                    case_id="MULTI-REG-001",
                    case_name="Clean workflow",
                    copilot_name="multi-agent-qa-copilot-v1",
                    status="passed",
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-multi-agent-regression-service",
            },
        )


def test_get_multi_agent_copilot_regression_suite_endpoint_should_return_suite() -> None:
    app.dependency_overrides[
        get_multi_agent_copilot_regression_suite_service
    ] = lambda: StubMultiAgentCopilotRegressionSuiteService()

    try:
        client = TestClient(app)

        response = client.get("/evals/multi-agent-copilot-regression/suite")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-multi-agent-copilot-regression-suite"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-suite-service"
    finally:
        app.dependency_overrides.clear()


def test_run_multi_agent_copilot_regression_endpoint_should_return_result_and_use_instrumentation() -> None:
    service = StubMultiAgentCopilotRegressionEvaluationService()
    instrumentation_service = StubInstrumentationService()

    app.dependency_overrides[
        get_multi_agent_copilot_regression_evaluation_service
    ] = lambda: service
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/multi-agent-copilot-regression/run",
            json={
                "case_ids": [
                    "MULTI-REG-001",
                ],
                "metadata": {
                    "source": "api-test",
                    "run_id": "multi-reg-run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["suite_name"] == "stub-multi-agent-copilot-regression-suite"
        assert body["case_count"] == 1

        assert service.last_request is not None
        assert service.last_request.case_ids == [
            "MULTI-REG-001",
        ]

        assert instrumentation_service.last_event_type == (
            "multi_agent_copilot_regression_run"
        )
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == (
            "api:/evals/multi-agent-copilot-regression/run"
        )
        assert instrumentation_service.last_run_id == "multi-reg-run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_multi_agent_copilot_regression_suite"
        )
    finally:
        app.dependency_overrides.clear()


def test_run_multi_agent_copilot_regression_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/multi-agent-copilot-regression/run",
        json={
            "suite": {
                "name": "invalid-suite",
                "version": "0.1.0",
                "description": "Invalid suite.",
                "cases": [
                    {
                        "id": "",
                        "name": "Invalid case",
                        "copilot_name": "multi-agent-qa-copilot-v1",
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
