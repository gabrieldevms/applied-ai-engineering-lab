from fastapi.testclient import TestClient
from ai_api.main import app


client = TestClient(app)


def test_blocked_tool_call_telemetry_endpoint_should_return_records_response() -> None:
    response = client.get("/security/blocked-tool-calls?limit=10")

    assert response.status_code == 200

    body = response.json()

    assert "records" in body
    assert "count" in body
    assert "metadata" in body
    assert body["metadata"]["telemetry_type"] == "blocked_tool_call"
    assert body["metadata"]["limit"] == 10


def test_blocked_tool_call_telemetry_endpoint_should_reject_invalid_limit() -> None:
    response = client.get("/security/blocked-tool-calls?limit=0")

    assert response.status_code == 422