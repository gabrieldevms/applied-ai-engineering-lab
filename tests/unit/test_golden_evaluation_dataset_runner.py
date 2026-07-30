from typing import Any
from ai_api.evals import (
    EvaluationExpectation,
    EvaluationScenario,
    GoldenEvaluationDataset,
    GoldenEvaluationDatasetRunRequest,
    GoldenEvaluationDatasetRunnerService,
    build_default_golden_evaluation_dataset,
)


class StubModelResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        return self.data


class StubToolExecutionResponse:
    def __init__(self, output: dict[str, Any]) -> None:
        self.output = output


class StubRequirementAnalyzerService:
    def analyze(
        self,
        requirement_text: str,
        language: str,
    ) -> StubModelResponse:
        return StubModelResponse(
            {
                "status": "completed",
                "summary": "Requirement analyzed.",
                "business_rules": [
                    "Business rule identified.",
                ],
                "acceptance_criteria": [
                    "Acceptance criterion identified.",
                ],
                "positive_test_scenarios": [
                    "Positive scenario identified.",
                ],
                "negative_test_scenarios": [
                    "Negative scenario identified.",
                ],
                "edge_cases": [
                    "Edge case identified.",
                ],
            }
        )


class StubToolExecutionService:
    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        metadata: dict[str, Any],
    ) -> StubToolExecutionResponse:
        return StubToolExecutionResponse(
            {
                "status": "completed",
                "answer": "Boleto must be registered before customer delivery.",
                "citations": [
                    {
                        "source": "billing-policy.md",
                    }
                ],
                "retrieved_chunks": [
                    {
                        "content": "Boletos devem ser registrados.",
                    }
                ],
            }
        )


class StubQAAgentService:
    def run(self, request: Any) -> StubModelResponse:
        return StubModelResponse(
            {
                "status": "completed",
                "requirement_analysis": {
                    "summary": "QA analysis completed.",
                },
                "trace": [],
                "metadata": {
                    "source": "stub-qa-agent-service",
                },
            }
        )


class StubDataAnalystAgentService:
    def run(self, request: Any) -> StubModelResponse:
        return StubModelResponse(
            {
                "status": "completed",
                "workflow": {
                    "status": "executed",
                },
                "evidence": {
                    "row_count": 2,
                    "column_count": 2,
                },
                "trace": [],
                "metadata": {
                    "source": "stub-data-analyst-agent-service",
                },
            }
        )


class StubMultiAgentQACopilotService:
    def run(self, request: Any) -> StubModelResponse:
        return StubModelResponse(
            {
                "status": "completed",
                "roles": [],
                "shared_state": {},
                "task_results": [],
                "final_report": {
                    "summary": "Final report generated.",
                    "metadata": {
                        "quality_gate": "approved",
                    },
                },
                "trace": [],
                "contract_validation": {
                    "status": "passed",
                },
                "conflict_analysis": {
                    "status": "passed",
                },
                "metadata": {
                    "contract_validation_status": "passed",
                    "conflict_analysis_status": "passed",
                },
            }
        )


def _build_runner() -> GoldenEvaluationDatasetRunnerService:
    return GoldenEvaluationDatasetRunnerService(
        requirement_analyzer_service=StubRequirementAnalyzerService(),
        tool_execution_service=StubToolExecutionService(),
        qa_agent_service=StubQAAgentService(),
        data_analyst_agent_service=StubDataAnalystAgentService(),
        multi_agent_qa_copilot_service=StubMultiAgentQACopilotService(),
    )


