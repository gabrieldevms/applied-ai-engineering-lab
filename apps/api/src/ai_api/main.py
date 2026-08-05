import logging
import time
from collections.abc import Awaitable, Callable
from typing import Annotated, Any
from fastapi import Depends, FastAPI, File, Query, Form, Request, UploadFile
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
    StructuredTableExtractionResponse,
    TableExtractionService,
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
    QAAgentRunRequest,
    QAAgentRunResponse,
    QAAgentService,
    AgentPlanRequest,
    AgentPlanResponse,
    AgentPlanningService,
    ToolRegistry,
    get_agent_planning_service,
    AgentToolSelectionRequest,
    AgentToolSelectionResponse,
    AgentToolSelectionService,
    get_agent_tool_selection_service,
    AgentMultiStepExecutionRequest,
    AgentMultiStepExecutionResponse,
    AgentMultiStepExecutionService,
    get_agent_multi_step_execution_service,
    AgentExecutionLogListResponse,
    AgentExecutionLogService,
    get_agent_execution_log_service,
    AgentEvaluationRequest,
    AgentEvaluationResponse,
    AgentEvaluationService,
    SpecializedAgentRegistry,
    SpecializedAgentRegistryResponse,
    get_specialized_agent_registry,
    QAAgentEvaluationRequest,
    QAAgentEvaluationResponse,
    QAAgentEvaluationService,
)
from ai_api.data_analysis import (
    DataAnalystAgentEvaluationRequest,
    DataAnalystAgentEvaluationResponse,
    DataAnalystAgentEvaluationService,
    DataAnalystAgentRequest,
    DataAnalystAgentResponse,
    DataAnalystAgentService,
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    NaturalLanguageSQLRequest,
    SQLExecutionError,
    SQLExecutionRequest,
    SQLExecutionResponse,
    SQLGenerationError,
    SQLGenerationResponse,
    SQLWorkflowRequest,
    SQLWorkflowResponse,
    SQLiteReadOnlyQueryExecutor,
    get_data_analyst_agent_evaluation_service,
    get_data_analyst_agent_service,
    get_data_analyst_sql_generation_service,
    get_data_analyst_sql_workflow_service,
    get_sql_query_executor,
    SQLRegressionSuiteRequest,
    SQLRegressionSuiteResponse,
    SQLWorkflowRegressionService,
    get_sql_workflow_regression_service,
)
from ai_api.agents.dependencies import (
    get_agent_runtime,
    get_tool_execution_service,
    get_qa_agent_service,
    get_qa_agent_evaluation_service,
)
from ai_api.multi_agent import (
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotResponse,
    MultiAgentQACopilotService,
    get_multi_agent_qa_copilot_service,
    MultiAgentQACopilotEvaluationRequest,
    MultiAgentQACopilotEvaluationResponse,
    MultiAgentQACopilotEvaluationService,
    get_multi_agent_qa_copilot_evaluation_service,
)
from ai_api.evals import (
    EvaluationDatasetValidationResponse,
    GoldenEvaluationDataset,
    GoldenEvaluationDatasetService,
    GoldenEvaluationDatasetValidationService,
    get_golden_evaluation_dataset_service,
    get_golden_evaluation_dataset_validation_service,
    GoldenEvaluationDatasetRunRequest,
    GoldenEvaluationDatasetRunResponse,
    GoldenEvaluationDatasetRunnerService,
    get_golden_evaluation_dataset_runner_service,
    PromptRegressionEvaluationService,
    PromptRegressionRunRequest,
    PromptRegressionRunResponse,
    PromptRegressionSuite,
    PromptRegressionSuiteService,
    get_prompt_regression_evaluation_service,
    get_prompt_regression_suite_service,
    AIEvaluationReportAggregationRequest,
    AIEvaluationReportAggregationResponse,
    AIEvaluationReportAggregationService,
    get_ai_evaluation_report_aggregation_service,
    EvaluationTelemetryEvent,
    EvaluationTelemetryEventsResponse,
    EvaluationTelemetryRecordRequest,
    EvaluationTelemetryService,
    EvaluationTelemetrySummaryRequest,
    EvaluationTelemetrySummaryResponse,
    get_evaluation_telemetry_service,
    EvaluationTelemetryInstrumentationService,
    get_evaluation_telemetry_instrumentation_service,
    LLMOutputEvaluationRunRequest,
    LLMOutputEvaluationRunResponse,
    LLMOutputEvaluationService,
    LLMOutputEvaluationSuite,
    LLMOutputEvaluationSuiteService,
    RAGRegressionEvaluationService,
    RAGRegressionRunRequest,
    RAGRegressionRunResponse,
    RAGRegressionSuite,
    RAGRegressionSuiteService,
    get_llm_output_evaluation_service,
    get_llm_output_evaluation_suite_service,
    get_rag_regression_evaluation_service,
    get_rag_regression_suite_service,
    AgentRegressionEvaluationService,
    AgentRegressionRunRequest,
    AgentRegressionRunResponse,
    AgentRegressionSuite,
    AgentRegressionSuiteService,
    ToolCallingEvaluationRunRequest,
    ToolCallingEvaluationRunResponse,
    ToolCallingEvaluationService,
    ToolCallingEvaluationSuite,
    ToolCallingEvaluationSuiteService,
    get_agent_regression_evaluation_service,
    get_agent_regression_suite_service,
    get_tool_calling_evaluation_service,
    get_tool_calling_evaluation_suite_service,
    MultiAgentCopilotRegressionEvaluationService,
    MultiAgentCopilotRegressionRunRequest,
    MultiAgentCopilotRegressionRunResponse,
    MultiAgentCopilotRegressionSuite,
    MultiAgentCopilotRegressionSuiteService,
    get_multi_agent_copilot_regression_evaluation_service,
    get_multi_agent_copilot_regression_suite_service,
    LLMAsJudgeEvaluationRunRequest,
    LLMAsJudgeEvaluationRunResponse,
    LLMAsJudgeEvaluationService,
    LLMAsJudgeEvaluationSuite,
    LLMAsJudgeEvaluationSuiteService,
    get_llm_as_judge_evaluation_service,
    get_llm_as_judge_evaluation_suite_service,
    CIEvaluationPipelineRunRequest,
    CIEvaluationPipelineRunResponse,
    CIEvaluationPipelineService,
    get_ci_evaluation_pipeline_service,
    AIUsageRecord,
    AIUsageRecordRequest,
    AIUsageRecordsResponse,
    AIUsageSummaryRequest,
    AIUsageSummaryResponse,
    AIUsageTrackingService,
    get_ai_usage_tracking_service,
    AIRetrievalQualityRecord,
    AIRetrievalQualityRecordRequest,
    AIRetrievalQualityRecordsResponse,
    AIRetrievalQualitySummaryRequest,
    AIRetrievalQualitySummaryResponse,
    AIRetrievalQualityTelemetryService,
    get_ai_retrieval_quality_telemetry_service,
    AIAgentExecutionRecord,
    AIAgentExecutionRecordRequest,
    AIAgentExecutionRecordsResponse,
    AIAgentExecutionSummaryRequest,
    AIAgentExecutionSummaryResponse,
    AIAgentExecutionTelemetryService,
    get_ai_agent_execution_telemetry_service,
    AIMultiAgentExecutionRecord,
    AIMultiAgentExecutionRecordRequest,
    AIMultiAgentExecutionRecordsResponse,
    AIMultiAgentExecutionSummaryRequest,
    AIMultiAgentExecutionSummaryResponse,
    AIMultiAgentExecutionTelemetryService,
    get_ai_multi_agent_execution_telemetry_service,
    AIObservabilityDashboardResponse,
    AIObservabilityDashboardService,
    get_ai_observability_dashboard_service,
)
from ai_api.evals.dependencies import get_ai_execution_history_service
from ai_api.evals.execution_history import (
    AIExecutionHistoryResponse,
    AIExecutionHistoryService,
)
from ai_api.security import (
    PromptInjectionAssessmentRequest,
    PromptInjectionAssessmentResponse,
    PromptInjectionDetectionService,
    BlockedToolCallTelemetryRecordsResponse,
    BlockedToolCallTelemetryService,
    PromptInjectionTelemetryRecordsResponse,
    PromptInjectionTelemetryRequest,
    PromptInjectionTelemetryService,
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


@app.exception_handler(SQLGenerationError)
async def sql_generation_exception_handler(
    request: Request,
    exc: SQLGenerationError,
) -> JSONResponse:
    logger.warning(
        "SQL generation error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=502,
        content={
            "error": {
                "type": "sql_generation_error",
                "message": str(exc),
            }
        },
    )


@app.exception_handler(SQLExecutionError)
async def sql_execution_exception_handler(
    request: Request,
    exc: SQLExecutionError,
) -> JSONResponse:
    logger.warning(
        "SQL execution error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": "sql_execution_error",
                "message": str(exc),
            }
        },
    )


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


