from typing import Any
from fastmcp import FastMCP
from ai_api.mcp_server.tools import (
    analyze_requirement_tool,
    answer_with_rag_tool,
    get_project_status_tool,
    list_agent_tools_tool,
    list_specialized_agents_tool,
    retrieve_rag_context_tool,
    run_data_analyst_agent_tool,
    run_multi_agent_qa_copilot_tool,
    run_qa_agent_tool,
    run_sql_regression_suite_tool,
)


mcp = FastMCP("Applied AI Engineering Lab MCP Server")


@mcp.tool()
def get_project_status() -> dict[str, Any]:
    """Return the current project status and completed AI engineering foundations."""
    return get_project_status_tool()


@mcp.tool()
def list_agent_tools() -> dict[str, Any]:
    """List the tools currently registered in the Agent Tool Registry."""
    return list_agent_tools_tool()


@mcp.tool()
def list_specialized_agents() -> dict[str, Any]:
    """List the specialized agents currently available in the project."""
    return list_specialized_agents_tool()


@mcp.tool()
def analyze_requirement(
    requirement_text: str,
    language: str = "pt-BR",
) -> dict[str, Any]:
    """Analyze a software requirement and return structured QA-oriented output."""
    return analyze_requirement_tool(
        requirement_text=requirement_text,
        language=language,
    )


@mcp.tool()
def retrieve_rag_context(
    query: str,
    documents: list[dict[str, Any]],
    top_k: int = 3,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> dict[str, Any]:
    """Retrieve relevant RAG context from provided documents."""
    return retrieve_rag_context_tool(
        query=query,
        documents=documents,
        top_k=top_k,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


@mcp.tool()
def answer_with_rag(
    query: str,
    documents: list[dict[str, Any]],
    language: str = "pt-BR",
    top_k: int = 3,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> dict[str, Any]:
    """Generate a grounded answer using RAG over provided documents."""
    return answer_with_rag_tool(
        query=query,
        documents=documents,
        language=language,
        top_k=top_k,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


@mcp.tool()
def run_qa_agent(
    requirement_text: str,
    language: str = "pt-BR",
    max_steps: int = 6,
    data_validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the QA Agent with optional data validation context."""
    return run_qa_agent_tool(
        requirement_text=requirement_text,
        language=language,
        max_steps=max_steps,
        data_validation=data_validation,
    )


@mcp.tool()
def run_data_analyst_agent(
    objective: str,
    database_schema: dict[str, Any],
    table_data: list[dict[str, Any]],
    language: str = "pt-BR",
    max_rows: int = 100,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the Data Analyst Agent with controlled read-only SQL execution."""
    return run_data_analyst_agent_tool(
        objective=objective,
        database_schema=database_schema,
        table_data=table_data,
        language=language,
        max_rows=max_rows,
        metadata=metadata,
    )


@mcp.tool()
def run_sql_regression_suite(
    suite: dict[str, Any],
) -> dict[str, Any]:
    """Run SQL workflow regression scenarios and return deterministic checks."""
    return run_sql_regression_suite_tool(suite=suite)


@mcp.tool()
def run_multi_agent_qa_copilot(
    requirement_text: str,
    objective: str | None = None,
    language: str = "pt-BR",
    context: dict[str, Any] | None = None,
    data_validation: dict[str, Any] | None = None,
    max_agents: int = 6,
    failure_strategy: str = "stop_on_failure",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the Multi-Agent QA Copilot workflow."""
    return run_multi_agent_qa_copilot_tool(
        requirement_text=requirement_text,
        objective=objective,
        language=language,
        context=context,
        data_validation=data_validation,
        max_agents=max_agents,
        failure_strategy=failure_strategy,
        metadata=metadata,
    )


if __name__ == "__main__":
    mcp.run()
