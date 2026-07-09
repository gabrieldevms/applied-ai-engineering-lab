from typing import Literal

from pydantic import BaseModel, Field


LLMProviderStatus = Literal["configured", "missing_configuration"]


class LLMProvidersResponse(BaseModel):
    supported_providers: list[str]
    active_provider: str


class LLMHealthResponse(BaseModel):
    provider: str
    model: str | None = None
    status: LLMProviderStatus
    missing_settings: list[str] = Field(default_factory=list)
    safe_metadata: dict[str, str] = Field(default_factory=dict)
    message: str
