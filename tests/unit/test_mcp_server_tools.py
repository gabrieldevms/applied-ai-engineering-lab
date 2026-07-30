from ai_api.mcp_server import (
    get_project_status_tool,
    list_agent_tools_tool,
    list_specialized_agents_tool,
)


def test_get_project_status_tool_should_return_m5_status() -> None:
    response = get_project_status_tool()

    assert response["project"] == "applied-ai-engineering-lab"
    assert response["status"] == "ready_for_m5_mcp_qa_server"
    assert response["current_milestone"] == "M5 — MCP QA Server"
    assert "AI Agents" in response["completed_foundations"]
    assert "Data Analyst Agent Foundation" in response["completed_foundations"]
    assert "qa-agent-v1" in response["available_specialized_agents"]
    assert "data-analyst-agent-v1" in response["available_specialized_agents"]


def test_list_agent_tools_tool_should_return_registered_tools() -> None:
    response = list_agent_tools_tool()

    tool_names = [
        tool["name"]
        for tool in response["tools"]
    ]

    assert response["total_tools"] == 4
    assert "rag.retrieve" in tool_names
    assert "rag.answer" in tool_names
    assert "requirements.analyze" in tool_names
    assert "data_analysis.agent.run" in tool_names
    assert response["metadata"]["registry"] == "agent-tool-registry-v1"


def test_list_specialized_agents_tool_should_return_registered_agents() -> None:
    response = list_specialized_agents_tool()

    agent_names = [
        agent["name"]
        for agent in response["agents"]
    ]

    assert response["agent_count"] == 2
    assert "qa-agent-v1" in agent_names
    assert "data-analyst-agent-v1" in agent_names
    assert response["metadata"]["registry"] == "specialized-agent-registry-v1"
