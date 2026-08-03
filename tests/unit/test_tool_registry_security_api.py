from fastapi.testclient import TestClient
from ai_api.main import app


client = TestClient(app)


def test_agents_tools_endpoint_should_return_tool_security_metadata() -> None:
    response = client.get("/agents/tools")

    assert response.status_code == 200

    body = response.json()

    assert body["metadata"]["security_classification"] == (
        "tool-risk-classification-v1"
    )
    assert body["metadata"]["authorization_enforced"] is True

    tools = body["tools"]

    assert tools

    for tool in tools:
        assert "security" in tool
        assert tool["security"]["risk_level"] in [
            "low",
            "medium",
            "high",
            "critical",
        ]
        assert tool["security"]["allowed_callers"]
        assert tool["security"]["allowed_environments"]


def test_agents_tools_endpoint_should_classify_data_analysis_tool_as_medium_risk() -> None:
    response = client.get("/agents/tools")

    assert response.status_code == 200

    body = response.json()
    tools_by_name = {tool["name"]: tool for tool in body["tools"]}

    data_analysis_tool = tools_by_name["data_analysis.agent.run"]

    assert data_analysis_tool["security"]["risk_level"] == "medium"
    assert data_analysis_tool["security"]["allows_sensitive_data"] is True
    assert data_analysis_tool["security"][
        "requires_prompt_injection_assessment"
    ] is True
