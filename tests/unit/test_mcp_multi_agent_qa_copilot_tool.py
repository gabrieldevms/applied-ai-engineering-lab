from typing import Any
import pytest
from pydantic import ValidationError
from ai_api.mcp_server import run_multi_agent_qa_copilot_tool


class StubResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        return self.data


class StubMultiAgentQACopilotService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> StubResponse:
        self.last_request = request

        return StubResponse(
            {
                "status": "completed",
                "copilot_name": "multi-agent-qa-copilot-v1",
                "objective": request.objective
                or "Orchestrate a multi-agent QA analysis for the provided requirement.",
                "roles": [],
                "shared_state": {
                    "objective": request.objective
                    or "Orchestrate a multi-agent QA analysis for the provided requirement.",
                    "requirement_text": request.requirement_text,
                    "language": request.language,
                    "context": request.context,
                    "artifacts": [],
                    "messages": [],
                    "metadata": {
                        "source": "stub-service",
                    },
                },
                "task_results": [],
                "final_report": {
                    "summary": "Relatório multiagente gerado com sucesso.",
                    "requirement_understanding": [
                        "Requisito entendido pelo copilot.",
                    ],
                    "functional_coverage": [
                        "Cobertura funcional proposta.",
                    ],
                    "automation_strategy": [
                        "Estratégia de automação proposta.",
                    ],
                    "data_validation_evidence": [],
                    "review_notes": [
                        "Revisão concluída.",
                    ],
                    "next_steps": [
                        "Evoluir integração com agentes reais.",
                    ],
                    "metadata": {
                        "quality_gate": "approved",
                    },
                },
                "trace": [],
                "contract_validation": {
                    "status": "passed",
                    "total_contracts": 0,
                    "passed_contracts": 0,
                    "warning_contracts": 0,
                    "failed_contracts": 0,
                    "checks": [],
                    "metadata": {},
                },
                "failures": [],
                "conflict_analysis": {
                    "status": "passed",
                    "conflict_count": 0,
                    "warning_count": 0,
                    "critical_count": 0,
                    "conflicts": [],
                    "metadata": {},
                },
                "metadata": {
                    "source": "stub-service",
                    "data_validation_requested": request.data_validation is not None,
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
                ],
            }
        ],
        "max_rows": 100,
    }


def test_run_multi_agent_qa_copilot_tool_should_execute_service() -> None:
    service = StubMultiAgentQACopilotService()

    response = run_multi_agent_qa_copilot_tool(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        objective="Gerar análise QA multiagente.",
        language="pt-BR",
        context={
            "domain": "financial",
        },
        max_agents=6,
        failure_strategy="stop_on_failure",
        metadata={
            "source": "mcp-unit-test",
        },
        multi_agent_qa_copilot_service=service,
    )

    assert response["status"] == "completed"
    assert response["copilot_name"] == "multi-agent-qa-copilot-v1"
    assert response["objective"] == "Gerar análise QA multiagente."
    assert response["final_report"]["summary"]

    assert service.last_request is not None
    assert service.last_request.requirement_text == (
        "Como QA, preciso validar o saldo final por conta considerando "
        "depósitos e retiradas."
    )
    assert service.last_request.language == "pt-BR"
    assert service.last_request.context["domain"] == "financial"
    assert service.last_request.max_agents == 6
    assert service.last_request.failure_strategy == "stop_on_failure"
    assert service.last_request.metadata["source"] == "mcp-unit-test"


def test_run_multi_agent_qa_copilot_tool_should_accept_data_validation_context() -> None:
    service = StubMultiAgentQACopilotService()

    response = run_multi_agent_qa_copilot_tool(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        language="pt-BR",
        data_validation=_build_data_validation_payload(),
        multi_agent_qa_copilot_service=service,
    )

    assert response["status"] == "completed"
    assert response["metadata"]["data_validation_requested"] is True

    assert service.last_request is not None
    assert service.last_request.data_validation is not None
    assert (
        service.last_request.data_validation["database_schema"]["tables"][0]["name"]
        == "transactions"
    )
    assert (
        service.last_request.data_validation["table_data"][0]["table_name"]
        == "transactions"
    )


def test_run_multi_agent_qa_copilot_tool_should_reject_blank_requirement() -> None:
    service = StubMultiAgentQACopilotService()

    with pytest.raises(ValidationError):
        run_multi_agent_qa_copilot_tool(
            requirement_text="   ",
            language="pt-BR",
            multi_agent_qa_copilot_service=service,
        )


def test_run_multi_agent_qa_copilot_tool_should_reject_invalid_failure_strategy() -> None:
    service = StubMultiAgentQACopilotService()

    with pytest.raises(ValidationError):
        run_multi_agent_qa_copilot_tool(
            requirement_text="Como QA, preciso validar uma regra.",
            language="pt-BR",
            failure_strategy="invalid_strategy",
            multi_agent_qa_copilot_service=service,
        )
