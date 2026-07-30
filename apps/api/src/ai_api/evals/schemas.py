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
    "agent_regression_run",
    "tool_calling_evaluation_run",
    "multi_agent_copilot_regression_run",
    "llm_as_judge_evaluation_run",
    "ci_evaluation_pipeline_run",
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


AgentRegressionRunStatus = Literal[
    "passed",
    "warning",
    "failed",
]

ToolCallingEvaluationRunStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class AgentRegressionExpectation(BaseModel):
    expected_status: str | None = None
    required_artifacts: list[str] = Field(default_factory=list)
    required_trace_steps: list[str] = Field(default_factory=list)
    required_metadata_keys: list[str] = Field(default_factory=list)
    forbidden_error_markers: list[str] = Field(default_factory=list)
    min_trace_steps: int = Field(default=0, ge=0)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRegressionCase(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    agent_name: str = Field(..., min_length=1)
    input_payload: dict[str, Any]
    actual_output: dict[str, Any]
    expectations: AgentRegressionExpectation = Field(
        default_factory=AgentRegressionExpectation
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "agent_name")
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


class AgentRegressionSuite(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cases: list[AgentRegressionCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class AgentRegressionCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRegressionCaseResult(BaseModel):
    case_id: str
    case_name: str
    agent_name: str
    status: AgentRegressionRunStatus
    checks: list[AgentRegressionCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRegressionRunRequest(BaseModel):
    suite: AgentRegressionSuite | None = None
    case_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRegressionRunResponse(BaseModel):
    status: AgentRegressionRunStatus
    suite_name: str
    suite_version: str
    case_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    results: list[AgentRegressionCaseResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallEvaluationRecord(BaseModel):
    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str = "completed"
    output: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("tool_name must not be blank")

        return normalized_value


class ToolCallingEvaluationExpectation(BaseModel):
    expected_status: str | None = None
    required_tool_names: list[str] = Field(default_factory=list)
    forbidden_tool_names: list[str] = Field(default_factory=list)
    required_argument_keys: list[str] = Field(default_factory=list)
    required_metadata_keys: list[str] = Field(default_factory=list)
    min_tool_calls: int = Field(default=0, ge=0)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallingEvaluationCase(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    workflow_name: str = Field(..., min_length=1)
    input_payload: dict[str, Any]
    actual_tool_calls: list[ToolCallEvaluationRecord] = Field(default_factory=list)
    actual_output: dict[str, Any] = Field(default_factory=dict)
    expectations: ToolCallingEvaluationExpectation = Field(
        default_factory=ToolCallingEvaluationExpectation
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "workflow_name")
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


class ToolCallingEvaluationSuite(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cases: list[ToolCallingEvaluationCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class ToolCallingEvaluationCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallingEvaluationCaseResult(BaseModel):
    case_id: str
    case_name: str
    workflow_name: str
    status: ToolCallingEvaluationRunStatus
    checks: list[ToolCallingEvaluationCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallingEvaluationRunRequest(BaseModel):
    suite: ToolCallingEvaluationSuite | None = None
    case_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallingEvaluationRunResponse(BaseModel):
    status: ToolCallingEvaluationRunStatus
    suite_name: str
    suite_version: str
    case_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    results: list[ToolCallingEvaluationCaseResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


MultiAgentCopilotRegressionRunStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class MultiAgentCopilotRegressionExpectation(BaseModel):
    expected_status: str | None = None
    expected_quality_gate: str | None = None
    expected_contract_status: str | None = None
    expected_conflict_status: str | None = None
    required_roles: list[str] = Field(default_factory=list)
    required_artifacts: list[str] = Field(default_factory=list)
    required_final_report_sections: list[str] = Field(default_factory=list)
    required_metadata_keys: list[str] = Field(default_factory=list)
    min_trace_steps: int = Field(default=0, ge=0)
    min_task_results: int = Field(default=0, ge=0)
    require_data_validation_evidence: bool = False
    forbidden_error_markers: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentCopilotRegressionCase(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    copilot_name: str = Field(..., min_length=1)
    input_payload: dict[str, Any]
    actual_output: dict[str, Any]
    expectations: MultiAgentCopilotRegressionExpectation = Field(
        default_factory=MultiAgentCopilotRegressionExpectation
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "copilot_name")
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


class MultiAgentCopilotRegressionSuite(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cases: list[MultiAgentCopilotRegressionCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class MultiAgentCopilotRegressionCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentCopilotRegressionCaseResult(BaseModel):
    case_id: str
    case_name: str
    copilot_name: str
    status: MultiAgentCopilotRegressionRunStatus
    checks: list[MultiAgentCopilotRegressionCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentCopilotRegressionRunRequest(BaseModel):
    suite: MultiAgentCopilotRegressionSuite | None = None
    case_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentCopilotRegressionRunResponse(BaseModel):
    status: MultiAgentCopilotRegressionRunStatus
    suite_name: str
    suite_version: str
    case_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    results: list[MultiAgentCopilotRegressionCaseResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


LLMAsJudgeVerdict = Literal[
    "pass",
    "warning",
    "fail",
]

LLMAsJudgeRunStatus = Literal[
    "passed",
    "warning",
    "failed",
]

LLMAsJudgeEvaluationTarget = Literal[
    "requirement_analysis",
    "rag_answer",
    "agent_output",
    "multi_agent_final_report",
    "tool_calling",
]


class LLMAsJudgeRubricItem(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    weight: float = Field(default=1.0, ge=0.0)
    passing_score: float = Field(default=0.7, ge=0.0, le=1.0)

    @field_validator("name", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class LLMAsJudgeOutput(BaseModel):
    verdict: LLMAsJudgeVerdict
    score: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., min_length=1)
    criteria_scores: dict[str, float] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("rationale")
    @classmethod
    def validate_rationale(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("rationale must not be blank")

        return normalized_value


class LLMAsJudgeExpectation(BaseModel):
    allowed_verdicts: list[LLMAsJudgeVerdict] = Field(
        default_factory=lambda: ["pass"]
    )
    min_score: float = Field(default=0.8, ge=0.0, le=1.0)
    required_rationale_markers: list[str] = Field(default_factory=list)
    forbidden_rationale_markers: list[str] = Field(default_factory=list)
    required_criteria: list[str] = Field(default_factory=list)
    require_strengths: bool = False
    require_weaknesses: bool = False
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMAsJudgeEvaluationCase(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    evaluation_target: LLMAsJudgeEvaluationTarget
    input_payload: dict[str, Any]
    candidate_output: str | dict[str, Any]
    rubric: list[LLMAsJudgeRubricItem] = Field(default_factory=list)
    judge_output: LLMAsJudgeOutput | None = None
    expectations: LLMAsJudgeExpectation = Field(
        default_factory=LLMAsJudgeExpectation
    )
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name")
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


class LLMAsJudgeEvaluationSuite(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cases: list[LLMAsJudgeEvaluationCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "version", "description")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class LLMAsJudgeEvaluationCheck(BaseModel):
    name: str
    status: EvaluationMetricStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMAsJudgeEvaluationCaseResult(BaseModel):
    case_id: str
    case_name: str
    evaluation_target: LLMAsJudgeEvaluationTarget
    status: LLMAsJudgeRunStatus
    checks: list[LLMAsJudgeEvaluationCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMAsJudgeEvaluationRunRequest(BaseModel):
    suite: LLMAsJudgeEvaluationSuite | None = None
    case_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMAsJudgeEvaluationRunResponse(BaseModel):
    status: LLMAsJudgeRunStatus
    suite_name: str
    suite_version: str
    case_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    average_score: float | None = None
    results: list[LLMAsJudgeEvaluationCaseResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


CIEvaluationPipelineStatus = Literal[
    "passed",
    "warning",
    "failed",
]

CIEvaluationPipelineStageName = Literal[
    "golden_dataset_smoke",
    "prompt_regression",
    "llm_output_evaluation",
    "rag_regression",
    "agent_regression",
    "tool_calling_evaluation",
    "multi_agent_copilot_regression",
    "llm_as_judge_evaluation",
]


class CIEvaluationPipelineStageResult(BaseModel):
    name: CIEvaluationPipelineStageName
    status: CIEvaluationPipelineStatus
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    summary: str
    output: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CIEvaluationPipelineRunRequest(BaseModel):
    include_golden_dataset_smoke: bool = True
    include_prompt_regression: bool = True
    include_llm_output_evaluation: bool = True
    include_rag_regression: bool = True
    include_agent_regression: bool = True
    include_tool_calling_evaluation: bool = True
    include_multi_agent_copilot_regression: bool = True
    include_llm_as_judge_evaluation: bool = True
    fail_on_warning: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CIEvaluationPipelineRunResponse(BaseModel):
    status: CIEvaluationPipelineStatus
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    stage_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    should_fail_ci: bool
    stages: list[CIEvaluationPipelineStageResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


AIUsageProvider = Literal[
    "openai",
    "ollama",
    "anthropic",
    "google",
    "fake",
    "unknown",
]

AIUsageComponent = Literal[
    "api",
    "evaluation",
    "llm",
    "rag",
    "agent",
    "multi_agent",
    "tool",
    "mcp",
]


class AIUsageRecordRequest(BaseModel):
    provider: AIUsageProvider = "unknown"
    model_name: str = Field(..., min_length=1)
    component: AIUsageComponent
    operation: str = Field(..., min_length=1)
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    embedding_tokens: int = Field(default=0, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    input_cost_per_1k_tokens_usd: float | None = Field(default=None, ge=0.0)
    output_cost_per_1k_tokens_usd: float | None = Field(default=None, ge=0.0)
    embedding_cost_per_1k_tokens_usd: float | None = Field(default=None, ge=0.0)
    total_cost_usd: float | None = Field(default=None, ge=0.0)
    currency: str = "USD"
    run_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("model_name", "operation", "currency")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class AIUsageRecord(BaseModel):
    record_id: str
    provider: AIUsageProvider
    model_name: str
    component: AIUsageComponent
    operation: str
    prompt_tokens: int
    completion_tokens: int
    embedding_tokens: int
    total_tokens: int
    input_cost_per_1k_tokens_usd: float | None = None
    output_cost_per_1k_tokens_usd: float | None = None
    embedding_cost_per_1k_tokens_usd: float | None = None
    input_cost_usd: float | None = None
    output_cost_usd: float | None = None
    embedding_cost_usd: float | None = None
    total_cost_usd: float | None = None
    currency: str = "USD"
    recorded_at: str
    run_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIUsageRecordsResponse(BaseModel):
    records: list[AIUsageRecord] = Field(default_factory=list)
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIUsageSummaryRequest(BaseModel):
    records: list[AIUsageRecord] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIUsageSummaryResponse(BaseModel):
    record_count: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_embedding_tokens: int
    total_tokens: int
    total_cost_usd: float | None = None
    average_cost_usd: float | None = None
    provider_coverage: dict[str, int] = Field(default_factory=dict)
    model_coverage: dict[str, int] = Field(default_factory=dict)
    component_coverage: dict[str, int] = Field(default_factory=dict)
    operation_coverage: dict[str, int] = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


AIRetrievalQualityStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class AIRetrievalQualityRecordRequest(BaseModel):
    component: AIUsageComponent = "rag"
    operation: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    requested_top_k: int | None = Field(default=None, ge=1)
    retrieved_chunks_count: int = Field(default=0, ge=0)
    relevant_chunks_count: int | None = Field(default=None, ge=0)
    citation_count: int = Field(default=0, ge=0)
    unique_source_count: int = Field(default=0, ge=0)
    required_source_count: int | None = Field(default=None, ge=0)
    matched_required_source_count: int | None = Field(default=None, ge=0)
    min_similarity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    max_similarity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    average_similarity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    expected_min_retrieved_chunks: int = Field(default=1, ge=0)
    expected_min_citations: int = Field(default=0, ge=0)
    min_quality_score: float = Field(default=0.7, ge=0.0, le=1.0)
    run_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("operation", "query")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class AIRetrievalQualityRecord(BaseModel):
    record_id: str
    component: AIUsageComponent
    operation: str
    query: str
    status: AIRetrievalQualityStatus
    requested_top_k: int | None = None
    retrieved_chunks_count: int
    relevant_chunks_count: int | None = None
    citation_count: int
    unique_source_count: int
    required_source_count: int | None = None
    matched_required_source_count: int | None = None
    precision_at_k: float | None = None
    source_coverage_score: float | None = None
    quality_score: float | None = None
    min_similarity_score: float | None = None
    max_similarity_score: float | None = None
    average_similarity_score: float | None = None
    expected_min_retrieved_chunks: int
    expected_min_citations: int
    min_quality_score: float
    risks: list[str] = Field(default_factory=list)
    recorded_at: str
    run_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIRetrievalQualityRecordsResponse(BaseModel):
    records: list[AIRetrievalQualityRecord] = Field(default_factory=list)
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIRetrievalQualitySummaryRequest(BaseModel):
    records: list[AIRetrievalQualityRecord] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIRetrievalQualitySummaryResponse(BaseModel):
    record_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    total_retrieved_chunks: int
    total_relevant_chunks: int
    total_citations: int
    total_unique_sources: int
    average_precision_at_k: float | None = None
    average_source_coverage_score: float | None = None
    average_quality_score: float | None = None
    average_similarity_score: float | None = None
    component_coverage: dict[str, int] = Field(default_factory=dict)
    operation_coverage: dict[str, int] = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


AIAgentExecutionMetricStatus = Literal[
    "passed",
    "warning",
    "failed",
]

AIAgentRunStatus = Literal[
    "completed",
    "partial",
    "failed",
    "blocked",
    "cancelled",
]


class AIAgentExecutionRecordRequest(BaseModel):
    component: AIUsageComponent = "agent"
    operation: str = Field(..., min_length=1)
    agent_name: str = Field(..., min_length=1)
    run_status: AIAgentRunStatus
    duration_ms: float | None = Field(default=None, ge=0.0)
    step_count: int = Field(default=0, ge=0)
    successful_step_count: int = Field(default=0, ge=0)
    failed_step_count: int = Field(default=0, ge=0)
    tool_call_count: int = Field(default=0, ge=0)
    successful_tool_call_count: int = Field(default=0, ge=0)
    failed_tool_call_count: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    fallback_count: int = Field(default=0, ge=0)
    error_count: int = Field(default=0, ge=0)
    human_approval_request_count: int = Field(default=0, ge=0)
    human_approval_granted_count: int = Field(default=0, ge=0)
    max_duration_ms: float | None = Field(default=None, ge=0.0)
    max_failed_steps: int = Field(default=0, ge=0)
    max_failed_tool_calls: int = Field(default=0, ge=0)
    max_error_count: int = Field(default=0, ge=0)
    min_quality_score: float = Field(default=0.7, ge=0.0, le=1.0)
    run_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("operation", "agent_name")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("value must not be blank")

        return normalized_value


class AIAgentExecutionRecord(BaseModel):
    record_id: str
    component: AIUsageComponent
    operation: str
    agent_name: str
    run_status: AIAgentRunStatus
    status: AIAgentExecutionMetricStatus
    duration_ms: float | None = None
    step_count: int
    successful_step_count: int
    failed_step_count: int
    tool_call_count: int
    successful_tool_call_count: int
    failed_tool_call_count: int
    retry_count: int
    fallback_count: int
    error_count: int
    human_approval_request_count: int
    human_approval_granted_count: int
    step_success_rate: float | None = None
    tool_success_rate: float | None = None
    human_approval_rate: float | None = None
    quality_score: float | None = None
    max_duration_ms: float | None = None
    max_failed_steps: int
    max_failed_tool_calls: int
    max_error_count: int
    min_quality_score: float
    risks: list[str] = Field(default_factory=list)
    recorded_at: str
    run_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIAgentExecutionRecordsResponse(BaseModel):
    records: list[AIAgentExecutionRecord] = Field(default_factory=list)
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIAgentExecutionSummaryRequest(BaseModel):
    records: list[AIAgentExecutionRecord] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIAgentExecutionSummaryResponse(BaseModel):
    record_count: int
    passed_count: int
    warning_count: int
    failed_count: int
    total_steps: int
    total_successful_steps: int
    total_failed_steps: int
    total_tool_calls: int
    total_successful_tool_calls: int
    total_failed_tool_calls: int
    total_retries: int
    total_fallbacks: int
    total_errors: int
    total_human_approval_requests: int
    total_human_approvals_granted: int
    average_duration_ms: float | None = None
    average_step_success_rate: float | None = None
    average_tool_success_rate: float | None = None
    average_human_approval_rate: float | None = None
    average_quality_score: float | None = None
    component_coverage: dict[str, int] = Field(default_factory=dict)
    agent_coverage: dict[str, int] = Field(default_factory=dict)
    operation_coverage: dict[str, int] = Field(default_factory=dict)
    run_status_coverage: dict[str, int] = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
