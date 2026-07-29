from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


SQLValidationStatus = Literal[
    "approved",
    "blocked",
]

SQLExecutionStatus = Literal[
    "executed",
    "blocked",
]


class DatabaseColumn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    data_type: str = Field(min_length=1)
    description: str | None = None
    nullable: bool = True
    primary_key: bool = False
    foreign_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "data_type")
    @classmethod
    def text_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value


class DatabaseTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str | None = None
    columns: list[DatabaseColumn] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("table name cannot be blank")

        return cleaned_value


class DatabaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str | None = None
    tables: list[DatabaseTable] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("schema name cannot be blank")

        return cleaned_value


class DatabaseTableData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_name: str = Field(min_length=1)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("table_name")
    @classmethod
    def table_name_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("table name cannot be blank")

        return cleaned_value


class NaturalLanguageSQLRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    database_schema: DatabaseSchema
    language: str = "pt-BR"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("question", "language")
    @classmethod
    def text_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value


class SQLGenerationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sql: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("sql", "explanation")
    @classmethod
    def text_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value


class SQLSafetyViolation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str = Field(min_length=1)
    message: str = Field(min_length=1)
    token: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: SQLValidationStatus
    sql: str
    normalized_sql: str
    violations: list[SQLSafetyViolation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLGenerationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: SQLValidationStatus
    request: NaturalLanguageSQLRequest
    candidate: SQLGenerationCandidate
    validation: SQLValidationResponse
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sql: str = Field(min_length=1)
    database_schema: DatabaseSchema
    table_data: list[DatabaseTableData] = Field(default_factory=list)
    max_rows: int = Field(default=100, ge=1, le=1000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("sql")
    @classmethod
    def sql_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("SQL cannot be blank")

        return cleaned_value


class SQLResultColumn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    data_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLQueryEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    truncated: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLExecutionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: SQLExecutionStatus
    sql: str
    normalized_sql: str
    validation: SQLValidationResponse
    columns: list[SQLResultColumn] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = Field(ge=0)
    truncated: bool = False
    evidence: SQLQueryEvidence
    metadata: dict[str, Any] = Field(default_factory=dict)
