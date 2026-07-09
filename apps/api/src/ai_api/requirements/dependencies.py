from ai_api.config import get_settings
from ai_api.llm import FakeLLMProvider
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
