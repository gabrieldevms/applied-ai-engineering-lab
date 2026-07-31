import pytest
from pydantic import ValidationError
from ai_api.evals.usage_tracking import JsonlAIUsageRecordStore
from ai_api.evals import (
    AIUsageRecord,
    AIUsageRecordRequest,
    AIUsageSummaryRequest,
    AIUsageTrackingService,
)


def test_ai_usage_tracking_service_should_record_token_usage_and_cost() -> None:
    service = AIUsageTrackingService()

    record = service.record(
        AIUsageRecordRequest(
            provider="openai",
            model_name="test-model",
            component="llm",
            operation="requirement_analysis",
            prompt_tokens=1000,
            completion_tokens=500,
            input_cost_per_1k_tokens_usd=0.01,
            output_cost_per_1k_tokens_usd=0.03,
            run_id="run-001",
            metadata={
                "source": "unit-test",
            },
        )
    )

    assert record.record_id
    assert record.provider == "openai"
    assert record.model_name == "test-model"
    assert record.component == "llm"
    assert record.operation == "requirement_analysis"
    assert record.prompt_tokens == 1000
    assert record.completion_tokens == 500
    assert record.embedding_tokens == 0
    assert record.total_tokens == 1500
    assert record.input_cost_usd == 0.01
    assert record.output_cost_usd == 0.015
    assert record.embedding_cost_usd is None
    assert record.total_cost_usd == 0.025
    assert record.run_id == "run-001"
    assert record.metadata["usage_schema_version"] == "0.1.0"
    assert record.metadata["pricing_mode"] == "caller_provided"
    assert record.metadata["source"] == "unit-test"


def test_ai_usage_tracking_service_should_record_embedding_usage_and_cost() -> None:
    service = AIUsageTrackingService()

    record = service.record(
        AIUsageRecordRequest(
            provider="openai",
            model_name="embedding-test-model",
            component="rag",
            operation="document_embedding",
            embedding_tokens=2000,
            embedding_cost_per_1k_tokens_usd=0.02,
        )
    )

    assert record.total_tokens == 2000
    assert record.embedding_cost_usd == 0.04
    assert record.total_cost_usd == 0.04


def test_ai_usage_tracking_service_should_use_provided_total_tokens_and_total_cost() -> None:
    service = AIUsageTrackingService()

    record = service.record(
        AIUsageRecordRequest(
            provider="unknown",
            model_name="custom-model",
            component="agent",
            operation="agent_run",
            prompt_tokens=100,
            completion_tokens=100,
            total_tokens=500,
            total_cost_usd=0.1234,
        )
    )

    assert record.total_tokens == 500
    assert record.total_cost_usd == 0.1234


def test_ai_usage_tracking_service_should_list_records_with_filters() -> None:
    service = AIUsageTrackingService()

    service.record(
        AIUsageRecordRequest(
            provider="openai",
            model_name="model-a",
            component="llm",
            operation="requirement_analysis",
            prompt_tokens=10,
        )
    )
    service.record(
        AIUsageRecordRequest(
            provider="ollama",
            model_name="model-b",
            component="agent",
            operation="qa_agent_run",
            prompt_tokens=20,
        )
    )

    response = service.list_records(
        provider="ollama",
    )

    assert response.count == 1
    assert response.records[0].provider == "ollama"
    assert response.records[0].model_name == "model-b"
    assert response.metadata["total_stored_records"] == 2


def test_ai_usage_tracking_service_should_summarize_stored_records() -> None:
    service = AIUsageTrackingService()

    service.record(
        AIUsageRecordRequest(
            provider="openai",
            model_name="model-a",
            component="llm",
            operation="requirement_analysis",
            prompt_tokens=1000,
            completion_tokens=500,
            input_cost_per_1k_tokens_usd=0.01,
            output_cost_per_1k_tokens_usd=0.03,
        )
    )
    service.record(
        AIUsageRecordRequest(
            provider="openai",
            model_name="model-a",
            component="rag",
            operation="rag_answer",
            prompt_tokens=2000,
            completion_tokens=1000,
            input_cost_per_1k_tokens_usd=0.01,
            output_cost_per_1k_tokens_usd=0.03,
        )
    )

    response = service.summarize(AIUsageSummaryRequest())

    assert response.record_count == 2
    assert response.total_prompt_tokens == 3000
    assert response.total_completion_tokens == 1500
    assert response.total_embedding_tokens == 0
    assert response.total_tokens == 4500
    assert response.total_cost_usd == 0.075
    assert response.average_cost_usd == 0.0375
    assert response.provider_coverage["openai"] == 2
    assert response.model_coverage["model-a"] == 2
    assert response.component_coverage["llm"] == 1
    assert response.component_coverage["rag"] == 1
    assert response.risks == [
        "No AI usage risks detected.",
    ]


