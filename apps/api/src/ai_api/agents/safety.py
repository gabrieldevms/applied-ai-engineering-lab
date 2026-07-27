from collections.abc import Sequence
from ai_api.agents.schemas import (
    AgentSafetyCheckResponse,
    AgentSafetyPolicy,
    AgentSafetyViolation,
    AgentSelectedToolCall,
    AgentToolApprovalDecision,
)


class AgentSafetyService:
    def evaluate_tool_calls(
        self,
        selected_tool_calls: Sequence[AgentSelectedToolCall],
        executable_tool_calls: Sequence[AgentSelectedToolCall],
        approval_decisions: Sequence[AgentToolApprovalDecision],
        safety_policy: AgentSafetyPolicy | None = None,
    ) -> AgentSafetyCheckResponse:
        policy = safety_policy or AgentSafetyPolicy()

        violations: list[AgentSafetyViolation] = []

        if len(selected_tool_calls) > policy.max_selected_tool_calls:
            violations.append(
                AgentSafetyViolation(
                    rule="max_selected_tool_calls",
                    message=(
                        "Selected tool calls exceed the configured safety limit."
                    ),
                    metadata={
                        "limit": policy.max_selected_tool_calls,
                        "actual": len(selected_tool_calls),
                    },
                )
            )

        if len(executable_tool_calls) > policy.max_executable_tool_calls:
            violations.append(
                AgentSafetyViolation(
                    rule="max_executable_tool_calls",
                    message=(
                        "Executable tool calls exceed the configured safety limit."
                    ),
                    metadata={
                        "limit": policy.max_executable_tool_calls,
                        "actual": len(executable_tool_calls),
                    },
                )
            )

        for tool_call in executable_tool_calls:
            if tool_call.tool_name in policy.blocked_tools:
                violations.append(
                    AgentSafetyViolation(
                        rule="blocked_tool",
                        message="Tool is blocked by the safety policy.",
                        tool_name=tool_call.tool_name,
                        source_step_id=tool_call.source_step_id,
                        metadata={
                            "blocked_tools": policy.blocked_tools,
                        },
                    )
                )

            if (
                not policy.allow_llm_tools
                and tool_call.metadata.get("requires_llm") is True
            ):
                violations.append(
                    AgentSafetyViolation(
                        rule="llm_tool_not_allowed",
                        message="LLM-based tools are blocked by the safety policy.",
                        tool_name=tool_call.tool_name,
                        source_step_id=tool_call.source_step_id,
                        metadata={
                            "requires_llm": True,
                        },
                    )
                )

        status = "blocked" if violations else "passed"

        return AgentSafetyCheckResponse(
            status=status,
            violations=violations,
            metadata={
                **policy.metadata,
                "safety_service": "agent-safety-service-v1",
                "selected_tool_calls": len(selected_tool_calls),
                "executable_tool_calls": len(executable_tool_calls),
                "approval_decisions": len(approval_decisions),
                "violations": len(violations),
            },
        )

    def filter_safe_executable_tool_calls(
        self,
        executable_tool_calls: Sequence[AgentSelectedToolCall],
        safety_policy: AgentSafetyPolicy | None = None,
    ) -> list[AgentSelectedToolCall]:
        policy = safety_policy or AgentSafetyPolicy()

        safe_tool_calls: list[AgentSelectedToolCall] = []

        for tool_call in executable_tool_calls:
            if tool_call.tool_name in policy.blocked_tools:
                continue

            if (
                not policy.allow_llm_tools
                and tool_call.metadata.get("requires_llm") is True
            ):
                continue

            safe_tool_calls.append(tool_call)

        return safe_tool_calls[: policy.max_executable_tool_calls]
