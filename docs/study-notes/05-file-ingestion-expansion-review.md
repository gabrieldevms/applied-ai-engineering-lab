# File Ingestion Expansion Review

## Purpose

The File Ingestion Expansion milestone improves the RAG and agent workflows by supporting more real-world document and data formats.

Before this milestone, the project was mainly focused on plain text and Markdown extraction.

After this milestone, the project supports both narrative documents and table-oriented files.

## Current Status

Status: completed

The file ingestion layer now supports:

```text
TXT
Markdown
PDF
DOCX
CSV
Excel / XLSX
```

The project also includes a separate structured table extraction path for files that contain tabular data.

## Why This Matters

Real QA and business workflows rarely depend only on plain text.

Common inputs include:

```text
business requirements in DOCX
specifications in PDF
test data in CSV
business rules in spreadsheets
evidence tables in Excel
mixed documentation with embedded tables
```

This milestone makes the project more useful for realistic QA, RAG and agent scenarios.

## Extraction Architecture

The file ingestion expansion uses an extractor-based architecture.

```text
uploaded file
  ↓
file extension detection
  ↓
extractor registry
  ↓
specialized extractor
  ↓
normalized extraction response
```

The main components are:

```text
FileExtractor
FileExtractorRegistry
TextExtractionService
```

Each file extractor is responsible for one or more supported file extensions.

This keeps the pipeline extensible and avoids spreading file-type conditionals across the application.

## Text Extraction Path

The text extraction path is used by the existing RAG ingestion pipeline.

Endpoint:

```http
POST /rag/extract-text
```

The endpoint returns normalized text from supported files.

Supported text extraction formats:

| Format | Extension |
| --- | --- |
| Plain text | `.txt` |
| Markdown | `.md`, `.markdown` |
| PDF | `.pdf` |
| DOCX | `.docx` |
| CSV | `.csv` |
| Excel | `.xlsx` |

## Text Extractors

Current text extractors:

```text
Utf8TextFileExtractor
PDFFileExtractor
DOCXFileExtractor
CSVFileExtractor
ExcelFileExtractor
```

### UTF-8 text extraction

Used for:

```text
.txt
.md
.markdown
```

It decodes files as UTF-8 text and normalizes line endings.

### PDF extraction

Used for:

```text
.pdf
```

It extracts text from PDF pages and returns normalized text.

Encrypted PDFs are not supported at this stage.

### DOCX extraction

Used for:

```text
.docx
```

It extracts paragraph text and table text from Word documents.

### CSV extraction

Used for:

```text
.csv
```

It decodes CSV content as UTF-8, detects the delimiter and normalizes rows into pipe-separated text.

Example output:

```text
Field | Value
status | active
amount | 100.00
```

### Excel extraction

Used for:

```text
.xlsx
```

It reads workbook sheets and normalizes rows into text grouped by sheet.

Example output:

```text
# Sheet: Requirements
Field | Value
status | active

# Sheet: Rules
rule | boleto obrigatório
```

## Structured Table Extraction Path

Structured table extraction is a separate path from text extraction.

Endpoint:

```http
POST /rag/extract-tables
```

This endpoint returns structured table data instead of plain normalized text.

Supported structured table formats:

| Format | Extension |
| --- | --- |
| CSV | `.csv` |
| Excel | `.xlsx` |
| DOCX tables | `.docx` |

## Structured Table Components

Current structured table components:

```text
ExtractedTable
StructuredTableExtractionResponse
StructuredTableExtractor
StructuredTableExtractorRegistry
TableExtractionService
CSVStructuredTableExtractor
ExcelStructuredTableExtractor
DOCXStructuredTableExtractor
```

## Structured Table Response

A structured table contains:

```text
table id
source
filename
table index
rows
row count
column count
sheet name when available
metadata
```

Example conceptual response:

```json
{
  "filename": "data.csv",
  "table_count": 1,
  "tables": [
    {
      "table_id": "table-abc123",
      "filename": "data.csv",
      "table_index": 0,
      "rows": [
        ["Field", "Value"],
        ["status", "active"]
      ],
      "row_count": 2,
      "column_count": 2,
      "sheet_name": null
    }
  ]
}
```

## Relationship with RAG

The project now has two complementary extraction paths:

```text
/rag/extract-text
  returns normalized text for RAG ingestion, chunking, embeddings and retrieval

/rag/extract-tables
  returns structured tables for future data and agent workflows
```

The existing RAG pipeline continues to use normalized text.

Structured table extraction prepares the project for richer data-oriented workflows.

## Relationship with the Future Data Analyst Agent

Structured table extraction is an important foundation for the future Data Analyst Agent.

The future agent may use structured table data to:

```text
understand tabular inputs
inspect headers and rows
infer simple data schemas
validate business rules
generate SQL-like reasoning
support QA evidence generation
```

This is especially useful for QA scenarios involving:

```text
business rules
financial calculations
status transitions
test datasets
spreadsheet-based evidence
database validation requirements
```

## Current Limitations

Known limitations:

```text
PDF extraction depends on text being extractable from the PDF
scanned PDFs and OCR are not supported
legacy .doc files are not supported
legacy .xls files are not supported
CSV extraction currently assumes UTF-8-compatible content
structured table extraction does not yet infer semantic column types
structured table extraction does not yet generate database schemas
structured table extraction is not yet connected to a Data Analyst Agent
```

These limitations are expected at this stage.

The current milestone focuses on extraction foundation, supported formats and structured table output.

## Validation

This milestone was validated through automated tests covering:

```text
file extractor registry
PDF extraction
DOCX extraction
CSV extraction
Excel extraction
text extraction service integration
file ingestion integration
structured table extraction
structured table API endpoint
unsupported file behavior
invalid file behavior
```

## Conclusion

The File Ingestion Expansion milestone makes the project significantly more practical.

The platform can now work with common QA and business file types and provides both normalized text extraction and structured table extraction.

This creates a strong foundation for the next milestone:

```text
Data Analyst Agent foundation
```