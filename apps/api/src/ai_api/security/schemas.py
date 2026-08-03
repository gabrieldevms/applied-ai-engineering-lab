from typing import Literal
from pydantic import BaseModel, Field


PromptInjectionRiskLevel = Literal["none", "low", "medium", "high"]
PromptInjectionRecommendedAction = Literal[
    "allow",
    "allow_with_warning",
    "require_review",
    "block",
]


class PromptInjectionAssessmentRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=20000,
        description="Text to assess. The response must not echo this value.",
    )
    input_source: str = Field(
        default="user_input",
        min_length=1,
        max_length=100,
        description="Logical source of the assessed text.",
    )
    workflow: str | None = Field(
        default=None,
        max_length=100,
        description="Optional workflow name, such as rag, qa_agent or data_analyst.",
    )


class PromptInjectionAssessmentResponse(BaseModel):
    risk_level: PromptInjectionRiskLevel
    recommended_action: PromptInjectionRecommendedAction
    is_blocking_required: bool
    detected_patterns: list[str] = Field(default_factory=list)
    risk_reasons: list[str] = Field(default_factory=list)
    input_source: str
    workflow: str | None = None
    inspected_character_count: int
