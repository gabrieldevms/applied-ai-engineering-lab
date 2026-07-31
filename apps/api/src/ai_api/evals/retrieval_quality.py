from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4
from ai_api.config import Settings
from ai_api.evals.schemas import (
    AIRetrievalQualityRecord,
    AIRetrievalQualityRecordRequest,
    AIRetrievalQualityRecordsResponse,
    AIRetrievalQualitySummaryRequest,
    AIRetrievalQualitySummaryResponse,
)
from ai_api.storage import JsonlStore, resolve_storage_path


class AIRetrievalQualityRecordStore(Protocol):
    def append(
        self,
        record: AIRetrievalQualityRecord,
    ) -> AIRetrievalQualityRecord:
        """Append a retrieval quality record."""
        ...

    def list_records(self) -> list[AIRetrievalQualityRecord]:
        """List all stored retrieval quality records."""
        ...

    def count(self) -> int:
        """Return the number of stored retrieval quality records."""
        ...

    def clear(self) -> None:
        """Clear all stored retrieval quality records."""
        ...


class InMemoryAIRetrievalQualityRecordStore:
    def __init__(self) -> None:
        self._records: list[AIRetrievalQualityRecord] = []

    def append(
        self,
        record: AIRetrievalQualityRecord,
    ) -> AIRetrievalQualityRecord:
        self._records.append(record)

        return record

    def list_records(self) -> list[AIRetrievalQualityRecord]:
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()


class JsonlAIRetrievalQualityRecordStore:
    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        self._store = JsonlStore(
            file_path=file_path,
            record_type=AIRetrievalQualityRecord,
        )

    def append(
        self,
        record: AIRetrievalQualityRecord,
    ) -> AIRetrievalQualityRecord:
        return self._store.append(record)

    def list_records(self) -> list[AIRetrievalQualityRecord]:
        return self._store.list_records()

    def count(self) -> int:
        return self._store.count()

    def clear(self) -> None:
        self._store.clear()