def test_golden_evaluation_dataset_runner_should_pass_default_dataset_with_stub_services() -> None:
    runner = _build_runner()

    response = runner.run(
        GoldenEvaluationDatasetRunRequest(
            dataset=build_default_golden_evaluation_dataset(),
        )
    )

    assert response.status == "passed"
    assert response.scenario_count == 6
    assert response.executed_count == 6
    assert response.passed_count == 6
    assert response.failed_count == 0
    assert response.skipped_count == 0

    result_status_by_id = {
        result.scenario_id: result.status
        for result in response.results
    }

    assert result_status_by_id["REQ-001"] == "passed"
    assert result_status_by_id["RAG-001"] == "passed"
    assert result_status_by_id["QA-001"] == "passed"
    assert result_status_by_id["DATA-001"] == "passed"
    assert result_status_by_id["MULTI-001"] == "passed"
    assert result_status_by_id["MCP-001"] == "passed"


def test_golden_evaluation_dataset_runner_should_filter_by_scenario_id() -> None:
    runner = _build_runner()

    response = runner.run(
        GoldenEvaluationDatasetRunRequest(
            dataset=build_default_golden_evaluation_dataset(),
            scenario_ids=[
                "REQ-001",
                "MCP-001",
            ],
        )
    )

    scenario_ids = [
        result.scenario_id
        for result in response.results
    ]

    assert response.status == "passed"
    assert response.scenario_count == 2
    assert scenario_ids == [
        "REQ-001",
        "MCP-001",
    ]


def test_golden_evaluation_dataset_runner_should_filter_by_scenario_type() -> None:
    runner = _build_runner()

    response = runner.run(
        GoldenEvaluationDatasetRunRequest(
            dataset=build_default_golden_evaluation_dataset(),
            scenario_types=[
                "multi_agent_qa_copilot",
            ],
        )
    )

    assert response.status == "passed"
    assert response.scenario_count == 1
    assert response.results[0].scenario_id == "MULTI-001"
    assert response.results[0].scenario_type == "multi_agent_qa_copilot"


def test_golden_evaluation_dataset_runner_should_skip_scenarios_in_dry_run() -> None:
    runner = _build_runner()

    response = runner.run(
        GoldenEvaluationDatasetRunRequest(
            dataset=build_default_golden_evaluation_dataset(),
            dry_run=True,
        )
    )

    assert response.status == "warning"
    assert response.scenario_count == 6
    assert response.executed_count == 0
    assert response.skipped_count == 6

    assert all(
        result.status == "skipped"
        for result in response.results
    )


def test_golden_evaluation_dataset_runner_should_skip_when_handler_is_not_configured() -> None:
    runner = GoldenEvaluationDatasetRunnerService()

    response = runner.run(
        GoldenEvaluationDatasetRunRequest(
            dataset=build_default_golden_evaluation_dataset(),
            scenario_ids=[
                "REQ-001",
            ],
        )
    )

    assert response.status == "warning"
    assert response.scenario_count == 1
    assert response.executed_count == 0
    assert response.skipped_count == 1
    assert response.results[0].status == "skipped"
    assert "RequirementAnalyzerService" in response.results[0].error_message


def test_golden_evaluation_dataset_runner_should_fail_when_required_marker_is_missing() -> None:
    runner = GoldenEvaluationDatasetRunnerService(
        requirement_analyzer_service=StubRequirementAnalyzerService(),
    )

    dataset = GoldenEvaluationDataset(
        name="custom-dataset",
        version="0.1.0",
        description="Dataset with missing required marker.",
        scenarios=[
            EvaluationScenario(
                id="REQ-MISSING-MARKER",
                name="Requirement marker validation",
                type="requirement_analysis",
                description="Should fail because the required marker is missing.",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                    "language": "pt-BR",
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "summary",
                        "missing_marker",
                    ],
                ),
            )
        ],
    )

    response = runner.run(
        GoldenEvaluationDatasetRunRequest(
            dataset=dataset,
        )
    )

    assert response.status == "failed"
    assert response.failed_count == 1
    assert response.results[0].status == "failed"

    marker_check = [
        check
        for check in response.results[0].checks
        if check.name == "required_output_markers"
    ][0]

    assert marker_check.status == "failed"
    assert marker_check.metadata["missing_markers"] == [
        "missing_marker",
    ]
