import pytest
from ai_api.rag import (
    DocumentFileIngestionService,
    TextExtractionError,
)


def test_file_ingestion_should_extract_and_ingest_text_file() -> None:
    service = DocumentFileIngestionService()

    response = service.ingest_file(
        file_content="Como cliente, quero renegociar minha dívida.".encode("utf-8"),
        filename="requirement.txt",
        content_type="text/plain",
        source="requirement-001",
        title="Renegociação de dívida",
        metadata={"domain": "billing"},
        chunk_size=800,
        chunk_overlap=120,
    )

    assert response.document.source == "requirement-001"
    assert response.document.title == "Renegociação de dívida"
    assert response.document.metadata["domain"] == "billing"
    assert response.document.metadata["filename"] == "requirement.txt"
    assert response.document.metadata["extraction"]["extension"] == ".txt"

    assert response.total_chunks == 1
    assert response.chunks[0].metadata["document_id"] == response.document.document_id
    assert response.extraction_metadata["filename"] == "requirement.txt"


def test_file_ingestion_should_use_filename_as_source_when_source_is_not_provided() -> None:
    service = DocumentFileIngestionService()

    response = service.ingest_file(
        file_content="Texto do documento.".encode("utf-8"),
        filename="notes.md",
        content_type="text/markdown",
    )

    assert response.document.source == "notes.md"
    assert response.document.metadata["filename"] == "notes.md"
    assert response.extraction_metadata["extension"] == ".md"


def test_file_ingestion_should_reject_unsupported_file_type() -> None:
    service = DocumentFileIngestionService()

    with pytest.raises(
        TextExtractionError,
        match="Unsupported file type: .exe",
    ):
        service.ingest_file(
            file_content=b"fake executable content",
            filename="document.exe",
            content_type="application/octet-stream",
        )
