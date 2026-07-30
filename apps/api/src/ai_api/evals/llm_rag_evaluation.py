import json
from typing import Any
from ai_api.evals.schemas import (
    LLMOutputEvaluationCase,
    LLMOutputEvaluationCaseResult,
    LLMOutputEvaluationCheck,
    LLMOutputEvaluationExpectation,
    LLMOutputEvaluationRunRequest,
    LLMOutputEvaluationRunResponse,
    LLMOutputEvaluationSuite,
    RAGRegressionCase,
    RAGRegressionCaseResult,
    RAGRegressionCheck,
    RAGRegressionExpectation,
    RAGRegressionRunRequest,
    RAGRegressionRunResponse,
    RAGRegressionSuite,
)


def build_default_llm_output_evaluation_suite() -> LLMOutputEvaluationSuite:
    return LLMOutputEvaluationSuite(
        name="applied-ai-engineering-lab-llm-output-evaluation-suite",
        version="0.1.0",
        description=(
            "LLM output evaluation suite for deterministic validation of "
            "structured outputs produced by LLM, RAG and agent workflows."
        ),
        cases=[
            LLMOutputEvaluationCase(
                id="LLM-REQ-001",
                name="Requirement analysis structured JSON output",
                component_name="requirement_analyzer",
                output_format="json",
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "language": "pt-BR",
                },
                actual_output={
                    "status": "completed",
                    "summary": (
                        "Validar saldo final por conta considerando depósitos "
                        "e retiradas."
                    ),
                    "business_rules": [
                        "Depósitos devem aumentar o saldo.",
                        "Retiradas devem reduzir o saldo.",
                    ],
                    "acceptance_criteria": [
                        "O saldo final deve refletir todas as transações.",
                    ],
                    "risks": [
                        {
                            "title": "Erro no cálculo do saldo.",
                            "severity": "high",
                        }
                    ],
                    "positive_test_scenarios": [
                        "Conta com depósitos e retiradas válidos.",
                    ],
                    "negative_test_scenarios": [
                        "Transação com tipo inválido.",
                    ],
                    "edge_cases": [
                        "Conta sem transações.",
                    ],
                },
                expectations=LLMOutputEvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "summary",
                        "business_rules",
                        "acceptance_criteria",
                        "risks",
                        "positive_test_scenarios",
                        "negative_test_scenarios",
                        "edge_cases",
                    ],
                    forbidden_output_markers=[
                        "As an AI language model",
                        "I cannot",
                    ],
                    required_json_keys=[
                        "status",
                        "summary",
                        "business_rules",
                        "acceptance_criteria",
                    ],
                    min_output_length=80,
                ),
                tags=[
                    "llm",
                    "requirements",
                    "structured-output",
                    "qa",
                ],
                metadata={
                    "source": "m7_llm_output_evaluation_suite",
                },
            ),
            LLMOutputEvaluationCase(
                id="LLM-AGENT-001",
                name="Agent planning structured output",
                component_name="agent_planner",
                output_format="json",
                input_payload={
                    "objective": (
                        "Planejar uma análise QA com RAG, análise de requisito "
                        "e validação de dados."
                    ),
                    "language": "pt-BR",
                },
                actual_output={
                    "status": "completed",
                    "selected_tools": [
                        "requirements.analyze",
                        "rag.retrieve",
                        "data_analysis.agent.run",
                    ],
                    "plan": [
                        "Analisar requisito.",
                        "Buscar contexto relevante.",
                        "Validar evidência de dados.",
                    ],
                    "metadata": {
                        "planning_strategy": "deterministic_tool_selection",
                    },
                },
                expectations=LLMOutputEvaluationExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "selected_tools",
                        "plan",
                        "requirements.analyze",
                        "rag.retrieve",
                    ],
                    forbidden_output_markers=[
                        "unknown tool",
                        "placeholder",
                    ],
                    required_json_keys=[
                        "status",
                        "selected_tools",
                        "plan",
                    ],
                    min_output_length=60,
                ),
                tags=[
                    "llm",
                    "agent",
                    "planning",
                ],
                metadata={
                    "source": "m7_llm_output_evaluation_suite",
                },
            ),
            LLMOutputEvaluationCase(
                id="LLM-REPORT-001",
                name="AI quality report structured output",
                component_name="ai_evaluation_report",
                output_format="json",
                input_payload={
                    "evaluation_sources": [
                        "golden_dataset",
                        "prompt_regression",
                        "multi_agent_qa_copilot",
                    ],
                },
                actual_output={
                    "status": "passed",
                    "score": 1.0,
                    "summary": "AI evaluation report passed.",
                    "sections": [
                        {
                            "name": "prompt_regression",
                            "status": "passed",
                            "score": 1.0,
                        }
                    ],
                    "recommendations": [
                        "Keep evaluation datasets stable and versioned.",
                    ],
                },
                expectations=LLMOutputEvaluationExpectation(
                    expected_status="passed",
                    required_output_markers=[
                        "summary",
                        "sections",
                        "recommendations",
                        "score",
                    ],
                    forbidden_output_markers=[
                        "TODO",
                        "placeholder",
                    ],
                    required_json_keys=[
                        "status",
                        "score",
                        "summary",
                        "sections",
                    ],
                    min_output_length=70,
                ),
                tags=[
                    "llm",
                    "evaluation",
                    "reporting",
                ],
                metadata={
                    "source": "m7_llm_output_evaluation_suite",
                },
            ),
        ],
        metadata={
            "source": "m7_llm_output_evaluation_suite",
            "suite_type": "llm_output_evaluation",
            "execution_mode": "deterministic_output_validation",
        },
    )


