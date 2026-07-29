from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


SpecializedAgentStatus = Literal[
    "available",
    "disabled",
]


class SpecializedAgentCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SpecializedAgentDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    status: SpecializedAgentStatus = "available"
    domain: str = Field(min_length=1)
    description: str = Field(min_length=1)
    capabilities: list[SpecializedAgentCapability] = Field(
        default_factory=list
    )
    entrypoint: str = Field(min_length=1)
    endpoint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SpecializedAgentRegistryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agents: list[SpecializedAgentDescriptor]
    agent_count: int = Field(ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SpecializedAgentRegistry:
    def __init__(
        self,
        agents: list[SpecializedAgentDescriptor] | None = None,
    ) -> None:
        self._agents_by_name: dict[str, SpecializedAgentDescriptor] = {}

        selected_agents = (
            [
                build_qa_agent_descriptor(),
                build_data_analyst_agent_descriptor(),
            ]
            if agents is None
            else agents
        )

        for agent in selected_agents:
            self.register(agent)

    def register(
        self,
        agent: SpecializedAgentDescriptor,
    ) -> None:
        if agent.name in self._agents_by_name:
            raise ValueError(
                f"Specialized agent already registered: {agent.name}"
            )

        self._agents_by_name[agent.name] = agent

    def get(
        self,
        name: str,
    ) -> SpecializedAgentDescriptor:
        agent = self._agents_by_name.get(name)

        if agent is None:
            raise KeyError(
                f"Specialized agent not found: {name}"
            )

        return agent

    def list_agents(self) -> list[SpecializedAgentDescriptor]:
        return [
            self._agents_by_name[name]
            for name in sorted(self._agents_by_name)
        ]

    def to_response(self) -> SpecializedAgentRegistryResponse:
        agents = self.list_agents()

        return SpecializedAgentRegistryResponse(
            agents=agents,
            agent_count=len(agents),
            metadata={
                "registry": "specialized-agent-registry-v1",
            },
        )


def build_qa_agent_descriptor() -> SpecializedAgentDescriptor:
    return SpecializedAgentDescriptor(
        name="qa-agent-v1",
        version="v1",
        status="available",
        domain="quality_engineering",
        description=(
            "Specialized QA agent for requirement analysis, RAG-assisted "
            "answers and quality engineering workflows."
        ),
        capabilities=[
            SpecializedAgentCapability(
                name="requirement_analysis",
                description="Analyze requirements and identify QA-relevant information.",
            ),
            SpecializedAgentCapability(
                name="rag_retrieval",
                description="Retrieve knowledge from ingested documents.",
            ),
            SpecializedAgentCapability(
                name="rag_answering",
                description="Generate answers grounded in retrieved context.",
            ),
        ],
        entrypoint="ai_api.agents.qa_agent",
        endpoint="/agents/qa/run",
        metadata={
            "agent_type": "domain_agent",
            "runtime_integration": "existing",
        },
    )


def build_data_analyst_agent_descriptor() -> SpecializedAgentDescriptor:
    return SpecializedAgentDescriptor(
        name="data-analyst-agent-v1",
        version="v1",
        status="available",
        domain="data_analysis",
        description=(
            "Specialized Data Analyst agent for natural-language SQL "
            "generation, read-only validation, controlled execution and "
            "query evidence generation."
        ),
        capabilities=[
            SpecializedAgentCapability(
                name="database_schema_understanding",
                description="Represent database schemas, tables and columns.",
            ),
            SpecializedAgentCapability(
                name="natural_language_to_sql",
                description="Generate SQL candidates from natural-language questions.",
            ),
            SpecializedAgentCapability(
                name="read_only_sql_safety",
                description="Validate SQL candidates and block unsafe operations.",
            ),
            SpecializedAgentCapability(
                name="controlled_query_execution",
                description="Execute approved SQL against controlled in-memory data.",
            ),
            SpecializedAgentCapability(
                name="agent_evaluation",
                description="Evaluate Data Analyst Agent responses deterministically.",
            ),
        ],
        entrypoint="ai_api.data_analysis.agent.DataAnalystAgentService",
        endpoint="/data-analysis/agent/run",
        metadata={
            "agent_type": "domain_agent",
            "runtime_integration": "adapter_pending",
            "execution_mode": "controlled_in_memory_sqlite",
            "future_extensions": [
                "generic_agent_runtime_adapter",
                "qa_agent_tool_integration",
                "database_connector_abstraction",
                "nosql_data_source_abstraction",
            ],
        },
    )


def get_specialized_agent_registry() -> SpecializedAgentRegistry:
    return SpecializedAgentRegistry()
