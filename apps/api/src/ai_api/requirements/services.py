import logging
from collections.abc import Sequence
from ai_api.llm import LLMMessage, LLMProvider, LLMProviderError
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
        fallback_provider: LLMProvider | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.retry_config = retry_config or RetryConfig()
        self.fallback_provider = fallback_provider

    def analyze(
        self,
        requirement_text: str,
        language: str = "pt-BR",
    ) -> RequirementAnalysisResponse:
        messages = build_requirement_analysis_messages(
            requirement_text=requirement_text,
            language=language,
        )

        try:
            return self._analyze_with_provider(self.llm_provider, messages)
        except (RequirementAnalysisError, LLMProviderError) as exc:
            logger.warning("Primary LLM provider failed.")

            if self.fallback_provider is None:
                if isinstance(exc, RequirementAnalysisError):
                    raise

                raise RequirementAnalysisError("LLM provider failed.") from exc

            logger.info("Trying fallback LLM provider.")

            try:
                return self._analyze_with_provider(
                    self.fallback_provider,
                    messages,
                )
            except LLMProviderError as fallback_exc:
                raise RequirementAnalysisError(
                    "Fallback LLM provider failed."
                ) from fallback_exc

    def _analyze_with_provider(
        self,
        provider: LLMProvider,
        messages: Sequence[LLMMessage],
    ) -> RequirementAnalysisResponse:
        for attempt in range(1, self.retry_config.max_attempts + 1):
            try:
                llm_response = provider.generate(messages)
                return parse_requirement_analysis_response(llm_response.content)
            except (RequirementAnalysisError, LLMProviderError):
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
