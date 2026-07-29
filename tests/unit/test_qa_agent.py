import pytest
from ai_api.agents import (
    DataAnalystAgentTool,
    QAAgentDataValidationRequest,
    QAAgentService,
    ToolExecutionService,
)
from ai_api.agents.runtime import AgentRuntime
from ai_api.data_analysis import (
    DataAnalystAgentService,
    DataAnalystSQLGenerationService,
    DataAnalystSQLWorkflowService,
    DatabaseColumn,
    DatabaseSchema,
    DatabaseTable,
    DatabaseTableData,
    SQLiteReadOnlyQueryExecutor,
)
from ai_api.llm import FakeLLMProvider
from ai_api.rag import SemanticSearchDocument


VALID_SQL_RESPONSE_JSON = """
{
  "sql": "SELECT account_id, SUM(CASE WHEN transaction_type = 'Deposit' THEN amount WHEN transaction_type = 'Withdrawal' THEN -amount ELSE 0 END) AS final_balance FROM transactions GROUP BY account_id ORDER BY account_id",
  "explanation": "Calcula o saldo final por conta somando depósitos e subtraindo retiradas.",
  "assumptions": [
    "A tabela transactions contém uma linha por transação financeira.",
    "Transações do tipo Deposit aumentam o saldo.",
    "Transações do tipo Withdrawal reduzem o saldo."
  ]
}
"""


def _build_database_schema() -> DatabaseSchema:
    return DatabaseSchema(
        name="qa_database",
        description="Database used for QA validation.",
        tables=[
            DatabaseTable(
                name="transactions",
                description="Financial transactions.",
                columns=[
                    DatabaseColumn(
                        name="transaction_id",
                        data_type="integer",
                        primary_key=True,
                        nullable=False,
                    ),
                    DatabaseColumn(
                        name="account_id",
                        data_type="integer",
                        nullable=False,
                    ),
                    DatabaseColumn(
                        name="amount",
                        data_type="decimal",
                        nullable=False,
                    ),
                    DatabaseColumn(
                        name="transaction_type",
                        data_type="varchar",
                        nullable=False,
                    ),
                ],
            )
        ],
    )


def _build_table_data() -> list[DatabaseTableData]:
    return [
        DatabaseTableData(
            table_name="transactions",
            rows=[
                {
                    "transaction_id": 123,
                    "account_id": 101,
                    "amount": 10.00,
                    "transaction_type": "Deposit",
                },
                {
                    "transaction_id": 124,
                    "account_id": 101,
                    "amount": 20.00,
                    "transaction_type": "Deposit",
                },
                {
                    "transaction_id": 125,
                    "account_id": 101,
                    "amount": 5.00,
                    "transaction_type": "Withdrawal",
                },
                {
                    "transaction_id": 126,
                    "account_id": 201,
                    "amount": 20.00,
                    "transaction_type": "Deposit",
                },
                {
                    "transaction_id": 128,
                    "account_id": 201,
                    "amount": 10.00,
                    "transaction_type": "Withdrawal",
                },
            ],
        )
    ]


def _build_data_validation_request() -> QAAgentDataValidationRequest:
    return QAAgentDataValidationRequest(
        objective="Validar o saldo final por conta.",
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
        max_rows=100,
    )


def _build_qa_agent_service_with_data_analyst_fake() -> QAAgentService:
    generation_service = DataAnalystSQLGenerationService(
        llm_provider=FakeLLMProvider(
            response_content=VALID_SQL_RESPONSE_JSON,
        )
    )

    workflow_service = DataAnalystSQLWorkflowService(
        sql_generation_service=generation_service,
        query_executor=SQLiteReadOnlyQueryExecutor(),
    )

    data_analyst_service = DataAnalystAgentService(
        sql_workflow_service=workflow_service,
    )

    tool_execution_service = ToolExecutionService(
        handlers={
            DataAnalystAgentTool.tool_name: DataAnalystAgentTool(
                agent_service=data_analyst_service,
            )
        }
    )

    return QAAgentService(
        agent_runtime=AgentRuntime(
            tool_execution_service=tool_execution_service,
        )
    )


