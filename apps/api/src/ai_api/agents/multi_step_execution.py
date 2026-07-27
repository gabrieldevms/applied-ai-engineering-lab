from ai_api.agents.approval import AgentApprovalService
from ai_api.agents.execution_logs import AgentExecutionLogService
from ai_api.agents.runtime import AgentRuntime
from ai_api.agents.safety import AgentSafetyService
from ai_api.agents.schemas import (
    AgentApprovalPolicy,
    AgentMultiStepExecutionResponse,
    AgentToolApprovalDecision,
    AgentToolCall,
    ToolDefinition,
    AgentSafetyPolicy,
)
from ai_api.agents.state import AgentStateService
from ai_api.agents.tool_selection import AgentToolSelectionService


class AgentMultiStepExecutionService:
    def __init__(
        self,
        tool_selection_service: AgentToolSelectionService,
        agent_runtime: AgentRuntime | None = None,
        state_service: AgentStateService | None = None,
        approval_service: AgentApprovalService | None = None,
        safety_service: AgentSafetyService | None = None,
        log_service: AgentExecutionLogService | None = None,
    ) -> None:
        self.tool_selection_service = tool_selection_service
        self.agent_runtime = agent_runtime or AgentRuntime()
        self.state_service = state_service or AgentStateService()
        self.approval_service = approval_service or AgentApprovalService()
        self.safety_service = safety_service or AgentSafetyService()
        self.log_service = log_service or AgentExecutionLogService()

    def execute(
        self,
        objective: str,
        context: str | None = None,
        available_tools: list[ToolDefinition] | None = None,
        max_plan_steps: int = 5,
        max_execution_steps: int = 10,
        language: str = "pt-BR",
        metadata: dict | None = None,
        approval_policy: AgentApprovalPolicy | None = None,
        safety_policy: AgentSafetyPolicy | None = None,
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

        approval_decisions = self.approval_service.evaluate_tool_calls(
            selected_tool_calls=selection_response.selected_tool_calls,
            approval_policy=approval_policy,
        )

        executable_tool_calls = (
            self.approval_service.filter_executable_tool_calls(
                selected_tool_calls=selection_response.selected_tool_calls,
                approval_decisions=approval_decisions,
            )
        )

        safety_check = self.safety_service.evaluate_tool_calls(
            selected_tool_calls=selection_response.selected_tool_calls,
            executable_tool_calls=executable_tool_calls,
            approval_decisions=approval_decisions,
            safety_policy=safety_policy,
        )

        safe_executable_tool_calls = (
            self.safety_service.filter_safe_executable_tool_calls(
                executable_tool_calls=executable_tool_calls,
                safety_policy=safety_policy,
            )
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
                    "approval_status": self._get_approval_status(
                        source_step_id=selected_tool.source_step_id,
                        approval_decisions=approval_decisions,
                    ),
                },
            )
            for selected_tool in safe_executable_tool_calls
        ]

        agent_run = self.agent_runtime.run(
            objective=cleaned_objective,
            context=context,
            max_steps=max_execution_steps,
            metadata={
                **(metadata or {}),
                "execution": "agent-multi-step-execution-v1",
                "plan_summary": selection_response.plan_summary,
                "selected_tool_calls": len(
                    selection_response.selected_tool_calls
                ),
                "skipped_plan_steps": len(selection_response.skipped_steps),
                "planning_provider": selection_response.provider,
                "planning_model": selection_response.model,
                "approval_decisions": len(approval_decisions),
                "executable_tool_calls": len(tool_calls),
                "safety_status": safety_check.status,
                "safety_violations": len(safety_check.violations),
                "safe_executable_tool_calls": len(tool_calls),
            },
            tool_calls=tool_calls,
        )

        execution_state = self.state_service.record_run_state(
            agent_run=agent_run,
            metadata={
                "source": "multi_step_execution",
                "selected_tool_calls": len(
                    selection_response.selected_tool_calls
                ),
                "skipped_plan_steps": len(selection_response.skipped_steps),
                "approval_decisions": len(approval_decisions),
                "executable_tool_calls": len(tool_calls),
                "safety_status": safety_check.status,
                "safety_violations": len(safety_check.violations),
                "safe_executable_tool_calls": len(tool_calls),
            },
        )

        execution_logs = self.log_service.record_workflow_execution(
            plan_summary=selection_response.plan_summary,
            selected_tool_calls=selection_response.selected_tool_calls,
            skipped_steps=selection_response.skipped_steps,
            approval_decisions=approval_decisions,
            safety_check=safety_check,
            agent_run=agent_run,
            execution_state=execution_state,
            metadata={
                "source": "multi_step_execution",
                
            },
        )

        return AgentMultiStepExecutionResponse(
            objective=cleaned_objective,
            status=agent_run.status,
            plan_summary=selection_response.plan_summary,
            selected_tool_calls=selection_response.selected_tool_calls,
            skipped_steps=selection_response.skipped_steps,
            approval_decisions=approval_decisions,
            agent_run=agent_run,
            execution_state=execution_state,
            execution_logs=execution_logs,
            provider=selection_response.provider,
            model=selection_response.model,
            safety_check=safety_check,
            metadata={
                **selection_response.metadata,
                "executor": "agent-multi-step-execution-service-v1",
                "agent_run_id": agent_run.run_id,
                "agent_run_status": agent_run.status,
                "execution_logs": len(execution_logs),
                "safety_status": safety_check.status,
                "safety_violations": len(safety_check.violations),
            },
        )

    def _get_approval_status(
        self,
        source_step_id: str,
        approval_decisions: list[AgentToolApprovalDecision],
    ) -> str:
        for decision in approval_decisions:
            if decision.source_step_id == source_step_id:
                return decision.status

        return "unknown"
