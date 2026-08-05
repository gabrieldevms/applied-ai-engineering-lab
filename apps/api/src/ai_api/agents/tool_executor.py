import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any, Protocol
from ai_api.agents.exceptions import ToolExecutionError
from ai_api.agents.schemas import (
    ToolAuthorizationDecision,
    ToolDefinition,
    ToolExecutionResponse,
)
from ai_api.config import get_settings
from ai_api.security.blocked_tool_call_telemetry import (
    BlockedToolCallTelemetryRequest,
    BlockedToolCallTelemetryService,
)
from ai_api.security.audit_logs import (
    AuditActor,
    AuditCaller,
    AuditLogEventRequest,
    AuditLogService,
    AuditPolicy,
    AuditRisk,
    AuditRunContext,
    AuditTarget,
)
from ai_api.agents.tool_registry import ToolRegistry
from ai_api.agents.tool_authorization import ToolAuthorizationService
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
        authorization_service: ToolAuthorizationService | None = None,
        blocked_tool_call_telemetry_service: (
            BlockedToolCallTelemetryService | None
        ) = None,
        audit_log_service: AuditLogService | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry()

        self.authorization_service = (
            authorization_service or ToolAuthorizationService()
        )

        self.blocked_tool_call_telemetry_service = (
            blocked_tool_call_telemetry_service
            if blocked_tool_call_telemetry_service is not None
            else BlockedToolCallTelemetryService.from_settings(get_settings())
        )

        self.audit_log_service = (
            audit_log_service
            if audit_log_service is not None
            else AuditLogService.from_settings(get_settings())
        )

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

        authorization_decision = self.authorization_service.authorize(
            tool=tool_definition,
            metadata=metadata,
        )

        if authorization_decision.status == "blocked":
            self._record_blocked_tool_call_telemetry(
                tool_definition=tool_definition,
                authorization_decision=authorization_decision,
                metadata=metadata,
            )
            self._record_blocked_tool_call_audit_event(
                tool_definition=tool_definition,
                authorization_decision=authorization_decision,
                metadata=metadata,
            )

            raise ToolExecutionError(
                "Tool execution blocked by authorization policy: "
                + "; ".join(authorization_decision.violations)
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
                "tool_risk_level": tool_definition.security.risk_level,
                "requires_human_approval": (
                    tool_definition.security.requires_human_approval
                ),
                "requires_audit_log": tool_definition.security.requires_audit_log,
                "allows_state_change": tool_definition.security.allows_state_change,
                "allows_external_network": (
                    tool_definition.security.allows_external_network
                ),
                "allows_sensitive_data": (
                    tool_definition.security.allows_sensitive_data
                ),
                "requires_prompt_injection_assessment": (
                    tool_definition.security.requires_prompt_injection_assessment
                ),
                "authorization_enforced": True,
                "authorization_status": authorization_decision.status,
                "authorization_reason": authorization_decision.reason,
                "authorization_policy": authorization_decision.metadata[
                    "authorization_policy"
                ],
                "caller_type": authorization_decision.caller_type,
                "environment": authorization_decision.environment,
            },
        )

    def _record_blocked_tool_call_telemetry(
        self,
        tool_definition: ToolDefinition,
        authorization_decision: ToolAuthorizationDecision,
        metadata: dict[str, Any] | None,
    ) -> None:
        execution_metadata = metadata or {}

        try:
            self.blocked_tool_call_telemetry_service.record(
                BlockedToolCallTelemetryRequest(
                    tool_name=tool_definition.name,
                    caller_type=authorization_decision.caller_type,
                    environment=authorization_decision.environment,
                    risk_level=authorization_decision.risk_level,
                    authorization_policy=authorization_decision.metadata[
                        "authorization_policy"
                    ],
                    reason=authorization_decision.reason,
                    violations=authorization_decision.violations,
                    prompt_injection_risk_level=str(
                        execution_metadata.get(
                            "prompt_injection_risk_level",
                            "none",
                        )
                    ).strip().lower()
                    or "none",
                    run_id=_optional_string(execution_metadata.get("run_id")),
                    trace_id=_optional_string(execution_metadata.get("trace_id")),
                    request_id=_optional_string(
                        execution_metadata.get("request_id")
                    ),
                    metadata={
                        "source": "tool_execution_service",
                        "telemetry_bridge": "blocked_tool_call_telemetry",
                        "authorization_enforced": True,
                        "tool_category": tool_definition.metadata.get(
                            "category",
                            "",
                        ),
                        "requires_llm": tool_definition.metadata.get(
                            "requires_llm",
                            False,
                        ),
                        "requires_human_approval": (
                            tool_definition.security.requires_human_approval
                        ),
                        "requires_audit_log": (
                            tool_definition.security.requires_audit_log
                        ),
                        "allows_state_change": (
                            tool_definition.security.allows_state_change
                        ),
                        "allows_external_network": (
                            tool_definition.security.allows_external_network
                        ),
                        "allows_sensitive_data": (
                            tool_definition.security.allows_sensitive_data
                        ),
                        "requires_prompt_injection_assessment": (
                            tool_definition.security.requires_prompt_injection_assessment
                        ),
                    },
                )
            )
        except Exception:
            return
    def _record_blocked_tool_call_audit_event(
        self,
        tool_definition: ToolDefinition,
        authorization_decision: ToolAuthorizationDecision,
        metadata: dict[str, Any] | None,
    ) -> None:
        execution_metadata = metadata or {}

        try:
            self.audit_log_service.record(
                AuditLogEventRequest(
                    event_type="tool_authorization_blocked",
                    severity=_audit_severity_for_tool_risk(
                        authorization_decision.risk_level,
                    ),
                    status="blocked",
                    component="tool_execution_service",
                    operation="execute_tool",
                    environment=authorization_decision.environment,
                    actor=AuditActor(
                        actor_type="backend_service",
                        actor_id="tool-execution-service",
                    ),
                    caller=AuditCaller(
                        caller_type=authorization_decision.caller_type,
                        caller_id=_optional_string(
                            execution_metadata.get("caller_id")
                        ),
                    ),
                    target=AuditTarget(
                        target_type="tool",
                        target_id=tool_definition.name,
                        target_name=tool_definition.name,
                    ),
                    run_context=AuditRunContext(
                        run_id=_optional_string(execution_metadata.get("run_id")),
                        trace_id=_optional_string(
                            execution_metadata.get("trace_id")
                        ),
                        request_id=_optional_string(
                            execution_metadata.get("request_id")
                        ),
                        session_id=_optional_string(
                            execution_metadata.get("session_id")
                        ),
                    ),
                    policy=AuditPolicy(
                        policy_name=str(
                            authorization_decision.metadata.get(
                                "authorization_policy",
                                "tool-authorization-policy-v1",
                            )
                        ),
                        policy_version="v1",
                        decision="blocked",
                        reason=authorization_decision.reason,
                        violations=authorization_decision.violations,
                    ),
                    risk=AuditRisk(
                        risk_level=authorization_decision.risk_level,
                        risk_reasons=authorization_decision.violations,
                        prompt_injection_risk_level=str(
                            authorization_decision.metadata.get(
                                "prompt_injection_risk_level",
                                "none",
                            )
                        )
                        or "none",
                        sensitive_data_detected=(
                            tool_definition.security.allows_sensitive_data
                        ),
                    ),
                    metadata={
                        "source": "tool_execution_service",
                        "audit_bridge": "blocked_tool_call_authorization",
                        "authorization_enforced": True,
                        "raw_arguments_stored": False,
                        "sensitive_payload_stored": False,
                        "tool_category": tool_definition.metadata.get(
                            "category",
                            "",
                        ),
                        "requires_llm": tool_definition.metadata.get(
                            "requires_llm",
                            False,
                        ),
                        "requires_human_approval": (
                            tool_definition.security.requires_human_approval
                        ),
                        "requires_audit_log": (
                            tool_definition.security.requires_audit_log
                        ),
                        "allows_state_change": (
                            tool_definition.security.allows_state_change
                        ),
                        "allows_external_network": (
                            tool_definition.security.allows_external_network
                        ),
                        "allows_sensitive_data": (
                            tool_definition.security.allows_sensitive_data
                        ),
                        "requires_prompt_injection_assessment": (
                            tool_definition.security.requires_prompt_injection_assessment
                        ),
                    },
                )
            )
        except Exception:
            return    

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
    

def _optional_string(value: Any) -> str | None:
    if value is None:
        return None

    cleaned_value = str(value).strip()

    if not cleaned_value:
        return None

    return cleaned_value


def _audit_severity_for_tool_risk(risk_level: str) -> str:
    if risk_level == "critical":
        return "critical"

    if risk_level in {"medium", "high"}:
        return "high"

    return "warning"
