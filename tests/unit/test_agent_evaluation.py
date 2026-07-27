from ai_api.agents import (
    AgentEvaluationService,
    AgentExecutionLogEvent,
    AgentExecutionState,
    AgentRunResponse,
    AgentSafetyCheckResponse,
    AgentStep,
)


def test_agent_evaluation_service_should_pass_completed_traceable_execution() -> None:
    service = AgentEvaluationService()

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

    safety_check = AgentSafetyCheckResponse(
        status="passed",
    )

    execution_logs = [
        AgentExecutionLogEvent(
            log_id="agent-log-123",
            run_id="agent-run-123",
            event_type="runtime_completed",
            level="info",
            message="Runtime completed.",
            created_at="2026-01-01T00:00:00+00:00",
        )
    ]

    response = service.evaluate_execution(
        objective="Analisar requisito.",
        agent_run=agent_run,
        execution_state=execution_state,
        safety_check=safety_check,
        execution_logs=execution_logs,
    )

    assert response.status == "passed"
    assert response.overall_score == 1.0
    assert len(response.metrics) == 5
    assert response.metadata["evaluator"] == "agent-evaluation-service-v1"


def test_agent_evaluation_service_should_fail_when_agent_run_failed() -> None:
    service = AgentEvaluationService()

    agent_run = AgentRunResponse(
        run_id="agent-run-failed",
        objective="Executar fluxo.",
        status="failed",
        final_answer="Execução falhou.",
        steps=[
            AgentStep(
                step_id="step-1",
                name="tool_call:requirements.analyze",
                status="failed",
            )
        ],
    )

    response = service.evaluate_execution(
        objective="Executar fluxo.",
        agent_run=agent_run,
    )

    assert response.status == "failed"
    assert any(
        metric.name == "completion" and metric.status == "failed"
        for metric in response.metrics
    )


def test_agent_evaluation_service_should_warn_when_safety_has_violations() -> None:
    service = AgentEvaluationService()

    agent_run = AgentRunResponse(
        run_id="agent-run-123",
        objective="Executar fluxo.",
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

    safety_check = AgentSafetyCheckResponse(
        status="blocked",
    )

    response = service.evaluate_execution(
        objective="Executar fluxo.",
        agent_run=agent_run,
        safety_check=safety_check,
    )

    assert response.status == "warning"
    assert any(
        metric.name == "safety" and metric.status == "warning"
        for metric in response.metrics
    )
