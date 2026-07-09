from ai_api.config import get_settings
from ai_api.llm import FakeLLMProvider, OllamaProvider, OpenAIProvider
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.services import RequirementAnalyzerService


def get_requirement_analyzer_service() -> RequirementAnalyzerService:
    settings = get_settings()

    if settings.llm_provider == "fake":
        provider = FakeLLMProvider(
            response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
        )
    elif settings.llm_provider == "openai":
        if settings.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY must be configured.")

        if settings.openai_model is None:
            raise ValueError("OPENAI_MODEL must be configured.")

        provider = OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
    elif settings.llm_provider == "ollama":
        provider = OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    else:
        raise ValueError(
            f"Unsupported LLM provider configured: {settings.llm_provider}"
        )

    return RequirementAnalyzerService(
        llm_provider=provider,
        retry_config=RetryConfig(
            max_attempts=settings.requirement_analysis_retry_attempts,
        ),
    )
