from fastapi.testclient import TestClient

from ai_api.main import app


client = TestClient(app)


def test_health_check_should_return_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_should_return_structured_response() -> None:
    payload = {
        "text": "Applied AI Engineering is about building reliable AI systems.",
        "language": "en",
    }

    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["original_text"] == payload["text"]
    assert body["language"] == "en"
    assert body["word_count"] == 9
    assert body["character_count"] == len(payload["text"])
    assert "summary" in body


def test_analyze_should_validate_empty_text() -> None:
    payload = {
        "text": "",
        "language": "en",
    }

    response = client.post("/analyze", json=payload)

    assert response.status_code == 422
