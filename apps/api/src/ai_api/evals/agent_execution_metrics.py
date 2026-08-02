from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4
from ai_api.config import Settings
from ai_api.evals.schemas import (
    AIAgentExecutionRecord,
    AIAgentExecutionRecordRequest,
    AIAgentExecutionRecordsResponse,
    AIAgentExecutionSummaryRequest,
    AIAgentExecutionSummaryResponse,
)
from ai_api.storage import JsonlStore, resolve_storage_path


class AIAgentExecutionRecordStore(Protocol):
    def append(
        self,
        record: AIAgentExecutionRecord,
    ) -> AIAgentExecutionRecord:
        """Append an agent execution record."""
        ...

    def list_records(self) -> list[AIAgentExecutionRecord]:
        """List all stored agent execution records."""
        ...

    def count(self) -> int:
        """Return the number of stored agent execution records."""
        ...

    def clear(self) -> None:
        """Clear all stored agent execution records."""
        ...


class InMemoryAIAgentExecutionRecordStore:
    def __init__(self) -> None:
        self._records: list[AIAgentExecutionRecord] = []

    def append(
        self,
        record: AIAgentExecutionRecord,
    ) -> AIAgentExecutionRecord:
        self._records.append(record)

        return record

    def list_records(self) -> list[AIAgentExecutionRecord]:
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()


class JsonlAIAgentExecutionRecordStore:
    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        self._store = JsonlStore(
            file_path=file_path,
            record_type=AIAgentExecutionRecord,
        )

    def append(
        self,
        record: AIAgentExecutionRecord,
    ) -> AIAgentExecutionRecord:
        return self._store.append(record)

    def list_records(self) -> list[AIAgentExecutionRecord]:
        return self._store.list_records()

    def count(self) -> int:
        return self._store.count()

    def clear(self) -> None:
        self._store.clear()


