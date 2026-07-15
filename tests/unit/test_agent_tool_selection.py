from ai_api.agents import (
    AgentToolSelectionService,
    ToolRegistry,
)
from ai_api.agents.planning import AgentPlanningService
from ai_api.llm import FakeLLMProvider


def test_agent_tool_selection_should_select_executable_tools_from_plan() -> None:
    service = AgentToolSelectionService(
        planning_service=AgentPlanningService(
            llm_provider=FakeLLMProvider(
                response_content="""
                {
                  "summary": "Plano para análise de requisito.",
                  "steps": [
                    {
                      "step_id": "plan-step-1",
                      "objective": "Analisar requisito.",
                      "tool_name": "requirements.analyze",
                      "arguments": {
                        "requirement_text": "Como cliente, quero gerar boleto.",
                        "language": "pt-BR"
                      },
                      "rationale": "A ferramenta de requisitos é adequada."
                    }
                  ]
                }
                """
            )
        )
    )

    response = service.select_tools(
        objective="Analisar requisito de boleto.",
        max_steps=3,
    )

    assert response.objective == "Analisar requisito de boleto."
    assert response.provider == "fake"
    assert len(response.selected_tool_calls) == 1
    assert response.selected_tool_calls[0].tool_name == "requirements.analyze"
    assert response.selected_tool_calls[0].arguments["language"] == "pt-BR"
    assert response.skipped_steps == []
    assert response.metadata["selector"] == "agent-tool-selection-service-v1"


def test_agent_tool_selection_should_skip_steps_without_tool() -> None:
    service = AgentToolSelectionService(
        planning_service=AgentPlanningService(
            llm_provider=FakeLLMProvider(
                response_content="""
                {
                  "summary": "Plano sem ferramenta.",
                  "steps": [
                    {
                      "step_id": "plan-step-1",
                      "objective": "Entender o objetivo.",
                      "tool_name": null,
                      "arguments": {},
                      "rationale": "Etapa de compreensão."
                    }
                  ]
                }
                """
            )
        )
    )

    response = service.select_tools(
        objective="Entender solicitação.",
        max_steps=3,
    )

    assert response.selected_tool_calls == []
    assert len(response.skipped_steps) == 1
    assert response.skipped_steps[0].reason == (
        "Plan step does not require a tool."
    )


def test_agent_tool_selection_should_skip_unregistered_tool() -> None:
    service = AgentToolSelectionService(
        planning_service=AgentPlanningService(
            llm_provider=FakeLLMProvider(
                response_content="""
                {
                  "summary": "Plano com ferramenta desconhecida.",
                  "steps": [
                    {
                      "step_id": "plan-step-1",
                      "objective": "Usar ferramenta desconhecida.",
                      "tool_name": "unknown.tool",
                      "arguments": {},
                      "rationale": "Teste de ferramenta inválida."
                    }
                  ]
                }
                """
            )
        ),
        registry=ToolRegistry(),
    )

    response = service.select_tools(
        objective="Executar plano inválido.",
        max_steps=3,
    )

    assert response.selected_tool_calls == []
    assert len(response.skipped_steps) == 1
    assert response.skipped_steps[0].reason == (
        "Tool is not registered: unknown.tool"
    )
