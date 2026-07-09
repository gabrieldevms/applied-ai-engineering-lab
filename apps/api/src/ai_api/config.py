from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


LLMProviderName = Literal["fake", "openai", "ollama"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="local")
    llm_provider: LLMProviderName = Field(default="fake")

    requirement_analysis_retry_attempts: int = Field(default=2, ge=1)

    openai_api_key: str | None = Field(default=None)
    openai_model: str | None = Field(default=None)

    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.1")
    ollama_timeout_seconds: float = Field(default=120, ge=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
