from ai_api.agents import (
    AgentMultiStepExecutionService,
    AgentPlanningService,
    AgentToolSelectionService,
)
from ai_api.llm import FakeLLMProvider


def test_agent_multi_step_execution_should_plan_select_and_execute_tool() -> None:
    execution_service = AgentMultiStepExecutionService(
        tool_selection_service=AgentToolSelectionService(
            planning_service=AgentPlanningService(
                llm_provider=FakeLLMProvider(
                    response_content="""
                    {
                      "summary": "Plano para análise de requisito.",
                      "steps": [
                        {
                          "step_id": "plan-step-1",
                          "objective": "Entender solicitação.",
                          "tool_name": null,
                          "arguments": {},
                          "rationale": "Compreender o objetivo antes de executar."
                        },
                        {
                          "step_id": "plan-step-2",
                          "objective": "Analisar requisito.",
                          "tool_name": "requirements.analyze",
                          "arguments": {
                            "requirement_text": "Como cliente, quero gerar boleto.",
                            "language": "pt-BR"
                          },
                          "rationale": "A análise de requisitos identifica riscos e cenários."
                        }
                      ]
                    }
                    """
                )
            )
        )
    )

    response = execution_service.execute(
        objective="Analisar requisito de boleto.",
        context="Contexto de qualidade.",
        max_plan_steps=3,
        max_execution_steps=5,
        language="pt-BR",
        metadata={
            "domain": "qa",
        },
    )

    assert response.status == "completed"
    assert response.objective == "Analisar requisito de boleto."
    assert response.plan_summary == "Plano para análise de requisito."
    assert response.provider == "fake"
    assert len(response.selected_tool_calls) == 1
    assert response.selected_tool_calls[0].tool_name == "requirements.analyze"
    assert len(response.skipped_steps) == 1
    assert response.agent_run.status == "completed"
    assert response.agent_run.steps[2].name == "tool_call:requirements.analyze"
    assert response.agent_run.steps[2].status == "completed"
    assert response.execution_state is not None
    assert response.execution_state.run_id == response.agent_run.run_id
    assert response.execution_state.status == "completed"
    assert response.execution_state.tool_calls == 1
    assert response.execution_state.metadata["source"] == "multi_step_execution"
    assert response.metadata["executor"] == (
        "agent-multi-step-execution-service-v1"
    )


def test_agent_multi_step_execution_should_complete_when_no_tools_are_selected() -> None:
    execution_service = AgentMultiStepExecutionService(
        tool_selection_service=AgentToolSelectionService(
            planning_service=AgentPlanningService(
                llm_provider=FakeLLMProvider(
                    response_content="""
                    {
                      "summary": "Plano sem ferramentas.",
                      "steps": [
                        {
                          "step_id": "plan-step-1",
                          "objective": "Entender objetivo.",
                          "tool_name": null,
                          "arguments": {},
                          "rationale": "Nenhuma ferramenta é necessária."
                        }
                      ]
                    }
                    """
                )
            )
        )
    )

    response = execution_service.execute(
        objective="Entender solicitação.",
        max_plan_steps=3,
        max_execution_steps=3,
    )

    assert response.status == "completed"
    assert response.selected_tool_calls == []
    assert len(response.skipped_steps) == 1
    assert response.agent_run.status == "completed"
    assert response.agent_run.metadata["requested_tool_calls"] == 0


def test_agent_multi_step_execution_should_return_failed_status_when_tool_fails() -> None:
    execution_service = AgentMultiStepExecutionService(
        tool_selection_service=AgentToolSelectionService(
            planning_service=AgentPlanningService(
                llm_provider=FakeLLMProvider(
                    response_content="""
                    {
                      "summary": "Plano com ferramenta inválida.",
                      "steps": [
                        {
                          "step_id": "plan-step-1",
                          "objective": "Executar análise inválida.",
                          "tool_name": "requirements.analyze",
                          "arguments": {},
                          "rationale": "Teste de falha de execução."
                        }
                      ]
                    }
                    """
                )
            )
        )
    )

    response = execution_service.execute(
        objective="Executar fluxo inválido.",
        max_plan_steps=3,
        max_execution_steps=4,
    )

    assert response.status == "failed"
    assert len(response.selected_tool_calls) == 1
    assert response.agent_run.status == "failed"
    assert response.agent_run.steps[2].name == "tool_call:requirements.analyze"
    assert response.agent_run.steps[2].status == "failed"
    assert response.execution_state is not None
    assert response.execution_state.status == "failed"
    assert response.execution_state.failed_steps == 1
    assert response.execution_state.tool_calls == 1
