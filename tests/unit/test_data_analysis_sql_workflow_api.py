from fastapi.testclient import TestClient
from ai_api.data_analysis import (
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    SQLiteReadOnlyQueryExecutor,
    get_data_analyst_sql_workflow_service,
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
        "question": "Qual é o saldo final por conta?",
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


def _override_sql_workflow_service(response_content: str) -> None:
    def get_test_service() -> DataAnalystSQLWorkflowService:
        generation_service = DataAnalystSQLGenerationService(
            llm_provider=FakeLLMProvider(
                response_content=response_content,
            )
        )

        return DataAnalystSQLWorkflowService(
            sql_generation_service=generation_service,
            query_executor=SQLiteReadOnlyQueryExecutor(),
        )

    app.dependency_overrides[
        get_data_analyst_sql_workflow_service
    ] = get_test_service


def test_run_sql_workflow_endpoint_should_generate_and_execute_sql() -> None:
    _override_sql_workflow_service(VALID_SQL_RESPONSE_JSON)

    try:
        response = client.post(
            "/data-analysis/sql/run",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_data_analyst_sql_workflow_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "executed"
    assert body["generation"]["status"] == "approved"
    assert body["generation"]["candidate"]["explanation"].startswith("Calcula")
    assert body["execution"]["status"] == "executed"
    assert body["execution"]["row_count"] == 1
    assert body["execution"]["rows"] == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        }
    ]
    assert body["evidence"]["row_count"] == 1
    assert body["metadata"]["executed"] is True


def test_run_sql_workflow_endpoint_should_not_execute_blocked_generated_sql() -> None:
    _override_sql_workflow_service(UNSAFE_SQL_RESPONSE_JSON)

    try:
        response = client.post(
            "/data-analysis/sql/run",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_data_analyst_sql_workflow_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "blocked"
    assert body["generation"]["status"] == "blocked"
    assert body["execution"] is None
    assert body["evidence"] is None
    assert body["metadata"]["executed"] is False
    assert any(
        violation["rule"] == "blocked_token"
        and violation["token"] == "delete"
        for violation in body["generation"]["validation"]["violations"]
    )
