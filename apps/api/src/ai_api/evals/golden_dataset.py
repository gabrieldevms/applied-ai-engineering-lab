from ai_api.evals.schemas import (
    EvaluationExpectation,
    EvaluationScenario,
    GoldenEvaluationDataset,
)


def build_default_golden_evaluation_dataset() -> GoldenEvaluationDataset:
    return GoldenEvaluationDataset(
        name="applied-ai-engineering-lab-golden-evaluation-dataset",
        version="0.1.0",
        description=(
            "Golden evaluation dataset for deterministic regression coverage "
            "across requirement analysis, RAG, agents, data analysis, multi-agent "
            "workflows and MCP tools."
        ),
        scenarios=[
            EvaluationScenario(
                id="REQ-001",
                name="Requirement analysis for financial balance validation",
                type="requirement_analysis",
                priority="smoke",
                description=(
                    "Validates whether a requirement analysis workflow can process "
                    "a financial balance requirement and produce structured QA output."
                ),
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "language": "pt-BR",
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "summary",
                        "business_rules",
                        "acceptance_criteria",
                        "positive_test_scenarios",
                        "negative_test_scenarios",
                        "edge_cases",
                    ],
                    notes=[
                        "The output should preserve QA-oriented structure.",
                        "The output should be understandable in Portuguese.",
                    ],
                ),
                tags=[
                    "requirements",
                    "qa",
                    "financial",
                    "smoke",
                ],
                metadata={
                    "source": "m7_golden_dataset_foundation",
                },
            ),
            EvaluationScenario(
                id="RAG-001",
                name="RAG answer for billing policy context",
                type="rag_answer",
                priority="regression",
                description=(
                    "Validates whether a RAG answer workflow can use provided "
                    "billing context and return a grounded response."
                ),
                input_payload={
                    "query": "Quando o boleto deve ser registrado?",
                    "language": "pt-BR",
                    "documents": [
                        {
                            "id": "billing-policy",
                            "text": (
                                "Boletos de cobrança devem ser registrados antes "
                                "do envio ao cliente. O registro deve ocorrer após "
                                "a validação dos dados obrigatórios."
                            ),
                            "metadata": {
                                "source": "billing-policy.md",
                            },
                        }
                    ],
                    "top_k": 3,
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "answer",
                        "citations",
                        "retrieved_chunks",
                    ],
                    notes=[
                        "The answer should be grounded in the provided document.",
                    ],
                ),
                tags=[
                    "rag",
                    "billing",
                    "retrieval",
                ],
                metadata={
                    "source": "m7_golden_dataset_foundation",
                },
            ),
            EvaluationScenario(
                id="QA-001",
                name="QA Agent for boleto requirement",
                type="qa_agent",
                priority="regression",
                description=(
                    "Validates whether the QA Agent can analyze a boleto-related "
                    "requirement and produce QA-oriented output."
                ),
                input_payload={
                    "requirement_text": (
                        "Como cliente, quero gerar um boleto atualizado após "
                        "renegociar minha dívida."
                    ),
                    "language": "pt-BR",
                    "max_steps": 6,
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "requirement_analysis",
                        "trace",
                        "metadata",
                    ],
                    notes=[
                        "The QA Agent should preserve traceability.",
                    ],
                ),
                tags=[
                    "qa-agent",
                    "boleto",
                    "requirements",
                ],
                metadata={
                    "source": "m7_golden_dataset_foundation",
                },
            ),
            EvaluationScenario(
                id="DATA-001",
                name="Data Analyst Agent for final account balance",
                type="data_analyst_agent",
                priority="smoke",
                description=(
                    "Validates whether the Data Analyst Agent can reason over "
                    "transaction data and produce controlled SQL evidence."
                ),
                input_payload={
                    "objective": (
                        "Validar o saldo final por conta considerando depósitos "
                        "e retiradas."
                    ),
                    "language": "pt-BR",
                    "database_schema": {
                        "name": "qa_database",
                        "description": "Database used for QA validation.",
                        "tables": [
                            {
                                "name": "transactions",
                                "description": "Financial transactions.",
                                "columns": [
                                    {
                                        "name": "transaction_id",
                                        "data_type": "integer",
                                        "nullable": False,
                                        "primary_key": True,
                                    },
                                    {
                                        "name": "account_id",
                                        "data_type": "integer",
                                        "nullable": False,
                                    },
                                    {
                                        "name": "amount",
                                        "data_type": "decimal",
                                        "nullable": False,
                                    },
                                    {
                                        "name": "transaction_type",
                                        "data_type": "varchar",
                                        "nullable": False,
                                    },
                                ],
                            }
                        ],
                    },
                    "table_data": [
                        {
                            "table_name": "transactions",
                            "rows": [
                                {
                                    "transaction_id": 123,
                                    "account_id": 101,
                                    "amount": 10.0,
                                    "transaction_type": "Deposit",
                                },
                                {
                                    "transaction_id": 124,
                                    "account_id": 101,
                                    "amount": 20.0,
                                    "transaction_type": "Deposit",
                                },
                                {
                                    "transaction_id": 125,
                                    "account_id": 101,
                                    "amount": 5.0,
                                    "transaction_type": "Withdrawal",
                                },
                                {
                                    "transaction_id": 126,
                                    "account_id": 201,
                                    "amount": 20.0,
                                    "transaction_type": "Deposit",
                                },
                                {
                                    "transaction_id": 128,
                                    "account_id": 201,
                                    "amount": 10.0,
                                    "transaction_type": "Withdrawal",
                                },
                            ],
                        }
                    ],
                    "max_rows": 100,
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "workflow",
                        "evidence",
                        "trace",
                    ],
                    notes=[
                        "Expected business result: account 101 should have final balance 25.",
                        "Expected business result: account 201 should have final balance 10.",
                    ],
                ),
                tags=[
                    "data-analysis",
                    "sql",
                    "financial",
                    "smoke",
                ],
                metadata={
                    "source": "m7_golden_dataset_foundation",
                },
            ),
            EvaluationScenario(
                id="MULTI-001",
                name="Multi-Agent QA Copilot clean execution",
                type="multi_agent_qa_copilot",
                priority="smoke",
                description=(
                    "Validates whether the Multi-Agent QA Copilot can complete "
                    "a full QA workflow with all default agents."
                ),
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "objective": (
                        "Gerar uma análise multiagente de qualidade para o requisito."
                    ),
                    "language": "pt-BR",
                    "context": {
                        "domain": "financial",
                        "system": "billing",
                    },
                    "max_agents": 6,
                    "failure_strategy": "stop_on_failure",
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                    expected_quality_gate="approved",
                    required_output_markers=[
                        "roles",
                        "shared_state",
                        "task_results",
                        "final_report",
                        "trace",
                        "contract_validation",
                        "conflict_analysis",
                    ],
                    required_metadata_keys=[
                        "contract_validation_status",
                        "conflict_analysis_status",
                    ],
                    notes=[
                        "All default roles should be present.",
                        "Communication contracts should pass.",
                    ],
                ),
                tags=[
                    "multi-agent",
                    "qa-copilot",
                    "smoke",
                ],
                metadata={
                    "source": "m7_golden_dataset_foundation",
                },
            ),
            EvaluationScenario(
                id="MCP-001",
                name="MCP project status discovery",
                type="mcp_tool",
                priority="smoke",
                description=(
                    "Validates whether the MCP server can expose project status "
                    "and available tools."
                ),
                input_payload={
                    "tool_name": "get_project_status",
                    "arguments": {},
                },
                expectations=EvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "project",
                        "status",
                        "current_milestone",
                        "available_mcp_tools",
                    ],
                    notes=[
                        "The MCP status should reflect the current project milestone.",
                    ],
                ),
                tags=[
                    "mcp",
                    "discovery",
                    "smoke",
                ],
                metadata={
                    "source": "m7_golden_dataset_foundation",
                },
            ),
        ],
        metadata={
            "source": "m7_golden_dataset_foundation",
            "dataset_type": "golden_regression_dataset",
            "execution_mode": "definition_only",
        },
    )
