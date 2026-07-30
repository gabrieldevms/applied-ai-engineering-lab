from ai_api.evals import (
    CIEvaluationPipelineRunRequest,
    CIEvaluationPipelineService,
)


def test_ci_evaluation_pipeline_should_pass_all_default_deterministic_stages() -> None:
    service = CIEvaluationPipelineService()

    response = service.run(
        CIEvaluationPipelineRunRequest(
            metadata={
                "source": "unit-test",
            },
        )
    )

    stage_names = [
        stage.name
        for stage in response.stages
    ]

    assert response.status == "passed"
    assert response.stage_count == 8
    assert response.passed_count == 8
    assert response.warning_count == 0
    assert response.failed_count == 0
    assert response.should_fail_ci is False
    assert response.score is not None
    assert response.score >= 0.98

    assert stage_names == [
        "golden_dataset_smoke",
        "prompt_regression",
        "llm_output_evaluation",
        "rag_regression",
        "agent_regression",
        "tool_calling_evaluation",
        "multi_agent_copilot_regression",
        "llm_as_judge_evaluation",
    ]

    assert response.metadata["runner"] == "ci-evaluation-pipeline-v1"
    assert response.metadata["external_llm_required"] is False
    assert response.metadata["source"] == "unit-test"


def test_ci_evaluation_pipeline_should_allow_skipping_optional_stages() -> None:
    service = CIEvaluationPipelineService()

    response = service.run(
        CIEvaluationPipelineRunRequest(
            include_golden_dataset_smoke=False,
            include_llm_as_judge_evaluation=False,
        )
    )

    stage_names = [
        stage.name
        for stage in response.stages
    ]

    assert response.status == "passed"
    assert response.stage_count == 6
    assert "golden_dataset_smoke" not in stage_names
    assert "llm_as_judge_evaluation" not in stage_names


def test_ci_evaluation_pipeline_should_set_should_fail_ci_when_failed() -> None:
    service = CIEvaluationPipelineService()

    response = service.run(
        CIEvaluationPipelineRunRequest(
            include_golden_dataset_smoke=False,
            include_prompt_regression=False,
            include_llm_output_evaluation=False,
            include_rag_regression=False,
            include_agent_regression=False,
            include_tool_calling_evaluation=False,
            include_multi_agent_copilot_regression=False,
            include_llm_as_judge_evaluation=False,
        )
    )

    assert response.status == "passed"
    assert response.stage_count == 0
    assert response.should_fail_ci is False
    assert response.score is None
