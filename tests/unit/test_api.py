from fastapi.testclient import TestClient
from ai_api.llm import FakeLLMProvider
from ai_api.requirements.dependencies import get_requirement_analyzer_service
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.services import RequirementAnalyzerService
from ai_api.main import app
from ai_api.config import Settings, get_settings
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)

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

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."
    assert "details" in body["error"]


def test_requirement_analysis_endpoint_should_return_structured_response() -> None:
    def get_fake_requirement_analyzer_service() -> RequirementAnalyzerService:
        return RequirementAnalyzerService(
            llm_provider=FakeLLMProvider(
                response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
            ),
            retry_config=RetryConfig(max_attempts=2),
        )

    app.dependency_overrides[get_requirement_analyzer_service] = (
        get_fake_requirement_analyzer_service
    )

    try:
        payload = {
            "requirement_text": "Como cliente, quero renegociar minha dívida para gerar um novo boleto.",
            "language": "pt-BR",
        }

        response = client.post("/requirements/analyze", json=payload)

        assert response.status_code == 200

        body = response.json()

        assert body["summary"].startswith("O cliente deseja renegociar")
        assert len(body["business_rules"]) == 2
        assert len(body["acceptance_criteria"]) == 2
        assert len(body["risks"]) == 1
        assert body["risks"][0]["severity"] == "high"
        assert len(body["automation_opportunities"]) == 2
    finally:
        app.dependency_overrides.clear()


