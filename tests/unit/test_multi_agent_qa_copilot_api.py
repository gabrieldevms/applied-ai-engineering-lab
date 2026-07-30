from typing import Any
from fastapi.testclient import TestClient
from ai_api.main import app
from ai_api.multi_agent import (
    MultiAgentQACopilotResponse,
    MultiAgentQACopilotService,
    get_multi_agent_qa_copilot_service,
)


class StubMultiAgentQACopilotService:
    def __init__(self) -> None:
        self.last_request: Any | None = None

    def run(self, request: Any) -> MultiAgentQACopilotResponse:
        self.last_request = request

        return MultiAgentQACopilotResponse(
            status="completed",
            copilot_name="multi-agent-qa-copilot-v1",
            objective=request.objective
            or "Orchestrate a multi-agent QA analysis for the provided requirement.",
            roles=[],
            shared_state={
                "objective": request.objective
                or "Orchestrate a multi-agent QA analysis for the provided requirement.",
                "requirement_text": request.requirement_text,
                "language": request.language,
                "context": request.context,
                "artifacts": [],
                "messages": [],
                "metadata": {
                    "source": "stub-service",
                },
            },
            task_results=[],
            final_report={
                "summary": "Relatório multiagente gerado com sucesso.",
                "requirement_understanding": [
                    "Requisito entendido pelo copilot.",
                ],
                "functional_coverage": [
                    "Cobertura funcional proposta.",
                ],
                "automation_strategy": [
                    "Estratégia de automação proposta.",
                ],
                "review_notes": [
                    "Revisão concluída.",
                ],
                "next_steps": [
                    "Evoluir integração com agentes reais.",
                ],
                "metadata": {
                    "source": "stub-service",
                },
            },
            trace=[],
            metadata={
                "source": "stub-service",
            },
        )


def test_run_multi_agent_qa_copilot_endpoint_should_return_response() -> None:
    service = StubMultiAgentQACopilotService()
    app.dependency_overrides[get_multi_agent_qa_copilot_service] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/multi-agent/qa-copilot/run",
            json={
                "requirement_text": (
                    "Como QA, preciso validar o saldo final por conta "
                    "considerando depósitos e retiradas."
                ),
                "objective": (
                    "Gerar uma análise multiagente de qualidade para o requisito."
                ),
                "language": "pt-BR",
                "context": {
                    "domain": "financial",
                },
                "max_agents": 6,
                "metadata": {
                    "source": "api-test",
                },
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "completed"
        assert body["copilot_name"] == "multi-agent-qa-copilot-v1"
        assert body["objective"] == (
            "Gerar uma análise multiagente de qualidade para o requisito."
        )
        assert body["shared_state"]["requirement_text"] == (
            "Como QA, preciso validar o saldo final por conta "
            "considerando depósitos e retiradas."
        )
        assert body["shared_state"]["language"] == "pt-BR"
        assert body["final_report"]["summary"]
        assert service.last_request is not None
        assert service.last_request.language == "pt-BR"
        assert service.last_request.max_agents == 6
    finally:
        app.dependency_overrides.clear()


def test_run_multi_agent_qa_copilot_endpoint_should_reject_blank_requirement() -> None:
    client = TestClient(app)

    response = client.post(
        "/multi-agent/qa-copilot/run",
        json={
            "requirement_text": "   ",
            "language": "pt-BR",
        },
    )

    assert response.status_code == 422
