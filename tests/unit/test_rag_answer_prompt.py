import pytest

from ai_api.rag import build_rag_answer_messages
from ai_api.rag.schemas import VectorSearchResult


def test_build_rag_answer_messages_should_create_system_and_user_messages() -> None:
    messages = build_rag_answer_messages(
        query="Como gerar boleto?",
        context_chunks=[
            VectorSearchResult(
                record_id="chunk-1",
                text="O sistema deve gerar boleto após a renegociação.",
                score=0.9,
                metadata={
                    "source": "requirement-001",
                    "title": "Renegociação",
                    "chunk_id": "requirement-001-0",
                },
            )
        ],
        language="pt-BR",
    )

    assert len(messages) == 2
    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert "Como gerar boleto?" in messages[1].content
    assert "O sistema deve gerar boleto" in messages[1].content
    assert "requirement-001" in messages[1].content


def test_build_rag_answer_messages_should_reject_blank_query() -> None:
    with pytest.raises(ValueError, match="query cannot be blank"):
        build_rag_answer_messages(
            query="   ",
            context_chunks=[
                VectorSearchResult(
                    record_id="chunk-1",
                    text="Texto válido.",
                    score=0.9,
                )
            ],
        )


def test_build_rag_answer_messages_should_reject_empty_context() -> None:
    with pytest.raises(ValueError, match="context_chunks cannot be empty"):
        build_rag_answer_messages(
            query="Pergunta válida?",
            context_chunks=[],
        )
