import logging

from ai_api.llm import LLMProvider
from ai_api.requirements.exceptions import RequirementAnalysisError
from ai_api.requirements.parsers import parse_requirement_analysis_response
from ai_api.requirements.prompts import build_requirement_analysis_messages
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.schemas import RequirementAnalysisResponse


logger = logging.getLogger("ai_api.requirements")


class RequirementAnalyzerService:
    def __init__(
        self,
        llm_provider: LLMProvider,
        retry_config: RetryConfig | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.retry_config = retry_config or RetryConfig()

    def analyze(
        self,
        requirement_text: str,
        language: str = "pt-BR",
    ) -> RequirementAnalysisResponse:
        messages = build_requirement_analysis_messages(
            requirement_text=requirement_text,
            language=language,
        )

        for attempt in range(1, self.retry_config.max_attempts + 1):
            llm_response = self.llm_provider.generate(messages)

            try:
                return parse_requirement_analysis_response(llm_response.content)
            except RequirementAnalysisError:
                logger.warning(
                    "Requirement analysis attempt %s/%s failed.",
                    attempt,
                    self.retry_config.max_attempts,
                )

                if attempt == self.retry_config.max_attempts:
                    raise

        raise RequirementAnalysisError("Requirement analysis failed.")


__all__ = [
    "RequirementAnalysisError",
    "RequirementAnalyzerService",
]
