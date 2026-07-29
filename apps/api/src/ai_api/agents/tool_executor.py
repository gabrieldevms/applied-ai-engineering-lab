import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any, Protocol
from ai_api.agents.exceptions import ToolExecutionError
from ai_api.agents.schemas import ToolExecutionResponse
from ai_api.agents.tool_registry import ToolRegistry
from ai_api.data_analysis import (
    DataAnalystAgentRequest,
    DataAnalystAgentService,
    get_data_analyst_agent_service,
)
from ai_api.llm import FakeLLMProvider
from ai_api.rag import RetrievalRequest, RetrievalService
from ai_api.rag.answer_generation import RAGAnswerService
from ai_api.rag.fake_responses import DEFAULT_RAG_ANSWER_RESPONSE
from ai_api.rag.schemas import RAGAnswerRequest
from ai_api.rag.semantic_search import SemanticSearchService
from ai_api.requirements.fake_responses import (
    DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
)
from ai_api.requirements.retry import RetryConfig
from ai_api.requirements.schemas import RequirementAnalysisRequest
from ai_api.requirements.services import RequirementAnalyzerService


class ToolHandler(Protocol):
    tool_name: str

    def execute(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        """Execute a tool with validated arguments."""
        ...


class RAGRetrieveTool:
    tool_name = "rag.retrieve"

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service or RetrievalService()

    def execute(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        payload = RetrievalRequest.model_validate(arguments)

        response = self.retrieval_service.retrieve(
            query=payload.query,
            documents=payload.documents,
            top_k=payload.top_k,
            chunk_size=payload.chunk_size,
            chunk_overlap=payload.chunk_overlap,
        )

        return response.model_dump(mode="json")


class RequirementAnalysisTool:
    tool_name = "requirements.analyze"

    def __init__(
        self,
        analyzer_service: RequirementAnalyzerService | None = None,
    ) -> None:
        self.analyzer_service = analyzer_service or RequirementAnalyzerService(
            llm_provider=FakeLLMProvider(
                response_content=DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON,
            ),
            retry_config=RetryConfig(max_attempts=2),
        )

    def execute(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        payload = RequirementAnalysisRequest.model_validate(arguments)

        response = self.analyzer_service.analyze(
            requirement_text=payload.requirement_text,
            language=payload.language,
        )

        return response.model_dump(mode="json")


class RAGAnswerTool:
    tool_name = "rag.answer"

    def __init__(
        self,
        answer_service: RAGAnswerService | None = None,
    ) -> None:
        self.answer_service = answer_service or RAGAnswerService(
            semantic_search_service=SemanticSearchService(),
            llm_provider=FakeLLMProvider(
                response_content=DEFAULT_RAG_ANSWER_RESPONSE,
            ),
        )

    def execute(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        payload = RAGAnswerRequest.model_validate(arguments)

        response = self.answer_service.answer(
            query=payload.query,
            documents=payload.documents,
            language=payload.language,
            top_k=payload.top_k,
            chunk_size=payload.chunk_size,
            chunk_overlap=payload.chunk_overlap,
        )

        return response.model_dump(mode="json")


class DataAnalystAgentTool:
    tool_name = "data_analysis.agent.run"

    def __init__(
        self,
        agent_service: DataAnalystAgentService | None = None,
    ) -> None:
        self.agent_service = (
            agent_service
            if agent_service is not None
            else get_data_analyst_agent_service()
        )

    def execute(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        payload = DataAnalystAgentRequest.model_validate(arguments)

        response = self.agent_service.run(payload)

        return response.model_dump(mode="json")


class ToolExecutionService:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
        handlers: Mapping[str, ToolHandler] | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry()

        default_handlers = {
            RAGRetrieveTool.tool_name: RAGRetrieveTool(),
            RequirementAnalysisTool.tool_name: RequirementAnalysisTool(),
            RAGAnswerTool.tool_name: RAGAnswerTool(),
            DataAnalystAgentTool.tool_name: DataAnalystAgentTool(),
        }

        self.handlers = dict(default_handlers)

        if handlers is not None:
            self.handlers.update(handlers)

    def execute(
        self,
        tool_name: str,
        arguments: Mapping[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ToolExecutionResponse:
        cleaned_tool_name = tool_name.strip()

        if not cleaned_tool_name:
            raise ToolExecutionError("tool_name cannot be blank")

        tool_definition = self.registry.get(cleaned_tool_name)

        if tool_definition is None:
            raise ToolExecutionError(
                f"Tool is not registered: {cleaned_tool_name}"
            )

        handler = self.handlers.get(cleaned_tool_name)

        if handler is None:
            raise ToolExecutionError(
                f"Tool has no execution handler: {cleaned_tool_name}"
            )

        execution_arguments = dict(arguments or {})

        try:
            output = handler.execute(execution_arguments)
        except Exception as exc:
            raise ToolExecutionError(
                f"Tool execution failed for {cleaned_tool_name}: {exc}"
            ) from exc

        return ToolExecutionResponse(
            execution_id=self._build_execution_id(
                tool_name=cleaned_tool_name,
                arguments=execution_arguments,
            ),
            tool_name=cleaned_tool_name,
            status="completed",
            output=output,
            metadata={
                **(metadata or {}),
                "executor": "agent-tool-execution-service-v1",
                "tool_category": tool_definition.metadata.get("category", ""),
                "requires_llm": tool_definition.metadata.get(
                    "requires_llm",
                    False,
                ),
                "specialized_agent": tool_definition.metadata.get(
                    "specialized_agent",
                    "",
                ),
            },
        )

    def _build_execution_id(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
    ) -> str:
        safe_tool_name = re.sub(
            r"[^a-zA-Z0-9]+",
            "-",
            tool_name,
        ).strip("-")

        arguments_payload = json.dumps(
            arguments,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

        arguments_hash = hashlib.sha256(
            arguments_payload.encode("utf-8")
        ).hexdigest()[:12]

        return f"tool-execution-{safe_tool_name}-{arguments_hash}"

    def has_handler(self, tool_name: str) -> bool:
        cleaned_tool_name = tool_name.strip()

        if not cleaned_tool_name:
            return False

        return cleaned_tool_name in self.handlers
