from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Protocol
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from ai_api.storage import JsonlStore

BlockedToolCallCallerType = Literal[
    "frontend_console",
    "backend_service",
    "qa_agent",
    "data_analyst_agent",
    "multi_agent_copilot",
    "mcp_client",
    "evaluation_runner",
    "ci_pipeline",
    "future_authenticated_user",
    "future_admin_user",
]

BlockedToolCallEnvironment = Literal[
    "local",
    "test",
    "ci",
    "staging",
    "production",
]

BlockedToolCallRiskLevel = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


class BlockedToolCallTelemetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(min_length=1)
    caller_type: BlockedToolCallCallerType
    environment: BlockedToolCallEnvironment
    risk_level: BlockedToolCallRiskLevel
    authorization_status: str = Field(default="blocked")
    authorization_policy: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    violations: list[str] = Field(default_factory=list)
    prompt_injection_risk_level: str = "none"
    run_id: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BlockedToolCallTelemetryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    tool_name: str
    caller_type: BlockedToolCallCallerType
    environment: BlockedToolCallEnvironment
    risk_level: BlockedToolCallRiskLevel
    authorization_status: str
    authorization_policy: str
    reason: str
    violations: list[str]
    prompt_injection_risk_level: str
    run_id: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    recorded_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class BlockedToolCallTelemetryRecordsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[BlockedToolCallTelemetryRecord]
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class BlockedToolCallTelemetryRecordStore(Protocol):
    def append(
        self,
        record: BlockedToolCallTelemetryRecord,
    ) -> BlockedToolCallTelemetryRecord:
        """Append a blocked tool-call telemetry record."""
        ...

    def list_records(self) -> list[BlockedToolCallTelemetryRecord]:
        """List all stored blocked tool-call telemetry records."""
        ...

    def count(self) -> int:
        """Return the number of stored records."""
        ...

    def clear(self) -> None:
        """Clear all stored records."""
        ...


class InMemoryBlockedToolCallTelemetryRecordStore:
    def __init__(self) -> None:
        self._records: list[BlockedToolCallTelemetryRecord] = []

    def append(
        self,
        record: BlockedToolCallTelemetryRecord,
    ) -> BlockedToolCallTelemetryRecord:
        self._records.append(record)

        return record

    def list_records(self) -> list[BlockedToolCallTelemetryRecord]:
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()


class JsonlBlockedToolCallTelemetryRecordStore:
    def __init__(
        self,
        storage_path: Path,
    ) -> None:
        self._store = JsonlStore(
            storage_path,
            BlockedToolCallTelemetryRecord,
        )
    def append(
        self,
        record: BlockedToolCallTelemetryRecord,
    ) -> BlockedToolCallTelemetryRecord:
        return self._store.append(record)

    def list_records(self) -> list[BlockedToolCallTelemetryRecord]:
        return self._store.list_records()

    def count(self) -> int:
        return self._store.count()

    def clear(self) -> None:
        self._store.clear()


class BlockedToolCallTelemetryService:
    def __init__(
        self,
        record_store: BlockedToolCallTelemetryRecordStore | None = None,
        storage_backend: str = "memory",
    ) -> None:
        self.record_store = (
            record_store
            if record_store is not None
            else InMemoryBlockedToolCallTelemetryRecordStore()
        )
        self.storage_backend = storage_backend

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> "BlockedToolCallTelemetryService":
        if settings.storage_backend == "local_jsonl":
            return cls(
                record_store=JsonlBlockedToolCallTelemetryRecordStore(
                storage_path=(
                    Path(settings.storage_base_dir)
                    / settings.blocked_tool_call_records_path
                ),
            ),
                storage_backend=settings.storage_backend,
            )

        return cls(
            record_store=InMemoryBlockedToolCallTelemetryRecordStore(),
            storage_backend=settings.storage_backend,
        )

    def record(
        self,
        request: BlockedToolCallTelemetryRequest,
    ) -> BlockedToolCallTelemetryRecord:
        record = BlockedToolCallTelemetryRecord(
            record_id=f"blocked-tool-call-{uuid4()}",
            tool_name=request.tool_name,
            caller_type=request.caller_type,
            environment=request.environment,
            risk_level=request.risk_level,
            authorization_status="blocked",
            authorization_policy=request.authorization_policy,
            reason=request.reason,
            violations=request.violations,
            prompt_injection_risk_level=request.prompt_injection_risk_level,
            run_id=request.run_id,
            trace_id=request.trace_id,
            request_id=request.request_id,
            recorded_at=datetime.now(UTC).isoformat(),
            metadata={
                "telemetry_type": "blocked_tool_call",
                "storage_backend": self.storage_backend,
                "raw_arguments_stored": False,
                "sensitive_payload_stored": False,
                **request.metadata,
            },
        )

        return self.record_store.append(record)

    def list_records(
        self,
        limit: int = 100,
        tool_name: str | None = None,
        caller_type: str | None = None,
        environment: str | None = None,
        risk_level: str | None = None,
    ) -> BlockedToolCallTelemetryRecordsResponse:
        if limit < 1:
            raise ValueError("limit must be greater than or equal to 1")

        stored_records = self.record_store.list_records()
        filtered_records = list(stored_records)

        if tool_name is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.tool_name == tool_name
            ]

        if caller_type is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.caller_type == caller_type
            ]

        if environment is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.environment == environment
            ]

        if risk_level is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.risk_level == risk_level
            ]

        filtered_records = sorted(
            filtered_records,
            key=lambda record: record.recorded_at,
            reverse=True,
        )

        limited_records = filtered_records[:limit]

        return BlockedToolCallTelemetryRecordsResponse(
            records=limited_records,
            count=len(limited_records),
            metadata={
                "telemetry_type": "blocked_tool_call",
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
