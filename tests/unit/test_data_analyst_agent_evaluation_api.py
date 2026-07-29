from fastapi.testclient import TestClient
from ai_api.data_analysis import (
    DataAnalystAgentRequest,
    DataAnalystAgentService,
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    DatabaseColumn,
    DatabaseSchema,
    DatabaseTable,
    DatabaseTableData,
    SQLiteReadOnlyQueryExecutor,
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


def _build_database_schema() -> DatabaseSchema:
    return DatabaseSchema(
        name="qa_database",
        description="Database used for QA validation.",
        tables=[
            DatabaseTable(
                name="transactions",
                description="Financial transactions.",
                columns=[
                    DatabaseColumn(
                        name="transaction_id",
                        data_type="integer",
                        primary_key=True,
                        nullable=False,
                    ),
                    DatabaseColumn(
                        name="account_id",
                        data_type="integer",
                        nullable=False,
                    ),
                    DatabaseColumn(
                        name="amount",
                        data_type="decimal",
                        nullable=False,
                    ),
                    DatabaseColumn(
                        name="transaction_type",
                        data_type="varchar",
                        nullable=False,
                    ),
                ],
            )
        ],
    )


def _build_table_data() -> list[DatabaseTableData]:
    return [
        DatabaseTableData(
            table_name="transactions",
            rows=[
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
        )
    ]


def _build_agent_response_body() -> dict:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )

    workflow_service = DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )

    agent_service = DataAnalystAgentService(
        sql_workflow_service=workflow_service,
    )

    agent_response = agent_service.run(
        DataAnalystAgentRequest(
            objective="Qual é o saldo final por conta?",
            database_schema=_build_database_schema(),
            table_data=_build_table_data(),
            language="pt-BR",
        )
    )

    return agent_response.model_dump(mode="json")


def test_data_analyst_agent_evaluation_endpoint_should_pass_valid_response() -> None:
    response = client.post(
        "/data-analysis/agent/evaluate",
        json={
            "agent_response": _build_agent_response_body(),
            "expected_status": "completed",
            "expected_row_count": 1,
            "expected_columns": [
                "account_id",
                "final_balance",
            ],
            "expected_language": "pt-BR",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "passed"
    assert body["score"] == 1.0
    assert all(
        metric["status"] == "passed"
        for metric in body["metrics"]
    )


def test_data_analyst_agent_evaluation_endpoint_should_fail_invalid_expectation() -> None:
    response = client.post(
        "/data-analysis/agent/evaluate",
        json={
            "agent_response": _build_agent_response_body(),
            "expected_status": "completed",
            "expected_row_count": 999,
            "expected_columns": [
                "account_id",
                "final_balance",
            ],
            "expected_language": "pt-BR",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "failed"
    assert any(
        metric["name"] == "result_shape"
        and metric["status"] == "failed"
        for metric in body["metrics"]
    )
