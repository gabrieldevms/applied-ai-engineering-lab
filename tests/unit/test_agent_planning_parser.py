import pytest
from ai_api.agents import parse_agent_plan_response


def test_parse_agent_plan_response_should_parse_valid_json() -> None:
    parsed_plan = parse_agent_plan_response(
        """
        {
          "summary": "Plano válido.",
          "steps": [
            {
              "step_id": "plan-step-1",
              "objective": "Entender objetivo.",
              "tool_name": null,
              "arguments": {},
              "rationale": "Necessário para planejar."
            }
          ]
        }
        """
    )

    assert parsed_plan.summary == "Plano válido."
    assert len(parsed_plan.steps) == 1
    assert parsed_plan.steps[0].step_id == "plan-step-1"


def test_parse_agent_plan_response_should_extract_json_from_text() -> None:
    parsed_plan = parse_agent_plan_response(
        """
        Aqui está o plano:
        {
          "summary": "Plano válido.",
          "steps": [
            {
              "step_id": "plan-step-1",
              "objective": "Entender objetivo.",
              "tool_name": "requirements.analyze",
              "arguments": {},
              "rationale": "Análise necessária."
            }
          ]
        }
        """
    )

    assert parsed_plan.steps[0].tool_name == "requirements.analyze"


def test_parse_agent_plan_response_should_reject_empty_response() -> None:
    with pytest.raises(ValueError, match="LLM response is empty."):
        parse_agent_plan_response("   ")


def test_parse_agent_plan_response_should_reject_invalid_schema() -> None:
    with pytest.raises(
        ValueError,
        match="LLM response does not match agent plan schema.",
    ):
        parse_agent_plan_response(
            """
            {
              "summary": "Plano inválido.",
              "steps": []
            }
            """
        )
