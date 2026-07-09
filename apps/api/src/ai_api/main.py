import logging
import time
from collections.abc import Awaitable, Callable
from typing import Annotated, Any
from fastapi import FastAPI, Request, UploadFile, Depends, File, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response
from ai_api.config import Settings, get_settings
from ai_api.llm import (
    LLMHealthResponse,
    LLMProvidersResponse,
    get_llm_health_status,
    get_llm_providers_status,
)
from ai_api.rag import (
    DocumentChunkingRequest,
    DocumentChunkingResponse,
    DocumentIngestionRequest,
    DocumentIngestionResponse,
    DocumentIngestionService,
    DocumentFileIngestionResponse,
    DocumentFileIngestionService,
    TextChunker,
    TextExtractionError,
    TextExtractionResponse,
    TextExtractionService,
    RAGRequestError,
    parse_metadata_json,
)
from ai_api.requirements.dependencies import get_requirement_analyzer_service
from ai_api.requirements.exceptions import RequirementAnalysisError
from ai_api.requirements.schemas import (
    RequirementAnalysisRequest,
    RequirementAnalysisResponse,
)
from ai_api.requirements.services import RequirementAnalyzerService
from ai_api.schemas import AnalyzeRequest, AnalyzeResponse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("ai_api")


app = FastAPI(
    title="Applied AI Engineering Lab API",
    description="Base API for the Applied AI Engineering Lab.",
    version="0.1.0",
)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s completed with status %s in %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


@app.exception_handler(RAGRequestError)
async def rag_request_exception_handler(
    request: Request,
    exc: RAGRequestError,
) -> JSONResponse:
    logger.warning(
        "RAG request error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": "rag_request_error",
                "message": str(exc),
            }
        },
    )


@app.exception_handler(TextExtractionError)
async def text_extraction_exception_handler(
    request: Request,
    exc: TextExtractionError,
) -> JSONResponse:
    logger.warning(
        "Text extraction error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": "text_extraction_error",
                "message": str(exc),
            }
        },
    )


@app.exception_handler(RequirementAnalysisError)
async def requirement_analysis_exception_handler(
    request: Request,
    exc: RequirementAnalysisError,
) -> JSONResponse:
    logger.warning(
        "Requirement analysis error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=502,
        content={
            "error": {
                "type": "requirement_analysis_error",
                "message": "Requirement analysis failed.",
            }
        },
    )



def sanitize_validation_errors(
    errors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sanitized_errors = []

    for error in errors:
        sanitized_error = dict(error)

        ctx = sanitized_error.get("ctx")

        if isinstance(ctx, dict):
            sanitized_error["ctx"] = {
                key: str(value)
                for key, value in ctx.items()
            }

        sanitized_errors.append(sanitized_error)

    return sanitized_errors


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = sanitize_validation_errors(exc.errors())

    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        details,
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "validation_error",
                "message": "Invalid request payload.",
                "details": details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_server_error",
                "message": "An unexpected error occurred.",
            }
        },
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/llm/providers", response_model=LLMProvidersResponse)
def list_llm_providers(
    settings: Annotated[Settings, Depends(get_settings)],
) -> LLMProvidersResponse:
    return get_llm_providers_status(settings)


@app.get("/llm/health", response_model=LLMHealthResponse)
def get_llm_health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> LLMHealthResponse:
    return get_llm_health_status(settings)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(payload: AnalyzeRequest) -> AnalyzeResponse:
    word_count = len(payload.text.split())
    character_count = len(payload.text)

    return AnalyzeResponse(
        original_text=payload.text,
        summary="Initial deterministic analysis. LLM integration will be added in a future module.",
        word_count=word_count,
        character_count=character_count,
        language=payload.language,
    )


@app.post("/requirements/analyze", response_model=RequirementAnalysisResponse)
def analyze_requirement(
    payload: RequirementAnalysisRequest,
    service: Annotated[
        RequirementAnalyzerService,
        Depends(get_requirement_analyzer_service),
    ],
) -> RequirementAnalysisResponse:
    return service.analyze(
        requirement_text=payload.requirement_text,
        language=payload.language,
    )


@app.post("/rag/chunk", response_model=DocumentChunkingResponse)
def chunk_document(
    payload: DocumentChunkingRequest,
) -> DocumentChunkingResponse:
    chunker = TextChunker()

    return chunker.chunk(
        document_text=payload.document_text,
        source=payload.source,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )


@app.post("/rag/ingest", response_model=DocumentIngestionResponse)
def ingest_document(
    payload: DocumentIngestionRequest,
) -> DocumentIngestionResponse:
    ingestion_service = DocumentIngestionService()

    return ingestion_service.ingest(
        document_text=payload.document_text,
        source=payload.source,
        title=payload.title,
        metadata=payload.metadata,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )


@app.post("/rag/ingest-file", response_model=DocumentFileIngestionResponse)
async def ingest_file(
    file: UploadFile = File(...),
    source: str | None = Form(default=None),
    title: str | None = Form(default=None),
    metadata: str | None = Form(default=None),
    chunk_size: int = Form(default=800),
    chunk_overlap: int = Form(default=120),
) -> DocumentFileIngestionResponse:
    parsed_metadata = parse_metadata_json(metadata)
    file_content = await file.read()

    file_ingestion_service = DocumentFileIngestionService()

    return file_ingestion_service.ingest_file(
        file_content=file_content,
        filename=file.filename or "uploaded-file",
        content_type=file.content_type,
        source=source,
        title=title,
        metadata=parsed_metadata,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


@app.post("/rag/extract-text", response_model=TextExtractionResponse)
async def extract_text_from_file(
    file: UploadFile = File(...),
) -> TextExtractionResponse:
    file_content = await file.read()

    extraction_service = TextExtractionService()

    return extraction_service.extract_from_bytes(
        file_content=file_content,
        filename=file.filename or "uploaded-file",
        content_type=file.content_type,
    )
