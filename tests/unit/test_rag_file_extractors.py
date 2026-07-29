import pytest

from ai_api.rag.exceptions import TextExtractionError
from ai_api.rag.file_extractors import (
    FileExtractorRegistry,
    Utf8TextFileExtractor,
)
from ai_api.rag.schemas import TextExtractionResponse
from ai_api.rag.text_extraction import TextExtractionService


class CustomFileExtractor:
    name = "custom-text"

    supported_extensions = frozenset(
        {
            ".custom",
        }
    )

    def extract(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> TextExtractionResponse:
        extracted_text = file_content.decode("utf-8").strip()

        return TextExtractionResponse(
            source=filename,
            filename=filename,
            content_type=content_type,
            character_count=len(extracted_text),
            text=extracted_text,
            metadata={
                "extension": ".custom",
                "extraction_method": self.name,
                "extractor": type(self).__name__,
            },
        )


def test_file_extractor_registry_should_register_default_text_extensions() -> None:
    registry = FileExtractorRegistry()

    assert registry.supported_extensions == (
        ".markdown",
        ".md",
        ".txt",
    )


def test_file_extractor_registry_should_resolve_extension_case_insensitively() -> None:
    registry = FileExtractorRegistry()

    extractor = registry.get_for_filename("NOTES.MD")

    assert isinstance(extractor, Utf8TextFileExtractor)


def test_text_extraction_service_should_use_injected_custom_extractor() -> None:
    registry = FileExtractorRegistry(
        extractors=[
            CustomFileExtractor(),
        ]
    )

    service = TextExtractionService(
        extractor_registry=registry,
    )

    response = service.extract_from_bytes(
        file_content=b"Custom file content.",
        filename="example.custom",
        content_type="text/custom",
    )

    assert response.filename == "example.custom"
    assert response.text == "Custom file content."
    assert response.content_type == "text/custom"
    assert response.metadata["extension"] == ".custom"
    assert response.metadata["extraction_method"] == "custom-text"
    assert response.metadata["extractor"] == "CustomFileExtractor"


def test_file_extractor_registry_should_reject_duplicate_extensions() -> None:
    with pytest.raises(
        ValueError,
        match="Extractor already registered for extension:",
    ):
        FileExtractorRegistry(
            extractors=[
                Utf8TextFileExtractor(),
                Utf8TextFileExtractor(),
            ]
        )


def test_empty_file_extractor_registry_should_reject_unknown_extension() -> None:
    registry = FileExtractorRegistry(
        extractors=[],
    )

    with pytest.raises(
        TextExtractionError,
        match="Unsupported file type: .pdf",
    ):
        registry.get_for_filename("document.pdf")
