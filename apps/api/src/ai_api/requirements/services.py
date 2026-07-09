from ai_api.llm import LLMProvider
from ai_api.requirements.exceptions import RequirementAnalysisError
from ai_api.requirements.parsers import parse_requirement_analysis_response
from ai_api.requirements.prompts import build_requirement_analysis_messages
from ai_api.requirements.schemas import RequirementAnalysisResponse


class RequirementAnalyzerService:
    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    def analyze(
        self,
        requirement_text: str,
        language: str = "pt-BR",
    ) -> RequirementAnalysisResponse:
        messages = build_requirement_analysis_messages(
            requirement_text=requirement_text,
            language=language,
        )

        llm_response = self.llm_provider.generate(messages)

        return parse_requirement_analysis_response(llm_response.content)


__all__ = [
    "RequirementAnalysisError",
    "RequirementAnalyzerService",
]
