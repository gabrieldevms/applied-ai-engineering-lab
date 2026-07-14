import hashlib
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from ai_api.agents.exceptions import ToolExecutionError
from ai_api.agents.schemas import (
    AgentRunResponse,
    AgentStep,
    AgentToolCall,
)
from ai_api.agents.tool_executor import ToolExecutionService


class AgentRuntime:
    def __init__(
        self,
        tool_execution_service: ToolExecutionService | None = None,
    ) -> None:
        self.tool_execution_service = (
            tool_execution_service or ToolExecutionService()
        )

    def run(
        self,
        objective: str,
        context: str | None = None,
        max_steps: int = 3,
        metadata: dict[str, Any] | None = None,
        tool_calls: Sequence[AgentToolCall] | None = None,
    ) -> AgentRunResponse:
        cleaned_objective = objective.strip()
        cleaned_context = context.strip() if context else None
        requested_tool_calls = list(tool_calls or [])

        if not cleaned_objective:
            raise ValueError("objective cannot be blank")

        if max_steps < 1:
            raise ValueError("max_steps must be greater than zero")

        run_id = self._build_run_id(cleaned_objective)

        steps: list[AgentStep] = []
        steps.append(
            self._build_understand_objective_step(cleaned_objective)
        )

        if len(steps) < max_steps:
            steps.append(
                self._build_inspect_context_step(cleaned_context)
            )

        execution_failed = False

        for index, tool_call in enumerate(requested_tool_calls, start=1):
            if len(steps) >= max_steps:
                break

            tool_step = self._execute_tool_call_step(
                index=index,
                tool_call=tool_call,
            )
            steps.append(tool_step)

            if tool_step.status == "failed":
                execution_failed = True
                break

        if len(steps) < max_steps:
            steps.append(
                self._build_final_answer_step(
                    objective=cleaned_objective,
                    context=cleaned_context,
                    tool_calls=requested_tool_calls,
                    execution_failed=execution_failed,
                )
            )

        status = "failed" if execution_failed else "completed"

        return AgentRunResponse(
            run_id=run_id,
            objective=cleaned_objective,
            status=status,
            final_answer=self._build_final_answer(
                objective=cleaned_objective,
                context=cleaned_context,
                total_steps=len(steps),
                total_tool_calls=len(requested_tool_calls),
                execution_failed=execution_failed,
            ),
            steps=steps,
            metadata={
                **(metadata or {}),
                "runtime": "deterministic-agent-runtime-v2",
                "created_at": datetime.now(UTC).isoformat(),
                "max_steps": max_steps,
                "has_context": cleaned_context is not None,
                "requested_tool_calls": len(requested_tool_calls),
                "executed_steps": len(steps),
            },
        )

    def _build_understand_objective_step(
        self,
        objective: str,
    ) -> AgentStep:
        return AgentStep(
            step_id="step-1",
            name="understand_objective",
            status="completed",
            input={"objective": objective},
            output={
                "summary": "Objective was received and normalized.",
            },
        )

    def _build_inspect_context_step(
        self,
        context: str | None,
    ) -> AgentStep:
        return AgentStep(
            step_id="step-2",
            name="inspect_context",
            status="completed" if context else "skipped",
            input={"has_context": context is not None},
            output={
                "summary": (
                    "Context was provided and inspected."
                    if context
                    else "No context was provided."
                )
            },
        )

    def _execute_tool_call_step(
        self,
        index: int,
        tool_call: AgentToolCall,
    ) -> AgentStep:
        step_id = f"step-tool-{index}"
        tool_name = tool_call.tool_name

        try:
            execution_response = self.tool_execution_service.execute(
                tool_name=tool_name,
                arguments=tool_call.arguments,
                metadata={
                    **tool_call.metadata,
                    "called_by": "agent-runtime",
                },
            )

            return AgentStep(
                step_id=step_id,
                name=f"tool_call:{tool_name}",
                status="completed",
                input={
                    "tool_name": tool_name,
                    "arguments": tool_call.arguments,
                },
                output=execution_response.model_dump(mode="json"),
                metadata={
                    "execution_id": execution_response.execution_id,
                },
            )
        except ToolExecutionError as exc:
            return AgentStep(
                step_id=step_id,
                name=f"tool_call:{tool_name}",
                status="failed",
                input={
                    "tool_name": tool_name,
                    "arguments": tool_call.arguments,
                },
                output={
                    "error": str(exc),
                },
                metadata={
                    "error_type": "tool_execution_error",
                },
            )

    def _build_final_answer_step(
        self,
        objective: str,
        context: str | None,
        tool_calls: Sequence[AgentToolCall],
        execution_failed: bool,
    ) -> AgentStep:
        return AgentStep(
            step_id="step-final",
            name="produce_final_answer",
            status="completed" if not execution_failed else "skipped",
            input={
                "objective": objective,
                "has_context": context is not None,
                "tool_calls": len(tool_calls),
            },
            output={
                "summary": (
                    "Final answer was produced."
                    if not execution_failed
                    else "Final answer was skipped because a tool call failed."
                ),
            },
        )

    def _build_final_answer(
        self,
        objective: str,
        context: str | None,
        total_steps: int,
        total_tool_calls: int,
        execution_failed: bool,
    ) -> str:
        if execution_failed:
            return (
                "Agent execution failed while calling a tool. "
                f"Objective: {objective}. "
                f"Executed steps: {total_steps}."
            )

        if total_tool_calls > 0:
            return (
                "Agent execution completed with tool calls. "
                f"Objective: {objective}. "
                f"Tool calls requested: {total_tool_calls}. "
                f"Executed steps: {total_steps}."
            )

        if context:
            return (
                "Agent execution completed using the provided context. "
                f"Objective: {objective}. "
                f"Executed steps: {total_steps}."
            )

        return (
            "Agent execution completed without additional context. "
            f"Objective: {objective}. "
            f"Executed steps: {total_steps}."
        )

    def _build_run_id(self, objective: str) -> str:
        objective_hash = hashlib.sha256(
            objective.encode("utf-8")
        ).hexdigest()[:12]

        return f"agent-run-{objective_hash}"
