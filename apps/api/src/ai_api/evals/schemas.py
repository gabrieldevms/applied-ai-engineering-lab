from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


EvaluationScenarioType = Literal[
    "requirement_analysis",
    "rag_answer",
    "qa_agent",
    "data_analyst_agent",
    "multi_agent_qa_copilot",
    "mcp_tool",
]

EvaluationScenarioPriority = Literal[
    "smoke",
    "regression",
    "edge_case",
]

EvaluationDatasetValidationStatus = Literal[
    "valid",
    "warning",
    "invalid",
]

EvaluationMetricStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class EvaluationExpectation(BaseModel):
    expected_status: str | None = None
    expected_quality_gate: str | None = None
    required_output_markers: list[str] = Field(default_factory=list)
    required_metadata_keys: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationScenario(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    type: EvaluationScenarioType
    priority: EvaluationScenarioPriority = "regression"
    description: str = Field(..., min_length=1)
    input_payload: dict[str, Any]
    expectations: EvaluationExpectation = Field(default_factory=EvaluationExpectation)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value

    @field_validator("input_payload")
    @classmethod
    def validate_input_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("input_payload must not be empty")

        return value


class GoldenEvaluationDataset(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    scenarios: list[EvaluationScenario] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class EvaluationDatasetValidationMetric(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationDatasetValidationResponse(BaseModel):
    status: EvaluationDatasetValidationStatus
    dataset_name: str
    dataset_version: str
    scenario_count: int
    type_coverage: dict[str, int]
    missing_required_types: list[str] = Field(default_factory=list)
    metrics: list[EvaluationDatasetValidationMetric] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
