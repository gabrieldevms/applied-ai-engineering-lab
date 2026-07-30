from typing import Any
from ai_api.agents import (
    SpecializedAgentRegistry,
    ToolRegistry,
)


def get_project_status_tool() -> dict[str, Any]:
    return {
        "project": "applied-ai-engineering-lab",
        "status": "ready_for_m5_mcp_qa_server",
        "current_milestone": "M5 — MCP QA Server",
        "completed_foundations": [
            "AI API Base",
            "LLM Engineering",
            "RAG Knowledge Assistant",
            "AI Agents",
            "File Ingestion Expansion",
            "Data Analyst Agent Foundation",
            "QA Agent and Data Analyst Agent Integration",
            "Agent Evaluation",
            "SQL Workflow Regression Dataset",
        ],
        "available_specialized_agents": [
            "qa-agent-v1",
            "data-analyst-agent-v1",
        ],
        "metadata": {
            "tool": "get_project_status",
            "source": "mcp_server_foundation",
        },
    }


def list_agent_tools_tool() -> dict[str, Any]:
    registry = ToolRegistry()
    response = registry.describe()

    return response.model_dump(mode="json")


def list_specialized_agents_tool() -> dict[str, Any]:
    registry = SpecializedAgentRegistry()
    response = registry.to_response()

    return response.model_dump(mode="json")
