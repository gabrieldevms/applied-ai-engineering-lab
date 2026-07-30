import pytest
from pydantic import ValidationError
from ai_api.evals import (
    EvaluationExpectation,
    EvaluationScenario,
    GoldenEvaluationDataset,
    GoldenEvaluationDatasetService,
    GoldenEvaluationDatasetValidationService,
    build_default_golden_evaluation_dataset,
)


def test_default_golden_evaluation_dataset_should_include_required_scenario_types() -> None:
    dataset = build_default_golden_evaluation_dataset()

    scenario_types = {
        scenario.type
        for scenario in dataset.scenarios
    }

    assert dataset.name == "applied-ai-engineering-lab-golden-evaluation-dataset"
    assert dataset.version == "0.1.0"
    assert len(dataset.scenarios) == 6

    assert scenario_types == {
        "requirement_analysis",
        "rag_answer",
        "qa_agent",
        "data_analyst_agent",
        "multi_agent_qa_copilot",
        "mcp_tool",
    }


def test_golden_evaluation_dataset_service_should_return_default_dataset() -> None:
    service = GoldenEvaluationDatasetService()

    dataset = service.get_default_dataset()

    assert dataset.scenarios
    assert dataset.metadata["dataset_type"] == "golden_regression_dataset"
    assert dataset.metadata["execution_mode"] == "definition_only"


def test_golden_evaluation_dataset_validation_should_pass_default_dataset() -> None:
    service = GoldenEvaluationDatasetValidationService()
    dataset = build_default_golden_evaluation_dataset()

    response = service.validate(dataset)

    assert response.status == "valid"
    assert response.dataset_name == dataset.name
    assert response.dataset_version == dataset.version
    assert response.scenario_count == 6
    assert response.missing_required_types == []

    metric_status_by_name = {
        metric.name: metric.status
        for metric in response.metrics
    }

    assert metric_status_by_name["non_empty_dataset"] == "passed"
    assert metric_status_by_name["unique_scenario_ids"] == "passed"
    assert metric_status_by_name["required_type_coverage"] == "passed"
    assert metric_status_by_name["scenario_inputs"] == "passed"
    assert metric_status_by_name["scenario_expectations"] == "passed"


def test_golden_evaluation_dataset_validation_should_fail_when_required_type_is_missing() -> None:
    service = GoldenEvaluationDatasetValidationService()

    dataset = GoldenEvaluationDataset(
        name="custom-dataset",
        version="0.1.0",
        description="Dataset missing required coverage.",
        scenarios=[
            EvaluationScenario(
                id="REQ-ONLY",
                name="Requirement only scenario",
                type="requirement_analysis",
                description="Only covers requirement analysis.",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                    "language": "pt-BR",
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                ),
            )
        ],
    )

    response = service.validate(dataset)

    assert response.status == "invalid"
    assert "rag_answer" in response.missing_required_types
    assert "qa_agent" in response.missing_required_types
    assert "data_analyst_agent" in response.missing_required_types
    assert "multi_agent_qa_copilot" in response.missing_required_types
    assert "mcp_tool" in response.missing_required_types


def test_golden_evaluation_dataset_validation_should_fail_for_duplicate_ids() -> None:
    service = GoldenEvaluationDatasetValidationService()

    dataset = GoldenEvaluationDataset(
        name="duplicate-dataset",
        version="0.1.0",
        description="Dataset with duplicate scenario IDs.",
        scenarios=[
            EvaluationScenario(
                id="DUP-001",
                name="First scenario",
                type="requirement_analysis",
                description="First scenario.",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                    "language": "pt-BR",
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                ),
            ),
            EvaluationScenario(
                id="DUP-001",
                name="Second scenario",
                type="rag_answer",
                description="Second scenario.",
                input_payload={
                    "query": "Qual é a regra?",
                    "documents": [
                        {
                            "id": "doc-1",
                            "text": "Regra de teste.",
                        }
                    ],
                },
                expectations=EvaluationExpectation(
                    required_output_markers=[
                        "answer",
                    ],
                ),
            ),
        ],
    )

    response = service.validate(dataset)

    assert response.status == "invalid"

    duplicate_metric = [
        metric
        for metric in response.metrics
        if metric.name == "unique_scenario_ids"
    ][0]

    assert duplicate_metric.status == "failed"
    assert duplicate_metric.metadata["duplicate_ids"] == [
        "DUP-001",
    ]


def test_evaluation_scenario_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        EvaluationScenario(
            id="INVALID-001",
            name="Invalid scenario",
            type="requirement_analysis",
            description="Invalid scenario.",
            input_payload={},
        )
