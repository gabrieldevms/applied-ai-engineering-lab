from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    AIEvaluationReportAggregationResponse,
    AIEvaluationReportSection,
    get_ai_evaluation_report_aggregation_service,
)
from ai_api.main import app


class StubAIEvaluationReportAggregationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def aggregate(
        self,
        request: Any,
    ) -> AIEvaluationReportAggregationResponse:
        self.last_request = request

        return AIEvaluationReportAggregationResponse(
            status="passed",
            score=1.0,
            summary="AI evaluation report passed.",
            sections=[
                AIEvaluationReportSection(
                    name="prompt_regression",
                    status="passed",
                    score=1.0,
                    summary="Prompt regression passed.",
                    highlights=[
                        "Cases passed: 1.",
                    ],
                    risks=[],
                    metrics={
                        "case_count": 1,
                    },
                )
            ],
            recommendations=[
                "Keep the golden dataset stable and versioned.",
            ],
            metadata={
                "source": "stub-aggregation-service",
            },
        )


def test_aggregate_ai_evaluation_report_endpoint_should_return_report() -> None:
    service = StubAIEvaluationReportAggregationService()
    app.dependency_overrides[
        get_ai_evaluation_report_aggregation_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/evals/reports/aggregate",
            json={
                "prompt_regression_run": {
                    "status": "passed",
                    "suite_name": "prompt-regression-suite",
                    "suite_version": "0.1.0",
                    "case_count": 1,
                    "passed_count": 1,
                    "warning_count": 0,
                    "failed_count": 0,
                    "results": [],
                    "metadata": {
                        "source": "api-test",
                    },
                },
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["score"] == 1.0
        assert body["sections"][0]["name"] == "prompt_regression"
        assert body["metadata"]["source"] == "stub-aggregation-service"

        assert service.last_request is not None
        assert service.last_request.prompt_regression_run is not None
        assert service.last_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_aggregate_ai_evaluation_report_endpoint_should_reject_empty_sources() -> None:
    client = TestClient(app)

    response = client.post(
        "/evals/reports/aggregate",
        json={
            "metadata": {
                "source": "api-test",
            },
        },
    )

    assert response.status_code == 422
