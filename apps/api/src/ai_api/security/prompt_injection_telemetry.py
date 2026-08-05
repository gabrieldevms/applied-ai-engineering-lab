from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from ai_api.security.schemas import (
    PromptInjectionRecommendedAction,
    PromptInjectionRiskLevel,
)
from ai_api.storage import JsonlStore


class PromptInjectionTelemetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: PromptInjectionRiskLevel
    recommended_action: PromptInjectionRecommendedAction
    is_blocking_required: bool
    detected_patterns: list[str] = Field(default_factory=list)
    risk_reasons: list[str] = Field(default_factory=list)
    input_source: str = Field(min_length=1)
    workflow: str | None = None
    inspected_character_count: int = Field(ge=0)
    run_id: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptInjectionTelemetryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    risk_level: PromptInjectionRiskLevel
    recommended_action: PromptInjectionRecommendedAction
    is_blocking_required: bool
    detected_patterns: list[str]
    risk_reasons: list[str]
    input_source: str
    workflow: str | None = None
    inspected_character_count: int
    run_id: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    recorded_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptInjectionTelemetryRecordsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[PromptInjectionTelemetryRecord]
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptInjectionTelemetryRecordStore(Protocol):
    def append(
        self,
        record: PromptInjectionTelemetryRecord,
    ) -> PromptInjectionTelemetryRecord:
        """Append a prompt injection telemetry record."""
        ...

    def list_records(self) -> list[PromptInjectionTelemetryRecord]:
        """List all stored prompt injection telemetry records."""
        ...

    def count(self) -> int:
        """Return the number of stored records."""
        ...

    def clear(self) -> None:
        """Clear all stored records."""
        ...


class InMemoryPromptInjectionTelemetryRecordStore:
    def __init__(self) -> None:
        self._records: list[PromptInjectionTelemetryRecord] = []

    def append(
        self,
        record: PromptInjectionTelemetryRecord,
    ) -> PromptInjectionTelemetryRecord:
        self._records.append(record)

        return record

    def list_records(self) -> list[PromptInjectionTelemetryRecord]:
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()


class JsonlPromptInjectionTelemetryRecordStore:
    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        self._store = JsonlStore(
            file_path,
            PromptInjectionTelemetryRecord,
        )

    def append(
        self,
        record: PromptInjectionTelemetryRecord,
    ) -> PromptInjectionTelemetryRecord:
        return self._store.append(record)

    def list_records(self) -> list[PromptInjectionTelemetryRecord]:
        return self._store.list_records()

    def count(self) -> int:
        return self._store.count()

    def clear(self) -> None:
        self._store.clear()


class PromptInjectionTelemetryService:
    def __init__(
        self,
        record_store: PromptInjectionTelemetryRecordStore | None = None,
        storage_backend: str = "memory",
    ) -> None:
        self.record_store = (
            record_store
            if record_store is not None
            else InMemoryPromptInjectionTelemetryRecordStore()
        )
        self.storage_backend = storage_backend

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> "PromptInjectionTelemetryService":
        if settings.storage_backend == "local_jsonl":
            return cls(
                record_store=JsonlPromptInjectionTelemetryRecordStore(
                    file_path=(
                        Path(settings.storage_base_dir)
                        / settings.prompt_injection_records_path
                    ),
                ),
                storage_backend=settings.storage_backend,
            )

        return cls(
            record_store=InMemoryPromptInjectionTelemetryRecordStore(),
            storage_backend=settings.storage_backend,
        )

    def record(
        self,
        request: PromptInjectionTelemetryRequest,
    ) -> PromptInjectionTelemetryRecord:
        record = PromptInjectionTelemetryRecord(
            record_id=f"prompt-injection-{uuid4()}",
            risk_level=request.risk_level,
            recommended_action=request.recommended_action,
            is_blocking_required=request.is_blocking_required,
            detected_patterns=request.detected_patterns,
            risk_reasons=request.risk_reasons,
            input_source=request.input_source,
            workflow=request.workflow,
            inspected_character_count=request.inspected_character_count,
            run_id=request.run_id,
            trace_id=request.trace_id,
            request_id=request.request_id,
            recorded_at=datetime.now(UTC).isoformat(),
            metadata={
                "telemetry_type": "prompt_injection",
                "storage_backend": self.storage_backend,
                "raw_input_stored": False,
                "sensitive_payload_stored": False,
                **request.metadata,
            },
        )

        return self.record_store.append(record)

    def record_if_relevant(
        self,
        request: PromptInjectionTelemetryRequest,
    ) -> PromptInjectionTelemetryRecord | None:
        if not _should_record_prompt_injection_telemetry(request):
            return None

        return self.record(request)

    def list_records(
        self,
        limit: int = 100,
        risk_level: str | None = None,
        recommended_action: str | None = None,
        input_source: str | None = None,
        workflow: str | None = None,
    ) -> PromptInjectionTelemetryRecordsResponse:
        if limit < 1:
            raise ValueError("limit must be greater than or equal to 1")

        stored_records = self.record_store.list_records()
        filtered_records = list(stored_records)

        if risk_level is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.risk_level == risk_level
            ]

        if recommended_action is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.recommended_action == recommended_action
            ]

        if input_source is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.input_source == input_source
            ]

        if workflow is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.workflow == workflow
            ]

        filtered_records = sorted(
            filtered_records,
            key=lambda record: record.recorded_at,
            reverse=True,
        )

        limited_records = filtered_records[:limit]

        return PromptInjectionTelemetryRecordsResponse(
            records=limited_records,
            count=len(limited_records),
            metadata={
                "telemetry_type": "prompt_injection",
                "storage_backend": self.storage_backend,
                "total_stored_records": len(stored_records),
                "total_filtered_records": len(filtered_records),
                "limit": limit,
            },
        )

    def count(self) -> int:
        return self.record_store.count()

    def clear(self) -> None:
        self.record_store.clear()


def _should_record_prompt_injection_telemetry(
    request: PromptInjectionTelemetryRequest,
) -> bool:
    return (
        request.risk_level in {"medium", "high"}
        or request.recommended_action in {"require_review", "block"}
        or request.is_blocking_required
    )
