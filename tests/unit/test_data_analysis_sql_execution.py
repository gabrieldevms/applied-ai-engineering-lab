import pytest
from ai_api.data_analysis import (
    DatabaseColumn,
    DatabaseSchema,
    DatabaseTable,
    DatabaseTableData,
    SQLExecutionError,
    SQLExecutionRequest,
    SQLiteReadOnlyQueryExecutor,
)


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


def test_sql_query_executor_should_execute_safe_select_query() -> None:
    executor = SQLiteReadOnlyQueryExecutor()

    request = SQLExecutionRequest(
        sql="""
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
        ORDER BY account_id
        """,
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
    )

    response = executor.execute(request)

    assert response.status == "executed"
    assert response.validation.status == "approved"
    assert response.row_count == 2
    assert response.truncated is False
    assert response.columns[0].name == "account_id"
    assert response.columns[1].name == "final_balance"
    assert response.rows == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        },
        {
            "account_id": 201,
            "final_balance": 10.0,
        },
    ]
    assert response.evidence.row_count == 2
    assert response.evidence.column_count == 2
    assert response.metadata["executed"] is True


def test_sql_query_executor_should_block_unsafe_query_before_execution() -> None:
    executor = SQLiteReadOnlyQueryExecutor()

    request = SQLExecutionRequest(
        sql="DROP TABLE transactions",
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
    )

    response = executor.execute(request)

    assert response.status == "blocked"
    assert response.validation.status == "blocked"
    assert response.rows == []
    assert response.row_count == 0
    assert response.metadata["executed"] is False
    assert any(
        violation.rule == "blocked_token"
        and violation.token == "drop"
        for violation in response.validation.violations
    )


def test_sql_query_executor_should_truncate_rows_when_max_rows_is_reached() -> None:
    executor = SQLiteReadOnlyQueryExecutor()

    request = SQLExecutionRequest(
        sql="""
        SELECT transaction_id, account_id
        FROM transactions
        ORDER BY transaction_id
        """,
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
        max_rows=2,
    )

    response = executor.execute(request)

    assert response.status == "executed"
    assert response.row_count == 2
    assert response.truncated is True
    assert response.evidence.truncated is True


def test_sql_query_executor_should_reject_table_data_for_unknown_table() -> None:
    executor = SQLiteReadOnlyQueryExecutor()

    request = SQLExecutionRequest(
        sql="SELECT * FROM transactions",
        database_schema=_build_database_schema(),
        table_data=[
            DatabaseTableData(
                table_name="unknown_table",
                rows=[],
            )
        ],
    )

    with pytest.raises(
        SQLExecutionError,
        match="Table data references unknown table: unknown_table",
    ):
        executor.execute(request)


def test_sql_query_executor_should_reject_unknown_columns_in_table_data() -> None:
    executor = SQLiteReadOnlyQueryExecutor()

    request = SQLExecutionRequest(
        sql="SELECT * FROM transactions",
        database_schema=_build_database_schema(),
        table_data=[
            DatabaseTableData(
                table_name="transactions",
                rows=[
                    {
                        "transaction_id": 1,
                        "account_id": 101,
                        "amount": 10.0,
                        "transaction_type": "Deposit",
                        "unexpected_column": "invalid",
                    }
                ],
            )
        ],
    )

    with pytest.raises(
        SQLExecutionError,
        match="contains unknown columns: unexpected_column",
    ):
        executor.execute(request)


def test_sql_query_executor_should_raise_error_for_invalid_select_query() -> None:
    executor = SQLiteReadOnlyQueryExecutor()

    request = SQLExecutionRequest(
        sql="SELECT missing_column FROM transactions",
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
    )

    with pytest.raises(
        SQLExecutionError,
        match="SQL query could not be executed.",
    ):
        executor.execute(request)
