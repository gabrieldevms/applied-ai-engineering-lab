import pytest
from pydantic import ValidationError
from ai_api.evals import (
    LLMAsJudgeEvaluationCase,
    LLMAsJudgeEvaluationRunRequest,
    LLMAsJudgeEvaluationService,
    LLMAsJudgeEvaluationSuite,
    LLMAsJudgeEvaluationSuiteService,
    LLMAsJudgeExpectation,
    LLMAsJudgeOutput,
    LLMAsJudgeRubricItem,
    build_default_llm_as_judge_evaluation_suite,
)


def test_default_llm_as_judge_evaluation_suite_should_include_expected_cases() -> None:
    suite = build_default_llm_as_judge_evaluation_suite()

    case_ids = [
        evaluation_case.id
        for evaluation_case in suite.cases
    ]

    assert suite.name == "applied-ai-engineering-lab-llm-as-judge-evaluation-suite"
    assert suite.version == "0.1.0"
    assert case_ids == [
        "JUDGE-REQ-001",
        "JUDGE-RAG-001",
        "JUDGE-MULTI-001",
    ]


def test_llm_as_judge_evaluation_suite_service_should_return_default_suite() -> None:
    service = LLMAsJudgeEvaluationSuiteService()

    suite = service.get_default_suite()

    assert suite.cases
    assert suite.metadata["suite_type"] == "llm_as_judge_evaluation"
    assert suite.metadata["execution_mode"] == "controlled_judge_output_validation"


def test_llm_as_judge_evaluation_should_pass_default_suite() -> None:
    service = LLMAsJudgeEvaluationService()

    response = service.run(
        LLMAsJudgeEvaluationRunRequest(
            suite=build_default_llm_as_judge_evaluation_suite(),
        )
    )

    assert response.status == "passed"
    assert response.case_count == 3
    assert response.passed_count == 3
    assert response.failed_count == 0
    assert response.average_score == 0.9233


def test_llm_as_judge_evaluation_should_filter_by_case_id() -> None:
    service = LLMAsJudgeEvaluationService()

    response = service.run(
        LLMAsJudgeEvaluationRunRequest(
            suite=build_default_llm_as_judge_evaluation_suite(),
            case_ids=[
                "JUDGE-RAG-001",
            ],
        )
    )

    assert response.status == "passed"
    assert response.case_count == 1
    assert response.results[0].case_id == "JUDGE-RAG-001"


def test_llm_as_judge_evaluation_should_fail_when_judge_output_is_missing() -> None:
    service = LLMAsJudgeEvaluationService()

    suite = LLMAsJudgeEvaluationSuite(
        name="custom-judge-suite",
        version="0.1.0",
        description="Custom suite with missing judge output.",
        cases=[
            LLMAsJudgeEvaluationCase(
                id="JUDGE-CUSTOM-001",
                name="Missing judge output",
                evaluation_target="requirement_analysis",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                candidate_output={
                    "status": "completed",
                    "summary": "Output candidato.",
                },
                judge_output=None,
            )
        ],
    )

    response = service.run(
        LLMAsJudgeEvaluationRunRequest(
            suite=suite,
        )
    )

    presence_check = [
        check
        for check in response.results[0].checks
        if check.name == "judge_output_presence"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert presence_check.status == "failed"


def test_llm_as_judge_evaluation_should_fail_when_score_is_below_minimum() -> None:
    service = LLMAsJudgeEvaluationService()

    suite = LLMAsJudgeEvaluationSuite(
        name="custom-judge-suite",
        version="0.1.0",
        description="Custom suite with low judge score.",
        cases=[
            LLMAsJudgeEvaluationCase(
                id="JUDGE-CUSTOM-002",
                name="Low score",
                evaluation_target="rag_answer",
                input_payload={
                    "query": "Qual é a regra?",
                },
                candidate_output={
                    "status": "completed",
                    "answer": "Resposta candidata.",
                },
                judge_output=LLMAsJudgeOutput(
                    verdict="warning",
                    score=0.5,
                    rationale="The answer is partially grounded.",
                    criteria_scores={
                        "grounding": 0.5,
                    },
                ),
                expectations=LLMAsJudgeExpectation(
                    allowed_verdicts=[
                        "pass",
                        "warning",
                    ],
                    min_score=0.8,
                    required_criteria=[
                        "grounding",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        LLMAsJudgeEvaluationRunRequest(
            suite=suite,
        )
    )

    score_check = [
        check
        for check in response.results[0].checks
        if check.name == "min_score"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert score_check.status == "failed"
    assert score_check.metadata["actual_score"] == 0.5


def test_llm_as_judge_evaluation_should_fail_when_required_criterion_is_missing() -> None:
    service = LLMAsJudgeEvaluationService()

    suite = LLMAsJudgeEvaluationSuite(
        name="custom-judge-suite",
        version="0.1.0",
        description="Custom suite with missing criterion.",
        cases=[
            LLMAsJudgeEvaluationCase(
                id="JUDGE-CUSTOM-003",
                name="Missing criterion",
                evaluation_target="agent_output",
                input_payload={
                    "objective": "Avaliar saída de agente.",
                },
                candidate_output={
                    "status": "completed",
                },
                judge_output=LLMAsJudgeOutput(
                    verdict="pass",
                    score=0.9,
                    rationale="The agent output is acceptable.",
                    criteria_scores={
                        "structure": 0.9,
                    },
                ),
                expectations=LLMAsJudgeExpectation(
                    required_criteria=[
                        "structure",
                        "traceability",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        LLMAsJudgeEvaluationRunRequest(
            suite=suite,
        )
    )

    criteria_check = [
        check
        for check in response.results[0].checks
        if check.name == "required_criteria"
    ][0]

    assert response.status == "failed"
    assert criteria_check.status == "failed"
    assert criteria_check.metadata["missing_criteria"] == [
        "traceability",
    ]


def test_llm_as_judge_evaluation_should_fail_when_rubric_score_is_below_threshold() -> None:
    service = LLMAsJudgeEvaluationService()

    suite = LLMAsJudgeEvaluationSuite(
        name="custom-judge-suite",
        version="0.1.0",
        description="Custom suite with failing rubric score.",
        cases=[
            LLMAsJudgeEvaluationCase(
                id="JUDGE-CUSTOM-004",
                name="Failing rubric score",
                evaluation_target="multi_agent_final_report",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                candidate_output={
                    "status": "completed",
                },
                rubric=[
                    LLMAsJudgeRubricItem(
                        name="actionability",
                        description="Output should be actionable.",
                        passing_score=0.8,
                    )
                ],
                judge_output=LLMAsJudgeOutput(
                    verdict="pass",
                    score=0.85,
                    rationale="The output is acceptable but not very actionable.",
                    criteria_scores={
                        "actionability": 0.6,
                    },
                ),
                expectations=LLMAsJudgeExpectation(
                    min_score=0.8,
                    required_criteria=[
                        "actionability",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        LLMAsJudgeEvaluationRunRequest(
            suite=suite,
        )
    )

    rubric_check = [
        check
        for check in response.results[0].checks
        if check.name == "rubric_scores"
    ][0]

    assert response.status == "failed"
    assert rubric_check.status == "failed"
    assert rubric_check.metadata["failed_items"][0]["criterion"] == "actionability"


def test_llm_as_judge_evaluation_case_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        LLMAsJudgeEvaluationCase(
            id="JUDGE-INVALID-001",
            name="Invalid judge case",
            evaluation_target="requirement_analysis",
            input_payload={},
            candidate_output={
                "status": "completed",
            },
        )
