from pathlib import Path

from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from ai_api.agents import AgentExecutionLogService, get_agent_execution_log_service
from ai_api.config import Settings
from ai_api.main import app
from ai_api.operational_metrics import OperationalMetrics
from ai_api.readiness import evaluate_readiness, get_readiness_report


client = TestClient(app)


def _sample_value(name: str, labels: dict[str, str]) -> float:
    response = client.get("/metrics")
    for family in text_string_to_metric_families(response.text):
        for sample in family.samples:
            if sample.name == name and sample.labels == labels:
                return sample.value
    return 0


def test_metrics_endpoint_exposes_prometheus_text_without_counting_scrapes() -> None:
    labels = {"method": "GET", "route": "/health", "status_class": "2xx"}
    before = _sample_value("ai_quality_http_requests_total", labels)

    health = client.get("/health")
    first_scrape = client.get("/metrics")
    after = _sample_value("ai_quality_http_requests_total", labels)

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert first_scrape.status_code == 200
    assert first_scrape.headers["content-type"].startswith("text/plain")
    assert "ai_quality_http_request_duration_seconds_bucket" in first_scrape.text
    assert after == before + 1
    assert 'route="/metrics"' not in first_scrape.text
    assert "/metrics" not in client.get("/openapi.json").json()["paths"]


def test_metrics_use_bounded_status_and_never_expose_raw_paths_or_queries() -> None:
    secret = "private-run-identifier"
    app.dependency_overrides[get_agent_execution_log_service] = (
        lambda: AgentExecutionLogService()
    )
    try:
        matched = client.get(f"/agents/logs/{secret}?token={secret}")
    finally:
        app.dependency_overrides.clear()
    unmatched = client.get(f"/unknown/{secret}?token={secret}")
    invalid = client.post("/analyze", json={"text": "", "language": "en"})
    metrics = client.get("/metrics").text

    assert matched.status_code == 200
    assert unmatched.status_code == 404
    assert invalid.status_code == 422
    assert _sample_value(
        "ai_quality_http_requests_total",
        {"method": "GET", "route": "/agents/logs/{run_id}", "status_class": "2xx"},
    ) >= 1
    assert _sample_value(
        "ai_quality_http_requests_total",
        {"method": "GET", "route": "unmatched", "status_class": "4xx"},
    ) >= 1
    assert _sample_value(
        "ai_quality_http_requests_total",
        {"method": "POST", "route": "/analyze", "status_class": "4xx"},
    ) >= 1
    assert secret not in metrics
    assert "token=" not in metrics


def test_readiness_metric_tracks_existing_ready_response(tmp_path: Path) -> None:
    app.dependency_overrides[get_readiness_report] = lambda: evaluate_readiness(
        lambda: Settings(_env_file=None, storage_base_dir=str(tmp_path))
    )
    try:
        ready = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert _sample_value("ai_quality_readiness", {}) == 1

    app.dependency_overrides[get_readiness_report] = lambda: evaluate_readiness(
        lambda: Settings(_env_file=None, storage_base_dir=str(tmp_path / "missing"))
    )
    try:
        not_ready = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert not_ready.status_code == 503
    assert not_ready.json()["status"] == "not_ready"
    assert _sample_value("ai_quality_readiness", {}) == 0


def test_status_class_and_method_labels_are_bounded() -> None:
    assert OperationalMetrics.status_class(503) == "5xx"
    assert OperationalMetrics.status_class(422) == "4xx"
    assert OperationalMetrics.status_class(999) == "other"
    assert OperationalMetrics.method_label("SENSITIVE-CUSTOM-METHOD") == "OTHER"


def test_unhandled_errors_are_classified_without_changing_api_response() -> None:
    def broken_readiness():
        raise RuntimeError("forced test failure")

    app.dependency_overrides[get_readiness_report] = broken_readiness
    try:
        response = TestClient(app, raise_server_exceptions=False).get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json()["error"]["type"] == "internal_server_error"
    assert _sample_value(
        "ai_quality_http_requests_total",
        {"method": "GET", "route": "/ready", "status_class": "5xx"},
    ) >= 1
