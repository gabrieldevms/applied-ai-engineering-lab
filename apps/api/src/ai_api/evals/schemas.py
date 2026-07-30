from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


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

EvaluationScenarioRunStatus = Literal[
    "passed",
    "warning",
    "failed",
    "skipped",
]

EvaluationDatasetRunStatus = Literal[
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


class EvaluationScenarioRunCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationScenarioRunResult(BaseModel):
    scenario_id: str
    scenario_name: str
    scenario_type: EvaluationScenarioType
    priority: EvaluationScenarioPriority
    status: EvaluationScenarioRunStatus
    output: dict[str, Any] = Field(default_factory=dict)
    checks: list[EvaluationScenarioRunCheck] = Field(default_factory=list)
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GoldenEvaluationDatasetRunRequest(BaseModel):
    dataset: GoldenEvaluationDataset | None = None
    scenario_ids: list[str] = Field(default_factory=list)
    scenario_types: list[EvaluationScenarioType] = Field(default_factory=list)
    dry_run: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class GoldenEvaluationDatasetRunResponse(BaseModel):
    status: EvaluationDatasetRunStatus
    dataset_name: str
    dataset_version: str
    scenario_count: int
    executed_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    skipped_count: int
    results: list[EvaluationScenarioRunResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


PromptRegressionOutputFormat = Literal[
    "text",
    "json",
]

PromptRegressionRunStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class PromptRegressionExpectation(BaseModel):
    expected_status: str | None = None
    required_output_markers: list[str] = Field(default_factory=list)
    forbidden_output_markers: list[str] = Field(default_factory=list)
    required_json_keys: list[str] = Field(default_factory=list)
    min_output_length: int = Field(default=0, ge=0)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptRegressionCase(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    prompt_name: str = Field(..., min_length=1)
    output_format: PromptRegressionOutputFormat = "json"
    input_payload: dict[str, Any]
    actual_output: str | dict[str, Any]
    expectations: PromptRegressionExpectation = Field(
        default_factory=PromptRegressionExpectation
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "prompt_name")
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


class PromptRegressionSuite(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cases: list[PromptRegressionCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class PromptRegressionCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptRegressionCaseResult(BaseModel):
    case_id: str
    case_name: str
    prompt_name: str
    status: PromptRegressionRunStatus
    checks: list[PromptRegressionCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptRegressionRunRequest(BaseModel):
    suite: PromptRegressionSuite | None = None
    case_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptRegressionRunResponse(BaseModel):
    status: PromptRegressionRunStatus
    suite_name: str
    suite_version: str
    case_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    results: list[PromptRegressionCaseResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


AIEvaluationReportStatus = Literal[
    "passed",
    "warning",
    "failed",
]

AIEvaluationReportSectionName = Literal[
    "golden_dataset",
    "prompt_regression",
    "multi_agent_qa_copilot",
]


class AIEvaluationReportSection(BaseModel):
    name: AIEvaluationReportSectionName
    status: AIEvaluationReportStatus
    score: float = Field(..., ge=0.0, le=1.0)
    summary: str
    highlights: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIEvaluationReportAggregationRequest(BaseModel):
    golden_dataset_run: GoldenEvaluationDatasetRunResponse | None = None
    prompt_regression_run: PromptRegressionRunResponse | None = None
    multi_agent_qa_copilot_evaluation: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_at_least_one_evaluation_source(
        self,
    ) -> "AIEvaluationReportAggregationRequest":
        if (
            self.golden_dataset_run is None
            and self.prompt_regression_run is None
            and self.multi_agent_qa_copilot_evaluation is None
        ):
            raise ValueError(
                "at least one evaluation source must be provided"
            )

        return self


class AIEvaluationReportAggregationResponse(BaseModel):
    status: AIEvaluationReportStatus
    score: float = Field(..., ge=0.0, le=1.0)
    summary: str
    sections: list[AIEvaluationReportSection] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
