import json
from typing import Any
from ai_api.evals.schemas import (
    AgentRegressionCase,
    AgentRegressionCaseResult,
    AgentRegressionCheck,
    AgentRegressionExpectation,
    AgentRegressionRunRequest,
    AgentRegressionRunResponse,
    AgentRegressionSuite,
    ToolCallEvaluationRecord,
    ToolCallingEvaluationCase,
    ToolCallingEvaluationCaseResult,
    ToolCallingEvaluationCheck,
    ToolCallingEvaluationExpectation,
    ToolCallingEvaluationRunRequest,
    ToolCallingEvaluationRunResponse,
    ToolCallingEvaluationSuite,
)


def build_default_agent_regression_suite() -> AgentRegressionSuite:
    return AgentRegressionSuite(
        name="applied-ai-engineering-lab-agent-regression-suite",
        version="0.1.0",
        description=(
            "Agent regression suite for deterministic validation of QA Agent, "
            "Data Analyst Agent and Multi-Agent QA Copilot outputs."
        ),
        cases=[
            AgentRegressionCase(
                id="AGENT-QA-001",
                name="QA Agent requirement analysis workflow",
                agent_name="qa-agent-v1",
                input_payload={
                    "requirement_text": (
                        "Como cliente, quero gerar um boleto atualizado após "
                        "renegociar minha dívida."
                    ),
                    "language": "pt-BR",
                    "max_steps": 6,
                },
                actual_output={
                    "status": "completed",
                    "agent_name": "qa-agent-v1",
                    "requirement_analysis": {
                        "summary": "Análise QA do requisito de boleto atualizado.",
                    },
                    "trace": [
                        {
                            "step_name": "requirement_analysis",
                            "status": "completed",
                        },
                        {
                            "step_name": "qa_review",
                            "status": "completed",
                        },
                    ],
                    "metadata": {
                        "source": "agent-regression-suite",
                    },
                },
                expectations=AgentRegressionExpectation(
                    expected_status="completed",
                    required_artifacts=[
                        "requirement_analysis",
                    ],
                    required_trace_steps=[
                        "requirement_analysis",
                    ],
                    required_metadata_keys=[
                        "source",
                    ],
                    forbidden_error_markers=[
                        "Traceback",
                        "Exception",
                    ],
                    min_trace_steps=1,
                ),
                tags=[
                    "agent",
                    "qa",
                    "requirements",
                ],
                metadata={
                    "source": "m7_agent_regression_suite",
                },
            ),
            AgentRegressionCase(
                id="AGENT-DATA-001",
                name="Data Analyst Agent SQL evidence workflow",
                agent_name="data-analyst-agent-v1",
                input_payload={
                    "objective": (
                        "Validar saldo final por conta considerando depósitos "
                        "e retiradas."
                    ),
                    "language": "pt-BR",
                    "database_schema": {
                        "name": "qa_database",
                        "tables": [
                            {
                                "name": "transactions",
                                "columns": [
                                    {
                                        "name": "account_id",
                                        "data_type": "integer",
                                    },
                                    {
                                        "name": "amount",
                                        "data_type": "decimal",
                                    },
                                    {
                                        "name": "transaction_type",
                                        "data_type": "varchar",
                                    },
                                ],
                            }
                        ],
                    },
                    "table_data": [
                        {
                            "table_name": "transactions",
                            "rows": [
                                {
                                    "account_id": 101,
                                    "amount": 10.0,
                                    "transaction_type": "Deposit",
                                }
                            ],
                        }
                    ],
                },
                actual_output={
                    "status": "completed",
                    "agent_name": "data-analyst-agent-v1",
                    "workflow": {
                        "status": "executed",
                        "generated_sql": "SELECT account_id FROM transactions",
                    },
                    "evidence": {
                        "row_count": 1,
                        "column_count": 1,
                    },
                    "trace": [
                        {
                            "step_name": "sql_generation",
                            "status": "completed",
                        },
                        {
                            "step_name": "sql_execution",
                            "status": "completed",
                        },
                    ],
                    "metadata": {
                        "source": "agent-regression-suite",
                    },
                },
                expectations=AgentRegressionExpectation(
                    expected_status="completed",
                    required_artifacts=[
                        "workflow",
                        "evidence",
                    ],
                    required_trace_steps=[
                        "sql_generation",
                        "sql_execution",
                    ],
                    required_metadata_keys=[
                        "source",
                    ],
                    forbidden_error_markers=[
                        "DROP",
                        "DELETE",
                        "UPDATE",
                        "Traceback",
                    ],
                    min_trace_steps=2,
                ),
                tags=[
                    "agent",
                    "data-analysis",
                    "sql",
                ],
                metadata={
                    "source": "m7_agent_regression_suite",
                },
            ),
            AgentRegressionCase(
                id="AGENT-MULTI-001",
                name="Multi-Agent QA Copilot full workflow",
                agent_name="multi-agent-qa-copilot-v1",
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "language": "pt-BR",
                    "max_agents": 6,
                },
                actual_output={
                    "status": "completed",
                    "copilot_name": "multi-agent-qa-copilot-v1",
                    "roles": [
                        {
                            "name": "orchestrator_agent",
                        },
                        {
                            "name": "requirement_analyst_agent",
                        },
                        {
                            "name": "functional_qa_agent",
                        },
                    ],
                    "shared_state": {
                        "artifacts": [
                            {
                                "name": "workflow_plan",
                            },
                            {
                                "name": "requirement_analysis",
                            },
                            {
                                "name": "functional_test_strategy",
                            },
                        ]
                    },
                    "final_report": {
                        "summary": "Relatório final QA gerado com sucesso.",
                        "metadata": {
                            "quality_gate": "approved",
                        },
                    },
                    "trace": [
                        {
                            "step_name": "orchestrator_agent",
                            "status": "completed",
                        },
                        {
                            "step_name": "requirement_analyst_agent",
                            "status": "completed",
                        },
                        {
                            "step_name": "functional_qa_agent",
                            "status": "completed",
                        },
                    ],
                    "metadata": {
                        "contract_validation_status": "passed",
                        "conflict_analysis_status": "passed",
                    },
                },
                expectations=AgentRegressionExpectation(
                    expected_status="completed",
                    required_artifacts=[
                        "workflow_plan",
                        "requirement_analysis",
                        "functional_test_strategy",
                        "final_report",
                    ],
                    required_trace_steps=[
                        "orchestrator_agent",
                        "requirement_analyst_agent",
                        "functional_qa_agent",
                    ],
                    required_metadata_keys=[
                        "contract_validation_status",
                        "conflict_analysis_status",
                    ],
                    forbidden_error_markers=[
                        "Traceback",
                        "KeyError",
                    ],
                    min_trace_steps=3,
                ),
                tags=[
                    "agent",
                    "multi-agent",
                    "qa-copilot",
                ],
                metadata={
                    "source": "m7_agent_regression_suite",
                },
            ),
        ],
        metadata={
            "source": "m7_agent_regression_suite",
            "suite_type": "agent_regression",
            "execution_mode": "deterministic_output_validation",
        },
    )


