from ai_api.rag.file_extractors import (
    FileExtractorRegistry,
    Utf8TextFileExtractor,
)
from ai_api.rag.schemas import TextExtractionResponse


SUPPORTED_TEXT_EXTENSIONS = (
    Utf8TextFileExtractor.supported_extensions
)


class TextExtractionService:
    def __init__(
        self,
        extractor_registry: FileExtractorRegistry | None = None,
    ) -> None:
        self.extractor_registry = (
            extractor_registry
            if extractor_registry is not None
            else FileExtractorRegistry()
        )

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return self.extractor_registry.supported_extensions

    def extract_from_bytes(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> TextExtractionResponse:
        cleaned_filename = filename.strip() or "uploaded-file"

        extractor = self.extractor_registry.get_for_filename(
            cleaned_filename
        )

        return extractor.extract(
            file_content=file_content,
            filename=cleaned_filename,
            content_type=content_type,
        )
    