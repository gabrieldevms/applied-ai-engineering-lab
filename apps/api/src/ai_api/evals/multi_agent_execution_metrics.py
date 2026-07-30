from datetime import UTC, datetime
from uuid import uuid4
from ai_api.evals.schemas import (
    AIMultiAgentExecutionRecord,
    AIMultiAgentExecutionRecordRequest,
    AIMultiAgentExecutionRecordsResponse,
    AIMultiAgentExecutionSummaryRequest,
    AIMultiAgentExecutionSummaryResponse,
)


class AIMultiAgentExecutionTelemetryService:
    def __init__(self) -> None:
        self._records: list[AIMultiAgentExecutionRecord] = []

    def record(
        self,
        request: AIMultiAgentExecutionRecordRequest,
    ) -> AIMultiAgentExecutionRecord:
        agent_success_rate = self._calculate_rate(
            numerator=request.completed_agent_count,
            denominator=request.agent_count,
        )
        task_success_rate = self._calculate_rate(
            numerator=request.successful_task_count,
            denominator=request.task_count,
        )
        handoff_success_rate = self._calculate_inverse_failure_rate(
            total_count=request.handoff_count,
            failed_count=request.failed_handoff_count,
        )
        contract_success_rate = self._calculate_rate(
            numerator=request.passed_contract_check_count,
            denominator=request.contract_check_count,
        )
        artifact_coverage_score = self._calculate_coverage_score(
            actual_count=request.artifact_count,
            expected_min_count=request.expected_min_artifacts,
        )
        final_report_coverage_score = self._calculate_coverage_score(
            actual_count=request.final_report_section_count,
            expected_min_count=request.expected_min_final_report_sections,
        )
        data_validation_score = self._calculate_data_validation_score(
            require_data_validation_evidence=request.require_data_validation_evidence,
            data_validation_evidence_count=request.data_validation_evidence_count,
        )
        quality_score = self._calculate_quality_score(
            run_status=request.run_status,
            agent_success_rate=agent_success_rate,
            task_success_rate=task_success_rate,
            handoff_success_rate=handoff_success_rate,
            contract_success_rate=contract_success_rate,
            artifact_coverage_score=artifact_coverage_score,
            final_report_coverage_score=final_report_coverage_score,
            data_validation_score=data_validation_score,
        )
        failure_risks = self._build_failure_risks(
            request=request,
            quality_score=quality_score,
        )
        warning_risks = self._build_warning_risks(
            request=request,
            quality_score=quality_score,
        )
        status = self._resolve_status(
            failure_risks=failure_risks,
            warning_risks=warning_risks,
        )
        risks = failure_risks + warning_risks

        if not risks:
            risks = [
                "No multi-agent execution risks detected.",
            ]

        record = AIMultiAgentExecutionRecord(
            record_id=str(uuid4()),
            component=request.component,
            operation=request.operation,
            workflow_name=request.workflow_name,
            run_status=request.run_status,
            status=status,
            duration_ms=request.duration_ms,
            agent_count=request.agent_count,
            completed_agent_count=request.completed_agent_count,
            failed_agent_count=request.failed_agent_count,
            skipped_agent_count=request.skipped_agent_count,
            task_count=request.task_count,
            successful_task_count=request.successful_task_count,
            failed_task_count=request.failed_task_count,
            artifact_count=request.artifact_count,
            expected_min_artifacts=request.expected_min_artifacts,
            handoff_count=request.handoff_count,
            failed_handoff_count=request.failed_handoff_count,
            contract_check_count=request.contract_check_count,
            passed_contract_check_count=request.passed_contract_check_count,
            failed_contract_check_count=request.failed_contract_check_count,
            conflict_count=request.conflict_count,
            critical_conflict_count=request.critical_conflict_count,
            failure_count=request.failure_count,
            error_count=request.error_count,
            final_report_section_count=request.final_report_section_count,
            expected_min_final_report_sections=(
                request.expected_min_final_report_sections
            ),
            data_validation_evidence_count=request.data_validation_evidence_count,
            require_data_validation_evidence=request.require_data_validation_evidence,
            retry_count=request.retry_count,
            fallback_count=request.fallback_count,
            agent_success_rate=agent_success_rate,
            task_success_rate=task_success_rate,
            handoff_success_rate=handoff_success_rate,
            contract_success_rate=contract_success_rate,
            artifact_coverage_score=artifact_coverage_score,
            final_report_coverage_score=final_report_coverage_score,
            data_validation_score=data_validation_score,
            quality_score=quality_score,
            max_duration_ms=request.max_duration_ms,
            max_failed_agents=request.max_failed_agents,
            max_failed_tasks=request.max_failed_tasks,
            max_failed_handoffs=request.max_failed_handoffs,
            max_failed_contract_checks=request.max_failed_contract_checks,
            max_critical_conflicts=request.max_critical_conflicts,
            max_failures=request.max_failures,
            max_errors=request.max_errors,
            min_quality_score=request.min_quality_score,
            risks=risks,
            recorded_at=self._utc_now(),
            run_id=request.run_id,
            trace_id=request.trace_id,
            metadata={
                "multi_agent_execution_schema_version": "0.1.0",
                "scoring_mode": "caller_provided_multi_agent_execution_signals",
                **request.metadata,
            },
        )

        self._records.append(record)

        return record

    def list_records(
        self,
        component: str | None = None,
        workflow_name: str | None = None,
        operation: str | None = None,
        status: str | None = None,
        run_status: str | None = None,
        limit: int = 100,
    ) -> AIMultiAgentExecutionRecordsResponse:
        filtered_records = self._records

        if component is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.component == component
            ]

        if workflow_name is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.workflow_name == workflow_name
            ]

        if operation is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.operation == operation
            ]

        if status is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.status == status
            ]

        if run_status is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.run_status == run_status
            ]

        limited_records = filtered_records[-limit:]

        return AIMultiAgentExecutionRecordsResponse(
            records=limited_records,
            count=len(limited_records),
            metadata={
                "source": "ai-multi-agent-execution-telemetry-service",
                "total_stored_records": len(self._records),
                "applied_filters": {
                    "component": component,
                    "workflow_name": workflow_name,
                    "operation": operation,
                    "status": status,
                    "run_status": run_status,
                    "limit": limit,
                },
            },
        )

    def summarize(
        self,
        request: AIMultiAgentExecutionSummaryRequest,
    ) -> AIMultiAgentExecutionSummaryResponse:
        records = request.records if request.records is not None else self._records

        return AIMultiAgentExecutionSummaryResponse(
            record_count=len(records),
            passed_count=self._count_records(records, "passed"),
            warning_count=self._count_records(records, "warning"),
            failed_count=self._count_records(records, "failed"),
            total_agents=sum(record.agent_count for record in records),
            total_completed_agents=sum(
                record.completed_agent_count
                for record in records
            ),
            total_failed_agents=sum(
                record.failed_agent_count
                for record in records
            ),
            total_skipped_agents=sum(
                record.skipped_agent_count
                for record in records
            ),
            total_tasks=sum(record.task_count for record in records),
            total_successful_tasks=sum(
                record.successful_task_count
                for record in records
            ),
            total_failed_tasks=sum(
                record.failed_task_count
                for record in records
            ),
            total_artifacts=sum(record.artifact_count for record in records),
            total_handoffs=sum(record.handoff_count for record in records),
            total_failed_handoffs=sum(
                record.failed_handoff_count
                for record in records
            ),
            total_contract_checks=sum(
                record.contract_check_count
                for record in records
            ),
            total_passed_contract_checks=sum(
                record.passed_contract_check_count
                for record in records
            ),
            total_failed_contract_checks=sum(
                record.failed_contract_check_count
                for record in records
            ),
            total_conflicts=sum(record.conflict_count for record in records),
            total_critical_conflicts=sum(
                record.critical_conflict_count
                for record in records
            ),
            total_failures=sum(record.failure_count for record in records),
            total_errors=sum(record.error_count for record in records),
            total_final_report_sections=sum(
                record.final_report_section_count
                for record in records
            ),
            total_data_validation_evidence=sum(
                record.data_validation_evidence_count
                for record in records
            ),
            total_retries=sum(record.retry_count for record in records),
            total_fallbacks=sum(record.fallback_count for record in records),
            average_duration_ms=self._average_optional_metric(
                [
                    record.duration_ms
                    for record in records
                ]
            ),
            average_agent_success_rate=self._average_optional_metric(
                [
                    record.agent_success_rate
                    for record in records
                ]
            ),
            average_task_success_rate=self._average_optional_metric(
                [
                    record.task_success_rate
                    for record in records
                ]
            ),
            average_handoff_success_rate=self._average_optional_metric(
                [
                    record.handoff_success_rate
                    for record in records
                ]
            ),
            average_contract_success_rate=self._average_optional_metric(
                [
                    record.contract_success_rate
                    for record in records
                ]
            ),
            average_artifact_coverage_score=self._average_optional_metric(
                [
                    record.artifact_coverage_score
                    for record in records
                ]
            ),
            average_final_report_coverage_score=self._average_optional_metric(
                [
                    record.final_report_coverage_score
                    for record in records
                ]
            ),
            average_data_validation_score=self._average_optional_metric(
                [
                    record.data_validation_score
                    for record in records
                ]
            ),
            average_quality_score=self._average_optional_metric(
                [
                    record.quality_score
                    for record in records
                ]
            ),
            component_coverage=self._build_coverage(
                [
                    record.component
                    for record in records
                ]
            ),
            workflow_coverage=self._build_coverage(
                [
                    record.workflow_name
                    for record in records
                ]
            ),
            operation_coverage=self._build_coverage(
                [
                    record.operation
                    for record in records
                ]
            ),
            run_status_coverage=self._build_coverage(
                [
                    record.run_status
                    for record in records
                ]
            ),
            risks=self._build_summary_risks(records),
            metadata={
                "summarizer": "ai-multi-agent-execution-summary-v1",
                "source": "stored_records"
                if request.records is None
                else "request_records",
                **request.metadata,
            },
        )

    def clear(self) -> None:
        self._records.clear()

    @staticmethod
    def _calculate_rate(
        numerator: int,
        denominator: int,
    ) -> float | None:
        if denominator == 0:
            return None

        return round(min(numerator / denominator, 1.0), 4)

    @staticmethod
    def _calculate_inverse_failure_rate(
        total_count: int,
        failed_count: int,
    ) -> float | None:
        if total_count == 0:
            return None

        success_count = max(total_count - failed_count, 0)

        return round(success_count / total_count, 4)

    @staticmethod
    def _calculate_coverage_score(
        actual_count: int,
        expected_min_count: int,
    ) -> float | None:
        if expected_min_count == 0:
            return None

        return round(min(actual_count / expected_min_count, 1.0), 4)

    @staticmethod
    def _calculate_data_validation_score(
        require_data_validation_evidence: bool,
        data_validation_evidence_count: int,
    ) -> float | None:
        if not require_data_validation_evidence:
            return None

        if data_validation_evidence_count > 0:
            return 1.0

        return 0.0

    @staticmethod
    def _calculate_quality_score(
        run_status: str,
        agent_success_rate: float | None,
        task_success_rate: float | None,
        handoff_success_rate: float | None,
        contract_success_rate: float | None,
        artifact_coverage_score: float | None,
        final_report_coverage_score: float | None,
        data_validation_score: float | None,
    ) -> float | None:
        run_status_score_map = {
            "completed": 1.0,
            "partial": 0.6,
            "failed": 0.0,
            "blocked": 0.0,
            "cancelled": 0.0,
        }

        available_scores = [
            run_status_score_map.get(run_status, 0.0),
        ]

        for score in [
            agent_success_rate,
            task_success_rate,
            handoff_success_rate,
            contract_success_rate,
            artifact_coverage_score,
            final_report_coverage_score,
            data_validation_score,
        ]:
            if score is not None:
                available_scores.append(score)

        if not available_scores:
            return None

        return round(sum(available_scores) / len(available_scores), 4)

    @staticmethod
    def _build_failure_risks(
        request: AIMultiAgentExecutionRecordRequest,
        quality_score: float | None,
    ) -> list[str]:
        risks: list[str] = []

        if request.run_status in {"failed", "blocked", "cancelled"}:
            risks.append(
                "Multi-agent run ended with a non-success terminal status."
            )

        if request.failed_agent_count > request.max_failed_agents:
            risks.append(
                "Failed agent count exceeded the configured maximum."
            )

        if request.failed_task_count > request.max_failed_tasks:
            risks.append(
                "Failed task count exceeded the configured maximum."
            )

        if request.failed_handoff_count > request.max_failed_handoffs:
            risks.append(
                "Failed handoff count exceeded the configured maximum."
            )

        if request.failed_contract_check_count > request.max_failed_contract_checks:
            risks.append(
                "Failed contract check count exceeded the configured maximum."
            )

        if request.critical_conflict_count > request.max_critical_conflicts:
            risks.append(
                "Critical conflict count exceeded the configured maximum."
            )

        if request.failure_count > request.max_failures:
            risks.append(
                "Failure count exceeded the configured maximum."
            )

        if request.error_count > request.max_errors:
            risks.append(
                "Error count exceeded the configured maximum."
            )

        if (
            request.artifact_count < request.expected_min_artifacts
        ):
            risks.append(
                "Artifact count is below the expected minimum."
            )

        if (
            request.final_report_section_count
            < request.expected_min_final_report_sections
        ):
            risks.append(
                "Final report section count is below the expected minimum."
            )

        if (
            request.require_data_validation_evidence
            and request.data_validation_evidence_count == 0
        ):
            risks.append(
                "Data validation evidence was required but not provided."
            )

        if quality_score is not None and quality_score < request.min_quality_score:
            risks.append(
                "Multi-agent execution quality score is below the configured minimum."
            )

        return risks

    @staticmethod
    def _build_warning_risks(
        request: AIMultiAgentExecutionRecordRequest,
        quality_score: float | None,
    ) -> list[str]:
        risks: list[str] = []

        if (
            request.max_duration_ms is not None
            and request.duration_ms is not None
            and request.duration_ms > request.max_duration_ms
        ):
            risks.append(
                "Multi-agent execution duration exceeded the configured maximum."
            )

        if request.retry_count > 0:
            risks.append(
                "Multi-agent execution required retries."
            )

        if request.fallback_count > 0:
            risks.append(
                "Multi-agent execution used fallback behavior."
            )

        if request.skipped_agent_count > 0:
            risks.append(
                "One or more agents were skipped."
            )

        if quality_score is None:
            risks.append(
                "Multi-agent execution quality score could not be calculated."
            )

        if request.duration_ms is None:
            risks.append(
                "Multi-agent execution duration was not provided."
            )

        return risks

    @staticmethod
    def _resolve_status(
        failure_risks: list[str],
        warning_risks: list[str],
    ) -> str:
        if failure_risks:
            return "failed"

        if warning_risks:
            return "warning"

        return "passed"

    @staticmethod
    def _average_optional_metric(
        values: list[float | None],
    ) -> float | None:
        available_values = [
            value
            for value in values
            if value is not None
        ]

        if not available_values:
            return None

        return round(sum(available_values) / len(available_values), 4)

    @staticmethod
    def _count_records(
        records: list[AIMultiAgentExecutionRecord],
        status: str,
    ) -> int:
        return len(
            [
                record
                for record in records
                if record.status == status
            ]
        )

    @staticmethod
    def _build_coverage(
        values: list[str],
    ) -> dict[str, int]:
        coverage: dict[str, int] = {}

        for value in values:
            coverage[value] = coverage.get(value, 0) + 1

        return coverage

    @staticmethod
    def _build_summary_risks(
        records: list[AIMultiAgentExecutionRecord],
    ) -> list[str]:
        if not records:
            return [
                "No multi-agent execution records available.",
            ]

        failed_count = AIMultiAgentExecutionTelemetryService._count_records(
            records,
            "failed",
        )
        warning_count = AIMultiAgentExecutionTelemetryService._count_records(
            records,
            "warning",
        )

        risks: list[str] = []

        if failed_count > 0:
            risks.append(
                f"{failed_count} multi-agent execution record(s) failed."
            )

        if warning_count > 0:
            risks.append(
                f"{warning_count} multi-agent execution record(s) returned warning."
            )

        if not risks:
            risks.append(
                "No multi-agent execution risks detected."
            )

        return risks

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
    