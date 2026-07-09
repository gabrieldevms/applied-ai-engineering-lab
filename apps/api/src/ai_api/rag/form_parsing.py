import json
from typing import Any
from ai_api.rag.exceptions import RAGRequestError


def parse_metadata_json(metadata: str | None) -> dict[str, Any]:
    if metadata is None or not metadata.strip():
        return {}

    try:
        parsed_metadata = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise RAGRequestError(
            "metadata must be a valid JSON object."
        ) from exc

    if not isinstance(parsed_metadata, dict):
        raise RAGRequestError(
            "metadata must be a valid JSON object."
        )

    return parsed_metadata
