import pytest

from ai_api.rag import RAGEvaluationService
from ai_api.rag.schemas import SourceCitation, VectorSearchResult


def test_rag_evaluation_should_pass_for_grounded_answer_with_citation() -> None:
    service = RAGEvaluationService()

    context_chunks = [
        VectorSearchResult(
            record_id="requirement-001-0",
            text="Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
            score=0.9,
            metadata={
                "source": "requirement-001",
                "chunk_id": "requirement-001-0",
            },
        )
    ]
    citations = [
        SourceCitation(
            citation_id="source-1",
            source="requirement-001",
            chunk_id="requirement-001-0",
            excerpt="Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
            score=0.9,
        )
    ]

    response = service.evaluate(
        query="Como o cliente pode gerar boleto?",
        answer="O cliente pode gerar boleto atualizado após renegociar a dívida [source-1].",
        context_chunks=context_chunks,
        citations=citations,
    )

    assert response.passed is True
    assert response.overall_score >= 0.6
    assert response.issues == []


def test_rag_evaluation_should_fail_when_citations_are_missing() -> None:
    service = RAGEvaluationService()

    response = service.evaluate(
        query="Como o cliente pode gerar boleto?",
        answer="O cliente pode gerar boleto atualizado após renegociar a dívida.",
        context_chunks=[
            VectorSearchResult(
                record_id="requirement-001-0",
                text="Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                score=0.9,
                metadata={
                    "chunk_id": "requirement-001-0",
                },
            )
        ],
        citations=[],
    )

    assert response.passed is False
    assert "No citations were provided." in response.issues


def test_rag_evaluation_should_fail_for_ungrounded_answer() -> None:
    service = RAGEvaluationService()

    response = service.evaluate(
        query="Como o cliente pode gerar boleto?",
        answer="O usuário deve informar senha e token para autenticar login [source-1].",
        context_chunks=[
            VectorSearchResult(
                record_id="requirement-001-0",
                text="Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                score=0.9,
                metadata={
                    "chunk_id": "requirement-001-0",
                },
            )
        ],
        citations=[
            SourceCitation(
                citation_id="source-1",
                source="requirement-001",
                chunk_id="requirement-001-0",
                excerpt="Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                score=0.9,
            )
        ],
    )

    assert response.passed is False
    assert any(
        issue == "Answer has low lexical overlap with retrieved context."
        for issue in response.issues
    )


def test_rag_evaluation_should_reject_blank_query() -> None:
    service = RAGEvaluationService()

    with pytest.raises(ValueError, match="query cannot be blank"):
        service.evaluate(
            query="   ",
            answer="Resposta válida.",
            context_chunks=[
                VectorSearchResult(
                    record_id="chunk-1",
                    text="Texto válido.",
                    score=0.8,
                )
            ],
        )


def test_rag_evaluation_should_reject_empty_context_chunks() -> None:
    service = RAGEvaluationService()

    with pytest.raises(ValueError, match="context_chunks cannot be empty"):
        service.evaluate(
            query="Pergunta válida?",
            answer="Resposta válida.",
            context_chunks=[],
        )
