from ai_api.rag import build_source_citations
from ai_api.rag.schemas import VectorSearchResult


def test_build_source_citations_should_create_citations_from_context_chunks() -> None:
    citations = build_source_citations(
        [
            VectorSearchResult(
                record_id="chunk-1",
                text="Após renegociar a dívida, o cliente pode gerar um boleto atualizado.",
                score=0.92,
                metadata={
                    "source": "requirement-001",
                    "title": "Renegociação de dívida",
                    "chunk_id": "requirement-001-0",
                    "chunk_index": "0",
                    "start_index": "0",
                    "end_index": "80",
                },
            )
        ]
    )

    assert len(citations) == 1
    assert citations[0].citation_id == "source-1"
    assert citations[0].source == "requirement-001"
    assert citations[0].title == "Renegociação de dívida"
    assert citations[0].chunk_id == "requirement-001-0"
    assert citations[0].score == 0.92
    assert citations[0].excerpt.startswith("Após renegociar")


def test_build_source_citations_should_truncate_long_excerpt() -> None:
    long_text = " ".join(["texto"] * 100)

    citations = build_source_citations(
        [
            VectorSearchResult(
                record_id="chunk-1",
                text=long_text,
                score=0.8,
                metadata={
                    "source": "doc-1",
                    "chunk_id": "doc-1-0",
                },
            )
        ],
        excerpt_max_chars=40,
    )

    assert len(citations[0].excerpt) <= 40
    assert citations[0].excerpt.endswith("...")


def test_build_source_citations_should_use_defaults_when_metadata_is_missing() -> None:
    citations = build_source_citations(
        [
            VectorSearchResult(
                record_id="chunk-1",
                text="Texto de contexto.",
                score=0.7,
            )
        ]
    )

    assert citations[0].source == "unknown"
    assert citations[0].title is None
    assert citations[0].chunk_id == "chunk-1"
