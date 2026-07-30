from typing import Any
from fastapi.testclient import TestClient
from ai_api.main import app
from ai_api.multi_agent import (
    MultiAgentEvaluationMetric,
    MultiAgentQACopilotEvaluationResponse,
    MultiAgentQACopilotEvaluationService,
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotService,
    get_multi_agent_qa_copilot_evaluation_service,
)


class StubMultiAgentQACopilotEvaluationService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def evaluate(self, request: Any) -> MultiAgentQACopilotEvaluationResponse:
        self.last_request = request

        return MultiAgentQACopilotEvaluationResponse(
            status="passed",
            score=1.0,
            metrics=[
                MultiAgentEvaluationMetric(
                    name="status_alignment",
                    status="passed",
                    score=1.0,
                    summary="Status matched.",
                )
            ],
            metadata={
                "source": "stub-evaluation-service",
            },
        )


def test_evaluate_multi_agent_qa_copilot_endpoint_should_return_evaluation() -> None:
    copilot_response = MultiAgentQACopilotService().run(
        MultiAgentQACopilotRequest(
            requirement_text=(
                "Como QA, preciso validar o saldo final por conta considerando "
                "depósitos e retiradas."
            ),
            language="pt-BR",
        )
    )

    service = StubMultiAgentQACopilotEvaluationService()
    app.dependency_overrides[
        get_multi_agent_qa_copilot_evaluation_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/multi-agent/qa-copilot/evaluate",
            json={
                "response": copilot_response.model_dump(mode="json"),
                "expected_status": "completed",
                "expected_quality_gate": "approved",
                "require_all_roles": True,
                "require_contracts_passed": True,
                "require_no_failures": True,
                "require_no_critical_conflicts": True,
                "require_final_report": True,
                "require_data_validation_evidence": False,
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "passed"
        assert body["score"] == 1.0
        assert body["metrics"][0]["name"] == "status_alignment"
        assert service.last_request is not None
        assert service.last_request.expected_status == "completed"
        assert service.last_request.expected_quality_gate == "approved"
    finally:
        app.dependency_overrides.clear()


def test_evaluate_multi_agent_qa_copilot_endpoint_should_reject_missing_response() -> None:
    client = TestClient(app)

    response = client.post(
        "/multi-agent/qa-copilot/evaluate",
        json={
            "expected_status": "completed",
        },
    )

    assert response.status_code == 422
