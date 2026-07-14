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
    EmbeddingService,
    FakeEmbeddingProvider,
    TextEmbeddingRequest,
    TextEmbeddingResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchService,
    RAGAnswerGenerationError,
    RAGAnswerRequest,
    RAGAnswerResponse,
    RAGAnswerService,
    get_rag_answer_service,
    RAGEvaluationRequest,
    RAGEvaluationResponse,
    RAGEvaluationService,
    RetrievalRequest,
    RetrievalResponse,
    RetrievalService,
)
from ai_api.requirements.dependencies import get_requirement_analyzer_service
from ai_api.requirements.exceptions import RequirementAnalysisError
from ai_api.requirements.schemas import (
    RequirementAnalysisRequest,
    RequirementAnalysisResponse,
)
from ai_api.requirements.services import RequirementAnalyzerService
from ai_api.schemas import AnalyzeRequest, AnalyzeResponse
from ai_api.agents import (
    AgentRunRequest,
    AgentRunResponse,
    AgentRuntime,
    ToolRegistry,
    ToolRegistryResponse,
    ToolExecutionError,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolExecutionService,
)


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


@app.exception_handler(ToolExecutionError)
async def tool_execution_exception_handler(
    request: Request,
    exc: ToolExecutionError,
) -> JSONResponse:
    logger.warning(
        "Tool execution error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": "tool_execution_error",
                "message": str(exc),
            }
        },
    )


@app.exception_handler(RAGAnswerGenerationError)
async def rag_answer_generation_exception_handler(
    request: Request,
    exc: RAGAnswerGenerationError,
) -> JSONResponse:
    logger.warning(
        "RAG answer generation error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=502,
        content={
            "error": {
                "type": "rag_answer_generation_error",
                "message": str(exc),
            }
        },
    )


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


@app.post("/rag/embed", response_model=TextEmbeddingResponse)
def embed_texts(
    payload: TextEmbeddingRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TextEmbeddingResponse:
    embedding_provider = FakeEmbeddingProvider(
        dimensions=settings.embedding_dimensions,
    )
    embedding_service = EmbeddingService(
        embedding_provider=embedding_provider,
    )

    return embedding_service.embed_texts(payload.texts)


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


@app.post("/rag/search", response_model=SemanticSearchResponse)
def semantic_search(
    payload: SemanticSearchRequest,
) -> SemanticSearchResponse:
    search_service = SemanticSearchService()

    return search_service.search(
        query=payload.query,
        documents=payload.documents,
        top_k=payload.top_k,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )


@app.post("/rag/answer", response_model=RAGAnswerResponse)
def generate_rag_answer(
    payload: RAGAnswerRequest,
    service: Annotated[
        RAGAnswerService,
        Depends(get_rag_answer_service),
    ],
) -> RAGAnswerResponse:
    return service.answer(
        query=payload.query,
        documents=payload.documents,
        language=payload.language,
        top_k=payload.top_k,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )


@app.post("/rag/evaluate", response_model=RAGEvaluationResponse)
def evaluate_rag_answer(
    payload: RAGEvaluationRequest,
) -> RAGEvaluationResponse:
    evaluation_service = RAGEvaluationService()

    return evaluation_service.evaluate(
        query=payload.query,
        answer=payload.answer,
        context_chunks=payload.context_chunks,
        citations=payload.citations,
        minimum_overall_score=payload.minimum_overall_score,
    )


@app.post("/rag/retrieve", response_model=RetrievalResponse)
def retrieve_context(
    payload: RetrievalRequest,
) -> RetrievalResponse:
    retrieval_service = RetrievalService()

    return retrieval_service.retrieve(
        query=payload.query,
        documents=payload.documents,
        top_k=payload.top_k,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )


@app.post("/agents/run", response_model=AgentRunResponse)
def run_agent(
    payload: AgentRunRequest,
) -> AgentRunResponse:
    agent_runtime = AgentRuntime()

    return agent_runtime.run(
        objective=payload.objective,
        context=payload.context,
        max_steps=payload.max_steps,
        metadata=payload.metadata,
    )


@app.get("/agents/tools", response_model=ToolRegistryResponse)
def list_agent_tools() -> ToolRegistryResponse:
    tool_registry = ToolRegistry()

    return tool_registry.describe()


@app.post("/agents/tools/execute", response_model=ToolExecutionResponse)
def execute_agent_tool(
    payload: ToolExecutionRequest,
) -> ToolExecutionResponse:
    tool_execution_service = ToolExecutionService()

    return tool_execution_service.execute(
        tool_name=payload.tool_name,
        arguments=payload.arguments,
        metadata=payload.metadata,
    )
