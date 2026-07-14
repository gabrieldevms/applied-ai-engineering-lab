import pytest

from ai_api.agents import AgentRuntime


def test_agent_runtime_should_complete_run_without_context() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Analyze a requirement and identify risks.",
    )

    assert response.status == "completed"
    assert response.objective == "Analyze a requirement and identify risks."
    assert response.run_id.startswith("agent-run-")
    assert response.final_answer
    assert len(response.steps) == 3
    assert response.steps[0].name == "understand_objective"
    assert response.steps[1].status == "skipped"
    assert response.metadata["has_context"] is False


def test_agent_runtime_should_complete_run_with_context() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Summarize retrieved context.",
        context="Relevant context about billing requirements.",
    )

    assert response.status == "completed"
    assert len(response.steps) == 3
    assert response.steps[1].status == "completed"
    assert response.metadata["has_context"] is True


def test_agent_runtime_should_respect_max_steps() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Run a short agent execution.",
        max_steps=2,
    )

    assert len(response.steps) == 2
    assert response.steps[-1].name == "inspect_context"


def test_agent_runtime_should_reject_blank_objective() -> None:
    runtime = AgentRuntime()

    with pytest.raises(ValueError, match="objective cannot be blank"):
        runtime.run(objective="   ")


def test_agent_runtime_should_reject_invalid_max_steps() -> None:
    runtime = AgentRuntime()

    with pytest.raises(
        ValueError,
        match="max_steps must be greater than zero",
    ):
        runtime.run(
            objective="Valid objective.",
            max_steps=0,
        )
