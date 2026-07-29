from fastapi.testclient import TestClient
from ai_api.main import app


client = TestClient(app)


def _build_request_body(sql: str) -> dict:
    return {
        "sql": sql,
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


def test_execute_sql_endpoint_should_execute_safe_query() -> None:
    response = client.post(
        "/data-analysis/sql/execute",
        json=_build_request_body(
            """
            SELECT
                account_id,
                SUM(
                    CASE
                        WHEN transaction_type = 'Deposit' THEN amount
                        WHEN transaction_type = 'Withdrawal' THEN -amount
                        ELSE 0
                    END
                ) AS final_balance
            FROM transactions
            GROUP BY account_id
            """
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "executed"
    assert body["validation"]["status"] == "approved"
    assert body["row_count"] == 1
    assert body["rows"] == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        }
    ]
    assert body["evidence"]["row_count"] == 1
    assert body["metadata"]["executed"] is True


def test_execute_sql_endpoint_should_block_unsafe_query() -> None:
    response = client.post(
        "/data-analysis/sql/execute",
        json=_build_request_body("DELETE FROM transactions"),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "blocked"
    assert body["validation"]["status"] == "blocked"
    assert body["rows"] == []
    assert any(
        violation["rule"] == "blocked_token"
        and violation["token"] == "delete"
        for violation in body["validation"]["violations"]
    )


def test_execute_sql_endpoint_should_return_error_for_invalid_query() -> None:
    response = client.post(
        "/data-analysis/sql/execute",
        json=_build_request_body("SELECT missing_column FROM transactions"),
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "sql_execution_error"
    assert body["error"]["message"] == "SQL query could not be executed."
