from fastapi.testclient import TestClient
from ai_api.data_analysis import (
    DataAnalystAgentService,
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    SQLiteReadOnlyQueryExecutor,
    get_data_analyst_agent_service,
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


UNSAFE_SQL_RESPONSE_JSON = """
{
  "sql": "DELETE FROM transactions",
  "explanation": "Remove transações.",
  "assumptions": []
}
"""


def _build_request_body() -> dict:
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


def _override_agent_service(response_content: str) -> None:
    def get_test_service() -> DataAnalystAgentService:
        generation_service = DataAnalystSQLGenerationService(
            llm_provider=FakeLLMProvider(
                response_content=response_content,
            )
        )

        workflow_service = DataAnalystSQLWorkflowService(
            sql_generation_service=generation_service,
            query_executor=SQLiteReadOnlyQueryExecutor(),
        )

        return DataAnalystAgentService(
            sql_workflow_service=workflow_service,
        )

    app.dependency_overrides[
        get_data_analyst_agent_service
    ] = get_test_service


def test_data_analyst_agent_endpoint_should_complete_analysis() -> None:
    _override_agent_service(VALID_SQL_RESPONSE_JSON)

    try:
        response = client.post(
            "/data-analysis/agent/run",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_data_analyst_agent_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["agent_name"] == "data-analyst-agent-v1"
    assert body["answer"].startswith("A análise foi concluída com sucesso")
    assert body["workflow"]["status"] == "executed"
    assert body["workflow"]["execution"]["rows"] == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        }
    ]
    assert body["evidence"]["row_count"] == 1
    assert body["trace"][0]["step"] == "request_received"
    assert body["trace"][-1]["step"] == "sql_workflow_completed"
    assert body["metadata"]["executed"] is True


def test_data_analyst_agent_endpoint_should_return_blocked_analysis() -> None:
    _override_agent_service(UNSAFE_SQL_RESPONSE_JSON)

    try:
        response = client.post(
            "/data-analysis/agent/run",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_data_analyst_agent_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "blocked"
    assert body["workflow"]["status"] == "blocked"
    assert body["workflow"]["execution"] is None
    assert body["evidence"] is None
    assert body["trace"][-1]["step"] == "sql_workflow_blocked"
    assert body["metadata"]["executed"] is False
