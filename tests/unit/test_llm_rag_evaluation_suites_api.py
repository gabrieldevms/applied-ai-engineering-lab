from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    EvaluationTelemetryInstrumentationService,
    LLMOutputEvaluationCaseResult,
    LLMOutputEvaluationRunResponse,
    LLMOutputEvaluationSuite,
    RAGRegressionCaseResult,
    RAGRegressionRunResponse,
    RAGRegressionSuite,
    get_evaluation_telemetry_instrumentation_service,
    get_llm_output_evaluation_service,
    get_llm_output_evaluation_suite_service,
    get_rag_regression_evaluation_service,
    get_rag_regression_suite_service,
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


class StubLLMOutputEvaluationSuiteService:
    def get_default_suite(self) -> LLMOutputEvaluationSuite:
        return LLMOutputEvaluationSuite(
            name="stub-llm-output-suite",
            version="0.1.0",
            description="Stub LLM output suite.",
            cases=[],
            metadata={
                "source": "stub-suite-service",
            },
        )


class StubLLMOutputEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> LLMOutputEvaluationRunResponse:
        self.last_request = request

        return LLMOutputEvaluationRunResponse(
            status="passed",
            suite_name="stub-llm-output-suite",
            suite_version="0.1.0",
            case_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            results=[
                LLMOutputEvaluationCaseResult(
                    case_id="LLM-REQ-001",
                    case_name="Requirement output",
                    component_name="requirement_analyzer",
                    status="passed",
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-llm-output-evaluation-service",
            },
        )


class StubRAGRegressionSuiteService:
    def get_default_suite(self) -> RAGRegressionSuite:
        return RAGRegressionSuite(
            name="stub-rag-regression-suite",
            version="0.1.0",
            description="Stub RAG regression suite.",
            cases=[],
            metadata={
                "source": "stub-suite-service",
            },
        )


class StubRAGRegressionEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> RAGRegressionRunResponse:
        self.last_request = request

        return RAGRegressionRunResponse(
            status="passed",
            suite_name="stub-rag-regression-suite",
            suite_version="0.1.0",
            case_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            results=[
                RAGRegressionCaseResult(
                    case_id="RAG-REG-001",
                    case_name="Billing RAG",
                    query="Quando o boleto deve ser registrado?",
                    status="passed",
                    checks=[],
                )
            ],
            metadata={
                "source": "stub-rag-regression-evaluation-service",
            },
        )


def test_get_llm_output_evaluation_suite_endpoint_should_return_suite() -> None:
    app.dependency_overrides[
        get_llm_output_evaluation_suite_service
    ] = lambda: StubLLMOutputEvaluationSuiteService()

    try:
        client = TestClient(app)

        response = client.get("/evals/llm-output/suite")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-llm-output-suite"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-suite-service"
    finally:
        app.dependency_overrides.clear()


def test_run_llm_output_evaluation_endpoint_should_return_result_and_use_instrumentation() -> None:
    service = StubLLMOutputEvaluationService()
    instrumentation_service = StubInstrumentationService()

    app.dependency_overrides[
        get_llm_output_evaluation_service
    ] = lambda: service
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/llm-output/run",
            json={
                "case_ids": [
                    "LLM-REQ-001",
                ],
                "metadata": {
                    "source": "api-test",
                    "run_id": "llm-run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["suite_name"] == "stub-llm-output-suite"
        assert body["case_count"] == 1

        assert service.last_request is not None
        assert service.last_request.case_ids == [
            "LLM-REQ-001",
        ]

        assert instrumentation_service.last_event_type == (
            "llm_output_evaluation_run"
        )
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == "api:/evals/llm-output/run"
        assert instrumentation_service.last_run_id == "llm-run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_llm_output_evaluation_suite"
        )
    finally:
        app.dependency_overrides.clear()


def test_get_rag_regression_suite_endpoint_should_return_suite() -> None:
    app.dependency_overrides[
        get_rag_regression_suite_service
    ] = lambda: StubRAGRegressionSuiteService()

    try:
        client = TestClient(app)

        response = client.get("/evals/rag-regression/suite")

        assert response.status_code == 200

        body = response.json()

        assert body["name"] == "stub-rag-regression-suite"
        assert body["version"] == "0.1.0"
        assert body["metadata"]["source"] == "stub-suite-service"
    finally:
        app.dependency_overrides.clear()


def test_run_rag_regression_endpoint_should_return_result_and_use_instrumentation() -> None:
    service = StubRAGRegressionEvaluationService()
    instrumentation_service = StubInstrumentationService()

    app.dependency_overrides[
        get_rag_regression_evaluation_service
    ] = lambda: service
    app.dependency_overrides[
        get_evaluation_telemetry_instrumentation_service
    ] = lambda: instrumentation_service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/rag-regression/run",
            json={
                "case_ids": [
                    "RAG-REG-001",
                ],
                "metadata": {
                    "source": "api-test",
                    "run_id": "rag-run-001",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["suite_name"] == "stub-rag-regression-suite"
        assert body["case_count"] == 1

        assert service.last_request is not None
        assert service.last_request.case_ids == [
            "RAG-REG-001",
        ]

        assert instrumentation_service.last_event_type == "rag_regression_run"
        assert instrumentation_service.last_component == "evaluation"
        assert instrumentation_service.last_source == (
            "api:/evals/rag-regression/run"
        )
        assert instrumentation_service.last_run_id == "rag-run-001"
        assert instrumentation_service.last_metadata is not None
        assert instrumentation_service.last_metadata["operation"] == (
            "run_rag_regression_suite"
        )
    finally:
        app.dependency_overrides.clear()


def test_run_llm_output_evaluation_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/llm-output/run",
        json={
            "suite": {
                "name": "invalid-suite",
                "version": "0.1.0",
                "description": "Invalid suite.",
                "cases": [
                    {
                        "id": "",
                        "name": "Invalid case",
                        "component_name": "component",
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


def test_run_rag_regression_endpoint_should_reject_invalid_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/rag-regression/run",
        json={
            "suite": {
                "name": "invalid-suite",
                "version": "0.1.0",
                "description": "Invalid suite.",
                "cases": [
                    {
                        "id": "",
                        "name": "Invalid case",
                        "query": "Qual é a regra?",
                        "input_payload": {
                            "query": "Qual é a regra?"
                        },
                        "actual_output": {
                            "status": "completed",
                            "answer": "Resposta."
                        }
                    }
                ]
            }
        },
    )

    assert response.status_code == 422