class AIAgentExecutionTelemetryService:
    def __init__(
        self,
        record_store: AIAgentExecutionRecordStore | None = None,
        storage_backend: str = "memory",
    ) -> None:
        self.record_store = record_store or InMemoryAIAgentExecutionRecordStore()
        self.storage_backend = storage_backend

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
    ) -> "AIAgentExecutionTelemetryService":
        if settings.storage_backend == "local_jsonl":
            return cls(
                record_store=JsonlAIAgentExecutionRecordStore(
                    file_path=resolve_storage_path(
                        settings=settings,
                        relative_path=settings.agent_execution_records_path,
                    ),
                ),
                storage_backend="local_jsonl",
            )

        return cls(
            record_store=InMemoryAIAgentExecutionRecordStore(),
            storage_backend="memory",
        )

    def record(
        self,
        request: AIAgentExecutionRecordRequest,
    ) -> AIAgentExecutionRecord:
        step_success_rate = self._calculate_rate(
            numerator=request.successful_step_count,
            denominator=request.step_count,
        )
        tool_success_rate = self._calculate_rate(
            numerator=request.successful_tool_call_count,
            denominator=request.tool_call_count,
        )
        human_approval_rate = self._calculate_rate(
            numerator=request.human_approval_granted_count,
            denominator=request.human_approval_request_count,
        )
        quality_score = self._calculate_quality_score(
            run_status=request.run_status,
            step_success_rate=step_success_rate,
            tool_success_rate=tool_success_rate,
            human_approval_rate=human_approval_rate,
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
                "No agent execution risks detected.",
            ]

        record = AIAgentExecutionRecord(
            record_id=str(uuid4()),
            component=request.component,
            operation=request.operation,
            agent_name=request.agent_name,
            run_status=request.run_status,
            status=status,
            duration_ms=request.duration_ms,
            step_count=request.step_count,
            successful_step_count=request.successful_step_count,
            failed_step_count=request.failed_step_count,
            tool_call_count=request.tool_call_count,
            successful_tool_call_count=request.successful_tool_call_count,
            failed_tool_call_count=request.failed_tool_call_count,
            retry_count=request.retry_count,
            fallback_count=request.fallback_count,
            error_count=request.error_count,
            human_approval_request_count=request.human_approval_request_count,
            human_approval_granted_count=request.human_approval_granted_count,
            step_success_rate=step_success_rate,
            tool_success_rate=tool_success_rate,
            human_approval_rate=human_approval_rate,
            quality_score=quality_score,
            max_duration_ms=request.max_duration_ms,
            max_failed_steps=request.max_failed_steps,
            max_failed_tool_calls=request.max_failed_tool_calls,
            max_error_count=request.max_error_count,
            min_quality_score=request.min_quality_score,
            risks=risks,
            recorded_at=self._utc_now(),
            run_id=request.run_id,
            trace_id=request.trace_id,
            metadata={
                "agent_execution_schema_version": "0.1.0",
                "scoring_mode": "caller_provided_execution_signals",
                "storage_backend": self.storage_backend,
                **request.metadata,
            },
        )

        return self.record_store.append(record)

    def list_records(
        self,
        component: str | None = None,
        agent_name: str | None = None,
        operation: str | None = None,
        status: str | None = None,
        run_status: str | None = None,
        limit: int = 100,
    ) -> AIAgentExecutionRecordsResponse:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        stored_records = self.record_store.list_records()
        filtered_records = stored_records

        if component is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.component == component
            ]

        if agent_name is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.agent_name == agent_name
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

        return AIAgentExecutionRecordsResponse(
            records=limited_records,
            count=len(limited_records),
            metadata={
                "source": "ai-agent-execution-telemetry-service",
                "storage_backend": self.storage_backend,
                "total_stored_records": len(stored_records),
                "applied_filters": {
                    "component": component,
                    "agent_name": agent_name,
                    "operation": operation,
                    "status": status,
                    "run_status": run_status,
                    "limit": limit,
                },
            },
        )

    def summarize(
        self,
        request: AIAgentExecutionSummaryRequest,
    ) -> AIAgentExecutionSummaryResponse:
        records = (
            request.records
            if request.records is not None
            else self.record_store.list_records()
        )

        return AIAgentExecutionSummaryResponse(
            record_count=len(records),
            passed_count=self._count_records(records, "passed"),
            warning_count=self._count_records(records, "warning"),
            failed_count=self._count_records(records, "failed"),
            total_steps=sum(record.step_count for record in records),
            total_successful_steps=sum(
                record.successful_step_count
                for record in records
            ),
            total_failed_steps=sum(
                record.failed_step_count
                for record in records
            ),
            total_tool_calls=sum(
                record.tool_call_count
                for record in records
            ),
            total_successful_tool_calls=sum(
                record.successful_tool_call_count
                for record in records
            ),
            total_failed_tool_calls=sum(
                record.failed_tool_call_count
                for record in records
            ),
            total_retries=sum(
                record.retry_count
                for record in records
            ),
            total_fallbacks=sum(
                record.fallback_count
                for record in records
            ),
            total_errors=sum(
                record.error_count
                for record in records
            ),
            total_human_approval_requests=sum(
                record.human_approval_request_count
                for record in records
            ),
            total_human_approvals_granted=sum(
                record.human_approval_granted_count
                for record in records
            ),
            average_duration_ms=self._average_optional_metric(
                [
                    record.duration_ms
                    for record in records
                ]
            ),
            average_step_success_rate=self._average_optional_metric(
                [
                    record.step_success_rate
                    for record in records
                ]
            ),
            average_tool_success_rate=self._average_optional_metric(
                [
                    record.tool_success_rate
                    for record in records
                ]
            ),
            average_human_approval_rate=self._average_optional_metric(
                [
                    record.human_approval_rate
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
            agent_coverage=self._build_coverage(
                [
                    record.agent_name
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
                "summarizer": "ai-agent-execution-summary-v1",
                "source": "stored_records"
                if request.records is None
                else "request_records",
                "storage_backend": self.storage_backend,
                **request.metadata,
            },
        )

    def clear(self) -> None:
        self.record_store.clear()

    @staticmethod
    def _calculate_rate(
        numerator: int,
        denominator: int,
    ) -> float | None:
        if denominator == 0:
            return None

        return round(min(numerator / denominator, 1.0), 4)

    @staticmethod
    def _calculate_quality_score(
        run_status: str,
        step_success_rate: float | None,
        tool_success_rate: float | None,
        human_approval_rate: float | None,
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
            step_success_rate,
            tool_success_rate,
            human_approval_rate,
        ]:
            if score is not None:
                available_scores.append(score)

        if not available_scores:
            return None

        return round(sum(available_scores) / len(available_scores), 4)

    @staticmethod
    def _build_failure_risks(
        request: AIAgentExecutionRecordRequest,
        quality_score: float | None,
    ) -> list[str]:
        risks: list[str] = []

        if request.run_status in {"failed", "blocked", "cancelled"}:
            risks.append(
                "Agent run ended with a non-success terminal status."
            )

        if request.failed_step_count > request.max_failed_steps:
            risks.append(
                "Failed step count exceeded the configured maximum."
            )

        if request.failed_tool_call_count > request.max_failed_tool_calls:
            risks.append(
                "Failed tool call count exceeded the configured maximum."
            )

        if request.error_count > request.max_error_count:
            risks.append(
                "Error count exceeded the configured maximum."
            )

        if quality_score is not None and quality_score < request.min_quality_score:
            risks.append(
                "Agent execution quality score is below the configured minimum."
            )

        return risks

    @staticmethod
    def _build_warning_risks(
        request: AIAgentExecutionRecordRequest,
        quality_score: float | None,
    ) -> list[str]:
        risks: list[str] = []

        if (
            request.max_duration_ms is not None
            and request.duration_ms is not None
            and request.duration_ms > request.max_duration_ms
        ):
            risks.append(
                "Agent execution duration exceeded the configured maximum."
            )

        if request.retry_count > 0:
            risks.append(
                "Agent execution required retries."
            )

        if request.fallback_count > 0:
            risks.append(
                "Agent execution used fallback behavior."
            )

        if (
            request.human_approval_request_count > 0
            and request.human_approval_granted_count
            < request.human_approval_request_count
        ):
            risks.append(
                "Not all human approval requests were granted."
            )

        if quality_score is None:
            risks.append(
                "Agent execution quality score could not be calculated."
            )

        if request.duration_ms is None:
            risks.append(
                "Agent execution duration was not provided."
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
        records: list[AIAgentExecutionRecord],
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
        records: list[AIAgentExecutionRecord],
    ) -> list[str]:
        if not records:
            return [
                "No agent execution records available.",
            ]

        failed_count = AIAgentExecutionTelemetryService._count_records(
            records,
            "failed",
        )
        warning_count = AIAgentExecutionTelemetryService._count_records(
            records,
            "warning",
        )

        risks: list[str] = []

        if failed_count > 0:
            risks.append(
                f"{failed_count} agent execution record(s) failed."
            )

        if warning_count > 0:
            risks.append(
                f"{warning_count} agent execution record(s) returned warning."
            )

        if not risks:
            risks.append(
                "No agent execution risks detected."
            )

        return risks

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
