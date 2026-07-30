from typing import Any
from ai_api.multi_agent.conflict_handling import MultiAgentConflictDetector
from ai_api.multi_agent.contracts import MultiAgentCommunicationContractValidator
from ai_api.multi_agent.failure_handling import MultiAgentFailureHandler
from ai_api.multi_agent.roles import build_default_multi_agent_roles
from ai_api.multi_agent.schemas import (
    MultiAgentArtifact,
    MultiAgentConflictAnalysisResponse,
    MultiAgentFailureRecord,
    MultiAgentFinalReport,
    MultiAgentMessage,
    MultiAgentQACopilotRequest,
    MultiAgentQACopilotResponse,
    MultiAgentRoleDescriptor,
    MultiAgentRoleName,
    MultiAgentSharedState,
    MultiAgentTaskResult,
    MultiAgentTraceStep,
)


class MultiAgentQACopilotService:
    def __init__(
        self,
        roles: list[MultiAgentRoleDescriptor] | None = None,
        contract_validator: MultiAgentCommunicationContractValidator | None = None,
        failure_handler: MultiAgentFailureHandler | None = None,
        conflict_detector: MultiAgentConflictDetector | None = None,
    ) -> None:
        self.roles = roles if roles is not None else build_default_multi_agent_roles()
        self.contract_validator = (
            contract_validator
            if contract_validator is not None
            else MultiAgentCommunicationContractValidator()
        )
        self.failure_handler = (
            failure_handler
            if failure_handler is not None
            else MultiAgentFailureHandler()
        )
        self.conflict_detector = (
            conflict_detector
            if conflict_detector is not None
            else MultiAgentConflictDetector()
        )

    def run(
        self,
        request: MultiAgentQACopilotRequest,
    ) -> MultiAgentQACopilotResponse:
        objective = (
            request.objective
            or "Orchestrate a multi-agent QA analysis for the provided requirement."
        )

        shared_state = MultiAgentSharedState(
            objective=objective,
            requirement_text=request.requirement_text,
            language=request.language,
            context=request.context,
            metadata={
                "execution_mode": "deterministic_foundation",
                "failure_strategy": request.failure_strategy,
                "source": "multi-agent-qa-copilot-v1",
                **request.metadata,
            },
        )

        selected_roles = self.roles[: request.max_agents]
        task_results: list[MultiAgentTaskResult] = []
        trace: list[MultiAgentTraceStep] = []
        failures: list[MultiAgentFailureRecord] = []
        execution_blocked = False
        blocked_by: MultiAgentRoleName | None = None

        for role in selected_roles:
            if execution_blocked and blocked_by is not None:
                task_result = self.failure_handler.build_skipped_task_result(
                    agent_name=role.name,
                    blocked_by=blocked_by,
                )
            else:
                try:
                    task_result = self._run_role(
                        role_name=role.name,
                        request=request,
                        shared_state=shared_state,
                    )
                except Exception as error:
                    failure = self.failure_handler.build_failure_record(
                        agent_name=role.name,
                        error=error,
                    )
                    failures.append(failure)
                    task_result = self.failure_handler.build_failed_task_result(
                        failure=failure,
                    )

                    if request.failure_strategy == "stop_on_failure":
                        execution_blocked = True
                        blocked_by = role.name

            task_results.append(task_result)
            shared_state.artifacts.extend(task_result.artifacts)
            shared_state.messages.extend(task_result.messages)

            trace.append(
                MultiAgentTraceStep(
                    step_name=role.name,
                    agent_name=role.name,
                    status=task_result.status,
                    summary=task_result.summary,
                    metadata={
                        "artifact_count": len(task_result.artifacts),
                        "message_count": len(task_result.messages),
                    },
                )
            )

        contract_validation = self.contract_validator.validate(shared_state)
        conflict_analysis = self.conflict_detector.detect(shared_state)
        final_report = self._build_final_report(
            shared_state=shared_state,
            failures=failures,
            conflict_analysis=conflict_analysis,
        )
        response_status = self._resolve_status(
            task_results=task_results,
            failures=failures,
            conflict_analysis=conflict_analysis,
        )

        return MultiAgentQACopilotResponse(
            status=response_status,
            copilot_name="multi-agent-qa-copilot-v1",
            objective=objective,
            roles=selected_roles,
            shared_state=shared_state,
            task_results=task_results,
            final_report=final_report,
            trace=trace,
            contract_validation=contract_validation,
            failures=failures,
            conflict_analysis=conflict_analysis,
            metadata={
                "execution_mode": "deterministic_foundation",
                "failure_strategy": request.failure_strategy,
                "agent_count": len(selected_roles),
                "artifact_count": len(shared_state.artifacts),
                "message_count": len(shared_state.messages),
                "failure_count": len(failures),
                "contract_validation_status": contract_validation.status,
                "conflict_analysis_status": conflict_analysis.status,
            },
        )

    def _run_role(
        self,
        role_name: MultiAgentRoleName,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentTaskResult:
        if role_name == "orchestrator_agent":
            return self._run_orchestrator_agent(request, shared_state)

        if role_name == "requirement_analyst_agent":
            return self._run_requirement_analyst_agent(request, shared_state)

        if role_name == "functional_qa_agent":
            return self._run_functional_qa_agent(request, shared_state)

        if role_name == "test_automation_agent":
            return self._run_test_automation_agent(request, shared_state)

        if role_name == "reviewer_agent":
            return self._run_reviewer_agent(request, shared_state)

        return self._run_report_agent(request, shared_state)

    def _run_orchestrator_agent(
        self,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentTaskResult:
        artifact = MultiAgentArtifact(
            name="workflow_plan",
            produced_by="orchestrator_agent",
            content={
                "objective": shared_state.objective,
                "planned_agents": [
                    role.name
                    for role in self.roles[: request.max_agents]
                ],
                "execution_strategy": "sequential_shared_state",
                "expected_outputs": [
                    "requirement_analysis",
                    "functional_test_strategy",
                    "test_automation_strategy",
                    "review_findings",
                    "final_qa_report",
                ],
            },
        )

        message = MultiAgentMessage(
            sender="orchestrator_agent",
            recipient="requirement_analyst_agent",
            content=(
                "Plano de execução multiagente criado para análise de qualidade."
            ),
        )

        return MultiAgentTaskResult(
            agent_name="orchestrator_agent",
            status="completed",
            summary="Orquestração inicial criada com sucesso.",
            artifacts=[artifact],
            messages=[message],
        )

    def _run_requirement_analyst_agent(
        self,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentTaskResult:
        excerpt = self._build_requirement_excerpt(request.requirement_text)

        artifact = MultiAgentArtifact(
            name="requirement_analysis",
            produced_by="requirement_analyst_agent",
            content={
                "summary": f"Requisito analisado: {excerpt}",
                "identified_rules": [
                    "Entender o comportamento esperado descrito no requisito.",
                    "Identificar condições de aceite antes da validação final.",
                    "Mapear dependências de dados, integrações ou regras de negócio.",
                ],
                "open_questions": [
                    "Existem regras de negócio não descritas explicitamente?",
                    "Há cenários de exceção que precisam ser confirmados?",
                ],
            },
        )

        message = MultiAgentMessage(
            sender="requirement_analyst_agent",
            recipient="functional_qa_agent",
            content=(
                "Análise inicial do requisito concluída e disponível para "
                "planejamento funcional."
            ),
        )

        return MultiAgentTaskResult(
            agent_name="requirement_analyst_agent",
            status="completed",
            summary="Requisito analisado em nível funcional e de negócio.",
            artifacts=[artifact],
            messages=[message],
        )

    def _run_functional_qa_agent(
        self,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentTaskResult:
        artifact = MultiAgentArtifact(
            name="functional_test_strategy",
            produced_by="functional_qa_agent",
            content={
                "positive_scenarios": [
                    "Validar o fluxo principal com dados válidos.",
                    "Validar que o resultado esperado é apresentado ao usuário.",
                ],
                "negative_scenarios": [
                    "Validar comportamento com dados inválidos ou incompletos.",
                    "Validar mensagens de erro e bloqueios esperados.",
                ],
                "edge_cases": [
                    "Validar limites de valores, datas, estados ou combinações críticas.",
                    "Validar comportamento quando dependências externas não respondem.",
                ],
            },
        )

        message = MultiAgentMessage(
            sender="functional_qa_agent",
            recipient="test_automation_agent",
            content=(
                "Estratégia funcional criada e pronta para análise de automação."
            ),
        )

        return MultiAgentTaskResult(
            agent_name="functional_qa_agent",
            status="completed",
            summary="Estratégia de testes funcionais criada.",
            artifacts=[artifact],
            messages=[message],
        )

    def _run_test_automation_agent(
        self,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentTaskResult:
        artifact = MultiAgentArtifact(
            name="test_automation_strategy",
            produced_by="test_automation_agent",
            content={
                "automation_candidates": [
                    "Automatizar o fluxo principal em nível de API ou E2E.",
                    "Automatizar validações de regras de negócio determinísticas.",
                    "Criar testes de regressão para cenários críticos.",
                ],
                "suggested_layers": [
                    "API tests",
                    "Integration tests",
                    "E2E tests where user journey validation is required",
                ],
                "implementation_notes": [
                    "Priorizar testes determinísticos e independentes.",
                    "Separar dados de teste da lógica de execução.",
                    "Evitar dependência desnecessária de ambientes instáveis.",
                ],
            },
        )

        message = MultiAgentMessage(
            sender="test_automation_agent",
            recipient="reviewer_agent",
            content=(
                "Estratégia de automação criada e pronta para revisão."
            ),
        )

        return MultiAgentTaskResult(
            agent_name="test_automation_agent",
            status="completed",
            summary="Estratégia inicial de automação criada.",
            artifacts=[artifact],
            messages=[message],
        )

    def _run_reviewer_agent(
        self,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentTaskResult:
        artifact = MultiAgentArtifact(
            name="review_findings",
            produced_by="reviewer_agent",
            content={
                "strengths": [
                    "Fluxo multiagente produziu análise funcional e estratégia de automação.",
                    "Estado compartilhado preservou artefatos intermediários.",
                ],
                "risks": [
                    "A análise ainda é determinística e não usa raciocínio LLM por agente.",
                    "Conflitos entre agentes são detectados, mas ainda não resolvidos automaticamente.",
                ],
                "recommended_improvements": [
                    "Adicionar resolução automática de conflitos.",
                    "Integrar agentes especializados com serviços reais do projeto.",
                    "Evoluir geração de relatório final com base em avaliação dos artefatos.",
                ],
            },
        )

        message = MultiAgentMessage(
            sender="reviewer_agent",
            recipient="report_agent",
            content=(
                "Revisão concluída com riscos e melhorias recomendadas."
            ),
        )

        return MultiAgentTaskResult(
            agent_name="reviewer_agent",
            status="completed",
            summary="Revisão dos artefatos multiagente concluída.",
            artifacts=[artifact],
            messages=[message],
        )

    def _run_report_agent(
        self,
        request: MultiAgentQACopilotRequest,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentTaskResult:
        artifact = MultiAgentArtifact(
            name="final_qa_report_draft",
            produced_by="report_agent",
            content={
                "summary": (
                    "Relatório final preliminar criado a partir do estado "
                    "compartilhado multiagente."
                ),
                "sections": [
                    "Requirement understanding",
                    "Functional coverage",
                    "Automation strategy",
                    "Review notes",
                    "Next steps",
                ],
            },
        )

        message = MultiAgentMessage(
            sender="report_agent",
            recipient="shared_state",
            content="Relatório final preliminar consolidado.",
        )

        return MultiAgentTaskResult(
            agent_name="report_agent",
            status="completed",
            summary="Relatório final preliminar criado.",
            artifacts=[artifact],
            messages=[message],
        )

    def _build_final_report(
        self,
        shared_state: MultiAgentSharedState,
        failures: list[MultiAgentFailureRecord],
        conflict_analysis: MultiAgentConflictAnalysisResponse,
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
        review_findings = self._find_artifact_content(
            shared_state=shared_state,
            artifact_name="review_findings",
        )

        next_steps = [
            "Integrar agentes especializados com serviços reais do projeto.",
            "Adicionar exposição MCP para o Multi-Agent QA Copilot.",
            "Evoluir agentes determinísticos para agentes com raciocínio LLM controlado.",
            "Adicionar resolução automática de conflitos.",
        ]

        if failures:
            next_steps.insert(
                0,
                "Investigar falhas capturadas durante a execução multiagente.",
            )

        if conflict_analysis.status != "passed":
            next_steps.insert(
                0,
                "Revisar conflitos detectados no estado compartilhado multiagente.",
            )

        return MultiAgentFinalReport(
            summary=(
                "Execução do Multi-Agent QA Copilot concluída com geração de "
                "análise de requisito, estratégia funcional, estratégia de "
                "automação, revisão e relatório final."
            ),
            requirement_understanding=[
                requirement_analysis.get(
                    "summary",
                    "Requirement analysis was not available.",
                ),
                *requirement_analysis.get("identified_rules", []),
            ],
            functional_coverage=[
                *functional_strategy.get("positive_scenarios", []),
                *functional_strategy.get("negative_scenarios", []),
                *functional_strategy.get("edge_cases", []),
            ],
            automation_strategy=[
                *automation_strategy.get("automation_candidates", []),
                *automation_strategy.get("suggested_layers", []),
                *automation_strategy.get("implementation_notes", []),
            ],
            review_notes=[
                *review_findings.get("strengths", []),
                *review_findings.get("risks", []),
                *review_findings.get("recommended_improvements", []),
            ],
            next_steps=next_steps,
            metadata={
                "source": "multi-agent-qa-copilot-v1",
                "artifact_count": len(shared_state.artifacts),
                "failure_count": len(failures),
                "conflict_analysis_status": conflict_analysis.status,
            },
        )

    @staticmethod
    def _resolve_status(
        task_results: list[MultiAgentTaskResult],
        failures: list[MultiAgentFailureRecord],
        conflict_analysis: MultiAgentConflictAnalysisResponse,
    ) -> str:
        completed_count = len(
            [
                task_result
                for task_result in task_results
                if task_result.status == "completed"
            ]
        )
        skipped_count = len(
            [
                task_result
                for task_result in task_results
                if task_result.status == "skipped"
            ]
        )

        if completed_count == 0:
            return "failed"

        if failures or skipped_count > 0 or conflict_analysis.status == "failed":
            return "partial"

        return "completed"

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
    def _build_requirement_excerpt(requirement_text: str) -> str:
        normalized_text = " ".join(requirement_text.split())

        if len(normalized_text) <= 180:
            return normalized_text

        return f"{normalized_text[:177]}..."
