from ai_api.llm import FakeLLMProvider
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.services import RequirementAnalyzerService


def get_requirement_analyzer_service() -> RequirementAnalyzerService:
    return RequirementAnalyzerService(
        llm_provider=FakeLLMProvider(
            response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
        ),
        retry_config=RetryConfig(max_attempts=2),
    )
