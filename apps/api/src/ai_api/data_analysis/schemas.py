from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


SQLValidationStatus = Literal[
    "approved",
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
