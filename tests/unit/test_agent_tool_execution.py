import pytest
from ai_api.agents import ToolExecutionError, ToolExecutionService


def test_tool_execution_service_should_execute_rag_retrieve_tool() -> None:
    service = ToolExecutionService()

    response = service.execute(
        tool_name="rag.retrieve",
        arguments={
            "query": "boleto cobrança",
            "documents": [
                {
                    "source": "billing-doc",
                    "title": "Cobrança",
                    "document_text": "boleto cobrança vencimento pagamento dívida",
                    "metadata": {
                        "domain": "billing",
                    },
                },
                {
                    "source": "auth-doc",
                    "title": "Autenticação",
                    "document_text": "login senha autenticação usuário sessão",
                    "metadata": {
                        "domain": "auth",
                    },
                },
            ],
            "top_k": 1,
            "chunk_size": 200,
            "chunk_overlap": 40,
        },
        metadata={
            "requested_by": "agent",
        },
    )

    assert response.status == "completed"
    assert response.tool_name == "rag.retrieve"
    assert response.execution_id.startswith("tool-execution-rag-retrieve-")
    assert response.output["query"] == "boleto cobrança"
    assert response.output["total_retrieved_chunks"] == 1
    assert (
        response.output["retrieved_chunks"][0]["metadata"]["source"]
        == "billing-doc"
    )
    assert response.metadata["requested_by"] == "agent"
    assert response.metadata["tool_category"] == "rag"


def test_tool_execution_service_should_reject_unknown_tool() -> None:
    service = ToolExecutionService()

    with pytest.raises(
        ToolExecutionError,
        match="Tool is not registered: unknown.tool",
    ):
        service.execute(
            tool_name="unknown.tool",
            arguments={},
        )


def test_tool_execution_service_should_reject_unimplemented_tool() -> None:
    service = ToolExecutionService()

    with pytest.raises(
        ToolExecutionError,
        match="Tool has no execution handler: rag.answer",
    ):
        service.execute(
            tool_name="rag.answer",
            arguments={},
        )


def test_tool_execution_service_should_reject_invalid_rag_retrieve_arguments() -> None:
    service = ToolExecutionService()

    with pytest.raises(
        ToolExecutionError,
        match="Tool execution failed for rag.retrieve",
    ):
        service.execute(
            tool_name="rag.retrieve",
            arguments={
                "query": "   ",
                "documents": [],
            },
        )


def test_tool_execution_service_should_reject_blank_tool_name() -> None:
    service = ToolExecutionService()

    with pytest.raises(
        ToolExecutionError,
        match="tool_name cannot be blank",
    ):
        service.execute(
            tool_name="   ",
            arguments={},
        )


def test_tool_execution_service_should_execute_requirement_analysis_tool() -> None:
    service = ToolExecutionService()

    response = service.execute(
        tool_name="requirements.analyze",
        arguments={
            "requirement_text": (
                "Como cliente, quero renegociar minha dívida para gerar "
                "um boleto atualizado."
            ),
            "language": "pt-BR",
        },
        metadata={
            "requested_by": "agent",
        },
    )

    assert response.status == "completed"
    assert response.tool_name == "requirements.analyze"
    assert response.execution_id.startswith(
        "tool-execution-requirements-analyze-"
    )
    assert response.output["summary"]
    assert "business_rules" in response.output
    assert "acceptance_criteria" in response.output
    assert "risks" in response.output
    assert "positive_test_scenarios" in response.output
    assert response.metadata["requested_by"] == "agent"
    assert response.metadata["tool_category"] == "qa"
    assert response.metadata["requires_llm"] is True
