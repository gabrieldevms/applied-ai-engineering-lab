from ai_api.data_analysis import (
    DatabaseColumn,
    DatabaseSchema,
    DatabaseTable,
    NaturalLanguageSQLRequest,
    ReadOnlySQLValidator,
    SQLGenerationCandidate,
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


def test_natural_language_sql_request_should_represent_schema_context() -> None:
    payload = NaturalLanguageSQLRequest(
        question="Qual é o saldo final por conta?",
        database_schema=_build_database_schema(),
        language="pt-BR",
        metadata={
            "domain": "qa",
        },
    )

    assert payload.question == "Qual é o saldo final por conta?"
    assert payload.database_schema.name == "qa_database"
    assert payload.database_schema.tables[0].name == "transactions"
    assert payload.database_schema.tables[0].columns[0].name == "transaction_id"
    assert payload.metadata["domain"] == "qa"


def test_sql_generation_candidate_should_store_sql_and_explanation() -> None:
    candidate = SQLGenerationCandidate(
        sql="""
        SELECT account_id, SUM(amount) AS final_balance
        FROM transactions
        GROUP BY account_id
        """,
        explanation="Calcula o saldo final agrupando transações por conta.",
        assumptions=[
            "amount already represents the signed transaction value",
        ],
    )

    assert "SELECT account_id" in candidate.sql
    assert candidate.explanation.startswith("Calcula")
    assert candidate.assumptions == [
        "amount already represents the signed transaction value"
    ]


def test_read_only_sql_validator_should_approve_select_statement() -> None:
    validator = ReadOnlySQLValidator()

    response = validator.validate(
        """
        SELECT account_id, SUM(amount) AS final_balance
        FROM transactions
        GROUP BY account_id;
        """
    )

    assert response.status == "approved"
    assert response.violations == []
    assert response.normalized_sql.startswith("select account_id")
    assert response.metadata["validator"] == "read-only-sql-validator-v1"


def test_read_only_sql_validator_should_approve_with_statement() -> None:
    validator = ReadOnlySQLValidator()

    response = validator.validate(
        """
        WITH account_totals AS (
            SELECT account_id, SUM(amount) AS final_balance
            FROM transactions
            GROUP BY account_id
        )
        SELECT *
        FROM account_totals
        """
    )

    assert response.status == "approved"
    assert response.violations == []


def test_read_only_sql_validator_should_block_update_statement() -> None:
    validator = ReadOnlySQLValidator()

    response = validator.validate(
        """
        UPDATE transactions
        SET amount = 0
        WHERE account_id = 101
        """
    )

    assert response.status == "blocked"
    assert any(
        violation.rule == "non_read_only_statement"
        for violation in response.violations
    )
    assert any(
        violation.rule == "blocked_token" and violation.token == "update"
        for violation in response.violations
    )


def test_read_only_sql_validator_should_block_delete_inside_statement() -> None:
    validator = ReadOnlySQLValidator()

    response = validator.validate(
        """
        SELECT *
        FROM transactions
        WHERE transaction_id IN (
            DELETE FROM audit_log
        )
        """
    )

    assert response.status == "blocked"
    assert any(
        violation.rule == "blocked_token" and violation.token == "delete"
        for violation in response.violations
    )


def test_read_only_sql_validator_should_block_multiple_statements() -> None:
    validator = ReadOnlySQLValidator()

    response = validator.validate(
        """
        SELECT * FROM transactions;
        DROP TABLE transactions;
        """
    )

    assert response.status == "blocked"
    assert any(
        violation.rule == "multiple_statements"
        for violation in response.violations
    )
    assert any(
        violation.rule == "blocked_token" and violation.token == "drop"
        for violation in response.violations
    )


def test_read_only_sql_validator_should_block_blank_sql() -> None:
    validator = ReadOnlySQLValidator()

    response = validator.validate("   ")

    assert response.status == "blocked"
    assert response.violations[0].rule == "blank_sql"
