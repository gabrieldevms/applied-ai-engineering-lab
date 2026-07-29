from ai_api.data_analysis import (
    DataAnalystAgentEvaluationRequest,
    DataAnalystAgentEvaluationService,
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


def test_data_analyst_agent_evaluation_should_pass_completed_response() -> None:
    agent_service = _build_agent_service(VALID_SQL_RESPONSE_JSON)
    agent_response = agent_service.run(_build_agent_request())

    evaluation_service = DataAnalystAgentEvaluationService()

    evaluation = evaluation_service.evaluate(
        DataAnalystAgentEvaluationRequest(
            agent_response=agent_response,
            expected_status="completed",
            expected_row_count=2,
            expected_columns=[
                "account_id",
                "final_balance",
            ],
            expected_language="pt-BR",
        )
    )

    assert evaluation.status == "passed"
    assert evaluation.score == 1.0
    assert all(
        metric.status == "passed"
        for metric in evaluation.metrics
    )
    assert evaluation.metadata["evaluator"] == "data-analyst-agent-evaluator-v1"


def test_data_analyst_agent_evaluation_should_pass_blocked_response() -> None:
    agent_service = _build_agent_service(UNSAFE_SQL_RESPONSE_JSON)
    agent_response = agent_service.run(_build_agent_request())

    evaluation_service = DataAnalystAgentEvaluationService()

    evaluation = evaluation_service.evaluate(
        DataAnalystAgentEvaluationRequest(
            agent_response=agent_response,
            expected_status="blocked",
            expected_language="pt-BR",
        )
    )

    assert evaluation.status == "passed"
    assert evaluation.score == 1.0
    assert all(
        metric.status == "passed"
        for metric in evaluation.metrics
    )


def test_data_analyst_agent_evaluation_should_fail_when_row_count_does_not_match() -> None:
    agent_service = _build_agent_service(VALID_SQL_RESPONSE_JSON)
    agent_response = agent_service.run(_build_agent_request())

    evaluation_service = DataAnalystAgentEvaluationService()

    evaluation = evaluation_service.evaluate(
        DataAnalystAgentEvaluationRequest(
            agent_response=agent_response,
            expected_status="completed",
            expected_row_count=999,
            expected_columns=[
                "account_id",
                "final_balance",
            ],
            expected_language="pt-BR",
        )
    )

    assert evaluation.status == "failed"
    assert any(
        metric.name == "result_shape"
        and metric.status == "failed"
        for metric in evaluation.metrics
    )


def test_data_analyst_agent_evaluation_should_fail_when_expected_column_is_missing() -> None:
    agent_service = _build_agent_service(VALID_SQL_RESPONSE_JSON)
    agent_response = agent_service.run(_build_agent_request())

    evaluation_service = DataAnalystAgentEvaluationService()

    evaluation = evaluation_service.evaluate(
        DataAnalystAgentEvaluationRequest(
            agent_response=agent_response,
            expected_status="completed",
            expected_row_count=2,
            expected_columns=[
                "missing_column",
            ],
            expected_language="pt-BR",
        )
    )

    assert evaluation.status == "failed"
    assert any(
        metric.name == "result_shape"
        and metric.status == "failed"
        for metric in evaluation.metrics
    )
