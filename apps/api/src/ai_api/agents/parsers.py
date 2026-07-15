import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from ai_api.agents.schemas import AgentPlanStep


class ParsedAgentPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    steps: list[AgentPlanStep] = Field(min_length=1)


def parse_agent_plan_response(
    llm_content: str,
) -> ParsedAgentPlan:
    cleaned_content = llm_content.strip()

    if not cleaned_content:
        raise ValueError("LLM response is empty.")

    parsed_json = _extract_json_object(cleaned_content)

    try:
        return ParsedAgentPlan.model_validate(parsed_json)
    except ValidationError as exc:
        raise ValueError("LLM response does not match agent plan schema.") from exc


def _extract_json_object(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start_index = content.find("{")
        end_index = content.rfind("}")

        if start_index == -1 or end_index == -1 or end_index <= start_index:
            raise ValueError("LLM response does not contain a valid JSON object.")

        try:
            parsed = json.loads(content[start_index : end_index + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response does not contain a valid JSON object.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("LLM response must be a JSON object.")

    return parsed
