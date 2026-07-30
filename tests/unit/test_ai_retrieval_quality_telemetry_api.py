from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    AIRetrievalQualityRecord,
    AIRetrievalQualityRecordsResponse,
    AIRetrievalQualitySummaryResponse,
    get_ai_retrieval_quality_telemetry_service,
)
from ai_api.main import app


class StubAIRetrievalQualityTelemetryService:
    def __init__(self) -> None:
        self.last_record_request: Any | None = None
        self.last_summary_request: Any | None = None

    def record(self, request: Any) -> AIRetrievalQualityRecord:
        self.last_record_request = request

        return AIRetrievalQualityRecord(
            record_id="retrieval-quality-record-001",
            component=request.component,
            operation=request.operation,
            query=request.query,
            status="passed",
            requested_top_k=request.requested_top_k,
            retrieved_chunks_count=request.retrieved_chunks_count,
            relevant_chunks_count=request.relevant_chunks_count,
            citation_count=request.citation_count,
            unique_source_count=request.unique_source_count,
            precision_at_k=1.0,
            source_coverage_score=1.0,
            quality_score=0.95,
            average_similarity_score=request.average_similarity_score,
            expected_min_retrieved_chunks=request.expected_min_retrieved_chunks,
            expected_min_citations=request.expected_min_citations,
            min_quality_score=request.min_quality_score,
            risks=[
                "No retrieval quality risks detected.",
            ],
            recorded_at="2026-07-30T20:00:00+00:00",
            metadata={
                "source": "stub-retrieval-quality-service",
            },
        )

    def list_records(
        self,
        component: str | None = None,
        operation: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> AIRetrievalQualityRecordsResponse:
        return AIRetrievalQualityRecordsResponse(
            records=[
                AIRetrievalQualityRecord(
                    record_id="retrieval-quality-record-001",
                    component="rag",
                    operation="rag_answer",
                    query="Quando o boleto deve ser registrado?",
                    status="passed",
                    retrieved_chunks_count=3,
                    relevant_chunks_count=3,
                    citation_count=2,
                    unique_source_count=2,
                    precision_at_k=1.0,
                    source_coverage_score=1.0,
                    quality_score=0.95,
                    average_similarity_score=0.9,
                    expected_min_retrieved_chunks=1,
                    expected_min_citations=1,
                    min_quality_score=0.7,
                    risks=[
                        "No retrieval quality risks detected.",
                    ],
                    recorded_at="2026-07-30T20:00:00+00:00",
                )
            ],
            count=1,
            metadata={
                "component": component,
                "operation": operation,
                "status": status,
                "limit": limit,
            },
        )

    def summarize(self, request: Any) -> AIRetrievalQualitySummaryResponse:
        self.last_summary_request = request

        return AIRetrievalQualitySummaryResponse(
            record_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            total_retrieved_chunks=3,
            total_relevant_chunks=3,
            total_citations=2,
            total_unique_sources=2,
            average_precision_at_k=1.0,
            average_source_coverage_score=1.0,
            average_quality_score=0.95,
            average_similarity_score=0.9,
            component_coverage={
                "rag": 1,
            },
            operation_coverage={
                "rag_answer": 1,
            },
            risks=[
                "No retrieval quality risks detected.",
            ],
            metadata={
                "source": "stub-retrieval-quality-service",
            },
        )


def test_record_retrieval_quality_endpoint_should_return_record() -> None:
    service = StubAIRetrievalQualityTelemetryService()
    app.dependency_overrides[
        get_ai_retrieval_quality_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/retrieval-quality/records",
            json={
                "component": "rag",
                "operation": "rag_answer",
                "query": "Quando o boleto deve ser registrado?",
                "requested_top_k": 3,
                "retrieved_chunks_count": 3,
                "relevant_chunks_count": 3,
                "citation_count": 2,
                "unique_source_count": 2,
                "required_source_count": 2,
                "matched_required_source_count": 2,
                "average_similarity_score": 0.9,
                "expected_min_retrieved_chunks": 1,
                "expected_min_citations": 1,
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_id"] == "retrieval-quality-record-001"
        assert body["component"] == "rag"
        assert body["operation"] == "rag_answer"
        assert body["status"] == "passed"
        assert body["quality_score"] == 0.95

        assert service.last_record_request is not None
        assert service.last_record_request.query == (
            "Quando o boleto deve ser registrado?"
        )
    finally:
        app.dependency_overrides.clear()


def test_list_retrieval_quality_records_endpoint_should_return_records() -> None:
    app.dependency_overrides[
        get_ai_retrieval_quality_telemetry_service
    ] = lambda: StubAIRetrievalQualityTelemetryService()

    try:
        client = TestClient(app)

        response = client.get(
            "/observability/retrieval-quality/records?component=rag&status=passed&limit=10"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["count"] == 1
        assert body["records"][0]["operation"] == "rag_answer"
        assert body["metadata"]["component"] == "rag"
        assert body["metadata"]["status"] == "passed"
        assert body["metadata"]["limit"] == 10
    finally:
        app.dependency_overrides.clear()


def test_summarize_retrieval_quality_endpoint_should_return_summary() -> None:
    service = StubAIRetrievalQualityTelemetryService()
    app.dependency_overrides[
        get_ai_retrieval_quality_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/retrieval-quality/summary",
            json={
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["passed_count"] == 1
        assert body["average_quality_score"] == 0.95
        assert body["component_coverage"]["rag"] == 1

        assert service.last_summary_request is not None
        assert service.last_summary_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_summarize_stored_retrieval_quality_endpoint_should_return_summary() -> None:
    app.dependency_overrides[
        get_ai_retrieval_quality_telemetry_service
    ] = lambda: StubAIRetrievalQualityTelemetryService()

    try:
        client = TestClient(app)

        response = client.get("/observability/retrieval-quality/summary")

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["total_retrieved_chunks"] == 3
        assert body["average_precision_at_k"] == 1.0
    finally:
        app.dependency_overrides.clear()


def test_record_retrieval_quality_endpoint_should_reject_invalid_component() -> None:
    client = TestClient(app)

    response = client.post(
        "/observability/retrieval-quality/records",
        json={
            "component": "invalid-component",
            "operation": "rag_answer",
            "query": "Query",
        },
    )

    assert response.status_code == 422
