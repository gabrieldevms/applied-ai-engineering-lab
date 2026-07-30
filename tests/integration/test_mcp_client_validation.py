import pytest
from fastmcp import Client
from ai_api.mcp_server.server import mcp


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_mcp_client_should_list_available_tools() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

    tool_names = {
        tool.name
        for tool in tools
    }

    assert {
        "get_project_status",
        "list_agent_tools",
        "list_specialized_agents",
        "analyze_requirement",
        "retrieve_rag_context",
        "answer_with_rag",
        "run_qa_agent",
        "run_data_analyst_agent",
        "run_sql_regression_suite",
        "run_multi_agent_qa_copilot",
    }.issubset(tool_names)


@pytest.mark.anyio
async def test_mcp_client_should_call_project_status_tool() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool("get_project_status", {})

    assert result.data["project"] == "applied-ai-engineering-lab"
    assert result.data["status"] == "m6_multi_agent_qa_copilot_in_progress"
    assert result.data["current_milestone"] == "M6 — Multi-Agent QA Copilot"
    assert "M5 MCP QA Server" in result.data["completed_foundations"]
    assert "Multi-Agent Data Validation Integration" in (
        result.data["completed_foundations"]
    )
    assert "run_multi_agent_qa_copilot" in result.data["available_mcp_tools"]
    assert "multi-agent-qa-copilot-v1" in result.data["available_copilots"]

@pytest.mark.anyio
async def test_mcp_client_should_call_agent_tool_registry() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool("list_agent_tools", {})

    tool_names = {
        tool["name"]
        for tool in result.data["tools"]
    }

    assert result.data["total_tools"] == 4
    assert "rag.retrieve" in tool_names
    assert "rag.answer" in tool_names
    assert "requirements.analyze" in tool_names
    assert "data_analysis.agent.run" in tool_names
    assert result.data["metadata"]["registry"] == "agent-tool-registry-v1"


@pytest.mark.anyio
async def test_mcp_client_should_call_specialized_agent_registry() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool("list_specialized_agents", {})

    agent_names = {
        agent["name"]
        for agent in result.data["agents"]
    }

    assert result.data["agent_count"] == 2
    assert "qa-agent-v1" in agent_names
    assert "data-analyst-agent-v1" in agent_names
    assert result.data["metadata"]["registry"] == "specialized-agent-registry-v1"