def test_requirement_analysis_endpoint_should_validate_blank_requirement() -> None:
    payload = {
        "requirement_text": "   ",
        "language": "pt-BR",
    }

    response = client.post("/requirements/analyze", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_requirement_analysis_endpoint_should_handle_analysis_error() -> None:
    def get_invalid_requirement_analyzer_service() -> RequirementAnalyzerService:
        return RequirementAnalyzerService(
            llm_provider=FakeLLMProvider(response_content="not a json"),
            retry_config=RetryConfig(max_attempts=1),
        )

    app.dependency_overrides[get_requirement_analyzer_service] = (
        get_invalid_requirement_analyzer_service
    )

    try:
        payload = {
            "requirement_text": "Como cliente, quero consultar meus boletos em aberto.",
            "language": "pt-BR",
        }

        response = client.post("/requirements/analyze", json=payload)

        assert response.status_code == 502

        body = response.json()

        assert body["error"]["type"] == "requirement_analysis_error"
        assert body["error"]["message"] == "Requirement analysis failed."
    finally:
        app.dependency_overrides.clear()


def test_llm_providers_endpoint_should_return_active_provider() -> None:
    def get_test_settings() -> Settings:
        return Settings(
            _env_file=None,
            llm_provider="ollama",
            ollama_model="llama3.1",
        )

    app.dependency_overrides[get_settings] = get_test_settings

    try:
        response = client.get("/llm/providers")

        assert response.status_code == 200

        body = response.json()

        assert body["active_provider"] == "ollama"
        assert body["supported_providers"] == ["fake", "openai", "ollama"]
    finally:
        app.dependency_overrides.clear()


def test_llm_health_endpoint_should_return_provider_status() -> None:
    def get_test_settings() -> Settings:
        return Settings(
            _env_file=None,
            llm_provider="openai",
            openai_api_key=None,
            openai_model=None,
        )

    app.dependency_overrides[get_settings] = get_test_settings

    try:
        response = client.get("/llm/health")

        assert response.status_code == 200

        body = response.json()

        assert body["provider"] == "openai"
        assert body["status"] == "missing_configuration"
        assert body["missing_settings"] == ["OPENAI_API_KEY", "OPENAI_MODEL"]
    finally:
        app.dependency_overrides.clear()


def test_rag_chunk_endpoint_should_return_document_chunks() -> None:
    payload = {
        "document_text": " ".join(
            [
                "Como cliente, quero renegociar minha dívida para gerar um boleto atualizado."
                for _ in range(20)
            ]
        ),
        "source": "requirement-001",
        "chunk_size": 200,
        "chunk_overlap": 40,
    }

    response = client.post("/rag/chunk", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["source"] == "requirement-001"
    assert body["total_chunks"] > 1
    assert len(body["chunks"]) == body["total_chunks"]
    assert body["chunks"][0]["chunk_id"] == "requirement-001-0"


def test_rag_chunk_endpoint_should_validate_blank_document_text() -> None:
    payload = {
        "document_text": "   ",
        "source": "requirement-001",
        "chunk_size": 200,
        "chunk_overlap": 40,
    }

    response = client.post("/rag/chunk", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."

def test_rag_ingest_endpoint_should_return_document_and_chunks() -> None:
    payload = {
        "document_text": " ".join(
            [
                "Como cliente, quero renegociar minha dívida para gerar um boleto atualizado."
                for _ in range(20)
            ]
        ),
        "source": "requirement-001",
        "title": "Renegociação de dívida",
        "metadata": {
            "domain": "billing",
            "team": "qa",
        },
        "chunk_size": 200,
        "chunk_overlap": 40,
    }

    response = client.post("/rag/ingest", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["document"]["source"] == "requirement-001"
    assert body["document"]["title"] == "Renegociação de dívida"
    assert body["document"]["metadata"]["domain"] == "billing"
    assert body["total_chunks"] > 1
    assert len(body["chunks"]) == body["total_chunks"]
    assert body["chunks"][0]["metadata"]["document_id"] == body["document"]["document_id"]


def test_rag_ingest_endpoint_should_validate_blank_document_text() -> None:
    payload = {
        "document_text": "   ",
        "source": "requirement-001",
        "chunk_size": 200,
        "chunk_overlap": 40,
    }

    response = client.post("/rag/ingest", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_rag_extract_text_endpoint_should_return_extracted_text() -> None:
    response = client.post(
        "/rag/extract-text",
        files={
            "file": (
                "requirement.txt",
                b"Como cliente, quero renegociar minha divida.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["filename"] == "requirement.txt"
    assert body["source"] == "requirement.txt"
    assert body["text"] == "Como cliente, quero renegociar minha divida."
    assert body["metadata"]["extension"] == ".txt"


def test_rag_extract_text_endpoint_should_reject_unsupported_file_type() -> None:
    response = client.post(
        "/rag/extract-text",
        files={
            "file": (
                "document.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "text_extraction_error"
    assert body["error"]["message"] == "Unsupported file type: .pdf"


def test_rag_ingest_file_endpoint_should_extract_and_ingest_file() -> None:
    response = client.post(
        "/rag/ingest-file",
        data={
            "source": "requirement-001",
            "title": "Renegociação de dívida",
            "metadata": '{"domain": "billing", "team": "qa"}',
            "chunk_size": "200",
            "chunk_overlap": "40",
        },
        files={
            "file": (
                "requirement.txt",
                b"Como cliente, quero renegociar minha divida para gerar um boleto atualizado.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["document"]["source"] == "requirement-001"
    assert body["document"]["title"] == "Renegociação de dívida"
    assert body["document"]["metadata"]["domain"] == "billing"
    assert body["document"]["metadata"]["filename"] == "requirement.txt"
    assert body["total_chunks"] >= 1
    assert body["extraction_metadata"]["extension"] == ".txt"


def test_rag_ingest_file_endpoint_should_reject_invalid_metadata() -> None:
    response = client.post(
        "/rag/ingest-file",
        data={
            "metadata": "{invalid-json}",
        },
        files={
            "file": (
                "requirement.txt",
                b"Texto valido.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "rag_request_error"
    assert body["error"]["message"] == "metadata must be a valid JSON object."


def test_rag_ingest_file_endpoint_should_reject_unsupported_file_type() -> None:
    response = client.post(
        "/rag/ingest-file",
        files={
            "file": (
                "document.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "text_extraction_error"
    assert body["error"]["message"] == "Unsupported file type: .pdf"
