import pytest

from ai_api.agents import (
    AgentRunResponse,
    AgentStateService,
    AgentStep,
    InMemoryAgentStateStore,
)


def test_agent_state_service_should_record_agent_run_state() -> None:
    store = InMemoryAgentStateStore()
    service = AgentStateService(state_store=store)

    agent_run = AgentRunResponse(
        run_id="agent-run-123",
        objective="Analisar requisito.",
        status="completed",
        final_answer="Execução concluída.",
        steps=[
            AgentStep(
                step_id="step-1",
                name="understand_objective",
                status="completed",
            ),
            AgentStep(
                step_id="step-tool-1",
                name="tool_call:requirements.analyze",
                status="completed",
            ),
            AgentStep(
                step_id="step-final",
                name="produce_final_answer",
                status="completed",
            ),
        ],
    )

    state = service.record_run_state(
        agent_run=agent_run,
        metadata={
            "source": "test",
        },
    )

    assert state.run_id == "agent-run-123"
    assert state.status == "completed"
    assert state.current_step == "produce_final_answer"
    assert state.total_steps == 3
    assert state.completed_steps == 3
    assert state.failed_steps == 0
    assert state.skipped_steps == 0
    assert state.tool_calls == 1
    assert state.metadata["source"] == "test"
    assert store.count() == 1
    assert service.get_state("agent-run-123") == state


def test_agent_state_service_should_record_failed_agent_run_state() -> None:
    service = AgentStateService()

    agent_run = AgentRunResponse(
        run_id="agent-run-failed",
        objective="Executar ferramenta inválida.",
        status="failed",
        final_answer="Execução falhou.",
        steps=[
            AgentStep(
                step_id="step-1",
                name="understand_objective",
                status="completed",
            ),
            AgentStep(
                step_id="step-tool-1",
                name="tool_call:unknown.tool",
                status="failed",
            ),
            AgentStep(
                step_id="step-final",
                name="produce_final_answer",
                status="skipped",
            ),
        ],
    )

    state = service.record_run_state(agent_run=agent_run)

    assert state.status == "failed"
    assert state.current_step == "produce_final_answer"
    assert state.total_steps == 3
    assert state.completed_steps == 1
    assert state.failed_steps == 1
    assert state.skipped_steps == 1
    assert state.tool_calls == 1


def test_in_memory_agent_state_store_should_reject_blank_run_id() -> None:
    store = InMemoryAgentStateStore()

    with pytest.raises(ValueError, match="run_id cannot be blank"):
        store.get("   ")
