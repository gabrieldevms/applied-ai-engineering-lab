import { useMemo, useState } from "react";
import { recordAIMultiAgentExecutionTelemetry } from "../api/multiAgentExecutionTelemetryApi";
import { runMultiAgentQACopilot } from "../api/multiAgentCopilotApi";
import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import type {
  AIMultiAgentExecutionRecordRequest,
  AIMultiAgentTelemetryRunStatus,
} from "../types/multiAgentExecutionTelemetry";
import type {
  MultiAgentFailureStrategy,
  MultiAgentFinalReport,
  MultiAgentQACopilotRequest,
  MultiAgentQACopilotResponse,
  MultiAgentStepStatus,
  MultiAgentTaskResult,
  MultiAgentTraceStep,
} from "../types/multiAgentCopilot";
import type { JsonValue } from "../types/qaAgent";

type RequestState = "idle" | "loading" | "success" | "error";
type TelemetryState = "idle" | "recording" | "recorded" | "failed";

const defaultRequirement = `Como cliente autenticado,
quero renegociar uma dívida em atraso,
para gerar um novo acordo com parcelas, vencimento e emissão de boleto.`;

const defaultObjective = `Executar um fluxo multiagente de QA para analisar o requisito, identificar riscos, propor cobertura funcional, estratégia de automação, revisão e próximos passos.`;

const defaultAdvancedPayload = `{
  "context": {
    "domain": "banking",
    "product_area": "debt_renegotiation",
    "release_type": "controlled_launch"
  },
  "data_validation": null,
  "metadata": {
    "source": "ai-quality-command-center",
    "console": "multi-agent-copilot"
  }
}`;

function parseAdvancedPayload(value: string): Partial<MultiAgentQACopilotRequest> {
  if (!value.trim()) {
    return {};
  }

  const parsedValue = JSON.parse(value) as Partial<MultiAgentQACopilotRequest>;

  if (
    parsedValue === null ||
    Array.isArray(parsedValue) ||
    typeof parsedValue !== "object"
  ) {
    throw new Error("O payload avançado precisa ser um objeto JSON.");
  }

  return parsedValue;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao executar o Multi-Agent Copilot.";
}

function generateConsoleRunId(): string {
  return `multi-agent-console-${Date.now()}-${Math.round(Math.random() * 10000)}`;
}

function mergeRequestMetadata(
  metadata: Record<string, JsonValue> | undefined,
  consoleRunId: string,
): Record<string, JsonValue> {
  return {
    ...metadata,
    source: "ai-quality-command-center",
    console: "multi-agent-copilot",
    frontend_console_run_id: consoleRunId,
  };
}

function getQualityGate(report: MultiAgentFinalReport | null): string {
  if (!report) {
    return "N/A";
  }

  const qualityGate = report.metadata.quality_gate;

  if (typeof qualityGate === "string" && qualityGate.trim()) {
    return qualityGate;
  }

  return "Não informado";
}

function getArtifactCount(taskResults: MultiAgentTaskResult[]): number {
  return taskResults.reduce((total, taskResult) => {
    return total + taskResult.artifacts.length;
  }, 0);
}

function getMessageCount(taskResults: MultiAgentTaskResult[]): number {
  return taskResults.reduce((total, taskResult) => {
    return total + taskResult.messages.length;
  }, 0);
}

function isSuccessfulTaskStatus(status: MultiAgentStepStatus): boolean {
  return ["completed", "warning"].includes(status);
}

function isFailedTaskStatus(status: MultiAgentStepStatus): boolean {
  return ["failed", "blocked"].includes(status);
}

function isSkippedTaskStatus(status: MultiAgentStepStatus): boolean {
  return status === "skipped";
}

function getFinalReportSectionCount(report: MultiAgentFinalReport): number {
  const reportSections = [
    report.summary.trim(),
    ...report.requirement_understanding,
    ...report.functional_coverage,
    ...report.automation_strategy,
    ...report.data_validation_evidence,
    ...report.review_notes,
    ...report.next_steps,
  ];

  return reportSections.filter((item) => item.trim().length > 0).length;
}

function getContractCheckCount(response: MultiAgentQACopilotResponse): number {
  return response.contract_validation?.total_contracts ?? 0;
}

function getPassedContractCheckCount(
  response: MultiAgentQACopilotResponse,
): number {
  return response.contract_validation?.passed_contracts ?? 0;
}

function getFailedContractCheckCount(
  response: MultiAgentQACopilotResponse,
): number {
  return response.contract_validation?.failed_contracts ?? 0;
}

