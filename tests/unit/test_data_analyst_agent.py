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


def _build_agent_request() -> DataAnalystAgentRequest:
    return DataAnalystAgentRequest(
        objective="Qual é o saldo final por conta?",
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
        language="pt-BR",
    )


def _build_agent_service(
    response_content: str,
) -> DataAnalystAgentService:
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


def test_data_analyst_agent_should_complete_sql_analysis() -> None:
    service = _build_agent_service(VALID_SQL_RESPONSE_JSON)

    response = service.run(_build_agent_request())

    assert response.status == "completed"
    assert response.agent_name == "data-analyst-agent-v1"
    assert response.objective == "Qual é o saldo final por conta?"
    assert response.answer.startswith("A análise foi concluída com sucesso")
    assert response.workflow.status == "executed"
    assert response.workflow.execution is not None
    assert response.workflow.execution.rows == [
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
    assert response.trace[0].step == "request_received"
    assert response.trace[-1].step == "sql_workflow_completed"
    assert response.metadata["executed"] is True


def test_data_analyst_agent_should_return_blocked_when_generated_sql_is_unsafe() -> None:
    service = _build_agent_service(UNSAFE_SQL_RESPONSE_JSON)

    response = service.run(_build_agent_request())

    assert response.status == "blocked"
    assert response.answer == (
        "A consulta gerada foi bloqueada pela validação de "
        "segurança e não foi executada."
    )
    assert response.workflow.status == "blocked"
    assert response.workflow.execution is None
    assert response.evidence is None
    assert response.trace[-1].step == "sql_workflow_blocked"
    assert response.trace[-1].status == "blocked"
    assert response.metadata["executed"] is False
