from pathlib import Path
from ai_api.rag.exceptions import TextExtractionError
from ai_api.rag.schemas import TextExtractionResponse


SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}


class TextExtractionService:
    def extract_from_bytes(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> TextExtractionResponse:
        cleaned_filename = filename.strip() or "uploaded-file"
        extension = Path(cleaned_filename).suffix.lower()

        if extension not in SUPPORTED_TEXT_EXTENSIONS:
            raise TextExtractionError(
                f"Unsupported file type: {extension or 'unknown'}"
            )

        try:
            extracted_text = file_content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise TextExtractionError(
                "File content could not be decoded as UTF-8 text."
            ) from exc

        normalized_text = self._normalize_text(extracted_text)

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
                "extraction_method": "utf-8-text",
            },
        )

    def _normalize_text(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n").strip()
