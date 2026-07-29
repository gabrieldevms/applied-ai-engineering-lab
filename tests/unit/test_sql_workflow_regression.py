from ai_api.data_analysis import (
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    DatabaseColumn,
    DatabaseSchema,
    DatabaseTable,
    DatabaseTableData,
    SQLRegressionExpectedResult,
    SQLRegressionScenario,
    SQLRegressionSuiteRequest,
    SQLWorkflowRegressionService,
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


def _build_workflow_service() -> DataAnalystSQLWorkflowService:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )

    return DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )


def _build_scenario(
    expected_row_count: int = 2,
) -> SQLRegressionScenario:
    return SQLRegressionScenario(
        scenario_id="final-account-balance",
        name="Final account balance",
        description=(
            "Validate final account balance by account using deposits "
            "and withdrawals."
        ),
        request=SQLWorkflowRequest(
            question="Qual é o saldo final por conta?",
            database_schema=_build_database_schema(),
            table_data=_build_table_data(),
            language="pt-BR",
            max_rows=100,
        ),
        expected_result=SQLRegressionExpectedResult(
            expected_status="executed",
            expected_row_count=expected_row_count,
            expected_columns=[
                "account_id",
                "final_balance",
            ],
            expected_rows=[
                {
                    "account_id": 101,
                    "final_balance": 25.0,
                },
                {
                    "account_id": 201,
                    "final_balance": 10.0,
                },
            ],
        ),
        metadata={
            "source": "unit-test",
        },
    )


def test_sql_workflow_regression_should_pass_expected_scenario() -> None:
    service = SQLWorkflowRegressionService(
        workflow_service=_build_workflow_service(),
    )

    response = service.run_suite(
        SQLRegressionSuiteRequest(
            suite_name="data-analysis-regression",
            scenarios=[
                _build_scenario(),
            ],
            metadata={
                "environment": "test",
            },
        )
    )

    result = response.results[0]

    assert response.status == "passed"
    assert response.total_scenarios == 1
    assert response.passed_scenarios == 1
    assert response.failed_scenarios == 0
    assert response.metadata["environment"] == "test"

    assert result.status == "passed"
    assert result.scenario_id == "final-account-balance"
    assert result.workflow_response.status == "executed"

    check_statuses = {
        check.name: check.status
        for check in result.checks
    }

    assert check_statuses == {
        "status": "passed",
        "row_count": "passed",
        "columns": "passed",
        "rows": "passed",
    }


def test_sql_workflow_regression_should_fail_when_row_count_does_not_match() -> None:
    service = SQLWorkflowRegressionService(
        workflow_service=_build_workflow_service(),
    )

    response = service.run_suite(
        SQLRegressionSuiteRequest(
            suite_name="data-analysis-regression",
            scenarios=[
                _build_scenario(expected_row_count=99),
            ],
        )
    )

    result = response.results[0]

    row_count_check = next(
        check
        for check in result.checks
        if check.name == "row_count"
    )

    assert response.status == "failed"
    assert response.failed_scenarios == 1
    assert result.status == "failed"
    assert row_count_check.status == "failed"
    assert row_count_check.metadata["expected_row_count"] == 99
    assert row_count_check.metadata["actual_row_count"] == 2
