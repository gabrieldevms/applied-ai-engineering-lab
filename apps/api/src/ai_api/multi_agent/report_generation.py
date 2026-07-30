from typing import Any
from ai_api.multi_agent.schemas import (
    MultiAgentConflictAnalysisResponse,
    MultiAgentFailureRecord,
    MultiAgentFinalReport,
    MultiAgentSharedState,
)


class MultiAgentFinalReportGenerator:
    def generate(
        self,
        shared_state: MultiAgentSharedState,
        failures: list[MultiAgentFailureRecord],
        conflict_analysis: MultiAgentConflictAnalysisResponse,
        contract_validation_status: str,
    ) -> MultiAgentFinalReport:
        requirement_analysis = self._find_artifact_content(
            shared_state=shared_state,
            artifact_name="requirement_analysis",
        )
        functional_strategy = self._find_artifact_content(
            shared_state=shared_state,
            artifact_name="functional_test_strategy",
        )
        automation_strategy = self._find_artifact_content(
            shared_state=shared_state,
            artifact_name="test_automation_strategy",
        )
        data_validation_analysis = self._find_artifact_content(
            shared_state=shared_state,
            artifact_name="data_validation_analysis",
        )
        review_findings = self._find_artifact_content(
            shared_state=shared_state,
            artifact_name="review_findings",
        )

        quality_gate = self._resolve_quality_gate(
            failures=failures,
            conflict_analysis=conflict_analysis,
            contract_validation_status=contract_validation_status,
        )

        report_metadata = {
            "source": "multi-agent-final-report-generator-v1",
            "artifact_count": len(shared_state.artifacts),
            "message_count": len(shared_state.messages),
            "failure_count": len(failures),
            "conflict_count": conflict_analysis.conflict_count,
            "contract_validation_status": contract_validation_status,
            "conflict_analysis_status": conflict_analysis.status,
            "quality_gate": quality_gate,
            "data_validation_available": bool(data_validation_analysis),
        }

        return MultiAgentFinalReport(
            summary=self._build_summary(
                quality_gate=quality_gate,
                failures=failures,
                conflict_analysis=conflict_analysis,
                contract_validation_status=contract_validation_status,
            ),
            requirement_understanding=self._build_requirement_understanding(
                requirement_analysis=requirement_analysis,
                shared_state=shared_state,
            ),
            functional_coverage=self._build_functional_coverage(
                functional_strategy=functional_strategy,
            ),
            automation_strategy=self._build_automation_strategy(
                automation_strategy=automation_strategy,
            ),
            data_validation_evidence=self._build_data_validation_evidence(
                data_validation_analysis=data_validation_analysis,
            ),
            review_notes=self._build_review_notes(
                review_findings=review_findings,
                failures=failures,
                conflict_analysis=conflict_analysis,
                contract_validation_status=contract_validation_status,
                data_validation_analysis=data_validation_analysis,
            ),
            next_steps=self._build_next_steps(
                quality_gate=quality_gate,
                failures=failures,
                conflict_analysis=conflict_analysis,
                contract_validation_status=contract_validation_status,
                data_validation_analysis=data_validation_analysis,
            ),
            metadata=report_metadata,
        )

    def _build_summary(
        self,
        quality_gate: str,
        failures: list[MultiAgentFailureRecord],
        conflict_analysis: MultiAgentConflictAnalysisResponse,
        contract_validation_status: str,
    ) -> str:
        if quality_gate == "approved":
            return (
                "Relatório final QA gerado com sucesso. O fluxo multiagente "
                "foi concluído sem falhas, sem conflitos críticos e com contratos "
                "de comunicação válidos."
            )

        if quality_gate == "requires_review":
            return (
                "Relatório final QA gerado com ressalvas. O fluxo multiagente "
                "foi executado, mas existem avisos, contratos incompletos, "
                "conflitos não críticos ou pontos que exigem revisão."
            )

        return (
            "Relatório final QA gerado em modo parcial. O fluxo multiagente "
            "encontrou falhas, conflitos críticos ou quebras relevantes de "
            "contrato e precisa de revisão antes de ser considerado aprovado."
        )

    def _build_requirement_understanding(
        self,
        requirement_analysis: dict[str, Any],
        shared_state: MultiAgentSharedState,
    ) -> list[str]:
        items = [
            requirement_analysis.get(
                "summary",
                f"Requisito analisado: {shared_state.requirement_text}",
            ),
            *requirement_analysis.get("identified_rules", []),
        ]

        return self._deduplicate(items)

    def _build_functional_coverage(
        self,
        functional_strategy: dict[str, Any],
    ) -> list[str]:
        items = [
            *functional_strategy.get("positive_scenarios", []),
            *functional_strategy.get("negative_scenarios", []),
            *functional_strategy.get("edge_cases", []),
        ]

        if not items:
            return [
                "Cobertura funcional não foi gerada ou está incompleta.",
            ]

        return self._deduplicate(items)

    def _build_automation_strategy(
        self,
        automation_strategy: dict[str, Any],
    ) -> list[str]:
        items = [
            *automation_strategy.get("automation_candidates", []),
            *automation_strategy.get("suggested_layers", []),
            *automation_strategy.get("implementation_notes", []),
        ]

        if not items:
            return [
                "Estratégia de automação não foi gerada ou está incompleta.",
            ]

        return self._deduplicate(items)

    def _build_data_validation_evidence(
        self,
        data_validation_analysis: dict[str, Any],
    ) -> list[str]:
        if not data_validation_analysis:
            return []

        workflow = data_validation_analysis.get("workflow", {})
        evidence = data_validation_analysis.get("evidence", {})

        items = [
            f"Validação de dados retornou status: {data_validation_analysis.get('status', 'unknown')}.",
            f"Resposta da validação de dados: {data_validation_analysis.get('answer', 'não disponível')}",
        ]

        if workflow:
            items.append(
                f"Workflow SQL retornou status: {workflow.get('status', 'unknown')}."
            )

            generated_sql = workflow.get("generated_sql")
            if generated_sql:
                items.append(f"SQL gerado para validação: {generated_sql}")

        if evidence:
            row_count = evidence.get("row_count")
            column_count = evidence.get("column_count")

            if row_count is not None:
                items.append(f"Linhas retornadas pela validação: {row_count}.")

            if column_count is not None:
                items.append(f"Colunas retornadas pela validação: {column_count}.")

        return self._deduplicate(items)

    def _build_review_notes(
        self,
        review_findings: dict[str, Any],
        failures: list[MultiAgentFailureRecord],
        conflict_analysis: MultiAgentConflictAnalysisResponse,
        contract_validation_status: str,
        data_validation_analysis: dict[str, Any],
    ) -> list[str]:
        items = [
            *review_findings.get("strengths", []),
            *review_findings.get("risks", []),
            *review_findings.get("recommended_improvements", []),
        ]

        if data_validation_analysis:
            items.append(
                "Evidência de validação de dados foi incorporada ao relatório final."
            )

        if failures:
            items.append(
                f"Foram capturadas {len(failures)} falha(s) durante a execução."
            )

        if conflict_analysis.status != "passed":
            items.append(
                f"Análise de conflitos retornou status {conflict_analysis.status}."
            )

        if contract_validation_status != "passed":
            items.append(
                f"Validação de contratos retornou status {contract_validation_status}."
            )

        if not items:
            return [
                "Nenhuma observação de revisão foi gerada.",
            ]

        return self._deduplicate(items)

    def _build_next_steps(
        self,
        quality_gate: str,
        failures: list[MultiAgentFailureRecord],
        conflict_analysis: MultiAgentConflictAnalysisResponse,
        contract_validation_status: str,
        data_validation_analysis: dict[str, Any],
    ) -> list[str]:
        next_steps: list[str] = []

        if failures:
            next_steps.append(
                "Investigar falhas capturadas durante a execução multiagente."
            )

        if conflict_analysis.status != "passed":
            next_steps.append(
                "Revisar conflitos detectados no estado compartilhado multiagente."
            )

        if contract_validation_status != "passed":
            next_steps.append(
                "Corrigir contratos de comunicação que não foram atendidos."
            )

        if not data_validation_analysis:
            next_steps.append(
                "Adicionar validação de dados quando o requisito depender de evidência em tabelas ou bases de dados."
            )

        if quality_gate != "approved":
            next_steps.append(
                "Executar nova rodada do copilot após correções e revisão dos pontos críticos."
            )

        next_steps.extend(
            [
                "Integrar mais agentes especializados com serviços reais do projeto.",
                "Adicionar exposição MCP para o Multi-Agent QA Copilot.",
                "Evoluir agentes determinísticos para agentes com raciocínio LLM controlado.",
                "Preparar relatório final para uso em demonstrações de portfólio.",
            ]
        )

        return self._deduplicate(next_steps)

    @staticmethod
    def _resolve_quality_gate(
        failures: list[MultiAgentFailureRecord],
        conflict_analysis: MultiAgentConflictAnalysisResponse,
        contract_validation_status: str,
    ) -> str:
        if failures or conflict_analysis.status == "failed":
            return "blocked"

        if (
            conflict_analysis.status == "warning"
            or contract_validation_status in {"warning", "failed"}
        ):
            return "requires_review"

        return "approved"

    @staticmethod
    def _find_artifact_content(
        shared_state: MultiAgentSharedState,
        artifact_name: str,
    ) -> dict[str, Any]:
        for artifact in shared_state.artifacts:
            if artifact.name == artifact_name:
                return artifact.content

        return {}

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        deduplicated_items: list[str] = []
        seen_items: set[str] = set()

        for item in items:
            normalized_item = str(item).strip()

            if not normalized_item or normalized_item in seen_items:
                continue

            seen_items.add(normalized_item)
            deduplicated_items.append(normalized_item)

        return deduplicated_items
