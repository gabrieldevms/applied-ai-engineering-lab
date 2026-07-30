from ai_api.multi_agent.schemas import (
    MultiAgentArtifact,
    MultiAgentEvaluationMetric,
    MultiAgentQACopilotEvaluationRequest,
    MultiAgentQACopilotEvaluationResponse,
    MultiAgentQACopilotResponse,
    MultiAgentRoleName,
)


EXPECTED_MULTI_AGENT_ROLE_NAMES: list[MultiAgentRoleName] = [
    "orchestrator_agent",
    "requirement_analyst_agent",
    "functional_qa_agent",
    "test_automation_agent",
    "reviewer_agent",
    "report_agent",
]


class MultiAgentQACopilotEvaluationService:
    def evaluate(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentQACopilotEvaluationResponse:
        response = request.response

        metrics = [
            self._evaluate_status_alignment(request),
            self._evaluate_role_coverage(request),
            self._evaluate_trace_integrity(response),
            self._evaluate_contract_validation(request),
            self._evaluate_failure_control(request),
            self._evaluate_conflict_control(request),
            self._evaluate_final_report(request),
            self._evaluate_data_validation_evidence(request),
        ]

        status = self._resolve_status(metrics)
        score = self._calculate_score(metrics)

        return MultiAgentQACopilotEvaluationResponse(
            status=status,
            score=score,
            metrics=metrics,
            metadata={
                "evaluator": "multi-agent-qa-copilot-evaluator-v1",
                "metric_count": len(metrics),
                "passed_metrics": self._count_metrics(metrics, "passed"),
                "warning_metrics": self._count_metrics(metrics, "warning"),
                "failed_metrics": self._count_metrics(metrics, "failed"),
                "copilot_status": response.status,
                "quality_gate": response.final_report.metadata.get(
                    "quality_gate",
                    "unknown",
                ),
                **request.metadata,
            },
        )

    def _evaluate_status_alignment(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentEvaluationMetric:
        if request.expected_status is None:
            return MultiAgentEvaluationMetric(
                name="status_alignment",
                status="passed",
                score=1.0,
                summary="No expected status was provided, so status alignment passed.",
                metadata={
                    "actual_status": request.response.status,
                    "expected_status": None,
                },
            )

        if request.response.status == request.expected_status:
            return MultiAgentEvaluationMetric(
                name="status_alignment",
                status="passed",
                score=1.0,
                summary="Copilot status matches the expected status.",
                metadata={
                    "actual_status": request.response.status,
                    "expected_status": request.expected_status,
                },
            )

        return MultiAgentEvaluationMetric(
            name="status_alignment",
            status="failed",
            score=0.0,
            summary="Copilot status does not match the expected status.",
            metadata={
                "actual_status": request.response.status,
                "expected_status": request.expected_status,
            },
        )

    def _evaluate_role_coverage(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentEvaluationMetric:
        response = request.response

        if not request.require_all_roles:
            return MultiAgentEvaluationMetric(
                name="role_coverage",
                status="passed",
                score=1.0,
                summary="Full role coverage was not required for this evaluation.",
                metadata={
                    "required": False,
                },
            )

        response_role_names = {
            role.name
            for role in response.roles
        }
        task_role_names = {
            task_result.agent_name
            for task_result in response.task_results
        }

        missing_roles = [
            role_name
            for role_name in EXPECTED_MULTI_AGENT_ROLE_NAMES
            if role_name not in response_role_names
            or role_name not in task_role_names
        ]

        if not missing_roles:
            return MultiAgentEvaluationMetric(
                name="role_coverage",
                status="passed",
                score=1.0,
                summary="All expected multi-agent roles were present.",
                metadata={
                    "expected_roles": EXPECTED_MULTI_AGENT_ROLE_NAMES,
                    "missing_roles": [],
                },
            )

        return MultiAgentEvaluationMetric(
            name="role_coverage",
            status="failed",
            score=0.0,
            summary="One or more expected multi-agent roles were missing.",
            metadata={
                "expected_roles": EXPECTED_MULTI_AGENT_ROLE_NAMES,
                "missing_roles": missing_roles,
            },
        )

    def _evaluate_trace_integrity(
        self,
        response: MultiAgentQACopilotResponse,
    ) -> MultiAgentEvaluationMetric:
        if not response.trace:
            return MultiAgentEvaluationMetric(
                name="trace_integrity",
                status="failed",
                score=0.0,
                summary="Execution trace is missing.",
                metadata={
                    "trace_count": 0,
                    "task_result_count": len(response.task_results),
                },
            )

        if len(response.trace) != len(response.task_results):
            return MultiAgentEvaluationMetric(
                name="trace_integrity",
                status="warning",
                score=0.5,
                summary="Trace count does not match task result count.",
                metadata={
                    "trace_count": len(response.trace),
                    "task_result_count": len(response.task_results),
                },
            )

        return MultiAgentEvaluationMetric(
            name="trace_integrity",
            status="passed",
            score=1.0,
            summary="Execution trace is present and aligned with task results.",
            metadata={
                "trace_count": len(response.trace),
                "task_result_count": len(response.task_results),
            },
        )

    def _evaluate_contract_validation(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentEvaluationMetric:
        contract_validation = request.response.contract_validation

        if contract_validation is None:
            return MultiAgentEvaluationMetric(
                name="contract_validation",
                status="failed",
                score=0.0,
                summary="Contract validation result is missing.",
                metadata={
                    "required": request.require_contracts_passed,
                },
            )

        if not request.require_contracts_passed:
            return MultiAgentEvaluationMetric(
                name="contract_validation",
                status="passed",
                score=1.0,
                summary="Contract validation was available but not required to pass.",
                metadata={
                    "contract_validation_status": contract_validation.status,
                    "required": False,
                },
            )

        if contract_validation.status == "passed":
            return MultiAgentEvaluationMetric(
                name="contract_validation",
                status="passed",
                score=1.0,
                summary="Communication contracts passed.",
                metadata={
                    "contract_validation_status": contract_validation.status,
                    "failed_contracts": contract_validation.failed_contracts,
                    "warning_contracts": contract_validation.warning_contracts,
                },
            )

        return MultiAgentEvaluationMetric(
            name="contract_validation",
            status="failed",
            score=0.0,
            summary="Communication contracts did not pass.",
            metadata={
                "contract_validation_status": contract_validation.status,
                "failed_contracts": contract_validation.failed_contracts,
                "warning_contracts": contract_validation.warning_contracts,
            },
        )

    def _evaluate_failure_control(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentEvaluationMetric:
        response = request.response

        failed_or_skipped_tasks = [
            task_result
            for task_result in response.task_results
            if task_result.status in {"failed", "skipped"}
        ]

        if not request.require_no_failures:
            status = "warning" if response.failures else "passed"
            score = 0.5 if response.failures else 1.0

            return MultiAgentEvaluationMetric(
                name="failure_control",
                status=status,
                score=score,
                summary=(
                    "Failures were allowed for this evaluation."
                    if response.failures
                    else "No failures were found."
                ),
                metadata={
                    "required_no_failures": False,
                    "failure_count": len(response.failures),
                    "failed_or_skipped_task_count": len(failed_or_skipped_tasks),
                },
            )

        if response.failures or failed_or_skipped_tasks:
            return MultiAgentEvaluationMetric(
                name="failure_control",
                status="failed",
                score=0.0,
                summary="Failures or skipped tasks were found.",
                metadata={
                    "failure_count": len(response.failures),
                    "failed_or_skipped_task_count": len(failed_or_skipped_tasks),
                },
            )

        return MultiAgentEvaluationMetric(
            name="failure_control",
            status="passed",
            score=1.0,
            summary="No failures or skipped tasks were found.",
            metadata={
                "failure_count": 0,
                "failed_or_skipped_task_count": 0,
            },
        )

    def _evaluate_conflict_control(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentEvaluationMetric:
        conflict_analysis = request.response.conflict_analysis

        if conflict_analysis is None:
            return MultiAgentEvaluationMetric(
                name="conflict_control",
                status="failed",
                score=0.0,
                summary="Conflict analysis result is missing.",
                metadata={
                    "required_no_critical_conflicts": (
                        request.require_no_critical_conflicts
                    ),
                },
            )

        if (
            request.require_no_critical_conflicts
            and conflict_analysis.critical_count > 0
        ):
            return MultiAgentEvaluationMetric(
                name="conflict_control",
                status="failed",
                score=0.0,
                summary="Critical conflicts were detected.",
                metadata={
                    "conflict_analysis_status": conflict_analysis.status,
                    "critical_count": conflict_analysis.critical_count,
                    "warning_count": conflict_analysis.warning_count,
                },
            )

        if conflict_analysis.warning_count > 0:
            return MultiAgentEvaluationMetric(
                name="conflict_control",
                status="warning",
                score=0.5,
                summary="Non-critical conflicts were detected.",
                metadata={
                    "conflict_analysis_status": conflict_analysis.status,
                    "critical_count": conflict_analysis.critical_count,
                    "warning_count": conflict_analysis.warning_count,
                },
            )

        return MultiAgentEvaluationMetric(
            name="conflict_control",
            status="passed",
            score=1.0,
            summary="No conflicts were detected.",
            metadata={
                "conflict_analysis_status": conflict_analysis.status,
                "critical_count": conflict_analysis.critical_count,
                "warning_count": conflict_analysis.warning_count,
            },
        )

    def _evaluate_final_report(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentEvaluationMetric:
        final_report = request.response.final_report
        quality_gate = final_report.metadata.get("quality_gate")

        if request.expected_quality_gate is not None and (
            quality_gate != request.expected_quality_gate
        ):
            return MultiAgentEvaluationMetric(
                name="final_report",
                status="failed",
                score=0.0,
                summary="Final report quality gate does not match the expected value.",
                metadata={
                    "actual_quality_gate": quality_gate,
                    "expected_quality_gate": request.expected_quality_gate,
                },
            )

        if not request.require_final_report:
            return MultiAgentEvaluationMetric(
                name="final_report",
                status="passed",
                score=1.0,
                summary="Final report validation was not required.",
                metadata={
                    "required": False,
                    "quality_gate": quality_gate,
                },
            )

        missing_sections = []

        if not final_report.summary:
            missing_sections.append("summary")

        if not final_report.requirement_understanding:
            missing_sections.append("requirement_understanding")

        if not final_report.functional_coverage:
            missing_sections.append("functional_coverage")

        if not final_report.automation_strategy:
            missing_sections.append("automation_strategy")

        if not final_report.review_notes:
            missing_sections.append("review_notes")

        if not final_report.next_steps:
            missing_sections.append("next_steps")

        if missing_sections:
            return MultiAgentEvaluationMetric(
                name="final_report",
                status="failed",
                score=0.0,
                summary="Final report is missing required sections.",
                metadata={
                    "missing_sections": missing_sections,
                    "quality_gate": quality_gate,
                },
            )

        return MultiAgentEvaluationMetric(
            name="final_report",
            status="passed",
            score=1.0,
            summary="Final report contains the expected sections.",
            metadata={
                "missing_sections": [],
                "quality_gate": quality_gate,
            },
        )

    def _evaluate_data_validation_evidence(
        self,
        request: MultiAgentQACopilotEvaluationRequest,
    ) -> MultiAgentEvaluationMetric:
        response = request.response

        if not request.require_data_validation_evidence:
            return MultiAgentEvaluationMetric(
                name="data_validation_evidence",
                status="passed",
                score=1.0,
                summary="Data validation evidence was not required.",
                metadata={
                    "required": False,
                    "data_validation_available": response.final_report.metadata.get(
                        "data_validation_available",
                        False,
                    ),
                },
            )

        data_validation_artifact = self._find_artifact(
            response=response,
            artifact_name="data_validation_analysis",
        )

        if data_validation_artifact is None:
            return MultiAgentEvaluationMetric(
                name="data_validation_evidence",
                status="failed",
                score=0.0,
                summary="Data validation evidence was required but no artifact was found.",
                metadata={
                    "required": True,
                    "artifact_found": False,
                },
            )

        artifact_status = data_validation_artifact.content.get("status")

        if artifact_status != "completed":
            return MultiAgentEvaluationMetric(
                name="data_validation_evidence",
                status="failed",
                score=0.0,
                summary="Data validation artifact was found but did not complete successfully.",
                metadata={
                    "required": True,
                    "artifact_found": True,
                    "artifact_status": artifact_status,
                },
            )

        if not response.final_report.data_validation_evidence:
            return MultiAgentEvaluationMetric(
                name="data_validation_evidence",
                status="failed",
                score=0.0,
                summary="Data validation artifact completed, but final report evidence is missing.",
                metadata={
                    "required": True,
                    "artifact_found": True,
                    "artifact_status": artifact_status,
                    "report_evidence_count": 0,
                },
            )

        return MultiAgentEvaluationMetric(
            name="data_validation_evidence",
            status="passed",
            score=1.0,
            summary="Data validation evidence was found and included in the final report.",
            metadata={
                "required": True,
                "artifact_found": True,
                "artifact_status": artifact_status,
                "report_evidence_count": len(
                    response.final_report.data_validation_evidence
                ),
            },
        )

    @staticmethod
    def _find_artifact(
        response: MultiAgentQACopilotResponse,
        artifact_name: str,
    ) -> MultiAgentArtifact | None:
        for artifact in response.shared_state.artifacts:
            if artifact.name == artifact_name:
                return artifact

        return None

    @staticmethod
    def _resolve_status(
        metrics: list[MultiAgentEvaluationMetric],
    ) -> str:
        if any(metric.status == "failed" for metric in metrics):
            return "failed"

        if any(metric.status == "warning" for metric in metrics):
            return "warning"

        return "passed"

    @staticmethod
    def _calculate_score(
        metrics: list[MultiAgentEvaluationMetric],
    ) -> float:
        if not metrics:
            return 0.0

        total_score = sum(metric.score for metric in metrics)

        return round(total_score / len(metrics), 4)

    @staticmethod
    def _count_metrics(
        metrics: list[MultiAgentEvaluationMetric],
        status: str,
    ) -> int:
        return len(
            [
                metric
                for metric in metrics
                if metric.status == status
            ]
        )
