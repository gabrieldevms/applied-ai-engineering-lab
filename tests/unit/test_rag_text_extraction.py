import pytest

from ai_api.rag import TextExtractionError, TextExtractionService


def test_text_extraction_should_extract_txt_file() -> None:
    service = TextExtractionService()

    response = service.extract_from_bytes(
        file_content="Texto do requisito.".encode("utf-8"),
        filename="requirement.txt",
        content_type="text/plain",
    )

    assert response.filename == "requirement.txt"
    assert response.source == "requirement.txt"
    assert response.content_type == "text/plain"
    assert response.text == "Texto do requisito."
    assert response.character_count == len("Texto do requisito.")
    assert response.metadata["extension"] == ".txt"


def test_text_extraction_should_extract_markdown_file() -> None:
    service = TextExtractionService()

    response = service.extract_from_bytes(
        file_content="# Título\n\nConteúdo do documento.".encode("utf-8"),
        filename="notes.md",
        content_type="text/markdown",
    )

    assert response.filename == "notes.md"
    assert response.text.startswith("# Título")
    assert response.metadata["extension"] == ".md"


def test_text_extraction_should_normalize_line_breaks() -> None:
    service = TextExtractionService()

    response = service.extract_from_bytes(
        file_content="Linha 1\r\nLinha 2\rLinha 3".encode("utf-8"),
        filename="document.txt",
    )

    assert response.text == "Linha 1\nLinha 2\nLinha 3"


def test_text_extraction_should_reject_unsupported_file_type() -> None:
    service = TextExtractionService()

    with pytest.raises(
        TextExtractionError,
        match="Unsupported file type: .pdf",
    ):
        service.extract_from_bytes(
            file_content=b"fake pdf content",
            filename="document.pdf",
        )


def test_text_extraction_should_reject_empty_text() -> None:
    service = TextExtractionService()

    with pytest.raises(
        TextExtractionError,
        match="Extracted text is empty.",
    ):
        service.extract_from_bytes(
            file_content="   ".encode("utf-8"),
            filename="empty.txt",
        )


def test_text_extraction_should_reject_invalid_utf8() -> None:
    service = TextExtractionService()

    with pytest.raises(
        TextExtractionError,
        match="File content could not be decoded as UTF-8 text.",
    ):
        service.extract_from_bytes(
            file_content=b"\xff\xfe\x00\x00",
            filename="invalid.txt",
        )
