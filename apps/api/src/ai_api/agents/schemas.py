from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


AgentRunStatus = Literal["completed", "failed"]
AgentStepStatus = Literal["completed", "failed", "skipped"]


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
