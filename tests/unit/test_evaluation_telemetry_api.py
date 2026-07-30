from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    EvaluationTelemetryEvent,
    EvaluationTelemetryEventsResponse,
    EvaluationTelemetrySummaryResponse,
    get_evaluation_telemetry_service,
)
from ai_api.main import app


class StubEvaluationTelemetryService:
    def __init__(self) -> None:
        self.last_record_request: Any | None = None
        self.last_summary_request: Any | None = None

    def record(self, request: Any) -> EvaluationTelemetryEvent:
        self.last_record_request = request

        return EvaluationTelemetryEvent(
            event_id="event-001",
            event_type=request.event_type,
            component=request.component,
            status=request.status,
            source=request.source,
            recorded_at="2026-07-30T20:00:00+00:00",
            duration_ms=request.duration_ms,
            score=request.score,
            metadata={
                "source": "stub-telemetry-service",
            },
        )

    def list_events(
        self,
        event_type: str | None = None,
        component: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> EvaluationTelemetryEventsResponse:
        return EvaluationTelemetryEventsResponse(
            events=[
                EvaluationTelemetryEvent(
                    event_id="event-001",
                    event_type="prompt_regression_run",
                    component="evaluation",
                    status="completed",
                    source="unit-test",
                    recorded_at="2026-07-30T20:00:00+00:00",
                    duration_ms=100.0,
                    score=1.0,
                )
            ],
            count=1,
            metadata={
                "event_type": event_type,
                "component": component,
                "status": status,
                "limit": limit,
            },
        )

    def summarize(self, request: Any) -> EvaluationTelemetrySummaryResponse:
        self.last_summary_request = request

        return EvaluationTelemetrySummaryResponse(
            status="passed",
            event_count=1,
            completed_count=1,
            warning_count=0,
            failed_count=0,
            skipped_count=0,
            average_score=1.0,
            average_duration_ms=100.0,
            event_type_coverage={
                "prompt_regression_run": 1,
            },
            component_coverage={
                "evaluation": 1,
            },
            risks=[
                "No telemetry risks detected.",
            ],
            metadata={
                "source": "stub-telemetry-service",
            },
        )


def test_record_evaluation_telemetry_event_endpoint_should_return_event() -> None:
    service = StubEvaluationTelemetryService()
    app.dependency_overrides[
        get_evaluation_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/telemetry/events",
            json={
                "event_type": "prompt_regression_run",
                "component": "evaluation",
                "status": "completed",
                "source": "api-test",
                "duration_ms": 100.0,
                "score": 1.0,
                "metadata": {
                    "suite_name": "prompt-regression-suite",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["event_id"] == "event-001"
        assert body["event_type"] == "prompt_regression_run"
        assert body["component"] == "evaluation"
        assert body["status"] == "completed"
        assert body["source"] == "api-test"
        assert body["score"] == 1.0
        assert body["metadata"]["source"] == "stub-telemetry-service"

        assert service.last_record_request is not None
        assert service.last_record_request.source == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_list_evaluation_telemetry_events_endpoint_should_return_events() -> None:
    app.dependency_overrides[
        get_evaluation_telemetry_service
    ] = lambda: StubEvaluationTelemetryService()

    try:
        client = TestClient(app)

        response = client.get(
            "/evals/telemetry/events?component=evaluation&limit=10"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["count"] == 1
        assert body["events"][0]["event_type"] == "prompt_regression_run"
        assert body["metadata"]["component"] == "evaluation"
        assert body["metadata"]["limit"] == 10
    finally:
        app.dependency_overrides.clear()


def test_summarize_evaluation_telemetry_endpoint_should_return_summary() -> None:
    service = StubEvaluationTelemetryService()
    app.dependency_overrides[
        get_evaluation_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/telemetry/summary",
            json={
                "events": [
                    {
                        "event_id": "event-001",
                        "event_type": "prompt_regression_run",
                        "component": "evaluation",
                        "status": "completed",
                        "source": "api-test",
                        "recorded_at": "2026-07-30T20:00:00+00:00",
                        "duration_ms": 100.0,
                        "score": 1.0,
                    }
                ],
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["event_count"] == 1
        assert body["average_score"] == 1.0
        assert body["metadata"]["source"] == "stub-telemetry-service"

        assert service.last_summary_request is not None
        assert service.last_summary_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_summarize_stored_evaluation_telemetry_endpoint_should_return_summary() -> None:
    app.dependency_overrides[
        get_evaluation_telemetry_service
    ] = lambda: StubEvaluationTelemetryService()

    try:
        client = TestClient(app)

        response = client.get("/evals/telemetry/summary")

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["event_count"] == 1
        assert body["completed_count"] == 1
    finally:
        app.dependency_overrides.clear()


def test_record_evaluation_telemetry_event_endpoint_should_reject_invalid_status() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/telemetry/events",
        json={
            "event_type": "prompt_regression_run",
            "component": "evaluation",
            "status": "invalid_status",
            "source": "api-test",
        },
    )

    assert response.status_code == 422
