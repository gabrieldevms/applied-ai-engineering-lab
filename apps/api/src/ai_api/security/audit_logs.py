from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Protocol
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from ai_api.storage import JsonlStore


AuditEventType = Literal[
    "tool_authorization_allowed",
    "tool_authorization_blocked",
    "tool_execution_started",
    "tool_execution_completed",
    "tool_execution_failed",
    "prompt_injection_detected",
    "prompt_injection_blocked",
    "human_approval_requested",
    "human_approval_granted",
    "human_approval_rejected",
    "sensitive_data_detected",
    "provider_configuration_accessed",
    "provider_configuration_changed",
    "mcp_tool_called",
    "mcp_tool_blocked",
    "authentication_succeeded",
    "authentication_failed",
    "authorization_failed",
    "policy_violation_detected",
]

AuditEventSeverity = Literal[
    "info",
    "warning",
    "high",
    "critical",
]

AuditEventStatus = Literal[
    "allowed",
    "blocked",
    "completed",
    "failed",
    "requested",
    "granted",
    "rejected",
    "detected",
    "redacted",
]

AuditEnvironment = Literal[
    "local",
    "test",
    "ci",
    "staging",
    "production",
]

AuditActorType = Literal[
    "system",
    "frontend_user",
    "backend_service",
    "agent",
    "mcp_client",
    "ci_pipeline",
    "future_authenticated_user",
    "future_admin_user",
]

