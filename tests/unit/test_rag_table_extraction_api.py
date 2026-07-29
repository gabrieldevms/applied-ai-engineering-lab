from fastapi.testclient import TestClient
from ai_api.main import app


client = TestClient(app)


def test_rag_extract_tables_endpoint_should_extract_csv_table() -> None:
    response = client.post(
        "/rag/extract-tables",
        files={
            "file": (
                "data.csv",
                (
                    "Field,Value\n"
                    "status,active\n"
                ).encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["filename"] == "data.csv"
    assert body["table_count"] == 1
    assert body["tables"][0]["rows"] == [
        [
            "Field",
            "Value",
        ],
        [
            "status",
            "active",
        ],
    ]
    assert body["tables"][0]["row_count"] == 2
    assert body["tables"][0]["column_count"] == 2


def test_rag_extract_tables_endpoint_should_reject_unsupported_file_type() -> None:
    response = client.post(
        "/rag/extract-tables",
        files={
            "file": (
                "document.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["type"] == "text_extraction_error"
    assert (
        body["error"]["message"]
        == "Unsupported table extraction file type: .pdf"
    )
