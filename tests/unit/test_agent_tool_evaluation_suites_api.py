from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    AgentRegressionCaseResult,
    AgentRegressionRunResponse,
    AgentRegressionSuite,
    ToolCallingEvaluationCaseResult,
    ToolCallingEvaluationRunResponse,
    ToolCallingEvaluationSuite,
    get_agent_regression_evaluation_service,
    get_agent_regression_suite_service,
    get_evaluation_telemetry_instrumentation_service,
    get_tool_calling_evaluation_service,
    get_tool_calling_evaluation_suite_service,
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


class StubAgentRegressionSuiteService:
    def get_default_suite(self) -> AgentRegressionSuite:
        return AgentRegressionSuite(
            name="stub-agent-regression-suite",
            version="0.1.0",
            description="Stub agent regression suite.",
            cases=[],
            metadata={
                "source": "stub-suite-service",
            },
        )


class StubAgentRegressionEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> AgentRegressionRunResponse:
        self.last_request = request

        return AgentRegressionRunResponse(
            status="passed",
            suite_name="stub-agent-regression-suite",
            suite_version="0.1.0",
            case_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            results=[
                AgentRegressionCaseResult(
                    case_id="AGENT-QA-001",
                    case_name="QA Agent",
                    agent_name="qa-agent-v1",
                    status="passed",
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-agent-regression-service",
            },
        )


class StubToolCallingEvaluationSuiteService:
    def get_default_suite(self) -> ToolCallingEvaluationSuite:
        return ToolCallingEvaluationSuite(
            name="stub-tool-calling-suite",
            version="0.1.0",
            description="Stub tool-calling suite.",
            cases=[],
            metadata={
                "source": "stub-suite-service",
            },
        )


class StubToolCallingEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> ToolCallingEvaluationRunResponse:
        self.last_request = request

        return ToolCallingEvaluationRunResponse(
            status="passed",
            suite_name="stub-tool-calling-suite",
            suite_version="0.1.0",
            case_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            results=[
                ToolCallingEvaluationCaseResult(
                    case_id="TOOL-QA-001",
                    case_name="QA tool selection",
                    workflow_name="qa_agent_tool_selection",
                    status="passed",
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-tool-calling-service",
            },
        )


def test_get_agent_regression_suite_endpoint_should_return_suite() -> None:
    app.dependency_overrides[
        get_agent_regression_suite_service
    ] = lambda: StubAgentRegressionSuiteService()

    try:
        client = TestClient(app)

        response = client.get("/evals/agent-regression/suite")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-agent-regression-suite"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-suite-service"
    finally:
        app.dependency_overrides.clear()


def test_run_agent_regression_endpoint_should_return_result_and_use_instrumentation() -> None:
    service = StubAgentRegressionEvaluationService()
    instrumentation_service = StubInstrumentationService()

    app.dependency_overrides[
        get_agent_regression_evaluation_service
    ] = lambda: service
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/agent-regression/run",
            json={
                "case_ids": [
                    "AGENT-QA-001",
                ],
                "metadata": {
                    "source": "api-test",
                    "run_id": "agent-run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["suite_name"] == "stub-agent-regression-suite"
        assert body["case_count"] == 1

        assert service.last_request is not None
        assert service.last_request.case_ids == [
            "AGENT-QA-001",
        ]

        assert instrumentation_service.last_event_type == "agent_regression_run"
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == (
            "api:/evals/agent-regression/run"
        )
        assert instrumentation_service.last_run_id == "agent-run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_agent_regression_suite"
        )
    finally:
        app.dependency_overrides.clear()


def test_get_tool_calling_evaluation_suite_endpoint_should_return_suite() -> None:
    app.dependency_overrides[
        get_tool_calling_evaluation_suite_service
    ] = lambda: StubToolCallingEvaluationSuiteService()

    try:
        client = TestClient(app)

        response = client.get("/evals/tool-calling/suite")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-tool-calling-suite"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-suite-service"
    finally:
        app.dependency_overrides.clear()


def test_run_tool_calling_evaluation_endpoint_should_return_result_and_use_instrumentation() -> None:
    service = StubToolCallingEvaluationService()
    instrumentation_service = StubInstrumentationService()

    app.dependency_overrides[
        get_tool_calling_evaluation_service
    ] = lambda: service
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/tool-calling/run",
            json={
                "case_ids": [
                    "TOOL-QA-001",
                ],
                "metadata": {
                    "source": "api-test",
                    "run_id": "tool-run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["suite_name"] == "stub-tool-calling-suite"
        assert body["case_count"] == 1

        assert service.last_request is not None
        assert service.last_request.case_ids == [
            "TOOL-QA-001",
        ]

        assert instrumentation_service.last_event_type == (
            "tool_calling_evaluation_run"
        )
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == (
            "api:/evals/tool-calling/run"
        )
        assert instrumentation_service.last_run_id == "tool-run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_tool_calling_evaluation_suite"
        )
    finally:
        app.dependency_overrides.clear()


def test_run_agent_regression_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/agent-regression/run",
        json={
            "suite": {
                "name": "invalid-suite",
                "version": "0.1.0",
                "description": "Invalid suite.",
                "cases": [
                    {
                        "id": "",
                        "name": "Invalid case",
                        "agent_name": "qa-agent-v1",
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


def test_run_tool_calling_evaluation_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/tool-calling/run",
        json={
            "suite": {
                "name": "invalid-suite",
                "version": "0.1.0",
                "description": "Invalid suite.",
                "cases": [
                    {
                        "id": "",
                        "name": "Invalid case",
                        "workflow_name": "workflow",
                        "input_payload": {
                            "value": "test"
                        },
                        "actual_tool_calls": [],
                        "actual_output": {
                            "status": "completed"
                        }
                    }
                ]
            }
        },
    )

    assert response.status_code == 422
