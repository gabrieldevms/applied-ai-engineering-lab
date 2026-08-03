import pytest
from ai_api.agents.exceptions import ToolExecutionError
from ai_api.agents.tool_authorization import ToolAuthorizationService
from ai_api.agents.tool_executor import ToolExecutionService
from ai_api.agents.tool_registry import ToolRegistry


def test_tool_authorization_should_allow_default_backend_local_execution() -> None:
    registry = ToolRegistry()
    tool = registry.get("requirements.analyze")

    assert tool is not None

    decision = ToolAuthorizationService().authorize(tool)

    assert decision.status == "allowed"
    assert decision.caller_type == "backend_service"
    assert decision.environment == "local"
    assert decision.violations == []


def test_tool_authorization_should_block_disallowed_caller() -> None:
    registry = ToolRegistry()
    tool = registry.get("requirements.analyze")

    assert tool is not None

    decision = ToolAuthorizationService().authorize(
        tool,
        metadata={
            "caller_type": "future_admin_user",
            "environment": "local",
        },
    )

    assert decision.status == "blocked"
    assert any(
        "caller_type=future_admin_user" in violation
        for violation in decision.violations
    )


def test_tool_authorization_should_block_disallowed_environment() -> None:
    registry = ToolRegistry()
    tool = registry.get("requirements.analyze")

    assert tool is not None

    decision = ToolAuthorizationService().authorize(
        tool,
        metadata={
            "caller_type": "backend_service",
            "environment": "production",
        },
    )

    assert decision.status == "blocked"
    assert any(
        "environment=production" in violation
        for violation in decision.violations
    )


def test_tool_authorization_should_block_high_prompt_injection_risk() -> None:
    registry = ToolRegistry()
    tool = registry.get("requirements.analyze")

    assert tool is not None

    decision = ToolAuthorizationService().authorize(
        tool,
        metadata={
            "caller_type": "backend_service",
            "environment": "local",
            "prompt_injection_risk_level": "high",
        },
    )

    assert decision.status == "blocked"
    assert any(
        "prompt injection risk is high" in violation
        for violation in decision.violations
    )


def test_tool_execution_should_include_authorization_metadata_when_allowed() -> None:
    service = ToolExecutionService()

    response = service.execute(
        tool_name="requirements.analyze",
        arguments={
            "requirement_text": "The user should be able to login.",
            "language": "en",
        },
        metadata={
            "caller_type": "backend_service",
            "environment": "local",
        },
    )

    assert response.status == "completed"
    assert response.metadata["authorization_enforced"] is True
    assert response.metadata["authorization_status"] == "allowed"
    assert response.metadata["authorization_policy"] == (
        "tool-authorization-policy-v1"
    )
    assert response.metadata["caller_type"] == "backend_service"
    assert response.metadata["environment"] == "local"


def test_tool_execution_should_raise_error_when_authorization_blocks_tool() -> None:
    service = ToolExecutionService()

    with pytest.raises(
        ToolExecutionError,
        match="Tool execution blocked by authorization policy",
    ):
        service.execute(
            tool_name="requirements.analyze",
            arguments={
                "requirement_text": "The user should be able to login.",
                "language": "en",
            },
            metadata={
                "caller_type": "future_admin_user",
                "environment": "local",
            },
        )
