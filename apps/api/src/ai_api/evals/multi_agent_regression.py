import json
from typing import Any
from ai_api.evals.schemas import (
    MultiAgentCopilotRegressionCase,
    MultiAgentCopilotRegressionCaseResult,
    MultiAgentCopilotRegressionCheck,
    MultiAgentCopilotRegressionExpectation,
    MultiAgentCopilotRegressionRunRequest,
    MultiAgentCopilotRegressionRunResponse,
    MultiAgentCopilotRegressionSuite,
)


DEFAULT_MULTI_AGENT_ROLE_NAMES = [
    "orchestrator_agent",
    "requirement_analyst_agent",
    "functional_qa_agent",
    "test_automation_agent",
    "reviewer_agent",
    "report_agent",
]


def build_default_multi_agent_copilot_regression_suite() -> (
    MultiAgentCopilotRegressionSuite
):
    return MultiAgentCopilotRegressionSuite(
        name="applied-ai-engineering-lab-multi-agent-copilot-regression-suite",
        version="0.1.0",
        description=(
            "Multi-Agent QA Copilot regression suite for deterministic validation "
            "of roles, artifacts, trace, contracts, conflicts, final report quality "
            "and data validation evidence."
        ),
        cases=[
            MultiAgentCopilotRegressionCase(
                id="MULTI-REG-001",
                name="Multi-Agent QA Copilot clean workflow",
                copilot_name="multi-agent-qa-copilot-v1",
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "objective": (
                        "Gerar análise multiagente de qualidade para o requisito."
                    ),
                    "language": "pt-BR",
                    "max_agents": 6,
                    "failure_strategy": "stop_on_failure",
                },
                actual_output={
                    "status": "completed",
                    "roles": [
                        {"name": "orchestrator_agent"},
                        {"name": "requirement_analyst_agent"},
                        {"name": "functional_qa_agent"},
                        {"name": "test_automation_agent"},
                        {"name": "reviewer_agent"},
                        {"name": "report_agent"},
                    ],
                    "shared_state": {
                        "artifacts": [
                            {"name": "workflow_plan"},
                            {"name": "requirement_analysis"},
                            {"name": "functional_test_strategy"},
                            {"name": "test_automation_strategy"},
                            {"name": "review_findings"},
                            {"name": "final_qa_report_draft"},
                        ]
                    },
                    "task_results": [
                        {"agent_name": "orchestrator_agent", "status": "completed"},
                        {"agent_name": "requirement_analyst_agent", "status": "completed"},
                        {"agent_name": "functional_qa_agent", "status": "completed"},
                        {"agent_name": "test_automation_agent", "status": "completed"},
                        {"agent_name": "reviewer_agent", "status": "completed"},
                        {"agent_name": "report_agent", "status": "completed"},
                    ],
                    "final_report": {
                        "summary": "Relatório final QA gerado com sucesso.",
                        "requirement_understanding": [
                            "O saldo final deve considerar depósitos e retiradas."
                        ],
                        "functional_coverage": [
                            "Validar cenários positivos, negativos e bordas."
                        ],
                        "automation_strategy": [
                            "Automatizar validação em camada de API."
                        ],
                        "data_validation_evidence": [],
                        "review_notes": [
                            "Revisar regras de arredondamento e tipos de transação."
                        ],
                        "next_steps": [
                            "Adicionar dataset de regressão para saldos por conta."
                        ],
                        "metadata": {
                            "quality_gate": "approved",
                            "contract_validation_status": "passed",
                            "conflict_analysis_status": "passed",
                        },
                    },
                    "trace": [
                        {"step_name": "orchestrator_agent", "status": "completed"},
                        {"step_name": "requirement_analyst_agent", "status": "completed"},
                        {"step_name": "functional_qa_agent", "status": "completed"},
                        {"step_name": "test_automation_agent", "status": "completed"},
                        {"step_name": "reviewer_agent", "status": "completed"},
                        {"step_name": "report_agent", "status": "completed"},
                    ],
                    "contract_validation": {
                        "status": "passed",
                    },
                    "conflict_analysis": {
                        "status": "passed",
                    },
                    "failures": [],
                    "metadata": {
                        "contract_validation_status": "passed",
                        "conflict_analysis_status": "passed",
                    },
                },
                expectations=MultiAgentCopilotRegressionExpectation(
                    expected_status="completed",
                    expected_quality_gate="approved",
                    expected_contract_status="passed",
                    expected_conflict_status="passed",
                    required_roles=DEFAULT_MULTI_AGENT_ROLE_NAMES,
                    required_artifacts=[
                        "workflow_plan",
                        "requirement_analysis",
                        "functional_test_strategy",
                        "test_automation_strategy",
                        "review_findings",
                        "final_qa_report_draft",
                    ],
                    required_final_report_sections=[
                        "summary",
                        "requirement_understanding",
                        "functional_coverage",
                        "automation_strategy",
                        "review_notes",
                        "next_steps",
                    ],
                    required_metadata_keys=[
                        "contract_validation_status",
                        "conflict_analysis_status",
                    ],
                    min_trace_steps=6,
                    min_task_results=6,
                    forbidden_error_markers=[
                        "Traceback",
                        "KeyError",
                        "Unhandled",
                    ],
                ),
                tags=[
                    "multi-agent",
                    "qa-copilot",
                    "regression",
                    "clean-workflow",
                ],
                metadata={
                    "source": "m7_multi_agent_copilot_regression_suite",
                },
            ),
            MultiAgentCopilotRegressionCase(
                id="MULTI-REG-002",
                name="Multi-Agent QA Copilot with data validation evidence",
                copilot_name="multi-agent-qa-copilot-v1",
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "objective": (
                        "Gerar análise multiagente com evidência de dados."
                    ),
                    "language": "pt-BR",
                    "max_agents": 6,
                    "failure_strategy": "stop_on_failure",
                    "data_validation": {
                        "objective": "Validar saldo final por conta.",
                    },
                },
                actual_output={
                    "status": "completed",
                    "roles": [
                        {"name": "orchestrator_agent"},
                        {"name": "requirement_analyst_agent"},
                        {"name": "functional_qa_agent"},
                        {"name": "test_automation_agent"},
                        {"name": "reviewer_agent"},
                        {"name": "report_agent"},
                    ],
                    "shared_state": {
                        "artifacts": [
                            {"name": "workflow_plan"},
                            {"name": "requirement_analysis"},
                            {"name": "functional_test_strategy"},
                            {"name": "data_validation_analysis"},
                            {"name": "test_automation_strategy"},
                            {"name": "review_findings"},
                            {"name": "final_qa_report_draft"},
                        ]
                    },
                    "task_results": [
                        {"agent_name": "orchestrator_agent", "status": "completed"},
                        {"agent_name": "requirement_analyst_agent", "status": "completed"},
                        {"agent_name": "functional_qa_agent", "status": "completed"},
                        {"agent_name": "test_automation_agent", "status": "completed"},
                        {"agent_name": "reviewer_agent", "status": "completed"},
                        {"agent_name": "report_agent", "status": "completed"},
                    ],
                    "final_report": {
                        "summary": "Relatório final QA com evidência de dados.",
                        "requirement_understanding": [
                            "O saldo final depende da soma de depósitos e retiradas."
                        ],
                        "functional_coverage": [
                            "Validar contas com múltiplas transações."
                        ],
                        "automation_strategy": [
                            "Automatizar cenários de API com massa controlada."
                        ],
                        "data_validation_evidence": [
                            "Data validation completed with controlled SQL evidence."
                        ],
                        "review_notes": [
                            "Evidência de dados foi incluída no relatório final."
                        ],
                        "next_steps": [
                            "Expandir massa para contas sem transações."
                        ],
                        "metadata": {
                            "quality_gate": "approved",
                            "contract_validation_status": "passed",
                            "conflict_analysis_status": "passed",
                            "data_validation_available": True,
                        },
                    },
                    "trace": [
                        {"step_name": "orchestrator_agent", "status": "completed"},
                        {"step_name": "requirement_analyst_agent", "status": "completed"},
                        {"step_name": "functional_qa_agent", "status": "completed"},
                        {"step_name": "test_automation_agent", "status": "completed"},
                        {"step_name": "reviewer_agent", "status": "completed"},
                        {"step_name": "report_agent", "status": "completed"},
                    ],
                    "contract_validation": {
                        "status": "passed",
                    },
                    "conflict_analysis": {
                        "status": "passed",
                    },
                    "failures": [],
                    "metadata": {
                        "contract_validation_status": "passed",
                        "conflict_analysis_status": "passed",
                        "data_validation_requested": True,
                        "data_validation_available": True,
                    },
                },
                expectations=MultiAgentCopilotRegressionExpectation(
                    expected_status="completed",
                    expected_quality_gate="approved",
                    expected_contract_status="passed",
                    expected_conflict_status="passed",
                    required_roles=DEFAULT_MULTI_AGENT_ROLE_NAMES,
                    required_artifacts=[
                        "workflow_plan",
                        "requirement_analysis",
                        "functional_test_strategy",
                        "data_validation_analysis",
                        "test_automation_strategy",
                        "review_findings",
                        "final_qa_report_draft",
                    ],
                    required_final_report_sections=[
                        "summary",
                        "requirement_understanding",
                        "functional_coverage",
                        "automation_strategy",
                        "data_validation_evidence",
                        "review_notes",
                        "next_steps",
                    ],
                    required_metadata_keys=[
                        "contract_validation_status",
                        "conflict_analysis_status",
                        "data_validation_requested",
                        "data_validation_available",
                    ],
                    min_trace_steps=6,
                    min_task_results=6,
                    require_data_validation_evidence=True,
                    forbidden_error_markers=[
                        "Traceback",
                        "KeyError",
                        "Unhandled",
                    ],
                ),
                tags=[
                    "multi-agent",
                    "qa-copilot",
                    "regression",
                    "data-validation",
                ],
                metadata={
                    "source": "m7_multi_agent_copilot_regression_suite",
                },
            ),
        ],
        metadata={
            "source": "m7_multi_agent_copilot_regression_suite",
            "suite_type": "multi_agent_copilot_regression",
            "execution_mode": "deterministic_output_validation",
        },
    )


