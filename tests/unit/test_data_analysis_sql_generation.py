import pytest
from ai_api.data_analysis import (
    DataAnalystSQLGenerationService,
    DatabaseColumn,
    DatabaseSchema,
    DatabaseTable,
    NaturalLanguageSQLRequest,
    SQLGenerationError,
)
from ai_api.data_analysis.parsers import parse_sql_generation_response
from ai_api.data_analysis.prompts import build_sql_generation_messages
from ai_api.llm import FakeLLMProvider


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
  "sql": "DELETE FROM transactions WHERE account_id = 101",
  "explanation": "Remove transações da conta.",
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


def _build_request() -> NaturalLanguageSQLRequest:
    return NaturalLanguageSQLRequest(
        question="Qual é o saldo final por conta?",
        database_schema=_build_database_schema(),
        language="pt-BR",
    )


def test_build_sql_generation_messages_should_include_question_and_schema() -> None:
    messages = build_sql_generation_messages(_build_request())

    assert messages[0].role == "system"
    assert "Only SELECT or WITH statements are allowed" in messages[0].content
    assert messages[1].role == "user"
    assert "Qual é o saldo final por conta?" in messages[1].content
    assert "transactions" in messages[1].content
    assert "account_id" in messages[1].content
    assert "Requested language: pt-BR" in messages[1].content
    assert "Do not translate table names or column names" in messages[0].content
    assert "Write explanation and assumptions in the requested language" in messages[0].content


def test_parse_sql_generation_response_should_parse_valid_json() -> None:
    candidate = parse_sql_generation_response(VALID_SQL_RESPONSE_JSON)

    assert candidate.sql.startswith("SELECT account_id")
    assert candidate.explanation == "Calcula o saldo final por conta."
    assert candidate.assumptions == [
        "The amount column already represents signed values."
    ]


def test_parse_sql_generation_response_should_extract_json_from_surrounding_text() -> None:
    candidate = parse_sql_generation_response(
        f"Here is the SQL JSON:\n{VALID_SQL_RESPONSE_JSON}\nDone."
    )

    assert candidate.sql.startswith("SELECT account_id")


def test_parse_sql_generation_response_should_reject_invalid_schema() -> None:
    with pytest.raises(
        SQLGenerationError,
        match="LLM response does not match the SQL generation schema.",
    ):
        parse_sql_generation_response(
            """
            {
              "sql": "SELECT * FROM transactions"
            }
            """
        )


def test_sql_generation_service_should_generate_and_approve_safe_sql() -> None:
    service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )

    response = service.generate(_build_request())

    assert response.status == "approved"
    assert response.candidate.sql.startswith("SELECT account_id")
    assert response.validation.status == "approved"
    assert response.validation.violations == []
    assert response.metadata["llm_provider"] == "fake"
    assert response.metadata["llm_model"] == "fake-llm-v1"


def test_sql_generation_service_should_return_blocked_status_for_unsafe_sql() -> None:
    service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=UNSAFE_SQL_RESPONSE_JSON,
        )
    )

    response = service.generate(_build_request())

    assert response.status == "blocked"
    assert response.validation.status == "blocked"
    assert any(
        violation.rule == "non_read_only_statement"
        for violation in response.validation.violations
    )
    assert any(
        violation.rule == "blocked_token" and violation.token == "delete"
        for violation in response.validation.violations
    )
