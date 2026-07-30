import pytest
from pydantic import ValidationError

from ai_api.multi_agent import (
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotService,
    build_default_multi_agent_roles,
)


def test_build_default_multi_agent_roles_should_return_expected_roles() -> None:
    roles = build_default_multi_agent_roles()

    role_names = [
        role.name
        for role in roles
    ]

    assert role_names == [
        "orchestrator_agent",
        "requirement_analyst_agent",
        "functional_qa_agent",
        "test_automation_agent",
        "reviewer_agent",
        "report_agent",
    ]


def test_multi_agent_qa_copilot_should_execute_full_foundation_flow() -> None:
    service = MultiAgentQACopilotService()

    request = MultiAgentQACopilotRequest(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        objective=(
            "Gerar uma análise multiagente de qualidade para o requisito."
        ),
        language="pt-BR",
        context={
            "domain": "financial",
            "system": "billing",
        },
        metadata={
            "source": "unit-test",
        },
    )

    response = service.run(request)

    assert response.status == "completed"
    assert response.copilot_name == "multi-agent-qa-copilot-v1"
    assert response.objective == (
        "Gerar uma análise multiagente de qualidade para o requisito."
    )
    assert len(response.roles) == 6
    assert len(response.task_results) == 6
    assert len(response.trace) == 6

    artifact_names = [
        artifact.name
        for artifact in response.shared_state.artifacts
    ]

    assert "workflow_plan" in artifact_names
    assert "requirement_analysis" in artifact_names
    assert "functional_test_strategy" in artifact_names
    assert "test_automation_strategy" in artifact_names
    assert "review_findings" in artifact_names
    assert "final_qa_report_draft" in artifact_names

    assert response.final_report.summary
    assert response.final_report.requirement_understanding
    assert response.final_report.functional_coverage
    assert response.final_report.automation_strategy
    assert response.final_report.review_notes
    assert response.final_report.next_steps
    assert response.final_report.metadata["source"] == (
        "multi-agent-final-report-generator-v1"
    )
    assert response.final_report.metadata["quality_gate"] == "approved"
    assert response.final_report.metadata["contract_validation_status"] == "passed"
    assert response.final_report.metadata["conflict_analysis_status"] == "passed"

    assert response.metadata["execution_mode"] == "deterministic_foundation"
    assert response.metadata["agent_count"] == 6
    assert response.contract_validation is not None
    assert response.contract_validation.status == "passed"
    assert response.contract_validation.total_contracts == 6
    assert response.contract_validation.passed_contracts == 6
    assert response.metadata["contract_validation_status"] == "passed"


def test_multi_agent_qa_copilot_should_support_limited_agent_execution() -> None:
    service = MultiAgentQACopilotService()

    request = MultiAgentQACopilotRequest(
        requirement_text="Como cliente, quero gerar um boleto atualizado.",
        max_agents=3,
    )

    response = service.run(request)

    role_names = [
        role.name
        for role in response.roles
    ]

    assert response.status == "completed"
    assert role_names == [
        "orchestrator_agent",
        "requirement_analyst_agent",
        "functional_qa_agent",
    ]
    assert len(response.task_results) == 3
    assert len(response.trace) == 3
    assert response.metadata["agent_count"] == 3
    assert response.contract_validation is not None
    assert response.contract_validation.status == "failed"
    assert response.contract_validation.failed_contracts > 0
    assert response.final_report.metadata["quality_gate"] == "requires_review"


def test_multi_agent_qa_copilot_should_use_default_objective_when_not_provided() -> None:
    service = MultiAgentQACopilotService()

    request = MultiAgentQACopilotRequest(
        requirement_text="Como usuário, quero consultar meus pagamentos.",
    )

    response = service.run(request)

    assert response.objective == (
        "Orchestrate a multi-agent QA analysis for the provided requirement."
    )


def test_multi_agent_qa_copilot_request_should_reject_blank_requirement() -> None:
    with pytest.raises(ValidationError):
        MultiAgentQACopilotRequest(
            requirement_text="   ",
        )
