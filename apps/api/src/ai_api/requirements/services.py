import json

from pydantic import ValidationError

from ai_api.llm import LLMProvider
from ai_api.requirements.prompts import build_requirement_analysis_messages
from ai_api.requirements.schemas import (
    RequirementAnalysisResponse,
)


class RequirementAnalysisError(Exception):
    """Raised when requirement analysis cannot be parsed or validated."""


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

        try:
            parsed_content = json.loads(llm_response.content)
            return RequirementAnalysisResponse.model_validate(parsed_content)
        except json.JSONDecodeError as exc:
            raise RequirementAnalysisError(
                "LLM response is not a valid JSON object."
            ) from exc
        except ValidationError as exc:
            raise RequirementAnalysisError(
                "LLM response does not match the requirement analysis schema."
            ) from exc
