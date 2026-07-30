from ai_api.multi_agent import (
    MultiAgentArtifact,
    MultiAgentCommunicationContractValidator,
    MultiAgentMessage,
    MultiAgentSharedState,
    build_default_multi_agent_communication_contracts,
)


def test_build_default_multi_agent_communication_contracts_should_return_expected_flow() -> None:
    contracts = build_default_multi_agent_communication_contracts()

    contract_names = [
        contract.name
        for contract in contracts
    ]

    assert contract_names == [
        "orchestrator_to_requirement_analyst",
        "requirement_analyst_to_functional_qa",
        "functional_qa_to_test_automation",
        "test_automation_to_reviewer",
        "reviewer_to_report",
        "report_to_shared_state",
    ]


def test_multi_agent_contract_validator_should_pass_valid_shared_state() -> None:
    validator = MultiAgentCommunicationContractValidator()

    shared_state = MultiAgentSharedState(
        objective="Validate QA workflow.",
        requirement_text="Como QA, preciso validar uma regra de negócio.",
        artifacts=[
            MultiAgentArtifact(
                name="workflow_plan",
                produced_by="orchestrator_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="requirement_analysis",
                produced_by="requirement_analyst_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="functional_test_strategy",
                produced_by="functional_qa_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="test_automation_strategy",
                produced_by="test_automation_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="review_findings",
                produced_by="reviewer_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="final_qa_report_draft",
                produced_by="report_agent",
                content={},
            ),
        ],
        messages=[
            MultiAgentMessage(
                sender="orchestrator_agent",
                recipient="requirement_analyst_agent",
                content="Workflow plan created.",
            ),
            MultiAgentMessage(
                sender="requirement_analyst_agent",
                recipient="functional_qa_agent",
                content="Requirement analysis completed.",
            ),
            MultiAgentMessage(
                sender="functional_qa_agent",
                recipient="test_automation_agent",
                content="Functional strategy completed.",
            ),
            MultiAgentMessage(
                sender="test_automation_agent",
                recipient="reviewer_agent",
                content="Automation strategy completed.",
            ),
            MultiAgentMessage(
                sender="reviewer_agent",
                recipient="report_agent",
                content="Review findings completed.",
            ),
            MultiAgentMessage(
                sender="report_agent",
                recipient="shared_state",
                content="Final report draft created.",
            ),
        ],
    )

    response = validator.validate(shared_state)

    assert response.status == "passed"
    assert response.total_contracts == 6
    assert response.passed_contracts == 6
    assert response.warning_contracts == 0
    assert response.failed_contracts == 0


def test_multi_agent_contract_validator_should_fail_when_required_artifact_is_missing() -> None:
    validator = MultiAgentCommunicationContractValidator()

    shared_state = MultiAgentSharedState(
        objective="Validate QA workflow.",
        requirement_text="Como QA, preciso validar uma regra de negócio.",
        artifacts=[],
        messages=[],
    )

    response = validator.validate(shared_state)

    assert response.status == "failed"
    assert response.failed_contracts == 6

    failed_contract_names = [
        check.contract_name
        for check in response.checks
        if check.status == "failed"
    ]

    assert "orchestrator_to_requirement_analyst" in failed_contract_names
    assert "report_to_shared_state" in failed_contract_names


def test_multi_agent_contract_validator_should_warn_when_message_is_missing() -> None:
    validator = MultiAgentCommunicationContractValidator()

    shared_state = MultiAgentSharedState(
        objective="Validate QA workflow.",
        requirement_text="Como QA, preciso validar uma regra de negócio.",
        artifacts=[
            MultiAgentArtifact(
                name="workflow_plan",
                produced_by="orchestrator_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="requirement_analysis",
                produced_by="requirement_analyst_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="functional_test_strategy",
                produced_by="functional_qa_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="test_automation_strategy",
                produced_by="test_automation_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="review_findings",
                produced_by="reviewer_agent",
                content={},
            ),
            MultiAgentArtifact(
                name="final_qa_report_draft",
                produced_by="report_agent",
                content={},
            ),
        ],
        messages=[],
    )

    response = validator.validate(shared_state)

    assert response.status == "warning"
    assert response.passed_contracts == 0
    assert response.warning_contracts == 6
    assert response.failed_contracts == 0
