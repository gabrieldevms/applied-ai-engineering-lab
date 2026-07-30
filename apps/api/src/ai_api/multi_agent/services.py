from typing import Any
from ai_api.multi_agent.roles import build_default_multi_agent_roles
from ai_api.multi_agent.schemas import (
    MultiAgentArtifact,
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
    ) -> None:
        self.roles = roles if roles is not None else build_default_multi_agent_roles()

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
                "source": "multi-agent-qa-copilot-v1",
                **request.metadata,
            },
        )

        selected_roles = self.roles[: request.max_agents]
        task_results: list[MultiAgentTaskResult] = []
        trace: list[MultiAgentTraceStep] = []

        for role in selected_roles:
            task_result = self._run_role(
                role_name=role.name,
                request=request,
                shared_state=shared_state,
            )

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

        final_report = self._build_final_report(shared_state)

        return MultiAgentQACopilotResponse(
            status="completed",
            copilot_name="multi-agent-qa-copilot-v1",
            objective=objective,
            roles=selected_roles,
            shared_state=shared_state,
            task_results=task_results,
            final_report=final_report,
            trace=trace,
            metadata={
                "execution_mode": "deterministic_foundation",
                "agent_count": len(selected_roles),
                "artifact_count": len(shared_state.artifacts),
                "message_count": len(shared_state.messages),
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
            recipient="shared_state",
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
                    "Conflitos entre agentes ainda não são tratados nesta fundação.",
                ],
                "recommended_improvements": [
                    "Adicionar contratos explícitos de comunicação entre agentes.",
                    "Adicionar tratamento de falhas e conflitos.",
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
            next_steps=[
                "Adicionar contratos formais de comunicação entre agentes.",
                "Adicionar tratamento de conflitos e falhas.",
                "Integrar agentes especializados com serviços reais do projeto.",
                "Adicionar endpoint HTTP e futura exposição MCP para o copilot.",
            ],
            metadata={
                "source": "multi-agent-qa-copilot-v1",
                "artifact_count": len(shared_state.artifacts),
            },
        )

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
