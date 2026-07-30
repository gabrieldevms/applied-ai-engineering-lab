import pytest
from pydantic import ValidationError
from ai_api.evals import (
    MultiAgentCopilotRegressionCase,
    MultiAgentCopilotRegressionEvaluationService,
    MultiAgentCopilotRegressionExpectation,
    MultiAgentCopilotRegressionRunRequest,
    MultiAgentCopilotRegressionSuite,
    MultiAgentCopilotRegressionSuiteService,
    build_default_multi_agent_copilot_regression_suite,
)


def test_default_multi_agent_copilot_regression_suite_should_include_expected_cases() -> None:
    suite = build_default_multi_agent_copilot_regression_suite()

    case_ids = [
        regression_case.id
        for regression_case in suite.cases
    ]

    assert suite.name == (
        "applied-ai-engineering-lab-multi-agent-copilot-regression-suite"
    )
    assert suite.version == "0.1.0"
    assert case_ids == [
        "MULTI-REG-001",
        "MULTI-REG-002",
    ]


def test_multi_agent_copilot_regression_suite_service_should_return_default_suite() -> None:
    service = MultiAgentCopilotRegressionSuiteService()

    suite = service.get_default_suite()

    assert suite.cases
    assert suite.metadata["suite_type"] == "multi_agent_copilot_regression"
    assert suite.metadata["execution_mode"] == "deterministic_output_validation"


def test_multi_agent_copilot_regression_should_pass_default_suite() -> None:
    service = MultiAgentCopilotRegressionEvaluationService()

    response = service.run(
        MultiAgentCopilotRegressionRunRequest(
            suite=build_default_multi_agent_copilot_regression_suite(),
        )
    )

    assert response.status == "passed"
    assert response.case_count == 2
    assert response.passed_count == 2
    assert response.failed_count == 0


def test_multi_agent_copilot_regression_should_filter_by_case_id() -> None:
    service = MultiAgentCopilotRegressionEvaluationService()

    response = service.run(
        MultiAgentCopilotRegressionRunRequest(
            suite=build_default_multi_agent_copilot_regression_suite(),
            case_ids=[
                "MULTI-REG-001",
            ],
        )
    )

    assert response.status == "passed"
    assert response.case_count == 1
    assert response.results[0].case_id == "MULTI-REG-001"


def test_multi_agent_copilot_regression_should_fail_when_required_role_is_missing() -> None:
    service = MultiAgentCopilotRegressionEvaluationService()

    suite = MultiAgentCopilotRegressionSuite(
        name="custom-multi-agent-suite",
        version="0.1.0",
        description="Custom suite with missing role.",
        cases=[
            MultiAgentCopilotRegressionCase(
                id="MULTI-CUSTOM-001",
                name="Missing role",
                copilot_name="multi-agent-qa-copilot-v1",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output={
                    "status": "completed",
                    "roles": [
                        {
                            "name": "orchestrator_agent",
                        }
                    ],
                    "shared_state": {
                        "artifacts": [],
                    },
                    "final_report": {
                        "metadata": {
                            "quality_gate": "approved",
                        }
                    },
                    "trace": [],
                    "task_results": [],
                    "contract_validation": {
                        "status": "passed",
                    },
                    "conflict_analysis": {
                        "status": "passed",
                    },
                    "metadata": {},
                },
                expectations=MultiAgentCopilotRegressionExpectation(
                    expected_status="completed",
                    required_roles=[
                        "orchestrator_agent",
                        "requirement_analyst_agent",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        MultiAgentCopilotRegressionRunRequest(
            suite=suite,
        )
    )

    role_check = [
        check
        for check in response.results[0].checks
        if check.name == "required_roles"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert role_check.status == "failed"
    assert role_check.metadata["missing_roles"] == [
        "requirement_analyst_agent",
    ]


def test_multi_agent_copilot_regression_should_fail_when_final_report_section_is_missing() -> None:
    service = MultiAgentCopilotRegressionEvaluationService()

    suite = MultiAgentCopilotRegressionSuite(
        name="custom-multi-agent-suite",
        version="0.1.0",
        description="Custom suite with missing final report section.",
        cases=[
            MultiAgentCopilotRegressionCase(
                id="MULTI-CUSTOM-002",
                name="Missing final report section",
                copilot_name="multi-agent-qa-copilot-v1",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output={
                    "status": "completed",
                    "roles": [],
                    "shared_state": {
                        "artifacts": [],
                    },
                    "final_report": {
                        "summary": "Final report.",
                        "metadata": {
                            "quality_gate": "approved",
                        },
                    },
                    "trace": [],
                    "task_results": [],
                    "contract_validation": {
                        "status": "passed",
                    },
                    "conflict_analysis": {
                        "status": "passed",
                    },
                    "metadata": {},
                },
                expectations=MultiAgentCopilotRegressionExpectation(
                    expected_status="completed",
                    required_final_report_sections=[
                        "summary",
                        "automation_strategy",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        MultiAgentCopilotRegressionRunRequest(
            suite=suite,
        )
    )

    final_report_check = [
        check
        for check in response.results[0].checks
        if check.name == "final_report_sections"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert final_report_check.status == "failed"
    assert final_report_check.metadata["missing_sections"] == [
        "automation_strategy",
    ]


def test_multi_agent_copilot_regression_should_fail_when_data_validation_evidence_is_missing() -> None:
    service = MultiAgentCopilotRegressionEvaluationService()

    suite = MultiAgentCopilotRegressionSuite(
        name="custom-multi-agent-suite",
        version="0.1.0",
        description="Custom suite with missing data validation evidence.",
        cases=[
            MultiAgentCopilotRegressionCase(
                id="MULTI-CUSTOM-003",
                name="Missing data validation evidence",
                copilot_name="multi-agent-qa-copilot-v1",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output={
                    "status": "completed",
                    "roles": [],
                    "shared_state": {
                        "artifacts": [
                            {
                                "name": "data_validation_analysis",
                            }
                        ],
                    },
                    "final_report": {
                        "summary": "Final report.",
                        "data_validation_evidence": [],
                        "metadata": {
                            "quality_gate": "approved",
                        },
                    },
                    "trace": [],
                    "task_results": [],
                    "contract_validation": {
                        "status": "passed",
                    },
                    "conflict_analysis": {
                        "status": "passed",
                    },
                    "metadata": {},
                },
                expectations=MultiAgentCopilotRegressionExpectation(
                    expected_status="completed",
                    require_data_validation_evidence=True,
                ),
            )
        ],
    )

    response = service.run(
        MultiAgentCopilotRegressionRunRequest(
            suite=suite,
        )
    )

    data_validation_check = [
        check
        for check in response.results[0].checks
        if check.name == "data_validation_evidence"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert data_validation_check.status == "failed"
    assert data_validation_check.metadata["evidence_count"] == 0
    assert data_validation_check.metadata["artifact_found"] is True


def test_multi_agent_copilot_regression_case_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        MultiAgentCopilotRegressionCase(
            id="MULTI-INVALID-001",
            name="Invalid case",
            copilot_name="multi-agent-qa-copilot-v1",
            input_payload={},
            actual_output={
                "status": "completed",
            },
        )
