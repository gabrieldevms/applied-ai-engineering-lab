from ai_api.agents.runtime import AgentRuntime
from ai_api.agents.fake_responses import DEFAULT_AGENT_PLAN_RESPONSE_JSON
from ai_api.agents.planning import AgentPlanningService
from ai_api.config import get_settings
from ai_api.llm.factory import build_llm_provider
from ai_api.agents.tool_selection import AgentToolSelectionService
from ai_api.agents.multi_step_execution import AgentMultiStepExecutionService
from ai_api.agents.tool_executor import ToolExecutionService
from ai_api.agents.execution_logs import (
    AgentExecutionLogService,
    FileAgentExecutionLogStore,
)

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


def get_agent_multi_step_execution_service() -> AgentMultiStepExecutionService:
    tool_selection_service = get_agent_tool_selection_service()
    log_service = get_agent_execution_log_service()

    return AgentMultiStepExecutionService(
        tool_selection_service=tool_selection_service,
        log_service=log_service,
    )

def get_agent_execution_log_service() -> AgentExecutionLogService:
    settings = get_settings()

    return AgentExecutionLogService(
        log_store=FileAgentExecutionLogStore(
            file_path=settings.agent_execution_log_path,
        ),
    )


def get_tool_execution_service() -> ToolExecutionService:
    return ToolExecutionService()


def get_agent_runtime() -> AgentRuntime:
    return AgentRuntime(
        tool_execution_service=get_tool_execution_service(),
    )


def get_qa_agent_service():
    from ai_api.agents.qa_agent import QAAgentService

    return QAAgentService(
        agent_runtime=get_agent_runtime(),
    )


def get_qa_agent_evaluation_service():
    from ai_api.agents.qa_evaluation import QAAgentEvaluationService

    return QAAgentEvaluationService()
