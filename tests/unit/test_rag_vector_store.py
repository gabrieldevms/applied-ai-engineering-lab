import pytest
from pydantic import ValidationError

from ai_api.rag import InMemoryVectorStore, VectorRecord


def test_in_memory_vector_store_should_upsert_and_get_record() -> None:
    store = InMemoryVectorStore()

    record = VectorRecord(
        record_id="doc-1-chunk-0",
        text="Texto sobre boleto.",
        vector=[1.0, 0.0, 0.0],
        metadata={"document_id": "doc-1"},
    )

    store.upsert([record])

    stored_record = store.get("doc-1-chunk-0")

    assert store.count() == 1
    assert stored_record is not None
    assert stored_record.text == "Texto sobre boleto."
    assert stored_record.metadata["document_id"] == "doc-1"


def test_in_memory_vector_store_should_replace_existing_record() -> None:
    store = InMemoryVectorStore()

    first_record = VectorRecord(
        record_id="same-id",
        text="Texto antigo.",
        vector=[1.0, 0.0],
    )
    updated_record = VectorRecord(
        record_id="same-id",
        text="Texto atualizado.",
        vector=[0.0, 1.0],
    )

    store.upsert([first_record])
    store.upsert([updated_record])

    stored_record = store.get("same-id")

    assert store.count() == 1
    assert stored_record is not None
    assert stored_record.text == "Texto atualizado."
    assert stored_record.vector == [0.0, 1.0]


def test_in_memory_vector_store_should_search_by_cosine_similarity() -> None:
    store = InMemoryVectorStore()

    store.upsert(
        [
            VectorRecord(
                record_id="boleto",
                text="Texto sobre boleto e cobrança.",
                vector=[1.0, 0.0, 0.0],
            ),
            VectorRecord(
                record_id="login",
                text="Texto sobre login e autenticação.",
                vector=[0.0, 1.0, 0.0],
            ),
            VectorRecord(
                record_id="mixed",
                text="Texto parcialmente relacionado a boleto.",
                vector=[0.8, 0.2, 0.0],
            ),
        ]
    )

    results = store.search(
        query_vector=[1.0, 0.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].record_id == "boleto"
    assert results[0].score == 1.0
    assert results[1].record_id == "mixed"


def test_in_memory_vector_store_should_limit_results_by_top_k() -> None:
    store = InMemoryVectorStore()

    store.upsert(
        [
            VectorRecord(record_id="a", text="A", vector=[1.0, 0.0]),
            VectorRecord(record_id="b", text="B", vector=[0.9, 0.1]),
            VectorRecord(record_id="c", text="C", vector=[0.0, 1.0]),
        ]
    )

    results = store.search(
        query_vector=[1.0, 0.0],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].record_id == "a"


def test_in_memory_vector_store_should_return_empty_results_when_store_is_empty() -> None:
    store = InMemoryVectorStore()

    results = store.search(
        query_vector=[1.0, 0.0],
        top_k=3,
    )

    assert results == []


def test_in_memory_vector_store_should_clear_records() -> None:
    store = InMemoryVectorStore()

    store.upsert(
        [
            VectorRecord(
                record_id="doc-1",
                text="Texto.",
                vector=[1.0, 0.0],
            )
        ]
    )

    store.clear()

    assert store.count() == 0
    assert store.get("doc-1") is None


def test_in_memory_vector_store_should_reject_empty_upsert() -> None:
    store = InMemoryVectorStore()

    with pytest.raises(ValueError, match="records cannot be empty"):
        store.upsert([])


def test_in_memory_vector_store_should_reject_invalid_top_k() -> None:
    store = InMemoryVectorStore()

    with pytest.raises(ValueError, match="top_k must be greater than zero"):
        store.search(
            query_vector=[1.0, 0.0],
            top_k=0,
        )


def test_in_memory_vector_store_should_reject_dimension_mismatch() -> None:
    store = InMemoryVectorStore()

    store.upsert(
        [
            VectorRecord(
                record_id="doc-1",
                text="Texto.",
                vector=[1.0, 0.0, 0.0],
            )
        ]
    )

    with pytest.raises(
        ValueError,
        match="query vector and stored vectors must have the same dimensions",
    ):
        store.search(
            query_vector=[1.0, 0.0],
            top_k=1,
        )


def test_vector_record_should_reject_empty_vector() -> None:
    with pytest.raises(ValidationError):
        VectorRecord(
            record_id="doc-1",
            text="Texto.",
            vector=[],
        )
