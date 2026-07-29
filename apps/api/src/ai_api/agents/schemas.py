from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from ai_api.rag.schemas import SemanticSearchDocument
from ai_api.data_analysis.schemas import DatabaseSchema, DatabaseTableData

AgentRunStatus = Literal["completed", "failed"]
AgentStepStatus = Literal["completed", "failed", "skipped"]
ToolExecutionStatus = Literal["completed", "failed"]

class AgentToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(
        min_length=1,
        description="Name of the tool the agent should call.",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tool_name")
    @classmethod
    def tool_name_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("tool_name cannot be blank")

        return cleaned_value


class AgentRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(
        min_length=1,
        description="Goal the agent should work on.",
    )
    context: str | None = Field(
        default=None,
        description="Optional context available to the agent.",
    )
    max_steps: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of execution steps.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    tool_calls: list[AgentToolCall] = Field(
        default_factory=list,
        max_length=5,
        description="Explicit tool calls the agent should execute.",
    )  

    @field_validator("objective")
    @classmethod
    def objective_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("objective cannot be blank")

        return cleaned_value

    @field_validator("context")
    @classmethod
    def context_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("context cannot be blank")

        return cleaned_value 


class AgentStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    name: str
    status: AgentStepStatus
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    objective: str
    status: AgentRunStatus
    final_answer: str
    steps: list[AgentStep]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=1,
        description="Unique tool name.",
    )
    description: str = Field(
        min_length=1,
        description="Human-readable tool description.",
    )
    input_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON-schema-like input contract.",
    )
    output_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON-schema-like output contract.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "description")
    @classmethod
    def required_tool_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value


class ToolRegistryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_tools: int
    tools: list[ToolDefinition]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(
        min_length=1,
        description="Name of the tool to execute.",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool execution arguments.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tool_name")
    @classmethod
    def tool_name_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("tool_name cannot be blank")

        return cleaned_value


class ToolExecutionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    execution_id: str
    tool_name: str
    status: ToolExecutionStatus
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


QAAgentDataValidationMode = Literal[
    "auto",
    "required",
    "disabled",
]


class QAAgentDataValidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str | None = Field(
        default=None,
        description=(
            "Optional data analysis objective. When omitted, the QA Agent "
            "will derive the objective from the requirement text."
        ),
    )
    mode: QAAgentDataValidationMode = Field(
        default="auto",
        description=(
            "Controls whether data validation should be automatically selected, "
            "always required or disabled."
        ),
    )
    database_schema: DatabaseSchema
    table_data: list[DatabaseTableData] = Field(default_factory=list)
    max_rows: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of rows returned by data validation.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective")
    @classmethod
    def objective_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("objective cannot be blank")

        return cleaned_value


class QAAgentRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_text: str = Field(
        min_length=1,
        description="Software requirement to be analyzed by the QA agent.",
    )
    knowledge_documents: list[SemanticSearchDocument] = Field(
        default_factory=list,
        max_length=20,
        description="Optional documents used as supporting knowledge.",
    )
    data_validation: QAAgentDataValidationRequest | None = Field(
        default=None,
        description=(
            "Optional data validation request executed through the "
            "Data Analyst Agent capability."
        ),
    )
    language: str = Field(
        default="pt-BR",
        min_length=2,
        max_length=10,
        description="Expected language for the QA analysis.",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Maximum number of retrieved chunks when knowledge documents are provided.",
    )
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=4000,
    )
    chunk_overlap: int = Field(
        default=120,
        ge=0,
        le=1000,
    )
    max_steps: int = Field(
        default=6,
        ge=3,
        le=10,
        description="Maximum number of agent execution steps.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("requirement_text")
    @classmethod
    def requirement_text_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("requirement_text cannot be blank")

        return cleaned_value

    @model_validator(mode="after")
    def chunk_overlap_must_be_smaller_than_chunk_size(
        self,
    ) -> "QAAgentRunRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        return self


class QAAgentRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: AgentRunStatus
    final_answer: str
    requirement_analysis: dict[str, Any] = Field(default_factory=dict)
    retrieved_context: dict[str, Any] | None = None
    data_validation_selection: dict[str, Any] | None = None
    data_validation: dict[str, Any] | None = None
    steps: list[AgentStep]
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentPlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(min_length=1)

    @field_validator("step_id", "objective", "rationale")
    @classmethod
    def required_plan_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value

    @field_validator("tool_name")
    @classmethod
    def optional_tool_name_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("tool_name cannot be blank")

        return cleaned_value


class AgentPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(
        min_length=1,
        description="Goal the agent should plan for.",
    )
    context: str | None = Field(
        default=None,
        description="Optional context for planning.",
    )
    available_tools: list[ToolDefinition] = Field(
        default_factory=list,
        max_length=20,
        description="Tools available for the agent planner.",
    )
    max_steps: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of planned steps.",
    )
    language: str = Field(
        default="pt-BR",
        min_length=2,
        max_length=10,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective")
    @classmethod
    def objective_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("objective cannot be blank")

        return cleaned_value

    @field_validator("context")
    @classmethod
    def context_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("context cannot be blank")

        return cleaned_value


class AgentPlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str
    summary: str
    steps: list[AgentPlanStep]
    provider: str
    model: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentSelectedToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_step_id: str = Field(min_length=1)
    source_step_objective: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "source_step_id",
        "source_step_objective",
        "tool_name",
        "rationale",
    )
    @classmethod
    def required_selected_tool_fields_cannot_be_blank(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value


class AgentSkippedPlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


AgentApprovalStatus = Literal[
    "approved",
    "rejected",
    "pending",
    "not_required",
]


class AgentApprovalPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    require_approval_for_tools: list[str] = Field(default_factory=list)
    auto_approve_safe_tools: bool = True
    reject_tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentToolApprovalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_step_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    status: AgentApprovalStatus
    reason: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentToolSelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(
        min_length=1,
        description="Goal the agent should select tools for.",
    )
    context: str | None = Field(
        default=None,
        description="Optional context for tool selection.",
    )
    available_tools: list[ToolDefinition] = Field(
        default_factory=list,
        max_length=20,
        description="Tools available for selection.",
    )
    max_steps: int = Field(
        default=5,
        ge=1,
        le=10,
    )
    language: str = Field(
        default="pt-BR",
        min_length=2,
        max_length=10,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective")
    @classmethod
    def objective_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("objective cannot be blank")

        return cleaned_value

    @field_validator("context")
    @classmethod
    def context_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("context cannot be blank")

        return cleaned_value


class AgentToolSelectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str
    plan_summary: str
    selected_tool_calls: list[AgentSelectedToolCall]
    skipped_steps: list[AgentSkippedPlanStep]
    provider: str
    model: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentExecutionState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    status: AgentRunStatus
    current_step: str | None = None
    total_steps: int = Field(ge=0)
    completed_steps: int = Field(ge=0)
    failed_steps: int = Field(ge=0)
    skipped_steps: int = Field(ge=0)
    tool_calls: int = Field(ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


AgentExecutionLogLevel = Literal[
    "info",
    "warning",
    "error",
]


class AgentExecutionLogEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    log_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    level: AgentExecutionLogLevel = "info"
    message: str = Field(min_length=1)
    created_at: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentExecutionLogListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[AgentExecutionLogEvent]
    total: int = Field(ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


AgentSafetyStatus = Literal[
    "passed",
    "blocked",
]


class AgentSafetyPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_selected_tool_calls: int = Field(default=5, ge=0, le=20)
    max_executable_tool_calls: int = Field(default=5, ge=0, le=10)
    blocked_tools: list[str] = Field(default_factory=list)
    allow_llm_tools: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentSafetyViolation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str = Field(min_length=1)
    message: str = Field(min_length=1)
    tool_name: str | None = None
    source_step_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentSafetyCheckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AgentSafetyStatus
    violations: list[AgentSafetyViolation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


AgentEvaluationStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class AgentEvaluationMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    status: AgentEvaluationStatus
    message: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(min_length=1)
    agent_run: AgentRunResponse
    execution_state: AgentExecutionState | None = None
    selected_tool_calls: list[AgentSelectedToolCall] = Field(default_factory=list)
    approval_decisions: list[AgentToolApprovalDecision] = Field(default_factory=list)
    safety_check: AgentSafetyCheckResponse | None = None
    execution_logs: list[AgentExecutionLogEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective")
    @classmethod
    def objective_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("objective cannot be blank")

        return cleaned_value


class AgentEvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AgentEvaluationStatus
    overall_score: float = Field(ge=0.0, le=1.0)
    metrics: list[AgentEvaluationMetric]
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMultiStepExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_policy: AgentApprovalPolicy = Field(
        default_factory=AgentApprovalPolicy,
        description="Policy used to decide whether selected tool calls require approval.",
    )

    safety_policy: AgentSafetyPolicy = Field(
        default_factory=AgentSafetyPolicy,
        description="Safety limits applied before executing selected tool calls.",
    )

    objective: str = Field(
        min_length=1,
        description="Goal the agent should plan, select tools and execute.",
    )
    context: str | None = Field(
        default=None,
        description="Optional context for planning and execution.",
    )
    available_tools: list[ToolDefinition] = Field(
        default_factory=list,
        max_length=20,
        description="Tools available for planning and selection.",
    )
    max_plan_steps: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of planned steps.",
    )
    max_execution_steps: int = Field(
        default=10,
        ge=3,
        le=10,
        description="Maximum number of runtime execution steps.",
    )
    language: str = Field(
        default="pt-BR",
        min_length=2,
        max_length=10,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective")
    @classmethod
    def objective_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("objective cannot be blank")

        return cleaned_value

    @field_validator("context")
    @classmethod
    def context_cannot_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("context cannot be blank")

        return cleaned_value


class AgentMultiStepExecutionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str
    status: AgentRunStatus
    plan_summary: str
    selected_tool_calls: list[AgentSelectedToolCall]
    skipped_steps: list[AgentSkippedPlanStep]
    approval_decisions: list[AgentToolApprovalDecision] = Field(default_factory=list)
    safety_check: AgentSafetyCheckResponse | None = None
    agent_run: AgentRunResponse
    execution_state: AgentExecutionState | None = None
    execution_logs: list[AgentExecutionLogEvent] = Field(default_factory=list)
    evaluation: AgentEvaluationResponse | None = None
    provider: str
    model: str
    metadata: dict[str, Any] = Field(default_factory=dict)