class MultiAgentCopilotRegressionSuiteService:
    def get_default_suite(self) -> MultiAgentCopilotRegressionSuite:
        return build_default_multi_agent_copilot_regression_suite()


class MultiAgentCopilotRegressionEvaluationService:
    def run(
        self,
        request: MultiAgentCopilotRegressionRunRequest,
    ) -> MultiAgentCopilotRegressionRunResponse:
        suite = request.suite or build_default_multi_agent_copilot_regression_suite()
        selected_cases = self._select_cases(
            cases=suite.cases,
            case_ids=request.case_ids,
        )

        results = [
            self._run_case(regression_case)
            for regression_case in selected_cases
        ]

        passed_count = self._count_results(results, "passed")
        warning_count = self._count_results(results, "warning")
        failed_count = self._count_results(results, "failed")

        if failed_count > 0:
            status = "failed"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "passed"

        return MultiAgentCopilotRegressionRunResponse(
            status=status,
            suite_name=suite.name,
            suite_version=suite.version,
            case_count=len(selected_cases),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            results=results,
            metadata={
                "runner": "multi-agent-copilot-regression-evaluator-v1",
                "selected_case_ids": [
                    regression_case.id
                    for regression_case in selected_cases
                ],
                **request.metadata,
            },
        )

    def _run_case(
        self,
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCaseResult:
        checks = [
            self._check_expected_status(regression_case),
            self._check_quality_gate(regression_case),
            self._check_contract_status(regression_case),
            self._check_conflict_status(regression_case),
            self._check_required_roles(regression_case),
            self._check_required_artifacts(regression_case),
            self._check_final_report_sections(regression_case),
            self._check_min_trace_steps(regression_case),
            self._check_min_task_results(regression_case),
            self._check_required_metadata_keys(regression_case),
            self._check_data_validation_evidence(regression_case),
            self._check_forbidden_error_markers(regression_case),
        ]

        status = self._resolve_status(checks)

        return MultiAgentCopilotRegressionCaseResult(
            case_id=regression_case.id,
            case_name=regression_case.name,
            copilot_name=regression_case.copilot_name,
            status=status,
            checks=checks,
            metadata={
                "tags": regression_case.tags,
            },
        )

    @staticmethod
    def _check_expected_status(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        expected_status = regression_case.expectations.expected_status

        if expected_status is None:
            return MultiAgentCopilotRegressionCheck(
                name="expected_status",
                status="passed",
                summary="No expected status was configured.",
            )

        actual_status = regression_case.actual_output.get("status")

        if actual_status == expected_status:
            return MultiAgentCopilotRegressionCheck(
                name="expected_status",
                status="passed",
                summary="Copilot output status matched the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="expected_status",
            status="failed",
            summary="Copilot output status did not match the expected status.",
            metadata={
                "expected_status": expected_status,
                "actual_status": actual_status,
            },
        )

    @staticmethod
    def _check_quality_gate(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        expected_quality_gate = regression_case.expectations.expected_quality_gate

        if expected_quality_gate is None:
            return MultiAgentCopilotRegressionCheck(
                name="quality_gate",
                status="passed",
                summary="No expected quality gate was configured.",
            )

        final_report = regression_case.actual_output.get("final_report", {})
        final_report_metadata = final_report.get("metadata", {})
        actual_quality_gate = final_report_metadata.get("quality_gate")

        if actual_quality_gate == expected_quality_gate:
            return MultiAgentCopilotRegressionCheck(
                name="quality_gate",
                status="passed",
                summary="Quality gate matched the expected value.",
                metadata={
                    "expected_quality_gate": expected_quality_gate,
                    "actual_quality_gate": actual_quality_gate,
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="quality_gate",
            status="failed",
            summary="Quality gate did not match the expected value.",
            metadata={
                "expected_quality_gate": expected_quality_gate,
                "actual_quality_gate": actual_quality_gate,
            },
        )

    @staticmethod
    def _check_contract_status(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        expected_contract_status = regression_case.expectations.expected_contract_status

        if expected_contract_status is None:
            return MultiAgentCopilotRegressionCheck(
                name="contract_status",
                status="passed",
                summary="No expected contract status was configured.",
            )

        contract_validation = regression_case.actual_output.get(
            "contract_validation",
            {},
        )
        actual_contract_status = contract_validation.get("status")

        if actual_contract_status == expected_contract_status:
            return MultiAgentCopilotRegressionCheck(
                name="contract_status",
                status="passed",
                summary="Contract validation status matched the expected value.",
                metadata={
                    "expected_contract_status": expected_contract_status,
                    "actual_contract_status": actual_contract_status,
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="contract_status",
            status="failed",
            summary="Contract validation status did not match the expected value.",
            metadata={
                "expected_contract_status": expected_contract_status,
                "actual_contract_status": actual_contract_status,
            },
        )

    @staticmethod
    def _check_conflict_status(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        expected_conflict_status = regression_case.expectations.expected_conflict_status

        if expected_conflict_status is None:
            return MultiAgentCopilotRegressionCheck(
                name="conflict_status",
                status="passed",
                summary="No expected conflict status was configured.",
            )

        conflict_analysis = regression_case.actual_output.get(
            "conflict_analysis",
            {},
        )
        actual_conflict_status = conflict_analysis.get("status")

        if actual_conflict_status == expected_conflict_status:
            return MultiAgentCopilotRegressionCheck(
                name="conflict_status",
                status="passed",
                summary="Conflict analysis status matched the expected value.",
                metadata={
                    "expected_conflict_status": expected_conflict_status,
                    "actual_conflict_status": actual_conflict_status,
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="conflict_status",
            status="failed",
            summary="Conflict analysis status did not match the expected value.",
            metadata={
                "expected_conflict_status": expected_conflict_status,
                "actual_conflict_status": actual_conflict_status,
            },
        )

    @staticmethod
    def _check_required_roles(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        required_roles = regression_case.expectations.required_roles
        available_roles = MultiAgentCopilotRegressionEvaluationService._extract_role_names(
            regression_case.actual_output
        )

        missing_roles = [
            role
            for role in required_roles
            if role not in available_roles
        ]

        if not missing_roles:
            return MultiAgentCopilotRegressionCheck(
                name="required_roles",
                status="passed",
                summary="All required multi-agent roles were found.",
                metadata={
                    "required_roles": required_roles,
                    "available_roles": available_roles,
                    "missing_roles": [],
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="required_roles",
            status="failed",
            summary="One or more required multi-agent roles were missing.",
            metadata={
                "required_roles": required_roles,
                "available_roles": available_roles,
                "missing_roles": missing_roles,
            },
        )

    @staticmethod
    def _check_required_artifacts(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        required_artifacts = regression_case.expectations.required_artifacts
        available_artifacts = (
            MultiAgentCopilotRegressionEvaluationService._extract_artifact_names(
                regression_case.actual_output
            )
        )

        missing_artifacts = [
            artifact
            for artifact in required_artifacts
            if artifact not in available_artifacts
        ]

        if not missing_artifacts:
            return MultiAgentCopilotRegressionCheck(
                name="required_artifacts",
                status="passed",
                summary="All required multi-agent artifacts were found.",
                metadata={
                    "required_artifacts": required_artifacts,
                    "available_artifacts": available_artifacts,
                    "missing_artifacts": [],
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="required_artifacts",
            status="failed",
            summary="One or more required multi-agent artifacts were missing.",
            metadata={
                "required_artifacts": required_artifacts,
                "available_artifacts": available_artifacts,
                "missing_artifacts": missing_artifacts,
            },
        )

    @staticmethod
    def _check_final_report_sections(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        required_sections = regression_case.expectations.required_final_report_sections
        final_report = regression_case.actual_output.get("final_report", {})

        missing_sections = [
            section
            for section in required_sections
            if section not in final_report
        ]

        if not missing_sections:
            return MultiAgentCopilotRegressionCheck(
                name="final_report_sections",
                status="passed",
                summary="All required final report sections were found.",
                metadata={
                    "required_final_report_sections": required_sections,
                    "missing_sections": [],
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="final_report_sections",
            status="failed",
            summary="One or more required final report sections were missing.",
            metadata={
                "required_final_report_sections": required_sections,
                "missing_sections": missing_sections,
            },
        )

    @staticmethod
    def _check_min_trace_steps(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        min_trace_steps = regression_case.expectations.min_trace_steps
        trace_steps = regression_case.actual_output.get("trace", [])

        if len(trace_steps) >= min_trace_steps:
            return MultiAgentCopilotRegressionCheck(
                name="min_trace_steps",
                status="passed",
                summary="Trace step count meets the configured minimum.",
                metadata={
                    "min_trace_steps": min_trace_steps,
                    "actual_trace_steps": len(trace_steps),
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="min_trace_steps",
            status="failed",
            summary="Trace step count is below the configured minimum.",
            metadata={
                "min_trace_steps": min_trace_steps,
                "actual_trace_steps": len(trace_steps),
            },
        )

    @staticmethod
    def _check_min_task_results(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        min_task_results = regression_case.expectations.min_task_results
        task_results = regression_case.actual_output.get("task_results", [])

        if len(task_results) >= min_task_results:
            return MultiAgentCopilotRegressionCheck(
                name="min_task_results",
                status="passed",
                summary="Task result count meets the configured minimum.",
                metadata={
                    "min_task_results": min_task_results,
                    "actual_task_results": len(task_results),
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="min_task_results",
            status="failed",
            summary="Task result count is below the configured minimum.",
            metadata={
                "min_task_results": min_task_results,
                "actual_task_results": len(task_results),
            },
        )

    @staticmethod
    def _check_required_metadata_keys(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        required_metadata_keys = regression_case.expectations.required_metadata_keys

        if not required_metadata_keys:
            return MultiAgentCopilotRegressionCheck(
                name="required_metadata_keys",
                status="passed",
                summary="No required metadata keys were configured.",
            )

        metadata = regression_case.actual_output.get("metadata", {})

        missing_keys = [
            key
            for key in required_metadata_keys
            if key not in metadata
        ]

        if not missing_keys:
            return MultiAgentCopilotRegressionCheck(
                name="required_metadata_keys",
                status="passed",
                summary="All required metadata keys were found.",
                metadata={
                    "required_metadata_keys": required_metadata_keys,
                    "missing_keys": [],
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="required_metadata_keys",
            status="failed",
            summary="One or more required metadata keys were missing.",
            metadata={
                "required_metadata_keys": required_metadata_keys,
                "missing_keys": missing_keys,
            },
        )

    @staticmethod
    def _check_data_validation_evidence(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        if not regression_case.expectations.require_data_validation_evidence:
            return MultiAgentCopilotRegressionCheck(
                name="data_validation_evidence",
                status="passed",
                summary="Data validation evidence was not required.",
            )

        final_report = regression_case.actual_output.get("final_report", {})
        data_validation_evidence = final_report.get("data_validation_evidence", [])

        available_artifacts = (
            MultiAgentCopilotRegressionEvaluationService._extract_artifact_names(
                regression_case.actual_output
            )
        )

        if data_validation_evidence and "data_validation_analysis" in available_artifacts:
            return MultiAgentCopilotRegressionCheck(
                name="data_validation_evidence",
                status="passed",
                summary="Data validation evidence was found in the final report and artifacts.",
                metadata={
                    "evidence_count": len(data_validation_evidence),
                    "artifact_found": True,
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="data_validation_evidence",
            status="failed",
            summary="Data validation evidence was required but missing or incomplete.",
            metadata={
                "evidence_count": len(data_validation_evidence),
                "artifact_found": "data_validation_analysis" in available_artifacts,
            },
        )

    @staticmethod
    def _check_forbidden_error_markers(
        regression_case: MultiAgentCopilotRegressionCase,
    ) -> MultiAgentCopilotRegressionCheck:
        forbidden_error_markers = regression_case.expectations.forbidden_error_markers
        output_text = json.dumps(
            regression_case.actual_output,
            ensure_ascii=False,
            sort_keys=True,
        )

        detected_markers = [
            marker
            for marker in forbidden_error_markers
            if marker in output_text
        ]

        if not detected_markers:
            return MultiAgentCopilotRegressionCheck(
                name="forbidden_error_markers",
                status="passed",
                summary="No forbidden error markers were detected.",
                metadata={
                    "forbidden_error_markers": forbidden_error_markers,
                    "detected_markers": [],
                },
            )

        return MultiAgentCopilotRegressionCheck(
            name="forbidden_error_markers",
            status="failed",
            summary="One or more forbidden error markers were detected.",
            metadata={
                "forbidden_error_markers": forbidden_error_markers,
                "detected_markers": detected_markers,
            },
        )

    @staticmethod
    def _extract_role_names(output: dict[str, Any]) -> list[str]:
        roles = output.get("roles", [])

        return sorted(
            [
                role.get("name")
                for role in roles
                if isinstance(role, dict) and role.get("name")
            ]
        )

    @staticmethod
    def _extract_artifact_names(output: dict[str, Any]) -> list[str]:
        artifact_names = set(output.keys())

        shared_state = output.get("shared_state", {})
        shared_state_artifacts = shared_state.get("artifacts", [])

        for artifact in shared_state_artifacts:
            if isinstance(artifact, dict) and artifact.get("name"):
                artifact_names.add(artifact["name"])

        if "final_report" in output:
            artifact_names.add("final_report")

        return sorted(artifact_names)

    @staticmethod
    def _select_cases(
        cases: list[MultiAgentCopilotRegressionCase],
        case_ids: list[str],
    ) -> list[MultiAgentCopilotRegressionCase]:
        if not case_ids:
            return cases

        case_id_set = set(case_ids)

        return [
            regression_case
            for regression_case in cases
            if regression_case.id in case_id_set
        ]

    @staticmethod
    def _resolve_status(
        checks: list[MultiAgentCopilotRegressionCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _count_results(
        results: list[MultiAgentCopilotRegressionCaseResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )
