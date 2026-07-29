import json
from typing import Any
from pydantic import ValidationError
from ai_api.data_analysis.exceptions import SQLGenerationError
from ai_api.data_analysis.schemas import SQLGenerationCandidate


def extract_json_object(llm_content: str) -> dict[str, Any]:
    cleaned_content = llm_content.strip()

    if not cleaned_content:
        raise SQLGenerationError("LLM response is empty.")

    try:
        parsed_content = json.loads(cleaned_content)

        if isinstance(parsed_content, dict):
            return parsed_content

        raise SQLGenerationError(
            "LLM response is not a valid JSON object."
        )
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()

    for index, character in enumerate(cleaned_content):
        if character != "{":
            continue

        try:
            parsed_content, _ = decoder.raw_decode(
                cleaned_content[index:]
            )
        except json.JSONDecodeError:
            continue

        if isinstance(parsed_content, dict):
            return parsed_content

    raise SQLGenerationError(
        "LLM response is not a valid JSON object."
    )


def parse_sql_generation_response(
    llm_content: str,
) -> SQLGenerationCandidate:
    try:
        parsed_content = extract_json_object(llm_content)

        return SQLGenerationCandidate.model_validate(parsed_content)
    except SQLGenerationError:
        raise
    except ValidationError as exc:
        raise SQLGenerationError(
            "LLM response does not match the SQL generation schema."
        ) from exc
