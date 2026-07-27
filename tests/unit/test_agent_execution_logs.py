from ai_api.agents import (
    AgentExecutionLogService,
    AgentExecutionState,
    AgentRunResponse,
    AgentStep,
    FileAgentExecutionLogStore,
    InMemoryAgentExecutionLogStore,
    AgentEvaluationResponse,
    AgentEvaluationMetric,
)


def test_agent_execution_log_service_should_record_event() -> None:
    store = InMemoryAgentExecutionLogStore()
    service = AgentExecutionLogService(log_store=store)

    event = service.record_event(
        run_id="agent-run-123",
        event_type="runtime_completed",
        message="Runtime completed.",
        metadata={
            "source": "test",
        },
    )

    assert event.log_id.startswith("agent-log-")
    assert event.run_id == "agent-run-123"
    assert event.event_type == "runtime_completed"
    assert event.level == "info"
    assert event.metadata["source"] == "test"
    assert store.count() == 1


def test_file_agent_execution_log_store_should_persist_events(tmp_path) -> None:
    file_path = tmp_path / "agent-execution-logs.jsonl"

    store = FileAgentExecutionLogStore(file_path=file_path)
    service = AgentExecutionLogService(log_store=store)

    service.record_event(
        run_id="agent-run-123",
        event_type="runtime_completed",
        message="Runtime completed.",
    )

    new_store = FileAgentExecutionLogStore(file_path=file_path)

    events = new_store.list_events()

    assert len(events) == 1
    assert events[0].run_id == "agent-run-123"
    assert events[0].event_type == "runtime_completed"


def test_agent_execution_log_service_should_list_events_by_run_id() -> None:
    store = InMemoryAgentExecutionLogStore()
    service = AgentExecutionLogService(log_store=store)

    service.record_event(
        run_id="agent-run-1",
        event_type="runtime_completed",
        message="Run 1 completed.",
    )
    service.record_event(
        run_id="agent-run-2",
        event_type="runtime_completed",
        message="Run 2 completed.",
    )

    events = service.list_events_by_run_id("agent-run-1")

    assert len(events) == 1
    assert events[0].run_id == "agent-run-1"


def test_agent_execution_log_service_should_record_workflow_execution() -> None:
    store = InMemoryAgentExecutionLogStore()
    service = AgentExecutionLogService(log_store=store)

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
                step_id="step-final",
                name="produce_final_answer",
                status="completed",
            ),
        ],
    )

    execution_state = AgentExecutionState(
        state_id="agent-state-agent-run-123",
        run_id="agent-run-123",
        objective="Analisar requisito.",
        status="completed",
        current_step="produce_final_answer",
        total_steps=2,
        completed_steps=2,
        failed_steps=0,
        skipped_steps=0,
        tool_calls=0,
    )

    events = service.record_workflow_execution(
        plan_summary="Plano gerado.",
        selected_tool_calls=[],
        skipped_steps=[],
        approval_decisions=[],
        safety_check=None,
        evaluation=None,
        agent_run=agent_run,
        execution_state=execution_state,
        metadata={
            "source": "test",
        },
    )

    event_types = [
        event.event_type
        for event in events
    ]

    assert len(events) == 5
    assert "plan_generated" in event_types
    assert "tools_selected" in event_types
    assert "approval_evaluated" in event_types
    assert "runtime_completed" in event_types
    assert "state_recorded" in event_types
    assert store.count() == 5


def test_agent_execution_log_service_should_record_evaluation_event() -> None:
    store = InMemoryAgentExecutionLogStore()
    service = AgentExecutionLogService(log_store=store)

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
            )
        ],
    )

    execution_state = AgentExecutionState(
        state_id="agent-state-agent-run-123",
        run_id="agent-run-123",
        objective="Analisar requisito.",
        status="completed",
        current_step="understand_objective",
        total_steps=1,
        completed_steps=1,
        failed_steps=0,
        skipped_steps=0,
        tool_calls=0,
    )

    evaluation = AgentEvaluationResponse(
        status="passed",
        overall_score=1.0,
        metrics=[
            AgentEvaluationMetric(
                name="completion",
                score=1.0,
                status="passed",
                message="Completed.",
            )
        ],
    )

    events = service.record_workflow_execution(
        plan_summary="Plano gerado.",
        selected_tool_calls=[],
        skipped_steps=[],
        approval_decisions=[],
        safety_check=None,
        evaluation=evaluation,
        agent_run=agent_run,
        execution_state=execution_state,
        metadata={
            "source": "test",
        },
    )

    assert len(events) == 6
    assert any(
        event.event_type == "evaluation_completed"
        for event in events
    )