function getConflictCount(response: MultiAgentQACopilotResponse): number {
  return response.conflict_analysis?.conflict_count ?? 0;
}

function getCriticalConflictCount(response: MultiAgentQACopilotResponse): number {
  return response.conflict_analysis?.critical_count ?? 0;
}

function mapCopilotStatusToTelemetryStatus(
  status: MultiAgentQACopilotResponse["status"],
): AIMultiAgentTelemetryRunStatus {
  if (status === "completed") {
    return "completed";
  }

  if (status === "partial") {
    return "partial";
  }

  if (status === "failed") {
    return "failed";
  }

  if (status === "blocked") {
    return "blocked";
  }

  return "partial";
}

function buildSuccessTelemetryPayload(
  request: MultiAgentQACopilotRequest,
  response: MultiAgentQACopilotResponse,
  durationMs: number,
  consoleRunId: string,
): AIMultiAgentExecutionRecordRequest {
  const successfulTaskCount = response.task_results.filter((taskResult) =>
    isSuccessfulTaskStatus(taskResult.status),
  ).length;
  const failedTaskCount = response.task_results.filter((taskResult) =>
    isFailedTaskStatus(taskResult.status),
  ).length;
  const skippedAgentCount = response.task_results.filter((taskResult) =>
    isSkippedTaskStatus(taskResult.status),
  ).length;

  const agentCount = response.roles.length;
  const completedAgentCount = successfulTaskCount;
  const failedAgentCount = failedTaskCount;
  const artifactCount = getArtifactCount(response.task_results);
  const messageCount = getMessageCount(response.task_results);
  const finalReportSectionCount = getFinalReportSectionCount(
    response.final_report,
  );
  const failureCount = response.failures.length;
  const criticalFailureCount = response.failures.filter((failure) => {
    return ["critical", "error", "high"].includes(
      failure.severity.toLowerCase(),
    );
  }).length;

  return {
    component: "multi_agent",
    operation: "multi_agent_copilot_console_run",
    workflow_name: response.copilot_name || "multi-agent-qa-copilot-v1",
    run_status: mapCopilotStatusToTelemetryStatus(response.status),
    duration_ms: Math.round(durationMs),

    agent_count: agentCount,
    completed_agent_count: completedAgentCount,
    failed_agent_count: failedAgentCount,
    skipped_agent_count: skippedAgentCount,

    task_count: response.task_results.length,
    successful_task_count: successfulTaskCount,
    failed_task_count: failedTaskCount,

    artifact_count: artifactCount,
    expected_min_artifacts: Math.max(1, response.task_results.length),

    handoff_count: messageCount,
    failed_handoff_count: 0,

    contract_check_count: getContractCheckCount(response),
    passed_contract_check_count: getPassedContractCheckCount(response),
    failed_contract_check_count: getFailedContractCheckCount(response),

    conflict_count: getConflictCount(response),
    critical_conflict_count: getCriticalConflictCount(response),

    failure_count: failureCount,
    error_count: criticalFailureCount,

    final_report_section_count: finalReportSectionCount,
    expected_min_final_report_sections: 4,

    data_validation_evidence_count:
      response.final_report.data_validation_evidence.length,
    require_data_validation_evidence: Boolean(request.data_validation),

    retry_count: 0,
    fallback_count: response.status === "partial" ? 1 : 0,

    max_failed_agents: 0,
    max_failed_tasks: 0,
    max_failed_handoffs: 0,
    max_failed_contract_checks: 0,
    max_critical_conflicts: 0,
    max_failures: 0,
    max_errors: 0,
    min_quality_score: 0.7,

    run_id: consoleRunId,
    metadata: {
      source: "ai-quality-command-center",
      console: "multi-agent-copilot",
      telemetry_source: "frontend_console",
      response_status: response.status,
      quality_gate: getQualityGate(response.final_report),
      requirement_length: request.requirement_text.length,
      objective_length: request.objective?.length ?? 0,
      language: request.language ?? "unknown",
      max_agents: request.max_agents ?? 0,
      failure_strategy: request.failure_strategy ?? "unknown",
      frontend_console_run_id: consoleRunId,
    },
  };
}

