from ai_api.multi_agent import (
    MultiAgentArtifact,
    MultiAgentConflictAnalysisResponse,
    MultiAgentConflictRecord,
    MultiAgentFailureRecord,
    MultiAgentFinalReportGenerator,
    MultiAgentSharedState,
)


def _build_shared_state() -> MultiAgentSharedState:
    return MultiAgentSharedState(
        objective="Gerar relatório QA multiagente.",
        requirement_text=(
            "Como QA, preciso validar o saldo final por conta considerando "
            "depósitos e retiradas."
        ),
        artifacts=[
            MultiAgentArtifact(
                name="requirement_analysis",
                produced_by="requirement_analyst_agent",
                content={
                    "summary": "O requisito descreve cálculo de saldo final.",
                    "identified_rules": [
                        "Depósitos aumentam o saldo.",
                        "Retiradas reduzem o saldo.",
                    ],
                },
            ),
            MultiAgentArtifact(
                name="functional_test_strategy",
                produced_by="functional_qa_agent",
                content={
                    "positive_scenarios": [
                        "Validar saldo com depósitos e retiradas.",
                    ],
                    "negative_scenarios": [
                        "Validar transação com tipo inválido.",
                    ],
                    "edge_cases": [
                        "Validar conta sem transações.",
                    ],
                },
            ),
            MultiAgentArtifact(
                name="test_automation_strategy",
                produced_by="test_automation_agent",
                content={
                    "automation_candidates": [
                        "Automatizar cálculo de saldo final por conta.",
                    ],
                    "suggested_layers": [
                        "API tests",
                    ],
                    "implementation_notes": [
                        "Usar massa de dados determinística.",
                    ],
                },
            ),
            MultiAgentArtifact(
                name="review_findings",
                produced_by="reviewer_agent",
                content={
                    "strengths": [
                        "Cobertura funcional e automação foram propostas.",
                    ],
                    "risks": [
                        "Regras financeiras precisam ser validadas com dados reais.",
                    ],
                    "recommended_improvements": [
                        "Adicionar regressão SQL para cenários críticos.",
                    ],
                },
            ),
        ],
    )


def test_final_report_generator_should_approve_clean_execution() -> None:
    generator = MultiAgentFinalReportGenerator()

    report = generator.generate(
        shared_state=_build_shared_state(),
        failures=[],
        conflict_analysis=MultiAgentConflictAnalysisResponse(
            status="passed",
            conflict_count=0,
            warning_count=0,
            critical_count=0,
            conflicts=[],
        ),
        contract_validation_status="passed",
    )

    assert report.summary
    assert report.metadata["quality_gate"] == "approved"
    assert report.metadata["failure_count"] == 0
    assert report.metadata["conflict_count"] == 0
    assert "O requisito descreve cálculo de saldo final." in (
        report.requirement_understanding
    )
    assert "Validar saldo com depósitos e retiradas." in (
        report.functional_coverage
    )
    assert "Automatizar cálculo de saldo final por conta." in (
        report.automation_strategy
    )
    assert "Cobertura funcional e automação foram propostas." in (
        report.review_notes
    )


def test_final_report_generator_should_require_review_when_contracts_warn() -> None:
    generator = MultiAgentFinalReportGenerator()

    report = generator.generate(
        shared_state=_build_shared_state(),
        failures=[],
        conflict_analysis=MultiAgentConflictAnalysisResponse(
            status="passed",
            conflict_count=0,
            warning_count=0,
            critical_count=0,
            conflicts=[],
        ),
        contract_validation_status="warning",
    )

    assert report.metadata["quality_gate"] == "requires_review"
    assert "Corrigir contratos de comunicação que não foram atendidos." in (
        report.next_steps
    )
    assert "Validação de contratos retornou status warning." in report.review_notes


def test_final_report_generator_should_block_when_failures_exist() -> None:
    generator = MultiAgentFinalReportGenerator()

    report = generator.generate(
        shared_state=_build_shared_state(),
        failures=[
            MultiAgentFailureRecord(
                agent_name="functional_qa_agent",
                error_type="RuntimeError",
                message="Simulated failure.",
            )
        ],
        conflict_analysis=MultiAgentConflictAnalysisResponse(
            status="passed",
            conflict_count=0,
            warning_count=0,
            critical_count=0,
            conflicts=[],
        ),
        contract_validation_status="passed",
    )

    assert report.metadata["quality_gate"] == "blocked"
    assert report.metadata["failure_count"] == 1
    assert report.next_steps[0] == (
        "Investigar falhas capturadas durante a execução multiagente."
    )
    assert "Foram capturadas 1 falha(s) durante a execução." in report.review_notes


def test_final_report_generator_should_block_when_critical_conflicts_exist() -> None:
    generator = MultiAgentFinalReportGenerator()

    report = generator.generate(
        shared_state=_build_shared_state(),
        failures=[],
        conflict_analysis=MultiAgentConflictAnalysisResponse(
            status="failed",
            conflict_count=1,
            warning_count=0,
            critical_count=1,
            conflicts=[
                MultiAgentConflictRecord(
                    conflict_type="duplicate_artifact_name",
                    severity="critical",
                    artifact_name="requirement_analysis",
                    involved_agents=[
                        "requirement_analyst_agent",
                        "functional_qa_agent",
                    ],
                    summary="Conflicting artifacts detected.",
                )
            ],
        ),
        contract_validation_status="passed",
    )

    assert report.metadata["quality_gate"] == "blocked"
    assert report.metadata["conflict_count"] == 1
    assert report.next_steps[0] == (
        "Revisar conflitos detectados no estado compartilhado multiagente."
    )
    assert "Análise de conflitos retornou status failed." in report.review_notes
