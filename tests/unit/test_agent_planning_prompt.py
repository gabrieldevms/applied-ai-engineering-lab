import pytest
from ai_api.agents import ToolDefinition, build_agent_planning_messages


def test_build_agent_planning_messages_should_include_objective_and_tools() -> None:
    messages = build_agent_planning_messages(
        objective="Analisar requisito de boleto.",
        context="Contexto de QA.",
        available_tools=[
            ToolDefinition(
                name="requirements.analyze",
                description="Analisa requisitos.",
                metadata={"category": "qa"},
            )
        ],
        max_steps=3,
        language="pt-BR",
    )

    assert len(messages) == 2
    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert "Analisar requisito de boleto." in messages[1].content
    assert "requirements.analyze" in messages[1].content
    assert "Limite máximo de passos" in messages[1].content


def test_build_agent_planning_messages_should_reject_blank_objective() -> None:
    with pytest.raises(ValueError, match="objective cannot be blank"):
        build_agent_planning_messages(objective="   ")