def build_default_rag_regression_suite() -> RAGRegressionSuite:
    return RAGRegressionSuite(
        name="applied-ai-engineering-lab-rag-regression-suite",
        version="0.1.0",
        description=(
            "RAG regression suite for deterministic validation of grounded "
            "answers, citations and retrieved context."
        ),
        cases=[
            RAGRegressionCase(
                id="RAG-REG-001",
                name="Billing policy grounded answer",
                query="Quando o boleto deve ser registrado?",
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
                actual_output={
                    "status": "completed",
                    "answer": (
                        "O boleto deve ser registrado antes do envio ao cliente, "
                        "após a validação dos dados obrigatórios."
                    ),
                    "citations": [
                        {
                            "source": "billing-policy.md",
                        }
                    ],
                    "retrieved_chunks": [
                        {
                            "document_id": "billing-policy",
                            "content": (
                                "Boletos de cobrança devem ser registrados antes "
                                "do envio ao cliente."
                            ),
                            "metadata": {
                                "source": "billing-policy.md",
                            },
                        }
                    ],
                    "metadata": {
                        "retrieval_strategy": "semantic_search",
                    },
                },
                expectations=RAGRegressionExpectation(
                    expected_status="completed",
                    required_answer_markers=[
                        "antes do envio ao cliente",
                        "dados obrigatórios",
                    ],
                    forbidden_answer_markers=[
                        "não sei",
                        "sem contexto",
                    ],
                    required_citation_sources=[
                        "billing-policy.md",
                    ],
                    required_metadata_keys=[
                        "retrieval_strategy",
                    ],
                    min_retrieved_chunks=1,
                    require_citations=True,
                ),
                tags=[
                    "rag",
                    "billing",
                    "grounding",
                    "citations",
                ],
                metadata={
                    "source": "m7_rag_regression_suite",
                },
            ),
            RAGRegressionCase(
                id="RAG-REG-002",
                name="Data validation policy grounded answer",
                query="Como validar evidências de dados em QA?",
                input_payload={
                    "query": "Como validar evidências de dados em QA?",
                    "language": "pt-BR",
                    "documents": [
                        {
                            "id": "data-validation-policy",
                            "text": (
                                "Evidências de dados devem ser validadas com "
                                "consultas somente leitura, dados controlados e "
                                "resultados rastreáveis."
                            ),
                            "metadata": {
                                "source": "data-validation-policy.md",
                            },
                        }
                    ],
                    "top_k": 3,
                },
                actual_output={
                    "status": "completed",
                    "answer": (
                        "A validação deve usar consultas somente leitura, dados "
                        "controlados e resultados rastreáveis."
                    ),
                    "citations": [
                        {
                            "source": "data-validation-policy.md",
                        }
                    ],
                    "retrieved_chunks": [
                        {
                            "document_id": "data-validation-policy",
                            "content": (
                                "Evidências de dados devem ser validadas com "
                                "consultas somente leitura."
                            ),
                            "metadata": {
                                "source": "data-validation-policy.md",
                            },
                        }
                    ],
                    "metadata": {
                        "retrieval_strategy": "semantic_search",
                    },
                },
                expectations=RAGRegressionExpectation(
                    expected_status="completed",
                    required_answer_markers=[
                        "consultas somente leitura",
                        "resultados rastreáveis",
                    ],
                    forbidden_answer_markers=[
                        "alterar dados",
                        "DELETE",
                        "UPDATE",
                    ],
                    required_citation_sources=[
                        "data-validation-policy.md",
                    ],
                    required_metadata_keys=[
                        "retrieval_strategy",
                    ],
                    min_retrieved_chunks=1,
                    require_citations=True,
                ),
                tags=[
                    "rag",
                    "data-validation",
                    "qa",
                    "grounding",
                ],
                metadata={
                    "source": "m7_rag_regression_suite",
                },
            ),
        ],
        metadata={
            "source": "m7_rag_regression_suite",
            "suite_type": "rag_regression",
            "execution_mode": "deterministic_output_validation",
        },
    )


