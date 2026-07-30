import pytest
from pydantic import ValidationError
from ai_api.evals import (
    AIEvaluationReportAggregationRequest,
    AIEvaluationReportAggregationService,
    EvaluationScenarioRunResult,
    GoldenEvaluationDatasetRunResponse,
    PromptRegressionCaseResult,
    PromptRegressionRunResponse,
)


def _build_passed_golden_dataset_run() -> GoldenEvaluationDatasetRunResponse:
    return GoldenEvaluationDatasetRunResponse(
        status="passed",
        dataset_name="golden-dataset",
        dataset_version="0.1.0",
        scenario_count=2,
        executed_count=2,
        passed_count=2,
        warning_count=0,
        failed_count=0,
        skipped_count=0,
        results=[
            EvaluationScenarioRunResult(
                scenario_id="REQ-001",
                scenario_name="Requirement analysis",
                scenario_type="requirement_analysis",
                priority="smoke",
                status="passed",
            ),
            EvaluationScenarioRunResult(
                scenario_id="MCP-001",
                scenario_name="MCP status",
                scenario_type="mcp_tool",
                priority="smoke",
                status="passed",
            ),
        ],
    )


def _build_warning_golden_dataset_run() -> GoldenEvaluationDatasetRunResponse:
    return GoldenEvaluationDatasetRunResponse(
        status="warning",
        dataset_name="golden-dataset",
        dataset_version="0.1.0",
        scenario_count=2,
        executed_count=1,
        passed_count=1,
        warning_count=0,
        failed_count=0,
        skipped_count=1,
        results=[
            EvaluationScenarioRunResult(
                scenario_id="REQ-001",
                scenario_name="Requirement analysis",
                scenario_type="requirement_analysis",
                priority="smoke",
                status="passed",
            ),
            EvaluationScenarioRunResult(
                scenario_id="RAG-001",
                scenario_name="RAG answer",
                scenario_type="rag_answer",
                priority="regression",
                status="skipped",
            ),
        ],
    )


def _build_passed_prompt_regression_run() -> PromptRegressionRunResponse:
    return PromptRegressionRunResponse(
        status="passed",
        suite_name="prompt-regression-suite",
        suite_version="0.1.0",
        case_count=2,
        passed_count=2,
        warning_count=0,
        failed_count=0,
        results=[
            PromptRegressionCaseResult(
                case_id="PROMPT-REQ-001",
                case_name="Requirement prompt",
                prompt_name="requirement_analysis_prompt",
                status="passed",
            ),
            PromptRegressionCaseResult(
                case_id="PROMPT-RAG-001",
                case_name="RAG prompt",
                prompt_name="rag_answer_prompt",
                status="passed",
            ),
        ],
    )


def _build_failed_prompt_regression_run() -> PromptRegressionRunResponse:
    return PromptRegressionRunResponse(
        status="failed",
        suite_name="prompt-regression-suite",
        suite_version="0.1.0",
        case_count=2,
        passed_count=1,
        warning_count=0,
        failed_count=1,
        results=[
            PromptRegressionCaseResult(
                case_id="PROMPT-REQ-001",
                case_name="Requirement prompt",
                prompt_name="requirement_analysis_prompt",
                status="passed",
            ),
            PromptRegressionCaseResult(
                case_id="PROMPT-RAG-001",
                case_name="RAG prompt",
                prompt_name="rag_answer_prompt",
                status="failed",
            ),
        ],
    )


def _build_passed_multi_agent_evaluation() -> dict:
    return {
        "status": "passed",
        "score": 1.0,
        "metrics": [
            {
                "name": "status_alignment",
                "status": "passed",
                "score": 1.0,
                "summary": "Status matched.",
            },
            {
                "name": "role_coverage",
                "status": "passed",
                "score": 1.0,
                "summary": "Roles matched.",
            },
        ],
        "metadata": {
            "evaluator": "multi-agent-qa-copilot-evaluator-v1",
            "passed_metrics": 2,
            "warning_metrics": 0,
            "failed_metrics": 0,
            "quality_gate": "approved",
        },
    }


