from fastapi.testclient import TestClient

from ai_api.evals import (
    AIObservabilityDashboardResponse,
    AIObservabilityDashboardSection,
    get_ai_observability_dashboard_service,
)
from ai_api.main import app


class StubAIObservabilityDashboardService:
    def get_dashboard(self) -> AIObservabilityDashboardResponse:
        return AIObservabilityDashboardResponse(
            status="healthy",
            generated_at="2026-07-30T20:00:00+00:00",
            sections=[
                AIObservabilityDashboardSection(
                    name="usage",
                    title="Token and cost usage",
                    status="healthy",
                    metrics={
                        "record_count": 1,
                        "total_tokens": 1500,
                        "total_cost_usd": 0.025,
                    },
                    risks=[
                        "No usage risks detected.",
                    ],
                    recommendations=[
                        "Continue monitoring Token and cost usage over time.",
                    ],
                )
            ],
            global_risks=[
                "No global observability risks detected.",
            ],
            recommendations=[
                "Observability indicators are healthy. Continue monitoring trends across evaluation and agent workflows.",
            ],
            metadata={
                "dashboard_schema_version": "0.1.0",
                "dashboard_type": "backend_observability_read_model",
                "future_frontend": "AI Quality Command Center",
            },
        )


def test_get_observability_dashboard_endpoint_should_return_dashboard() -> None:
    app.dependency_overrides[
        get_ai_observability_dashboard_service
    ] = lambda: StubAIObservabilityDashboardService()

    try:
        client = TestClient(app)

        response = client.get("/observability/dashboard")

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "healthy"
        assert body["sections"][0]["name"] == "usage"
        assert body["sections"][0]["status"] == "healthy"
        assert body["sections"][0]["metrics"]["total_tokens"] == 1500
        assert body["metadata"]["future_frontend"] == "AI Quality Command Center"
    finally:
        app.dependency_overrides.clear()
