from collections.abc import Sequence

from ai_api.rag.schemas import SourceCitation, VectorSearchResult


def build_source_citations(
    context_chunks: Sequence[VectorSearchResult],
    excerpt_max_chars: int = 280,
) -> list[SourceCitation]:
    citations: list[SourceCitation] = []

    for index, chunk in enumerate(context_chunks, start=1):
        source = chunk.metadata.get("source", "unknown")
        title = chunk.metadata.get("title") or None
        chunk_id = chunk.metadata.get("chunk_id", chunk.record_id)

        citations.append(
            SourceCitation(
                citation_id=f"source-{index}",
                source=source,
                title=title,
                chunk_id=chunk_id,
                excerpt=_build_excerpt(
                    text=chunk.text,
                    max_chars=excerpt_max_chars,
                ),
                score=chunk.score,
                metadata={
                    "record_id": chunk.record_id,
                    "chunk_index": chunk.metadata.get("chunk_index", ""),
                    "start_index": chunk.metadata.get("start_index", ""),
                    "end_index": chunk.metadata.get("end_index", ""),
                },
            )
        )

    return citations


def _build_excerpt(
    text: str,
    max_chars: int,
) -> str:
    cleaned_text = " ".join(text.strip().split())

    if len(cleaned_text) <= max_chars:
        return cleaned_text

    return f"{cleaned_text[: max_chars - 3].rstrip()}..."
