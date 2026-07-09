import pytest

from ai_api.rag import DocumentIngestionService


def test_document_ingestion_should_create_document_and_chunks() -> None:
    service = DocumentIngestionService()

    response = service.ingest(
        document_text="Como cliente, quero renegociar minha dívida.",
        source="requirement-001",
        title="Renegociação de dívida",
        metadata={"domain": "billing"},
        chunk_size=800,
        chunk_overlap=120,
    )

    assert response.document.source == "requirement-001"
    assert response.document.title == "Renegociação de dívida"
    assert response.document.character_count > 0
    assert response.document.metadata["domain"] == "billing"

    assert response.total_chunks == 1
    assert response.chunks[0].source == response.document.document_id
    assert response.chunks[0].metadata["document_id"] == response.document.document_id
    assert response.chunks[0].metadata["original_source"] == "requirement-001"


def test_document_ingestion_should_create_stable_document_id_for_same_content() -> None:
    service = DocumentIngestionService()

    first_response = service.ingest(
        document_text="Texto do documento.",
        source="Document A",
    )
    second_response = service.ingest(
        document_text="Texto do documento.",
        source="Document A",
    )

    assert first_response.document.document_id == second_response.document.document_id


def test_document_ingestion_should_create_different_document_id_for_different_content() -> None:
    service = DocumentIngestionService()

    first_response = service.ingest(
        document_text="Texto do documento A.",
        source="Document A",
    )
    second_response = service.ingest(
        document_text="Texto do documento B.",
        source="Document A",
    )

    assert first_response.document.document_id != second_response.document.document_id


def test_document_ingestion_should_reject_blank_document_text() -> None:
    service = DocumentIngestionService()

    with pytest.raises(ValueError, match="document_text cannot be blank"):
        service.ingest(document_text="   ")


def test_document_ingestion_should_reject_blank_source() -> None:
    service = DocumentIngestionService()

    with pytest.raises(ValueError, match="source cannot be blank"):
        service.ingest(
            document_text="Texto válido.",
            source="   ",
        )
