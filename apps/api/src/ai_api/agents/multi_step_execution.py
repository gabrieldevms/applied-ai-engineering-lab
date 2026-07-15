from ai_api.agents.runtime import AgentRuntime
from ai_api.agents.schemas import (
    AgentMultiStepExecutionResponse,
    AgentToolCall,
    ToolDefinition,
)
from ai_api.agents.tool_selection import AgentToolSelectionService


class AgentMultiStepExecutionService:
    def __init__(
        self,
        tool_selection_service: AgentToolSelectionService,
        agent_runtime: AgentRuntime | None = None,
    ) -> None:
        self.tool_selection_service = tool_selection_service
        self.agent_runtime = agent_runtime or AgentRuntime()

    def execute(
        self,
        objective: str,
        context: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
        max_plan_steps: int = 5,
        max_execution_steps: int = 10,
        language: str = "pt-BR",
        metadata: dict | None = None,
    ) -> AgentMultiStepExecutionResponse:
        cleaned_objective = objective.strip()

        if not cleaned_objective:
            raise ValueError("objective cannot be blank")

        selection_response = self.tool_selection_service.select_tools(
            objective=cleaned_objective,
            context=context,
            available_tools=available_tools,
            max_steps=max_plan_steps,
            language=language,
            metadata=metadata,
        )

        tool_calls = [
            AgentToolCall(
                tool_name=selected_tool.tool_name,
                arguments=selected_tool.arguments,
                metadata={
                    **selected_tool.metadata,
                    "source_step_id": selected_tool.source_step_id,
                    "source_step_objective": (
                        selected_tool.source_step_objective
                    ),
                    "rationale": selected_tool.rationale,
                },
            )
            for selected_tool in selection_response.selected_tool_calls
        ]

        agent_run = self.agent_runtime.run(
            objective=cleaned_objective,
            context=context,
            max_steps=max_execution_steps,
            metadata={
                **(metadata or {}),
                "execution": "agent-multi-step-execution-v1",
                "plan_summary": selection_response.plan_summary,
                "selected_tool_calls": len(tool_calls),
                "skipped_plan_steps": len(selection_response.skipped_steps),
                "planning_provider": selection_response.provider,
                "planning_model": selection_response.model,
            },
            tool_calls=tool_calls,
        )

        return AgentMultiStepExecutionResponse(
            objective=cleaned_objective,
            status=agent_run.status,
            plan_summary=selection_response.plan_summary,
            selected_tool_calls=selection_response.selected_tool_calls,
            skipped_steps=selection_response.skipped_steps,
            agent_run=agent_run,
            provider=selection_response.provider,
            model=selection_response.model,
            metadata={
                **selection_response.metadata,
                "executor": "agent-multi-step-execution-service-v1",
                "agent_run_id": agent_run.run_id,
                "agent_run_status": agent_run.status,
            },
        )
