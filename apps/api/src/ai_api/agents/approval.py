from ai_api.agents.schemas import (
    AgentApprovalPolicy,
    AgentSelectedToolCall,
    AgentToolApprovalDecision,
)


class AgentApprovalService:
    def evaluate_tool_calls(
        self,
        selected_tool_calls: list[AgentSelectedToolCall],
        approval_policy: AgentApprovalPolicy | None = None,
    ) -> list[AgentToolApprovalDecision]:
        policy = approval_policy or AgentApprovalPolicy()

        decisions: list[AgentToolApprovalDecision] = []

        for tool_call in selected_tool_calls:
            decisions.append(
                self._evaluate_tool_call(
                    tool_call=tool_call,
                    policy=policy,
                )
            )

        return decisions

    def filter_executable_tool_calls(
        self,
        selected_tool_calls: list[AgentSelectedToolCall],
        approval_decisions: list[AgentToolApprovalDecision],
    ) -> list[AgentSelectedToolCall]:
        approved_step_ids = {
            decision.source_step_id
            for decision in approval_decisions
            if decision.status in {"approved", "not_required"}
        }

        return [
            tool_call
            for tool_call in selected_tool_calls
            if tool_call.source_step_id in approved_step_ids
        ]

    def _evaluate_tool_call(
        self,
        tool_call: AgentSelectedToolCall,
        policy: AgentApprovalPolicy,
    ) -> AgentToolApprovalDecision:
        if tool_call.tool_name in policy.reject_tools:
            return AgentToolApprovalDecision(
                source_step_id=tool_call.source_step_id,
                tool_name=tool_call.tool_name,
                status="rejected",
                reason="Tool is explicitly rejected by approval policy.",
                arguments=tool_call.arguments,
                metadata={
                    **policy.metadata,
                    "approval_service": "agent-approval-service-v1",
                },
            )

        if tool_call.tool_name in policy.require_approval_for_tools:
            return AgentToolApprovalDecision(
                source_step_id=tool_call.source_step_id,
                tool_name=tool_call.tool_name,
                status="pending",
                reason="Tool requires human approval before execution.",
                arguments=tool_call.arguments,
                metadata={
                    **policy.metadata,
                    "approval_service": "agent-approval-service-v1",
                },
            )

        if policy.auto_approve_safe_tools:
            return AgentToolApprovalDecision(
                source_step_id=tool_call.source_step_id,
                tool_name=tool_call.tool_name,
                status="not_required",
                reason="Tool does not require approval under the current policy.",
                arguments=tool_call.arguments,
                metadata={
                    **policy.metadata,
                    "approval_service": "agent-approval-service-v1",
                },
            )

        return AgentToolApprovalDecision(
            source_step_id=tool_call.source_step_id,
            tool_name=tool_call.tool_name,
            status="pending",
            reason="Tool approval is required because auto approval is disabled.",
            arguments=tool_call.arguments,
            metadata={
                **policy.metadata,
                "approval_service": "agent-approval-service-v1",
            },
        )
