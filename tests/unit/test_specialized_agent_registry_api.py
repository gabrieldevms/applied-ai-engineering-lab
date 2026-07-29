from fastapi.testclient import TestClient
from ai_api.main import app


client = TestClient(app)


def test_specialized_agents_endpoint_should_list_registered_agents() -> None:
    response = client.get("/agents/specialized")

    assert response.status_code == 200

    body = response.json()

    assert body["agent_count"] == 2

    agent_names = [
        agent["name"]
        for agent in body["agents"]
    ]

    assert agent_names == [
        "data-analyst-agent-v1",
        "qa-agent-v1",
    ]


def test_specialized_agents_endpoint_should_include_data_analyst_capabilities() -> None:
    response = client.get("/agents/specialized")

    assert response.status_code == 200

    body = response.json()

    data_analyst_agent = next(
        agent
        for agent in body["agents"]
        if agent["name"] == "data-analyst-agent-v1"
    )

    capability_names = [
        capability["name"]
        for capability in data_analyst_agent["capabilities"]
    ]

    assert data_analyst_agent["domain"] == "data_analysis"
    assert data_analyst_agent["endpoint"] == "/data-analysis/agent/run"
    assert "natural_language_to_sql" in capability_names
    assert "controlled_query_execution" in capability_names
    assert (
        data_analyst_agent["metadata"]["runtime_integration"]
        == "adapter_pending"
    )
