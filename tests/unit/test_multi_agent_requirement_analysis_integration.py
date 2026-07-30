from typing import Any
from ai_api.llm import FakeLLMProvider
from ai_api.multi_agent import (
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotService,
    MultiAgentSharedState,
)
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.services import RequirementAnalyzerService


class FailingRequirementAnalyzerService:
    def analyze(
        self,
        requirement_text: str,
        language: str,
    ) -> Any:
        raise RuntimeError("Simulated requirement analysis failure.")


def _build_requirement_analyzer_service() -> RequirementAnalyzerService:
    return RequirementAnalyzerService(
        llm_provider=FakeLLMProvider(
            response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
        ),
        retry_config=RetryConfig(max_attempts=2),
    )


def _find_artifact_content(
    shared_state: MultiAgentSharedState,
    artifact_name: str,
) -> dict[str, Any]:
    for artifact in shared_state.artifacts:
        if artifact.name == artifact_name:
            return artifact.content

    return {}


def _find_artifact_metadata(
    shared_state: MultiAgentSharedState,
    artifact_name: str,
) -> dict[str, Any]:
    for artifact in shared_state.artifacts:
        if artifact.name == artifact_name:
            return artifact.metadata

    return {}


def test_multi_agent_copilot_should_use_requirement_analysis_service_when_available() -> None:
    service = MultiAgentQACopilotService(
        requirement_analyzer_service=_build_requirement_analyzer_service(),
    )

    request = MultiAgentQACopilotRequest(
        requirement_text=(
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        language="pt-BR",
    )

    response = service.run(request)

    requirement_analysis = _find_artifact_content(
        shared_state=response.shared_state,
        artifact_name="requirement_analysis",
    )
    requirement_analysis_metadata = _find_artifact_metadata(
        shared_state=response.shared_state,
        artifact_name="requirement_analysis",
    )

    assert response.status == "completed"
    assert requirement_analysis["summary"]
    assert isinstance(requirement_analysis["identified_rules"], list)
    assert isinstance(requirement_analysis["acceptance_criteria"], list)
    assert isinstance(requirement_analysis["risks"], list)
    assert isinstance(requirement_analysis["positive_test_scenarios"], list)
    assert isinstance(requirement_analysis["negative_test_scenarios"], list)
    assert isinstance(requirement_analysis["edge_cases"], list)
    assert isinstance(requirement_analysis["open_questions"], list)
    assert isinstance(requirement_analysis["automation_opportunities"], list)
    assert requirement_analysis_metadata["source"] == "requirement_analyzer_service"

    requirement_task = [
        task_result
        for task_result in response.task_results
        if task_result.agent_name == "requirement_analyst_agent"
    ][0]

    assert requirement_task.status == "completed"
    assert requirement_task.metadata["source"] == "requirement_analyzer_service"
    assert response.final_report.requirement_understanding


def test_multi_agent_copilot_should_keep_deterministic_requirement_analysis_without_service() -> None:
    service = MultiAgentQACopilotService()

    request = MultiAgentQACopilotRequest(
        requirement_text="Como usuário, quero consultar meus pagamentos.",
        language="pt-BR",
    )

    response = service.run(request)

    requirement_analysis = _find_artifact_content(
        shared_state=response.shared_state,
        artifact_name="requirement_analysis",
    )
    requirement_analysis_metadata = _find_artifact_metadata(
        shared_state=response.shared_state,
        artifact_name="requirement_analysis",
    )

    assert response.status == "completed"
    assert requirement_analysis["summary"].startswith("Requisito analisado:")
    assert requirement_analysis["identified_rules"]
    assert requirement_analysis_metadata["source"] == "deterministic_fallback"


def test_multi_agent_copilot_should_capture_requirement_analysis_service_failure() -> None:
    service = MultiAgentQACopilotService(
        requirement_analyzer_service=FailingRequirementAnalyzerService(),
    )

    request = MultiAgentQACopilotRequest(
        requirement_text="Como QA, preciso validar uma regra crítica.",
        language="pt-BR",
        failure_strategy="stop_on_failure",
    )

    response = service.run(request)

    status_by_agent = {
        task_result.agent_name: task_result.status
        for task_result in response.task_results
    }

    assert response.status == "partial"
    assert len(response.failures) == 1
    assert response.failures[0].agent_name == "requirement_analyst_agent"
    assert response.failures[0].error_type == "RuntimeError"
    assert response.failures[0].message == (
        "Simulated requirement analysis failure."
    )

    assert status_by_agent["orchestrator_agent"] == "completed"
    assert status_by_agent["requirement_analyst_agent"] == "failed"
    assert status_by_agent["functional_qa_agent"] == "skipped"
    assert status_by_agent["test_automation_agent"] == "skipped"
    assert status_by_agent["reviewer_agent"] == "skipped"
    assert status_by_agent["report_agent"] == "skipped"

    assert response.metadata["failure_count"] == 1
    assert response.metadata["failure_strategy"] == "stop_on_failure"
