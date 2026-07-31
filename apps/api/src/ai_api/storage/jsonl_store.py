from pathlib import Path
from typing import Generic, TypeVar
from pydantic import BaseModel, ValidationError
from ai_api.storage.paths import ensure_parent_dir
from ai_api.storage.schemas import JsonlStoreMetadata

RecordT = TypeVar("RecordT", bound=BaseModel)


class JsonlStoreReadError(Exception):
    """Raised when a JSONL store cannot read or validate a stored record."""


class JsonlStore(Generic[RecordT]):
    def __init__(
        self,
        file_path: str | Path,
        record_type: type[RecordT],
    ) -> None:
        self.file_path = ensure_parent_dir(file_path)
        self.record_type = record_type

    def append(self, record: RecordT) -> RecordT:
        with self.file_path.open("a", encoding="utf-8") as file:
            file.write(record.model_dump_json())
            file.write("\n")

        return record

    def append_many(self, records: list[RecordT]) -> list[RecordT]:
        if not records:
            return []

        with self.file_path.open("a", encoding="utf-8") as file:
            for record in records:
                file.write(record.model_dump_json())
                file.write("\n")

        return records

    def list_records(self) -> list[RecordT]:
        if not self.file_path.exists():
            return []

        records: list[RecordT] = []

        with self.file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                cleaned_line = line.strip()

                if not cleaned_line:
                    continue

                try:
                    records.append(
                        self.record_type.model_validate_json(cleaned_line)
                    )
                except ValidationError as error:
                    raise JsonlStoreReadError(
                        "Could not validate JSONL record "
                        f"at line {line_number} from {self.file_path}."
                    ) from error
                except ValueError as error:
                    raise JsonlStoreReadError(
                        "Could not parse JSONL record "
                        f"at line {line_number} from {self.file_path}."
                    ) from error

        return records

    def list_recent(self, limit: int = 100) -> list[RecordT]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        return list(reversed(self.list_records()))[:limit]

    def get_by_field(
        self,
        field_name: str,
        value: object,
    ) -> RecordT | None:
        cleaned_field_name = field_name.strip()

        if not cleaned_field_name:
            raise ValueError("field_name cannot be blank")

        for record in self.list_records():
            if getattr(record, cleaned_field_name, None) == value:
                return record

        return None

    def count(self) -> int:
        return len(self.list_records())

    def clear(self) -> None:
        self.file_path.write_text("", encoding="utf-8")

    def metadata(self) -> JsonlStoreMetadata:
        return JsonlStoreMetadata(
            file_path=str(self.file_path),
            record_count=self.count(),
            exists=self.file_path.exists(),
        )
