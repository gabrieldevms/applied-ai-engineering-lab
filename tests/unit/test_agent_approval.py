from ai_api.agents import (
    AgentApprovalPolicy,
    AgentApprovalService,
    AgentSelectedToolCall,
)


def test_agent_approval_service_should_mark_safe_tool_as_not_required() -> None:
    service = AgentApprovalService()

    decisions = service.evaluate_tool_calls(
        selected_tool_calls=[
            AgentSelectedToolCall(
                source_step_id="plan-step-1",
                source_step_objective="Analisar requisito.",
                tool_name="requirements.analyze",
                arguments={
                    "requirement_text": "Como cliente, quero gerar boleto.",
                    "language": "pt-BR",
                },
                rationale="Ferramenta adequada.",
            )
        ]
    )

    assert len(decisions) == 1
    assert decisions[0].status == "not_required"
    assert decisions[0].tool_name == "requirements.analyze"


def test_agent_approval_service_should_mark_tool_as_pending_when_required() -> None:
    service = AgentApprovalService()

    decisions = service.evaluate_tool_calls(
        selected_tool_calls=[
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
        ],
        approval_policy=AgentApprovalPolicy(
            require_approval_for_tools=["rag.answer"],
        ),
    )

    assert decisions[0].status == "pending"
    assert decisions[0].reason == (
        "Tool requires human approval before execution."
    )


def test_agent_approval_service_should_mark_tool_as_rejected() -> None:
    service = AgentApprovalService()

    decisions = service.evaluate_tool_calls(
        selected_tool_calls=[
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
        ],
        approval_policy=AgentApprovalPolicy(
            reject_tools=["rag.answer"],
        ),
    )

    assert decisions[0].status == "rejected"
    assert decisions[0].reason == (
        "Tool is explicitly rejected by approval policy."
    )


def test_agent_approval_service_should_filter_executable_tool_calls() -> None:
    service = AgentApprovalService()

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
        ),
        AgentSelectedToolCall(
            source_step_id="plan-step-2",
            source_step_objective="Responder com RAG.",
            tool_name="rag.answer",
            arguments={
                "query": "Como gerar boleto?",
                "documents": [],
            },
            rationale="Resposta fundamentada.",
        ),
    ]

    decisions = service.evaluate_tool_calls(
        selected_tool_calls=selected_tool_calls,
        approval_policy=AgentApprovalPolicy(
            require_approval_for_tools=["rag.answer"],
        ),
    )

    executable_tool_calls = service.filter_executable_tool_calls(
        selected_tool_calls=selected_tool_calls,
        approval_decisions=decisions,
    )

    assert len(executable_tool_calls) == 1
    assert executable_tool_calls[0].tool_name == "requirements.analyze"
