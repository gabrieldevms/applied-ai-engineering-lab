import pytest
from pydantic import ValidationError
from ai_api.evals import (
    EvaluationTelemetryEvent,
    EvaluationTelemetryRecordRequest,
    EvaluationTelemetryService,
    EvaluationTelemetrySummaryRequest,
)


def test_evaluation_telemetry_service_should_record_event() -> None:
    service = EvaluationTelemetryService()

    event = service.record(
        EvaluationTelemetryRecordRequest(
            event_type="prompt_regression_run",
            component="evaluation",
            status="completed",
            source="unit-test",
            duration_ms=120.5,
            score=1.0,
            run_id="run-001",
            metadata={
                "suite_name": "prompt-regression-suite",
            },
        )
    )

    assert event.event_id
    assert event.event_type == "prompt_regression_run"
    assert event.component == "evaluation"
    assert event.status == "completed"
    assert event.source == "unit-test"
    assert event.duration_ms == 120.5
    assert event.score == 1.0
    assert event.run_id == "run-001"
    assert event.metadata["suite_name"] == "prompt-regression-suite"
    assert event.metadata["telemetry_schema_version"] == "0.1.0"


def test_evaluation_telemetry_service_should_list_events_with_filters() -> None:
    service = EvaluationTelemetryService()

    service.record(
        EvaluationTelemetryRecordRequest(
            event_type="prompt_regression_run",
            component="evaluation",
            status="completed",
            source="unit-test",
        )
    )
    service.record(
        EvaluationTelemetryRecordRequest(
            event_type="agent_run",
            component="agent",
            status="failed",
            source="unit-test",
            error_message="Agent failed.",
        )
    )

    response = service.list_events(
        component="agent",
    )

    assert response.count == 1
    assert response.events[0].event_type == "agent_run"
    assert response.events[0].component == "agent"
    assert response.events[0].status == "failed"


def test_evaluation_telemetry_service_should_summarize_stored_events() -> None:
    service = EvaluationTelemetryService()

    service.record(
        EvaluationTelemetryRecordRequest(
            event_type="prompt_regression_run",
            component="evaluation",
            status="completed",
            source="unit-test",
            duration_ms=100.0,
            score=1.0,
        )
    )
    service.record(
        EvaluationTelemetryRecordRequest(
            event_type="golden_dataset_run",
            component="evaluation",
            status="warning",
            source="unit-test",
            duration_ms=300.0,
            score=0.5,
        )
    )

    response = service.summarize(EvaluationTelemetrySummaryRequest())

    assert response.status == "warning"
    assert response.event_count == 2
    assert response.completed_count == 1
    assert response.warning_count == 1
    assert response.failed_count == 0
    assert response.average_score == 0.75
    assert response.average_duration_ms == 200.0
    assert response.event_type_coverage["prompt_regression_run"] == 1
    assert response.event_type_coverage["golden_dataset_run"] == 1
    assert response.component_coverage["evaluation"] == 2


def test_evaluation_telemetry_service_should_summarize_request_events() -> None:
    service = EvaluationTelemetryService()

    event = EvaluationTelemetryEvent(
        event_id="event-001",
        event_type="copilot_evaluation",
        component="multi_agent",
        status="completed",
        source="unit-test",
        recorded_at="2026-07-30T20:00:00+00:00",
        duration_ms=50.0,
        score=1.0,
    )

    response = service.summarize(
        EvaluationTelemetrySummaryRequest(
            events=[
                event,
            ],
            metadata={
                "source": "request-summary-test",
            },
        )
    )

    assert response.status == "passed"
    assert response.event_count == 1
    assert response.average_score == 1.0
    assert response.average_duration_ms == 50.0
    assert response.metadata["source"] == "request-summary-test"


def test_evaluation_telemetry_service_should_mark_summary_as_failed_when_any_event_failed() -> None:
    service = EvaluationTelemetryService()

    service.record(
        EvaluationTelemetryRecordRequest(
            event_type="tool_call",
            component="tool",
            status="failed",
            source="unit-test",
            error_message="Tool execution failed.",
        )
    )

    response = service.summarize(EvaluationTelemetrySummaryRequest())

    assert response.status == "failed"
    assert response.failed_count == 1
    assert response.risks == [
        "1 telemetry event(s) failed.",
    ]


def test_evaluation_telemetry_record_request_should_reject_invalid_score() -> None:
    with pytest.raises(ValidationError):
        EvaluationTelemetryRecordRequest(
            event_type="prompt_regression_run",
            component="evaluation",
            status="completed",
            source="unit-test",
            score=1.5,
        )


def test_evaluation_telemetry_record_request_should_reject_blank_source() -> None:
    with pytest.raises(ValidationError):
        EvaluationTelemetryRecordRequest(
            event_type="prompt_regression_run",
            component="evaluation",
            status="completed",
            source="   ",
        )
