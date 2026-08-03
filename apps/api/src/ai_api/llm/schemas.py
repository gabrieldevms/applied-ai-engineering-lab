from typing import Literal
from pydantic import BaseModel, Field


LLMProviderStatus = Literal["configured", "missing_configuration"]


class LLMSafeConfigurationField(BaseModel):
    name: str
    label: str
    required: bool = True
    configured: bool
    sensitive: bool = False


class LLMProvidersResponse(BaseModel):
    supported_providers: list[str]
    active_provider: str


class LLMHealthResponse(BaseModel):
    provider: str
    model: str | None = None
    status: LLMProviderStatus
    configured: bool
    missing_settings: list[str] = Field(
        default_factory=list,
        description="Safe logical configuration names only. Do not expose env var names.",
    )
    safe_settings: list[LLMSafeConfigurationField] = Field(default_factory=list)
    safe_metadata: dict[str, str] = Field(default_factory=dict)
    message: str
    security_note: str = (
        "Provider credentials are backend-owned and are never returned by this endpoint."
    )
