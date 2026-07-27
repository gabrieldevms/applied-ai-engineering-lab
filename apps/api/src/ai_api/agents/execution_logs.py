import hashlib
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from ai_api.agents.schemas import (
    AgentExecutionLogEvent,
    AgentExecutionLogLevel,
    AgentExecutionState,
    AgentRunResponse,
    AgentSelectedToolCall,
    AgentSkippedPlanStep,
    AgentToolApprovalDecision,
    AgentSafetyCheckResponse,
)


class AgentExecutionLogStore(Protocol):
    def append(self, event: AgentExecutionLogEvent) -> None:
        """Append an agent execution log event."""
        ...

    def list_events(self) -> list[AgentExecutionLogEvent]:
        """List all stored log events."""
        ...

    def list_events_by_run_id(
        self,
        run_id: str,
    ) -> list[AgentExecutionLogEvent]:
        """List stored log events for a run ID."""
        ...

    def count(self) -> int:
        """Return the number of stored log events."""
        ...


class InMemoryAgentExecutionLogStore:
    def __init__(self) -> None:
        self._events: list[AgentExecutionLogEvent] = []

    def append(self, event: AgentExecutionLogEvent) -> None:
        self._events.append(event)

    def list_events(self) -> list[AgentExecutionLogEvent]:
        return list(self._events)

    def list_events_by_run_id(
        self,
        run_id: str,
    ) -> list[AgentExecutionLogEvent]:
        cleaned_run_id = run_id.strip()

        if not cleaned_run_id:
            raise ValueError("run_id cannot be blank")

        return [
            event
            for event in self._events
            if event.run_id == cleaned_run_id
        ]

    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()


class FileAgentExecutionLogStore:
    def __init__(
        self,
        file_path: str | Path = ".data/agent-execution-logs.jsonl",
    ) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: AgentExecutionLogEvent) -> None:
        with self.file_path.open("a", encoding="utf-8") as file:
            file.write(event.model_dump_json())
            file.write("\n")

    def list_events(self) -> list[AgentExecutionLogEvent]:
        if not self.file_path.exists():
            return []

        events: list[AgentExecutionLogEvent] = []

        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                cleaned_line = line.strip()

                if not cleaned_line:
                    continue

                events.append(
                    AgentExecutionLogEvent.model_validate_json(
                        cleaned_line,
                    )
                )

        return events

    def list_events_by_run_id(
        self,
        run_id: str,
    ) -> list[AgentExecutionLogEvent]:
        cleaned_run_id = run_id.strip()

        if not cleaned_run_id:
            raise ValueError("run_id cannot be blank")

        return [
            event
            for event in self.list_events()
            if event.run_id == cleaned_run_id
        ]

    def count(self) -> int:
        return len(self.list_events())


