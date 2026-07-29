from fastapi.testclient import TestClient
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
from ai_api.main import app


client = TestClient(app)


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
            ],
        )
    ]


def _build_data_validation_request() -> QAAgentDataValidationRequest:
    return QAAgentDataValidationRequest(
        objective="Validar o saldo final por conta.",
        mode="auto",
        database_schema=_build_database_schema(),
        table_data=_build_table_data(),
        max_rows=100,
    )


def _build_qa_agent_service() -> QAAgentService:
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


def _run_qa_agent_with_data_validation():
    service = _build_qa_agent_service()

    return service.run(
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        data_validation=_build_data_validation_request(),
        language="pt-BR",
        max_steps=6,
    )


def test_qa_agent_evaluation_endpoint_should_pass_with_data_evidence() -> None:
    agent_response = _run_qa_agent_with_data_validation()

    response = client.post(
        "/agents/qa/evaluate",
        json={
            "agent_response": agent_response.model_dump(mode="json"),
            "expected_status": "completed",
            "expect_data_validation": True,
            "expected_data_row_count": 1,
            "expected_data_columns": [
                "account_id",
                "final_balance",
            ],
            "metadata": {
                "test_case": "api_evaluation",
            },
        },
    )

    assert response.status_code == 200

    body = response.json()

    metric_names = [
        metric["name"]
        for metric in body["metrics"]
    ]

    assert body["status"] == "passed"
    assert body["score"] == 1.0
    assert "status_alignment" in metric_names
    assert "requirement_analysis" in metric_names
    assert "data_validation_selection" in metric_names
    assert "data_validation_evidence" in metric_names
    assert "result_shape" in metric_names
    assert "tool_trace" in metric_names
    assert body["metadata"]["test_case"] == "api_evaluation"


def test_qa_agent_evaluation_endpoint_should_fail_when_expected_shape_is_wrong() -> None:
    agent_response = _run_qa_agent_with_data_validation()

    response = client.post(
        "/agents/qa/evaluate",
        json={
            "agent_response": agent_response.model_dump(mode="json"),
            "expected_status": "completed",
            "expect_data_validation": True,
            "expected_data_row_count": 99,
            "expected_data_columns": [
                "account_id",
                "final_balance",
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    result_shape_metric = next(
        metric
        for metric in body["metrics"]
        if metric["name"] == "result_shape"
    )

    assert body["status"] == "failed"
    assert result_shape_metric["status"] == "failed"
    assert result_shape_metric["metadata"]["actual_row_count"] == 1
    assert result_shape_metric["metadata"]["expected_row_count"] == 99
