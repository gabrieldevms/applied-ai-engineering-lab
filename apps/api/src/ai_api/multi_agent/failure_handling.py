from ai_api.multi_agent.schemas import (
    MultiAgentFailureRecord,
    MultiAgentRoleName,
    MultiAgentTaskResult,
)


class MultiAgentFailureHandler:
    def build_failure_record(
        self,
        agent_name: MultiAgentRoleName,
        error: Exception,
    ) -> MultiAgentFailureRecord:
        error_message = str(error) or "Unknown execution error."

        return MultiAgentFailureRecord(
            agent_name=agent_name,
            error_type=error.__class__.__name__,
            message=error_message,
            severity="recoverable",
            metadata={
                "handler": "multi-agent-failure-handler-v1",
            },
        )

    def build_failed_task_result(
        self,
        failure: MultiAgentFailureRecord,
    ) -> MultiAgentTaskResult:
        return MultiAgentTaskResult(
            agent_name=failure.agent_name,
            status="failed",
            summary=(
                "Agent execution failed and was captured by the "
                "multi-agent failure handler."
            ),
            artifacts=[],
            messages=[],
            metadata={
                "failure": failure.model_dump(mode="json"),
            },
        )

    def build_skipped_task_result(
        self,
        agent_name: MultiAgentRoleName,
        blocked_by: MultiAgentRoleName,
    ) -> MultiAgentTaskResult:
        return MultiAgentTaskResult(
            agent_name=agent_name,
            status="skipped",
            summary=(
                "Agent execution skipped because a previous agent failed "
                "and the failure strategy is stop_on_failure."
            ),
            artifacts=[],
            messages=[],
            metadata={
                "skipped_reason": "previous_agent_failure",
                "blocked_by": blocked_by,
            },
        )