@app.post("/data-analysis/sql/generate", response_model=SQLGenerationResponse,)
def generate_sql(
    payload: NaturalLanguageSQLRequest,
    service: Annotated[
        DataAnalystSQLGenerationService,
        Depends(get_data_analyst_sql_generation_service),
    ],
) -> SQLGenerationResponse:
    return service.generate(payload)


@app.post("/data-analysis/sql/execute", response_model=SQLExecutionResponse,)
def execute_sql(
    payload: SQLExecutionRequest,
    executor: Annotated[
        SQLiteReadOnlyQueryExecutor,
        Depends(get_sql_query_executor),
    ],
) -> SQLExecutionResponse:
    return executor.execute(payload)


@app.post("/data-analysis/sql/run", response_model=SQLWorkflowResponse,)
def run_sql_workflow(
    payload: SQLWorkflowRequest,
    service: Annotated[
        DataAnalystSQLWorkflowService,
        Depends(get_data_analyst_sql_workflow_service),
    ],
) -> SQLWorkflowResponse:
    return service.run(payload)


@app.post(
    "/data-analysis/sql/regression/run",
    response_model=SQLRegressionSuiteResponse,
)
def run_sql_workflow_regression_suite(
    payload: SQLRegressionSuiteRequest,
    service: Annotated[
        SQLWorkflowRegressionService,
        Depends(get_sql_workflow_regression_service),
    ],
) -> SQLRegressionSuiteResponse:
    return service.run_suite(payload)


