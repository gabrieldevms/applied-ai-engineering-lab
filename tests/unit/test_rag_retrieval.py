import pytest

from ai_api.rag import RetrievalService, SemanticSearchDocument


def test_retrieval_service_should_retrieve_relevant_chunks() -> None:
    service = RetrievalService()

    response = service.retrieve(
        query="boleto cobrança",
        documents=[
            SemanticSearchDocument(
                source="billing-doc",
                title="Billing",
                document_text="boleto cobrança vencimento pagamento dívida",
                metadata={"domain": "billing"},
            ),
            SemanticSearchDocument(
                source="auth-doc",
                title="Authentication",
                document_text="login senha autenticação usuário sessão",
                metadata={"domain": "auth"},
            ),
        ],
        top_k=1,
        chunk_size=200,
        chunk_overlap=40,
    )

    assert response.query == "boleto cobrança"
    assert response.total_indexed_chunks == 2
    assert response.total_retrieved_chunks == 1
    assert response.retrieved_chunks[0].metadata["source"] == "billing-doc"
    assert response.retrieved_chunks[0].metadata["domain"] == "billing"


def test_retrieval_service_should_preserve_chunk_metadata() -> None:
    service = RetrievalService()

    response = service.retrieve(
        query="renegociação",
        documents=[
            SemanticSearchDocument(
                source="requirement-001",
                title="Renegociação de dívida",
                document_text="renegociação dívida boleto atualizado",
                metadata={"team": "qa"},
            )
        ],
        top_k=1,
        chunk_size=200,
        chunk_overlap=40,
    )

    chunk = response.retrieved_chunks[0]

    assert chunk.metadata["source"] == "requirement-001"
    assert chunk.metadata["title"] == "Renegociação de dívida"
    assert chunk.metadata["team"] == "qa"
    assert chunk.metadata["chunk_id"] == "requirement-001-0"
    assert chunk.metadata["chunk_index"] == "0"


def test_retrieval_service_should_reject_blank_query() -> None:
    service = RetrievalService()

    with pytest.raises(ValueError, match="query cannot be blank"):
        service.retrieve(
            query="   ",
            documents=[
                SemanticSearchDocument(
                    source="doc-1",
                    document_text="Texto válido.",
                )
            ],
        )


def test_retrieval_service_should_reject_empty_documents() -> None:
    service = RetrievalService()

    with pytest.raises(ValueError, match="documents cannot be empty"):
        service.retrieve(
            query="boleto",
            documents=[],
        )
