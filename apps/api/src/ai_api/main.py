import logging
import time
from typing import Annotated, Any
from collections.abc import Awaitable, Callable
from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response
from ai_api.schemas import AnalyzeRequest, AnalyzeResponse
from ai_api.requirements.dependencies import get_requirement_analyzer_service
from ai_api.requirements.exceptions import RequirementAnalysisError
from ai_api.requirements.schemas import (
    RequirementAnalysisRequest,
    RequirementAnalysisResponse,
)
from ai_api.requirements.services import RequirementAnalyzerService


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
