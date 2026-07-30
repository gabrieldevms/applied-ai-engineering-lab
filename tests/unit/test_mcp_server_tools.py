import pytest
from pydantic import ValidationError
from ai_api.llm import FakeLLMProvider
from ai_api.mcp_server import (
    analyze_requirement_tool,
    get_project_status_tool,
    list_agent_tools_tool,
    list_specialized_agents_tool,
)
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.services import RequirementAnalyzerService


def _build_requirement_analyzer_service() -> RequirementAnalyzerService:
    return RequirementAnalyzerService(
        llm_provider=FakeLLMProvider(
            response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
        ),
        retry_config=RetryConfig(max_attempts=2),
    )


def test_get_project_status_tool_should_return_m5_status() -> None:
    response = get_project_status_tool()

    assert response["project"] == "applied-ai-engineering-lab"
    assert response["status"] == "m5_mcp_qa_server_in_progress"
    assert response["current_milestone"] == "M5 — MCP QA Server"
    assert "AI Agents" in response["completed_foundations"]
    assert "Data Analyst Agent Foundation" in response["completed_foundations"]
    assert "MCP Server Foundation" in response["completed_foundations"]
    assert "analyze_requirement" in response["available_mcp_tools"]
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


def test_analyze_requirement_tool_should_return_structured_analysis() -> None:
    response = analyze_requirement_tool(
        requirement_text=(
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        language="pt-BR",
        analyzer_service=_build_requirement_analyzer_service(),
    )

    assert response["summary"]
    assert isinstance(response["business_rules"], list)
    assert isinstance(response["acceptance_criteria"], list)
    assert isinstance(response["risks"], list)
    assert isinstance(response["positive_test_scenarios"], list)
    assert isinstance(response["negative_test_scenarios"], list)
    assert isinstance(response["edge_cases"], list)
    assert isinstance(response["open_questions"], list)
    assert isinstance(response["automation_opportunities"], list)
    assert set(response.keys()) >= {
        "summary",
        "business_rules",
        "acceptance_criteria",
        "risks",
        "positive_test_scenarios",
        "negative_test_scenarios",
        "edge_cases",
        "open_questions",
        "automation_opportunities",
    }


def test_analyze_requirement_tool_should_reject_blank_requirement() -> None:
    with pytest.raises(ValidationError):
        analyze_requirement_tool(
            requirement_text="",
            language="pt-BR",
            analyzer_service=_build_requirement_analyzer_service(),
        )
