from fastapi.testclient import TestClient
from ai_api.data_analysis import (
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    SQLWorkflowRegressionService,
    SQLiteReadOnlyQueryExecutor,
    get_sql_workflow_regression_service,
)
from ai_api.llm import FakeLLMProvider
from ai_api.main import app


client = TestClient(app)


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


def _build_request_body(
    expected_row_count: int = 1,
) -> dict:
    return {
        "suite_name": "data-analysis-regression",
        "metadata": {
            "environment": "api-test",
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
                "expected_result": {
                    "expected_status": "executed",
                    "expected_row_count": expected_row_count,
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


def _build_regression_service() -> SQLWorkflowRegressionService:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )

    workflow_service = DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )

    return SQLWorkflowRegressionService(
        workflow_service=workflow_service,
    )


def test_sql_workflow_regression_endpoint_should_pass_expected_suite() -> None:
    def get_test_service() -> SQLWorkflowRegressionService:
        return _build_regression_service()

    app.dependency_overrides[
        get_sql_workflow_regression_service
    ] = get_test_service

    try:
        response = client.post(
            "/data-analysis/sql/regression/run",
            json=_build_request_body(),
        )
    finally:
        app.dependency_overrides.pop(
            get_sql_workflow_regression_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    result = body["results"][0]

    assert body["status"] == "passed"
    assert body["total_scenarios"] == 1
    assert body["passed_scenarios"] == 1
    assert body["failed_scenarios"] == 0
    assert body["metadata"]["environment"] == "api-test"

    assert result["status"] == "passed"
    assert result["workflow_response"]["status"] == "executed"


def test_sql_workflow_regression_endpoint_should_fail_wrong_expected_shape() -> None:
    def get_test_service() -> SQLWorkflowRegressionService:
        return _build_regression_service()

    app.dependency_overrides[
        get_sql_workflow_regression_service
    ] = get_test_service

    try:
        response = client.post(
            "/data-analysis/sql/regression/run",
            json=_build_request_body(expected_row_count=99),
        )
    finally:
        app.dependency_overrides.pop(
            get_sql_workflow_regression_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    result = body["results"][0]

    row_count_check = next(
        check
        for check in result["checks"]
        if check["name"] == "row_count"
    )

    assert body["status"] == "failed"
    assert body["failed_scenarios"] == 1
    assert result["status"] == "failed"
    assert row_count_check["status"] == "failed"
    assert row_count_check["metadata"]["expected_row_count"] == 99
    assert row_count_check["metadata"]["actual_row_count"] == 1
