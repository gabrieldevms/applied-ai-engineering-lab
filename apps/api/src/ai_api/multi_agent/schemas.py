from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


MultiAgentRoleName = Literal[
    "orchestrator_agent",
    "requirement_analyst_agent",
    "functional_qa_agent",
    "test_automation_agent",
    "reviewer_agent",
    "report_agent",
]

MultiAgentStepStatus = Literal[
    "completed",
    "skipped",
    "failed",
]

MultiAgentQACopilotStatus = Literal[
    "completed",
    "partial",
    "failed",
]


class MultiAgentRoleDescriptor(BaseModel):
    name: MultiAgentRoleName
    title: str
    responsibility: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentMessage(BaseModel):
    sender: MultiAgentRoleName
    recipient: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentArtifact(BaseModel):
    name: str
    produced_by: MultiAgentRoleName
    content: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentSharedState(BaseModel):
    objective: str
    requirement_text: str
    language: str = "pt-BR"
    context: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[MultiAgentArtifact] = Field(default_factory=list)
    messages: list[MultiAgentMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentTraceStep(BaseModel):
    step_name: str
    agent_name: MultiAgentRoleName
    status: MultiAgentStepStatus
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentTaskResult(BaseModel):
    agent_name: MultiAgentRoleName
    status: MultiAgentStepStatus
    summary: str
    artifacts: list[MultiAgentArtifact] = Field(default_factory=list)
    messages: list[MultiAgentMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentFinalReport(BaseModel):
    summary: str
    requirement_understanding: list[str] = Field(default_factory=list)
    functional_coverage: list[str] = Field(default_factory=list)
    automation_strategy: list[str] = Field(default_factory=list)
    review_notes: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultiAgentQACopilotRequest(BaseModel):
    requirement_text: str = Field(..., min_length=1)
    objective: str | None = None
    language: str = "pt-BR"
    context: dict[str, Any] = Field(default_factory=dict)
    max_agents: int = Field(default=6, ge=1, le=6)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("requirement_text")
    @classmethod
    def validate_requirement_text(cls, value: str) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("requirement_text must not be blank")

        return normalized_value

    @field_validator("objective")
    @classmethod
    def normalize_objective(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            return None

        return normalized_value


class MultiAgentQACopilotResponse(BaseModel):
    status: MultiAgentQACopilotStatus
    copilot_name: str
    objective: str
    roles: list[MultiAgentRoleDescriptor]
    shared_state: MultiAgentSharedState
    task_results: list[MultiAgentTaskResult]
    final_report: MultiAgentFinalReport
    trace: list[MultiAgentTraceStep]
    metadata: dict[str, Any] = Field(default_factory=dict)
