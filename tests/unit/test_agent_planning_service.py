from ai_api.agents import AgentPlanningService, ToolDefinition
from ai_api.llm import FakeLLMProvider


def test_agent_planning_service_should_generate_structured_plan() -> None:
    service = AgentPlanningService(
        llm_provider=FakeLLMProvider(
            response_content="""
            {
              "summary": "Plano para análise de requisito.",
              "steps": [
                {
                  "step_id": "plan-step-1",
                  "objective": "Analisar requisito.",
                  "tool_name": "requirements.analyze",
                  "arguments": {},
                  "rationale": "Identificar riscos e critérios."
                }
              ]
            }
            """
        )
    )

    response = service.plan(
        objective="Analisar requisito de boleto.",
        available_tools=[
            ToolDefinition(
                name="requirements.analyze",
                description="Analisa requisitos.",
            )
        ],
        max_steps=3,
    )

    assert response.objective == "Analisar requisito de boleto."
    assert response.summary == "Plano para análise de requisito."
    assert response.provider == "fake"
    assert response.model == "fake-llm-v1"
    assert len(response.steps) == 1
    assert response.steps[0].tool_name == "requirements.analyze"
    assert response.metadata["planner"] == "agent-planning-service-v1"


def test_agent_planning_service_should_limit_steps_to_max_steps() -> None:
    service = AgentPlanningService(
        llm_provider=FakeLLMProvider(
            response_content="""
            {
              "summary": "Plano longo.",
              "steps": [
                {
                  "step_id": "plan-step-1",
                  "objective": "Passo 1.",
                  "tool_name": null,
                  "arguments": {},
                  "rationale": "Racional 1."
                },
                {
                  "step_id": "plan-step-2",
                  "objective": "Passo 2.",
                  "tool_name": null,
                  "arguments": {},
                  "rationale": "Racional 2."
                }
              ]
            }
            """
        )
    )

    response = service.plan(
        objective="Executar plano curto.",
        max_steps=1,
    )

    assert len(response.steps) == 1
    assert response.metadata["requested_max_steps"] == 1
    assert response.metadata["returned_steps"] == 1
