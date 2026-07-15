from ai_api.agents.parsers import parse_agent_plan_response
from ai_api.agents.prompts import build_agent_planning_messages
from ai_api.agents.schemas import (
    AgentPlanResponse,
    ToolDefinition,
)
from ai_api.llm import LLMProvider, LLMProviderError


class AgentPlanningService:
    def __init__(
        self,
        llm_provider: LLMProvider,
    ) -> None:
        self.llm_provider = llm_provider

    def plan(
        self,
        objective: str,
        context: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
        max_steps: int = 5,
        language: str = "pt-BR",
        metadata: dict | None = None,
    ) -> AgentPlanResponse:
        messages = build_agent_planning_messages(
            objective=objective,
            context=context,
            available_tools=available_tools,
            max_steps=max_steps,
            language=language,
        )

        try:
            llm_response = self.llm_provider.generate(messages)
        except LLMProviderError as exc:
            raise ValueError("LLM provider failed during agent planning.") from exc

        parsed_plan = parse_agent_plan_response(llm_response.content)

        limited_steps = parsed_plan.steps[:max_steps]

        return AgentPlanResponse(
            objective=objective.strip(),
            summary=parsed_plan.summary,
            steps=limited_steps,
            provider=llm_response.provider,
            model=llm_response.model,
            metadata={
                **(metadata or {}),
                "planner": "agent-planning-service-v1",
                "requested_max_steps": max_steps,
                "returned_steps": len(limited_steps),
            },
        )
