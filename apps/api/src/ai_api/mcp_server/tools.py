from typing import Any
from ai_api.agents import (
    QAAgentRunRequest,
    SpecializedAgentRegistry,
    ToolExecutionService,
    ToolRegistry,
    get_qa_agent_service,
)
from ai_api.data_analysis.agent import DataAnalystAgentRequest
from ai_api.data_analysis.dependencies import get_data_analyst_agent_service
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
            "Requirement Analysis MCP Tool",
            "RAG MCP Tools",
            "QA Agent MCP Tool",
        ],
        "available_mcp_tools": [
            "get_project_status",
            "list_agent_tools",
            "list_specialized_agents",
            "analyze_requirement",
            "retrieve_rag_context",
            "answer_with_rag",
            "run_qa_agent",
            "run_data_analyst_agent",
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


def retrieve_rag_context_tool(
    query: str,
    documents: list[dict[str, Any]],
    top_k: int = 3,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    tool_execution_service: ToolExecutionService | None = None,
) -> dict[str, Any]:
    selected_service = (
        tool_execution_service
        if tool_execution_service is not None
        else ToolExecutionService()
    )

    response = selected_service.execute(
        tool_name="rag.retrieve",
        arguments={
            "query": query,
            "documents": documents,
            "top_k": top_k,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        },
        metadata={
            "requested_by": "mcp_server",
            "mcp_tool": "retrieve_rag_context",
        },
    )

    return response.output


def answer_with_rag_tool(
    query: str,
    documents: list[dict[str, Any]],
    language: str = "pt-BR",
    top_k: int = 3,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    tool_execution_service: ToolExecutionService | None = None,
) -> dict[str, Any]:
    selected_service = (
        tool_execution_service
        if tool_execution_service is not None
        else ToolExecutionService()
    )

    response = selected_service.execute(
        tool_name="rag.answer",
        arguments={
            "query": query,
            "documents": documents,
            "language": language,
            "top_k": top_k,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        },
        metadata={
            "requested_by": "mcp_server",
            "mcp_tool": "answer_with_rag",
        },
    )

    return response.output


def run_qa_agent_tool(
    requirement_text: str,
    language: str = "pt-BR",
    max_steps: int = 6,
    data_validation: dict[str, Any] | None = None,
    qa_agent_service: Any | None = None,
) -> dict[str, Any]:
    request_payload: dict[str, Any] = {
        "requirement_text": requirement_text,
        "language": language,
        "max_steps": max_steps,
    }

    if data_validation is not None:
        request_payload["data_validation"] = data_validation

    payload = QAAgentRunRequest.model_validate(request_payload)

    selected_service = (
        qa_agent_service
        if qa_agent_service is not None
        else get_qa_agent_service()
    )

    response = selected_service.run(payload)

    return response.model_dump(mode="json")


def run_data_analyst_agent_tool(
    objective: str,
    database_schema: dict[str, Any],
    table_data: list[dict[str, Any]],
    language: str = "pt-BR",
    max_rows: int = 100,
    metadata: dict[str, Any] | None = None,
    data_analyst_agent_service: Any | None = None,
) -> dict[str, Any]:
    payload = DataAnalystAgentRequest.model_validate(
        {
            "objective": objective,
            "language": language,
            "database_schema": database_schema,
            "table_data": table_data,
            "max_rows": max_rows,
            "metadata": metadata or {},
        }
    )

    selected_service = (
        data_analyst_agent_service
        if data_analyst_agent_service is not None
        else get_data_analyst_agent_service()
    )

    response = selected_service.run(payload)

    return response.model_dump(mode="json")
