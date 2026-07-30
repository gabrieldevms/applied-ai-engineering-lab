import pytest
from pydantic import ValidationError
from ai_api.evals import (
    AIRetrievalQualityRecord,
    AIRetrievalQualityRecordRequest,
    AIRetrievalQualitySummaryRequest,
    AIRetrievalQualityTelemetryService,
)


def test_retrieval_quality_service_should_record_passed_quality_metrics() -> None:
    service = AIRetrievalQualityTelemetryService()

    record = service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Quando o boleto deve ser registrado?",
            requested_top_k=3,
            retrieved_chunks_count=3,
            relevant_chunks_count=3,
            citation_count=2,
            unique_source_count=2,
            required_source_count=2,
            matched_required_source_count=2,
            min_similarity_score=0.81,
            max_similarity_score=0.95,
            average_similarity_score=0.9,
            expected_min_retrieved_chunks=1,
            expected_min_citations=1,
            min_quality_score=0.7,
            run_id="retrieval-run-001",
            metadata={
                "source": "unit-test",
            },
        )
    )

    assert record.record_id
    assert record.status == "passed"
    assert record.component == "rag"
    assert record.operation == "rag_answer"
    assert record.query == "Quando o boleto deve ser registrado?"
    assert record.retrieved_chunks_count == 3
    assert record.relevant_chunks_count == 3
    assert record.citation_count == 2
    assert record.unique_source_count == 2
    assert record.precision_at_k == 1.0
    assert record.source_coverage_score == 1.0
    assert record.quality_score == 0.9667
    assert record.average_similarity_score == 0.9
    assert record.run_id == "retrieval-run-001"
    assert record.risks == [
        "No retrieval quality risks detected.",
    ]
    assert record.metadata["retrieval_quality_schema_version"] == "0.1.0"
    assert record.metadata["source"] == "unit-test"


def test_retrieval_quality_service_should_warn_when_citations_are_missing() -> None:
    service = AIRetrievalQualityTelemetryService()

    record = service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Como validar evidências de dados?",
            retrieved_chunks_count=2,
            relevant_chunks_count=2,
            citation_count=0,
            unique_source_count=1,
            average_similarity_score=0.85,
            expected_min_citations=1,
        )
    )

    assert record.status == "warning"
    assert record.quality_score == 0.925
    assert record.risks == [
        "Citation count is below the expected minimum.",
    ]


def test_retrieval_quality_service_should_fail_when_no_chunks_are_retrieved() -> None:
    service = AIRetrievalQualityTelemetryService()

    record = service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_retrieve",
            query="Qual é a política de cobrança?",
            retrieved_chunks_count=0,
            citation_count=0,
            unique_source_count=0,
            expected_min_retrieved_chunks=1,
        )
    )

    assert record.status == "failed"
    assert record.quality_score is None
    assert "Retrieved chunk count is below the expected minimum." in record.risks


def test_retrieval_quality_service_should_fail_when_quality_score_is_below_minimum() -> None:
    service = AIRetrievalQualityTelemetryService()

    record = service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Quando o boleto deve ser registrado?",
            retrieved_chunks_count=4,
            relevant_chunks_count=1,
            citation_count=1,
            unique_source_count=1,
            required_source_count=2,
            matched_required_source_count=0,
            average_similarity_score=0.4,
            min_quality_score=0.7,
        )
    )

    assert record.status == "failed"
    assert record.precision_at_k == 0.25
    assert record.source_coverage_score == 0.0
    assert record.quality_score == 0.2167
    assert record.risks == [
        "Retrieval quality score is below the configured minimum.",
    ]


def test_retrieval_quality_service_should_list_records_with_filters() -> None:
    service = AIRetrievalQualityTelemetryService()

    service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Query 1",
            retrieved_chunks_count=1,
            relevant_chunks_count=1,
            average_similarity_score=0.9,
        )
    )
    service.record(
        AIRetrievalQualityRecordRequest(
            component="agent",
            operation="qa_agent_context_retrieval",
            query="Query 2",
            retrieved_chunks_count=0,
            expected_min_retrieved_chunks=1,
        )
    )

    response = service.list_records(
        component="agent",
    )

    assert response.count == 1
    assert response.records[0].component == "agent"
    assert response.records[0].operation == "qa_agent_context_retrieval"
    assert response.records[0].status == "failed"
    assert response.metadata["total_stored_records"] == 2


def test_retrieval_quality_service_should_summarize_stored_records() -> None:
    service = AIRetrievalQualityTelemetryService()

    service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Query 1",
            retrieved_chunks_count=3,
            relevant_chunks_count=3,
            citation_count=2,
            unique_source_count=2,
            required_source_count=2,
            matched_required_source_count=2,
            average_similarity_score=0.9,
            expected_min_citations=1,
        )
    )
    service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Query 2",
            retrieved_chunks_count=2,
            relevant_chunks_count=1,
            citation_count=0,
            unique_source_count=1,
            average_similarity_score=0.7,
            expected_min_citations=1,
            min_quality_score=0.5,
        )
    )

    response = service.summarize(AIRetrievalQualitySummaryRequest())

    assert response.record_count == 2
    assert response.passed_count == 1
    assert response.warning_count == 1
    assert response.failed_count == 0
    assert response.total_retrieved_chunks == 5
    assert response.total_relevant_chunks == 4
    assert response.total_citations == 2
    assert response.total_unique_sources == 3
    assert response.average_precision_at_k == 0.75
    assert response.average_quality_score == 0.7833
    assert response.average_similarity_score == 0.8
    assert response.component_coverage["rag"] == 2
    assert response.operation_coverage["rag_answer"] == 2
    assert response.risks == [
        "1 retrieval quality record(s) returned warning.",
    ]


def test_retrieval_quality_service_should_summarize_request_records() -> None:
    service = AIRetrievalQualityTelemetryService()

    record = AIRetrievalQualityRecord(
        record_id="retrieval-record-001",
        component="rag",
        operation="rag_answer",
        query="Query",
        status="passed",
        retrieved_chunks_count=1,
        relevant_chunks_count=1,
        citation_count=1,
        unique_source_count=1,
        precision_at_k=1.0,
        source_coverage_score=None,
        quality_score=0.9,
        average_similarity_score=0.8,
        expected_min_retrieved_chunks=1,
        expected_min_citations=1,
        min_quality_score=0.7,
        risks=[
            "No retrieval quality risks detected.",
        ],
        recorded_at="2026-07-30T20:00:00+00:00",
    )

    response = service.summarize(
        AIRetrievalQualitySummaryRequest(
            records=[
                record,
            ],
            metadata={
                "source": "request-summary-test",
            },
        )
    )

    assert response.record_count == 1
    assert response.passed_count == 1
    assert response.average_precision_at_k == 1.0
    assert response.average_quality_score == 0.9
    assert response.metadata["source"] == "request-summary-test"


def test_retrieval_quality_request_should_reject_blank_query() -> None:
    with pytest.raises(ValidationError):
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="   ",
        )


def test_retrieval_quality_request_should_reject_invalid_similarity_score() -> None:
    with pytest.raises(ValidationError):
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Query",
            average_similarity_score=1.5,
        )