@app.post("/data-analysis/agent/run", response_model=DataAnalystAgentResponse,)
def run_data_analyst_agent(
    payload: DataAnalystAgentRequest,
    service: Annotated[
        DataAnalystAgentService,
        Depends(get_data_analyst_agent_service),
    ],
) -> DataAnalystAgentResponse:
    return service.run(payload)


@app.post("/data-analysis/agent/evaluate", response_model=DataAnalystAgentEvaluationResponse,)
def evaluate_data_analyst_agent(
    payload: DataAnalystAgentEvaluationRequest,
    service: Annotated[
        DataAnalystAgentEvaluationService,
        Depends(get_data_analyst_agent_evaluation_service),
    ],
) -> DataAnalystAgentEvaluationResponse:
    return service.evaluate(payload)


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


@app.post("/rag/extract-tables", response_model=StructuredTableExtractionResponse)
async def extract_tables_from_file(
    file: Annotated[UploadFile, File(...)],
) -> StructuredTableExtractionResponse:
    file_content = await file.read()

    service = TableExtractionService()

    return service.extract_from_bytes(
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
    runtime: Annotated[
        AgentRuntime,
        Depends(get_agent_runtime),
    ],
) -> AgentRunResponse:
    return runtime.run(
        objective=payload.objective,
        context=payload.context,
        max_steps=payload.max_steps,
        tool_calls=payload.tool_calls,
        metadata=payload.metadata,
    )


@app.get("/agents/tools", response_model=ToolRegistryResponse)
def list_agent_tools() -> ToolRegistryResponse:
    tool_registry = ToolRegistry()

    return tool_registry.describe()


@app.get("/agents/specialized", response_model=SpecializedAgentRegistryResponse,)
def list_specialized_agents(
    registry: Annotated[
        SpecializedAgentRegistry,
        Depends(get_specialized_agent_registry),
    ],
) -> SpecializedAgentRegistryResponse:
    return registry.to_response()


@app.post(
    "/agents/tools/execute",
    response_model=ToolExecutionResponse,
)
def execute_tool(
    payload: ToolExecutionRequest,
    service: Annotated[
        ToolExecutionService,
        Depends(get_tool_execution_service),
    ],
) -> ToolExecutionResponse:
    return service.execute(
        tool_name=payload.tool_name,
        arguments=payload.arguments,
        metadata=payload.metadata,
    )


@app.post("/agents/qa/run", response_model=QAAgentRunResponse)
def run_qa_agent(
    payload: QAAgentRunRequest,
    qa_agent_service: Annotated[
        QAAgentService,
        Depends(get_qa_agent_service),
    ],
) -> QAAgentRunResponse:
    return qa_agent_service.run(
        requirement_text=payload.requirement_text,
        knowledge_documents=payload.knowledge_documents,
        data_validation=payload.data_validation,
        language=payload.language,
        top_k=payload.top_k,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
        max_steps=payload.max_steps,
        metadata=payload.metadata,
    )


@app.post(
    "/agents/qa/evaluate",
    response_model=QAAgentEvaluationResponse,
)
def evaluate_qa_agent(
    payload: QAAgentEvaluationRequest,
    service: Annotated[
        QAAgentEvaluationService,
        Depends(get_qa_agent_evaluation_service),
    ],
) -> QAAgentEvaluationResponse:
    return service.evaluate(payload)


@app.post("/agents/plan", response_model=AgentPlanResponse)
def plan_agent_execution(
    payload: AgentPlanRequest,
    planning_service: Annotated[
        AgentPlanningService,
        Depends(get_agent_planning_service),
    ],
) -> AgentPlanResponse:
    available_tools = (
        payload.available_tools
        if payload.available_tools
        else ToolRegistry().list_tools()
    )

    return planning_service.plan(
        objective=payload.objective,
        context=payload.context,
        available_tools=available_tools,
        max_steps=payload.max_steps,
        language=payload.language,
        metadata=payload.metadata,
    )


@app.post("/agents/tools/select", response_model=AgentToolSelectionResponse)
def select_agent_tools(
    payload: AgentToolSelectionRequest,
    selection_service: Annotated[
        AgentToolSelectionService,
        Depends(get_agent_tool_selection_service),
    ],
) -> AgentToolSelectionResponse:
    available_tools = (
        payload.available_tools
        if payload.available_tools
        else ToolRegistry().list_tools()
    )

    return selection_service.select_tools(
        objective=payload.objective,
        context=payload.context,
        available_tools=available_tools,
        max_steps=payload.max_steps,
        language=payload.language,
        metadata=payload.metadata,
    )


