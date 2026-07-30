from typing import Any
from ai_api.multi_agent import (
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotService,
    MultiAgentSharedState,
)


class StubDataAnalystAgentResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        return self.data


class StubDataAnalystAgentService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> StubDataAnalystAgentResponse:
        self.last_request = request

        return StubDataAnalystAgentResponse(
            {
                "status": "completed",
                "agent_name": "data-analyst-agent-v1",
                "objective": request.objective,
                "answer": (
                    "A análise foi concluída com sucesso. A consulta foi "
                    "gerada, validada e executada."
                ),
                "workflow": {
                    "status": "executed",
                    "generated_sql": (
                        "SELECT account_id, "
                        "SUM(CASE WHEN transaction_type = 'Deposit' "
                        "THEN amount ELSE -amount END) AS final_balance "
                        "FROM transactions GROUP BY account_id"
                    ),
                },
                "evidence": {
                    "row_count": 2,
                    "column_count": 2,
                },
                "trace": [
                    {
                        "step_name": "sql_workflow",
                        "status": "completed",
                    }
                ],
                "metadata": {
                    "source": "stub-data-analyst-agent-service",
                },
            }
        )


def _build_database_schema() -> dict[str, Any]:
    return {
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
    }


def _build_table_data() -> list[dict[str, Any]]:
    return [
        {
            "table_name": "transactions",
            "rows": [
                {
                    "transaction_id": 123,
                    "account_id": 101,
                    "amount": 10.0,
                    "transaction_type": "Deposit",
                },
                {
                    "transaction_id": 124,
                    "account_id": 101,
                    "amount": 20.0,
                    "transaction_type": "Deposit",
                },
                {
                    "transaction_id": 125,
                    "account_id": 101,
                    "amount": 5.0,
                    "transaction_type": "Withdrawal",
                },
                {
                    "transaction_id": 126,
                    "account_id": 201,
                    "amount": 20.0,
                    "transaction_type": "Deposit",
                },
                {
                    "transaction_id": 128,
                    "account_id": 201,
                    "amount": 10.0,
                    "transaction_type": "Withdrawal",
                },
            ],
        }
    ]


def _find_artifact_content(
    shared_state: MultiAgentSharedState,
    artifact_name: str,
) -> dict[str, Any]:
    for artifact in shared_state.artifacts:
        if artifact.name == artifact_name:
            return artifact.content

    return {}


def _find_artifact_metadata(
    shared_state: MultiAgentSharedState,
    artifact_name: str,
) -> dict[str, Any]:
    for artifact in shared_state.artifacts:
        if artifact.name == artifact_name:
            return artifact.metadata

    return {}


def test_multi_agent_copilot_should_use_data_validation_capability_when_requested() -> None:
    data_analyst_service = StubDataAnalystAgentService()
    service = MultiAgentQACopilotService(
        data_analyst_agent_service=data_analyst_service,
    )

    request = MultiAgentQACopilotRequest(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        language="pt-BR",
        data_validation={
            "objective": "Validar saldo final por conta.",
            "database_schema": _build_database_schema(),
            "table_data": _build_table_data(),
            "max_rows": 100,
            "metadata": {
                "source": "unit-test",
            },
        },
    )

    response = service.run(request)

    data_validation_analysis = _find_artifact_content(
        shared_state=response.shared_state,
        artifact_name="data_validation_analysis",
    )
    data_validation_metadata = _find_artifact_metadata(
        shared_state=response.shared_state,
        artifact_name="data_validation_analysis",
    )

    assert response.status == "completed"
    assert data_validation_analysis["status"] == "completed"
    assert data_validation_analysis["agent_name"] == "data-analyst-agent-v1"
    assert data_validation_analysis["workflow"]["status"] == "executed"
    assert data_validation_analysis["evidence"]["row_count"] == 2
    assert data_validation_metadata["source"] == "data_analyst_agent_service"
    assert data_validation_metadata["executed"] is True

    assert data_analyst_service.last_request is not None
    assert data_analyst_service.last_request.objective == (
        "Validar saldo final por conta."
    )
    assert data_analyst_service.last_request.language == "pt-BR"
    assert data_analyst_service.last_request.max_rows == 100

    assert response.metadata["data_validation_requested"] is True
    assert response.metadata["data_validation_available"] is True
    assert response.final_report.metadata["data_validation_available"] is True
    assert response.final_report.data_validation_evidence


def test_multi_agent_copilot_should_skip_data_validation_when_service_is_not_configured() -> None:
    service = MultiAgentQACopilotService()

    request = MultiAgentQACopilotRequest(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        language="pt-BR",
        data_validation={
            "objective": "Validar saldo final por conta.",
            "database_schema": _build_database_schema(),
            "table_data": _build_table_data(),
            "max_rows": 100,
        },
    )

    response = service.run(request)

    data_validation_analysis = _find_artifact_content(
        shared_state=response.shared_state,
        artifact_name="data_validation_analysis",
    )

    assert response.status == "completed"
    assert data_validation_analysis["status"] == "skipped"
    assert "no Data Analyst Agent service was configured" in (
        data_validation_analysis["reason"]
    )
    assert response.metadata["data_validation_requested"] is True
    assert response.metadata["data_validation_available"] is True
    assert response.final_report.data_validation_evidence


def test_multi_agent_copilot_should_not_add_data_validation_artifact_when_not_requested() -> None:
    service = MultiAgentQACopilotService()

    request = MultiAgentQACopilotRequest(
        requirement_text="Como usuário, quero consultar meus pagamentos.",
        language="pt-BR",
    )

    response = service.run(request)

    data_validation_analysis = _find_artifact_content(
        shared_state=response.shared_state,
        artifact_name="data_validation_analysis",
    )

    assert data_validation_analysis == {}
    assert response.metadata["data_validation_requested"] is False
    assert response.metadata["data_validation_available"] is False
    assert response.final_report.metadata["data_validation_available"] is False
    assert response.final_report.data_validation_evidence == []
