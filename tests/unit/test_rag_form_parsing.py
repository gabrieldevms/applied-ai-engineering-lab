import pytest
from ai_api.rag import RAGRequestError, parse_metadata_json


def test_parse_metadata_json_should_return_empty_dict_when_value_is_none() -> None:
    assert parse_metadata_json(None) == {}


def test_parse_metadata_json_should_return_empty_dict_when_value_is_blank() -> None:
    assert parse_metadata_json("   ") == {}


def test_parse_metadata_json_should_parse_valid_json_object() -> None:
    metadata = parse_metadata_json('{"domain": "billing", "team": "qa"}')

    assert metadata == {
        "domain": "billing",
        "team": "qa",
    }


def test_parse_metadata_json_should_reject_invalid_json() -> None:
    with pytest.raises(
        RAGRequestError,
        match="metadata must be a valid JSON object.",
    ):
        parse_metadata_json("{invalid-json}")


def test_parse_metadata_json_should_reject_json_array() -> None:
    with pytest.raises(
        RAGRequestError,
        match="metadata must be a valid JSON object.",
    ):
        parse_metadata_json('["billing", "qa"]')
