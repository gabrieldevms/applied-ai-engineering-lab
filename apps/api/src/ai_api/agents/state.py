from collections.abc import Sequence
from typing import Protocol
from ai_api.agents.schemas import (
    AgentExecutionState,
    AgentRunResponse,
    AgentStep,
)


class AgentStateStore(Protocol):
    def save(self, state: AgentExecutionState) -> None:
        """Save an agent execution state snapshot."""
        ...

    def get(self, run_id: str) -> AgentExecutionState | None:
        """Get an agent execution state snapshot by run ID."""
        ...

    def list_states(self) -> list[AgentExecutionState]:
        """List stored execution states."""
        ...

    def count(self) -> int:
        """Return the number of stored states."""
        ...


class InMemoryAgentStateStore:
    def __init__(self) -> None:
        self._states: dict[str, AgentExecutionState] = {}

    def save(self, state: AgentExecutionState) -> None:
        self._states[state.run_id] = state

    def get(self, run_id: str) -> AgentExecutionState | None:
        cleaned_run_id = run_id.strip()

        if not cleaned_run_id:
            raise ValueError("run_id cannot be blank")

        return self._states.get(cleaned_run_id)

    def list_states(self) -> list[AgentExecutionState]:
        return list(self._states.values())

    def count(self) -> int:
        return len(self._states)

    def clear(self) -> None:
        self._states.clear()


class AgentStateService:
    def __init__(
        self,
        state_store: AgentStateStore | None = None,
    ) -> None:
        self.state_store = state_store or InMemoryAgentStateStore()

    def record_run_state(
        self,
        agent_run: AgentRunResponse,
        metadata: dict | None = None,
    ) -> AgentExecutionState:
        state = AgentExecutionState(
            state_id=f"agent-state-{agent_run.run_id}",
            run_id=agent_run.run_id,
            objective=agent_run.objective,
            status=agent_run.status,
            current_step=self._get_current_step(agent_run.steps),
            total_steps=len(agent_run.steps),
            completed_steps=self._count_steps_by_status(
                steps=agent_run.steps,
                status="completed",
            ),
            failed_steps=self._count_steps_by_status(
                steps=agent_run.steps,
                status="failed",
            ),
            skipped_steps=self._count_steps_by_status(
                steps=agent_run.steps,
                status="skipped",
            ),
            tool_calls=self._count_tool_calls(agent_run.steps),
            metadata={
                **(metadata or {}),
                "state_store": "in-memory-agent-state-store-v1",
            },
        )

        self.state_store.save(state)

        return state

    def get_state(self, run_id: str) -> AgentExecutionState | None:
        return self.state_store.get(run_id)

    def list_states(self) -> list[AgentExecutionState]:
        return self.state_store.list_states()

    def _get_current_step(
        self,
        steps: Sequence[AgentStep],
    ) -> str | None:
        if not steps:
            return None

        return steps[-1].name

    def _count_steps_by_status(
        self,
        steps: Sequence[AgentStep],
        status: str,
    ) -> int:
        return sum(
            1
            for step in steps
            if step.status == status
        )

    def _count_tool_calls(
        self,
        steps: Sequence[AgentStep],
    ) -> int:
        return sum(
            1
            for step in steps
            if step.name.startswith("tool_call:")
        )
