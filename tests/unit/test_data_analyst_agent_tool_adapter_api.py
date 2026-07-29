from fastapi.testclient import TestClient
from ai_api.agents import (
    AgentRuntime,
    DataAnalystAgentTool,
    ToolExecutionService,
)
from ai_api.agents.dependencies import (
    get_agent_runtime,
    get_tool_execution_service,
)
from ai_api.data_analysis import (
    DataAnalystAgentService,
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    SQLiteReadOnlyQueryExecutor,
)
from ai_api.llm import FakeLLMProvider
from ai_api.main import app


client = TestClient(app)


VALID_SQL_RESPONSE_JSON = """
{
  "sql": "SELECT account_id, SUM(CASE WHEN transaction_type = 'Deposit' THEN amount WHEN transaction_type = 'Withdrawal' THEN -amount ELSE 0 END) AS final_balance FROM transactions GROUP BY account_id",
  "explanation": "Calcula o saldo final por conta somando depósitos e subtraindo retiradas.",
  "assumptions": [
    "A tabela transactions contém uma linha por transação financeira.",
    "Transações do tipo Deposit aumentam o saldo.",
    "Transações do tipo Withdrawal reduzem o saldo."
  ]
}
"""


def _build_data_analyst_agent_arguments() -> dict:
    return {
        "objective": "Qual é o saldo final por conta?",
        "language": "pt-BR",
        "max_rows": 100,
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
                        "amount": 10.00,
                        "transaction_type": "Deposit",
                    },
                    {
                        "transaction_id": 124,
                        "account_id": 101,
                        "amount": 20.00,
                        "transaction_type": "Deposit",
                    },
                    {
                        "transaction_id": 125,
                        "account_id": 101,
                        "amount": 5.00,
                        "transaction_type": "Withdrawal",
                    },
                ],
            }
        ],
    }


def _build_agent_service() -> DataAnalystAgentService:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )

    workflow_service = DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )

    return DataAnalystAgentService(
        sql_workflow_service=workflow_service,
    )


def _build_tool_execution_service() -> ToolExecutionService:
    return ToolExecutionService(
        handlers={
            DataAnalystAgentTool.tool_name: DataAnalystAgentTool(
                agent_service=_build_agent_service(),
            )
        }
    )


def _apply_agent_tool_overrides() -> None:
    tool_execution_service = _build_tool_execution_service()

    def get_test_tool_execution_service() -> ToolExecutionService:
        return tool_execution_service

    def get_test_agent_runtime() -> AgentRuntime:
        return AgentRuntime(
            tool_execution_service=tool_execution_service,
        )

    app.dependency_overrides[
        get_tool_execution_service
    ] = get_test_tool_execution_service
    app.dependency_overrides[
        get_agent_runtime
    ] = get_test_agent_runtime


def _clear_agent_tool_overrides() -> None:
    app.dependency_overrides.pop(
        get_tool_execution_service,
        None,
    )
    app.dependency_overrides.pop(
        get_agent_runtime,
        None,
    )


def test_agents_tools_endpoint_should_include_data_analyst_agent_tool() -> None:
    response = client.get("/agents/tools")

    assert response.status_code == 200

    body = response.json()

    tool_names = [
        tool["name"]
        for tool in body["tools"]
    ]

    assert "data_analysis.agent.run" in tool_names


def test_agents_tools_execute_endpoint_should_execute_data_analyst_agent_tool() -> None:
    _apply_agent_tool_overrides()

    try:
        response = client.post(
            "/agents/tools/execute",
            json={
                "tool_name": "data_analysis.agent.run",
                "arguments": _build_data_analyst_agent_arguments(),
                "metadata": {
                    "requested_by": "api-test",
                },
            },
        )
    finally:
        _clear_agent_tool_overrides()

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["tool_name"] == "data_analysis.agent.run"
    assert body["output"]["status"] == "completed"
    assert body["output"]["agent_name"] == "data-analyst-agent-v1"
    assert body["output"]["workflow"]["status"] == "executed"
    assert body["output"]["workflow"]["execution"]["rows"] == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        }
    ]
    assert body["metadata"]["requested_by"] == "api-test"
    assert body["metadata"]["tool_category"] == "data_analysis"


def test_agents_run_endpoint_should_execute_data_analyst_agent_tool_call() -> None:
    _apply_agent_tool_overrides()

    try:
        response = client.post(
            "/agents/run",
            json={
                "objective": (
                    "Calcular saldo final por conta usando o "
                    "Data Analyst Agent."
                ),
                "max_steps": 4,
                "tool_calls": [
                    {
                        "tool_name": "data_analysis.agent.run",
                        "arguments": _build_data_analyst_agent_arguments(),
                    }
                ],
            },
        )
    finally:
        _clear_agent_tool_overrides()

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["run_id"].startswith("agent-run-")

    tool_steps = [
        step
        for step in body["steps"]
        if step["name"] == "tool_call:data_analysis.agent.run"
    ]

    assert len(tool_steps) == 1

    tool_step = tool_steps[0]

    assert tool_step["status"] == "completed"
    assert tool_step["output"]["tool_name"] == "data_analysis.agent.run"
    assert tool_step["output"]["status"] == "completed"
    assert tool_step["output"]["output"]["status"] == "completed"
    assert tool_step["output"]["output"]["workflow"]["status"] == "executed"
    assert tool_step["output"]["output"]["evidence"]["row_count"] == 1