def test_qa_agent_should_analyze_requirement_without_knowledge_documents() -> None:
    service = QAAgentService()

    response = service.run(
        requirement_text=(
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        language="pt-BR",
        max_steps=4,
    )

    assert response.status == "completed"
    assert response.metadata["agent_type"] == "qa-agent-v1"
    assert response.metadata["knowledge_documents"] == 0
    assert response.metadata["data_validation_available"] is False
    assert response.metadata["data_validation_selected"] is False
    assert response.metadata["data_validation_mode"] == "not_provided"
    assert response.requirement_analysis["summary"]
    assert response.retrieved_context is None
    assert response.data_validation is None
    assert response.steps[2].name == "tool_call:requirements.analyze"


def test_qa_agent_should_retrieve_context_and_analyze_requirement() -> None:
    service = QAAgentService()

    response = service.run(
        requirement_text=(
            "Como cliente, quero renegociar minha dívida para gerar "
            "um boleto atualizado."
        ),
        knowledge_documents=[
            SemanticSearchDocument(
                source="billing-doc",
                title="Cobrança",
                document_text=(
                    "boleto cobrança renegociação dívida pagamento vencimento"
                ),
                metadata={
                    "domain": "billing",
                },
            ),
            SemanticSearchDocument(
                source="auth-doc",
                title="Autenticação",
                document_text="login senha autenticação usuário sessão",
                metadata={
                    "domain": "auth",
                },
            ),
        ],
        language="pt-BR",
        top_k=1,
        chunk_size=200,
        chunk_overlap=40,
        max_steps=5,
    )

    assert response.status == "completed"
    assert response.metadata["knowledge_documents"] == 2
    assert response.metadata["data_validation_available"] is False
    assert response.metadata["data_validation_selected"] is False
    assert response.metadata["data_validation_mode"] == "not_provided"
    assert response.retrieved_context is not None
    assert response.retrieved_context["total_retrieved_chunks"] == 1
    assert response.requirement_analysis["summary"]
    assert response.data_validation is None
    assert response.steps[2].name == "tool_call:rag.retrieve"
    assert response.steps[3].name == "tool_call:requirements.analyze"


def test_qa_agent_should_run_data_validation_when_requested() -> None:
    service = _build_qa_agent_service_with_data_analyst_fake()

    response = service.run(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        data_validation=_build_data_validation_request(),
        language="pt-BR",
        max_steps=6,
    )

    assert response.status == "completed"
    assert response.data_validation_selection is not None
    assert response.data_validation_selection["decision"] == "selected"
    assert response.metadata["data_validation_available"] is True
    assert response.metadata["data_validation_selected"] is True
    assert response.metadata["data_validation_mode"] == "auto"
    assert response.requirement_analysis["summary"]
    assert response.data_validation is not None
    assert response.data_validation["status"] == "completed"
    assert response.data_validation["workflow"]["status"] == "executed"
    assert response.data_validation["workflow"]["execution"]["rows"] == [
        {
            "account_id": 101,
            "final_balance": 25.0,
        },
        {
            "account_id": 201,
            "final_balance": 10.0,
        },
    ]

    step_names = [
        step.name
        for step in response.steps
    ]

    assert "tool_call:requirements.analyze" in step_names
    assert "tool_call:data_analysis.agent.run" in step_names
    assert response.data_validation_selection is not None
    assert response.data_validation_selection["decision"] == "selected"
    assert response.metadata["data_validation_available"] is True
    assert response.metadata["data_validation_selected"] is True
    assert response.metadata["data_validation_mode"] == "auto"


def test_qa_agent_should_reject_blank_requirement() -> None:
    service = QAAgentService()

    with pytest.raises(ValueError, match="requirement_text cannot be blank"):
        service.run(requirement_text="   ")


def test_qa_agent_should_skip_data_validation_when_auto_selection_does_not_match() -> None:
    service = _build_qa_agent_service_with_data_analyst_fake()

    response = service.run(
        requirement_text=(
            "Como usuário, quero alterar o tema visual da aplicação "
            "para modo escuro."
        ),
        data_validation=_build_data_validation_request(),
        language="pt-BR",
        max_steps=6,
    )

    assert response.status == "completed"
    assert response.data_validation_selection is not None
    assert response.data_validation_selection["decision"] == "skipped"
    assert response.data_validation is None
    assert response.metadata["data_validation_available"] is True
    assert response.metadata["data_validation_selected"] is False
    assert response.metadata["data_validation_mode"] == "auto"

    step_names = [
        step.name
        for step in response.steps
    ]

    assert "tool_call:requirements.analyze" in step_names
    assert "tool_call:data_analysis.agent.run" not in step_names


def test_qa_agent_should_run_data_validation_when_mode_is_required() -> None:
    service = _build_qa_agent_service_with_data_analyst_fake()
    data_validation = _build_data_validation_request()
    data_validation.mode = "required"

    response = service.run(
        requirement_text=(
            "Como usuário, quero alterar o tema visual da aplicação "
            "para modo escuro."
        ),
        data_validation=data_validation,
        language="pt-BR",
        max_steps=6,
    )

    assert response.status == "completed"
    assert response.data_validation_selection is not None
    assert response.data_validation_selection["decision"] == "selected"
    assert response.data_validation is not None
    assert response.metadata["data_validation_available"] is True
    assert response.metadata["data_validation_selected"] is True
    assert response.metadata["data_validation_mode"] == "required"

    step_names = [
        step.name
        for step in response.steps
    ]

    assert "tool_call:data_analysis.agent.run" in step_names
