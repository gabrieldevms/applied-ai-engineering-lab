from ai_api.agents import (
    AgentRuntime,
    AgentToolCall,
    DataAnalystAgentTool,
    ToolExecutionService,
    ToolRegistry,
)
from ai_api.data_analysis import (
    DataAnalystAgentService,
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    SQLiteReadOnlyQueryExecutor,
)
from ai_api.llm import FakeLLMProvider


VALID_SQL_RESPONSE_JSON = """
{
  "sql": "SELECT account_id, SUM(CASE WHEN transaction_type = 'Deposit' THEN amount WHEN transaction_type = 'Withdrawal' THEN -amount ELSE 0 END) AS final_balance FROM transactions GROUP BY account_id ORDER BY account_id",
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
                    {
                        "transaction_id": 126,
                        "account_id": 201,
                        "amount": 20.00,
                        "transaction_type": "Deposit",
                    },
                    {
                        "transaction_id": 128,
                        "account_id": 201,
                        "amount": 10.00,
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


def test_tool_registry_should_include_data_analyst_agent_tool() -> None:
    registry = ToolRegistry()

    tool = registry.get("data_analysis.agent.run")

    assert tool is not None
    assert tool.name == "data_analysis.agent.run"
    assert tool.metadata["category"] == "data_analysis"
    assert tool.metadata["safe_by_default"] is True
    assert tool.metadata["requires_llm"] is True
    assert tool.metadata["specialized_agent"] == "data-analyst-agent-v1"


def test_tool_execution_service_should_execute_data_analyst_agent_tool() -> None:
    service = _build_tool_execution_service()

    response = service.execute(
        tool_name="data_analysis.agent.run",
        arguments=_build_data_analyst_agent_arguments(),
        metadata={
            "requested_by": "unit-test",
        },
    )

    assert response.status == "completed"
    assert response.tool_name == "data_analysis.agent.run"
    assert response.execution_id.startswith(
        "tool-execution-data-analysis-agent-run-"
    )
    assert response.output["status"] == "completed"
    assert response.output["agent_name"] == "data-analyst-agent-v1"
    assert response.output["workflow"]["status"] == "executed"
    assert response.output["workflow"]["execution"]["rows"] == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        },
        {
            "account_id": 201,
            "final_balance": 10.0,
        },
    ]
    assert response.metadata["requested_by"] == "unit-test"
    assert response.metadata["tool_category"] == "data_analysis"
    assert response.metadata["specialized_agent"] == "data-analyst-agent-v1"


def test_generic_agent_runtime_should_call_data_analyst_agent_tool() -> None:
    runtime = AgentRuntime(
        tool_execution_service=_build_tool_execution_service(),
    )

    response = runtime.run(
        objective="Calcular saldo final por conta usando o Data Analyst Agent.",
        max_steps=4,
        tool_calls=[
            AgentToolCall(
                tool_name="data_analysis.agent.run",
                arguments=_build_data_analyst_agent_arguments(),
            )
        ],
    )

    assert response.status == "completed"
    assert response.run_id.startswith("agent-run-")

    tool_step = next(
        step
        for step in response.steps
        if step.name == "tool_call:data_analysis.agent.run"
    )

    assert tool_step.status == "completed"
    assert tool_step.output["tool_name"] == "data_analysis.agent.run"
    assert tool_step.output["status"] == "completed"
    assert tool_step.output["output"]["status"] == "completed"
    assert tool_step.output["output"]["workflow"]["status"] == "executed"
    assert tool_step.output["output"]["evidence"]["row_count"] == 2
