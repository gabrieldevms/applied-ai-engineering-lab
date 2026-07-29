import re
from ai_api.data_analysis.schemas import (
    SQLSafetyViolation,
    SQLValidationResponse,
)


class ReadOnlySQLValidator:
    blocked_tokens = frozenset(
        {
            "alter",
            "attach",
            "call",
            "create",
            "delete",
            "detach",
            "drop",
            "exec",
            "execute",
            "grant",
            "insert",
            "merge",
            "pragma",
            "replace",
            "revoke",
            "truncate",
            "update",
            "vacuum",
        }
    )

    allowed_start_tokens = frozenset(
        {
            "select",
            "with",
        }
    )

    def validate(
        self,
        sql: str,
    ) -> SQLValidationResponse:
        cleaned_sql = sql.strip()

        violations: list[SQLSafetyViolation] = []

        if not cleaned_sql:
            return SQLValidationResponse(
                status="blocked",
                sql=sql,
                normalized_sql="",
                violations=[
                    SQLSafetyViolation(
                        rule="blank_sql",
                        message="SQL cannot be blank.",
                    )
                ],
                metadata={
                    "validator": "read-only-sql-validator-v1",
                },
            )

        normalized_sql = self._normalize_sql(cleaned_sql)
        tokens = self._extract_tokens(normalized_sql)

        if not tokens:
            violations.append(
                SQLSafetyViolation(
                    rule="missing_sql_tokens",
                    message="SQL does not contain valid tokens.",
                )
            )
        else:
            first_token = tokens[0]

            if first_token not in self.allowed_start_tokens:
                violations.append(
                    SQLSafetyViolation(
                        rule="non_read_only_statement",
                        message="Only SELECT or WITH statements are allowed.",
                        token=first_token,
                    )
                )

        if self._has_multiple_statements(cleaned_sql):
            violations.append(
                SQLSafetyViolation(
                    rule="multiple_statements",
                    message="Multiple SQL statements are not allowed.",
                    token=";",
                )
            )

        for token in tokens:
            if token in self.blocked_tokens:
                violations.append(
                    SQLSafetyViolation(
                        rule="blocked_token",
                        message="SQL contains a blocked token.",
                        token=token,
                    )
                )

        status = "blocked" if violations else "approved"

        return SQLValidationResponse(
            status=status,
            sql=cleaned_sql,
            normalized_sql=normalized_sql,
            violations=violations,
            metadata={
                "validator": "read-only-sql-validator-v1",
                "tokens": tokens,
                "violation_count": len(violations),
            },
        )

    def _normalize_sql(
        self,
        sql: str,
    ) -> str:
        collapsed_sql = " ".join(sql.strip().split())

        if collapsed_sql.endswith(";"):
            collapsed_sql = collapsed_sql[:-1].strip()

        return collapsed_sql.lower()

    def _extract_tokens(
        self,
        normalized_sql: str,
    ) -> list[str]:
        return re.findall(
            r"\b[a-z_][a-z0-9_]*\b",
            normalized_sql,
        )

    def _has_multiple_statements(
        self,
        sql: str,
    ) -> bool:
        stripped_sql = sql.strip()

        if not stripped_sql:
            return False

        without_trailing_semicolon = stripped_sql[:-1] if stripped_sql.endswith(";") else stripped_sql

        return ";" in without_trailing_semicolon