class AIRetrievalQualityTelemetryService:
    def __init__(
        self,
        record_store: AIRetrievalQualityRecordStore | None = None,
        storage_backend: str = "memory",
    ) -> None:
        self.record_store = (
            record_store or InMemoryAIRetrievalQualityRecordStore()
        )
        self.storage_backend = storage_backend

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
    ) -> "AIRetrievalQualityTelemetryService":
        if settings.storage_backend == "local_jsonl":
            return cls(
                record_store=JsonlAIRetrievalQualityRecordStore(
                    file_path=resolve_storage_path(
                        settings=settings,
                        relative_path=settings.retrieval_quality_records_path,
                    ),
                ),
                storage_backend="local_jsonl",
            )

        return cls(
            record_store=InMemoryAIRetrievalQualityRecordStore(),
            storage_backend="memory",
        )

    def record(
        self,
        request: AIRetrievalQualityRecordRequest,
    ) -> AIRetrievalQualityRecord:
        precision_at_k = self._calculate_precision_at_k(request)
        source_coverage_score = self._calculate_source_coverage_score(request)
        quality_score = self._calculate_quality_score(
            precision_at_k=precision_at_k,
            source_coverage_score=source_coverage_score,
            average_similarity_score=request.average_similarity_score,
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
                "No retrieval quality risks detected.",
            ]

        record = AIRetrievalQualityRecord(
            record_id=str(uuid4()),
            component=request.component,
            operation=request.operation,
            query=request.query,
            status=status,
            requested_top_k=request.requested_top_k,
            retrieved_chunks_count=request.retrieved_chunks_count,
            relevant_chunks_count=request.relevant_chunks_count,
            citation_count=request.citation_count,
            unique_source_count=request.unique_source_count,
            required_source_count=request.required_source_count,
            matched_required_source_count=request.matched_required_source_count,
            precision_at_k=precision_at_k,
            source_coverage_score=source_coverage_score,
            quality_score=quality_score,
            min_similarity_score=request.min_similarity_score,
            max_similarity_score=request.max_similarity_score,
            average_similarity_score=request.average_similarity_score,
            expected_min_retrieved_chunks=request.expected_min_retrieved_chunks,
            expected_min_citations=request.expected_min_citations,
            min_quality_score=request.min_quality_score,
            risks=risks,
            recorded_at=self._utc_now(),
            run_id=request.run_id,
            trace_id=request.trace_id,
            metadata={
                "retrieval_quality_schema_version": "0.1.0",
                "scoring_mode": "caller_provided_retrieval_signals",
                "storage_backend": self.storage_backend,
                **request.metadata,
            },
        )

        return self.record_store.append(record)

    def list_records(
        self,
        component: str | None = None,
        operation: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> AIRetrievalQualityRecordsResponse:
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

        limited_records = filtered_records[-limit:]

        return AIRetrievalQualityRecordsResponse(
            records=limited_records,
            count=len(limited_records),
            metadata={
                "source": "ai-retrieval-quality-telemetry-service",
                "storage_backend": self.storage_backend,
                "total_stored_records": len(stored_records),
                "applied_filters": {
                    "component": component,
                    "operation": operation,
                    "status": status,
                    "limit": limit,
                },
            },
        )

    def summarize(
        self,
        request: AIRetrievalQualitySummaryRequest,
    ) -> AIRetrievalQualitySummaryResponse:
        records = (
            request.records
            if request.records is not None
            else self.record_store.list_records()
        )

        return AIRetrievalQualitySummaryResponse(
            record_count=len(records),
            passed_count=self._count_records(records, "passed"),
            warning_count=self._count_records(records, "warning"),
            failed_count=self._count_records(records, "failed"),
            total_retrieved_chunks=sum(
                record.retrieved_chunks_count
                for record in records
            ),
            total_relevant_chunks=sum(
                record.relevant_chunks_count or 0
                for record in records
            ),
            total_citations=sum(
                record.citation_count
                for record in records
            ),
            total_unique_sources=sum(
                record.unique_source_count
                for record in records
            ),
            average_precision_at_k=self._average_optional_metric(
                [
                    record.precision_at_k
                    for record in records
                ]
            ),
            average_source_coverage_score=self._average_optional_metric(
                [
                    record.source_coverage_score
                    for record in records
                ]
            ),
            average_quality_score=self._average_optional_metric(
                [
                    record.quality_score
                    for record in records
                ]
            ),
            average_similarity_score=self._average_optional_metric(
                [
                    record.average_similarity_score
                    for record in records
                ]
            ),
            component_coverage=self._build_coverage(
                [
                    record.component
                    for record in records
                ]
            ),
            operation_coverage=self._build_coverage(
                [
                    record.operation
                    for record in records
                ]
            ),
            risks=self._build_summary_risks(records),
            metadata={
                "summarizer": "ai-retrieval-quality-summary-v1",
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
    def _calculate_precision_at_k(
        request: AIRetrievalQualityRecordRequest,
    ) -> float | None:
        if request.relevant_chunks_count is None:
            return None

        if request.retrieved_chunks_count == 0:
            return None

        precision = request.relevant_chunks_count / request.retrieved_chunks_count

        return round(min(precision, 1.0), 4)

    @staticmethod
    def _calculate_source_coverage_score(
        request: AIRetrievalQualityRecordRequest,
    ) -> float | None:
        if (
            request.required_source_count is None
            or request.matched_required_source_count is None
        ):
            return None

        if request.required_source_count == 0:
            return None

        source_coverage = (
            request.matched_required_source_count / request.required_source_count
        )

        return round(min(source_coverage, 1.0), 4)

    @staticmethod
    def _calculate_quality_score(
        precision_at_k: float | None,
        source_coverage_score: float | None,
        average_similarity_score: float | None,
    ) -> float | None:
        available_scores = [
            score
            for score in [
                precision_at_k,
                source_coverage_score,
                average_similarity_score,
            ]
            if score is not None
        ]

        if not available_scores:
            return None

        return round(sum(available_scores) / len(available_scores), 4)

    @staticmethod
    def _build_failure_risks(
        request: AIRetrievalQualityRecordRequest,
        quality_score: float | None,
    ) -> list[str]:
        risks: list[str] = []

        if request.retrieved_chunks_count < request.expected_min_retrieved_chunks:
            risks.append(
                "Retrieved chunk count is below the expected minimum."
            )

        if quality_score is not None and quality_score < request.min_quality_score:
            risks.append(
                "Retrieval quality score is below the configured minimum."
            )

        return risks

    @staticmethod
    def _build_warning_risks(
        request: AIRetrievalQualityRecordRequest,
        quality_score: float | None,
    ) -> list[str]:
        risks: list[str] = []

        if request.citation_count < request.expected_min_citations:
            risks.append(
                "Citation count is below the expected minimum."
            )

        if quality_score is None:
            risks.append(
                "Retrieval quality score could not be calculated from the provided signals."
            )

        if request.average_similarity_score is None:
            risks.append(
                "Average similarity score was not provided."
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
        records: list[AIRetrievalQualityRecord],
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
        records: list[AIRetrievalQualityRecord],
    ) -> list[str]:
        if not records:
            return [
                "No retrieval quality records available.",
            ]

        failed_count = AIRetrievalQualityTelemetryService._count_records(
            records,
            "failed",
        )
        warning_count = AIRetrievalQualityTelemetryService._count_records(
            records,
            "warning",
        )

        risks: list[str] = []

        if failed_count > 0:
            risks.append(
                f"{failed_count} retrieval quality record(s) failed."
            )

        if warning_count > 0:
            risks.append(
                f"{warning_count} retrieval quality record(s) returned warning."
            )

        if not risks:
            risks.append(
                "No retrieval quality risks detected."
            )

        return risks

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
