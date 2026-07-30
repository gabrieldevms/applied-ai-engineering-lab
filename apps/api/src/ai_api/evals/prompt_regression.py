import json
from typing import Any
from ai_api.evals.schemas import (
    PromptRegressionCase,
    PromptRegressionCaseResult,
    PromptRegressionCheck,
    PromptRegressionExpectation,
    PromptRegressionRunRequest,
    PromptRegressionRunResponse,
    PromptRegressionSuite,
)


def build_default_prompt_regression_suite() -> PromptRegressionSuite:
    return PromptRegressionSuite(
        name="applied-ai-engineering-lab-prompt-regression-suite",
        version="0.1.0",
        description=(
            "Prompt regression suite for deterministic validation of expected "
            "LLM, RAG and agent output structures."
        ),
        cases=[
            PromptRegressionCase(
                id="PROMPT-REQ-001",
                name="Requirement analysis structured output",
                prompt_name="requirement_analysis_prompt",
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
                        "Validar o saldo final por conta considerando depósitos "
                        "e retiradas."
                    ),
                    "business_rules": [
                        "Depósitos devem aumentar o saldo.",
                        "Retiradas devem reduzir o saldo.",
                    ],
                    "acceptance_criteria": [
                        "O saldo final deve refletir todas as transações.",
                    ],
                    "positive_test_scenarios": [
                        "Conta com múltiplos depósitos e retiradas.",
                    ],
                    "negative_test_scenarios": [
                        "Transação com tipo inválido.",
                    ],
                    "edge_cases": [
                        "Conta sem transações.",
                    ],
                },
                expectations=PromptRegressionExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "summary",
                        "business_rules",
                        "acceptance_criteria",
                        "positive_test_scenarios",
                        "negative_test_scenarios",
                        "edge_cases",
                    ],
                    forbidden_output_markers=[
                        "I cannot",
                        "As an AI language model",
                    ],
                    required_json_keys=[
                        "status",
                        "summary",
                        "business_rules",
                        "acceptance_criteria",
                    ],
                    min_output_length=50,
                    notes=[
                        "The requirement analysis output must preserve structured QA fields.",
                    ],
                ),
                tags=[
                    "prompt",
                    "requirements",
                    "qa",
                    "structured-output",
                ],
                metadata={
                    "source": "m7_prompt_regression_foundation",
                },
            ),
            PromptRegressionCase(
                id="PROMPT-RAG-001",
                name="RAG grounded answer output",
                prompt_name="rag_answer_prompt",
                output_format="json",
                input_payload={
                    "query": "Quando o boleto deve ser registrado?",
                    "language": "pt-BR",
                    "context": (
                        "Boletos de cobrança devem ser registrados antes do "
                        "envio ao cliente."
                    ),
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
                            "content": (
                                "Boletos de cobrança devem ser registrados antes "
                                "do envio ao cliente."
                            ),
                        }
                    ],
                },
                expectations=PromptRegressionExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "answer",
                        "citations",
                        "retrieved_chunks",
                    ],
                    forbidden_output_markers=[
                        "não sei",
                        "sem contexto",
                    ],
                    required_json_keys=[
                        "status",
                        "answer",
                        "citations",
                    ],
                    min_output_length=50,
                    notes=[
                        "The RAG output should preserve grounding metadata.",
                    ],
                ),
                tags=[
                    "prompt",
                    "rag",
                    "grounding",
                ],
                metadata={
                    "source": "m7_prompt_regression_foundation",
                },
            ),
            PromptRegressionCase(
                id="PROMPT-MULTI-001",
                name="Multi-Agent QA final report output",
                prompt_name="multi_agent_final_report_prompt",
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
                    "final_report": {
                        "summary": (
                            "Relatório final QA gerado com sucesso para validação "
                            "de saldo final por conta."
                        ),
                        "requirement_understanding": [
                            "O saldo final deve considerar depósitos e retiradas.",
                        ],
                        "functional_coverage": [
                            "Validar cenário positivo com depósitos e retiradas.",
                        ],
                        "automation_strategy": [
                            "Automatizar validação em camada de API.",
                        ],
                        "review_notes": [
                            "Revisar cenários de borda financeiros.",
                        ],
                        "next_steps": [
                            "Adicionar dados representativos para regressão.",
                        ],
                        "metadata": {
                            "quality_gate": "approved",
                        },
                    },
                    "metadata": {
                        "contract_validation_status": "passed",
                        "conflict_analysis_status": "passed",
                    },
                },
                expectations=PromptRegressionExpectation(
                    expected_status="completed",
                    required_output_markers=[
                        "final_report",
                        "summary",
                        "requirement_understanding",
                        "functional_coverage",
                        "automation_strategy",
                        "review_notes",
                        "next_steps",
                        "quality_gate",
                    ],
                    forbidden_output_markers=[
                        "TODO",
                        "placeholder",
                    ],
                    required_json_keys=[
                        "status",
                        "final_report",
                        "metadata",
                    ],
                    min_output_length=80,
                    notes=[
                        "The final report output should preserve QA report structure.",
                    ],
                ),
                tags=[
                    "prompt",
                    "multi-agent",
                    "final-report",
                ],
                metadata={
                    "source": "m7_prompt_regression_foundation",
                },
            ),
        ],
        metadata={
            "source": "m7_prompt_regression_foundation",
            "suite_type": "prompt_regression",
            "execution_mode": "deterministic_output_validation",
        },
    )


class PromptRegressionSuiteService:
    def get_default_suite(self) -> PromptRegressionSuite:
        return build_default_prompt_regression_suite()


