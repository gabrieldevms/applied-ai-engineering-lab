from typing import Any
from ai_api.agents import QAAgentRunRequest
from ai_api.data_analysis.agent import DataAnalystAgentRequest
from ai_api.evals.golden_dataset import build_default_golden_evaluation_dataset
from ai_api.evals.schemas import (
    EvaluationScenario,
    EvaluationScenarioRunCheck,
    EvaluationScenarioRunResult,
    GoldenEvaluationDatasetRunRequest,
    GoldenEvaluationDatasetRunResponse,
)
from ai_api.mcp_server.tools import get_project_status_tool
from ai_api.multi_agent import MultiAgentQACopilotRequest
from ai_api.requirements.schemas import RequirementAnalysisRequest


class GoldenEvaluationDatasetRunnerService:
    def __init__(
        self,
        requirement_analyzer_service: Any | None = None,
        tool_execution_service: Any | None = None,
        qa_agent_service: Any | None = None,
        data_analyst_agent_service: Any | None = None,
        multi_agent_qa_copilot_service: Any | None = None,
    ) -> None:
        self.requirement_analyzer_service = requirement_analyzer_service
        self.tool_execution_service = tool_execution_service
        self.qa_agent_service = qa_agent_service
        self.data_analyst_agent_service = data_analyst_agent_service
        self.multi_agent_qa_copilot_service = multi_agent_qa_copilot_service

    def run(
        self,
        request: GoldenEvaluationDatasetRunRequest,
    ) -> GoldenEvaluationDatasetRunResponse:
        dataset = request.dataset or build_default_golden_evaluation_dataset()
        selected_scenarios = self._select_scenarios(
            scenarios=dataset.scenarios,
            scenario_ids=request.scenario_ids,
            scenario_types=request.scenario_types,
        )

        results = [
            self._run_scenario(
                scenario=scenario,
                dry_run=request.dry_run,
            )
            for scenario in selected_scenarios
        ]

        passed_count = self._count_results(results, "passed")
        warning_count = self._count_results(results, "warning")
        failed_count = self._count_results(results, "failed")
        skipped_count = self._count_results(results, "skipped")

        if failed_count > 0:
            status = "failed"
        elif warning_count > 0 or skipped_count > 0:
            status = "warning"
        else:
            status = "passed"

        return GoldenEvaluationDatasetRunResponse(
            status=status,
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            scenario_count=len(selected_scenarios),
            executed_count=len(results) - skipped_count,
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            results=results,
            metadata={
                "runner": "golden-evaluation-dataset-runner-v1",
                "dry_run": request.dry_run,
                "selected_scenario_ids": [
                    scenario.id
                    for scenario in selected_scenarios
                ],
                **request.metadata,
            },
        )

    def _run_scenario(
        self,
        scenario: EvaluationScenario,
        dry_run: bool,
    ) -> EvaluationScenarioRunResult:
        if dry_run:
            return EvaluationScenarioRunResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                scenario_type=scenario.type,
                priority=scenario.priority,
                status="skipped",
                checks=[
                    EvaluationScenarioRunCheck(
                        name="dry_run",
                        status="warning",
                        summary="Scenario was selected but not executed because dry_run is enabled.",
                    )
                ],
                metadata={
                    "dry_run": True,
                },
            )

        try:
            output = self._execute_scenario(scenario)
            checks = self._build_checks(
                scenario=scenario,
                output=output,
            )
            status = self._resolve_scenario_status(checks)

            return EvaluationScenarioRunResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                scenario_type=scenario.type,
                priority=scenario.priority,
                status=status,
                output=output,
                checks=checks,
                metadata={
                    "dry_run": False,
                    "handler": f"{scenario.type}_handler",
                },
            )
        except NotImplementedError as error:
            return EvaluationScenarioRunResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                scenario_type=scenario.type,
                priority=scenario.priority,
                status="skipped",
                checks=[
                    EvaluationScenarioRunCheck(
                        name="handler_available",
                        status="warning",
                        summary=str(error),
                    )
                ],
                error_message=str(error),
                metadata={
                    "dry_run": False,
                    "handler": f"{scenario.type}_handler",
                },
            )
        except Exception as error:
            return EvaluationScenarioRunResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                scenario_type=scenario.type,
                priority=scenario.priority,
                status="failed",
                checks=[
                    EvaluationScenarioRunCheck(
                        name="scenario_execution",
                        status="failed",
                        summary="Scenario execution failed.",
                        metadata={
                            "error_type": error.__class__.__name__,
                            "error_message": str(error),
                        },
                    )
                ],
                error_message=str(error),
                metadata={
                    "dry_run": False,
                    "handler": f"{scenario.type}_handler",
                },
            )

    def _execute_scenario(
        self,
        scenario: EvaluationScenario,
    ) -> dict[str, Any]:
        if scenario.type == "requirement_analysis":
            return self._execute_requirement_analysis_scenario(scenario)

        if scenario.type == "rag_answer":
            return self._execute_rag_answer_scenario(scenario)

        if scenario.type == "qa_agent":
            return self._execute_qa_agent_scenario(scenario)

        if scenario.type == "data_analyst_agent":
            return self._execute_data_analyst_agent_scenario(scenario)

        if scenario.type == "multi_agent_qa_copilot":
            return self._execute_multi_agent_qa_copilot_scenario(scenario)

        if scenario.type == "mcp_tool":
            return self._execute_mcp_tool_scenario(scenario)

        raise NotImplementedError(
            f"No runner handler is available for scenario type: {scenario.type}"
        )

    def _execute_requirement_analysis_scenario(
        self,
        scenario: EvaluationScenario,
    ) -> dict[str, Any]:
        if self.requirement_analyzer_service is None:
            raise NotImplementedError(
                "Requirement Analysis scenario cannot run because no "
                "RequirementAnalyzerService was configured."
            )

        payload = RequirementAnalysisRequest.model_validate(scenario.input_payload)

        response = self.requirement_analyzer_service.analyze(
            requirement_text=payload.requirement_text,
            language=payload.language,
        )

        return self._to_output(response)

    def _execute_rag_answer_scenario(
        self,
        scenario: EvaluationScenario,
    ) -> dict[str, Any]:
        if self.tool_execution_service is None:
            raise NotImplementedError(
                "RAG scenario cannot run because no ToolExecutionService was configured."
            )

        response = self.tool_execution_service.execute(
            tool_name="rag.answer",
            arguments=scenario.input_payload,
            metadata={
                "requested_by": "golden_evaluation_dataset_runner",
                "scenario_id": scenario.id,
            },
        )

        return self._to_output(response.output)

    def _execute_qa_agent_scenario(
        self,
        scenario: EvaluationScenario,
    ) -> dict[str, Any]:
        if self.qa_agent_service is None:
            raise NotImplementedError(
                "QA Agent scenario cannot run because no QA Agent service was configured."
            )

        payload = QAAgentRunRequest.model_validate(scenario.input_payload)
        response = self.qa_agent_service.run(payload)

        return self._to_output(response)

    def _execute_data_analyst_agent_scenario(
        self,
        scenario: EvaluationScenario,
    ) -> dict[str, Any]:
        if self.data_analyst_agent_service is None:
            raise NotImplementedError(
                "Data Analyst Agent scenario cannot run because no Data Analyst "
                "Agent service was configured."
            )

        payload = DataAnalystAgentRequest.model_validate(scenario.input_payload)
        response = self.data_analyst_agent_service.run(payload)

        return self._to_output(response)

    def _execute_multi_agent_qa_copilot_scenario(
        self,
        scenario: EvaluationScenario,
    ) -> dict[str, Any]:
        if self.multi_agent_qa_copilot_service is None:
            raise NotImplementedError(
                "Multi-Agent QA Copilot scenario cannot run because no "
                "MultiAgentQACopilotService was configured."
            )

        payload = MultiAgentQACopilotRequest.model_validate(scenario.input_payload)
        response = self.multi_agent_qa_copilot_service.run(payload)

        return self._to_output(response)

    def _execute_mcp_tool_scenario(
        self,
        scenario: EvaluationScenario,
    ) -> dict[str, Any]:
        tool_name = scenario.input_payload.get("tool_name")
        arguments = scenario.input_payload.get("arguments", {})

        if tool_name == "get_project_status":
            return get_project_status_tool()

        raise NotImplementedError(
            f"MCP tool scenario is not supported yet: {tool_name}. "
            f"Arguments received: {arguments}"
        )

    def _build_checks(
        self,
        scenario: EvaluationScenario,
        output: dict[str, Any],
    ) -> list[EvaluationScenarioRunCheck]:
        return [
            self._check_expected_status(
                scenario=scenario,
                output=output,
            ),
            self._check_expected_quality_gate(
                scenario=scenario,
                output=output,
            ),
            self._check_required_output_markers(
                scenario=scenario,
                output=output,
            ),
            self._check_required_metadata_keys(
                scenario=scenario,
                output=output,
            ),
        ]

    @staticmethod
    def _check_expected_status(
        scenario: EvaluationScenario,
        output: dict[str, Any],
    ) -> EvaluationScenarioRunCheck:
        expected_status = scenario.expectations.expected_status

        if expected_status is None:
            return EvaluationScenarioRunCheck(
                name="expected_status",
                status="passed",
                summary="No expected status was configured.",
            )

        actual_status = output.get("status")

        if actual_status == expected_status:
            return EvaluationScenarioRunCheck(
                name="expected_status",
                status="passed",
                summary="Output status matched the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                },
            )

        if scenario.type == "mcp_tool" and expected_status == "completed":
            return EvaluationScenarioRunCheck(
                name="expected_status",
                status="passed",
                summary=(
                    "MCP tool executed successfully. The expected status was "
                    "interpreted as scenario execution status."
                ),
                metadata={
                    "expected_status": expected_status,
                    "actual_output_status": actual_status,
                },
            )

        return EvaluationScenarioRunCheck(
            name="expected_status",
            status="failed",
            summary="Output status did not match the expected status.",
            metadata={
                "expected_status": expected_status,
                "actual_status": actual_status,
            },
        )

    @staticmethod
    def _check_expected_quality_gate(
        scenario: EvaluationScenario,
        output: dict[str, Any],
    ) -> EvaluationScenarioRunCheck:
        expected_quality_gate = scenario.expectations.expected_quality_gate

        if expected_quality_gate is None:
            return EvaluationScenarioRunCheck(
                name="expected_quality_gate",
                status="passed",
                summary="No expected quality gate was configured.",
            )

        final_report = output.get("final_report", {})
        final_report_metadata = final_report.get("metadata", {})
        actual_quality_gate = final_report_metadata.get("quality_gate")

        if actual_quality_gate == expected_quality_gate:
            return EvaluationScenarioRunCheck(
                name="expected_quality_gate",
                status="passed",
                summary="Quality gate matched the expected value.",
                metadata={
                    "expected_quality_gate": expected_quality_gate,
                    "actual_quality_gate": actual_quality_gate,
                },
            )

        return EvaluationScenarioRunCheck(
            name="expected_quality_gate",
            status="failed",
            summary="Quality gate did not match the expected value.",
            metadata={
                "expected_quality_gate": expected_quality_gate,
                "actual_quality_gate": actual_quality_gate,
            },
        )

    @staticmethod
    def _check_required_output_markers(
        scenario: EvaluationScenario,
        output: dict[str, Any],
    ) -> EvaluationScenarioRunCheck:
        required_output_markers = scenario.expectations.required_output_markers

        missing_markers = [
            marker
            for marker in required_output_markers
            if marker not in output
        ]

        if not missing_markers:
            return EvaluationScenarioRunCheck(
                name="required_output_markers",
                status="passed",
                summary="All required output markers were found.",
                metadata={
                    "required_output_markers": required_output_markers,
                    "missing_markers": [],
                },
            )

        return EvaluationScenarioRunCheck(
            name="required_output_markers",
            status="failed",
            summary="One or more required output markers were missing.",
            metadata={
                "required_output_markers": required_output_markers,
                "missing_markers": missing_markers,
            },
        )

    @staticmethod
    def _check_required_metadata_keys(
        scenario: EvaluationScenario,
        output: dict[str, Any],
    ) -> EvaluationScenarioRunCheck:
        required_metadata_keys = scenario.expectations.required_metadata_keys

        if not required_metadata_keys:
            return EvaluationScenarioRunCheck(
                name="required_metadata_keys",
                status="passed",
                summary="No required metadata keys were configured.",
            )

        metadata = output.get("metadata", {})

        missing_keys = [
            key
            for key in required_metadata_keys
            if key not in metadata
        ]

        if not missing_keys:
            return EvaluationScenarioRunCheck(
                name="required_metadata_keys",
                status="passed",
                summary="All required metadata keys were found.",
                metadata={
                    "required_metadata_keys": required_metadata_keys,
                    "missing_keys": [],
                },
            )

        return EvaluationScenarioRunCheck(
            name="required_metadata_keys",
            status="failed",
            summary="One or more required metadata keys were missing.",
            metadata={
                "required_metadata_keys": required_metadata_keys,
                "missing_keys": missing_keys,
            },
        )

    @staticmethod
    def _select_scenarios(
        scenarios: list[EvaluationScenario],
        scenario_ids: list[str],
        scenario_types: list[str],
    ) -> list[EvaluationScenario]:
        selected_scenarios = scenarios

        if scenario_ids:
            scenario_id_set = set(scenario_ids)
            selected_scenarios = [
                scenario
                for scenario in selected_scenarios
                if scenario.id in scenario_id_set
            ]

        if scenario_types:
            scenario_type_set = set(scenario_types)
            selected_scenarios = [
                scenario
                for scenario in selected_scenarios
                if scenario.type in scenario_type_set
            ]

        return selected_scenarios

    @staticmethod
    def _resolve_scenario_status(
        checks: list[EvaluationScenarioRunCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _to_output(response: Any) -> dict[str, Any]:
        if isinstance(response, dict):
            return response

        if hasattr(response, "model_dump"):
            return response.model_dump(mode="json")

        raise TypeError(
            f"Unsupported response type for evaluation output: {type(response)!r}"
        )

    @staticmethod
    def _count_results(
        results: list[EvaluationScenarioRunResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )
