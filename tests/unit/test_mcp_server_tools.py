from typing import Any
import pytest
from pydantic import ValidationError
from ai_api.llm import FakeLLMProvider
from ai_api.mcp_server import (
    analyze_requirement_tool,
    answer_with_rag_tool,
    get_project_status_tool,
    list_agent_tools_tool,
    list_specialized_agents_tool,
    retrieve_rag_context_tool,
    run_data_analyst_agent_tool,
    run_qa_agent_tool,
    run_sql_regression_suite_tool,
)
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.services import RequirementAnalyzerService


class StubResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def model_dump(self, mode: str = "json") -> dict[str, Any]:
        return self.data


class StubQAAgentService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> StubResponse:
        self.last_request = request

        return StubResponse(
            {
                "status": "completed",
                "agent_name": "qa-agent-v1",
                "requirement_text": request.requirement_text,
                "answer": "Análise de QA concluída com sucesso.",
                "requirement_analysis": {
                    "summary": "Resumo do requisito.",
                    "business_rules": [],
                    "acceptance_criteria": [],
                    "risks": [],
                    "positive_test_scenarios": [],
                    "negative_test_scenarios": [],
                    "edge_cases": [],
                    "open_questions": [],
                    "automation_opportunities": [],
                },
                "data_validation_selection": {
                    "decision": "skipped",
                    "reason": "No data validation context was required.",
                    "matched_signals": [],
                    "metadata": {
                        "mode": "auto",
                    },
                },
                "data_validation": None,
                "trace": [
                    {
                        "step_name": "requirement_analysis",
                        "status": "completed",
                    }
                ],
                "metadata": {
                    "source": "stub-qa-agent-service",
                },
            }
        )


class StubDataAnalystAgentService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> StubResponse:
        self.last_request = request

        return StubResponse(
            {
                "status": "completed",
                "agent_name": "data-analyst-agent-v1",
                "objective": request.objective,
                "answer": (
                    "A análise foi concluída com sucesso. "
                    "A consulta foi gerada, validada e executada."
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


class StubSQLWorkflowRegressionService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> StubResponse:
        self.last_request = request

        return StubResponse(
            {
                "suite_name": request.suite_name,
                "status": "passed",
                "total_scenarios": len(request.scenarios),
                "passed_scenarios": len(request.scenarios),
                "failed_scenarios": 0,
                "scenario_results": [
                    {
                        "scenario_id": request.scenarios[0].scenario_id,
                        "status": "passed",
                        "checks": [
                            {
                                "name": "expected_status",
                                "status": "passed",
                                "message": "Workflow status matched.",
                            }
                        ],
                    }
                ],
                "metadata": {
                    "source": "stub-sql-workflow-regression-service",
                },
            }
        )


def _build_requirement_analyzer_service() -> RequirementAnalyzerService:
    return RequirementAnalyzerService(
        llm_provider=FakeLLMProvider(
            response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
        ),
        retry_config=RetryConfig(max_attempts=2),
    )


def _build_documents() -> list[dict[str, Any]]:
    return [
        {
            "source": "billing-doc",
            "title": "Cobrança",
            "document_text": (
                "Boleto, cobrança, renegociação, dívida, pagamento, "
                "vencimento e saldo final por conta."
            ),
            "metadata": {
                "domain": "billing",
            },
        },
        {
            "source": "auth-doc",
            "title": "Autenticação",
            "document_text": "Login, senha, autenticação, usuário e sessão.",
            "metadata": {
                "domain": "auth",
            },
        },
    ]


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
            ],
        }
    ]


def _build_data_validation_payload() -> dict[str, Any]:
    return {
        "objective": "Validar saldo final por conta.",
        "mode": "required",
        "database_schema": _build_database_schema(),
        "table_data": _build_table_data(),
        "max_rows": 100,
    }


def _build_sql_regression_suite() -> dict[str, Any]:
    return {
        "suite_name": "mcp-sql-regression-suite",
        "metadata": {
            "source": "mcp-test",
        },
        "scenarios": [
            {
                "scenario_id": "final-account-balance",
                "name": "Final account balance",
                "description": (
                    "Validate final account balance by account using "
                    "deposits and withdrawals."
                ),
                "request": {
                    "question": "Qual é o saldo final por conta?",
                    "language": "pt-BR",
                    "max_rows": 100,
                    "database_schema": _build_database_schema(),
                    "table_data": _build_table_data(),
                },
                "expected_result": {
                    "expected_status": "executed",
                    "expected_row_count": 1,
                    "expected_columns": [
                        "account_id",
                        "final_balance",
                    ],
                    "expected_rows": [
                        {
                            "account_id": 101,
                            "final_balance": 25.0,
                        }
                    ],
                },
            }
        ],
    }


