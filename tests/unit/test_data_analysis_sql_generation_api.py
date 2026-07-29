from fastapi.testclient import TestClient
from ai_api.data_analysis import (
    DataAnalystSQLGenerationService,
    get_data_analyst_sql_generation_service,
)
from ai_api.llm import FakeLLMProvider
from ai_api.main import app


client = TestClient(app)


VALID_SQL_RESPONSE_JSON = """
{
  "sql": "SELECT account_id, SUM(amount) AS final_balance FROM transactions GROUP BY account_id",
  "explanation": "Calcula o saldo final por conta.",
  "assumptions": [
    "The amount column already represents signed values."
  ]
}
"""


UNSAFE_SQL_RESPONSE_JSON = """
{
  "sql": "DROP TABLE transactions",
  "explanation": "Remove a tabela de transações.",
  "assumptions": []
}
"""


def _build_request_body() -> dict:
    return {
        "question": "Qual é o saldo final por conta?",
        "language": "pt-BR",
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
                    ],
                }
            ],
        },
    }


def _override_sql_generation_service(response_content: str) -> None:
    def get_test_service() -> DataAnalystSQLGenerationService:
        return DataAnalystSQLGenerationService(
            llm_provider=FakeLLMProvider(
                response_content=response_content,
            )
        )

    app.dependency_overrides[
        get_data_analyst_sql_generation_service
    ] = get_test_service


def test_generate_sql_endpoint_should_return_approved_sql() -> None:
    _override_sql_generation_service(VALID_SQL_RESPONSE_JSON)

    try:
        response = client.post(
            "/data-analysis/sql/generate",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_data_analyst_sql_generation_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "approved"
    assert body["candidate"]["sql"].startswith("SELECT account_id")
    assert body["validation"]["status"] == "approved"
    assert body["validation"]["violations"] == []


def test_generate_sql_endpoint_should_return_blocked_sql_when_llm_generates_unsafe_query() -> None:
    _override_sql_generation_service(UNSAFE_SQL_RESPONSE_JSON)

    try:
        response = client.post(
            "/data-analysis/sql/generate",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_data_analyst_sql_generation_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "blocked"
    assert body["validation"]["status"] == "blocked"
    assert any(
        violation["rule"] == "blocked_token"
        and violation["token"] == "drop"
        for violation in body["validation"]["violations"]
    )
