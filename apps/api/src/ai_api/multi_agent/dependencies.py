from ai_api.multi_agent.services import MultiAgentQACopilotService
from ai_api.requirements.dependencies import get_requirement_analyzer_service


def get_multi_agent_qa_copilot_service() -> MultiAgentQACopilotService:
    return MultiAgentQACopilotService(
        requirement_analyzer_service=get_requirement_analyzer_service(),
    )