def _build_failed_multi_agent_evaluation() -> dict:
    return {
        "status": "failed",
        "score": 0.5,
        "metrics": [
            {
                "name": "contract_validation",
                "status": "failed",
                "score": 0.0,
                "summary": "Contracts failed.",
            },
            {
                "name": "final_report",
                "status": "passed",
                "score": 1.0,
                "summary": "Final report passed.",
            },
        ],
        "metadata": {
            "evaluator": "multi-agent-qa-copilot-evaluator-v1",
            "passed_metrics": 1,
            "warning_metrics": 0,
            "failed_metrics": 1,
            "quality_gate": "blocked",
        },
    }


def test_ai_evaluation_report_aggregation_should_pass_when_all_sources_pass() -> None:
    service = AIEvaluationReportAggregationService()

    response = service.aggregate(
        AIEvaluationReportAggregationRequest(
            golden_dataset_run=_build_passed_golden_dataset_run(),
            prompt_regression_run=_build_passed_prompt_regression_run(),
            multi_agent_qa_copilot_evaluation=(
                _build_passed_multi_agent_evaluation()
            ),
            metadata={
                "source": "unit-test",
            },
        )
    )

    assert response.status == "passed"
    assert response.score == 1.0
    assert len(response.sections) == 3
    assert response.metadata["aggregator"] == (
        "ai-evaluation-report-aggregator-v1"
    )
    assert response.metadata["passed_sections"] == 3
    assert response.metadata["source"] == "unit-test"
    assert response.recommendations


def test_ai_evaluation_report_aggregation_should_warn_when_a_source_warns() -> None:
    service = AIEvaluationReportAggregationService()

    response = service.aggregate(
        AIEvaluationReportAggregationRequest(
            golden_dataset_run=_build_warning_golden_dataset_run(),
            prompt_regression_run=_build_passed_prompt_regression_run(),
        )
    )

    section_status_by_name = {
        section.name: section.status
        for section in response.sections
    }

    assert response.status == "warning"
    assert response.score == 0.75
    assert section_status_by_name["golden_dataset"] == "warning"
    assert section_status_by_name["prompt_regression"] == "passed"


def test_ai_evaluation_report_aggregation_should_fail_when_a_source_fails() -> None:
    service = AIEvaluationReportAggregationService()

    response = service.aggregate(
        AIEvaluationReportAggregationRequest(
            golden_dataset_run=_build_passed_golden_dataset_run(),
            prompt_regression_run=_build_failed_prompt_regression_run(),
            multi_agent_qa_copilot_evaluation=(
                _build_failed_multi_agent_evaluation()
            ),
        )
    )

    section_status_by_name = {
        section.name: section.status
        for section in response.sections
    }

    assert response.status == "failed"
    assert response.score == 0.6667
    assert section_status_by_name["prompt_regression"] == "failed"
    assert section_status_by_name["multi_agent_qa_copilot"] == "failed"
    assert response.metadata["failed_sections"] == 2
    assert any(
        "prompt outputs" in recommendation
        for recommendation in response.recommendations
    )


def test_ai_evaluation_report_aggregation_should_accept_only_one_source() -> None:
    service = AIEvaluationReportAggregationService()

    response = service.aggregate(
        AIEvaluationReportAggregationRequest(
            prompt_regression_run=_build_passed_prompt_regression_run(),
        )
    )

    assert response.status == "passed"
    assert response.score == 1.0
    assert len(response.sections) == 1
    assert response.sections[0].name == "prompt_regression"


def test_ai_evaluation_report_aggregation_request_should_reject_empty_sources() -> None:
    with pytest.raises(ValidationError):
        AIEvaluationReportAggregationRequest()
