import math
from collections.abc import Sequence
from typing import Protocol

from ai_api.rag.schemas import VectorRecord, VectorSearchResult


class VectorStore(Protocol):
    def upsert(self, records: Sequence[VectorRecord]) -> None:
        """Insert or update vector records."""
        ...

    def get(self, record_id: str) -> VectorRecord | None:
        """Get a vector record by ID."""
        ...

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = 3,
    ) -> list[VectorSearchResult]:
        """Search the most similar records for a query vector."""
        ...

    def count(self) -> int:
        """Return the number of stored records."""
        ...


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, records: Sequence[VectorRecord]) -> None:
        if not records:
            raise ValueError("records cannot be empty")

        for record in records:
            self._validate_vector(record.vector)
            self._records[record.record_id] = record

    def get(self, record_id: str) -> VectorRecord | None:
        return self._records.get(record_id)

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = 3,
    ) -> list[VectorSearchResult]:
        query_values = list(query_vector)

        if top_k < 1:
            raise ValueError("top_k must be greater than zero")

        self._validate_vector(query_values)

        results = [
            VectorSearchResult(
                record_id=record.record_id,
                text=record.text,
                score=round(
                    self._cosine_similarity(query_values, record.vector),
                    6,
                ),
                metadata=record.metadata,
            )
            for record in self._records.values()
        ]

        return sorted(
            results,
            key=lambda result: result.score,
            reverse=True,
        )[:top_k]

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()

    def _validate_vector(self, vector: Sequence[float]) -> None:
        if not vector:
            raise ValueError("vector cannot be empty")

    def _cosine_similarity(
        self,
        first_vector: Sequence[float],
        second_vector: Sequence[float],
    ) -> float:
        if len(first_vector) != len(second_vector):
            raise ValueError(
                "query vector and stored vectors must have the same dimensions"
            )

        first_norm = math.sqrt(
            sum(value * value for value in first_vector)
        )
        second_norm = math.sqrt(
            sum(value * value for value in second_vector)
        )

        if first_norm == 0 or second_norm == 0:
            return 0.0

        dot_product = sum(
            first_value * second_value
            for first_value, second_value in zip(
                first_vector,
                second_vector,
                strict=True,
            )
        )

        return dot_product / (first_norm * second_norm)
