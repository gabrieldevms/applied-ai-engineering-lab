from typing import Any
from ai_api.multi_agent import (
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotService,
    MultiAgentSharedState,
)


class FailingFunctionalQAAgentService(MultiAgentQACopilotService):
    def _run_functional_qa_agent(
        self,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> Any:
        raise RuntimeError("Simulated functional QA failure.")


def test_multi_agent_copilot_should_stop_after_failure_when_strategy_is_stop_on_failure() -> None:
    service = FailingFunctionalQAAgentService()

    request = MultiAgentQACopilotRequest(
        requirement_text="Como QA, preciso validar uma regra crítica.",
        failure_strategy="stop_on_failure",
    )

    response = service.run(request)

    status_by_agent = {
        task_result.agent_name: task_result.status
        for task_result in response.task_results
    }

    assert response.status == "partial"
    assert len(response.failures) == 1
    assert response.failures[0].agent_name == "functional_qa_agent"
    assert response.failures[0].error_type == "RuntimeError"
    assert response.failures[0].message == "Simulated functional QA failure."

    assert status_by_agent["orchestrator_agent"] == "completed"
    assert status_by_agent["requirement_analyst_agent"] == "completed"
    assert status_by_agent["functional_qa_agent"] == "failed"
    assert status_by_agent["test_automation_agent"] == "skipped"
    assert status_by_agent["reviewer_agent"] == "skipped"
    assert status_by_agent["report_agent"] == "skipped"

    assert response.metadata["failure_count"] == 1
    assert response.metadata["failure_strategy"] == "stop_on_failure"
    assert response.final_report.next_steps[0] == (
        "Investigar falhas capturadas durante a execução multiagente."
    )


def test_multi_agent_copilot_should_continue_after_failure_when_strategy_is_continue_on_failure() -> None:
    service = FailingFunctionalQAAgentService()

    request = MultiAgentQACopilotRequest(
        requirement_text="Como QA, preciso validar uma regra crítica.",
        failure_strategy="continue_on_failure",
    )

    response = service.run(request)

    status_by_agent = {
        task_result.agent_name: task_result.status
        for task_result in response.task_results
    }

    assert response.status == "partial"
    assert len(response.failures) == 1
    assert response.failures[0].agent_name == "functional_qa_agent"

    assert status_by_agent["orchestrator_agent"] == "completed"
    assert status_by_agent["requirement_analyst_agent"] == "completed"
    assert status_by_agent["functional_qa_agent"] == "failed"
    assert status_by_agent["test_automation_agent"] == "completed"
    assert status_by_agent["reviewer_agent"] == "completed"
    assert status_by_agent["report_agent"] == "completed"

    assert response.contract_validation is not None
    assert response.contract_validation.status == "failed"
    assert response.metadata["failure_strategy"] == "continue_on_failure"
    assert response.metadata["failure_count"] == 1
