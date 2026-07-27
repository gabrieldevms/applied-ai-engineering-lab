from collections.abc import Sequence
from ai_api.agents.schemas import (
    AgentEvaluationMetric,
    AgentEvaluationResponse,
    AgentExecutionLogEvent,
    AgentExecutionState,
    AgentRunResponse,
    AgentSafetyCheckResponse,
    AgentSelectedToolCall,
    AgentToolApprovalDecision,
)


class AgentEvaluationService:
    def evaluate_execution(
        self,
        objective: str,
        agent_run: AgentRunResponse,
        execution_state: AgentExecutionState | None = None,
        selected_tool_calls: Sequence[AgentSelectedToolCall] | None = None,
        approval_decisions: Sequence[AgentToolApprovalDecision] | None = None,
        safety_check: AgentSafetyCheckResponse | None = None,
        execution_logs: Sequence[AgentExecutionLogEvent] | None = None,
        metadata: dict | None = None,
    ) -> AgentEvaluationResponse:
        cleaned_objective = objective.strip()

        if not cleaned_objective:
            raise ValueError("objective cannot be blank")

        selected_tools = list(selected_tool_calls or [])
        approvals = list(approval_decisions or [])
        logs = list(execution_logs or [])

        metrics = [
            self._evaluate_traceability(
                agent_run=agent_run,
                execution_state=execution_state,
                execution_logs=logs,
            ),
            self._evaluate_completion(
                agent_run=agent_run,
            ),
            self._evaluate_safety(
                safety_check=safety_check,
            ),
            self._evaluate_approval_control(
                selected_tool_calls=selected_tools,
                approval_decisions=approvals,
            ),
            self._evaluate_objective_alignment(
                objective=cleaned_objective,
                agent_run=agent_run,
            ),
        ]

        overall_score = round(
            sum(metric.score for metric in metrics) / len(metrics),
            2,
        )

        status = self._build_evaluation_status(metrics)

        return AgentEvaluationResponse(
            status=status,
            overall_score=overall_score,
            metrics=metrics,
            metadata={
                **(metadata or {}),
                "evaluator": "agent-evaluation-service-v1",
                "metrics": len(metrics),
                "agent_run_id": agent_run.run_id,
                "agent_run_status": agent_run.status,
            },
        )

    def _evaluate_traceability(
        self,
        agent_run: AgentRunResponse,
        execution_state: AgentExecutionState | None,
        execution_logs: Sequence[AgentExecutionLogEvent],
    ) -> AgentEvaluationMetric:
        has_steps = len(agent_run.steps) > 0
        has_state = execution_state is not None
        has_logs = len(execution_logs) > 0

        score = sum([has_steps, has_state, has_logs]) / 3

        status = "passed" if score == 1 else "warning"

        return AgentEvaluationMetric(
            name="traceability",
            score=round(score, 2),
            status=status,
            message="Execution trace, state and logs were evaluated.",
            metadata={
                "has_steps": has_steps,
                "has_state": has_state,
                "has_logs": has_logs,
                "steps": len(agent_run.steps),
                "logs": len(execution_logs),
            },
        )

    def _evaluate_completion(
        self,
        agent_run: AgentRunResponse,
    ) -> AgentEvaluationMetric:
        if agent_run.status == "completed":
            return AgentEvaluationMetric(
                name="completion",
                score=1.0,
                status="passed",
                message="Agent run completed successfully.",
                metadata={
                    "agent_run_status": agent_run.status,
                },
            )

        return AgentEvaluationMetric(
            name="completion",
            score=0.0,
            status="failed",
            message="Agent run did not complete successfully.",
            metadata={
                "agent_run_status": agent_run.status,
            },
        )

    def _evaluate_safety(
        self,
        safety_check: AgentSafetyCheckResponse | None,
    ) -> AgentEvaluationMetric:
        if safety_check is None:
            return AgentEvaluationMetric(
                name="safety",
                score=0.5,
                status="warning",
                message="Safety check was not available.",
            )

        if safety_check.status == "passed":
            return AgentEvaluationMetric(
                name="safety",
                score=1.0,
                status="passed",
                message="Safety check passed.",
                metadata={
                    "safety_status": safety_check.status,
                    "violations": len(safety_check.violations),
                },
            )

        return AgentEvaluationMetric(
            name="safety",
            score=0.5,
            status="warning",
            message="Safety check reported violations.",
            metadata={
                "safety_status": safety_check.status,
                "violations": len(safety_check.violations),
            },
        )

    def _evaluate_approval_control(
        self,
        selected_tool_calls: Sequence[AgentSelectedToolCall],
        approval_decisions: Sequence[AgentToolApprovalDecision],
    ) -> AgentEvaluationMetric:
        if not selected_tool_calls:
            return AgentEvaluationMetric(
                name="approval_control",
                score=1.0,
                status="passed",
                message="No selected tools required approval decisions.",
                metadata={
                    "selected_tool_calls": 0,
                    "approval_decisions": len(approval_decisions),
                },
            )

        if len(approval_decisions) >= len(selected_tool_calls):
            return AgentEvaluationMetric(
                name="approval_control",
                score=1.0,
                status="passed",
                message="Approval decisions cover all selected tool calls.",
                metadata={
                    "selected_tool_calls": len(selected_tool_calls),
                    "approval_decisions": len(approval_decisions),
                },
            )

        return AgentEvaluationMetric(
            name="approval_control",
            score=0.5,
            status="warning",
            message="Approval decisions do not cover all selected tool calls.",
            metadata={
                "selected_tool_calls": len(selected_tool_calls),
                "approval_decisions": len(approval_decisions),
            },
        )

    def _evaluate_objective_alignment(
        self,
        objective: str,
        agent_run: AgentRunResponse,
    ) -> AgentEvaluationMetric:
        normalized_objective = objective.lower()
        normalized_run_objective = agent_run.objective.lower()

        is_aligned = normalized_objective == normalized_run_objective

        if is_aligned:
            return AgentEvaluationMetric(
                name="objective_alignment",
                score=1.0,
                status="passed",
                message="Agent run objective matches the requested objective.",
            )

        return AgentEvaluationMetric(
            name="objective_alignment",
            score=0.5,
            status="warning",
            message="Agent run objective differs from the requested objective.",
            metadata={
                "requested_objective": objective,
                "agent_run_objective": agent_run.objective,
            },
        )

    def _build_evaluation_status(
        self,
        metrics: Sequence[AgentEvaluationMetric],
    ) -> str:
        if any(metric.status == "failed" for metric in metrics):
            return "failed"

        if any(metric.status == "warning" for metric in metrics):
            return "warning"

        return "passed"
