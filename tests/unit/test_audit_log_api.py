from fastapi.testclient import TestClient
from ai_api.main import app


client = TestClient(app)


def test_audit_log_events_endpoint_should_return_events_response() -> None:
    response = client.get("/security/audit/events?limit=10")

    assert response.status_code == 200

    body = response.json()

    assert "events" in body
    assert "count" in body
    assert "metadata" in body
    assert body["metadata"]["log_type"] == "security_audit"
    assert body["metadata"]["limit"] == 10


def test_audit_log_events_endpoint_should_support_filters() -> None:
    response = client.get(
        "/security/audit/events"
        "?event_type=tool_authorization_blocked"
        "&severity=high"
        "&status=blocked"
        "&limit=10"
    )

    assert response.status_code == 200

    body = response.json()

    assert "events" in body
    assert "count" in body
    assert "metadata" in body


def test_audit_log_events_endpoint_should_reject_invalid_limit() -> None:
    response = client.get("/security/audit/events?limit=0")

    assert response.status_code == 422
