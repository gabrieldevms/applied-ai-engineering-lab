from collections.abc import Iterable
from pathlib import Path
from typing import Protocol
from ai_api.rag.exceptions import TextExtractionError
from ai_api.rag.schemas import TextExtractionResponse


class FileExtractor(Protocol):
    name: str
    supported_extensions: frozenset[str]

    def extract(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> TextExtractionResponse:
        """Extract normalized content from a supported file."""
        ...


def normalize_extracted_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


class Utf8TextFileExtractor:
    name = "utf-8-text"

    supported_extensions = frozenset(
        {
            ".txt",
            ".md",
            ".markdown",
        }
    )

    def extract(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> TextExtractionResponse:
        cleaned_filename = filename.strip() or "uploaded-file"
        extension = Path(cleaned_filename).suffix.lower()

        if extension not in self.supported_extensions:
            raise TextExtractionError(
                f"Unsupported file type: {extension or 'unknown'}"
            )

        try:
            extracted_text = file_content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise TextExtractionError(
                "File content could not be decoded as UTF-8 text."
            ) from exc

        normalized_text = normalize_extracted_text(extracted_text)

        if not normalized_text:
            raise TextExtractionError("Extracted text is empty.")

        return TextExtractionResponse(
            source=cleaned_filename,
            filename=cleaned_filename,
            content_type=content_type,
            character_count=len(normalized_text),
            text=normalized_text,
            metadata={
                "extension": extension,
                "extraction_method": self.name,
                "extractor": type(self).__name__,
            },
        )


class FileExtractorRegistry:
    def __init__(
        self,
        extractors: Iterable[FileExtractor] | None = None,
    ) -> None:
        selected_extractors = (
            [Utf8TextFileExtractor()]
            if extractors is None
            else list(extractors)
        )

        self._extractors_by_extension: dict[str, FileExtractor] = {}

        for extractor in selected_extractors:
            self.register(extractor)

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return tuple(sorted(self._extractors_by_extension))

    def register(self, extractor: FileExtractor) -> None:
        if not extractor.supported_extensions:
            raise ValueError(
                "File extractor must define at least one supported extension."
            )

        normalized_extensions = {
            self._normalize_extension(extension)
            for extension in extractor.supported_extensions
        }

        for extension in normalized_extensions:
            if extension in self._extractors_by_extension:
                raise ValueError(
                    f"Extractor already registered for extension: {extension}"
                )

        for extension in normalized_extensions:
            self._extractors_by_extension[extension] = extractor

    def get_for_filename(self, filename: str) -> FileExtractor:
        cleaned_filename = filename.strip() or "uploaded-file"
        extension = Path(cleaned_filename).suffix.lower()

        return self.get_for_extension(extension)

    def get_for_extension(self, extension: str) -> FileExtractor:
        normalized_extension = self._normalize_extension(
            extension,
            allow_empty=True,
        )

        extractor = self._extractors_by_extension.get(
            normalized_extension
        )

        if extractor is None:
            raise TextExtractionError(
                "Unsupported file type: "
                f"{normalized_extension or 'unknown'}"
            )

        return extractor

    def _normalize_extension(
        self,
        extension: str,
        allow_empty: bool = False,
    ) -> str:
        normalized_extension = extension.strip().lower()

        if not normalized_extension:
            if allow_empty:
                return ""

            raise ValueError("File extension cannot be blank.")

        if not normalized_extension.startswith("."):
            normalized_extension = f".{normalized_extension}"

        return normalized_extension
