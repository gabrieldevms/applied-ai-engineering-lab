import { useMemo, useState } from "react";
import { runMultiAgentQACopilot } from "../api/multiAgentCopilotApi";
import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import type {
  MultiAgentFailureStrategy,
  MultiAgentFinalReport,
  MultiAgentQACopilotRequest,
  MultiAgentQACopilotResponse,
  MultiAgentTaskResult,
  MultiAgentTraceStep,
} from "../types/multiAgentCopilot";

type RequestState = "idle" | "loading" | "success" | "error";

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
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<MultiAgentQACopilotResponse | null>(
    null,
  );

  const qualityGate = useMemo(() => {
    return getQualityGate(response?.final_report ?? null);
  }, [response]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setRequestState("loading");
    setErrorMessage(null);
    setResponse(null);

    try {
      const parsedAdvancedPayload = parseAdvancedPayload(advancedPayload);

      const payload: MultiAgentQACopilotRequest = {
        requirement_text: requirementText,
        objective,
        language,
        max_agents: maxAgents,
        failure_strategy: failureStrategy,
        ...parsedAdvancedPayload,
      };

      const result = await runMultiAgentQACopilot(payload);

      setResponse(result);
      setRequestState("success");
    } catch (error) {
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
        <form className="console-form-card" onSubmit={(event) => void handleSubmit(event)}>
          <div>
            <span className="eyebrow">Input</span>
            <h2>Executar Multi-Agent Copilot</h2>
            <p>
              Informe o requisito e o objetivo do fluxo. O console envia o
              payload para <code>POST /multi-agent/qa-copilot/run</code>.
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