function buildFailureTelemetryPayload(
  request: MultiAgentQACopilotRequest,
  error: unknown,
  durationMs: number,
  consoleRunId: string,
): AIMultiAgentExecutionRecordRequest {
  return {
    component: "multi_agent",
    operation: "multi_agent_copilot_console_run",
    workflow_name: "multi-agent-qa-copilot-v1",
    run_status: "failed",
    duration_ms: Math.round(durationMs),

    agent_count: request.max_agents ?? 0,
    completed_agent_count: 0,
    failed_agent_count: 0,
    skipped_agent_count: 0,

    task_count: 0,
    successful_task_count: 0,
    failed_task_count: 0,

    artifact_count: 0,
    expected_min_artifacts: 0,

    handoff_count: 0,
    failed_handoff_count: 0,

    contract_check_count: 0,
    passed_contract_check_count: 0,
    failed_contract_check_count: 0,

    conflict_count: 0,
    critical_conflict_count: 0,

    failure_count: 1,
    error_count: 1,

    final_report_section_count: 0,
    expected_min_final_report_sections: 0,

    data_validation_evidence_count: 0,
    require_data_validation_evidence: Boolean(request.data_validation),

    retry_count: 0,
    fallback_count: 0,

    max_failed_agents: 0,
    max_failed_tasks: 0,
    max_failed_handoffs: 0,
    max_failed_contract_checks: 0,
    max_critical_conflicts: 0,
    max_failures: 0,
    max_errors: 0,
    min_quality_score: 0.7,

    run_id: consoleRunId,
    metadata: {
      source: "ai-quality-command-center",
      console: "multi-agent-copilot",
      telemetry_source: "frontend_console",
      failure_mode: "multi_agent_copilot_console_request_failed",
      error_message: getErrorMessage(error),
      requirement_length: request.requirement_text.length,
      objective_length: request.objective?.length ?? 0,
      language: request.language ?? "unknown",
      max_agents: request.max_agents ?? 0,
      failure_strategy: request.failure_strategy ?? "unknown",
      frontend_console_run_id: consoleRunId,
    },
  };
}

function getTelemetryMessage(state: TelemetryState): string {
  if (state === "recording") {
    return "Registrando telemetria da execução multiagente...";
  }

  if (state === "recorded") {
    return "Telemetria registrada. A execução multiagente já pode aparecer no Histórico de Execuções.";
  }

  if (state === "failed") {
    return "A execução foi processada, mas não foi possível registrar a telemetria multiagente automaticamente.";
  }

  return "";
}

