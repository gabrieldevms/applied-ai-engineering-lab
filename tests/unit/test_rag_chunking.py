import pytest

from ai_api.rag import TextChunker


def test_text_chunker_should_create_single_chunk_for_short_text() -> None:
    chunker = TextChunker()

    response = chunker.chunk(
        document_text="Este é um requisito simples.",
        source="requirement-001",
        chunk_size=800,
        chunk_overlap=120,
    )

    assert response.source == "requirement-001"
    assert response.total_chunks == 1
    assert response.chunks[0].content == "Este é um requisito simples."
    assert response.chunks[0].chunk_id == "requirement-001-0"


def test_text_chunker_should_create_multiple_chunks_for_long_text() -> None:
    chunker = TextChunker()

    document_text = " ".join(
        [
            "Como cliente, quero renegociar minha dívida para gerar um boleto atualizado."
            for _ in range(20)
        ]
    )

    response = chunker.chunk(
        document_text=document_text,
        source="requirement-long",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert response.total_chunks > 1
    assert response.chunks[0].chunk_index == 0
    assert response.chunks[1].chunk_index == 1
    assert all(chunk.source == "requirement-long" for chunk in response.chunks)


def test_text_chunker_should_reject_blank_document_text() -> None:
    chunker = TextChunker()

    with pytest.raises(ValueError, match="document_text cannot be blank"):
        chunker.chunk(document_text="   ")


def test_text_chunker_should_reject_blank_source() -> None:
    chunker = TextChunker()

    with pytest.raises(ValueError, match="source cannot be blank"):
        chunker.chunk(
            document_text="Texto válido.",
            source="   ",
        )


def test_text_chunker_should_reject_overlap_greater_than_or_equal_to_chunk_size() -> None:
    chunker = TextChunker()

    with pytest.raises(
        ValueError,
        match="chunk_overlap must be smaller than chunk_size",
    ):
        chunker.chunk(
            document_text="Texto válido.",
            chunk_size=100,
            chunk_overlap=100,
        )
