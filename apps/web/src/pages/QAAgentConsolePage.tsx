import { useMemo, useState } from "react";
import { recordAIAgentExecutionTelemetry } from "../api/agentExecutionTelemetryApi";
import { runQAAgent } from "../api/qaAgentApi";
import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import type {
  AIAgentExecutionRecordRequest,
  AIAgentTelemetryRunStatus,
} from "../types/agentExecutionTelemetry";
import type {
  AgentStep,
  JsonValue,
  QAAgentRunRequest,
  QAAgentRunResponse,
} from "../types/qaAgent";

type RequestState = "idle" | "loading" | "success" | "error";
type TelemetryState = "idle" | "recording" | "recorded" | "failed";

const defaultRequirement = `Como cliente autenticado,
quero renegociar uma dívida em atraso,
para gerar um novo acordo com parcelas, vencimento e emissão de boleto.`;

const defaultAdvancedPayload = `{
  "knowledge_documents": [],
  "data_validation": null,
  "metadata": {
    "source": "ai-quality-command-center",
    "console": "qa-agent"
  }
}`;

function parseAdvancedPayload(value: string): Partial<QAAgentRunRequest> {
  if (!value.trim()) {
    return {};
  }

  const parsedValue = JSON.parse(value) as Partial<QAAgentRunRequest>;

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

  return "Erro inesperado ao executar o QA Agent.";
}

function getStepTitle(step: Record<string, JsonValue | undefined>): string {
  const toolName = step.tool_name;

  if (typeof toolName === "string" && toolName.trim()) {
    return toolName;
  }

  const name = step.name;

  if (typeof name === "string" && name.trim()) {
    return name;
  }

  const stepId = step.step_id;

  if (typeof stepId === "string" && stepId.trim()) {
    return stepId;
  }

  return "step";
}

function getStepStatus(step: Record<string, JsonValue | undefined>): string {
  const status = step.status;

  if (typeof status === "string" && status.trim()) {
    return status;
  }

  return "unknown";
}

function isFailedStep(step: AgentStep): boolean {
  const status = getStepStatus(step).toLowerCase();

  return ["failed", "error", "blocked"].includes(status);
}

function hasToolCall(step: AgentStep): boolean {
  return typeof step.tool_name === "string" && step.tool_name.trim().length > 0;
}