AuditCallerType = Literal[
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

AuditTargetType = Literal[
    "tool",
    "agent",
    "workflow",
    "provider",
    "mcp_tool",
    "document",
    "dataset",
    "policy",
    "configuration",
    "approval_request",
]

AuditRiskLevel = Literal[
    "none",
    "low",
    "medium",
    "high",
    "critical",
]


class AuditActor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_type: AuditActorType
    actor_id: str = Field(min_length=1)
    display_name: str | None = None


class AuditCaller(BaseModel):
    model_config = ConfigDict(extra="forbid")

    caller_type: AuditCallerType
    caller_id: str | None = None


class AuditTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: AuditTargetType
    target_id: str = Field(min_length=1)
    target_name: str | None = None


class AuditRunContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    session_id: str | None = None


class AuditPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_name: str = Field(min_length=1)
    policy_version: str = "v1"
    decision: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    violations: list[str] = Field(default_factory=list)


class AuditRisk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: AuditRiskLevel = "none"
    risk_reasons: list[str] = Field(default_factory=list)
    prompt_injection_risk_level: str | None = None
    sensitive_data_detected: bool = False


class AuditRedaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    redacted: bool = False
    redacted_fields: list[str] = Field(default_factory=list)


class AuditLogEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: AuditEventType
    severity: AuditEventSeverity
    status: AuditEventStatus
    component: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    environment: AuditEnvironment = "local"
    actor: AuditActor
    caller: AuditCaller
    target: AuditTarget
    run_context: AuditRunContext = Field(default_factory=AuditRunContext)
    policy: AuditPolicy
    risk: AuditRisk = Field(default_factory=AuditRisk)
    metadata: dict[str, Any] = Field(default_factory=dict)
    redaction: AuditRedaction = Field(default_factory=AuditRedaction)


class AuditLogEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_event_id: str
    event_type: AuditEventType
    severity: AuditEventSeverity
    status: AuditEventStatus
    occurred_at: str
    component: str
    operation: str
    environment: AuditEnvironment
    actor: AuditActor
    caller: AuditCaller
    target: AuditTarget
    run_context: AuditRunContext = Field(default_factory=AuditRunContext)
    policy: AuditPolicy
    risk: AuditRisk = Field(default_factory=AuditRisk)
    metadata: dict[str, Any] = Field(default_factory=dict)
    redaction: AuditRedaction = Field(default_factory=AuditRedaction)


class AuditLogEventsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[AuditLogEvent]
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogEventStore(Protocol):
    def append(self, event: AuditLogEvent) -> AuditLogEvent:
        """Append an audit log event."""
        ...

    def list_records(self) -> list[AuditLogEvent]:
        """List all stored audit log events."""
        ...

    def count(self) -> int:
        """Return the number of stored audit log events."""
        ...

    def clear(self) -> None:
        """Clear all stored audit log events."""
        ...


class InMemoryAuditLogEventStore:
    def __init__(self) -> None:
        self._events: list[AuditLogEvent] = []

    def append(self, event: AuditLogEvent) -> AuditLogEvent:
        self._events.append(event)

        return event

    def list_records(self) -> list[AuditLogEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()


class JsonlAuditLogEventStore:
    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        self._store = JsonlStore(
            file_path,
            AuditLogEvent,
        )

    def append(self, event: AuditLogEvent) -> AuditLogEvent:
        return self._store.append(event)

    def list_records(self) -> list[AuditLogEvent]:
        return self._store.list_records()

    def count(self) -> int:
        return self._store.count()

    def clear(self) -> None:
        self._store.clear()


class AuditLogService:
    def __init__(
        self,
        event_store: AuditLogEventStore | None = None,
        storage_backend: str = "memory",
    ) -> None:
        self.event_store = (
            event_store
            if event_store is not None
            else InMemoryAuditLogEventStore()
        )
        self.storage_backend = storage_backend

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> "AuditLogService":
        if settings.storage_backend == "local_jsonl":
            return cls(
                event_store=JsonlAuditLogEventStore(
                    file_path=(
                        Path(settings.storage_base_dir)
                        / settings.audit_events_path
                    ),
                ),
                storage_backend=settings.storage_backend,
            )

        return cls(
            event_store=InMemoryAuditLogEventStore(),
            storage_backend=settings.storage_backend,
        )

    def record(
        self,
        request: AuditLogEventRequest,
    ) -> AuditLogEvent:
        event = AuditLogEvent(
            audit_event_id=f"audit-event-{uuid4()}",
            event_type=request.event_type,
            severity=request.severity,
            status=request.status,
            occurred_at=datetime.now(UTC).isoformat(),
            component=request.component,
            operation=request.operation,
            environment=request.environment,
            actor=request.actor,
            caller=request.caller,
            target=request.target,
            run_context=request.run_context,
            policy=request.policy,
            risk=request.risk,
            metadata={
                "log_type": "security_audit",
                "storage_backend": self.storage_backend,
                "raw_payload_stored": False,
                "sensitive_payload_stored": False,
                **request.metadata,
            },
            redaction=request.redaction,
        )

        return self.event_store.append(event)

    def list_events(
        self,
        limit: int = 100,
        event_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        component: str | None = None,
        operation: str | None = None,
        environment: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        run_id: str | None = None,
    ) -> AuditLogEventsResponse:
        if limit < 1:
            raise ValueError("limit must be greater than or equal to 1")

        stored_events = self.event_store.list_records()
        filtered_events = list(stored_events)

        if event_type is not None:
            filtered_events = [
                event for event in filtered_events if event.event_type == event_type
            ]

        if severity is not None:
            filtered_events = [
                event for event in filtered_events if event.severity == severity
            ]

        if status is not None:
            filtered_events = [
                event for event in filtered_events if event.status == status
            ]

        if component is not None:
            filtered_events = [
                event for event in filtered_events if event.component == component
            ]

        if operation is not None:
            filtered_events = [
                event for event in filtered_events if event.operation == operation
            ]

        if environment is not None:
            filtered_events = [
                event for event in filtered_events if event.environment == environment
            ]

        if target_type is not None:
            filtered_events = [
                event
                for event in filtered_events
                if event.target.target_type == target_type
            ]

        if target_id is not None:
            filtered_events = [
                event for event in filtered_events if event.target.target_id == target_id
            ]

        if run_id is not None:
            filtered_events = [
                event for event in filtered_events if event.run_context.run_id == run_id
            ]

        filtered_events = sorted(
            filtered_events,
            key=lambda event: event.occurred_at,
            reverse=True,
        )

        limited_events = filtered_events[:limit]

        return AuditLogEventsResponse(
            events=limited_events,
            count=len(limited_events),
            metadata={
                "log_type": "security_audit",
                "storage_backend": self.storage_backend,
                "total_stored_events": len(stored_events),
                "total_filtered_events": len(filtered_events),
                "limit": limit,
            },
        )

    def count(self) -> int:
        return self.event_store.count()

    def clear(self) -> None:
        self.event_store.clear()