@app.post("/agents/execute", response_model=AgentMultiStepExecutionResponse)
def execute_agent_workflow(
    payload: AgentMultiStepExecutionRequest,
    execution_service: Annotated[
        AgentMultiStepExecutionService,
        Depends(get_agent_multi_step_execution_service),
    ],
) -> AgentMultiStepExecutionResponse:
    available_tools = (
        payload.available_tools
        if payload.available_tools
        else ToolRegistry().list_tools()
    )

    return execution_service.execute(
        objective=payload.objective,
        context=payload.context,
        available_tools=available_tools,
        max_plan_steps=payload.max_plan_steps,
        max_execution_steps=payload.max_execution_steps,
        language=payload.language,
        metadata=payload.metadata,
        approval_policy=payload.approval_policy,
        safety_policy=payload.safety_policy,
    )


@app.post("/agents/evaluate", response_model=AgentEvaluationResponse)
def evaluate_agent_execution(
    payload: AgentEvaluationRequest,
) -> AgentEvaluationResponse:
    evaluation_service = AgentEvaluationService()

    return evaluation_service.evaluate_execution(
        objective=payload.objective,
        agent_run=payload.agent_run,
        execution_state=payload.execution_state,
        selected_tool_calls=payload.selected_tool_calls,
        approval_decisions=payload.approval_decisions,
        safety_check=payload.safety_check,
        execution_logs=payload.execution_logs,
        metadata=payload.metadata,
    )


@app.get("/agents/logs", response_model=AgentExecutionLogListResponse)
def list_agent_execution_logs(
    log_service: Annotated[
        AgentExecutionLogService,
        Depends(get_agent_execution_log_service),
    ],
) -> AgentExecutionLogListResponse:
    events = log_service.list_events()

    return AgentExecutionLogListResponse(
        events=events,
        total=len(events),
        metadata={
            "source": "agent-execution-logs",
        },
    )


@app.get("/agents/logs/{run_id}", response_model=AgentExecutionLogListResponse)
def list_agent_execution_logs_by_run_id(
    run_id: str,
    log_service: Annotated[
        AgentExecutionLogService,
        Depends(get_agent_execution_log_service),
    ],
) -> AgentExecutionLogListResponse:
    events = log_service.list_events_by_run_id(run_id)

    return AgentExecutionLogListResponse(
        events=events,
        total=len(events),
        metadata={
            "source": "agent-execution-logs",
            "run_id": run_id,
        },
    )


@app.post("/multi-agent/qa-copilot/run", response_model=MultiAgentQACopilotResponse,)
def run_multi_agent_qa_copilot(
    payload: MultiAgentQACopilotRequest,
    service: Annotated[
        MultiAgentQACopilotService,
        Depends(get_multi_agent_qa_copilot_service),
    ],
) -> MultiAgentQACopilotResponse:
    return service.run(payload)


