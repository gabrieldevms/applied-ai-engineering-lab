from ai_api.agents.tool_executor import ToolExecutionService
from ai_api.agents.tool_registry import ToolRegistry


def test_default_tools_should_have_security_classification() -> None:
    registry = ToolRegistry()

    tools = registry.list_tools()

    assert tools

    for tool in tools:
        assert tool.security.risk_level in {"low", "medium", "high", "critical"}
        assert tool.security.allowed_callers
        assert tool.security.allowed_environments
        assert tool.security.allows_state_change is False
        assert tool.security.allows_external_network is False


def test_low_risk_tools_should_be_read_only_and_not_require_approval() -> None:
    registry = ToolRegistry()

    low_risk_tools = [
        tool for tool in registry.list_tools() if tool.security.risk_level == "low"
    ]

    assert low_risk_tools

    for tool in low_risk_tools:
        assert tool.security.requires_human_approval is False
        assert tool.security.requires_audit_log is False
        assert tool.security.allows_state_change is False


def test_data_analysis_agent_tool_should_be_medium_risk_and_sensitive_data_capable() -> None:
    registry = ToolRegistry()

    tool = registry.get("data_analysis.agent.run")

    assert tool is not None
    assert tool.security.risk_level == "medium"
    assert tool.security.allows_sensitive_data is True
    assert tool.security.requires_prompt_injection_assessment is True
    assert "qa_agent" in tool.security.allowed_callers
    assert "mcp_client" in tool.security.allowed_callers


def test_tool_registry_response_should_expose_security_classification_metadata() -> None:
    registry = ToolRegistry()

    response = registry.describe()
    payload = response.model_dump(mode="json")

    assert payload["metadata"]["security_classification"] == (
        "tool-risk-classification-v1"
    )
    assert payload["metadata"]["authorization_enforced"] is False

    for tool in payload["tools"]:
        assert "security" in tool
        assert "risk_level" in tool["security"]
        assert "allowed_callers" in tool["security"]
        assert "allowed_environments" in tool["security"]


def test_tool_execution_metadata_should_include_security_classification() -> None:
    service = ToolExecutionService()

    response = service.execute(
        tool_name="requirements.analyze",
        arguments={
            "requirement_text": "The user should be able to login.",
            "language": "en",
        },
        metadata={"caller": "unit_test"},
    )

    assert response.status == "completed"
    assert response.metadata["tool_risk_level"] == "low"
    assert response.metadata["requires_human_approval"] is False
    assert response.metadata["requires_audit_log"] is False
    assert response.metadata["allows_state_change"] is False
    assert response.metadata["allows_external_network"] is False
    assert response.metadata["authorization_enforced"] is False
