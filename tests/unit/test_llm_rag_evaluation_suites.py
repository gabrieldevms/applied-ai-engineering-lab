import pytest
from pydantic import ValidationError
from ai_api.evals import (
    LLMOutputEvaluationCase,
    LLMOutputEvaluationExpectation,
    LLMOutputEvaluationRunRequest,
    LLMOutputEvaluationService,
    LLMOutputEvaluationSuite,
    LLMOutputEvaluationSuiteService,
    RAGRegressionCase,
    RAGRegressionEvaluationService,
    RAGRegressionExpectation,
    RAGRegressionRunRequest,
    RAGRegressionSuite,
    RAGRegressionSuiteService,
    build_default_llm_output_evaluation_suite,
    build_default_rag_regression_suite,
)


def test_default_llm_output_evaluation_suite_should_include_expected_cases() -> None:
    suite = build_default_llm_output_evaluation_suite()

    case_ids = [
        evaluation_case.id
        for evaluation_case in suite.cases
    ]

    assert suite.name == "applied-ai-engineering-lab-llm-output-evaluation-suite"
    assert suite.version == "0.1.0"
    assert case_ids == [
        "LLM-REQ-001",
        "LLM-AGENT-001",
        "LLM-REPORT-001",
    ]


def test_llm_output_evaluation_suite_service_should_return_default_suite() -> None:
    service = LLMOutputEvaluationSuiteService()

    suite = service.get_default_suite()

    assert suite.cases
    assert suite.metadata["suite_type"] == "llm_output_evaluation"
    assert suite.metadata["execution_mode"] == (
        "deterministic_output_validation"
    )


def test_llm_output_evaluation_should_pass_default_suite() -> None:
    service = LLMOutputEvaluationService()

    response = service.run(
        LLMOutputEvaluationRunRequest(
            suite=build_default_llm_output_evaluation_suite(),
        )
    )

    assert response.status == "passed"
    assert response.case_count == 3
    assert response.passed_count == 3
    assert response.failed_count == 0


def test_llm_output_evaluation_should_filter_by_case_id() -> None:
    service = LLMOutputEvaluationService()

    response = service.run(
        LLMOutputEvaluationRunRequest(
            suite=build_default_llm_output_evaluation_suite(),
            case_ids=[
                "LLM-REQ-001",
            ],
        )
    )

    assert response.status == "passed"
    assert response.case_count == 1
    assert response.results[0].case_id == "LLM-REQ-001"


def test_llm_output_evaluation_should_fail_when_required_json_key_is_missing() -> None:
    service = LLMOutputEvaluationService()

    suite = LLMOutputEvaluationSuite(
        name="custom-llm-suite",
        version="0.1.0",
        description="Custom LLM suite with missing JSON key.",
        cases=[
            LLMOutputEvaluationCase(
                id="LLM-CUSTOM-001",
                name="Missing JSON key",
                component_name="custom_component",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output={
                    "status": "completed",
                    "summary": "Output sem business_rules.",
                },
                expectations=LLMOutputEvaluationExpectation(
                    expected_status="completed",
                    required_json_keys=[
                        "status",
                        "summary",
                        "business_rules",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        LLMOutputEvaluationRunRequest(
            suite=suite,
        )
    )

    json_key_check = [
        check
        for check in response.results[0].checks
        if check.name == "required_json_keys"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert response.results[0].status == "failed"
    assert json_key_check.status == "failed"
    assert json_key_check.metadata["missing_keys"] == [
        "business_rules",
    ]


def test_default_rag_regression_suite_should_include_expected_cases() -> None:
    suite = build_default_rag_regression_suite()

    case_ids = [
        regression_case.id
        for regression_case in suite.cases
    ]

    assert suite.name == "applied-ai-engineering-lab-rag-regression-suite"
    assert suite.version == "0.1.0"
    assert case_ids == [
        "RAG-REG-001",
        "RAG-REG-002",
    ]


def test_rag_regression_suite_service_should_return_default_suite() -> None:
    service = RAGRegressionSuiteService()

    suite = service.get_default_suite()

    assert suite.cases
    assert suite.metadata["suite_type"] == "rag_regression"
    assert suite.metadata["execution_mode"] == (
        "deterministic_output_validation"
    )


def test_rag_regression_evaluation_should_pass_default_suite() -> None:
    service = RAGRegressionEvaluationService()

    response = service.run(
        RAGRegressionRunRequest(
            suite=build_default_rag_regression_suite(),
        )
    )

    assert response.status == "passed"
    assert response.case_count == 2
    assert response.passed_count == 2
    assert response.failed_count == 0


def test_rag_regression_evaluation_should_filter_by_case_id() -> None:
    service = RAGRegressionEvaluationService()

    response = service.run(
        RAGRegressionRunRequest(
            suite=build_default_rag_regression_suite(),
            case_ids=[
                "RAG-REG-001",
            ],
        )
    )

    assert response.status == "passed"
    assert response.case_count == 1
    assert response.results[0].case_id == "RAG-REG-001"


def test_rag_regression_evaluation_should_fail_when_required_citation_is_missing() -> None:
    service = RAGRegressionEvaluationService()

    suite = RAGRegressionSuite(
        name="custom-rag-suite",
        version="0.1.0",
        description="Custom RAG suite with missing citation.",
        cases=[
            RAGRegressionCase(
                id="RAG-CUSTOM-001",
                name="Missing citation source",
                query="Quando o boleto deve ser registrado?",
                input_payload={
                    "query": "Quando o boleto deve ser registrado?",
                    "documents": [
                        {
                            "id": "doc-1",
                            "text": "Boletos devem ser registrados.",
                        }
                    ],
                },
                actual_output={
                    "status": "completed",
                    "answer": "O boleto deve ser registrado antes do envio.",
                    "citations": [
                        {
                            "source": "wrong-source.md",
                        }
                    ],
                    "retrieved_chunks": [
                        {
                            "content": "Boletos devem ser registrados.",
                        }
                    ],
                    "metadata": {},
                },
                expectations=RAGRegressionExpectation(
                    expected_status="completed",
                    required_answer_markers=[
                        "antes do envio",
                    ],
                    required_citation_sources=[
                        "billing-policy.md",
                    ],
                    min_retrieved_chunks=1,
                ),
            )
        ],
    )

    response = service.run(
        RAGRegressionRunRequest(
            suite=suite,
        )
    )

    citation_check = [
        check
        for check in response.results[0].checks
        if check.name == "citations"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert response.results[0].status == "failed"
    assert citation_check.status == "failed"
    assert citation_check.metadata["missing_sources"] == [
        "billing-policy.md",
    ]


def test_llm_output_evaluation_case_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        LLMOutputEvaluationCase(
            id="LLM-INVALID-001",
            name="Invalid LLM case",
            component_name="invalid_component",
            input_payload={},
            actual_output={
                "status": "completed",
            },
        )


def test_rag_regression_case_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        RAGRegressionCase(
            id="RAG-INVALID-001",
            name="Invalid RAG case",
            query="Qual é a regra?",
            input_payload={},
            actual_output={
                "status": "completed",
                "answer": "Resposta.",
            },
        )