class PromptRegressionEvaluationService:
    def run(
        self,
        request: PromptRegressionRunRequest,
    ) -> PromptRegressionRunResponse:
        suite = request.suite or build_default_prompt_regression_suite()
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

        return PromptRegressionRunResponse(
            status=status,
            suite_name=suite.name,
            suite_version=suite.version,
            case_count=len(selected_cases),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            results=results,
            metadata={
                "runner": "prompt-regression-evaluator-v1",
                "selected_case_ids": [
                    regression_case.id
                    for regression_case in selected_cases
                ],
                **request.metadata,
            },
        )

    def _run_case(
        self,
        regression_case: PromptRegressionCase,
    ) -> PromptRegressionCaseResult:
        checks = [
            self._check_output_presence(regression_case),
            self._check_expected_status(regression_case),
            self._check_required_output_markers(regression_case),
            self._check_forbidden_output_markers(regression_case),
            self._check_required_json_keys(regression_case),
            self._check_min_output_length(regression_case),
        ]

        status = self._resolve_status(checks)

        return PromptRegressionCaseResult(
            case_id=regression_case.id,
            case_name=regression_case.name,
            prompt_name=regression_case.prompt_name,
            status=status,
            checks=checks,
            metadata={
                "output_format": regression_case.output_format,
                "tags": regression_case.tags,
            },
        )

    @staticmethod
    def _check_output_presence(
        regression_case: PromptRegressionCase,
    ) -> PromptRegressionCheck:
        output_text = PromptRegressionEvaluationService._serialize_output(
            regression_case.actual_output
        )

        if output_text.strip():
            return PromptRegressionCheck(
                name="output_presence",
                status="passed",
                summary="Prompt output is present.",
                metadata={
                    "output_length": len(output_text),
                },
            )

        return PromptRegressionCheck(
            name="output_presence",
            status="failed",
            summary="Prompt output is empty.",
            metadata={
                "output_length": 0,
            },
        )

    @staticmethod
    def _check_expected_status(
        regression_case: PromptRegressionCase,
    ) -> PromptRegressionCheck:
        expected_status = regression_case.expectations.expected_status

        if expected_status is None:
            return PromptRegressionCheck(
                name="expected_status",
                status="passed",
                summary="No expected status was configured.",
            )

        if isinstance(regression_case.actual_output, dict):
            actual_status = regression_case.actual_output.get("status")
        else:
            actual_status = None

        if actual_status == expected_status:
            return PromptRegressionCheck(
                name="expected_status",
                status="passed",
                summary="Output status matched the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                },
            )

        return PromptRegressionCheck(
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
        regression_case: PromptRegressionCase,
    ) -> PromptRegressionCheck:
        required_markers = regression_case.expectations.required_output_markers
        output_text = PromptRegressionEvaluationService._serialize_output(
            regression_case.actual_output
        )

        missing_markers = [
            marker
            for marker in required_markers
            if marker not in output_text
        ]

        if not missing_markers:
            return PromptRegressionCheck(
                name="required_output_markers",
                status="passed",
                summary="All required output markers were found.",
                metadata={
                    "required_output_markers": required_markers,
                    "missing_markers": [],
                },
            )

        return PromptRegressionCheck(
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
        regression_case: PromptRegressionCase,
    ) -> PromptRegressionCheck:
        forbidden_markers = regression_case.expectations.forbidden_output_markers
        output_text = PromptRegressionEvaluationService._serialize_output(
            regression_case.actual_output
        )

        detected_markers = [
            marker
            for marker in forbidden_markers
            if marker in output_text
        ]

        if not detected_markers:
            return PromptRegressionCheck(
                name="forbidden_output_markers",
                status="passed",
                summary="No forbidden output markers were detected.",
                metadata={
                    "forbidden_output_markers": forbidden_markers,
                    "detected_markers": [],
                },
            )

        return PromptRegressionCheck(
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
        regression_case: PromptRegressionCase,
    ) -> PromptRegressionCheck:
        required_json_keys = regression_case.expectations.required_json_keys

        if not required_json_keys:
            return PromptRegressionCheck(
                name="required_json_keys",
                status="passed",
                summary="No required JSON keys were configured.",
            )

        if not isinstance(regression_case.actual_output, dict):
            return PromptRegressionCheck(
                name="required_json_keys",
                status="failed",
                summary="Required JSON keys were configured, but output is not JSON.",
                metadata={
                    "required_json_keys": required_json_keys,
                    "output_type": type(regression_case.actual_output).__name__,
                },
            )

        missing_keys = [
            key
            for key in required_json_keys
            if key not in regression_case.actual_output
        ]

        if not missing_keys:
            return PromptRegressionCheck(
                name="required_json_keys",
                status="passed",
                summary="All required JSON keys were found.",
                metadata={
                    "required_json_keys": required_json_keys,
                    "missing_keys": [],
                },
            )

        return PromptRegressionCheck(
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
        regression_case: PromptRegressionCase,
    ) -> PromptRegressionCheck:
        min_output_length = regression_case.expectations.min_output_length
        output_text = PromptRegressionEvaluationService._serialize_output(
            regression_case.actual_output
        )

        if len(output_text) >= min_output_length:
            return PromptRegressionCheck(
                name="min_output_length",
                status="passed",
                summary="Output length is greater than or equal to the configured minimum.",
                metadata={
                    "min_output_length": min_output_length,
                    "actual_output_length": len(output_text),
                },
            )

        return PromptRegressionCheck(
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

        return json.dumps(
            output,
            ensure_ascii=False,
            sort_keys=True,
        )

    @staticmethod
    def _select_cases(
        cases: list[PromptRegressionCase],
        case_ids: list[str],
    ) -> list[PromptRegressionCase]:
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
        checks: list[PromptRegressionCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _count_results(
        results: list[PromptRegressionCaseResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )
