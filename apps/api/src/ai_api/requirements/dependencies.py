from ai_api.config import get_settings
from ai_api.llm.factory import build_llm_provider
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.services import RequirementAnalyzerService


def get_requirement_analyzer_service() -> RequirementAnalyzerService:
    settings = get_settings()

    provider = build_llm_provider(
        settings=settings,
        fake_response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
    )

    return RequirementAnalyzerService(
        llm_provider=provider,
        retry_config=RetryConfig(
            max_attempts=settings.requirement_analysis_retry_attempts,
        ),
    )