class AgentExecutionLogService:
    def __init__(
        self,
        log_store: AgentExecutionLogStore | None = None,
    ) -> None:
        self.log_store = log_store or InMemoryAgentExecutionLogStore()

    def record_event(
        self,
        run_id: str,
        event_type: str,
        message: str,
        level: AgentExecutionLogLevel = "info",
        metadata: dict | None = None,
    ) -> AgentExecutionLogEvent:
        cleaned_run_id = run_id.strip()
        cleaned_event_type = event_type.strip()
        cleaned_message = message.strip()

        if not cleaned_run_id:
            raise ValueError("run_id cannot be blank")

        if not cleaned_event_type:
            raise ValueError("event_type cannot be blank")

        if not cleaned_message:
            raise ValueError("message cannot be blank")

        created_at = datetime.now(timezone.utc).isoformat()

        event = AgentExecutionLogEvent(
            log_id=self._build_log_id(
                run_id=cleaned_run_id,
                event_type=cleaned_event_type,
                created_at=created_at,
                message=cleaned_message,
            ),
            run_id=cleaned_run_id,
            event_type=cleaned_event_type,
            level=level,
            message=cleaned_message,
            created_at=created_at,
            metadata={
                **(metadata or {}),
                "logger": "agent-execution-log-service-v1",
            },
        )

        self.log_store.append(event)

        return event

    def record_workflow_execution(
        self,
        plan_summary: str,
        selected_tool_calls: Sequence[AgentSelectedToolCall],
        skipped_steps: Sequence[AgentSkippedPlanStep],
        approval_decisions: Sequence[AgentToolApprovalDecision],
        safety_check: AgentSafetyCheckResponse | None,
        agent_run: AgentRunResponse,
        execution_state: AgentExecutionState,
        metadata: dict | None = None,
    ) -> list[AgentExecutionLogEvent]:
        common_metadata = {
            **(metadata or {}),
            "selected_tool_calls": len(selected_tool_calls),
            "skipped_steps": len(skipped_steps),
            "approval_decisions": len(approval_decisions),
            "agent_status": agent_run.status,
            "state_id": execution_state.state_id,
        }

        events = [
            self.record_event(
                run_id=agent_run.run_id,
                event_type="plan_generated",
                message="Agent plan was generated.",
                metadata={
                    **common_metadata,
                    "plan_summary": plan_summary,
                },
            ),
            self.record_event(
                run_id=agent_run.run_id,
                event_type="tools_selected",
                message="Executable tools were selected from the agent plan.",
                metadata=common_metadata,
            ),
            self.record_event(
                run_id=agent_run.run_id,
                event_type="approval_evaluated",
                message="Approval decisions were evaluated for selected tools.",
                metadata={
                    **common_metadata,
                    "pending_approvals": self._count_approval_status(
                        approval_decisions,
                        "pending",
                    ),
                    "rejected_approvals": self._count_approval_status(
                        approval_decisions,
                        "rejected",
                    ),
                },
            ),
        ]

        if safety_check is not None:
            events.append(
                self.record_event(
                    run_id=agent_run.run_id,
                    event_type="safety_evaluated",
                    message="Safety limits were evaluated for executable tools.",
                    level=(
                        "warning"
                        if safety_check.status == "blocked"
                        else "info"
                    ),
                    metadata={
                        **common_metadata,
                        "safety_status": safety_check.status,
                        "safety_violations": len(safety_check.violations),
                    },
                )
            )

        events.extend(
            [
                self.record_event(
                    run_id=agent_run.run_id,
                    event_type=self._build_runtime_event_type(agent_run),
                    message="Agent runtime execution finished.",
                    level="error" if agent_run.status == "failed" else "info",
                    metadata={
                        **common_metadata,
                        "executed_steps": len(agent_run.steps),
                        "final_status": agent_run.status,
                    },
                ),
                self.record_event(
                    run_id=agent_run.run_id,
                    event_type="state_recorded",
                    message="Agent execution state snapshot was recorded.",
                    metadata={
                        **common_metadata,
                        "total_steps": execution_state.total_steps,
                        "tool_calls": execution_state.tool_calls,
                    },
                ),
            ]
        )

        return events

    def list_events(self) -> list[AgentExecutionLogEvent]:
        return self.log_store.list_events()

    def list_events_by_run_id(
        self,
        run_id: str,
    ) -> list[AgentExecutionLogEvent]:
        return self.log_store.list_events_by_run_id(run_id)

    def _build_runtime_event_type(
        self,
        agent_run: AgentRunResponse,
    ) -> str:
        if agent_run.status == "failed":
            return "runtime_failed"

        return "runtime_completed"

    def _count_approval_status(
        self,
        approval_decisions: Sequence[AgentToolApprovalDecision],
        status: str,
    ) -> int:
        return sum(
            1
            for decision in approval_decisions
            if decision.status == status
        )

    def _build_log_id(
        self,
        run_id: str,
        event_type: str,
        created_at: str,
        message: str,
    ) -> str:
        raw_value = f"{run_id}:{event_type}:{created_at}:{message}"
        digest = hashlib.sha256(
            raw_value.encode("utf-8"),
        ).hexdigest()[:12]

        return f"agent-log-{digest}"
