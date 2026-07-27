from ai_api.agents import (
    AgentSafetyPolicy,
    AgentSafetyService,
    AgentSelectedToolCall,
)


def test_agent_safety_service_should_pass_when_limits_are_respected() -> None:
    service = AgentSafetyService()

    selected_tool_calls = [
        AgentSelectedToolCall(
            source_step_id="plan-step-1",
            source_step_objective="Analisar requisito.",
            tool_name="requirements.analyze",
            arguments={
                "requirement_text": "Como cliente, quero gerar boleto.",
                "language": "pt-BR",
            },
            rationale="Ferramenta adequada.",
            metadata={
                "requires_llm": True,
            },
        )
    ]

    response = service.evaluate_tool_calls(
        selected_tool_calls=selected_tool_calls,
        executable_tool_calls=selected_tool_calls,
        approval_decisions=[],
    )

    assert response.status == "passed"
    assert response.violations == []


def test_agent_safety_service_should_block_when_tool_is_blocked() -> None:
    service = AgentSafetyService()

    selected_tool_calls = [
        AgentSelectedToolCall(
            source_step_id="plan-step-1",
            source_step_objective="Responder com RAG.",
            tool_name="rag.answer",
            arguments={
                "query": "Como gerar boleto?",
                "documents": [],
            },
            rationale="Resposta fundamentada.",
        )
    ]

    response = service.evaluate_tool_calls(
        selected_tool_calls=selected_tool_calls,
        executable_tool_calls=selected_tool_calls,
        approval_decisions=[],
        safety_policy=AgentSafetyPolicy(
            blocked_tools=["rag.answer"],
        ),
    )

    safe_tool_calls = service.filter_safe_executable_tool_calls(
        executable_tool_calls=selected_tool_calls,
        safety_policy=AgentSafetyPolicy(
            blocked_tools=["rag.answer"],
        ),
    )

    assert response.status == "blocked"
    assert response.violations[0].rule == "blocked_tool"
    assert safe_tool_calls == []


def test_agent_safety_service_should_limit_executable_tool_calls() -> None:
    service = AgentSafetyService()

    selected_tool_calls = [
        AgentSelectedToolCall(
            source_step_id="plan-step-1",
            source_step_objective="Analisar requisito.",
            tool_name="requirements.analyze",
            arguments={
                "requirement_text": "Requisito 1.",
            },
            rationale="Análise 1.",
        ),
        AgentSelectedToolCall(
            source_step_id="plan-step-2",
            source_step_objective="Responder com RAG.",
            tool_name="rag.answer",
            arguments={
                "query": "Pergunta.",
                "documents": [],
            },
            rationale="Resposta 2.",
        ),
    ]

    policy = AgentSafetyPolicy(
        max_executable_tool_calls=1,
    )

    response = service.evaluate_tool_calls(
        selected_tool_calls=selected_tool_calls,
        executable_tool_calls=selected_tool_calls,
        approval_decisions=[],
        safety_policy=policy,
    )

    safe_tool_calls = service.filter_safe_executable_tool_calls(
        executable_tool_calls=selected_tool_calls,
        safety_policy=policy,
    )

    assert response.status == "blocked"
    assert response.violations[0].rule == "max_executable_tool_calls"
    assert len(safe_tool_calls) == 1


def test_agent_safety_service_should_block_llm_tools_when_disabled() -> None:
    service = AgentSafetyService()

    selected_tool_calls = [
        AgentSelectedToolCall(
            source_step_id="plan-step-1",
            source_step_objective="Analisar requisito.",
            tool_name="requirements.analyze",
            arguments={
                "requirement_text": "Como cliente, quero gerar boleto.",
            },
            rationale="Análise.",
            metadata={
                "requires_llm": True,
            },
        )
    ]

    policy = AgentSafetyPolicy(
        allow_llm_tools=False,
    )

    response = service.evaluate_tool_calls(
        selected_tool_calls=selected_tool_calls,
        executable_tool_calls=selected_tool_calls,
        approval_decisions=[],
        safety_policy=policy,
    )

    safe_tool_calls = service.filter_safe_executable_tool_calls(
        executable_tool_calls=selected_tool_calls,
        safety_policy=policy,
    )

    assert response.status == "blocked"
    assert response.violations[0].rule == "llm_tool_not_allowed"
    assert safe_tool_calls == []
