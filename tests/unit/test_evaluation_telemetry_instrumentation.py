import pytest
from ai_api.evals import (
    EvaluationTelemetryInstrumentationService,
    EvaluationTelemetryService,
)


class StubSuccessfulResult:
    status = "passed"
    score = 0.9


class StubWarningResult:
    status = "warning"
    score = 0.5


class StubCountBasedResult:
    status = "passed"
    passed_count = 3
    case_count = 4


def test_evaluation_telemetry_instrumentation_should_record_completed_event() -> None:
    telemetry_service = EvaluationTelemetryService()
    instrumentation_service = EvaluationTelemetryInstrumentationService(
        telemetry_service=telemetry_service,
    )

    result = instrumentation_service.instrument(
        event_type="prompt_regression_run",
        component="evaluation",
        source="unit-test",
        operation=lambda: StubSuccessfulResult(),
        run_id="run-001",
        metadata={
            "suite_name": "prompt-regression-suite",
        },
    )

    events_response = telemetry_service.list_events()

    assert isinstance(result, StubSuccessfulResult)
    assert events_response.count == 1

    event = events_response.events[0]

    assert event.event_type == "prompt_regression_run"
    assert event.component == "evaluation"
    assert event.status == "completed"
    assert event.source == "unit-test"
    assert event.score == 0.9
    assert event.run_id == "run-001"
    assert event.started_at is not None
    assert event.finished_at is not None
    assert event.duration_ms is not None
    assert event.duration_ms >= 0
    assert event.metadata["instrumentation"] == (
        "latency-error-telemetry-instrumentation-v1"
    )
    assert event.metadata["result_status"] == "passed"
    assert event.metadata["suite_name"] == "prompt-regression-suite"


def test_evaluation_telemetry_instrumentation_should_record_warning_event() -> None:
    telemetry_service = EvaluationTelemetryService()
    instrumentation_service = EvaluationTelemetryInstrumentationService(
        telemetry_service=telemetry_service,
    )

    instrumentation_service.instrument(
        event_type="golden_dataset_run",
        component="evaluation",
        source="unit-test",
        operation=lambda: StubWarningResult(),
    )

    events_response = telemetry_service.list_events()

    assert events_response.count == 1
    assert events_response.events[0].status == "warning"
    assert events_response.events[0].score == 0.5


def test_evaluation_telemetry_instrumentation_should_extract_count_based_score() -> None:
    telemetry_service = EvaluationTelemetryService()
    instrumentation_service = EvaluationTelemetryInstrumentationService(
        telemetry_service=telemetry_service,
    )

    instrumentation_service.instrument(
        event_type="prompt_regression_run",
        component="evaluation",
        source="unit-test",
        operation=lambda: StubCountBasedResult(),
    )

    events_response = telemetry_service.list_events()

    assert events_response.count == 1
    assert events_response.events[0].score == 0.75


def test_evaluation_telemetry_instrumentation_should_record_failed_event_and_reraise() -> None:
    telemetry_service = EvaluationTelemetryService()
    instrumentation_service = EvaluationTelemetryInstrumentationService(
        telemetry_service=telemetry_service,
    )

    def failing_operation() -> StubSuccessfulResult:
        raise RuntimeError("Synthetic failure.")

    with pytest.raises(RuntimeError):
        instrumentation_service.instrument(
            event_type="report_aggregation",
            component="evaluation",
            source="unit-test",
            operation=failing_operation,
            run_id="run-failed",
        )

    events_response = telemetry_service.list_events()

    assert events_response.count == 1

    event = events_response.events[0]

    assert event.status == "failed"
    assert event.score == 0.0
    assert event.run_id == "run-failed"
    assert event.error_message == "Synthetic failure."
    assert event.metadata["error_type"] == "RuntimeError"
    assert event.duration_ms is not None
    assert event.duration_ms >= 0
