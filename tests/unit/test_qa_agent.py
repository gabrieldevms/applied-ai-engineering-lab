import pytest
from ai_api.agents import QAAgentService
from ai_api.rag import SemanticSearchDocument


def test_qa_agent_should_analyze_requirement_without_knowledge_documents() -> None:
    service = QAAgentService()

    response = service.run(
        requirement_text=(
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        language="pt-BR",
        max_steps=4,
    )

    assert response.status == "completed"
    assert response.metadata["agent_type"] == "qa-agent-v1"
    assert response.metadata["knowledge_documents"] == 0
    assert response.requirement_analysis["summary"]
    assert response.retrieved_context is None
    assert response.steps[2].name == "tool_call:requirements.analyze"


def test_qa_agent_should_retrieve_context_and_analyze_requirement() -> None:
    service = QAAgentService()

    response = service.run(
        requirement_text=(
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        knowledge_documents=[
            SemanticSearchDocument(
                source="billing-doc",
                title="Cobrança",
                document_text=(
                    "boleto cobrança renegociação dívida pagamento vencimento"
                ),
                metadata={
                    "domain": "billing",
                },
            ),
            SemanticSearchDocument(
                source="auth-doc",
                title="Autenticação",
                document_text="login senha autenticação usuário sessão",
                metadata={
                    "domain": "auth",
                },
            ),
        ],
        language="pt-BR",
        top_k=1,
        chunk_size=200,
        chunk_overlap=40,
        max_steps=5,
    )

    assert response.status == "completed"
    assert response.metadata["knowledge_documents"] == 2
    assert response.retrieved_context is not None
    assert response.retrieved_context["total_retrieved_chunks"] == 1
    assert response.requirement_analysis["summary"]
    assert response.steps[2].name == "tool_call:rag.retrieve"
    assert response.steps[3].name == "tool_call:requirements.analyze"


def test_qa_agent_should_reject_blank_requirement() -> None:
    service = QAAgentService()

    with pytest.raises(ValueError, match="requirement_text cannot be blank"):
        service.run(requirement_text="   ")
