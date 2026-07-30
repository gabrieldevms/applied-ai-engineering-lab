from typing import Any
from ai_api.multi_agent import (
    MultiAgentQACopilotEvaluationRequest,
    MultiAgentQACopilotEvaluationService,
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotService,
)


class StubDataAnalystAgentResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        return self.data


class StubDataAnalystAgentService:
    def run(self, request: Any) -> StubDataAnalystAgentResponse:
        return StubDataAnalystAgentResponse(
            {
                "status": "completed",
                "agent_name": "data-analyst-agent-v1",
                "objective": request.objective,
                "answer": "A análise foi concluída com sucesso.",
                "workflow": {
                    "status": "executed",
                    "generated_sql": "SELECT account_id FROM transactions",
                },
                "evidence": {
                    "row_count": 2,
                    "column_count": 1,
                },
                "trace": [],
                "metadata": {
                    "source": "stub-data-analyst-agent-service",
                },
            }
        )


def _build_data_validation_payload() -> dict[str, Any]:
    return {
        "objective": "Validar saldo final por conta.",
        "database_schema": {
            "name": "qa_database",
            "description": "Database used for QA validation.",
            "tables": [
                {
                    "name": "transactions",
                    "description": "Financial transactions.",
                    "columns": [
                        {
                            "name": "transaction_id",
                            "data_type": "integer",
                            "nullable": False,
                            "primary_key": True,
                        },
                        {
                            "name": "account_id",
                            "data_type": "integer",
                            "nullable": False,
                        },
                        {
                            "name": "amount",
                            "data_type": "decimal",
                            "nullable": False,
                        },
                        {
                            "name": "transaction_type",
                            "data_type": "varchar",
                            "nullable": False,
                        },
                    ],
                }
            ],
        },
        "table_data": [
            {
                "table_name": "transactions",
                "rows": [
                    {
                        "transaction_id": 123,
                        "account_id": 101,
                        "amount": 10.0,
                        "transaction_type": "Deposit",
                    }
                ],
            }
        ],
        "max_rows": 100,
    }


def _find_metric(
    response_status: Any,
    metric_name: str,
) -> Any:
    for metric in response_status.metrics:
        if metric.name == metric_name:
            return metric

    raise AssertionError(f"Metric not found: {metric_name}")


def test_multi_agent_qa_copilot_evaluation_should_pass_clean_response() -> None:
    copilot_service = MultiAgentQACopilotService()
    evaluation_service = MultiAgentQACopilotEvaluationService()

    copilot_response = copilot_service.run(
        MultiAgentQACopilotRequest(
            requirement_text=(
                "Como QA, preciso validar o saldo final por conta considerando "
                "depósitos e retiradas."
            ),
            language="pt-BR",
        )
    )

    evaluation_response = evaluation_service.evaluate(
        MultiAgentQACopilotEvaluationRequest(
            response=copilot_response,
            expected_status="completed",
            expected_quality_gate="approved",
        )
    )

    assert evaluation_response.status == "passed"
    assert evaluation_response.score == 1.0
    assert evaluation_response.metadata["evaluator"] == (
        "multi-agent-qa-copilot-evaluator-v1"
    )

    metric_names = [
        metric.name
        for metric in evaluation_response.metrics
    ]

    assert metric_names == [
        "status_alignment",
        "role_coverage",
        "trace_integrity",
        "contract_validation",
        "failure_control",
        "conflict_control",
        "final_report",
        "data_validation_evidence",
    ]


def test_multi_agent_qa_copilot_evaluation_should_fail_when_status_does_not_match() -> None:
    copilot_service = MultiAgentQACopilotService()
    evaluation_service = MultiAgentQACopilotEvaluationService()

    copilot_response = copilot_service.run(
        MultiAgentQACopilotRequest(
            requirement_text="Como usuário, quero consultar meus pagamentos.",
            language="pt-BR",
        )
    )

    evaluation_response = evaluation_service.evaluate(
        MultiAgentQACopilotEvaluationRequest(
            response=copilot_response,
            expected_status="failed",
        )
    )

    status_metric = _find_metric(
        response_status=evaluation_response,
        metric_name="status_alignment",
    )

    assert evaluation_response.status == "failed"
    assert status_metric.status == "failed"
    assert status_metric.metadata["actual_status"] == "completed"
    assert status_metric.metadata["expected_status"] == "failed"


def test_multi_agent_qa_copilot_evaluation_should_fail_when_data_evidence_is_required_but_missing() -> None:
    copilot_service = MultiAgentQACopilotService()
    evaluation_service = MultiAgentQACopilotEvaluationService()

    copilot_response = copilot_service.run(
        MultiAgentQACopilotRequest(
            requirement_text="Como usuário, quero consultar meus pagamentos.",
            language="pt-BR",
        )
    )

    evaluation_response = evaluation_service.evaluate(
        MultiAgentQACopilotEvaluationRequest(
            response=copilot_response,
            require_data_validation_evidence=True,
        )
    )

    data_metric = _find_metric(
        response_status=evaluation_response,
        metric_name="data_validation_evidence",
    )

    assert evaluation_response.status == "failed"
    assert data_metric.status == "failed"
    assert data_metric.metadata["required"] is True
    assert data_metric.metadata["artifact_found"] is False


def test_multi_agent_qa_copilot_evaluation_should_pass_when_data_evidence_is_required_and_available() -> None:
    copilot_service = MultiAgentQACopilotService(
        data_analyst_agent_service=StubDataAnalystAgentService(),
    )
    evaluation_service = MultiAgentQACopilotEvaluationService()

    copilot_response = copilot_service.run(
        MultiAgentQACopilotRequest(
            requirement_text=(
                "Como QA, preciso validar o saldo final por conta considerando "
                "depósitos e retiradas."
            ),
            language="pt-BR",
            data_validation=_build_data_validation_payload(),
        )
    )

    evaluation_response = evaluation_service.evaluate(
        MultiAgentQACopilotEvaluationRequest(
            response=copilot_response,
            expected_status="completed",
            expected_quality_gate="approved",
            require_data_validation_evidence=True,
        )
    )

    data_metric = _find_metric(
        response_status=evaluation_response,
        metric_name="data_validation_evidence",
    )

    assert evaluation_response.status == "passed"
    assert data_metric.status == "passed"
    assert data_metric.metadata["artifact_found"] is True
    assert data_metric.metadata["artifact_status"] == "completed"
    assert data_metric.metadata["report_evidence_count"] > 0
