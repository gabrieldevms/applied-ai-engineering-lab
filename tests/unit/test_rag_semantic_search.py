import pytest

from ai_api.rag import (
    SemanticSearchDocument,
    SemanticSearchService,
)


def test_semantic_search_should_return_most_relevant_results() -> None:
    service = SemanticSearchService()

    response = service.search(
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
    assert response.total_results == 1
    assert response.results[0].metadata["source"] == "billing-doc"
    assert response.results[0].metadata["domain"] == "billing"
    assert response.results[0].score > 0


def test_semantic_search_should_limit_results_by_top_k() -> None:
    service = SemanticSearchService()

    response = service.search(
        query="boleto",
        documents=[
            SemanticSearchDocument(
                source="doc-1",
                document_text="boleto pagamento",
            ),
            SemanticSearchDocument(
                source="doc-2",
                document_text="boleto vencimento",
            ),
            SemanticSearchDocument(
                source="doc-3",
                document_text="login senha",
            ),
        ],
        top_k=2,
        chunk_size=200,
        chunk_overlap=40,
    )

    assert response.total_indexed_chunks == 3
    assert response.total_results == 2


def test_semantic_search_should_preserve_chunk_metadata() -> None:
    service = SemanticSearchService()

    response = service.search(
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

    result = response.results[0]

    assert result.metadata["source"] == "requirement-001"
    assert result.metadata["title"] == "Renegociação de dívida"
    assert result.metadata["team"] == "qa"
    assert result.metadata["chunk_id"] == "requirement-001-0"
    assert result.metadata["chunk_index"] == "0"


def test_semantic_search_should_reject_blank_query() -> None:
    service = SemanticSearchService()

    with pytest.raises(ValueError, match="query cannot be blank"):
        service.search(
            query="   ",
            documents=[
                SemanticSearchDocument(
                    source="doc-1",
                    document_text="Texto válido.",
                )
            ],
        )


def test_semantic_search_should_reject_empty_documents() -> None:
    service = SemanticSearchService()

    with pytest.raises(ValueError, match="documents cannot be empty"):
        service.search(
            query="boleto",
            documents=[],
        )
