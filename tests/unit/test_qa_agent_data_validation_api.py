from fastapi.testclient import TestClient
from ai_api.agents import (
    DataAnalystAgentTool,
    QAAgentService,
    ToolExecutionService,
    get_qa_agent_service,
)
from ai_api.agents.runtime import AgentRuntime
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


def _build_request_body() -> dict:
    return {
        "requirement_text": (
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        "language": "pt-BR",
        "max_steps": 6,
        "data_validation": {
            "objective": "Validar o saldo final por conta.",
            "mode": "auto",
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
        },
    }


def _build_qa_agent_service() -> QAAgentService:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )

    workflow_service = DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )

    data_analyst_service = DataAnalystAgentService(
        sql_workflow_service=workflow_service,
    )

    tool_execution_service = ToolExecutionService(
        handlers={
            DataAnalystAgentTool.tool_name: DataAnalystAgentTool(
                agent_service=data_analyst_service,
            )
        }
    )

    return QAAgentService(
        agent_runtime=AgentRuntime(
            tool_execution_service=tool_execution_service,
        )
    )


def test_qa_agent_endpoint_should_run_data_validation_capability() -> None:
    def get_test_service() -> QAAgentService:
        return _build_qa_agent_service()

    app.dependency_overrides[
        get_qa_agent_service
    ] = get_test_service

    try:
        response = client.post(
            "/agents/qa/run",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_qa_agent_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["data_validation_selection"] is not None
    assert body["data_validation_selection"]["decision"] == "selected"
    assert body["metadata"]["data_validation_available"] is True
    assert body["metadata"]["data_validation_selected"] is True
    assert body["metadata"]["data_validation_mode"] == "auto"
    assert body["requirement_analysis"]["summary"]
    assert body["data_validation"] is not None
    assert body["data_validation"]["status"] == "completed"
    assert body["data_validation"]["workflow"]["status"] == "executed"
    assert body["data_validation"]["workflow"]["execution"]["rows"] == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        }
    ]

    step_names = [
        step["name"]
        for step in body["steps"]
    ]

    assert "tool_call:requirements.analyze" in step_names
    assert "tool_call:data_analysis.agent.run" in step_names
    assert body["data_validation_selection"] is not None
    assert body["data_validation_selection"]["decision"] == "selected"
    assert body["metadata"]["data_validation_available"] is True
    assert body["metadata"]["data_validation_selected"] is True
    assert body["metadata"]["data_validation_mode"] == "auto"
