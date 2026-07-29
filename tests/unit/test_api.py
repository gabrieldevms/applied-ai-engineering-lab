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
from ai_api.agents import (
    AgentPlanningService,
    get_agent_planning_service,
    AgentToolSelectionService,
    get_agent_tool_selection_service,
    AgentMultiStepExecutionService,
    get_agent_multi_step_execution_service,
    AgentExecutionLogService,
    InMemoryAgentExecutionLogStore,
    get_agent_execution_log_service,
    
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
                "document.exe",
                b"fake executable content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "text_extraction_error"
    assert body["error"]["message"] == "Unsupported file type: .exe"


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
                "document.exe",
                b"fake executable content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "text_extraction_error"
    assert body["error"]["message"] == "Unsupported file type: .exe"

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

    assert body["total_tools"] == 4
    assert "rag.retrieve" in tool_names
    assert "rag.answer" in tool_names
    assert "requirements.analyze" in tool_names
    assert "data_analysis.agent.run" in tool_names
    assert body["metadata"]["registry"] == "agent-tool-registry-v1"


def test_agents_tools_execute_endpoint_should_execute_rag_retrieve() -> None:
    payload = {
        "tool_name": "rag.retrieve",
        "arguments": {
            "query": "boleto cobrança",
            "documents": [
                {
                    "source": "billing-doc",
                    "title": "Cobrança",
                    "document_text": "boleto cobrança vencimento pagamento dívida",
                    "metadata": {
                        "domain": "billing"
                    },
                },
                {
                    "source": "auth-doc",
                    "title": "Autenticação",
                    "document_text": "login senha autenticação usuário sessão",
                    "metadata": {
                        "domain": "auth"
                    },
                },
            ],
            "top_k": 1,
            "chunk_size": 200,
            "chunk_overlap": 40,
        },
        "metadata": {
            "requested_by": "api-test"
        },
    }

    response = client.post("/agents/tools/execute", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["tool_name"] == "rag.retrieve"
    assert body["execution_id"].startswith("tool-execution-rag-retrieve-")
    assert body["output"]["query"] == "boleto cobrança"
    assert body["output"]["total_retrieved_chunks"] == 1
    assert (
        body["output"]["retrieved_chunks"][0]["metadata"]["source"]
        == "billing-doc"
    )
    assert body["metadata"]["requested_by"] == "api-test"


def test_agents_tools_execute_endpoint_should_return_error_for_unknown_tool() -> None:
    payload = {
        "tool_name": "unknown.tool",
        "arguments": {},
    }

    response = client.post("/agents/tools/execute", json=payload)

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "tool_execution_error"
    assert body["error"]["message"] == "Tool is not registered: unknown.tool"


def test_agents_run_endpoint_should_execute_tool_call() -> None:
    payload = {
        "objective": "Recuperar contexto relevante sobre boleto.",
        "max_steps": 4,
        "tool_calls": [
            {
                "tool_name": "rag.retrieve",
                "arguments": {
                    "query": "boleto cobrança",
                    "documents": [
                        {
                            "source": "billing-doc",
                            "title": "Cobrança",
                            "document_text": (
                                "boleto cobrança vencimento pagamento dívida"
                            ),
                            "metadata": {
                                "domain": "billing"
                            },
                        },
                        {
                            "source": "auth-doc",
                            "title": "Autenticação",
                            "document_text": (
                                "login senha autenticação usuário sessão"
                            ),
                            "metadata": {
                                "domain": "auth"
                            },
                        },
                    ],
                    "top_k": 1,
                    "chunk_size": 200,
                    "chunk_overlap": 40,
                },
            }
        ],
    }

    response = client.post("/agents/run", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["metadata"]["requested_tool_calls"] == 1
    assert body["steps"][2]["name"] == "tool_call:rag.retrieve"
    assert body["steps"][2]["status"] == "completed"
    assert body["steps"][2]["output"]["tool_name"] == "rag.retrieve"
    assert (
        body["steps"][2]["output"]["output"]["total_retrieved_chunks"]
        == 1
    )


def test_agents_run_endpoint_should_return_failed_status_for_invalid_tool_call() -> None:
    payload = {
        "objective": "Executar ferramenta inexistente.",
        "max_steps": 4,
        "tool_calls": [
            {
                "tool_name": "unknown.tool",
                "arguments": {},
            }
        ],
    }

    response = client.post("/agents/run", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "failed"
    assert body["steps"][2]["name"] == "tool_call:unknown.tool"
    assert body["steps"][2]["status"] == "failed"
    assert (
        body["steps"][2]["output"]["error"]
        == "Tool is not registered: unknown.tool"
    )


def test_agents_tools_execute_endpoint_should_execute_requirement_analysis() -> None:
    payload = {
        "tool_name": "requirements.analyze",
        "arguments": {
            "requirement_text": (
                "Como cliente, quero renegociar minha dívida para gerar "
                "um boleto atualizado."
            ),
            "language": "pt-BR",
        },
        "metadata": {
            "requested_by": "api-test"
        },
    }

    response = client.post("/agents/tools/execute", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["tool_name"] == "requirements.analyze"
    assert body["execution_id"].startswith(
        "tool-execution-requirements-analyze-"
    )
    assert body["output"]["summary"]
    assert "business_rules" in body["output"]
    assert "risks" in body["output"]
    assert "acceptance_criteria" in body["output"]
    assert body["metadata"]["requested_by"] == "api-test"
    assert body["metadata"]["tool_category"] == "qa"
    assert body["metadata"]["requires_llm"] is True


def test_agents_qa_run_endpoint_should_analyze_requirement() -> None:
    payload = {
        "requirement_text": (
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        "language": "pt-BR",
        "max_steps": 4,
        "metadata": {
            "domain": "qa"
        },
    }

    response = client.post("/agents/qa/run", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["metadata"]["agent_type"] == "qa-agent-v1"
    assert body["requirement_analysis"]["summary"]
    assert body["retrieved_context"] is None
    assert body["steps"][2]["name"] == "tool_call:requirements.analyze"


def test_agents_qa_run_endpoint_should_retrieve_context_and_analyze_requirement() -> None:
    payload = {
        "requirement_text": (
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        "knowledge_documents": [
            {
                "source": "billing-doc",
                "title": "Cobrança",
                "document_text": (
                    "boleto cobrança renegociação dívida pagamento vencimento"
                ),
                "metadata": {
                    "domain": "billing"
                },
            },
            {
                "source": "auth-doc",
                "title": "Autenticação",
                "document_text": "login senha autenticação usuário sessão",
                "metadata": {
                    "domain": "auth"
                },
            },
        ],
        "language": "pt-BR",
        "top_k": 1,
        "chunk_size": 200,
        "chunk_overlap": 40,
        "max_steps": 5,
    }

    response = client.post("/agents/qa/run", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["metadata"]["knowledge_documents"] == 2
    assert body["retrieved_context"]["total_retrieved_chunks"] == 1
    assert body["requirement_analysis"]["summary"]
    assert body["steps"][2]["name"] == "tool_call:rag.retrieve"
    assert body["steps"][3]["name"] == "tool_call:requirements.analyze"


def test_agents_qa_run_endpoint_should_validate_blank_requirement() -> None:
    payload = {
        "requirement_text": "   "
    }

    response = client.post("/agents/qa/run", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_agents_tools_execute_endpoint_should_execute_rag_answer() -> None:
    payload = {
        "tool_name": "rag.answer",
        "arguments": {
            "query": "Como o cliente pode gerar boleto?",
            "documents": [
                {
                    "source": "requirement-001",
                    "title": "Renegociação",
                    "document_text": (
                        "Após renegociar a dívida, o cliente pode gerar "
                        "um boleto atualizado."
                    ),
                    "metadata": {
                        "domain": "billing"
                    },
                }
            ],
            "language": "pt-BR",
            "top_k": 1,
            "chunk_size": 200,
            "chunk_overlap": 40,
        },
        "metadata": {
            "requested_by": "api-test"
        },
    }

    response = client.post("/agents/tools/execute", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert body["tool_name"] == "rag.answer"
    assert body["execution_id"].startswith(
        "tool-execution-rag-answer-"
    )
    assert body["output"]["answer"]
    assert body["output"]["provider"] == "fake"
    assert body["output"]["total_context_chunks"] == 1
    assert len(body["output"]["citations"]) == 1
    assert body["metadata"]["requested_by"] == "api-test"
    assert body["metadata"]["tool_category"] == "rag"
    assert body["metadata"]["requires_llm"] is True


def test_agents_plan_endpoint_should_generate_plan() -> None:
    def get_test_agent_planning_service() -> AgentPlanningService:
        return AgentPlanningService(
            llm_provider=FakeLLMProvider(
                response_content="""
                {
                  "summary": "Plano estruturado para análise de requisito.",
                  "steps": [
                    {
                      "step_id": "plan-step-1",
                      "objective": "Analisar o requisito informado.",
                      "tool_name": "requirements.analyze",
                      "arguments": {},
                      "rationale": "A ferramenta de análise de requisitos ajuda a identificar riscos, regras e cenários de teste."
                    }
                  ]
                }
                """
            )
        )

    app.dependency_overrides[
        get_agent_planning_service
    ] = get_test_agent_planning_service

    try:
        payload = {
            "objective": "Analisar requisito de boleto.",
            "context": "Contexto de qualidade.",
            "max_steps": 3,
            "language": "pt-BR",
            "metadata": {
                "domain": "qa"
            },
        }

        response = client.post("/agents/plan", json=payload)

        assert response.status_code == 200

        body = response.json()

        assert body["objective"] == "Analisar requisito de boleto."
        assert body["summary"] == "Plano estruturado para análise de requisito."
        assert len(body["steps"]) == 1
        assert body["provider"] == "fake"
        assert body["model"] == "fake-llm-v1"
        assert body["metadata"]["domain"] == "qa"
        assert body["metadata"]["planner"] == "agent-planning-service-v1"
        assert body["steps"][0]["tool_name"] == "requirements.analyze"
    finally:
        app.dependency_overrides.clear()


def test_agents_plan_endpoint_should_validate_blank_objective() -> None:
    payload = {
        "objective": "   "
    }

    response = client.post("/agents/plan", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_agents_tools_select_endpoint_should_select_tools() -> None:
    def get_test_agent_tool_selection_service() -> AgentToolSelectionService:
        return AgentToolSelectionService(
            planning_service=AgentPlanningService(
                llm_provider=FakeLLMProvider(
                    response_content="""
                    {
                      "summary": "Plano para análise de requisito.",
                      "steps": [
                        {
                          "step_id": "plan-step-1",
                          "objective": "Analisar requisito.",
                          "tool_name": "requirements.analyze",
                          "arguments": {
                            "requirement_text": "Como cliente, quero gerar boleto.",
                            "language": "pt-BR"
                          },
                          "rationale": "A ferramenta de requisitos é adequada."
                        }
                      ]
                    }
                    """
                )
            )
        )

    app.dependency_overrides[
        get_agent_tool_selection_service
    ] = get_test_agent_tool_selection_service

    try:
        payload = {
            "objective": "Analisar requisito de boleto.",
            "context": "Contexto de qualidade.",
            "max_steps": 3,
            "language": "pt-BR",
            "metadata": {
                "domain": "qa"
            },
        }

        response = client.post("/agents/tools/select", json=payload)

        assert response.status_code == 200

        body = response.json()

        assert body["objective"] == "Analisar requisito de boleto."
        assert body["plan_summary"] == "Plano para análise de requisito."
        assert body["provider"] == "fake"
        assert len(body["selected_tool_calls"]) == 1
        assert (
            body["selected_tool_calls"][0]["tool_name"]
            == "requirements.analyze"
        )
        assert body["metadata"]["domain"] == "qa"
        assert body["metadata"]["selector"] == (
            "agent-tool-selection-service-v1"
        )
    finally:
        app.dependency_overrides.clear()


def test_agents_tools_select_endpoint_should_validate_blank_objective() -> None:
    payload = {
        "objective": "   "
    }

    response = client.post("/agents/tools/select", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_agents_execute_endpoint_should_plan_select_and_execute() -> None:
    def get_test_agent_multi_step_execution_service() -> AgentMultiStepExecutionService:
        return AgentMultiStepExecutionService(
            tool_selection_service=AgentToolSelectionService(
                planning_service=AgentPlanningService(
                    llm_provider=FakeLLMProvider(
                        response_content="""
                        {
                          "summary": "Plano para análise de requisito.",
                          "steps": [
                            {
                              "step_id": "plan-step-1",
                              "objective": "Analisar requisito.",
                              "tool_name": "requirements.analyze",
                              "arguments": {
                                "requirement_text": "Como cliente, quero gerar boleto.",
                                "language": "pt-BR"
                              },
                              "rationale": "A ferramenta de requisitos é adequada."
                            }
                          ]
                        }
                        """
                    )
                )
            )
        )

    app.dependency_overrides[
        get_agent_multi_step_execution_service
    ] = get_test_agent_multi_step_execution_service

    try:
        payload = {
            "objective": "Analisar requisito de boleto.",
            "context": "Contexto de qualidade.",
            "max_plan_steps": 3,
            "max_execution_steps": 5,
            "language": "pt-BR",
            "metadata": {
                "domain": "qa"
            },
        }

        response = client.post("/agents/execute", json=payload)

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "completed"
        assert body["objective"] == "Analisar requisito de boleto."
        assert body["plan_summary"] == "Plano para análise de requisito."
        assert body["provider"] == "fake"
        assert len(body["selected_tool_calls"]) == 1
        assert body["execution_state"]["run_id"] == body["agent_run"]["run_id"]
        assert body["execution_state"]["status"] == "completed"
        assert body["execution_state"]["tool_calls"] == 1
        assert body["execution_state"]["metadata"]["source"] == "multi_step_execution"
        assert len(body["approval_decisions"]) == 1
        assert body["approval_decisions"][0]["status"] == "not_required"
        assert (
            body["selected_tool_calls"][0]["tool_name"]
            == "requirements.analyze"
        )
        assert body["safety_check"]["status"] == "passed"
        assert body["evaluation"]["status"] == "passed"
        assert body["evaluation"]["overall_score"] >= 0.8
        assert len(body["execution_logs"]) == 7
        assert body["metadata"]["execution_logs"] == 7
        assert body["metadata"]["evaluation_status"] == "passed"
        assert any(
            event["event_type"] == "safety_evaluated"
            for event in body["execution_logs"]
        )
        assert any(
            event["event_type"] == "evaluation_completed"
            for event in body["execution_logs"]
        )
        assert body["agent_run"]["status"] == "completed"
        assert (
            body["agent_run"]["steps"][2]["name"]
            == "tool_call:requirements.analyze"
        )
        assert body["metadata"]["executor"] == (
            "agent-multi-step-execution-service-v1"
        )
    finally:
        app.dependency_overrides.clear()


def test_agents_execute_endpoint_should_not_execute_safety_blocked_tool_calls() -> None:
    def get_test_agent_multi_step_execution_service() -> AgentMultiStepExecutionService:
        return AgentMultiStepExecutionService(
            tool_selection_service=AgentToolSelectionService(
                planning_service=AgentPlanningService(
                    llm_provider=FakeLLMProvider(
                        response_content="""
                        {
                          "summary": "Plano para análise de requisito.",
                          "steps": [
                            {
                              "step_id": "plan-step-1",
                              "objective": "Analisar requisito.",
                              "tool_name": "requirements.analyze",
                              "arguments": {
                                "requirement_text": "Como cliente, quero gerar boleto.",
                                "language": "pt-BR"
                              },
                              "rationale": "A ferramenta de requisitos é adequada."
                            }
                          ]
                        }
                        """
                    )
                )
            )
        )

    app.dependency_overrides[
        get_agent_multi_step_execution_service
    ] = get_test_agent_multi_step_execution_service

    try:
        payload = {
            "objective": "Analisar requisito de boleto.",
            "max_plan_steps": 3,
            "max_execution_steps": 5,
            "safety_policy": {
                "max_selected_tool_calls": 5,
                "max_executable_tool_calls": 5,
                "blocked_tools": [
                    "requirements.analyze"
                ],
                "allow_llm_tools": True,
                "metadata": {
                    "safety_reason": "blocked for test"
                },
            },
        }

        response = client.post("/agents/execute", json=payload)

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "completed"
        assert body["safety_check"]["status"] == "blocked"
        assert body["safety_check"]["violations"][0]["rule"] == "blocked_tool"
        assert body["agent_run"]["metadata"]["requested_tool_calls"] == 0
        assert body["execution_state"]["tool_calls"] == 0
    finally:
        app.dependency_overrides.clear()


def test_agents_execute_endpoint_should_validate_blank_objective() -> None:
    payload = {
        "objective": "   "
    }

    response = client.post("/agents/execute", json=payload)

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["type"] == "validation_error"
    assert body["error"]["message"] == "Invalid request payload."


def test_agents_execute_endpoint_should_not_execute_pending_tool_calls() -> None:
    def get_test_agent_multi_step_execution_service() -> AgentMultiStepExecutionService:
        return AgentMultiStepExecutionService(
            tool_selection_service=AgentToolSelectionService(
                planning_service=AgentPlanningService(
                    llm_provider=FakeLLMProvider(
                        response_content="""
                        {
                          "summary": "Plano para análise de requisito.",
                          "steps": [
                            {
                              "step_id": "plan-step-1",
                              "objective": "Analisar requisito.",
                              "tool_name": "requirements.analyze",
                              "arguments": {
                                "requirement_text": "Como cliente, quero gerar boleto.",
                                "language": "pt-BR"
                              },
                              "rationale": "A ferramenta de requisitos é adequada."
                            }
                          ]
                        }
                        """
                    )
                )
            )
        )

    app.dependency_overrides[
        get_agent_multi_step_execution_service
    ] = get_test_agent_multi_step_execution_service

    try:
        payload = {
            "objective": "Analisar requisito de boleto.",
            "max_plan_steps": 3,
            "max_execution_steps": 5,
            "approval_policy": {
                "require_approval_for_tools": [
                    "requirements.analyze"
                ],
                "auto_approve_safe_tools": True,
                "reject_tools": [],
                "metadata": {
                    "approval_reason": "manual review required"
                },
            },
        }

        response = client.post("/agents/execute", json=payload)

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "completed"
        assert len(body["selected_tool_calls"]) == 1
        assert len(body["approval_decisions"]) == 1
        assert body["approval_decisions"][0]["status"] == "pending"
        assert body["agent_run"]["metadata"]["requested_tool_calls"] == 0
        assert body["execution_state"]["tool_calls"] == 0
    finally:
        app.dependency_overrides.clear()


def test_agents_logs_endpoint_should_list_execution_logs() -> None:
    log_service = AgentExecutionLogService(
        log_store=InMemoryAgentExecutionLogStore(),
    )

    log_service.record_event(
        run_id="agent-run-123",
        event_type="runtime_completed",
        message="Runtime completed.",
    )

    def get_test_agent_execution_log_service() -> AgentExecutionLogService:
        return log_service

    app.dependency_overrides[
        get_agent_execution_log_service
    ] = get_test_agent_execution_log_service

    try:
        response = client.get("/agents/logs")

        assert response.status_code == 200

        body = response.json()

        assert body["total"] == 1
        assert body["events"][0]["run_id"] == "agent-run-123"
        assert body["events"][0]["event_type"] == "runtime_completed"
    finally:
        app.dependency_overrides.clear()


def test_agents_logs_by_run_id_endpoint_should_filter_execution_logs() -> None:
    log_service = AgentExecutionLogService(
        log_store=InMemoryAgentExecutionLogStore(),
    )

    log_service.record_event(
        run_id="agent-run-1",
        event_type="runtime_completed",
        message="Run 1 completed.",
    )
    log_service.record_event(
        run_id="agent-run-2",
        event_type="runtime_completed",
        message="Run 2 completed.",
    )

    def get_test_agent_execution_log_service() -> AgentExecutionLogService:
        return log_service

    app.dependency_overrides[
        get_agent_execution_log_service
    ] = get_test_agent_execution_log_service

    try:
        response = client.get("/agents/logs/agent-run-1")

        assert response.status_code == 200

        body = response.json()

        assert body["total"] == 1
        assert body["events"][0]["run_id"] == "agent-run-1"
    finally:
        app.dependency_overrides.clear()


def test_agents_evaluate_endpoint_should_evaluate_execution() -> None:
    payload = {
        "objective": "Analisar requisito.",
        "agent_run": {
            "run_id": "agent-run-123",
            "objective": "Analisar requisito.",
            "status": "completed",
            "final_answer": "Execução concluída.",
            "steps": [
                {
                    "step_id": "step-1",
                    "name": "understand_objective",
                    "status": "completed",
                    "input": {},
                    "output": {},
                    "metadata": {},
                }
            ],
            "metadata": {},
        },
        "execution_state": {
            "state_id": "agent-state-agent-run-123",
            "run_id": "agent-run-123",
            "objective": "Analisar requisito.",
            "status": "completed",
            "current_step": "understand_objective",
            "total_steps": 1,
            "completed_steps": 1,
            "failed_steps": 0,
            "skipped_steps": 0,
            "tool_calls": 0,
            "metadata": {},
        },
        "safety_check": {
            "status": "passed",
            "violations": [],
            "metadata": {},
        },
        "execution_logs": [
            {
                "log_id": "agent-log-123",
                "run_id": "agent-run-123",
                "event_type": "runtime_completed",
                "level": "info",
                "message": "Runtime completed.",
                "created_at": "2026-01-01T00:00:00+00:00",
                "metadata": {},
            }
        ],
        "metadata": {
            "source": "api-test"
        },
    }

    response = client.post("/agents/evaluate", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "passed"
    assert body["overall_score"] == 1.0
    assert len(body["metrics"]) == 5
    assert body["metadata"]["source"] == "api-test"
    assert body["metadata"]["evaluator"] == "agent-evaluation-service-v1"