def test_get_project_status_tool_should_return_m5_status() -> None:
    response = get_project_status_tool()

    assert response["project"] == "applied-ai-engineering-lab"
    assert response["status"] == "m5_mcp_qa_server_in_progress"
    assert response["current_milestone"] == "M5 — MCP QA Server"
    assert "AI Agents" in response["completed_foundations"]
    assert "Data Analyst Agent Foundation" in response["completed_foundations"]
    assert "MCP Server Foundation" in response["completed_foundations"]
    assert "Requirement Analysis MCP Tool" in response["completed_foundations"]
    assert "RAG MCP Tools" in response["completed_foundations"]
    assert "QA Agent MCP Tool" in response["completed_foundations"]
    assert "Data Analyst Agent MCP Tool" in response["completed_foundations"]
    assert "analyze_requirement" in response["available_mcp_tools"]
    assert "retrieve_rag_context" in response["available_mcp_tools"]
    assert "answer_with_rag" in response["available_mcp_tools"]
    assert "run_qa_agent" in response["available_mcp_tools"]
    assert "run_data_analyst_agent" in response["available_mcp_tools"]
    assert "run_sql_regression_suite" in response["available_mcp_tools"]
    assert "qa-agent-v1" in response["available_specialized_agents"]
    assert "data-analyst-agent-v1" in response["available_specialized_agents"]


def test_list_agent_tools_tool_should_return_registered_tools() -> None:
    response = list_agent_tools_tool()

    tool_names = [
        tool["name"]
        for tool in response["tools"]
    ]

    assert response["total_tools"] == 4
    assert "rag.retrieve" in tool_names
    assert "rag.answer" in tool_names
    assert "requirements.analyze" in tool_names
    assert "data_analysis.agent.run" in tool_names
    assert response["metadata"]["registry"] == "agent-tool-registry-v1"


def test_list_specialized_agents_tool_should_return_registered_agents() -> None:
    response = list_specialized_agents_tool()

    agent_names = [
        agent["name"]
        for agent in response["agents"]
    ]

    assert response["agent_count"] == 2
    assert "qa-agent-v1" in agent_names
    assert "data-analyst-agent-v1" in agent_names
    assert response["metadata"]["registry"] == "specialized-agent-registry-v1"


def test_analyze_requirement_tool_should_return_structured_analysis() -> None:
    response = analyze_requirement_tool(
        requirement_text=(
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        language="pt-BR",
        analyzer_service=_build_requirement_analyzer_service(),
    )

    assert response["summary"]
    assert isinstance(response["business_rules"], list)
    assert isinstance(response["acceptance_criteria"], list)
    assert isinstance(response["risks"], list)
    assert isinstance(response["positive_test_scenarios"], list)
    assert isinstance(response["negative_test_scenarios"], list)
    assert isinstance(response["edge_cases"], list)
    assert isinstance(response["open_questions"], list)
    assert isinstance(response["automation_opportunities"], list)
    assert set(response.keys()) >= {
        "summary",
        "business_rules",
        "acceptance_criteria",
        "risks",
        "positive_test_scenarios",
        "negative_test_scenarios",
        "edge_cases",
        "open_questions",
        "automation_opportunities",
    }


def test_analyze_requirement_tool_should_reject_blank_requirement() -> None:
    with pytest.raises(ValidationError):
        analyze_requirement_tool(
            requirement_text="",
            language="pt-BR",
            analyzer_service=_build_requirement_analyzer_service(),
        )


def test_retrieve_rag_context_tool_should_return_relevant_chunks() -> None:
    response = retrieve_rag_context_tool(
        query="Como funciona a renegociação por boleto?",
        documents=_build_documents(),
        top_k=1,
        chunk_size=200,
        chunk_overlap=40,
    )

    assert response["total_retrieved_chunks"] == 1
    assert len(response["retrieved_chunks"]) == 1

    retrieved_chunk = response["retrieved_chunks"][0]
    serialized_chunk = str(retrieved_chunk).lower()

    assert "billing" in serialized_chunk or "cobrança" in serialized_chunk
    assert "boleto" in serialized_chunk


def test_answer_with_rag_tool_should_return_grounded_answer() -> None:
    response = answer_with_rag_tool(
        query="Como funciona a renegociação por boleto?",
        documents=_build_documents(),
        language="pt-BR",
        top_k=1,
        chunk_size=200,
        chunk_overlap=40,
    )

    assert response["answer"]
    assert isinstance(response["citations"], list)


def test_run_qa_agent_tool_should_execute_qa_agent_service() -> None:
    service = StubQAAgentService()

    response = run_qa_agent_tool(
        requirement_text=(
            "Como QA, preciso validar o fluxo de renegociação de dívida."
        ),
        language="pt-BR",
        max_steps=6,
        qa_agent_service=service,
    )

    assert response["status"] == "completed"
    assert response["agent_name"] == "qa-agent-v1"
    assert response["answer"] == "Análise de QA concluída com sucesso."
    assert service.last_request is not None
    assert service.last_request.requirement_text == (
        "Como QA, preciso validar o fluxo de renegociação de dívida."
    )
    assert service.last_request.language == "pt-BR"
    assert service.last_request.max_steps == 6


def test_run_qa_agent_tool_should_accept_data_validation_context() -> None:
    service = StubQAAgentService()

    response = run_qa_agent_tool(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta "
            "considerando depósitos e retiradas."
        ),
        language="pt-BR",
        max_steps=6,
        data_validation=_build_data_validation_payload(),
        qa_agent_service=service,
    )

    assert response["status"] == "completed"
    assert service.last_request is not None

    request_dump = service.last_request.model_dump(mode="json")

    assert request_dump["data_validation"]["mode"] == "required"
    assert (
        request_dump["data_validation"]["database_schema"]["tables"][0]["name"]
        == "transactions"
    )
    assert (
        request_dump["data_validation"]["table_data"][0]["table_name"]
        == "transactions"
    )


