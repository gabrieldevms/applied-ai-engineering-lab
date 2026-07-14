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
from ai_api.rag import (
    RAGAnswerService,
    SemanticSearchService,
    get_rag_answer_service,
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


def test_rag_embed_endpoint_should_return_embeddings() -> None:
    payload = {
        "texts": [
            "Como cliente, quero renegociar minha dívida.",
            "Como cliente, quero consultar meus boletos.",
        ]
    }

    response = client.post("/rag/embed", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["provider"] == "fake"
    assert body["model"] == "fake-keyword-hash-embedding-v1"
    assert body["total_embeddings"] == 2
    assert len(body["embeddings"]) == 2
    assert body["embeddings"][0]["dimensions"] == 32
    assert len(body["embeddings"][0]["vector"]) == 32


def test_rag_embed_endpoint_should_validate_blank_text() -> None:
    payload = {
        "texts": [
            "Texto válido.",
            "   ",
        ]
    }

    response = client.post("/rag/embed", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_rag_search_endpoint_should_return_semantic_results() -> None:
    payload = {
        "query": "boleto cobrança",
        "documents": [
            {
                "source": "billing-doc",
                "title": "Billing",
                "document_text": "boleto cobrança vencimento pagamento dívida",
                "metadata": {
                    "domain": "billing"
                },
            },
            {
                "source": "auth-doc",
                "title": "Authentication",
                "document_text": "login senha autenticação usuário sessão",
                "metadata": {
                    "domain": "auth"
                },
            },
        ],
        "top_k": 1,
        "chunk_size": 200,
        "chunk_overlap": 40,
    }

    response = client.post("/rag/search", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == "boleto cobrança"
    assert body["total_indexed_chunks"] == 2
    assert body["total_results"] == 1
    assert body["results"][0]["metadata"]["source"] == "billing-doc"


def test_rag_search_endpoint_should_validate_blank_query() -> None:
    payload = {
        "query": "   ",
        "documents": [
            {
                "source": "doc-1",
                "document_text": "Texto válido.",
            }
        ],
    }

    response = client.post("/rag/search", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_rag_answer_endpoint_should_generate_answer() -> None:
    def get_test_rag_answer_service() -> RAGAnswerService:
        return RAGAnswerService(
            semantic_search_service=SemanticSearchService(),
            llm_provider=FakeLLMProvider(
                response_content="O cliente pode gerar boleto após a renegociação."
            ),
        )

    app.dependency_overrides[get_rag_answer_service] = get_test_rag_answer_service

    try:
        payload = {
            "query": "Como o cliente gera um boleto?",
            "documents": [
                {
                    "source": "requirement-001",
                    "title": "Renegociação",
                    "document_text": "Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                    "metadata": {
                        "domain": "billing"
                    },
                }
            ],
            "language": "pt-BR",
            "top_k": 1,
            "chunk_size": 200,
            "chunk_overlap": 40,
        }

        response = client.post("/rag/answer", json=payload)

        assert response.status_code == 200

        body = response.json()

        assert body["answer"] == "O cliente pode gerar boleto após a renegociação."
        assert body["provider"] == "fake"
        assert body["total_context_chunks"] == 1
        assert body["context_chunks"][0]["metadata"]["source"] == "requirement-001"
        assert len(body["citations"]) == 1
        assert body["citations"][0]["citation_id"] == "source-1"
        assert body["citations"][0]["source"] == "requirement-001"
        assert body["citations"][0]["excerpt"] == "Após renegociar a dívida, o cliente pode gerar um boleto atualizado."
    finally:
        app.dependency_overrides.clear()


def test_rag_answer_endpoint_should_validate_blank_query() -> None:
    payload = {
        "query": "   ",
        "documents": [
            {
                "source": "requirement-001",
                "document_text": "Texto válido.",
            }
        ],
    }

    response = client.post("/rag/answer", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_rag_evaluate_endpoint_should_return_evaluation_result() -> None:
    payload = {
        "query": "Como o cliente pode gerar boleto?",
        "answer": "O cliente pode gerar boleto atualizado após renegociar a dívida [source-1].",
        "context_chunks": [
            {
                "record_id": "requirement-001-0",
                "text": "Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                "score": 0.9,
                "metadata": {
                    "source": "requirement-001",
                    "chunk_id": "requirement-001-0"
                }
            }
        ],
        "citations": [
            {
                "citation_id": "source-1",
                "source": "requirement-001",
                "title": "Renegociação",
                "chunk_id": "requirement-001-0",
                "excerpt": "Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                "score": 0.9,
                "metadata": {}
            }
        ],
        "minimum_overall_score": 0.6
    }

    response = client.post("/rag/evaluate", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["passed"] is True
    assert body["overall_score"] >= 0.6
    assert len(body["metrics"]) == 4
    assert body["metadata"]["total_context_chunks"] == 1


def test_rag_evaluate_endpoint_should_validate_blank_answer() -> None:
    payload = {
        "query": "Pergunta válida?",
        "answer": "   ",
        "context_chunks": [
            {
                "record_id": "chunk-1",
                "text": "Texto válido.",
                "score": 0.8,
                "metadata": {}
            }
        ]
    }

    response = client.post("/rag/evaluate", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_rag_retrieve_endpoint_should_return_retrieved_chunks() -> None:
    payload = {
        "query": "boleto cobrança",
        "documents": [
            {
                "source": "billing-doc",
                "title": "Billing",
                "document_text": "boleto cobrança vencimento pagamento dívida",
                "metadata": {
                    "domain": "billing"
                },
            },
            {
                "source": "auth-doc",
                "title": "Authentication",
                "document_text": "login senha autenticação usuário sessão",
                "metadata": {
                    "domain": "auth"
                },
            },
        ],
        "top_k": 1,
        "chunk_size": 200,
        "chunk_overlap": 40,
    }

    response = client.post("/rag/retrieve", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == "boleto cobrança"
    assert body["total_indexed_chunks"] == 2
    assert body["total_retrieved_chunks"] == 1
    assert body["retrieved_chunks"][0]["metadata"]["source"] == "billing-doc"


def test_rag_retrieve_endpoint_should_validate_blank_query() -> None:
    payload = {
        "query": "   ",
        "documents": [
            {
                "source": "doc-1",
                "document_text": "Texto válido.",
            }
        ],
    }

    response = client.post("/rag/retrieve", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_agents_run_endpoint_should_complete_agent_run() -> None:
    payload = {
        "objective": "Analyze a requirement and identify risks.",
        "context": "The requirement is about boleto generation.",
        "max_steps": 3,
        "metadata": {
            "domain": "qa"
        }
    }

    response = client.post("/agents/run", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["run_id"].startswith("agent-run-")
    assert body["objective"] == "Analyze a requirement and identify risks."
    assert len(body["steps"]) == 3
    assert body["metadata"]["domain"] == "qa"
    assert body["metadata"]["has_context"] is True


def test_agents_run_endpoint_should_validate_blank_objective() -> None:
    payload = {
        "objective": "   "
    }

    response = client.post("/agents/run", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_agents_tools_endpoint_should_list_available_tools() -> None:
    response = client.get("/agents/tools")

    assert response.status_code == 200

    body = response.json()

    tool_names = [
        tool["name"]
        for tool in body["tools"]
    ]

    assert body["total_tools"] == 3
    assert "rag.retrieve" in tool_names
    assert "rag.answer" in tool_names
    assert "requirements.analyze" in tool_names
    assert body["metadata"]["registry"] == "agent-tool-registry-v1"
