import hashlib
import re
from typing import Any

from ai_api.rag.chunking import TextChunker
from ai_api.rag.schemas import (
    DocumentChunk,
    DocumentIngestionResponse,
    IngestedDocument,
)


class DocumentIngestionService:
    def __init__(self, chunker: TextChunker | None = None) -> None:
        self.chunker = chunker or TextChunker()

    def ingest(
        self,
        document_text: str,
        source: str = "manual",
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> DocumentIngestionResponse:
        cleaned_text = document_text.strip()
        cleaned_source = source.strip()
        cleaned_title = title.strip() if title is not None else None
        cleaned_metadata = metadata or {}

        if not cleaned_text:
            raise ValueError("document_text cannot be blank")

        if not cleaned_source:
            raise ValueError("source cannot be blank")

        document_id = self._build_document_id(
            source=cleaned_source,
            document_text=cleaned_text,
        )

        document = IngestedDocument(
            document_id=document_id,
            source=cleaned_source,
            title=cleaned_title,
            character_count=len(cleaned_text),
            metadata=cleaned_metadata,
        )

        chunking_response = self.chunker.chunk(
            document_text=cleaned_text,
            source=document_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        enriched_chunks = [
            self._enrich_chunk(
                chunk=chunk,
                document=document,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            for chunk in chunking_response.chunks
        ]

        return DocumentIngestionResponse(
            document=document,
            total_chunks=len(enriched_chunks),
            chunks=enriched_chunks,
        )

    def _build_document_id(
        self,
        source: str,
        document_text: str,
    ) -> str:
        safe_source = self._slugify_source(source)
        content_hash = hashlib.sha256(
            document_text.encode("utf-8"),
        ).hexdigest()[:12]

        return f"{safe_source}-{content_hash}"

    def _slugify_source(self, source: str) -> str:
        normalized_source = source.strip().lower()
        normalized_source = re.sub(r"[^a-z0-9]+", "-", normalized_source)
        normalized_source = normalized_source.strip("-")

        return normalized_source or "document"

    def _enrich_chunk(
        self,
        chunk: DocumentChunk,
        document: IngestedDocument,
        chunk_size: int,
        chunk_overlap: int,
    ) -> DocumentChunk:
        return chunk.model_copy(
            update={
                "metadata": {
                    **chunk.metadata,
                    "document_id": document.document_id,
                    "original_source": document.source,
                    "title": document.title or "",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                }
            }
        )
