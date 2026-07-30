from ai_api.multi_agent.schemas import (
    MultiAgentCommunicationContract,
    MultiAgentContractCheckResult,
    MultiAgentContractValidationResponse,
    MultiAgentSharedState,
)


def build_default_multi_agent_communication_contracts() -> list[
    MultiAgentCommunicationContract
]:
    return [
        MultiAgentCommunicationContract(
            name="orchestrator_to_requirement_analyst",
            source_agent="orchestrator_agent",
            target_agent="requirement_analyst_agent",
            required_artifacts=[
                "workflow_plan",
            ],
            required_message=True,
            description=(
                "The orchestrator must create the workflow plan before "
                "requirement analysis continues."
            ),
        ),
        MultiAgentCommunicationContract(
            name="requirement_analyst_to_functional_qa",
            source_agent="requirement_analyst_agent",
            target_agent="functional_qa_agent",
            required_artifacts=[
                "requirement_analysis",
            ],
            required_message=True,
            description=(
                "The Requirement Analyst Agent must provide requirement analysis "
                "before functional QA planning."
            ),
        ),
        MultiAgentCommunicationContract(
            name="functional_qa_to_test_automation",
            source_agent="functional_qa_agent",
            target_agent="test_automation_agent",
            required_artifacts=[
                "functional_test_strategy",
            ],
            required_message=True,
            description=(
                "The Functional QA Agent must provide functional coverage before "
                "test automation planning."
            ),
        ),
        MultiAgentCommunicationContract(
            name="test_automation_to_reviewer",
            source_agent="test_automation_agent",
            target_agent="reviewer_agent",
            required_artifacts=[
                "test_automation_strategy",
            ],
            required_message=True,
            description=(
                "The Test Automation Agent must provide automation strategy before "
                "review."
            ),
        ),
        MultiAgentCommunicationContract(
            name="reviewer_to_report",
            source_agent="reviewer_agent",
            target_agent="report_agent",
            required_artifacts=[
                "review_findings",
            ],
            required_message=True,
            description=(
                "The Reviewer Agent must provide review findings before final "
                "report generation."
            ),
        ),
        MultiAgentCommunicationContract(
            name="report_to_shared_state",
            source_agent="report_agent",
            target_agent="shared_state",
            required_artifacts=[
                "final_qa_report_draft",
            ],
            required_message=True,
            description=(
                "The Report Agent must publish a final QA report draft back to "
                "the shared state."
            ),
        ),
    ]


class MultiAgentCommunicationContractValidator:
    def __init__(
        self,
        contracts: list[MultiAgentCommunicationContract] | None = None,
    ) -> None:
        self.contracts = (
            contracts
            if contracts is not None
            else build_default_multi_agent_communication_contracts()
        )

    def validate(
        self,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentContractValidationResponse:
        checks = [
            self._validate_contract(
                contract=contract,
                shared_state=shared_state,
            )
            for contract in self.contracts
        ]

        passed_contracts = len(
            [
                check
                for check in checks
                if check.status == "passed"
            ]
        )
        warning_contracts = len(
            [
                check
                for check in checks
                if check.status == "warning"
            ]
        )
        failed_contracts = len(
            [
                check
                for check in checks
                if check.status == "failed"
            ]
        )

        if failed_contracts > 0:
            status = "failed"
        elif warning_contracts > 0:
            status = "warning"
        else:
            status = "passed"

        return MultiAgentContractValidationResponse(
            status=status,
            total_contracts=len(self.contracts),
            passed_contracts=passed_contracts,
            warning_contracts=warning_contracts,
            failed_contracts=failed_contracts,
            checks=checks,
            metadata={
                "validator": "multi-agent-communication-contract-validator-v1",
            },
        )

    def _validate_contract(
        self,
        contract: MultiAgentCommunicationContract,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentContractCheckResult:
        missing_artifacts = self._find_missing_artifacts(
            contract=contract,
            shared_state=shared_state,
        )
        message_found = self._has_required_message(
            contract=contract,
            shared_state=shared_state,
        )

        if missing_artifacts:
            status = "failed"
            summary = (
                "Contract failed because one or more required artifacts "
                "were not found."
            )
        elif contract.required_message and not message_found:
            status = "warning"
            summary = (
                "Contract produced required artifacts, but the expected "
                "communication message was not found."
            )
        else:
            status = "passed"
            summary = "Contract passed."

        return MultiAgentContractCheckResult(
            contract_name=contract.name,
            status=status,
            source_agent=contract.source_agent,
            target_agent=contract.target_agent,
            missing_artifacts=missing_artifacts,
            message_found=message_found,
            summary=summary,
            metadata={
                "required_artifacts": contract.required_artifacts,
                "required_message": contract.required_message,
            },
        )

    @staticmethod
    def _find_missing_artifacts(
        contract: MultiAgentCommunicationContract,
        shared_state: MultiAgentSharedState,
    ) -> list[str]:
        artifact_names = {
            artifact.name
            for artifact in shared_state.artifacts
            if artifact.produced_by == contract.source_agent
        }

        return [
            artifact_name
            for artifact_name in contract.required_artifacts
            if artifact_name not in artifact_names
        ]

    @staticmethod
    def _has_required_message(
        contract: MultiAgentCommunicationContract,
        shared_state: MultiAgentSharedState,
    ) -> bool:
        if not contract.required_message:
            return True

        return any(
            message.sender == contract.source_agent
            and message.recipient == contract.target_agent
            for message in shared_state.messages
        )