def build_default_tool_calling_evaluation_suite() -> ToolCallingEvaluationSuite:
    return ToolCallingEvaluationSuite(
        name="applied-ai-engineering-lab-tool-calling-evaluation-suite",
        version="0.1.0",
        description=(
            "Tool-calling evaluation suite for deterministic validation of "
            "tool selection, arguments, forbidden tools and metadata."
        ),
        cases=[
            ToolCallingEvaluationCase(
                id="TOOL-QA-001",
                name="QA workflow tool selection",
                workflow_name="qa_agent_tool_selection",
                input_payload={
                    "objective": (
                        "Analisar requisito, buscar contexto RAG e validar dados."
                    ),
                    "language": "pt-BR",
                },
                actual_tool_calls=[
                    ToolCallEvaluationRecord(
                        tool_name="requirements.analyze",
                        arguments={
                            "requirement_text": "Como QA, preciso validar saldo.",
                            "language": "pt-BR",
                        },
                        status="completed",
                    ),
                    ToolCallEvaluationRecord(
                        tool_name="rag.retrieve",
                        arguments={
                            "query": "regra de saldo",
                            "top_k": 3,
                        },
                        status="completed",
                    ),
                    ToolCallEvaluationRecord(
                        tool_name="data_analysis.agent.run",
                        arguments={
                            "objective": "Validar saldo final.",
                            "max_rows": 100,
                        },
                        status="completed",
                    ),
                ],
                actual_output={
                    "status": "completed",
                    "metadata": {
                        "tool_selection_strategy": "deterministic",
                    },
                },
                expectations=ToolCallingEvaluationExpectation(
                    expected_status="completed",
                    required_tool_names=[
                        "requirements.analyze",
                        "rag.retrieve",
                        "data_analysis.agent.run",
                    ],
                    forbidden_tool_names=[
                        "shell.execute",
                        "database.write",
                    ],
                    required_argument_keys=[
                        "requirement_text",
                        "language",
                        "query",
                        "objective",
                    ],
                    required_metadata_keys=[
                        "tool_selection_strategy",
                    ],
                    min_tool_calls=3,
                ),
                tags=[
                    "tool-calling",
                    "qa-agent",
                    "data-validation",
                ],
                metadata={
                    "source": "m7_tool_calling_evaluation_suite",
                },
            ),
            ToolCallingEvaluationCase(
                id="TOOL-MCP-001",
                name="MCP project status tool call",
                workflow_name="mcp_project_status_discovery",
                input_payload={
                    "tool_name": "get_project_status",
                    "arguments": {},
                },
                actual_tool_calls=[
                    ToolCallEvaluationRecord(
                        tool_name="get_project_status",
                        arguments={},
                        status="completed",
                        output={
                            "project": "applied-ai-engineering-lab",
                            "available_mcp_tools": [
                                "get_project_status",
                                "run_multi_agent_qa_copilot",
                            ],
                        },
                    )
                ],
                actual_output={
                    "status": "completed",
                    "metadata": {
                        "mcp_server": "applied-ai-engineering-lab",
                    },
                },
                expectations=ToolCallingEvaluationExpectation(
                    expected_status="completed",
                    required_tool_names=[
                        "get_project_status",
                    ],
                    forbidden_tool_names=[
                        "unknown_tool",
                    ],
                    required_metadata_keys=[
                        "mcp_server",
                    ],
                    min_tool_calls=1,
                ),
                tags=[
                    "tool-calling",
                    "mcp",
                    "discovery",
                ],
                metadata={
                    "source": "m7_tool_calling_evaluation_suite",
                },
            ),
        ],
        metadata={
            "source": "m7_tool_calling_evaluation_suite",
            "suite_type": "tool_calling_evaluation",
            "execution_mode": "deterministic_tool_call_validation",
        },
    )


