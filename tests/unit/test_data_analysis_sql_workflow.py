from ai_api.data_analysis import (
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    DatabaseColumn,
    DatabaseSchema,
    DatabaseTable,
    DatabaseTableData,
    SQLWorkflowRequest,
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


UNSAFE_SQL_RESPONSE_JSON = """
{
  "sql": "DROP TABLE transactions",
  "explanation": "Remove a tabela de transações.",
  "assumptions": []
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
        )
    ]


def _build_workflow_request() -> SQLWorkflowRequest:
    return SQLWorkflowRequest(
        question="Qual é o saldo final por conta?",
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
        language="pt-BR",
        max_rows=100,
    )


def test_sql_workflow_should_generate_validate_execute_and_return_evidence() -> None:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )
    workflow_service = DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )

    response = workflow_service.run(_build_workflow_request())

    assert response.status == "executed"
    assert response.generation.status == "approved"
    assert response.generation.candidate.explanation.startswith("Calcula")
    assert response.execution is not None
    assert response.execution.status == "executed"
    assert response.execution.row_count == 2
    assert response.execution.rows == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        },
        {
            "account_id": 201,
            "final_balance": 10.0,
        },
    ]
    assert response.evidence is not None
    assert response.evidence.row_count == 2
    assert response.evidence.column_count == 2
    assert response.metadata["executed"] is True


def test_sql_workflow_should_not_execute_when_generated_sql_is_blocked() -> None:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=UNSAFE_SQL_RESPONSE_JSON,
        )
    )
    workflow_service = DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )

    response = workflow_service.run(_build_workflow_request())

    assert response.status == "blocked"
    assert response.generation.status == "blocked"
    assert response.execution is None
    assert response.evidence is None
    assert response.metadata["executed"] is False
    assert (
        response.metadata["blocked_reason"]
        == "generated_sql_failed_safety_validation"
    )
    assert any(
        violation.rule == "blocked_token"
        and violation.token == "drop"
        for violation in response.generation.validation.violations
    )
