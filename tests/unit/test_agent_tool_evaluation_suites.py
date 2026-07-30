import pytest
from pydantic import ValidationError
from ai_api.evals import (
    AgentRegressionCase,
    AgentRegressionEvaluationService,
    AgentRegressionExpectation,
    AgentRegressionRunRequest,
    AgentRegressionSuite,
    AgentRegressionSuiteService,
    ToolCallEvaluationRecord,
    ToolCallingEvaluationCase,
    ToolCallingEvaluationExpectation,
    ToolCallingEvaluationRunRequest,
    ToolCallingEvaluationService,
    ToolCallingEvaluationSuite,
    ToolCallingEvaluationSuiteService,
    build_default_agent_regression_suite,
    build_default_tool_calling_evaluation_suite,
)


def test_default_agent_regression_suite_should_include_expected_cases() -> None:
    suite = build_default_agent_regression_suite()

    case_ids = [
        regression_case.id
        for regression_case in suite.cases
    ]

    assert suite.name == "applied-ai-engineering-lab-agent-regression-suite"
    assert suite.version == "0.1.0"
    assert case_ids == [
        "AGENT-QA-001",
        "AGENT-DATA-001",
        "AGENT-MULTI-001",
    ]


def test_agent_regression_suite_service_should_return_default_suite() -> None:
    service = AgentRegressionSuiteService()

    suite = service.get_default_suite()

    assert suite.cases
    assert suite.metadata["suite_type"] == "agent_regression"
    assert suite.metadata["execution_mode"] == (
        "deterministic_output_validation"
    )


def test_agent_regression_evaluation_should_pass_default_suite() -> None:
    service = AgentRegressionEvaluationService()

    response = service.run(
        AgentRegressionRunRequest(
            suite=build_default_agent_regression_suite(),
        )
    )

    assert response.status == "passed"
    assert response.case_count == 3
    assert response.passed_count == 3
    assert response.failed_count == 0


def test_agent_regression_evaluation_should_filter_by_case_id() -> None:
    service = AgentRegressionEvaluationService()

    response = service.run(
        AgentRegressionRunRequest(
            suite=build_default_agent_regression_suite(),
            case_ids=[
                "AGENT-QA-001",
            ],
        )
    )

    assert response.status == "passed"
    assert response.case_count == 1
    assert response.results[0].case_id == "AGENT-QA-001"