function formatListItems(items: string[]) {
  if (items.length === 0) {
    return <p className="muted">Nenhum item retornado.</p>;
  }

  return (
    <ul>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function formatStatusLabel(status: string): string {
  return status.replaceAll("_", " ");
}

function renderTraceStep(step: MultiAgentTraceStep, index: number) {
  return (
    <article className="copilot-trace-card" key={`${index}-${step.step_name}`}>
      <div>
        <span className="eyebrow">Step {index + 1}</span>
        <h3>{step.step_name}</h3>
        <p>{step.summary}</p>
      </div>

      <div className="copilot-trace-meta">
        <strong>{step.agent_name}</strong>
        <span>{formatStatusLabel(step.status)}</span>
      </div>
    </article>
  );
}

export function MultiAgentCopilotConsolePage() {
  const [requirementText, setRequirementText] = useState(defaultRequirement);
  const [objective, setObjective] = useState(defaultObjective);
  const [language, setLanguage] = useState("pt-BR");
  const [maxAgents, setMaxAgents] = useState(6);
  const [failureStrategy, setFailureStrategy] =
    useState<MultiAgentFailureStrategy>("stop_on_failure");
  const [advancedPayload, setAdvancedPayload] = useState(defaultAdvancedPayload);
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [telemetryState, setTelemetryState] = useState<TelemetryState>("idle");
  const [telemetryErrorMessage, setTelemetryErrorMessage] = useState<
    string | null
  >(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<MultiAgentQACopilotResponse | null>(
    null,
  );

  const qualityGate = useMemo(() => {
    return getQualityGate(response?.final_report ?? null);
  }, [response]);

  async function recordTelemetry(
    payload: AIMultiAgentExecutionRecordRequest,
  ): Promise<void> {
    setTelemetryState("recording");
    setTelemetryErrorMessage(null);

    try {
      await recordAIMultiAgentExecutionTelemetry(payload);
      setTelemetryState("recorded");
    } catch (error) {
      setTelemetryState("failed");
      setTelemetryErrorMessage(getErrorMessage(error));
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setRequestState("loading");
    setTelemetryState("idle");
    setTelemetryErrorMessage(null);
    setErrorMessage(null);
    setResponse(null);

    let payload: MultiAgentQACopilotRequest | null = null;
    let startedAt = 0;
    const consoleRunId = generateConsoleRunId();

    try {
      const parsedAdvancedPayload = parseAdvancedPayload(advancedPayload);

      payload = {
        requirement_text: requirementText,
        objective,
        language,
        max_agents: maxAgents,
        failure_strategy: failureStrategy,
        ...parsedAdvancedPayload,
        metadata: mergeRequestMetadata(
          parsedAdvancedPayload.metadata,
          consoleRunId,
        ),
      };

      startedAt = performance.now();

      const result = await runMultiAgentQACopilot(payload);
      const durationMs = performance.now() - startedAt;

      setResponse(result);
      setRequestState("success");

      await recordTelemetry(
        buildSuccessTelemetryPayload(
          payload,
          result,
          durationMs,
          consoleRunId,
        ),
      );
    } catch (error) {
      const durationMs = startedAt > 0 ? performance.now() - startedAt : 0;

      if (payload && startedAt > 0) {
        await recordTelemetry(
          buildFailureTelemetryPayload(
            payload,
            error,
            durationMs,
            consoleRunId,
          ),
        );
      }

      setRequestState("error");
      setErrorMessage(getErrorMessage(error));
    }
  }

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Multi-Agent</span>
          <h1>Multi-Agent Copilot Console</h1>
          <p>
            Execute o QA Copilot multiagente para coordenar papéis
            especializados, gerar artefatos, validar contratos, consolidar
            riscos e produzir um relatório final de qualidade.
          </p>
        </div>
      </section>

      <section className="console-layout">
        <form
          className="console-form-card"
          onSubmit={(event) => void handleSubmit(event)}
        >
          <div>
            <span className="eyebrow">Input</span>
            <h2>Executar Multi-Agent Copilot</h2>
            <p>
              Informe o requisito e o objetivo do fluxo. O console envia o
              payload para <code>POST /multi-agent/qa-copilot/run</code> e
              registra telemetria em{" "}
              <code>POST /observability/multi-agent-execution/records</code>.
            </p>
          </div>

          <label className="form-field">
            <span>Requirement text</span>
            <textarea
              onChange={(event) => setRequirementText(event.target.value)}
              rows={7}
              value={requirementText}
            />
          </label>

          <label className="form-field">
            <span>Objective</span>
            <textarea
              onChange={(event) => setObjective(event.target.value)}
              rows={5}
              value={objective}
            />
          </label>

          <div className="form-grid">
            <label className="form-field">
              <span>Language</span>
              <input
                onChange={(event) => setLanguage(event.target.value)}
                value={language}
              />
            </label>

            <label className="form-field">
              <span>Max agents</span>
              <input
                min={1}
                max={6}
                onChange={(event) => setMaxAgents(Number(event.target.value))}
                type="number"
                value={maxAgents}
              />
            </label>

            <label className="form-field">
              <span>Failure strategy</span>
              <select
                onChange={(event) =>
                  setFailureStrategy(
                    event.target.value as MultiAgentFailureStrategy,
                  )
                }
                value={failureStrategy}
              >
                <option value="stop_on_failure">stop_on_failure</option>
                <option value="continue_with_warnings">
                  continue_with_warnings
                </option>
              </select>
            </label>
          </div>

          <label className="form-field">
            <span>Advanced payload JSON</span>
            <textarea
              onChange={(event) => setAdvancedPayload(event.target.value)}
              rows={10}
              value={advancedPayload}
            />
            <small>
              Use este campo para enviar <code>context</code>,{" "}
              <code>data_validation</code> e <code>metadata</code> sem limitar o
              console aos campos básicos.
            </small>
          </label>

          <button
            className="primary-button"
            disabled={requestState === "loading"}
            type="submit"
          >
            {requestState === "loading"
              ? "Executando..."
              : "Run Multi-Agent Copilot"}
          </button>
        </form>

        <section className="console-result-stack">
          {telemetryState !== "idle" ? (
            <article
              className={
                telemetryState === "failed" ? "alert-card" : "empty-state"
              }
            >
              <strong>{getTelemetryMessage(telemetryState)}</strong>
              {telemetryErrorMessage ? (
                <small>{telemetryErrorMessage}</small>
              ) : null}
            </article>
          ) : null}

          {requestState === "error" ? (
            <article className="alert-card">
              <strong>Não foi possível executar o Multi-Agent Copilot.</strong>
              <p>
                Verifique o payload enviado, se a API está rodando e se o
                endpoint <code>/multi-agent/qa-copilot/run</code> está
                disponível.
              </p>
              <small>{errorMessage}</small>
            </article>
          ) : null}

          {response ? (
            <>
              <section className="metrics-grid">
                <MetricCard
                  description="Status consolidado do copilot"
                  label="Status"
                  value={response.status}
                />
                <MetricCard
                  description="Gate de qualidade retornado no relatório"
                  label="Quality gate"
                  value={qualityGate}
                />
                <MetricCard
                  description="Papéis especializados executados"
                  label="Roles"
                  value={response.roles.length}
                />
                <MetricCard
                  description="Steps registrados no trace"
                  label="Trace"
                  value={response.trace.length}
                />
              </section>

              <section className="metrics-grid">
                <MetricCard
                  description="Resultados de tarefas dos agentes"
                  label="Tasks"
                  value={response.task_results.length}
                />
                <MetricCard
                  description="Artefatos produzidos pelos agentes"
                  label="Artifacts"
                  value={getArtifactCount(response.task_results)}
                />
                <MetricCard
                  description="Mensagens trocadas entre agentes"
                  label="Messages"
                  value={getMessageCount(response.task_results)}
                />
                <MetricCard
                  description="Falhas registradas no fluxo"
                  label="Failures"
                  value={response.failures.length}
                />
              </section>

              <article className="console-answer-card">
                <span className="eyebrow">Final report</span>
                <h2>{response.copilot_name}</h2>
                <p>{response.final_report.summary}</p>
              </article>

              <section className="copilot-report-grid">
                <article className="insight-card">
                  <h2>Entendimento do requisito</h2>
                  {formatListItems(
                    response.final_report.requirement_understanding,
                  )}
                </article>

                <article className="insight-card">
                  <h2>Cobertura funcional</h2>
                  {formatListItems(response.final_report.functional_coverage)}
                </article>

                <article className="insight-card">
                  <h2>Estratégia de automação</h2>
                  {formatListItems(response.final_report.automation_strategy)}
                </article>

                <article className="insight-card">
                  <h2>Evidências de dados</h2>
                  {formatListItems(
                    response.final_report.data_validation_evidence,
                  )}
                </article>

                <article className="insight-card">
                  <h2>Review notes</h2>
                  {formatListItems(response.final_report.review_notes)}
                </article>

                <article className="insight-card">
                  <h2>Next steps</h2>
                  {formatListItems(response.final_report.next_steps)}
                </article>
              </section>

              <section className="copilot-role-grid">
                {response.roles.map((role) => (
                  <article className="copilot-role-card" key={role.name}>
                    <span className="eyebrow">{role.name}</span>
                    <h3>{role.title}</h3>
                    <p>{role.responsibility}</p>
                  </article>
                ))}
              </section>

              <section className="console-steps-card">
                <div>
                  <span className="eyebrow">Tasks</span>
                  <h2>Resultados dos agentes</h2>
                </div>

                <div className="console-step-list">
                  {response.task_results.map((taskResult) => (
                    <article
                      className="console-step-card"
                      key={taskResult.agent_name}
                    >
                      <div>
                        <span className="eyebrow">{taskResult.agent_name}</span>
                        <h3>{formatStatusLabel(taskResult.status)}</h3>
                        <p>{taskResult.summary}</p>
                      </div>

                      <span className="status-badge status-empty">
                        {taskResult.artifacts.length} artifacts
                      </span>

                      <pre>{JSON.stringify(taskResult, null, 2)}</pre>
                    </article>
                  ))}
                </div>
              </section>

              <section className="console-steps-card">
                <div>
                  <span className="eyebrow">Trace</span>
                  <h2>Fluxo de execução</h2>
                </div>

                <div className="copilot-trace-list">
                  {response.trace.map((step, index) =>
                    renderTraceStep(step, index),
                  )}
                </div>
              </section>

              <section className="content-grid">
                <JsonViewer
                  title="Contract validation"
                  value={response.contract_validation}
                  emptyMessage="Nenhuma validação de contrato foi retornada."
                />

                <JsonViewer
                  title="Conflict analysis"
                  value={response.conflict_analysis}
                  emptyMessage="Nenhuma análise de conflito foi retornada."
                />
              </section>

              <section className="content-grid">
                <JsonViewer
                  title="Failures"
                  value={response.failures}
                  emptyMessage="Nenhuma falha foi registrada."
                />

                <JsonViewer
                  title="Shared state"
                  value={response.shared_state}
                />
              </section>

              <JsonViewer title="Metadata" value={response.metadata} />
            </>
          ) : (
            <section className="empty-state">
              <h2>Nenhuma execução realizada ainda</h2>
              <p>
                Preencha o requisito e execute o Multi-Agent Copilot para
                visualizar relatório final, roles, artifacts, trace, contratos,
                conflitos e metadata.
              </p>
            </section>
          )}
        </section>
      </section>
    </div>
  );
}
