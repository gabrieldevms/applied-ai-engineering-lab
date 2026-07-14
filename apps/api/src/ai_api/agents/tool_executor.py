import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any, Protocol

from ai_api.agents.exceptions import ToolExecutionError
from ai_api.agents.schemas import ToolExecutionResponse
from ai_api.agents.tool_registry import ToolRegistry
from ai_api.rag import RetrievalRequest, RetrievalService


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


class ToolExecutionService:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
        handlers: Mapping[str, ToolHandler] | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry()
        self.handlers = dict(
            handlers
            or {
                RAGRetrieveTool.tool_name: RAGRetrieveTool(),
            }
        )

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
            },
        )

    def _build_execution_id(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
    ) -> str:
        safe_tool_name = re.sub(r"[^a-zA-Z0-9]+", "-", tool_name).strip("-")
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