@app.post("/multi-agent/qa-copilot/evaluate", response_model=MultiAgentQACopilotEvaluationResponse,)
def evaluate_multi_agent_qa_copilot(
    payload: MultiAgentQACopilotEvaluationRequest,
    service: Annotated[
        MultiAgentQACopilotEvaluationService,
        Depends(get_multi_agent_qa_copilot_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> MultiAgentQACopilotEvaluationResponse:
    return instrumentation_service.instrument(
        event_type="copilot_evaluation",
        component="multi_agent",
        source="api:/multi-agent/qa-copilot/evaluate",
        operation=lambda: service.evaluate(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "evaluate_multi_agent_qa_copilot",
            **payload.metadata,
        },
    )


@app.get("/evals/golden-dataset", response_model=GoldenEvaluationDataset,)
def get_golden_evaluation_dataset(
    service: Annotated[
        GoldenEvaluationDatasetService,
        Depends(get_golden_evaluation_dataset_service),
    ],
) -> GoldenEvaluationDataset:
    return service.get_default_dataset()


@app.get("/evals/golden-dataset/validation", response_model=EvaluationDatasetValidationResponse,)
def validate_default_golden_evaluation_dataset(
    service: Annotated[
        GoldenEvaluationDatasetValidationService,
        Depends(get_golden_evaluation_dataset_validation_service),
    ],
) -> EvaluationDatasetValidationResponse:
    return service.validate_default_dataset()


@app.post("/evals/golden-dataset/validate", response_model=EvaluationDatasetValidationResponse,)
def validate_golden_evaluation_dataset(
    payload: GoldenEvaluationDataset,
    service: Annotated[
        GoldenEvaluationDatasetValidationService,
        Depends(get_golden_evaluation_dataset_validation_service),
    ],
) -> EvaluationDatasetValidationResponse:
    return service.validate(payload)


@app.post("/evals/golden-dataset/run", response_model=GoldenEvaluationDatasetRunResponse,)
def run_golden_evaluation_dataset(
    payload: GoldenEvaluationDatasetRunRequest,
    service: Annotated[
        GoldenEvaluationDatasetRunnerService,
        Depends(get_golden_evaluation_dataset_runner_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> GoldenEvaluationDatasetRunResponse:
    return instrumentation_service.instrument(
        event_type="golden_dataset_run",
        component="evaluation",
        source="api:/evals/golden-dataset/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_golden_evaluation_dataset",
            **payload.metadata,
        },
    )


@app.get("/evals/prompt-regression/suite", response_model=PromptRegressionSuite,)
def get_prompt_regression_suite(
    service: Annotated[
        PromptRegressionSuiteService,
        Depends(get_prompt_regression_suite_service),
    ],
) -> PromptRegressionSuite:
    return service.get_default_suite()


@app.post("/evals/prompt-regression/run", response_model=PromptRegressionRunResponse,)
def run_prompt_regression_suite(
    payload: PromptRegressionRunRequest,
    service: Annotated[
        PromptRegressionEvaluationService,
        Depends(get_prompt_regression_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> PromptRegressionRunResponse:
    return instrumentation_service.instrument(
        event_type="prompt_regression_run",
        component="evaluation",
        source="api:/evals/prompt-regression/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_prompt_regression_suite",
            **payload.metadata,
        },
    )


@app.post("/evals/reports/aggregate", response_model=AIEvaluationReportAggregationResponse,)
def aggregate_ai_evaluation_report(
    payload: AIEvaluationReportAggregationRequest,
    service: Annotated[
        AIEvaluationReportAggregationService,
        Depends(get_ai_evaluation_report_aggregation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> AIEvaluationReportAggregationResponse:
    return instrumentation_service.instrument(
        event_type="report_aggregation",
        component="evaluation",
        source="api:/evals/reports/aggregate",
        operation=lambda: service.aggregate(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "aggregate_ai_evaluation_report",
            **payload.metadata,
        },
    )


@app.post("/evals/telemetry/events", response_model=EvaluationTelemetryEvent,)
def record_evaluation_telemetry_event(
    payload: EvaluationTelemetryRecordRequest,
    service: Annotated[
        EvaluationTelemetryService,
        Depends(get_evaluation_telemetry_service),
    ],
) -> EvaluationTelemetryEvent:
    return service.record(payload)


@app.get("/evals/telemetry/events", response_model=EvaluationTelemetryEventsResponse,)
def list_evaluation_telemetry_events(
    service: Annotated[
        EvaluationTelemetryService,
        Depends(get_evaluation_telemetry_service),
    ],
    event_type: str | None = None,
    component: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> EvaluationTelemetryEventsResponse:
    return service.list_events(
        event_type=event_type,
        component=component,
        status=status,
        limit=limit,
    )


@app.post("/evals/telemetry/summary", response_model=EvaluationTelemetrySummaryResponse,)
def summarize_evaluation_telemetry(
    payload: EvaluationTelemetrySummaryRequest,
    service: Annotated[
        EvaluationTelemetryService,
        Depends(get_evaluation_telemetry_service),
    ],
) -> EvaluationTelemetrySummaryResponse:
    return service.summarize(payload)


@app.get("/evals/telemetry/summary", response_model=EvaluationTelemetrySummaryResponse,)
def summarize_stored_evaluation_telemetry(
    service: Annotated[
        EvaluationTelemetryService,
        Depends(get_evaluation_telemetry_service),
    ],
) -> EvaluationTelemetrySummaryResponse:
    return service.summarize(EvaluationTelemetrySummaryRequest())


@app.get("/evals/llm-output/suite", response_model=LLMOutputEvaluationSuite,)
def get_llm_output_evaluation_suite(
    service: Annotated[
        LLMOutputEvaluationSuiteService,
        Depends(get_llm_output_evaluation_suite_service),
    ],
) -> LLMOutputEvaluationSuite:
    return service.get_default_suite()


@app.post("/evals/llm-output/run", response_model=LLMOutputEvaluationRunResponse,)
def run_llm_output_evaluation_suite(
    payload: LLMOutputEvaluationRunRequest,
    service: Annotated[
        LLMOutputEvaluationService,
        Depends(get_llm_output_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> LLMOutputEvaluationRunResponse:
    return instrumentation_service.instrument(
        event_type="llm_output_evaluation_run",
        component="evaluation",
        source="api:/evals/llm-output/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_llm_output_evaluation_suite",
            **payload.metadata,
        },
    )


@app.get("/evals/rag-regression/suite", response_model=RAGRegressionSuite,)
def get_rag_regression_suite(
    service: Annotated[
        RAGRegressionSuiteService,
        Depends(get_rag_regression_suite_service),
    ],
) -> RAGRegressionSuite:
    return service.get_default_suite()


@app.post("/evals/rag-regression/run", response_model=RAGRegressionRunResponse,)
def run_rag_regression_suite(
    payload: RAGRegressionRunRequest,
    service: Annotated[
        RAGRegressionEvaluationService,
        Depends(get_rag_regression_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> RAGRegressionRunResponse:
    return instrumentation_service.instrument(
        event_type="rag_regression_run",
        component="evaluation",
        source="api:/evals/rag-regression/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_rag_regression_suite",
            **payload.metadata,
        },
    )


@app.get("/evals/agent-regression/suite", response_model=AgentRegressionSuite,)
def get_agent_regression_suite(
    service: Annotated[
        AgentRegressionSuiteService,
        Depends(get_agent_regression_suite_service),
    ],
) -> AgentRegressionSuite:
    return service.get_default_suite()


@app.post("/evals/agent-regression/run", response_model=AgentRegressionRunResponse,)
def run_agent_regression_suite(
    payload: AgentRegressionRunRequest,
    service: Annotated[
        AgentRegressionEvaluationService,
        Depends(get_agent_regression_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> AgentRegressionRunResponse:
    return instrumentation_service.instrument(
        event_type="agent_regression_run",
        component="evaluation",
        source="api:/evals/agent-regression/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_agent_regression_suite",
            **payload.metadata,
        },
    )


@app.get("/evals/tool-calling/suite", response_model=ToolCallingEvaluationSuite,)
def get_tool_calling_evaluation_suite(
    service: Annotated[
        ToolCallingEvaluationSuiteService,
        Depends(get_tool_calling_evaluation_suite_service),
    ],
) -> ToolCallingEvaluationSuite:
    return service.get_default_suite()


@app.post("/evals/tool-calling/run", response_model=ToolCallingEvaluationRunResponse,)
def run_tool_calling_evaluation_suite(
    payload: ToolCallingEvaluationRunRequest,
    service: Annotated[
        ToolCallingEvaluationService,
        Depends(get_tool_calling_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> ToolCallingEvaluationRunResponse:
    return instrumentation_service.instrument(
        event_type="tool_calling_evaluation_run",
        component="evaluation",
        source="api:/evals/tool-calling/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_tool_calling_evaluation_suite",
            **payload.metadata,
        },
    )


@app.get("/evals/multi-agent-copilot-regression/suite", response_model=MultiAgentCopilotRegressionSuite,)
def get_multi_agent_copilot_regression_suite(
    service: Annotated[
        MultiAgentCopilotRegressionSuiteService,
        Depends(get_multi_agent_copilot_regression_suite_service),
    ],
) -> MultiAgentCopilotRegressionSuite:
    return service.get_default_suite()


@app.post("/evals/multi-agent-copilot-regression/run", response_model=MultiAgentCopilotRegressionRunResponse,)
def run_multi_agent_copilot_regression_suite(
    payload: MultiAgentCopilotRegressionRunRequest,
    service: Annotated[
        MultiAgentCopilotRegressionEvaluationService,
        Depends(get_multi_agent_copilot_regression_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> MultiAgentCopilotRegressionRunResponse:
    return instrumentation_service.instrument(
        event_type="multi_agent_copilot_regression_run",
        component="evaluation",
        source="api:/evals/multi-agent-copilot-regression/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_multi_agent_copilot_regression_suite",
            **payload.metadata,
        },
    )


@app.get("/evals/llm-as-judge/suite", response_model=LLMAsJudgeEvaluationSuite,)
def get_llm_as_judge_evaluation_suite(
    service: Annotated[
        LLMAsJudgeEvaluationSuiteService,
        Depends(get_llm_as_judge_evaluation_suite_service),
    ],
) -> LLMAsJudgeEvaluationSuite:
    return service.get_default_suite()


@app.post("/evals/llm-as-judge/run", response_model=LLMAsJudgeEvaluationRunResponse,)
def run_llm_as_judge_evaluation_suite(
    payload: LLMAsJudgeEvaluationRunRequest,
    service: Annotated[
        LLMAsJudgeEvaluationService,
        Depends(get_llm_as_judge_evaluation_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> LLMAsJudgeEvaluationRunResponse:
    return instrumentation_service.instrument(
        event_type="llm_as_judge_evaluation_run",
        component="evaluation",
        source="api:/evals/llm-as-judge/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_llm_as_judge_evaluation_suite",
            **payload.metadata,
        },
    )


@app.post("/evals/ci/pipeline/run", response_model=CIEvaluationPipelineRunResponse,)
def run_ci_evaluation_pipeline(
    payload: CIEvaluationPipelineRunRequest,
    service: Annotated[
        CIEvaluationPipelineService,
        Depends(get_ci_evaluation_pipeline_service),
    ],
    instrumentation_service: Annotated[
        EvaluationTelemetryInstrumentationService,
        Depends(get_evaluation_telemetry_instrumentation_service),
    ],
) -> CIEvaluationPipelineRunResponse:
    return instrumentation_service.instrument(
        event_type="ci_evaluation_pipeline_run",
        component="evaluation",
        source="api:/evals/ci/pipeline/run",
        operation=lambda: service.run(payload),
        run_id=payload.metadata.get("run_id"),
        metadata={
            "operation": "run_ci_evaluation_pipeline",
            **payload.metadata,
        },
    )


@app.post("/security/prompt-injection/assess", response_model=PromptInjectionAssessmentResponse,)
def assess_prompt_injection(
    request: PromptInjectionAssessmentRequest,
) -> PromptInjectionAssessmentResponse:
    assessment = PromptInjectionDetectionService().assess(request)

    PromptInjectionTelemetryService.from_settings(
        get_settings()
    ).record_if_relevant(
        PromptInjectionTelemetryRequest(
            risk_level=assessment.risk_level,
            recommended_action=assessment.recommended_action,
            is_blocking_required=assessment.is_blocking_required,
            detected_patterns=assessment.detected_patterns,
            risk_reasons=assessment.risk_reasons,
            input_source=assessment.input_source,
            workflow=assessment.workflow,
            inspected_character_count=assessment.inspected_character_count,
            metadata={
                "source": "prompt_injection_assessment_endpoint",
                "raw_input_stored": False,
                "input_text_echoed": False,
            },
        )
    )

    return assessment


@app.get(
    "/security/prompt-injection/records",
    response_model=PromptInjectionTelemetryRecordsResponse,
)
def list_prompt_injection_telemetry_records(
    limit: int = Query(default=100, ge=1, le=1000),
    risk_level: str | None = None,
    recommended_action: str | None = None,
    input_source: str | None = None,
    workflow: str | None = None,
) -> PromptInjectionTelemetryRecordsResponse:
    return PromptInjectionTelemetryService.from_settings(
        get_settings()
    ).list_records(
        limit=limit,
        risk_level=risk_level,
        recommended_action=recommended_action,
        input_source=input_source,
        workflow=workflow,
    )


@app.post("/observability/usage/records", response_model=AIUsageRecord,)
def record_ai_usage(
    payload: AIUsageRecordRequest,
    service: Annotated[
        AIUsageTrackingService,
        Depends(get_ai_usage_tracking_service),
    ],
) -> AIUsageRecord:
    return service.record(payload)


@app.get("/observability/usage/records", response_model=AIUsageRecordsResponse,)
def list_ai_usage_records(
    service: Annotated[
        AIUsageTrackingService,
        Depends(get_ai_usage_tracking_service),
    ],
    provider: str | None = None,
    component: str | None = None,
    model_name: str | None = None,
    limit: int = 100,
) -> AIUsageRecordsResponse:
    return service.list_records(
        provider=provider,
        component=component,
        model_name=model_name,
        limit=limit,
    )


@app.post("/observability/usage/summary", response_model=AIUsageSummaryResponse,)
def summarize_ai_usage(
    payload: AIUsageSummaryRequest,
    service: Annotated[
        AIUsageTrackingService,
        Depends(get_ai_usage_tracking_service),
    ],
) -> AIUsageSummaryResponse:
    return service.summarize(payload)


@app.get("/observability/usage/summary", response_model=AIUsageSummaryResponse,)
def summarize_stored_ai_usage(
    service: Annotated[
        AIUsageTrackingService,
        Depends(get_ai_usage_tracking_service),
    ],
) -> AIUsageSummaryResponse:
    return service.summarize(AIUsageSummaryRequest())


@app.post("/observability/retrieval-quality/records", response_model=AIRetrievalQualityRecord,)
def record_ai_retrieval_quality(
    payload: AIRetrievalQualityRecordRequest,
    service: Annotated[
        AIRetrievalQualityTelemetryService,
        Depends(get_ai_retrieval_quality_telemetry_service),
    ],
) -> AIRetrievalQualityRecord:
    return service.record(payload)


@app.get("/observability/retrieval-quality/records", response_model=AIRetrievalQualityRecordsResponse,)
def list_ai_retrieval_quality_records(
    service: Annotated[
        AIRetrievalQualityTelemetryService,
        Depends(get_ai_retrieval_quality_telemetry_service),
    ],
    component: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> AIRetrievalQualityRecordsResponse:
    return service.list_records(
        component=component,
        operation=operation,
        status=status,
        limit=limit,
    )


@app.post("/observability/retrieval-quality/summary", response_model=AIRetrievalQualitySummaryResponse,)
def summarize_ai_retrieval_quality(
    payload: AIRetrievalQualitySummaryRequest,
    service: Annotated[
        AIRetrievalQualityTelemetryService,
        Depends(get_ai_retrieval_quality_telemetry_service),
    ],
) -> AIRetrievalQualitySummaryResponse:
    return service.summarize(payload)


@app.get("/observability/retrieval-quality/summary", response_model=AIRetrievalQualitySummaryResponse,)
def summarize_stored_ai_retrieval_quality(
    service: Annotated[
        AIRetrievalQualityTelemetryService,
        Depends(get_ai_retrieval_quality_telemetry_service),
    ],
) -> AIRetrievalQualitySummaryResponse:
    return service.summarize(AIRetrievalQualitySummaryRequest())


@app.post("/observability/agent-execution/records", response_model=AIAgentExecutionRecord,)
def record_ai_agent_execution(
    payload: AIAgentExecutionRecordRequest,
    service: Annotated[
        AIAgentExecutionTelemetryService,
        Depends(get_ai_agent_execution_telemetry_service),
    ],
) -> AIAgentExecutionRecord:
    return service.record(payload)


@app.get("/observability/agent-execution/records", response_model=AIAgentExecutionRecordsResponse,)
def list_ai_agent_execution_records(
    service: Annotated[
        AIAgentExecutionTelemetryService,
        Depends(get_ai_agent_execution_telemetry_service),
    ],
    component: str | None = None,
    agent_name: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    run_status: str | None = None,
    limit: int = 100,
) -> AIAgentExecutionRecordsResponse:
    return service.list_records(
        component=component,
        agent_name=agent_name,
        operation=operation,
        status=status,
        run_status=run_status,
        limit=limit,
    )


@app.post("/observability/agent-execution/summary", response_model=AIAgentExecutionSummaryResponse,)
def summarize_ai_agent_execution(
    payload: AIAgentExecutionSummaryRequest,
    service: Annotated[
        AIAgentExecutionTelemetryService,
        Depends(get_ai_agent_execution_telemetry_service),
    ],
) -> AIAgentExecutionSummaryResponse:
    return service.summarize(payload)


@app.get("/observability/agent-execution/summary", response_model=AIAgentExecutionSummaryResponse,)
def summarize_stored_ai_agent_execution(
    service: Annotated[
        AIAgentExecutionTelemetryService,
        Depends(get_ai_agent_execution_telemetry_service),
    ],
) -> AIAgentExecutionSummaryResponse:
    return service.summarize(AIAgentExecutionSummaryRequest())


@app.post("/observability/multi-agent-execution/records", response_model=AIMultiAgentExecutionRecord,)
def record_ai_multi_agent_execution(
    payload: AIMultiAgentExecutionRecordRequest,
    service: Annotated[
        AIMultiAgentExecutionTelemetryService,
        Depends(get_ai_multi_agent_execution_telemetry_service),
    ],
) -> AIMultiAgentExecutionRecord:
    return service.record(payload)


@app.get("/observability/multi-agent-execution/records", response_model=AIMultiAgentExecutionRecordsResponse,)
def list_ai_multi_agent_execution_records(
    service: Annotated[
        AIMultiAgentExecutionTelemetryService,
        Depends(get_ai_multi_agent_execution_telemetry_service),
    ],
    component: str | None = None,
    workflow_name: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    run_status: str | None = None,
    limit: int = 100,
) -> AIMultiAgentExecutionRecordsResponse:
    return service.list_records(
        component=component,
        workflow_name=workflow_name,
        operation=operation,
        status=status,
        run_status=run_status,
        limit=limit,
    )


@app.post("/observability/multi-agent-execution/summary", response_model=AIMultiAgentExecutionSummaryResponse,)
def summarize_ai_multi_agent_execution(
    payload: AIMultiAgentExecutionSummaryRequest,
    service: Annotated[
        AIMultiAgentExecutionTelemetryService,
        Depends(get_ai_multi_agent_execution_telemetry_service),
    ],
) -> AIMultiAgentExecutionSummaryResponse:
    return service.summarize(payload)


@app.get("/observability/multi-agent-execution/summary", response_model=AIMultiAgentExecutionSummaryResponse,)
def summarize_stored_ai_multi_agent_execution(
    service: Annotated[
        AIMultiAgentExecutionTelemetryService,
        Depends(get_ai_multi_agent_execution_telemetry_service),
    ],
) -> AIMultiAgentExecutionSummaryResponse:
    return service.summarize(AIMultiAgentExecutionSummaryRequest())


@app.get("/observability/dashboard", response_model=AIObservabilityDashboardResponse,)
def get_ai_observability_dashboard(
    service: Annotated[
        AIObservabilityDashboardService,
        Depends(get_ai_observability_dashboard_service),
    ],
) -> AIObservabilityDashboardResponse:
    return service.get_dashboard()


@app.get("/observability/execution-history", response_model=AIExecutionHistoryResponse,)
def get_ai_execution_history(
    service: Annotated[
        AIExecutionHistoryService,
        Depends(get_ai_execution_history_service),
    ],
    execution_type: str | None = None,
    status: str | None = None,
    component: str | None = None,
    run_id: str | None = None,
    limit: int = 100,
) -> AIExecutionHistoryResponse:
    return service.list_history(
        execution_type=execution_type,
        status=status,
        component=component,
        run_id=run_id,
        limit=limit,
    )


@app.get("/security/blocked-tool-calls", response_model=BlockedToolCallTelemetryRecordsResponse,)
def list_blocked_tool_call_telemetry(
    limit: int = Query(default=100, ge=1, le=1000),
    tool_name: str | None = None,
    caller_type: str | None = None,
    environment: str | None = None,
    risk_level: str | None = None,
) -> BlockedToolCallTelemetryRecordsResponse:
    return BlockedToolCallTelemetryService.from_settings(
        get_settings()
    ).list_records(
        limit=limit,
        tool_name=tool_name,
        caller_type=caller_type,
        environment=environment,
        risk_level=risk_level,
    )
