from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    AIUsageRecord,
    AIUsageRecordsResponse,
    AIUsageSummaryResponse,
    get_ai_usage_tracking_service,
)
from ai_api.main import app


class StubAIUsageTrackingService:
    def __init__(self) -> None:
        self.last_record_request: Any | None = None
        self.last_summary_request: Any | None = None

    def record(self, request: Any) -> AIUsageRecord:
        self.last_record_request = request

        return AIUsageRecord(
            record_id="usage-record-001",
            provider=request.provider,
            model_name=request.model_name,
            component=request.component,
            operation=request.operation,
            prompt_tokens=request.prompt_tokens,
            completion_tokens=request.completion_tokens,
            embedding_tokens=request.embedding_tokens,
            total_tokens=request.prompt_tokens + request.completion_tokens,
            input_cost_usd=0.01,
            output_cost_usd=0.015,
            total_cost_usd=0.025,
            recorded_at="2026-07-30T20:00:00+00:00",
            metadata={
                "source": "stub-usage-service",
            },
        )

    def list_records(
        self,
        provider: str | None = None,
        component: str | None = None,
        model_name: str | None = None,
        limit: int = 100,
    ) -> AIUsageRecordsResponse:
        return AIUsageRecordsResponse(
            records=[
                AIUsageRecord(
                    record_id="usage-record-001",
                    provider="openai",
                    model_name="test-model",
                    component="llm",
                    operation="requirement_analysis",
                    prompt_tokens=1000,
                    completion_tokens=500,
                    embedding_tokens=0,
                    total_tokens=1500,
                    total_cost_usd=0.025,
                    recorded_at="2026-07-30T20:00:00+00:00",
                )
            ],
            count=1,
            metadata={
                "provider": provider,
                "component": component,
                "model_name": model_name,
                "limit": limit,
            },
        )

    def summarize(self, request: Any) -> AIUsageSummaryResponse:
        self.last_summary_request = request

        return AIUsageSummaryResponse(
            record_count=1,
            total_prompt_tokens=1000,
            total_completion_tokens=500,
            total_embedding_tokens=0,
            total_tokens=1500,
            total_cost_usd=0.025,
            average_cost_usd=0.025,
            provider_coverage={
                "openai": 1,
            },
            model_coverage={
                "test-model": 1,
            },
            component_coverage={
                "llm": 1,
            },
            operation_coverage={
                "requirement_analysis": 1,
            },
            risks=[
                "No AI usage risks detected.",
            ],
            metadata={
                "source": "stub-usage-service",
            },
        )


def test_record_ai_usage_endpoint_should_return_record() -> None:
    service = StubAIUsageTrackingService()
    app.dependency_overrides[
        get_ai_usage_tracking_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/usage/records",
            json={
                "provider": "openai",
                "model_name": "test-model",
                "component": "llm",
                "operation": "requirement_analysis",
                "prompt_tokens": 1000,
                "completion_tokens": 500,
                "input_cost_per_1k_tokens_usd": 0.01,
                "output_cost_per_1k_tokens_usd": 0.03,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_id"] == "usage-record-001"
        assert body["provider"] == "openai"
        assert body["model_name"] == "test-model"
        assert body["component"] == "llm"
        assert body["operation"] == "requirement_analysis"
        assert body["total_tokens"] == 1500
        assert body["total_cost_usd"] == 0.025

        assert service.last_record_request is not None
        assert service.last_record_request.provider == "openai"
    finally:
        app.dependency_overrides.clear()


def test_list_ai_usage_records_endpoint_should_return_records() -> None:
    app.dependency_overrides[
        get_ai_usage_tracking_service
    ] = lambda: StubAIUsageTrackingService()

    try:
        client = TestClient(app)

        response = client.get(
            "/observability/usage/records?provider=openai&component=llm&limit=10"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["count"] == 1
        assert body["records"][0]["provider"] == "openai"
        assert body["metadata"]["provider"] == "openai"
        assert body["metadata"]["component"] == "llm"
        assert body["metadata"]["limit"] == 10
    finally:
        app.dependency_overrides.clear()


def test_summarize_ai_usage_endpoint_should_return_summary() -> None:
    service = StubAIUsageTrackingService()
    app.dependency_overrides[
        get_ai_usage_tracking_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/usage/summary",
            json={
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["total_tokens"] == 1500
        assert body["total_cost_usd"] == 0.025
        assert body["provider_coverage"]["openai"] == 1

        assert service.last_summary_request is not None
        assert service.last_summary_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_summarize_stored_ai_usage_endpoint_should_return_summary() -> None:
    app.dependency_overrides[
        get_ai_usage_tracking_service
    ] = lambda: StubAIUsageTrackingService()

    try:
        client = TestClient(app)

        response = client.get("/observability/usage/summary")

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["total_tokens"] == 1500
        assert body["average_cost_usd"] == 0.025
    finally:
        app.dependency_overrides.clear()


def test_record_ai_usage_endpoint_should_reject_invalid_provider() -> None:
    client = TestClient(app)

    response = client.post(
        "/observability/usage/records",
        json={
            "provider": "invalid-provider",
            "model_name": "test-model",
            "component": "llm",
            "operation": "requirement_analysis",
        },
    )

    assert response.status_code == 422