def test_run_data_analyst_agent_tool_should_execute_data_analyst_service() -> None:
    service = StubDataAnalystAgentService()

    response = run_data_analyst_agent_tool(
        objective="Calcule o saldo final por conta.",
        language="pt-BR",
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
        max_rows=100,
        metadata={
            "source": "mcp-test",
        },
        data_analyst_agent_service=service,
    )

    assert response["status"] == "completed"
    assert response["agent_name"] == "data-analyst-agent-v1"
    assert response["objective"] == "Calcule o saldo final por conta."
    assert response["workflow"]["status"] == "executed"
    assert response["evidence"]["row_count"] == 2

    assert service.last_request is not None
    assert service.last_request.objective == "Calcule o saldo final por conta."
    assert service.last_request.language == "pt-BR"
    assert service.last_request.max_rows == 100

    request_dump = service.last_request.model_dump(mode="json")

    assert request_dump["database_schema"]["tables"][0]["name"] == "transactions"
    assert request_dump["table_data"][0]["table_name"] == "transactions"
    assert request_dump["metadata"]["source"] == "mcp-test"


def test_run_data_analyst_agent_tool_should_reject_invalid_payload() -> None:
    service = StubDataAnalystAgentService()

    with pytest.raises(ValidationError):
        run_data_analyst_agent_tool(
            objective="",
            language="pt-BR",
            database_schema=_build_database_schema(),
            table_data=_build_table_data(),
            max_rows=100,
            data_analyst_agent_service=service,
        )


def test_run_sql_regression_suite_tool_should_execute_regression_service() -> None:
    service = StubSQLWorkflowRegressionService()

    response = run_sql_regression_suite_tool(
        suite=_build_sql_regression_suite(),
        sql_workflow_regression_service=service,
    )

    assert response["suite_name"] == "mcp-sql-regression-suite"
    assert response["status"] == "passed"
    assert response["total_scenarios"] == 1
    assert response["passed_scenarios"] == 1
    assert response["failed_scenarios"] == 0
    assert response["scenario_results"][0]["scenario_id"] == (
        "final-account-balance"
    )

    assert service.last_request is not None
    assert service.last_request.suite_name == "mcp-sql-regression-suite"

    request_dump = service.last_request.model_dump(mode="json")

    assert request_dump["metadata"]["source"] == "mcp-test"
    assert request_dump["scenarios"][0]["scenario_id"] == "final-account-balance"
    assert (
        request_dump["scenarios"][0]["request"]["database_schema"]["tables"][0]["name"]
        == "transactions"
    )


def test_run_sql_regression_suite_tool_should_reject_invalid_suite() -> None:
    service = StubSQLWorkflowRegressionService()

    with pytest.raises(ValidationError):
        run_sql_regression_suite_tool(
            suite={},
            sql_workflow_regression_service=service,
        )