class AgentRegressionSuiteService:
    def get_default_suite(self) -> AgentRegressionSuite:
        return build_default_agent_regression_suite()


class AgentRegressionEvaluationService:
    def run(
        self,
        request: AgentRegressionRunRequest,
    ) -> AgentRegressionRunResponse:
        suite = request.suite or build_default_agent_regression_suite()
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

        return AgentRegressionRunResponse(
            status=status,
            suite_name=suite.name,
            suite_version=suite.version,
            case_count=len(selected_cases),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            results=results,
            metadata={
                "runner": "agent-regression-evaluator-v1",
                "selected_case_ids": [
                    regression_case.id
                    for regression_case in selected_cases
                ],
                **request.metadata,
            },
        )

    def _run_case(
        self,
        regression_case: AgentRegressionCase,
    ) -> AgentRegressionCaseResult:
        checks = [
            self._check_expected_status(regression_case),
            self._check_required_artifacts(regression_case),
            self._check_required_trace_steps(regression_case),
            self._check_min_trace_steps(regression_case),
            self._check_required_metadata_keys(regression_case),
            self._check_forbidden_error_markers(regression_case),
        ]

        status = self._resolve_status(checks)

        return AgentRegressionCaseResult(
            case_id=regression_case.id,
            case_name=regression_case.name,
            agent_name=regression_case.agent_name,
            status=status,
            checks=checks,
            metadata={
                "tags": regression_case.tags,
            },
        )

    @staticmethod
    def _check_expected_status(
        regression_case: AgentRegressionCase,
    ) -> AgentRegressionCheck:
        expected_status = regression_case.expectations.expected_status

        if expected_status is None:
            return AgentRegressionCheck(
                name="expected_status",
                status="passed",
                summary="No expected status was configured.",
            )

        actual_status = regression_case.actual_output.get("status")

        if actual_status == expected_status:
            return AgentRegressionCheck(
                name="expected_status",
                status="passed",
                summary="Agent output status matched the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                },
            )

        return AgentRegressionCheck(
            name="expected_status",
            status="failed",
            summary="Agent output status did not match the expected status.",
            metadata={
                "expected_status": expected_status,
                "actual_status": actual_status,
            },
        )

    @staticmethod
    def _check_required_artifacts(
        regression_case: AgentRegressionCase,
    ) -> AgentRegressionCheck:
        required_artifacts = regression_case.expectations.required_artifacts
        available_artifacts = AgentRegressionEvaluationService._extract_artifact_names(
            regression_case.actual_output
        )

        missing_artifacts = [
            artifact
            for artifact in required_artifacts
            if artifact not in available_artifacts
        ]

        if not missing_artifacts:
            return AgentRegressionCheck(
                name="required_artifacts",
                status="passed",
                summary="All required artifacts were found.",
                metadata={
                    "required_artifacts": required_artifacts,
                    "available_artifacts": available_artifacts,
                    "missing_artifacts": [],
                },
            )

        return AgentRegressionCheck(
            name="required_artifacts",
            status="failed",
            summary="One or more required artifacts were missing.",
            metadata={
                "required_artifacts": required_artifacts,
                "available_artifacts": available_artifacts,
                "missing_artifacts": missing_artifacts,
            },
        )

    @staticmethod
    def _check_required_trace_steps(
        regression_case: AgentRegressionCase,
    ) -> AgentRegressionCheck:
        required_trace_steps = regression_case.expectations.required_trace_steps
        available_trace_steps = AgentRegressionEvaluationService._extract_trace_steps(
            regression_case.actual_output
        )

        missing_steps = [
            step
            for step in required_trace_steps
            if step not in available_trace_steps
        ]

        if not missing_steps:
            return AgentRegressionCheck(
                name="required_trace_steps",
                status="passed",
                summary="All required trace steps were found.",
                metadata={
                    "required_trace_steps": required_trace_steps,
                    "available_trace_steps": available_trace_steps,
                    "missing_steps": [],
                },
            )

        return AgentRegressionCheck(
            name="required_trace_steps",
            status="failed",
            summary="One or more required trace steps were missing.",
            metadata={
                "required_trace_steps": required_trace_steps,
                "available_trace_steps": available_trace_steps,
                "missing_steps": missing_steps,
            },
        )

    @staticmethod
    def _check_min_trace_steps(
        regression_case: AgentRegressionCase,
    ) -> AgentRegressionCheck:
        min_trace_steps = regression_case.expectations.min_trace_steps
        available_trace_steps = AgentRegressionEvaluationService._extract_trace_steps(
            regression_case.actual_output
        )

        if len(available_trace_steps) >= min_trace_steps:
            return AgentRegressionCheck(
                name="min_trace_steps",
                status="passed",
                summary="Trace step count meets the configured minimum.",
                metadata={
                    "min_trace_steps": min_trace_steps,
                    "actual_trace_steps": len(available_trace_steps),
                },
            )

        return AgentRegressionCheck(
            name="min_trace_steps",
            status="failed",
            summary="Trace step count is below the configured minimum.",
            metadata={
                "min_trace_steps": min_trace_steps,
                "actual_trace_steps": len(available_trace_steps),
            },
        )

    @staticmethod
    def _check_required_metadata_keys(
        regression_case: AgentRegressionCase,
    ) -> AgentRegressionCheck:
        required_metadata_keys = regression_case.expectations.required_metadata_keys

        if not required_metadata_keys:
            return AgentRegressionCheck(
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
            return AgentRegressionCheck(
                name="required_metadata_keys",
                status="passed",
                summary="All required metadata keys were found.",
                metadata={
                    "required_metadata_keys": required_metadata_keys,
                    "missing_keys": [],
                },
            )

        return AgentRegressionCheck(
            name="required_metadata_keys",
            status="failed",
            summary="One or more required metadata keys were missing.",
            metadata={
                "required_metadata_keys": required_metadata_keys,
                "missing_keys": missing_keys,
            },
        )

    @staticmethod
    def _check_forbidden_error_markers(
        regression_case: AgentRegressionCase,
    ) -> AgentRegressionCheck:
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
            return AgentRegressionCheck(
                name="forbidden_error_markers",
                status="passed",
                summary="No forbidden error markers were detected.",
                metadata={
                    "forbidden_error_markers": forbidden_error_markers,
                    "detected_markers": [],
                },
            )

        return AgentRegressionCheck(
            name="forbidden_error_markers",
            status="failed",
            summary="One or more forbidden error markers were detected.",
            metadata={
                "forbidden_error_markers": forbidden_error_markers,
                "detected_markers": detected_markers,
            },
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
    def _extract_trace_steps(output: dict[str, Any]) -> list[str]:
        trace = output.get("trace", [])

        return [
            step.get("step_name")
            for step in trace
            if isinstance(step, dict) and step.get("step_name")
        ]

    @staticmethod
    def _select_cases(
        cases: list[AgentRegressionCase],
        case_ids: list[str],
    ) -> list[AgentRegressionCase]:
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
        checks: list[AgentRegressionCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _count_results(
        results: list[AgentRegressionCaseResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )


class ToolCallingEvaluationSuiteService:
    def get_default_suite(self) -> ToolCallingEvaluationSuite:
        return build_default_tool_calling_evaluation_suite()


class ToolCallingEvaluationService:
    def run(
        self,
        request: ToolCallingEvaluationRunRequest,
    ) -> ToolCallingEvaluationRunResponse:
        suite = request.suite or build_default_tool_calling_evaluation_suite()
        selected_cases = self._select_cases(
            cases=suite.cases,
            case_ids=request.case_ids,
        )

        results = [
            self._run_case(evaluation_case)
            for evaluation_case in selected_cases
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

        return ToolCallingEvaluationRunResponse(
            status=status,
            suite_name=suite.name,
            suite_version=suite.version,
            case_count=len(selected_cases),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            results=results,
            metadata={
                "runner": "tool-calling-evaluator-v1",
                "selected_case_ids": [
                    evaluation_case.id
                    for evaluation_case in selected_cases
                ],
                **request.metadata,
            },
        )

    def _run_case(
        self,
        evaluation_case: ToolCallingEvaluationCase,
    ) -> ToolCallingEvaluationCaseResult:
        checks = [
            self._check_expected_status(evaluation_case),
            self._check_min_tool_calls(evaluation_case),
            self._check_required_tool_names(evaluation_case),
            self._check_forbidden_tool_names(evaluation_case),
            self._check_required_argument_keys(evaluation_case),
            self._check_required_metadata_keys(evaluation_case),
        ]

        status = self._resolve_status(checks)

        return ToolCallingEvaluationCaseResult(
            case_id=evaluation_case.id,
            case_name=evaluation_case.name,
            workflow_name=evaluation_case.workflow_name,
            status=status,
            checks=checks,
            metadata={
                "tags": evaluation_case.tags,
            },
        )

    @staticmethod
    def _check_expected_status(
        evaluation_case: ToolCallingEvaluationCase,
    ) -> ToolCallingEvaluationCheck:
        expected_status = evaluation_case.expectations.expected_status

        if expected_status is None:
            return ToolCallingEvaluationCheck(
                name="expected_status",
                status="passed",
                summary="No expected status was configured.",
            )

        actual_status = evaluation_case.actual_output.get("status")

        if actual_status == expected_status:
            return ToolCallingEvaluationCheck(
                name="expected_status",
                status="passed",
                summary="Tool-calling output status matched the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                },
            )

        return ToolCallingEvaluationCheck(
            name="expected_status",
            status="failed",
            summary="Tool-calling output status did not match the expected status.",
            metadata={
                "expected_status": expected_status,
                "actual_status": actual_status,
            },
        )

    @staticmethod
    def _check_min_tool_calls(
        evaluation_case: ToolCallingEvaluationCase,
    ) -> ToolCallingEvaluationCheck:
        min_tool_calls = evaluation_case.expectations.min_tool_calls
        actual_count = len(evaluation_case.actual_tool_calls)

        if actual_count >= min_tool_calls:
            return ToolCallingEvaluationCheck(
                name="min_tool_calls",
                status="passed",
                summary="Tool call count meets the configured minimum.",
                metadata={
                    "min_tool_calls": min_tool_calls,
                    "actual_tool_calls": actual_count,
                },
            )

        return ToolCallingEvaluationCheck(
            name="min_tool_calls",
            status="failed",
            summary="Tool call count is below the configured minimum.",
            metadata={
                "min_tool_calls": min_tool_calls,
                "actual_tool_calls": actual_count,
            },
        )

    @staticmethod
    def _check_required_tool_names(
        evaluation_case: ToolCallingEvaluationCase,
    ) -> ToolCallingEvaluationCheck:
        required_tool_names = evaluation_case.expectations.required_tool_names
        actual_tool_names = [
            tool_call.tool_name
            for tool_call in evaluation_case.actual_tool_calls
        ]

        missing_tools = [
            tool_name
            for tool_name in required_tool_names
            if tool_name not in actual_tool_names
        ]

        if not missing_tools:
            return ToolCallingEvaluationCheck(
                name="required_tool_names",
                status="passed",
                summary="All required tools were called.",
                metadata={
                    "required_tool_names": required_tool_names,
                    "actual_tool_names": actual_tool_names,
                    "missing_tools": [],
                },
            )

        return ToolCallingEvaluationCheck(
            name="required_tool_names",
            status="failed",
            summary="One or more required tools were not called.",
            metadata={
                "required_tool_names": required_tool_names,
                "actual_tool_names": actual_tool_names,
                "missing_tools": missing_tools,
            },
        )

    @staticmethod
    def _check_forbidden_tool_names(
        evaluation_case: ToolCallingEvaluationCase,
    ) -> ToolCallingEvaluationCheck:
        forbidden_tool_names = evaluation_case.expectations.forbidden_tool_names
        actual_tool_names = [
            tool_call.tool_name
            for tool_call in evaluation_case.actual_tool_calls
        ]

        detected_tools = [
            tool_name
            for tool_name in forbidden_tool_names
            if tool_name in actual_tool_names
        ]

        if not detected_tools:
            return ToolCallingEvaluationCheck(
                name="forbidden_tool_names",
                status="passed",
                summary="No forbidden tools were called.",
                metadata={
                    "forbidden_tool_names": forbidden_tool_names,
                    "detected_tools": [],
                },
            )

        return ToolCallingEvaluationCheck(
            name="forbidden_tool_names",
            status="failed",
            summary="One or more forbidden tools were called.",
            metadata={
                "forbidden_tool_names": forbidden_tool_names,
                "detected_tools": detected_tools,
            },
        )

    @staticmethod
    def _check_required_argument_keys(
        evaluation_case: ToolCallingEvaluationCase,
    ) -> ToolCallingEvaluationCheck:
        required_argument_keys = evaluation_case.expectations.required_argument_keys
        available_argument_keys: set[str] = set()

        for tool_call in evaluation_case.actual_tool_calls:
            available_argument_keys.update(tool_call.arguments.keys())

        missing_keys = [
            key
            for key in required_argument_keys
            if key not in available_argument_keys
        ]

        if not missing_keys:
            return ToolCallingEvaluationCheck(
                name="required_argument_keys",
                status="passed",
                summary="All required argument keys were found.",
                metadata={
                    "required_argument_keys": required_argument_keys,
                    "available_argument_keys": sorted(available_argument_keys),
                    "missing_keys": [],
                },
            )

        return ToolCallingEvaluationCheck(
            name="required_argument_keys",
            status="failed",
            summary="One or more required argument keys were missing.",
            metadata={
                "required_argument_keys": required_argument_keys,
                "available_argument_keys": sorted(available_argument_keys),
                "missing_keys": missing_keys,
            },
        )

    @staticmethod
    def _check_required_metadata_keys(
        evaluation_case: ToolCallingEvaluationCase,
    ) -> ToolCallingEvaluationCheck:
        required_metadata_keys = evaluation_case.expectations.required_metadata_keys

        if not required_metadata_keys:
            return ToolCallingEvaluationCheck(
                name="required_metadata_keys",
                status="passed",
                summary="No required metadata keys were configured.",
            )

        metadata = evaluation_case.actual_output.get("metadata", {})

        missing_keys = [
            key
            for key in required_metadata_keys
            if key not in metadata
        ]

        if not missing_keys:
            return ToolCallingEvaluationCheck(
                name="required_metadata_keys",
                status="passed",
                summary="All required metadata keys were found.",
                metadata={
                    "required_metadata_keys": required_metadata_keys,
                    "missing_keys": [],
                },
            )

        return ToolCallingEvaluationCheck(
            name="required_metadata_keys",
            status="failed",
            summary="One or more required metadata keys were missing.",
            metadata={
                "required_metadata_keys": required_metadata_keys,
                "missing_keys": missing_keys,
            },
        )

    @staticmethod
    def _select_cases(
        cases: list[ToolCallingEvaluationCase],
        case_ids: list[str],
    ) -> list[ToolCallingEvaluationCase]:
        if not case_ids:
            return cases

        case_id_set = set(case_ids)

        return [
            evaluation_case
            for evaluation_case in cases
            if evaluation_case.id in case_id_set
        ]

    @staticmethod
    def _resolve_status(
        checks: list[ToolCallingEvaluationCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _count_results(
        results: list[ToolCallingEvaluationCaseResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )
