from typing import Any, Literal
from pydantic import BaseModel, Field


StorageBackendName = Literal[
    "memory",
    "local_jsonl",
]


class StorageLocation(BaseModel):
    backend: StorageBackendName
    base_dir: str
    path: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class JsonlStoreMetadata(BaseModel):
    file_path: str
    record_count: int
    exists: bool
