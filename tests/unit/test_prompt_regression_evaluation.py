import pytest
from pydantic import ValidationError
from ai_api.evals import (
    PromptRegressionCase,
    PromptRegressionEvaluationService,
    PromptRegressionExpectation,
    PromptRegressionRunRequest,
    PromptRegressionSuite,
    PromptRegressionSuiteService,
    build_default_prompt_regression_suite,
)


def test_default_prompt_regression_suite_should_include_expected_cases() -> None:
    suite = build_default_prompt_regression_suite()

    case_ids = [
        regression_case.id
        for regression_case in suite.cases
    ]

    assert suite.name == "applied-ai-engineering-lab-prompt-regression-suite"
    assert suite.version == "0.1.0"
    assert case_ids == [
        "PROMPT-REQ-001",
        "PROMPT-RAG-001",
        "PROMPT-MULTI-001",
    ]


def test_prompt_regression_suite_service_should_return_default_suite() -> None:
    service = PromptRegressionSuiteService()

    suite = service.get_default_suite()

    assert suite.cases
    assert suite.metadata["suite_type"] == "prompt_regression"
    assert suite.metadata["execution_mode"] == (
        "deterministic_output_validation"
    )


def test_prompt_regression_evaluation_should_pass_default_suite() -> None:
    service = PromptRegressionEvaluationService()

    response = service.run(
        PromptRegressionRunRequest(
            suite=build_default_prompt_regression_suite(),
        )
    )

    assert response.status == "passed"
    assert response.case_count == 3
    assert response.passed_count == 3
    assert response.warning_count == 0
    assert response.failed_count == 0

    result_status_by_id = {
        result.case_id: result.status
        for result in response.results
    }

    assert result_status_by_id["PROMPT-REQ-001"] == "passed"
    assert result_status_by_id["PROMPT-RAG-001"] == "passed"
    assert result_status_by_id["PROMPT-MULTI-001"] == "passed"


def test_prompt_regression_evaluation_should_filter_by_case_id() -> None:
    service = PromptRegressionEvaluationService()

    response = service.run(
        PromptRegressionRunRequest(
            suite=build_default_prompt_regression_suite(),
            case_ids=[
                "PROMPT-RAG-001",
            ],
        )
    )

    assert response.status == "passed"
    assert response.case_count == 1
    assert response.results[0].case_id == "PROMPT-RAG-001"


def test_prompt_regression_evaluation_should_fail_when_required_marker_is_missing() -> None:
    service = PromptRegressionEvaluationService()

    suite = PromptRegressionSuite(
        name="custom-prompt-suite",
        version="0.1.0",
        description="Custom suite with missing marker.",
        cases=[
            PromptRegressionCase(
                id="PROMPT-CUSTOM-001",
                name="Missing marker case",
                prompt_name="custom_prompt",
                output_format="json",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output={
                    "status": "completed",
                    "summary": "Output sem o marcador obrigatório.",
                },
                expectations=PromptRegressionExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "summary",
                        "acceptance_criteria",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        PromptRegressionRunRequest(
            suite=suite,
        )
    )

    marker_check = [
        check
        for check in response.results[0].checks
        if check.name == "required_output_markers"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert response.results[0].status == "failed"
    assert marker_check.status == "failed"
    assert marker_check.metadata["missing_markers"] == [
        "acceptance_criteria",
    ]


def test_prompt_regression_evaluation_should_fail_when_forbidden_marker_is_detected() -> None:
    service = PromptRegressionEvaluationService()

    suite = PromptRegressionSuite(
        name="custom-prompt-suite",
        version="0.1.0",
        description="Custom suite with forbidden marker.",
        cases=[
            PromptRegressionCase(
                id="PROMPT-CUSTOM-002",
                name="Forbidden marker case",
                prompt_name="custom_prompt",
                output_format="text",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output=(
                    "As an AI language model, I cannot guarantee this result."
                ),
                expectations=PromptRegressionExpectation(
                    forbidden_output_markers=[
                        "As an AI language model",
                    ],
                    min_output_length=10,
                ),
            )
        ],
    )

    response = service.run(
        PromptRegressionRunRequest(
            suite=suite,
        )
    )

    forbidden_check = [
        check
        for check in response.results[0].checks
        if check.name == "forbidden_output_markers"
    ][0]

    assert response.status == "failed"
    assert response.results[0].status == "failed"
    assert forbidden_check.status == "failed"
    assert forbidden_check.metadata["detected_markers"] == [
        "As an AI language model",
    ]


def test_prompt_regression_case_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        PromptRegressionCase(
            id="PROMPT-INVALID-001",
            name="Invalid prompt case",
            prompt_name="invalid_prompt",
            input_payload={},
            actual_output={
                "status": "completed",
            },
        )
