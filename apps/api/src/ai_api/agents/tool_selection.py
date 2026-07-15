from ai_api.agents.planning import AgentPlanningService
from ai_api.agents.schemas import (
    AgentSkippedPlanStep,
    AgentSelectedToolCall,
    AgentToolSelectionResponse,
    ToolDefinition,
)
from ai_api.agents.tool_executor import ToolExecutionService
from ai_api.agents.tool_registry import ToolRegistry


class AgentToolSelectionService:
    def __init__(
        self,
        planning_service: AgentPlanningService,
        registry: ToolRegistry | None = None,
        tool_execution_service: ToolExecutionService | None = None,
    ) -> None:
        self.planning_service = planning_service
        self.registry = registry or ToolRegistry()
        self.tool_execution_service = (
            tool_execution_service or ToolExecutionService(
                registry=self.registry,
            )
        )

    def select_tools(
        self,
        objective: str,
        context: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
        max_steps: int = 5,
        language: str = "pt-BR",
        metadata: dict | None = None,
    ) -> AgentToolSelectionResponse:
        tools = (
            available_tools
            if available_tools
            else self.registry.list_tools()
        )

        plan_response = self.planning_service.plan(
            objective=objective,
            context=context,
            available_tools=tools,
            max_steps=max_steps,
            language=language,
            metadata=metadata,
        )

        selected_tool_calls: list[AgentSelectedToolCall] = []
        skipped_steps: list[AgentSkippedPlanStep] = []

        for step in plan_response.steps:
            if step.tool_name is None:
                skipped_steps.append(
                    AgentSkippedPlanStep(
                        step_id=step.step_id,
                        objective=step.objective,
                        reason="Plan step does not require a tool.",
                        metadata={
                            "rationale": step.rationale,
                        },
                    )
                )
                continue

            tool_definition = self.registry.get(step.tool_name)

            if tool_definition is None:
                skipped_steps.append(
                    AgentSkippedPlanStep(
                        step_id=step.step_id,
                        objective=step.objective,
                        reason=f"Tool is not registered: {step.tool_name}",
                        metadata={
                            "rationale": step.rationale,
                        },
                    )
                )
                continue

            if not self.tool_execution_service.has_handler(step.tool_name):
                skipped_steps.append(
                    AgentSkippedPlanStep(
                        step_id=step.step_id,
                        objective=step.objective,
                        reason=(
                            "Tool has no execution handler: "
                            f"{step.tool_name}"
                        ),
                        metadata={
                            "rationale": step.rationale,
                        },
                    )
                )
                continue

            selected_tool_calls.append(
                AgentSelectedToolCall(
                    source_step_id=step.step_id,
                    source_step_objective=step.objective,
                    tool_name=step.tool_name,
                    arguments=step.arguments,
                    rationale=step.rationale,
                    metadata={
                        "tool_category": tool_definition.metadata.get(
                            "category",
                            "",
                        ),
                        "requires_llm": tool_definition.metadata.get(
                            "requires_llm",
                            False,
                        ),
                    },
                )
            )

        return AgentToolSelectionResponse(
            objective=plan_response.objective,
            plan_summary=plan_response.summary,
            selected_tool_calls=selected_tool_calls,
            skipped_steps=skipped_steps,
            provider=plan_response.provider,
            model=plan_response.model,
            metadata={
                **plan_response.metadata,
                "selector": "agent-tool-selection-service-v1",
                "available_tools": len(tools),
                "selected_tool_calls": len(selected_tool_calls),
                "skipped_steps": len(skipped_steps),
            },
        )
