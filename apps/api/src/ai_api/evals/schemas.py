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


EvaluationTelemetryEventType = Literal[
    "evaluation_run",
    "golden_dataset_run",
    "llm_output_evaluation_run",
    "rag_regression_run",
    "scenario_run",
    "prompt_regression_run",
    "report_aggregation",
    "copilot_evaluation",
    "llm_call",
    "rag_retrieval",
    "agent_run",
    "multi_agent_run",
    "tool_call",
    "mcp_tool_call",
]

EvaluationTelemetryComponent = Literal[
    "api",
    "evaluation",
    "llm",
    "rag",
    "agent",
    "multi_agent",
    "tool",
    "mcp",
]

EvaluationTelemetryStatus = Literal[
    "started",
    "completed",
    "warning",
    "failed",
    "skipped",
]


class EvaluationTelemetryRecordRequest(BaseModel):
    event_type: EvaluationTelemetryEventType
    component: EvaluationTelemetryComponent
    status: EvaluationTelemetryStatus
    source: str = Field(..., min_length=1)
    started_at: str | None = None
    finished_at: str | None = None
    duration_ms: float | None = Field(default=None, ge=0.0)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    run_id: str | None = None
    scenario_id: str | None = None
    case_id: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("source must not be blank")

        return normalized_value


class EvaluationTelemetryEvent(BaseModel):
    event_id: str
    event_type: EvaluationTelemetryEventType
    component: EvaluationTelemetryComponent
    status: EvaluationTelemetryStatus
    source: str
    recorded_at: str
    started_at: str | None = None
    finished_at: str | None = None
    duration_ms: float | None = Field(default=None, ge=0.0)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    run_id: str | None = None
    scenario_id: str | None = None
    case_id: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationTelemetryEventsResponse(BaseModel):
    events: list[EvaluationTelemetryEvent] = Field(default_factory=list)
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationTelemetrySummaryRequest(BaseModel):
    events: list[EvaluationTelemetryEvent] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationTelemetrySummaryResponse(BaseModel):
    status: AIEvaluationReportStatus
    event_count: int
    completed_count: int
    warning_count: int
    failed_count: int
    skipped_count: int
    average_score: float | None = None
    average_duration_ms: float | None = None
    event_type_coverage: dict[str, int] = Field(default_factory=dict)
    component_coverage: dict[str, int] = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


LLMOutputEvaluationRunStatus = Literal[
    "passed",
    "warning",
    "failed",
]

LLMOutputFormat = Literal[
    "text",
    "json",
]

RAGRegressionRunStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class LLMOutputEvaluationExpectation(BaseModel):
    expected_status: str | None = None
    required_output_markers: list[str] = Field(default_factory=list)
    forbidden_output_markers: list[str] = Field(default_factory=list)
    required_json_keys: list[str] = Field(default_factory=list)
    min_output_length: int = Field(default=0, ge=0)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMOutputEvaluationCase(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    component_name: str = Field(..., min_length=1)
    output_format: LLMOutputFormat = "json"
    input_payload: dict[str, Any]
    actual_output: str | dict[str, Any]
    expectations: LLMOutputEvaluationExpectation = Field(
        default_factory=LLMOutputEvaluationExpectation
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "component_name")
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


class LLMOutputEvaluationSuite(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cases: list[LLMOutputEvaluationCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class LLMOutputEvaluationCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMOutputEvaluationCaseResult(BaseModel):
    case_id: str
    case_name: str
    component_name: str
    status: LLMOutputEvaluationRunStatus
    checks: list[LLMOutputEvaluationCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMOutputEvaluationRunRequest(BaseModel):
    suite: LLMOutputEvaluationSuite | None = None
    case_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMOutputEvaluationRunResponse(BaseModel):
    status: LLMOutputEvaluationRunStatus
    suite_name: str
    suite_version: str
    case_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    results: list[LLMOutputEvaluationCaseResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGRegressionExpectation(BaseModel):
    expected_status: str | None = None
    required_answer_markers: list[str] = Field(default_factory=list)
    forbidden_answer_markers: list[str] = Field(default_factory=list)
    required_citation_sources: list[str] = Field(default_factory=list)
    required_metadata_keys: list[str] = Field(default_factory=list)
    min_retrieved_chunks: int = Field(default=0, ge=0)
    require_citations: bool = True
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGRegressionCase(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    input_payload: dict[str, Any]
    actual_output: dict[str, Any]
    expectations: RAGRegressionExpectation = Field(
        default_factory=RAGRegressionExpectation
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "query")
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


class RAGRegressionSuite(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cases: list[RAGRegressionCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class RAGRegressionCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGRegressionCaseResult(BaseModel):
    case_id: str
    case_name: str
    query: str
    status: RAGRegressionRunStatus
    checks: list[RAGRegressionCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGRegressionRunRequest(BaseModel):
    suite: RAGRegressionSuite | None = None
    case_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGRegressionRunResponse(BaseModel):
    status: RAGRegressionRunStatus
    suite_name: str
    suite_version: str
    case_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    results: list[RAGRegressionCaseResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
