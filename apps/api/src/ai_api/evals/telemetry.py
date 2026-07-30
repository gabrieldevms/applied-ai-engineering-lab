from datetime import UTC, datetime
from uuid import uuid4
from ai_api.evals.schemas import (
    EvaluationTelemetryEvent,
    EvaluationTelemetryEventsResponse,
    EvaluationTelemetryRecordRequest,
    EvaluationTelemetrySummaryRequest,
    EvaluationTelemetrySummaryResponse,
)


class EvaluationTelemetryService:
    def __init__(self) -> None:
        self._events: list[EvaluationTelemetryEvent] = []

    def record(
        self,
        request: EvaluationTelemetryRecordRequest,
    ) -> EvaluationTelemetryEvent:
        event = EvaluationTelemetryEvent(
            event_id=str(uuid4()),
            event_type=request.event_type,
            component=request.component,
            status=request.status,
            source=request.source,
            recorded_at=self._utc_now(),
            started_at=request.started_at,
            finished_at=request.finished_at,
            duration_ms=request.duration_ms,
            score=request.score,
            run_id=request.run_id,
            scenario_id=request.scenario_id,
            case_id=request.case_id,
            error_message=request.error_message,
            metadata={
                "telemetry_schema_version": "0.1.0",
                **request.metadata,
            },
        )

        self._events.append(event)

        return event

    def list_events(
        self,
        event_type: str | None = None,
        component: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> EvaluationTelemetryEventsResponse:
        filtered_events = self._events

        if event_type is not None:
            filtered_events = [
                event
                for event in filtered_events
                if event.event_type == event_type
            ]

        if component is not None:
            filtered_events = [
                event
                for event in filtered_events
                if event.component == component
            ]

        if status is not None:
            filtered_events = [
                event
                for event in filtered_events
                if event.status == status
            ]

        limited_events = filtered_events[-limit:]

        return EvaluationTelemetryEventsResponse(
            events=limited_events,
            count=len(limited_events),
            metadata={
                "source": "evaluation-telemetry-service",
                "total_stored_events": len(self._events),
                "applied_filters": {
                    "event_type": event_type,
                    "component": component,
                    "status": status,
                    "limit": limit,
                },
            },
        )

    def summarize(
        self,
        request: EvaluationTelemetrySummaryRequest,
    ) -> EvaluationTelemetrySummaryResponse:
        events = request.events if request.events is not None else self._events

        completed_count = self._count_events(events, "completed")
        warning_count = self._count_events(events, "warning")
        failed_count = self._count_events(events, "failed")
        skipped_count = self._count_events(events, "skipped")

        status = self._resolve_summary_status(
            failed_count=failed_count,
            warning_count=warning_count,
            skipped_count=skipped_count,
        )

        return EvaluationTelemetrySummaryResponse(
            status=status,
            event_count=len(events),
            completed_count=completed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            average_score=self._average_score(events),
            average_duration_ms=self._average_duration(events),
            event_type_coverage=self._build_event_type_coverage(events),
            component_coverage=self._build_component_coverage(events),
            risks=self._build_risks(
                failed_count=failed_count,
                warning_count=warning_count,
                skipped_count=skipped_count,
            ),
            metadata={
                "summarizer": "evaluation-telemetry-summarizer-v1",
                "source": "stored_events"
                if request.events is None
                else "request_events",
                **request.metadata,
            },
        )

    def clear(self) -> None:
        self._events.clear()

    @staticmethod
    def _resolve_summary_status(
        failed_count: int,
        warning_count: int,
        skipped_count: int,
    ) -> str:
        if failed_count > 0:
            return "failed"

        if warning_count > 0 or skipped_count > 0:
            return "warning"

        return "passed"

    @staticmethod
    def _average_score(
        events: list[EvaluationTelemetryEvent],
    ) -> float | None:
        scores = [
            event.score
            for event in events
            if event.score is not None
        ]

        if not scores:
            return None

        return round(sum(scores) / len(scores), 4)

    @staticmethod
    def _average_duration(
        events: list[EvaluationTelemetryEvent],
    ) -> float | None:
        durations = [
            event.duration_ms
            for event in events
            if event.duration_ms is not None
        ]

        if not durations:
            return None

        return round(sum(durations) / len(durations), 4)

    @staticmethod
    def _build_event_type_coverage(
        events: list[EvaluationTelemetryEvent],
    ) -> dict[str, int]:
        coverage: dict[str, int] = {}

        for event in events:
            coverage[event.event_type] = coverage.get(event.event_type, 0) + 1

        return coverage

    @staticmethod
    def _build_component_coverage(
        events: list[EvaluationTelemetryEvent],
    ) -> dict[str, int]:
        coverage: dict[str, int] = {}

        for event in events:
            coverage[event.component] = coverage.get(event.component, 0) + 1

        return coverage

    @staticmethod
    def _build_risks(
        failed_count: int,
        warning_count: int,
        skipped_count: int,
    ) -> list[str]:
        risks: list[str] = []

        if failed_count > 0:
            risks.append(
                f"{failed_count} telemetry event(s) failed."
            )

        if warning_count > 0:
            risks.append(
                f"{warning_count} telemetry event(s) returned warning."
            )

        if skipped_count > 0:
            risks.append(
                f"{skipped_count} telemetry event(s) were skipped."
            )

        if not risks:
            risks.append(
                "No telemetry risks detected."
            )

        return risks

    @staticmethod
    def _count_events(
        events: list[EvaluationTelemetryEvent],
        status: str,
    ) -> int:
        return len(
            [
                event
                for event in events
                if event.status == status
            ]
        )

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
