from typing import Any
from ai_api.rag.ingestion import DocumentIngestionService
from ai_api.rag.schemas import DocumentFileIngestionResponse
from ai_api.rag.text_extraction import TextExtractionService


class DocumentFileIngestionService:
    def __init__(
        self,
        text_extraction_service: TextExtractionService | None = None,
        ingestion_service: DocumentIngestionService | None = None,
    ) -> None:
        self.text_extraction_service = (
            text_extraction_service or TextExtractionService()
        )
        self.ingestion_service = ingestion_service or DocumentIngestionService()

    def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
        source: str | None = None,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> DocumentFileIngestionResponse:
        extraction_response = self.text_extraction_service.extract_from_bytes(
            file_content=file_content,
            filename=filename,
            content_type=content_type,
        )

        effective_source = (
            source.strip()
            if source is not None and source.strip()
            else extraction_response.source
        )

        cleaned_title = (
            title.strip()
            if title is not None and title.strip()
            else None
        )

        merged_metadata = {
            **(metadata or {}),
            "filename": extraction_response.filename,
            "content_type": extraction_response.content_type or "",
            "extraction": extraction_response.metadata,
        }

        ingestion_response = self.ingestion_service.ingest(
            document_text=extraction_response.text,
            source=effective_source,
            title=cleaned_title,
            metadata=merged_metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return DocumentFileIngestionResponse(
            document=ingestion_response.document,
            total_chunks=ingestion_response.total_chunks,
            chunks=ingestion_response.chunks,
            extraction_metadata={
                "filename": extraction_response.filename,
                "content_type": extraction_response.content_type or "",
                "character_count": extraction_response.character_count,
                **extraction_response.metadata,
            },
        )