function mapAgentStatusToTelemetryStatus(
  status: QAAgentRunResponse["status"],
): AIAgentTelemetryRunStatus {
  if (status === "completed") {
    return "completed";
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
  request: QAAgentRunRequest,
  response: QAAgentRunResponse,
  durationMs: number,
): AIAgentExecutionRecordRequest {
  const failedSteps = response.steps.filter(isFailedStep);
  const toolSteps = response.steps.filter(hasToolCall);
  const failedToolSteps = toolSteps.filter(isFailedStep);

  return {
    component: "agent",
    operation: "qa_agent_console_run",
    agent_name: "qa-agent-v1",
    run_status: mapAgentStatusToTelemetryStatus(response.status),
    duration_ms: Math.round(durationMs),
    step_count: response.steps.length,
    successful_step_count: response.steps.length - failedSteps.length,
    failed_step_count: failedSteps.length,
    tool_call_count: toolSteps.length,
    successful_tool_call_count: toolSteps.length - failedToolSteps.length,
    failed_tool_call_count: failedToolSteps.length,
    retry_count: 0,
    fallback_count: 0,
    error_count: failedSteps.length,
    human_approval_request_count:
      response.status === "requires_approval" ? 1 : 0,
    human_approval_granted_count: 0,
    max_failed_steps: 0,
    max_failed_tool_calls: 0,
    max_error_count: 0,
    min_quality_score: 0.7,
    run_id: response.run_id,
    metadata: {
      source: "ai-quality-command-center",
      console: "qa-agent",
      telemetry_source: "frontend_console",
      response_status: response.status,
      requirement_length: request.requirement_text.length,
      language: request.language ?? "unknown",
      top_k: request.top_k ?? 0,
      max_steps: request.max_steps ?? 0,
    },
  };
}

function buildFailureTelemetryPayload(
  request: QAAgentRunRequest,
  error: unknown,
  durationMs: number,
): AIAgentExecutionRecordRequest {
  return {
    component: "agent",
    operation: "qa_agent_console_run",
    agent_name: "qa-agent-v1",
    run_status: "failed",
    duration_ms: Math.round(durationMs),
    step_count: 0,
    successful_step_count: 0,
    failed_step_count: 0,
    tool_call_count: 0,
    successful_tool_call_count: 0,
    failed_tool_call_count: 0,
    retry_count: 0,
    fallback_count: 0,
    error_count: 1,
    human_approval_request_count: 0,
    human_approval_granted_count: 0,
    max_failed_steps: 0,
    max_failed_tool_calls: 0,
    max_error_count: 0,
    min_quality_score: 0.7,
    run_id: null,
    metadata: {
      source: "ai-quality-command-center",
      console: "qa-agent",
      telemetry_source: "frontend_console",
      failure_mode: "qa_agent_console_request_failed",
      error_message: getErrorMessage(error),
      requirement_length: request.requirement_text.length,
      language: request.language ?? "unknown",
      top_k: request.top_k ?? 0,
      max_steps: request.max_steps ?? 0,
    },
  };
}

function getTelemetryMessage(state: TelemetryState): string {
  if (state === "recording") {
    return "Registrando telemetria da execução...";
  }

  if (state === "recorded") {
    return "Telemetria registrada. A execução já pode aparecer no Histórico de Execuções.";
  }

  if (state === "failed") {
    return "A execução foi processada, mas não foi possível registrar a telemetria automaticamente.";
  }

  return "";
}

export function QAAgentConsolePage() {
  const [requirementText, setRequirementText] = useState(defaultRequirement);
  const [language, setLanguage] = useState("pt-BR");
  const [topK, setTopK] = useState(3);
  const [maxSteps, setMaxSteps] = useState(6);
  const [advancedPayload, setAdvancedPayload] = useState(defaultAdvancedPayload);
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [telemetryState, setTelemetryState] = useState<TelemetryState>("idle");
  const [telemetryErrorMessage, setTelemetryErrorMessage] = useState<
    string | null
  >(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<QAAgentRunResponse | null>(null);

  const usedTools = useMemo(() => {
    if (!response) {
      return [];
    }

    return response.steps.map((step) => getStepTitle(step));
  }, [response]);

  async function recordTelemetry(
    payload: AIAgentExecutionRecordRequest,
  ): Promise<void> {
    setTelemetryState("recording");
    setTelemetryErrorMessage(null);

    try {
      await recordAIAgentExecutionTelemetry(payload);
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

    let payload: QAAgentRunRequest | null = null;
    let startedAt = 0;

    try {
      const parsedAdvancedPayload = parseAdvancedPayload(advancedPayload);

      payload = {
        requirement_text: requirementText,
        language,
        top_k: topK,
        chunk_size: 800,
        chunk_overlap: 120,
        max_steps: maxSteps,
        ...parsedAdvancedPayload,
      };

      startedAt = performance.now();

      const result = await runQAAgent(payload);
      const durationMs = performance.now() - startedAt;

      setResponse(result);
      setRequestState("success");

      await recordTelemetry(
        buildSuccessTelemetryPayload(payload, result, durationMs),
      );
    } catch (error) {
      const durationMs =
        startedAt > 0 ? performance.now() - startedAt : 0;

      if (payload && startedAt > 0) {
        await recordTelemetry(
          buildFailureTelemetryPayload(payload, error, durationMs),
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
          <span className="eyebrow">Agent Console</span>
          <h1>QA Agent Console</h1>
          <p>
            Execute o QA Agent para analisar requisitos, identificar riscos,
            gerar sinais de qualidade, consultar contexto via RAG e acionar
            validação de dados quando aplicável.
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
            <h2>Executar QA Agent</h2>
            <p>
              Informe um requisito ou cenário de negócio. O console envia o
              payload para <code>POST /agents/qa/run</code> e registra
              telemetria em{" "}
              <code>POST /observability/agent-execution/records</code>.
            </p>
          </div>

          <label className="form-field">
            <span>Requirement text</span>
            <textarea
              onChange={(event) => setRequirementText(event.target.value)}
              rows={8}
              value={requirementText}
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
              <span>Top K</span>
              <input
                min={1}
                max={20}
                onChange={(event) => setTopK(Number(event.target.value))}
                type="number"
                value={topK}
              />
            </label>

            <label className="form-field">
              <span>Max steps</span>
              <input
                min={1}
                max={20}
                onChange={(event) => setMaxSteps(Number(event.target.value))}
                type="number"
                value={maxSteps}
              />
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
              Use este campo para enviar <code>knowledge_documents</code>,{" "}
              <code>data_validation</code> e <code>metadata</code> sem limitar o
              console aos campos básicos.
            </small>
          </label>

          <button
            className="primary-button"
            disabled={requestState === "loading"}
            type="submit"
          >
            {requestState === "loading" ? "Executando..." : "Run QA Agent"}
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
              {telemetryErrorMessage ? <small>{telemetryErrorMessage}</small> : null}
            </article>
          ) : null}

          {requestState === "error" ? (
            <article className="alert-card">
              <strong>Não foi possível executar o QA Agent.</strong>
              <p>
                Verifique o payload enviado, se a API está rodando e se o
                endpoint <code>/agents/qa/run</code> está disponível.
              </p>
              <small>{errorMessage}</small>
            </article>
          ) : null}

          {response ? (
            <>
              <section className="metrics-grid">
                <MetricCard
                  description="Identificador da execução"
                  label="Run ID"
                  value={response.run_id}
                />
                <MetricCard
                  description="Status retornado pelo agent runtime"
                  label="Status"
                  value={response.status}
                />
                <MetricCard
                  description="Quantidade de steps executados"
                  label="Steps"
                  value={response.steps.length}
                />
                <MetricCard
                  description="Ferramentas acionadas durante a execução"
                  label="Tools"
                  value={new Set(usedTools).size}
                />
              </section>

              <article className="console-answer-card">
                <span className="eyebrow">Final answer</span>
                <h2>Resposta do QA Agent</h2>
                <p>{response.final_answer}</p>
              </article>

              <section className="content-grid">
                <JsonViewer
                  title="Requirement analysis"
                  value={response.requirement_analysis}
                />

                <JsonViewer
                  title="Retrieved context"
                  value={response.retrieved_context}
                  emptyMessage="Nenhum contexto RAG foi retornado."
                />
              </section>

              <section className="content-grid">
                <JsonViewer
                  title="Data validation selection"
                  value={response.data_validation_selection}
                  emptyMessage="Nenhuma decisão de validação de dados foi retornada."
                />

                <JsonViewer
                  title="Data validation"
                  value={response.data_validation}
                  emptyMessage="Nenhuma validação de dados foi executada."
                />
              </section>

              <section className="console-steps-card">
                <div>
                  <span className="eyebrow">Trace</span>
                  <h2>Execution steps</h2>
                </div>

                <div className="console-step-list">
                  {response.steps.map((step, index) => (
                    <article
                      className="console-step-card"
                      key={`${index}-${getStepTitle(step)}`}
                    >
                      <div>
                        <span className="eyebrow">Step {index + 1}</span>
                        <h3>{getStepTitle(step)}</h3>
                      </div>

                      <span className="status-badge status-empty">
                        {getStepStatus(step)}
                      </span>

                      <pre>{JSON.stringify(step, null, 2)}</pre>
                    </article>
                  ))}
                </div>
              </section>

              <JsonViewer title="Metadata" value={response.metadata} />
            </>
          ) : (
            <section className="empty-state">
              <h2>Nenhuma execução realizada ainda</h2>
              <p>
                Preencha o requisito e execute o QA Agent para visualizar a
                análise, o trace, as ferramentas usadas e as evidências
                retornadas.
              </p>
            </section>
          )}
        </section>
      </section>
    </div>
  );
}
