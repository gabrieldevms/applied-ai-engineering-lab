import pytest
from pydantic import BaseModel
from ai_api.storage import JsonlStore, JsonlStoreReadError


class DemoPersistentRecord(BaseModel):
    record_id: str
    run_id: str
    status: str
    value: int = 0


def test_jsonl_store_should_append_and_list_records(tmp_path) -> None:
    file_path = tmp_path / "records.jsonl"
    store = JsonlStore(
        file_path=file_path,
        record_type=DemoPersistentRecord,
    )

    store.append(
        DemoPersistentRecord(
            record_id="record-1",
            run_id="run-1",
            status="completed",
            value=10,
        )
    )

    records = store.list_records()

    assert len(records) == 1
    assert records[0].record_id == "record-1"
    assert records[0].run_id == "run-1"
    assert records[0].status == "completed"
    assert records[0].value == 10


def test_jsonl_store_should_persist_records_between_instances(tmp_path) -> None:
    file_path = tmp_path / "records.jsonl"

    first_store = JsonlStore(
        file_path=file_path,
        record_type=DemoPersistentRecord,
    )

    first_store.append(
        DemoPersistentRecord(
            record_id="record-1",
            run_id="run-1",
            status="completed",
        )
    )

    second_store = JsonlStore(
        file_path=file_path,
        record_type=DemoPersistentRecord,
    )

    records = second_store.list_records()

    assert len(records) == 1
    assert records[0].record_id == "record-1"


def test_jsonl_store_should_create_parent_directory(tmp_path) -> None:
    file_path = tmp_path / "nested" / "storage" / "records.jsonl"

    store = JsonlStore(
        file_path=file_path,
        record_type=DemoPersistentRecord,
    )

    store.append(
        DemoPersistentRecord(
            record_id="record-1",
            run_id="run-1",
            status="completed",
        )
    )

    assert file_path.exists()


def test_jsonl_store_should_return_empty_list_when_file_does_not_exist(
    tmp_path,
) -> None:
    store = JsonlStore(
        file_path=tmp_path / "missing.jsonl",
        record_type=DemoPersistentRecord,
    )

    assert store.list_records() == []
    assert store.count() == 0


def test_jsonl_store_should_append_many_records(tmp_path) -> None:
    store = JsonlStore(
        file_path=tmp_path / "records.jsonl",
        record_type=DemoPersistentRecord,
    )

    store.append_many(
        [
            DemoPersistentRecord(
                record_id="record-1",
                run_id="run-1",
                status="completed",
            ),
            DemoPersistentRecord(
                record_id="record-2",
                run_id="run-2",
                status="failed",
            ),
        ]
    )

    records = store.list_records()

    assert len(records) == 2
    assert records[0].record_id == "record-1"
    assert records[1].record_id == "record-2"


def test_jsonl_store_should_list_recent_records(tmp_path) -> None:
    store = JsonlStore(
        file_path=tmp_path / "records.jsonl",
        record_type=DemoPersistentRecord,
    )

    store.append_many(
        [
            DemoPersistentRecord(
                record_id="record-1",
                run_id="run-1",
                status="completed",
            ),
            DemoPersistentRecord(
                record_id="record-2",
                run_id="run-2",
                status="completed",
            ),
            DemoPersistentRecord(
                record_id="record-3",
                run_id="run-3",
                status="completed",
            ),
        ]
    )

    records = store.list_recent(limit=2)

    assert [record.record_id for record in records] == [
        "record-3",
        "record-2",
    ]


def test_jsonl_store_should_reject_invalid_recent_limit(tmp_path) -> None:
    store = JsonlStore(
        file_path=tmp_path / "records.jsonl",
        record_type=DemoPersistentRecord,
    )

    with pytest.raises(ValueError, match="limit must be greater than zero"):
        store.list_recent(limit=0)


def test_jsonl_store_should_get_record_by_field(tmp_path) -> None:
    store = JsonlStore(
        file_path=tmp_path / "records.jsonl",
        record_type=DemoPersistentRecord,
    )

    store.append_many(
        [
            DemoPersistentRecord(
                record_id="record-1",
                run_id="run-1",
                status="completed",
            ),
            DemoPersistentRecord(
                record_id="record-2",
                run_id="run-2",
                status="failed",
            ),
        ]
    )

    record = store.get_by_field("run_id", "run-2")

    assert record is not None
    assert record.record_id == "record-2"


def test_jsonl_store_should_return_none_when_field_value_is_not_found(
    tmp_path,
) -> None:
    store = JsonlStore(
        file_path=tmp_path / "records.jsonl",
        record_type=DemoPersistentRecord,
    )

    store.append(
        DemoPersistentRecord(
            record_id="record-1",
            run_id="run-1",
            status="completed",
        )
    )

    assert store.get_by_field("run_id", "missing-run") is None


def test_jsonl_store_should_reject_blank_field_name(tmp_path) -> None:
    store = JsonlStore(
        file_path=tmp_path / "records.jsonl",
        record_type=DemoPersistentRecord,
    )

    with pytest.raises(ValueError, match="field_name cannot be blank"):
        store.get_by_field(" ", "run-1")


def test_jsonl_store_should_clear_records(tmp_path) -> None:
    store = JsonlStore(
        file_path=tmp_path / "records.jsonl",
        record_type=DemoPersistentRecord,
    )

    store.append(
        DemoPersistentRecord(
            record_id="record-1",
            run_id="run-1",
            status="completed",
        )
    )

    store.clear()

    assert store.list_records() == []
    assert store.count() == 0


def test_jsonl_store_should_expose_metadata(tmp_path) -> None:
    file_path = tmp_path / "records.jsonl"

    store = JsonlStore(
        file_path=file_path,
        record_type=DemoPersistentRecord,
    )

    store.append(
        DemoPersistentRecord(
            record_id="record-1",
            run_id="run-1",
            status="completed",
        )
    )

    metadata = store.metadata()

    assert metadata.file_path == str(file_path)
    assert metadata.record_count == 1
    assert metadata.exists is True


def test_jsonl_store_should_ignore_blank_lines(tmp_path) -> None:
    file_path = tmp_path / "records.jsonl"
    file_path.write_text(
        '\n{"record_id":"record-1","run_id":"run-1","status":"completed","value":0}\n\n',
        encoding="utf-8",
    )

    store = JsonlStore(
        file_path=file_path,
        record_type=DemoPersistentRecord,
    )

    records = store.list_records()

    assert len(records) == 1
    assert records[0].record_id == "record-1"


def test_jsonl_store_should_raise_read_error_for_invalid_jsonl(
    tmp_path,
) -> None:
    file_path = tmp_path / "records.jsonl"
    file_path.write_text("not-json\n", encoding="utf-8")

    store = JsonlStore(
        file_path=file_path,
        record_type=DemoPersistentRecord,
    )

    with pytest.raises(
        JsonlStoreReadError,
        match="Could not validate JSONL record at line 1",
    ):
        store.list_records()
