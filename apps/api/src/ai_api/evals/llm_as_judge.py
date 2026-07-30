from ai_api.evals.schemas import (
    LLMAsJudgeEvaluationCase,
    LLMAsJudgeEvaluationCaseResult,
    LLMAsJudgeEvaluationCheck,
    LLMAsJudgeEvaluationRunRequest,
    LLMAsJudgeEvaluationRunResponse,
    LLMAsJudgeEvaluationSuite,
    LLMAsJudgeExpectation,
    LLMAsJudgeOutput,
    LLMAsJudgeRubricItem,
)


def build_default_llm_as_judge_evaluation_suite() -> LLMAsJudgeEvaluationSuite:
    return LLMAsJudgeEvaluationSuite(
        name="applied-ai-engineering-lab-llm-as-judge-evaluation-suite",
        version="0.1.0",
        description=(
            "Controlled LLM-as-judge evaluation prototype for validating "
            "judge outputs over requirement analysis, RAG answers and "
            "multi-agent final reports."
        ),
        cases=[
            LLMAsJudgeEvaluationCase(
                id="JUDGE-REQ-001",
                name="Judge requirement analysis quality",
                evaluation_target="requirement_analysis",
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "language": "pt-BR",
                },
                candidate_output={
                    "status": "completed",
                    "summary": "Validar saldo final por conta.",
                    "business_rules": [
                        "Depósitos aumentam saldo.",
                        "Retiradas reduzem saldo.",
                    ],
                    "acceptance_criteria": [
                        "Saldo final deve refletir todas as transações.",
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
                rubric=[
                    LLMAsJudgeRubricItem(
                        name="structure",
                        description="Output preserves the expected structured QA fields.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                    LLMAsJudgeRubricItem(
                        name="qa_relevance",
                        description="Output is relevant for QA analysis and testing.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                    LLMAsJudgeRubricItem(
                        name="business_alignment",
                        description="Output aligns with the business requirement.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                ],
                judge_output=LLMAsJudgeOutput(
                    verdict="pass",
                    score=0.95,
                    rationale=(
                        "The requirement analysis is structured, QA-oriented and "
                        "business-aligned. It covers rules, criteria, positive "
                        "scenarios, negative scenarios and edge cases."
                    ),
                    criteria_scores={
                        "structure": 1.0,
                        "qa_relevance": 0.95,
                        "business_alignment": 0.9,
                    },
                    strengths=[
                        "Strong structured QA output.",
                        "Relevant test scenario coverage.",
                    ],
                    weaknesses=[
                        "Could expand edge cases in future versions.",
                    ],
                    metadata={
                        "judge_mode": "controlled_prototype",
                    },
                ),
                expectations=LLMAsJudgeExpectation(
                    allowed_verdicts=[
                        "pass",
                    ],
                    min_score=0.8,
                    required_rationale_markers=[
                        "structured",
                        "QA-oriented",
                        "business-aligned",
                    ],
                    required_criteria=[
                        "structure",
                        "qa_relevance",
                        "business_alignment",
                    ],
                    require_strengths=True,
                    require_weaknesses=True,
                ),
                tags=[
                    "llm-as-judge",
                    "requirement-analysis",
                    "qa",
                ],
                metadata={
                    "source": "m7_llm_as_judge_evaluation_suite",
                },
            ),
            LLMAsJudgeEvaluationCase(
                id="JUDGE-RAG-001",
                name="Judge RAG answer grounding quality",
                evaluation_target="rag_answer",
                input_payload={
                    "query": "Quando o boleto deve ser registrado?",
                    "language": "pt-BR",
                    "context": (
                        "Boletos de cobrança devem ser registrados antes "
                        "do envio ao cliente."
                    ),
                },
                candidate_output={
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
                            "metadata": {
                                "source": "billing-policy.md",
                            },
                        }
                    ],
                },
                rubric=[
                    LLMAsJudgeRubricItem(
                        name="grounding",
                        description="Answer is grounded in the provided context.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                    LLMAsJudgeRubricItem(
                        name="citation_quality",
                        description="Answer includes useful citation evidence.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                    LLMAsJudgeRubricItem(
                        name="answer_relevance",
                        description="Answer directly addresses the user query.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                ],
                judge_output=LLMAsJudgeOutput(
                    verdict="pass",
                    score=0.92,
                    rationale=(
                        "The RAG answer is grounded in the supplied context, "
                        "includes citations and directly answers the boleto "
                        "registration question."
                    ),
                    criteria_scores={
                        "grounding": 0.95,
                        "citation_quality": 0.9,
                        "answer_relevance": 0.9,
                    },
                    strengths=[
                        "Grounded answer.",
                        "Citation evidence is present.",
                    ],
                    weaknesses=[
                        "Could include more detail about validation timing.",
                    ],
                    metadata={
                        "judge_mode": "controlled_prototype",
                    },
                ),
                expectations=LLMAsJudgeExpectation(
                    allowed_verdicts=[
                        "pass",
                    ],
                    min_score=0.8,
                    required_rationale_markers=[
                        "grounded",
                        "citations",
                        "directly answers",
                    ],
                    required_criteria=[
                        "grounding",
                        "citation_quality",
                        "answer_relevance",
                    ],
                    require_strengths=True,
                    require_weaknesses=True,
                ),
                tags=[
                    "llm-as-judge",
                    "rag",
                    "grounding",
                ],
                metadata={
                    "source": "m7_llm_as_judge_evaluation_suite",
                },
            ),
            LLMAsJudgeEvaluationCase(
                id="JUDGE-MULTI-001",
                name="Judge Multi-Agent QA final report quality",
                evaluation_target="multi_agent_final_report",
                input_payload={
                    "requirement_text": (
                        "Como QA, preciso validar o saldo final por conta "
                        "considerando depósitos e retiradas."
                    ),
                    "language": "pt-BR",
                },
                candidate_output={
                    "status": "completed",
                    "final_report": {
                        "summary": "Relatório final QA gerado com sucesso.",
                        "requirement_understanding": [
                            "O saldo final deve considerar depósitos e retiradas.",
                        ],
                        "functional_coverage": [
                            "Validar cenários positivos, negativos e bordas.",
                        ],
                        "automation_strategy": [
                            "Automatizar validação em camada de API.",
                        ],
                        "review_notes": [
                            "Revisar regras financeiras e massa de dados.",
                        ],
                        "next_steps": [
                            "Expandir dataset de regressão.",
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
                rubric=[
                    LLMAsJudgeRubricItem(
                        name="report_completeness",
                        description="Final report includes the expected QA sections.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                    LLMAsJudgeRubricItem(
                        name="risk_awareness",
                        description="Final report identifies review notes and risks.",
                        weight=1.0,
                        passing_score=0.7,
                    ),
                    LLMAsJudgeRubricItem(
                        name="actionability",
                        description="Final report includes useful next steps.",
                        weight=1.0,
                        passing_score=0.8,
                    ),
                ],
                judge_output=LLMAsJudgeOutput(
                    verdict="pass",
                    score=0.9,
                    rationale=(
                        "The multi-agent final report is complete, actionable and "
                        "includes QA review notes, final report sections and next steps."
                    ),
                    criteria_scores={
                        "report_completeness": 0.95,
                        "risk_awareness": 0.85,
                        "actionability": 0.9,
                    },
                    strengths=[
                        "Complete final report structure.",
                        "Clear next steps.",
                    ],
                    weaknesses=[
                        "Could include deeper risk scoring in future iterations.",
                    ],
                    metadata={
                        "judge_mode": "controlled_prototype",
                    },
                ),
                expectations=LLMAsJudgeExpectation(
                    allowed_verdicts=[
                        "pass",
                    ],
                    min_score=0.8,
                    required_rationale_markers=[
                        "complete",
                        "actionable",
                        "final report sections",
                    ],
                    required_criteria=[
                        "report_completeness",
                        "risk_awareness",
                        "actionability",
                    ],
                    require_strengths=True,
                    require_weaknesses=True,
                ),
                tags=[
                    "llm-as-judge",
                    "multi-agent",
                    "final-report",
                ],
                metadata={
                    "source": "m7_llm_as_judge_evaluation_suite",
                },
            ),
        ],
        metadata={
            "source": "m7_llm_as_judge_evaluation_suite",
            "suite_type": "llm_as_judge_evaluation",
            "execution_mode": "controlled_judge_output_validation",
            "prototype_scope": (
                "This version validates structured judge outputs. Future versions "
                "may generate judge outputs through configured LLM providers."
            ),
        },
    )


class LLMAsJudgeEvaluationSuiteService:
    def get_default_suite(self) -> LLMAsJudgeEvaluationSuite:
        return build_default_llm_as_judge_evaluation_suite()


class LLMAsJudgeEvaluationService:
    def run(
        self,
        request: LLMAsJudgeEvaluationRunRequest,
    ) -> LLMAsJudgeEvaluationRunResponse:
        suite = request.suite or build_default_llm_as_judge_evaluation_suite()
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

        return LLMAsJudgeEvaluationRunResponse(
            status=status,
            suite_name=suite.name,
            suite_version=suite.version,
            case_count=len(selected_cases),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            average_score=self._average_score(selected_cases),
            results=results,
            metadata={
                "runner": "llm-as-judge-evaluator-v1",
                "selected_case_ids": [
                    evaluation_case.id
                    for evaluation_case in selected_cases
                ],
                "execution_mode": "controlled_judge_output_validation",
                **request.metadata,
            },
        )

    def _run_case(
        self,
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCaseResult:
        checks = [
            self._check_judge_output_presence(evaluation_case),
            self._check_allowed_verdict(evaluation_case),
            self._check_min_score(evaluation_case),
            self._check_required_rationale_markers(evaluation_case),
            self._check_forbidden_rationale_markers(evaluation_case),
            self._check_required_criteria(evaluation_case),
            self._check_rubric_scores(evaluation_case),
            self._check_strengths(evaluation_case),
            self._check_weaknesses(evaluation_case),
        ]

        status = self._resolve_status(checks)

        return LLMAsJudgeEvaluationCaseResult(
            case_id=evaluation_case.id,
            case_name=evaluation_case.name,
            evaluation_target=evaluation_case.evaluation_target,
            status=status,
            checks=checks,
            metadata={
                "tags": evaluation_case.tags,
                "judge_score": evaluation_case.judge_output.score
                if evaluation_case.judge_output is not None
                else None,
                "judge_verdict": evaluation_case.judge_output.verdict
                if evaluation_case.judge_output is not None
                else None,
            },
        )

    @staticmethod
    def _check_judge_output_presence(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        if evaluation_case.judge_output is not None:
            return LLMAsJudgeEvaluationCheck(
                name="judge_output_presence",
                status="passed",
                summary="Judge output is present.",
            )

        return LLMAsJudgeEvaluationCheck(
            name="judge_output_presence",
            status="failed",
            summary="Judge output is required but missing.",
        )

    @staticmethod
    def _check_allowed_verdict(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output

        if judge_output is None:
            return LLMAsJudgeEvaluationCheck(
                name="allowed_verdict",
                status="failed",
                summary="Cannot validate verdict because judge output is missing.",
            )

        allowed_verdicts = evaluation_case.expectations.allowed_verdicts

        if judge_output.verdict in allowed_verdicts:
            return LLMAsJudgeEvaluationCheck(
                name="allowed_verdict",
                status="passed",
                summary="Judge verdict is allowed.",
                metadata={
                    "allowed_verdicts": allowed_verdicts,
                    "actual_verdict": judge_output.verdict,
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="allowed_verdict",
            status="failed",
            summary="Judge verdict is not allowed.",
            metadata={
                "allowed_verdicts": allowed_verdicts,
                "actual_verdict": judge_output.verdict,
            },
        )

    @staticmethod
    def _check_min_score(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output
        min_score = evaluation_case.expectations.min_score

        if judge_output is None:
            return LLMAsJudgeEvaluationCheck(
                name="min_score",
                status="failed",
                summary="Cannot validate score because judge output is missing.",
                metadata={
                    "min_score": min_score,
                    "actual_score": None,
                },
            )

        if judge_output.score >= min_score:
            return LLMAsJudgeEvaluationCheck(
                name="min_score",
                status="passed",
                summary="Judge score meets the configured minimum.",
                metadata={
                    "min_score": min_score,
                    "actual_score": judge_output.score,
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="min_score",
            status="failed",
            summary="Judge score is below the configured minimum.",
            metadata={
                "min_score": min_score,
                "actual_score": judge_output.score,
            },
        )

    @staticmethod
    def _check_required_rationale_markers(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output
        required_markers = evaluation_case.expectations.required_rationale_markers

        if judge_output is None:
            return LLMAsJudgeEvaluationCheck(
                name="required_rationale_markers",
                status="failed",
                summary="Cannot validate rationale markers because judge output is missing.",
            )

        missing_markers = [
            marker
            for marker in required_markers
            if marker not in judge_output.rationale
        ]

        if not missing_markers:
            return LLMAsJudgeEvaluationCheck(
                name="required_rationale_markers",
                status="passed",
                summary="All required rationale markers were found.",
                metadata={
                    "required_rationale_markers": required_markers,
                    "missing_markers": [],
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="required_rationale_markers",
            status="failed",
            summary="One or more required rationale markers were missing.",
            metadata={
                "required_rationale_markers": required_markers,
                "missing_markers": missing_markers,
            },
        )

    @staticmethod
    def _check_forbidden_rationale_markers(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output
        forbidden_markers = evaluation_case.expectations.forbidden_rationale_markers

        if judge_output is None:
            return LLMAsJudgeEvaluationCheck(
                name="forbidden_rationale_markers",
                status="failed",
                summary="Cannot validate forbidden rationale markers because judge output is missing.",
            )

        detected_markers = [
            marker
            for marker in forbidden_markers
            if marker in judge_output.rationale
        ]

        if not detected_markers:
            return LLMAsJudgeEvaluationCheck(
                name="forbidden_rationale_markers",
                status="passed",
                summary="No forbidden rationale markers were detected.",
                metadata={
                    "forbidden_rationale_markers": forbidden_markers,
                    "detected_markers": [],
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="forbidden_rationale_markers",
            status="failed",
            summary="One or more forbidden rationale markers were detected.",
            metadata={
                "forbidden_rationale_markers": forbidden_markers,
                "detected_markers": detected_markers,
            },
        )

    @staticmethod
    def _check_required_criteria(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output
        required_criteria = evaluation_case.expectations.required_criteria

        if judge_output is None:
            return LLMAsJudgeEvaluationCheck(
                name="required_criteria",
                status="failed",
                summary="Cannot validate criteria because judge output is missing.",
            )

        missing_criteria = [
            criterion
            for criterion in required_criteria
            if criterion not in judge_output.criteria_scores
        ]

        if not missing_criteria:
            return LLMAsJudgeEvaluationCheck(
                name="required_criteria",
                status="passed",
                summary="All required judge criteria were found.",
                metadata={
                    "required_criteria": required_criteria,
                    "missing_criteria": [],
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="required_criteria",
            status="failed",
            summary="One or more required judge criteria were missing.",
            metadata={
                "required_criteria": required_criteria,
                "missing_criteria": missing_criteria,
            },
        )

    @staticmethod
    def _check_rubric_scores(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output

        if judge_output is None:
            return LLMAsJudgeEvaluationCheck(
                name="rubric_scores",
                status="failed",
                summary="Cannot validate rubric scores because judge output is missing.",
            )

        failed_items = []

        for rubric_item in evaluation_case.rubric:
            actual_score = judge_output.criteria_scores.get(rubric_item.name)

            if actual_score is None:
                failed_items.append(
                    {
                        "criterion": rubric_item.name,
                        "reason": "missing_score",
                        "passing_score": rubric_item.passing_score,
                        "actual_score": None,
                    }
                )
                continue

            if actual_score < rubric_item.passing_score:
                failed_items.append(
                    {
                        "criterion": rubric_item.name,
                        "reason": "below_passing_score",
                        "passing_score": rubric_item.passing_score,
                        "actual_score": actual_score,
                    }
                )

        if not failed_items:
            return LLMAsJudgeEvaluationCheck(
                name="rubric_scores",
                status="passed",
                summary="All rubric item scores meet their passing thresholds.",
                metadata={
                    "failed_items": [],
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="rubric_scores",
            status="failed",
            summary="One or more rubric item scores failed.",
            metadata={
                "failed_items": failed_items,
            },
        )

    @staticmethod
    def _check_strengths(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output

        if not evaluation_case.expectations.require_strengths:
            return LLMAsJudgeEvaluationCheck(
                name="strengths",
                status="passed",
                summary="Strengths were not required.",
            )

        if judge_output is not None and judge_output.strengths:
            return LLMAsJudgeEvaluationCheck(
                name="strengths",
                status="passed",
                summary="Judge strengths are present.",
                metadata={
                    "strength_count": len(judge_output.strengths),
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="strengths",
            status="failed",
            summary="Judge strengths were required but missing.",
        )

    @staticmethod
    def _check_weaknesses(
        evaluation_case: LLMAsJudgeEvaluationCase,
    ) -> LLMAsJudgeEvaluationCheck:
        judge_output = evaluation_case.judge_output

        if not evaluation_case.expectations.require_weaknesses:
            return LLMAsJudgeEvaluationCheck(
                name="weaknesses",
                status="passed",
                summary="Weaknesses were not required.",
            )

        if judge_output is not None and judge_output.weaknesses:
            return LLMAsJudgeEvaluationCheck(
                name="weaknesses",
                status="passed",
                summary="Judge weaknesses are present.",
                metadata={
                    "weakness_count": len(judge_output.weaknesses),
                },
            )

        return LLMAsJudgeEvaluationCheck(
            name="weaknesses",
            status="failed",
            summary="Judge weaknesses were required but missing.",
        )

    @staticmethod
    def _select_cases(
        cases: list[LLMAsJudgeEvaluationCase],
        case_ids: list[str],
    ) -> list[LLMAsJudgeEvaluationCase]:
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
        checks: list[LLMAsJudgeEvaluationCheck],
    ) -> str:
        if any(check.status == "failed" for check in checks):
            return "failed"

        if any(check.status == "warning" for check in checks):
            return "warning"

        return "passed"

    @staticmethod
    def _count_results(
        results: list[LLMAsJudgeEvaluationCaseResult],
        status: str,
    ) -> int:
        return len(
            [
                result
                for result in results
                if result.status == status
            ]
        )

    @staticmethod
    def _average_score(
        cases: list[LLMAsJudgeEvaluationCase],
    ) -> float | None:
        scores = [
            evaluation_case.judge_output.score
            for evaluation_case in cases
            if evaluation_case.judge_output is not None
        ]

        if not scores:
            return None

        return round(sum(scores) / len(scores), 4)
