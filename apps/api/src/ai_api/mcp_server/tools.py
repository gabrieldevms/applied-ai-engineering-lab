from typing import Any
from ai_api.agents import (
    SpecializedAgentRegistry,
    ToolRegistry,
)
from ai_api.requirements.dependencies import (
    get_requirement_analyzer_service,
)
from ai_api.requirements.schemas import RequirementAnalysisRequest
from ai_api.requirements.services import RequirementAnalyzerService


def get_project_status_tool() -> dict[str, Any]:
    return {
        "project": "applied-ai-engineering-lab",
        "status": "m5_mcp_qa_server_in_progress",
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
            "MCP Server Foundation",
        ],
        "available_mcp_tools": [
            "get_project_status",
            "list_agent_tools",
            "list_specialized_agents",
            "analyze_requirement",
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


def analyze_requirement_tool(
    requirement_text: str,
    language: str = "pt-BR",
    analyzer_service: RequirementAnalyzerService | None = None,
) -> dict[str, Any]:
    payload = RequirementAnalysisRequest(
        requirement_text=requirement_text,
        language=language,
    )

    selected_service = (
        analyzer_service
        if analyzer_service is not None
        else get_requirement_analyzer_service()
    )

    response = selected_service.analyze(
        requirement_text=payload.requirement_text,
        language=payload.language,
    )

    return response.model_dump(mode="json")