class LLMOutputEvaluationSuiteService:
    def get_default_suite(self) -> LLMOutputEvaluationSuite:
        return build_default_llm_output_evaluation_suite()


class LLMOutputEvaluationService:
    def run(
        self,
        request: LLMOutputEvaluationRunRequest,
    ) -> LLMOutputEvaluationRunResponse:
        suite = request.suite or build_default_llm_output_evaluation_suite()
        selected_cases = self._select_cases(
            cases=suite.cases,
            case_ids=request.case_ids,
        )

        results = [
            self._run_case(evaluation_case)
            for evaluation_case in selected_cases
        ]

        passed_count = self._count_results(results, "passed")
        warning_count = self._count_results(results, "warning")
        failed_count = self._count_results(results, "failed")

        if failed_count > 0:
            status = "failed"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "passed"

        return LLMOutputEvaluationRunResponse(
            status=status,
            suite_name=suite.name,
            suite_version=suite.version,
            case_count=len(selected_cases),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            results=results,
            metadata={
                "runner": "llm-output-evaluator-v1",
                "selected_case_ids": [
                    evaluation_case.id
                    for evaluation_case in selected_cases
                ],
                **request.metadata,
            },
        )

    def _run_case(
        self,
        evaluation_case: LLMOutputEvaluationCase,
    ) -> LLMOutputEvaluationCaseResult:
        checks = [
            self._check_output_presence(evaluation_case),
            self._check_expected_status(evaluation_case),
            self._check_required_output_markers(evaluation_case),
            self._check_forbidden_output_markers(evaluation_case),
            self._check_required_json_keys(evaluation_case),
            self._check_min_output_length(evaluation_case),
        ]

        status = self._resolve_status(checks)

        return LLMOutputEvaluationCaseResult(
            case_id=evaluation_case.id,
            case_name=evaluation_case.name,
            component_name=evaluation_case.component_name,
            status=status,
            checks=checks,
            metadata={
                "output_format": evaluation_case.output_format,
                "tags": evaluation_case.tags,
            },
        )

    @staticmethod
    def _check_output_presence(
        evaluation_case: LLMOutputEvaluationCase,
    ) -> LLMOutputEvaluationCheck:
        output_text = LLMOutputEvaluationService._serialize_output(
            evaluation_case.actual_output
        )

        if output_text.strip():
            return LLMOutputEvaluationCheck(
                name="output_presence",
                status="passed",
                summary="LLM output is present.",
                metadata={
                    "output_length": len(output_text),
                },
            )

        return LLMOutputEvaluationCheck(
            name="output_presence",
            status="failed",
            summary="LLM output is empty.",
            metadata={
                "output_length": 0,
            },
        )

    @staticmethod
    def _check_expected_status(
        evaluation_case: LLMOutputEvaluationCase,
    ) -> LLMOutputEvaluationCheck:
        expected_status = evaluation_case.expectations.expected_status

        if expected_status is None:
            return LLMOutputEvaluationCheck(
                name="expected_status",
                status="passed",
                summary="No expected status was configured.",
            )

        actual_status = (
            evaluation_case.actual_output.get("status")
            if isinstance(evaluation_case.actual_output, dict)
            else None
        )

        if actual_status == expected_status:
            return LLMOutputEvaluationCheck(
                name="expected_status",
                status="passed",
                summary="Output status matched the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                },
            )

        return LLMOutputEvaluationCheck(
            name="expected_status",
            status="failed",
            summary="Output status did not match the expected status.",
            metadata={
                "expected_status": expected_status,
                "actual_status": actual_status,
            },
        )

    @staticmethod
    def _check_required_output_markers(
        evaluation_case: LLMOutputEvaluationCase,
    ) -> LLMOutputEvaluationCheck:
        required_markers = evaluation_case.expectations.required_output_markers
        output_text = LLMOutputEvaluationService._serialize_output(
            evaluation_case.actual_output
        )

        missing_markers = [
            marker
            for marker in required_markers
            if marker not in output_text
        ]

        if not missing_markers:
            return LLMOutputEvaluationCheck(
                name="required_output_markers",
                status="passed",
                summary="All required output markers were found.",
                metadata={
                    "required_output_markers": required_markers,
                    "missing_markers": [],
                },
            )

        return LLMOutputEvaluationCheck(
            name="required_output_markers",
            status="failed",
            summary="One or more required output markers were missing.",
            metadata={
                "required_output_markers": required_markers,
                "missing_markers": missing_markers,
            },
        )

    @staticmethod
    def _check_forbidden_output_markers(
        evaluation_case: LLMOutputEvaluationCase,
    ) -> LLMOutputEvaluationCheck:
        forbidden_markers = evaluation_case.expectations.forbidden_output_markers
        output_text = LLMOutputEvaluationService._serialize_output(
            evaluation_case.actual_output
        )

        detected_markers = [
            marker
            for marker in forbidden_markers
            if marker in output_text
        ]

        if not detected_markers:
            return LLMOutputEvaluationCheck(
                name="forbidden_output_markers",
                status="passed",
                summary="No forbidden output markers were detected.",
                metadata={
                    "forbidden_output_markers": forbidden_markers,
                    "detected_markers": [],
                },
            )

        return LLMOutputEvaluationCheck(
            name="forbidden_output_markers",
            status="failed",
            summary="One or more forbidden output markers were detected.",
            metadata={
                "forbidden_output_markers": forbidden_markers,
                "detected_markers": detected_markers,
            },
        )

    @staticmethod
    def _check_required_json_keys(
        evaluation_case: LLMOutputEvaluationCase,
    ) -> LLMOutputEvaluationCheck:
        required_json_keys = evaluation_case.expectations.required_json_keys

        if not required_json_keys:
            return LLMOutputEvaluationCheck(
                name="required_json_keys",
                status="passed",
                summary="No required JSON keys were configured.",
            )

        if not isinstance(evaluation_case.actual_output, dict):
            return LLMOutputEvaluationCheck(
                name="required_json_keys",
                status="failed",
                summary="Required JSON keys were configured, but output is not JSON.",
                metadata={
                    "required_json_keys": required_json_keys,
                    "output_type": type(evaluation_case.actual_output).__name__,
                },
            )

        missing_keys = [
            key
            for key in required_json_keys
            if key not in evaluation_case.actual_output
        ]

        if not missing_keys:
            return LLMOutputEvaluationCheck(
                name="required_json_keys",
                status="passed",
                summary="All required JSON keys were found.",
                metadata={
                    "required_json_keys": required_json_keys,
                    "missing_keys": [],
                },
            )

        return LLMOutputEvaluationCheck(
            name="required_json_keys",
            status="failed",
            summary="One or more required JSON keys were missing.",
            metadata={
                "required_json_keys": required_json_keys,
                "missing_keys": missing_keys,
            },
        )

    @staticmethod
    def _check_min_output_length(
        evaluation_case: LLMOutputEvaluationCase,
    ) -> LLMOutputEvaluationCheck:
        min_output_length = evaluation_case.expectations.min_output_length
        output_text = LLMOutputEvaluationService._serialize_output(
            evaluation_case.actual_output
        )

        if len(output_text) >= min_output_length:
            return LLMOutputEvaluationCheck(
                name="min_output_length",
                status="passed",
                summary="Output length is greater than or equal to the configured minimum.",
                metadata={
                    "min_output_length": min_output_length,
                    "actual_output_length": len(output_text),
                },
            )

        return LLMOutputEvaluationCheck(
            name="min_output_length",
            status="failed",
            summary="Output length is below the configured minimum.",
            metadata={
                "min_output_length": min_output_length,
                "actual_output_length": len(output_text),
            },
        )

    @staticmethod
    def _serialize_output(output: str | dict[str, Any]) -> str:
        if isinstance(output, str):
            return output

        return json.dumps(output, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def _select_cases(
        cases: list[LLMOutputEvaluationCase],
        case_ids: list[str],
    ) -> list[LLMOutputEvaluationCase]:
        if not case_ids:
            return cases

        case_id_set = set(case_ids)

        return [
            evaluation_case
            for evaluation_case in cases
            if evaluation_case.id in case_id_set
        ]

    @staticmethod
    def _resolve_status(
        checks: list[LLMOutputEvaluationCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _count_results(
        results: list[LLMOutputEvaluationCaseResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )


class RAGRegressionSuiteService:
    def get_default_suite(self) -> RAGRegressionSuite:
        return build_default_rag_regression_suite()


class RAGRegressionEvaluationService:
    def run(
        self,
        request: RAGRegressionRunRequest,
    ) -> RAGRegressionRunResponse:
        suite = request.suite or build_default_rag_regression_suite()
        selected_cases = self._select_cases(
            cases=suite.cases,
            case_ids=request.case_ids,
        )

        results = [
            self._run_case(regression_case)
            for regression_case in selected_cases
        ]

        passed_count = self._count_results(results, "passed")
        warning_count = self._count_results(results, "warning")
        failed_count = self._count_results(results, "failed")

        if failed_count > 0:
            status = "failed"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "passed"

        return RAGRegressionRunResponse(
            status=status,
            suite_name=suite.name,
            suite_version=suite.version,
            case_count=len(selected_cases),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            results=results,
            metadata={
                "runner": "rag-regression-evaluator-v1",
                "selected_case_ids": [
                    regression_case.id
                    for regression_case in selected_cases
                ],
                **request.metadata,
            },
        )

    def _run_case(
        self,
        regression_case: RAGRegressionCase,
    ) -> RAGRegressionCaseResult:
        checks = [
            self._check_expected_status(regression_case),
            self._check_answer_markers(regression_case),
            self._check_forbidden_answer_markers(regression_case),
            self._check_citations(regression_case),
            self._check_retrieved_chunks(regression_case),
            self._check_required_metadata_keys(regression_case),
        ]

        status = self._resolve_status(checks)

        return RAGRegressionCaseResult(
            case_id=regression_case.id,
            case_name=regression_case.name,
            query=regression_case.query,
            status=status,
            checks=checks,
            metadata={
                "tags": regression_case.tags,
            },
        )

    @staticmethod
    def _check_expected_status(
        regression_case: RAGRegressionCase,
    ) -> RAGRegressionCheck:
        expected_status = regression_case.expectations.expected_status

        if expected_status is None:
            return RAGRegressionCheck(
                name="expected_status",
                status="passed",
                summary="No expected status was configured.",
            )

        actual_status = regression_case.actual_output.get("status")

        if actual_status == expected_status:
            return RAGRegressionCheck(
                name="expected_status",
                status="passed",
                summary="Output status matched the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                },
            )

        return RAGRegressionCheck(
            name="expected_status",
            status="failed",
            summary="Output status did not match the expected status.",
            metadata={
                "expected_status": expected_status,
                "actual_status": actual_status,
            },
        )

    @staticmethod
    def _check_answer_markers(
        regression_case: RAGRegressionCase,
    ) -> RAGRegressionCheck:
        answer = regression_case.actual_output.get("answer", "")
        required_markers = regression_case.expectations.required_answer_markers

        missing_markers = [
            marker
            for marker in required_markers
            if marker not in answer
        ]

        if not missing_markers:
            return RAGRegressionCheck(
                name="required_answer_markers",
                status="passed",
                summary="All required answer markers were found.",
                metadata={
                    "required_answer_markers": required_markers,
                    "missing_markers": [],
                },
            )

        return RAGRegressionCheck(
            name="required_answer_markers",
            status="failed",
            summary="One or more required answer markers were missing.",
            metadata={
                "required_answer_markers": required_markers,
                "missing_markers": missing_markers,
            },
        )

    @staticmethod
    def _check_forbidden_answer_markers(
        regression_case: RAGRegressionCase,
    ) -> RAGRegressionCheck:
        answer = regression_case.actual_output.get("answer", "")
        forbidden_markers = regression_case.expectations.forbidden_answer_markers

        detected_markers = [
            marker
            for marker in forbidden_markers
            if marker in answer
        ]

        if not detected_markers:
            return RAGRegressionCheck(
                name="forbidden_answer_markers",
                status="passed",
                summary="No forbidden answer markers were detected.",
                metadata={
                    "forbidden_answer_markers": forbidden_markers,
                    "detected_markers": [],
                },
            )

        return RAGRegressionCheck(
            name="forbidden_answer_markers",
            status="failed",
            summary="One or more forbidden answer markers were detected.",
            metadata={
                "forbidden_answer_markers": forbidden_markers,
                "detected_markers": detected_markers,
            },
        )

    @staticmethod
    def _check_citations(
        regression_case: RAGRegressionCase,
    ) -> RAGRegressionCheck:
        citations = regression_case.actual_output.get("citations", [])
        required_sources = regression_case.expectations.required_citation_sources

        if regression_case.expectations.require_citations and not citations:
            return RAGRegressionCheck(
                name="citations",
                status="failed",
                summary="Citations are required but none were provided.",
                metadata={
                    "citation_count": 0,
                    "required_citation_sources": required_sources,
                },
            )

        citation_sources = [
            citation.get("source")
            for citation in citations
            if isinstance(citation, dict)
        ]

        missing_sources = [
            source
            for source in required_sources
            if source not in citation_sources
        ]

        if not missing_sources:
            return RAGRegressionCheck(
                name="citations",
                status="passed",
                summary="Required citation sources were found.",
                metadata={
                    "citation_count": len(citations),
                    "required_citation_sources": required_sources,
                    "missing_sources": [],
                },
            )

        return RAGRegressionCheck(
            name="citations",
            status="failed",
            summary="One or more required citation sources were missing.",
            metadata={
                "citation_count": len(citations),
                "required_citation_sources": required_sources,
                "missing_sources": missing_sources,
            },
        )

    @staticmethod
    def _check_retrieved_chunks(
        regression_case: RAGRegressionCase,
    ) -> RAGRegressionCheck:
        retrieved_chunks = regression_case.actual_output.get("retrieved_chunks", [])
        min_retrieved_chunks = regression_case.expectations.min_retrieved_chunks

        if len(retrieved_chunks) >= min_retrieved_chunks:
            return RAGRegressionCheck(
                name="retrieved_chunks",
                status="passed",
                summary="Retrieved chunk count meets the configured minimum.",
                metadata={
                    "min_retrieved_chunks": min_retrieved_chunks,
                    "actual_retrieved_chunks": len(retrieved_chunks),
                },
            )

        return RAGRegressionCheck(
            name="retrieved_chunks",
            status="failed",
            summary="Retrieved chunk count is below the configured minimum.",
            metadata={
                "min_retrieved_chunks": min_retrieved_chunks,
                "actual_retrieved_chunks": len(retrieved_chunks),
            },
        )

    @staticmethod
    def _check_required_metadata_keys(
        regression_case: RAGRegressionCase,
    ) -> RAGRegressionCheck:
        required_metadata_keys = regression_case.expectations.required_metadata_keys

        if not required_metadata_keys:
            return RAGRegressionCheck(
                name="required_metadata_keys",
                status="passed",
                summary="No required metadata keys were configured.",
            )

        metadata = regression_case.actual_output.get("metadata", {})

        missing_keys = [
            key
            for key in required_metadata_keys
            if key not in metadata
        ]

        if not missing_keys:
            return RAGRegressionCheck(
                name="required_metadata_keys",
                status="passed",
                summary="All required metadata keys were found.",
                metadata={
                    "required_metadata_keys": required_metadata_keys,
                    "missing_keys": [],
                },
            )

        return RAGRegressionCheck(
            name="required_metadata_keys",
            status="failed",
            summary="One or more required metadata keys were missing.",
            metadata={
                "required_metadata_keys": required_metadata_keys,
                "missing_keys": missing_keys,
            },
        )

    @staticmethod
    def _select_cases(
        cases: list[RAGRegressionCase],
        case_ids: list[str],
    ) -> list[RAGRegressionCase]:
        if not case_ids:
            return cases

        case_id_set = set(case_ids)

        return [
            regression_case
            for regression_case in cases
            if regression_case.id in case_id_set
        ]

    @staticmethod
    def _resolve_status(
        checks: list[RAGRegressionCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _count_results(
        results: list[RAGRegressionCaseResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )
