from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


RiskSeverity = Literal["low", "medium", "high"]


class RequirementRisk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    severity: RiskSeverity


class RequirementAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_text: str = Field(
        min_length=1,
        description="Software requirement to be analyzed.",
    )
    language: str = Field(
        default="pt-BR",
        min_length=2,
        max_length=10,
        description="Expected language for the analysis response.",
    )

    @field_validator("requirement_text")
    @classmethod
    def requirement_text_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("requirement_text cannot be blank")

        return cleaned_value


class RequirementAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    business_rules: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    risks: list[RequirementRisk] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    positive_test_scenarios: list[str] = Field(default_factory=list)
    negative_test_scenarios: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    automation_opportunities: list[str] = Field(default_factory=list)