def test_ai_usage_tracking_service_should_summarize_request_records() -> None:
    service = AIUsageTrackingService()

    record = AIUsageRecord(
        record_id="record-001",
        provider="fake",
        model_name="fake-model",
        component="evaluation",
        operation="prompt_regression",
        prompt_tokens=100,
        completion_tokens=50,
        embedding_tokens=0,
        total_tokens=150,
        total_cost_usd=0.0,
        recorded_at="2026-07-30T20:00:00+00:00",
    )

    response = service.summarize(
        AIUsageSummaryRequest(
            records=[
                record,
            ],
            metadata={
                "source": "request-summary-test",
            },
        )
    )

    assert response.record_count == 1
    assert response.total_tokens == 150
    assert response.total_cost_usd == 0.0
    assert response.average_cost_usd == 0.0
    assert response.metadata["source"] == "request-summary-test"


def test_ai_usage_tracking_service_should_report_risks_for_missing_cost_data() -> None:
    service = AIUsageTrackingService()

    service.record(
        AIUsageRecordRequest(
            provider="unknown",
            model_name="unknown-model",
            component="llm",
            operation="llm_call",
            prompt_tokens=100,
        )
    )

    response = service.summarize(AIUsageSummaryRequest())

    assert response.total_cost_usd is None
    assert response.average_cost_usd is None
    assert response.risks == [
        "1 usage record(s) do not have cost data.",
    ]


def test_ai_usage_tracking_request_should_reject_blank_model_name() -> None:
    with pytest.raises(ValidationError):
        AIUsageRecordRequest(
            provider="openai",
            model_name="   ",
            component="llm",
            operation="llm_call",
        )


def test_ai_usage_tracking_request_should_reject_negative_tokens() -> None:
    with pytest.raises(ValidationError):
        AIUsageRecordRequest(
            provider="openai",
            model_name="test-model",
            component="llm",
            operation="llm_call",
            prompt_tokens=-1,
        )


def test_ai_usage_tracking_service_should_persist_records_with_jsonl_store(
    tmp_path,
) -> None:
    file_path = tmp_path / "usage-records.jsonl"

    first_service = AIUsageTrackingService(
        record_store=JsonlAIUsageRecordStore(file_path=file_path),
        storage_backend="local_jsonl",
    )

    first_service.record(
        AIUsageRecordRequest(
            provider="fake",
            model_name="fake-llm-v1",
            component="agent",
            operation="qa_agent_console_demo",
            prompt_tokens=100,
            completion_tokens=50,
            input_cost_per_1k_tokens_usd=0.001,
            output_cost_per_1k_tokens_usd=0.002,
        )
    )

    second_service = AIUsageTrackingService(
        record_store=JsonlAIUsageRecordStore(file_path=file_path),
        storage_backend="local_jsonl",
    )

    response = second_service.list_records()

    assert response.count == 1
    assert response.records[0].provider == "fake"
    assert response.records[0].model_name == "fake-llm-v1"
    assert response.records[0].component == "agent"
    assert response.records[0].operation == "qa_agent_console_demo"
    assert response.records[0].total_tokens == 150
    assert response.records[0].total_cost_usd == 0.0002
    assert response.records[0].metadata["storage_backend"] == "local_jsonl"
    assert response.metadata["storage_backend"] == "local_jsonl"


def test_ai_usage_tracking_service_should_summarize_persisted_jsonl_records(
    tmp_path,
) -> None:
    file_path = tmp_path / "usage-records.jsonl"

    service = AIUsageTrackingService(
        record_store=JsonlAIUsageRecordStore(file_path=file_path),
        storage_backend="local_jsonl",
    )

    service.record(
        AIUsageRecordRequest(
            provider="fake",
            model_name="fake-llm-v1",
            component="llm",
            operation="requirement_analysis",
            prompt_tokens=1000,
            completion_tokens=500,
            input_cost_per_1k_tokens_usd=0.001,
            output_cost_per_1k_tokens_usd=0.002,
        )
    )

    restored_service = AIUsageTrackingService(
        record_store=JsonlAIUsageRecordStore(file_path=file_path),
        storage_backend="local_jsonl",
    )

    response = restored_service.summarize(AIUsageSummaryRequest())

    assert response.record_count == 1
    assert response.total_prompt_tokens == 1000
    assert response.total_completion_tokens == 500
    assert response.total_tokens == 1500
    assert response.total_cost_usd == 0.002
    assert response.average_cost_usd == 0.002
    assert response.provider_coverage["fake"] == 1
    assert response.metadata["storage_backend"] == "local_jsonl"


def test_ai_usage_tracking_service_should_clear_jsonl_records(tmp_path) -> None:
    file_path = tmp_path / "usage-records.jsonl"

    service = AIUsageTrackingService(
        record_store=JsonlAIUsageRecordStore(file_path=file_path),
        storage_backend="local_jsonl",
    )

    service.record(
        AIUsageRecordRequest(
            provider="fake",
            model_name="fake-llm-v1",
            component="llm",
            operation="llm_call",
            prompt_tokens=10,
        )
    )

    service.clear()

    assert service.list_records().count == 0
    assert service.summarize(AIUsageSummaryRequest()).record_count == 0
