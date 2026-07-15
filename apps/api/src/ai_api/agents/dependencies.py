from ai_api.agents.fake_responses import DEFAULT_AGENT_PLAN_RESPONSE_JSON
from ai_api.agents.planning import AgentPlanningService
from ai_api.config import get_settings
from ai_api.llm.factory import build_llm_provider
from ai_api.agents.tool_selection import AgentToolSelectionService


def get_agent_planning_service() -> AgentPlanningService:
    settings = get_settings()

    llm_provider = build_llm_provider(
        settings=settings,
        fake_response_content=DEFAULT_AGENT_PLAN_RESPONSE_JSON,
    )

    return AgentPlanningService(
        llm_provider=llm_provider,
    )


def get_agent_tool_selection_service() -> AgentToolSelectionService:
    planning_service = get_agent_planning_service()

    return AgentToolSelectionService(
        planning_service=planning_service,
    )