def test_agent_regression_evaluation_should_fail_when_required_artifact_is_missing() -> None:
    service = AgentRegressionEvaluationService()

    suite = AgentRegressionSuite(
        name="custom-agent-suite",
        version="0.1.0",
        description="Custom suite with missing artifact.",
        cases=[
            AgentRegressionCase(
                id="AGENT-CUSTOM-001",
                name="Missing artifact",
                agent_name="qa-agent-v1",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output={
                    "status": "completed",
                    "trace": [],
                    "metadata": {},
                },
                expectations=AgentRegressionExpectation(
                    expected_status="completed",
                    required_artifacts=[
                        "requirement_analysis",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        AgentRegressionRunRequest(
            suite=suite,
        )
    )

    artifact_check = [
        check
        for check in response.results[0].checks
        if check.name == "required_artifacts"
    ][0]

    assert response.status == "failed"
    assert response.failed_count == 1
    assert artifact_check.status == "failed"
    assert artifact_check.metadata["missing_artifacts"] == [
        "requirement_analysis",
    ]


def test_agent_regression_evaluation_should_fail_when_forbidden_error_marker_is_detected() -> None:
    service = AgentRegressionEvaluationService()

    suite = AgentRegressionSuite(
        name="custom-agent-suite",
        version="0.1.0",
        description="Custom suite with forbidden marker.",
        cases=[
            AgentRegressionCase(
                id="AGENT-CUSTOM-002",
                name="Forbidden error marker",
                agent_name="multi-agent-qa-copilot-v1",
                input_payload={
                    "requirement_text": "Como QA, preciso validar um requisito.",
                },
                actual_output={
                    "status": "completed",
                    "error": "KeyError: database_schema",
                    "metadata": {},
                },
                expectations=AgentRegressionExpectation(
                    expected_status="completed",
                    forbidden_error_markers=[
                        "KeyError",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        AgentRegressionRunRequest(
            suite=suite,
        )
    )

    error_marker_check = [
        check
        for check in response.results[0].checks
        if check.name == "forbidden_error_markers"
    ][0]

    assert response.status == "failed"
    assert error_marker_check.status == "failed"
    assert error_marker_check.metadata["detected_markers"] == [
        "KeyError",
    ]


def test_default_tool_calling_evaluation_suite_should_include_expected_cases() -> None:
    suite = build_default_tool_calling_evaluation_suite()

    case_ids = [
        evaluation_case.id
        for evaluation_case in suite.cases
    ]

    assert suite.name == "applied-ai-engineering-lab-tool-calling-evaluation-suite"
    assert suite.version == "0.1.0"
    assert case_ids == [
        "TOOL-QA-001",
        "TOOL-MCP-001",
    ]


def test_tool_calling_evaluation_suite_service_should_return_default_suite() -> None:
    service = ToolCallingEvaluationSuiteService()

    suite = service.get_default_suite()

    assert suite.cases
    assert suite.metadata["suite_type"] == "tool_calling_evaluation"
    assert suite.metadata["execution_mode"] == (
        "deterministic_tool_call_validation"
    )


def test_tool_calling_evaluation_should_pass_default_suite() -> None:
    service = ToolCallingEvaluationService()

    response = service.run(
        ToolCallingEvaluationRunRequest(
            suite=build_default_tool_calling_evaluation_suite(),
        )
    )

    assert response.status == "passed"
    assert response.case_count == 2
    assert response.passed_count == 2
    assert response.failed_count == 0


def test_tool_calling_evaluation_should_filter_by_case_id() -> None:
    service = ToolCallingEvaluationService()

    response = service.run(
        ToolCallingEvaluationRunRequest(
            suite=build_default_tool_calling_evaluation_suite(),
            case_ids=[
                "TOOL-MCP-001",
            ],
        )
    )

    assert response.status == "passed"
    assert response.case_count == 1
    assert response.results[0].case_id == "TOOL-MCP-001"


def test_tool_calling_evaluation_should_fail_when_required_tool_is_missing() -> None:
    service = ToolCallingEvaluationService()

    suite = ToolCallingEvaluationSuite(
        name="custom-tool-suite",
        version="0.1.0",
        description="Custom tool-calling suite with missing tool.",
        cases=[
            ToolCallingEvaluationCase(
                id="TOOL-CUSTOM-001",
                name="Missing tool",
                workflow_name="custom_workflow",
                input_payload={
                    "objective": "Executar workflow QA.",
                },
                actual_tool_calls=[
                    ToolCallEvaluationRecord(
                        tool_name="requirements.analyze",
                        arguments={
                            "requirement_text": "Como QA, preciso validar.",
                        },
                    )
                ],
                actual_output={
                    "status": "completed",
                    "metadata": {},
                },
                expectations=ToolCallingEvaluationExpectation(
                    expected_status="completed",
                    required_tool_names=[
                        "requirements.analyze",
                        "rag.retrieve",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        ToolCallingEvaluationRunRequest(
            suite=suite,
        )
    )

    required_tool_check = [
        check
        for check in response.results[0].checks
        if check.name == "required_tool_names"
    ][0]

    assert response.status == "failed"
    assert required_tool_check.status == "failed"
    assert required_tool_check.metadata["missing_tools"] == [
        "rag.retrieve",
    ]


def test_tool_calling_evaluation_should_fail_when_forbidden_tool_is_called() -> None:
    service = ToolCallingEvaluationService()

    suite = ToolCallingEvaluationSuite(
        name="custom-tool-suite",
        version="0.1.0",
        description="Custom tool-calling suite with forbidden tool.",
        cases=[
            ToolCallingEvaluationCase(
                id="TOOL-CUSTOM-002",
                name="Forbidden tool",
                workflow_name="custom_workflow",
                input_payload={
                    "objective": "Executar workflow QA.",
                },
                actual_tool_calls=[
                    ToolCallEvaluationRecord(
                        tool_name="database.write",
                        arguments={
                            "table": "transactions",
                        },
                    )
                ],
                actual_output={
                    "status": "completed",
                    "metadata": {},
                },
                expectations=ToolCallingEvaluationExpectation(
                    expected_status="completed",
                    forbidden_tool_names=[
                        "database.write",
                    ],
                ),
            )
        ],
    )

    response = service.run(
        ToolCallingEvaluationRunRequest(
            suite=suite,
        )
    )

    forbidden_tool_check = [
        check
        for check in response.results[0].checks
        if check.name == "forbidden_tool_names"
    ][0]

    assert response.status == "failed"
    assert forbidden_tool_check.status == "failed"
    assert forbidden_tool_check.metadata["detected_tools"] == [
        "database.write",
    ]


def test_agent_regression_case_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        AgentRegressionCase(
            id="AGENT-INVALID-001",
            name="Invalid agent case",
            agent_name="qa-agent-v1",
            input_payload={},
            actual_output={
                "status": "completed",
            },
        )


def test_tool_calling_evaluation_case_should_reject_empty_input_payload() -> None:
    with pytest.raises(ValidationError):
        ToolCallingEvaluationCase(
            id="TOOL-INVALID-001",
            name="Invalid tool case",
            workflow_name="invalid_workflow",
            input_payload={},
            actual_tool_calls=[],
            actual_output={
                "status": "completed",
            },
        )
