import pytest
from ai_api.agents.specialized_registry import (
    SpecializedAgentDescriptor,
    SpecializedAgentRegistry,
)


def test_specialized_agent_registry_should_register_default_agents() -> None:
    registry = SpecializedAgentRegistry()

    response = registry.to_response()

    agent_names = [
        agent.name
        for agent in response.agents
    ]

    assert response.agent_count == 2
    assert agent_names == [
        "data-analyst-agent-v1",
        "qa-agent-v1",
    ]


def test_specialized_agent_registry_should_describe_data_analyst_agent() -> None:
    registry = SpecializedAgentRegistry()

    agent = registry.get("data-analyst-agent-v1")

    capability_names = [
        capability.name
        for capability in agent.capabilities
    ]

    assert agent.domain == "data_analysis"
    assert agent.endpoint == "/data-analysis/agent/run"
    assert agent.entrypoint == "ai_api.data_analysis.agent.DataAnalystAgentService"
    assert "natural_language_to_sql" in capability_names
    assert "read_only_sql_safety" in capability_names
    assert "controlled_query_execution" in capability_names
    assert agent.metadata["runtime_integration"] == "adapter_pending"
    assert "nosql_data_source_abstraction" in agent.metadata["future_extensions"]


def test_specialized_agent_registry_should_describe_qa_agent() -> None:
    registry = SpecializedAgentRegistry()

    agent = registry.get("qa-agent-v1")

    capability_names = [
        capability.name
        for capability in agent.capabilities
    ]

    assert agent.domain == "quality_engineering"
    assert agent.endpoint == "/agents/qa/run"
    assert "requirement_analysis" in capability_names
    assert "rag_retrieval" in capability_names
    assert "rag_answering" in capability_names


def test_specialized_agent_registry_should_reject_duplicate_agent_names() -> None:
    agent = SpecializedAgentDescriptor(
        name="duplicate-agent",
        version="v1",
        domain="test",
        description="Test specialized agent.",
        entrypoint="test.Agent",
    )

    with pytest.raises(
        ValueError,
        match="Specialized agent already registered: duplicate-agent",
    ):
        SpecializedAgentRegistry(
            agents=[
                agent,
                agent,
            ]
        )


def test_specialized_agent_registry_should_reject_unknown_agent_name() -> None:
    registry = SpecializedAgentRegistry()

    with pytest.raises(
        KeyError,
        match="Specialized agent not found: unknown-agent",
    ):
        registry.get("unknown-agent")
