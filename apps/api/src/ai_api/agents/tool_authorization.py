from typing import Any, get_args
from ai_api.agents.schemas import (
    ToolAuthorizationDecision,
    ToolCallerType,
    ToolDefinition,
    ToolEnvironment,
)


DEFAULT_TOOL_CALLER_TYPE: ToolCallerType = "backend_service"
DEFAULT_TOOL_ENVIRONMENT: ToolEnvironment = "local"

_ALLOWED_CALLER_TYPES = set(get_args(ToolCallerType))
_ALLOWED_ENVIRONMENTS = set(get_args(ToolEnvironment))


class ToolAuthorizationService:
    def authorize(
        self,
        tool: ToolDefinition,
        metadata: dict[str, Any] | None = None,
    ) -> ToolAuthorizationDecision:
        execution_metadata = metadata or {}

        caller_type, caller_violations = _resolve_caller_type(execution_metadata)
        environment, environment_violations = _resolve_environment(
            execution_metadata,
        )

        violations = [
            *caller_violations,
            *environment_violations,
        ]

        if caller_type not in tool.security.allowed_callers:
            violations.append(
                f"Tool is not allowed for caller_type={caller_type}."
            )

        if environment not in tool.security.allowed_environments:
            violations.append(
                f"Tool is not allowed in environment={environment}."
            )

        human_approval_granted = _is_truthy(
            execution_metadata.get("human_approval_granted"),
        )

        if tool.security.requires_human_approval and not human_approval_granted:
            violations.append(
                "Tool requires human approval, but approval was not granted."
            )

        prompt_injection_risk_level = str(
            execution_metadata.get("prompt_injection_risk_level", "")
        ).strip().lower()

        if (
            tool.security.requires_prompt_injection_assessment
            and prompt_injection_risk_level == "high"
        ):
            violations.append(
                "Tool execution blocked because prompt injection risk is high."
            )

        status = "blocked" if violations else "allowed"

        return ToolAuthorizationDecision(
            status=status,
            tool_name=tool.name,
            caller_type=caller_type,
            environment=environment,
            risk_level=tool.security.risk_level,
            reason=(
                "Tool execution is allowed by authorization policy."
                if status == "allowed"
                else "Tool execution is blocked by authorization policy."
            ),
            violations=violations,
            metadata={
                "authorization_policy": "tool-authorization-policy-v1",
                "human_approval_granted": human_approval_granted,
                "prompt_injection_risk_level": prompt_injection_risk_level,
            },
        )


def _resolve_caller_type(
    metadata: dict[str, Any],
) -> tuple[ToolCallerType, list[str]]:
    raw_caller_type = str(
        metadata.get("caller_type", DEFAULT_TOOL_CALLER_TYPE)
    ).strip()

    if raw_caller_type in _ALLOWED_CALLER_TYPES:
        return raw_caller_type, []

    return DEFAULT_TOOL_CALLER_TYPE, [
        f"Invalid caller_type={raw_caller_type}.",
    ]


def _resolve_environment(
    metadata: dict[str, Any],
) -> tuple[ToolEnvironment, list[str]]:
    raw_environment = str(
        metadata.get("environment", DEFAULT_TOOL_ENVIRONMENT)
    ).strip()

    if raw_environment in _ALLOWED_ENVIRONMENTS:
        return raw_environment, []

    return DEFAULT_TOOL_ENVIRONMENT, [
        f"Invalid environment={raw_environment}.",
    ]


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "approved",
        "granted",
    }
