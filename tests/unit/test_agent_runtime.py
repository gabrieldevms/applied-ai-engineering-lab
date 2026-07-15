import pytest
from ai_api.agents import AgentRuntime, AgentToolCall


def test_agent_runtime_should_complete_run_without_context() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Analyze a requirement and identify risks.",
    )

    assert response.status == "completed"
    assert response.objective == "Analyze a requirement and identify risks."
    assert response.run_id.startswith("agent-run-")
    assert response.final_answer
    assert len(response.steps) == 3
    assert response.steps[0].name == "understand_objective"
    assert response.steps[1].status == "skipped"
    assert response.metadata["has_context"] is False


def test_agent_runtime_should_complete_run_with_context() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Summarize retrieved context.",
        context="Relevant context about billing requirements.",
    )

    assert response.status == "completed"
    assert len(response.steps) == 3
    assert response.steps[1].status == "completed"
    assert response.metadata["has_context"] is True


def test_agent_runtime_should_respect_max_steps() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Run a short agent execution.",
        max_steps=2,
    )

    assert len(response.steps) == 2
    assert response.steps[-1].name == "inspect_context"


def test_agent_runtime_should_reject_blank_objective() -> None:
    runtime = AgentRuntime()

    with pytest.raises(ValueError, match="objective cannot be blank"):
        runtime.run(objective="   ")


def test_agent_runtime_should_reject_invalid_max_steps() -> None:
    runtime = AgentRuntime()

    with pytest.raises(
        ValueError,
        match="max_steps must be greater than zero",
    ):
        runtime.run(
            objective="Valid objective.",
            max_steps=0,
        )


def test_agent_runtime_should_execute_tool_call() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Recuperar contexto relevante sobre boleto.",
        max_steps=4,
        tool_calls=[
            AgentToolCall(
                tool_name="rag.retrieve",
                arguments={
                    "query": "boleto cobrança",
                    "documents": [
                        {
                            "source": "billing-doc",
                            "title": "Cobrança",
                            "document_text": (
                                "boleto cobrança vencimento pagamento dívida"
                            ),
                            "metadata": {
                                "domain": "billing",
                            },
                        },
                        {
                            "source": "auth-doc",
                            "title": "Autenticação",
                            "document_text": (
                                "login senha autenticação usuário sessão"
                            ),
                            "metadata": {
                                "domain": "auth",
                            },
                        },
                    ],
                    "top_k": 1,
                    "chunk_size": 200,
                    "chunk_overlap": 40,
                },
            )
        ],
    )

    assert response.status == "completed"
    assert response.metadata["requested_tool_calls"] == 1
    assert len(response.steps) == 4
    assert response.steps[2].name == "tool_call:rag.retrieve"
    assert response.steps[2].status == "completed"
    assert response.steps[2].output["tool_name"] == "rag.retrieve"
    assert response.steps[2].output["output"]["total_retrieved_chunks"] == 1
    assert response.steps[3].name == "produce_final_answer"


def test_agent_runtime_should_return_failed_status_when_tool_call_fails() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Executar uma ferramenta inexistente.",
        max_steps=4,
        tool_calls=[
            AgentToolCall(
                tool_name="unknown.tool",
                arguments={},
            )
        ],
    )

    assert response.status == "failed"
    assert response.steps[2].name == "tool_call:unknown.tool"
    assert response.steps[2].status == "failed"
    assert (
        response.steps[2].output["error"]
        == "Tool is not registered: unknown.tool"
    )
    assert "failed while calling a tool" in response.final_answer


def test_agent_runtime_should_execute_requirement_analysis_tool_call() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Analisar requisito de renegociação de dívida.",
        max_steps=4,
        tool_calls=[
            AgentToolCall(
                tool_name="requirements.analyze",
                arguments={
                    "requirement_text": (
                        "Como cliente, quero renegociar minha dívida para "
                        "gerar um boleto atualizado."
                    ),
                    "language": "pt-BR",
                },
            )
        ],
    )

    assert response.status == "completed"
    assert response.metadata["requested_tool_calls"] == 1
    assert response.steps[2].name == "tool_call:requirements.analyze"
    assert response.steps[2].status == "completed"
    assert response.steps[2].output["tool_name"] == "requirements.analyze"
    assert response.steps[2].output["output"]["summary"]
    assert "risks" in response.steps[2].output["output"]


def test_agent_runtime_should_execute_rag_answer_tool_call() -> None:
    runtime = AgentRuntime()

    response = runtime.run(
        objective="Responder pergunta com base em contexto recuperado.",
        max_steps=4,
        tool_calls=[
            AgentToolCall(
                tool_name="rag.answer",
                arguments={
                    "query": "Como o cliente pode gerar boleto?",
                    "documents": [
                        {
                            "source": "requirement-001",
                            "title": "Renegociação",
                            "document_text": (
                                "Após renegociar a dívida, o cliente pode "
                                "gerar um boleto atualizado."
                            ),
                            "metadata": {
                                "domain": "billing",
                            },
                        }
                    ],
                    "language": "pt-BR",
                    "top_k": 1,
                    "chunk_size": 200,
                    "chunk_overlap": 40,
                },
            )
        ],
    )

    assert response.status == "completed"
    assert response.metadata["requested_tool_calls"] == 1
    assert response.steps[2].name == "tool_call:rag.answer"
    assert response.steps[2].status == "completed"
    assert response.steps[2].output["tool_name"] == "rag.answer"
    assert response.steps[2].output["output"]["answer"]
    assert len(response.steps[2].output["output"]["citations"]) == 1
