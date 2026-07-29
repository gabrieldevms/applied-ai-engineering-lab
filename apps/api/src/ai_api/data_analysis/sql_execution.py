import json
import re
import sqlite3
from typing import Any
from ai_api.data_analysis.exceptions import SQLExecutionError
from ai_api.data_analysis.schemas import (
    DatabaseSchema,
    DatabaseTable,
    DatabaseTableData,
    SQLExecutionRequest,
    SQLExecutionResponse,
    SQLQueryEvidence,
    SQLResultColumn,
)
from ai_api.data_analysis.sql_safety import ReadOnlySQLValidator


class SQLiteReadOnlyQueryExecutor:
    def __init__(
        self,
        sql_validator: ReadOnlySQLValidator | None = None,
    ) -> None:
        self.sql_validator = sql_validator or ReadOnlySQLValidator()

    def execute(
        self,
        request: SQLExecutionRequest,
    ) -> SQLExecutionResponse:
        validation = self.sql_validator.validate(request.sql)

        if validation.status == "blocked":
            return SQLExecutionResponse(
                status="blocked",
                sql=validation.sql,
                normalized_sql=validation.normalized_sql,
                validation=validation,
                columns=[],
                rows=[],
                row_count=0,
                truncated=False,
                evidence=SQLQueryEvidence(
                    query=validation.sql,
                    row_count=0,
                    column_count=0,
                    truncated=False,
                    metadata={
                        "execution_mode": "blocked_before_execution",
                    },
                ),
                metadata={
                    "executor": "sqlite-read-only-query-executor-v1",
                    "executed": False,
                },
            )

        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row

        try:
            inserted_row_count = self._load_schema_and_data(
                connection=connection,
                database_schema=request.database_schema,
                table_data=request.table_data,
            )

            connection.execute("PRAGMA query_only = ON")

            cursor = connection.execute(validation.sql)

            column_names = [
                column[0]
                for column in cursor.description or []
            ]

            fetched_rows = cursor.fetchmany(request.max_rows + 1)
            truncated = len(fetched_rows) > request.max_rows
            limited_rows = fetched_rows[: request.max_rows]

            rows = [
                {
                    column_name: row[column_name]
                    for column_name in column_names
                }
                for row in limited_rows
            ]

            columns = [
                SQLResultColumn(
                    name=column_name,
                )
                for column_name in column_names
            ]

            return SQLExecutionResponse(
                status="executed",
                sql=validation.sql,
                normalized_sql=validation.normalized_sql,
                validation=validation,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                truncated=truncated,
                evidence=SQLQueryEvidence(
                    query=validation.sql,
                    row_count=len(rows),
                    column_count=len(columns),
                    truncated=truncated,
                    metadata={
                        "execution_mode": "in_memory_sqlite_read_only",
                        "max_rows": request.max_rows,
                    },
                ),
                metadata={
                    "executor": "sqlite-read-only-query-executor-v1",
                    "executed": True,
                    "inserted_row_count": inserted_row_count,
                    "table_count": len(request.database_schema.tables),
                },
            )
        except SQLExecutionError:
            raise
        except sqlite3.Error as exc:
            raise SQLExecutionError(
                "SQL query could not be executed."
            ) from exc
        finally:
            connection.close()

    def _load_schema_and_data(
        self,
        connection: sqlite3.Connection,
        database_schema: DatabaseSchema,
        table_data: list[DatabaseTableData],
    ) -> int:
        tables_by_name = {
            table.name: table
            for table in database_schema.tables
        }

        table_data_by_name: dict[str, DatabaseTableData] = {}

        for data in table_data:
            if data.table_name not in tables_by_name:
                raise SQLExecutionError(
                    f"Table data references unknown table: {data.table_name}"
                )

            if data.table_name in table_data_by_name:
                raise SQLExecutionError(
                    f"Duplicate table data for table: {data.table_name}"
                )

            table_data_by_name[data.table_name] = data

        inserted_row_count = 0

        for table in database_schema.tables:
            self._create_table(
                connection=connection,
                table=table,
            )

            inserted_row_count += self._insert_rows(
                connection=connection,
                table=table,
                rows=table_data_by_name.get(
                    table.name,
                    DatabaseTableData(
                        table_name=table.name,
                        rows=[],
                    ),
                ).rows,
            )

        return inserted_row_count

    def _create_table(
        self,
        connection: sqlite3.Connection,
        table: DatabaseTable,
    ) -> None:
        if not table.columns:
            raise SQLExecutionError(
                f"Table '{table.name}' must define at least one column."
            )

        table_name = self._quote_identifier(table.name)

        column_definitions = [
            (
                f"{self._quote_identifier(column.name)} "
                f"{self._map_sqlite_type(column.data_type)}"
            )
            for column in table.columns
        ]

        connection.execute(
            f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
        )

    def _insert_rows(
        self,
        connection: sqlite3.Connection,
        table: DatabaseTable,
        rows: list[dict[str, Any]],
    ) -> int:
        if not rows:
            return 0

        table_name = self._quote_identifier(table.name)
        column_names = [
            column.name
            for column in table.columns
        ]
        known_columns = set(column_names)

        quoted_columns = [
            self._quote_identifier(column_name)
            for column_name in column_names
        ]

        placeholders = ", ".join(
            "?"
            for _ in column_names
        )

        insert_sql = (
            f"INSERT INTO {table_name} "
            f"({', '.join(quoted_columns)}) "
            f"VALUES ({placeholders})"
        )

        for row in rows:
            unknown_columns = set(row) - known_columns

            if unknown_columns:
                raise SQLExecutionError(
                    f"Table data for '{table.name}' contains unknown columns: "
                    f"{', '.join(sorted(unknown_columns))}"
                )

            values = [
                self._normalize_value(row.get(column_name))
                for column_name in column_names
            ]

            connection.execute(insert_sql, values)

        return len(rows)

    def _quote_identifier(
        self,
        identifier: str,
    ) -> str:
        if not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*",
            identifier,
        ):
            raise SQLExecutionError(
                "SQL identifiers must contain only letters, numbers and underscores."
            )

        return f'"{identifier}"'

    def _map_sqlite_type(
        self,
        data_type: str,
    ) -> str:
        normalized_type = data_type.strip().lower()

        if any(
            token in normalized_type
            for token in ["int", "bigint", "smallint"]
        ):
            return "INTEGER"

        if any(
            token in normalized_type
            for token in ["decimal", "numeric", "float", "double", "real"]
        ):
            return "REAL"

        if any(
            token in normalized_type
            for token in ["bool"]
        ):
            return "INTEGER"

        return "TEXT"

    def _normalize_value(
        self,
        value: Any,
    ) -> Any:
        if value is None:
            return None

        if isinstance(value, bool):
            return int(value)

        if isinstance(value, int | float | str):
            return value

        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
        )
