import json
from pydantic import ValidationError
from ai_api.requirements.exceptions import RequirementAnalysisError
from ai_api.requirements.schemas import RequirementAnalysisResponse


def parse_requirement_analysis_response(
    llm_content: str,
) -> RequirementAnalysisResponse:
    try:
        parsed_content = json.loads(llm_content)
        return RequirementAnalysisResponse.model_validate(parsed_content)
    except json.JSONDecodeError as exc:
        raise RequirementAnalysisError(
            "LLM response is not a valid JSON object."
        ) from exc
    except ValidationError as exc:
        raise RequirementAnalysisError(
            "LLM response does not match the requirement analysis schema."
        ) from exc
