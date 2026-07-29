from io import BytesIO
import pytest
from openpyxl import Workbook
from ai_api.rag.exceptions import TextExtractionError
from ai_api.rag.file_extractors import CSVFileExtractor, ExcelFileExtractor
from ai_api.rag.text_extraction import TextExtractionService


def _build_xlsx_bytes() -> bytes:
    buffer = BytesIO()

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Requirements"
    worksheet.append(
        [
            "Field",
            "Value",
        ]
    )
    worksheet.append(
        [
            "status",
            "active",
        ]
    )

    rules_sheet = workbook.create_sheet("Rules")
    rules_sheet.append(
        [
            "rule",
            "boleto obrigatório",
        ]
    )

    workbook.save(buffer)

    return buffer.getvalue()


def test_csv_file_extractor_should_extract_rows_as_text() -> None:
    extractor = CSVFileExtractor()

    response = extractor.extract(
        file_content=(
            "Field,Value\n"
            "status,active\n"
            "amount,100.00\n"
        ).encode("utf-8"),
        filename="data.csv",
        content_type="text/csv",
    )

    assert response.filename == "data.csv"
    assert "Field | Value" in response.text
    assert "status | active" in response.text
    assert "amount | 100.00" in response.text
    assert response.content_type == "text/csv"
    assert response.metadata["extension"] == ".csv"
    assert response.metadata["extraction_method"] == "csv"
    assert response.metadata["extractor"] == "CSVFileExtractor"
    assert response.metadata["row_count"] == 3
    assert response.metadata["column_count"] == 2
    assert response.metadata["delimiter"] == ","


def test_text_extraction_service_should_extract_csv_with_default_registry() -> None:
    service = TextExtractionService()

    response = service.extract_from_bytes(
        file_content=(
            "Field,Value\n"
            "status,active\n"
        ).encode("utf-8"),
        filename="sample.csv",
        content_type="text/csv",
    )

    assert "Field | Value" in response.text
    assert "status | active" in response.text
    assert response.metadata["extractor"] == "CSVFileExtractor"


def test_csv_file_extractor_should_reject_invalid_utf8_content() -> None:
    extractor = CSVFileExtractor()

    with pytest.raises(
        TextExtractionError,
        match="CSV content could not be decoded as UTF-8 text.",
    ):
        extractor.extract(
            file_content=b"\xff\xfe\xfa",
            filename="broken.csv",
            content_type="text/csv",
        )


def test_excel_file_extractor_should_extract_rows_from_workbook() -> None:
    extractor = ExcelFileExtractor()

    response = extractor.extract(
        file_content=_build_xlsx_bytes(),
        filename="requirements.xlsx",
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    assert response.filename == "requirements.xlsx"
    assert "# Sheet: Requirements" in response.text
    assert "Field | Value" in response.text
    assert "status | active" in response.text
    assert "# Sheet: Rules" in response.text
    assert "rule | boleto obrigatório" in response.text
    assert response.metadata["extension"] == ".xlsx"
    assert response.metadata["extraction_method"] == "excel"
    assert response.metadata["extractor"] == "ExcelFileExtractor"
    assert response.metadata["sheet_count"] == 2
    assert response.metadata["sheet_names"] == [
        "Requirements",
        "Rules",
    ]
    assert response.metadata["row_count"] == 3
    assert response.metadata["column_count"] == 2


def test_text_extraction_service_should_extract_xlsx_with_default_registry() -> None:
    service = TextExtractionService()

    response = service.extract_from_bytes(
        file_content=_build_xlsx_bytes(),
        filename="sample.xlsx",
    )

    assert "# Sheet: Requirements" in response.text
    assert "status | active" in response.text
    assert response.metadata["extractor"] == "ExcelFileExtractor"


def test_excel_file_extractor_should_reject_invalid_xlsx_content() -> None:
    extractor = ExcelFileExtractor()

    with pytest.raises(
        TextExtractionError,
        match="Excel content could not be extracted.",
    ):
        extractor.extract(
            file_content=b"not a real xlsx file",
            filename="broken.xlsx",
        )
