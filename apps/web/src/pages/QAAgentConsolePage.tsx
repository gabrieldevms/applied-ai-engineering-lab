import { useMemo, useState } from "react";
import { runQAAgent } from "../api/qaAgentApi";
import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import type {
  JsonValue,
  QAAgentRunRequest,
  QAAgentRunResponse,
} from "../types/qaAgent";

type RequestState = "idle" | "loading" | "success" | "error";

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

export function QAAgentConsolePage() {
  const [requirementText, setRequirementText] = useState(defaultRequirement);
  const [language, setLanguage] = useState("pt-BR");
  const [topK, setTopK] = useState(3);
  const [maxSteps, setMaxSteps] = useState(6);
  const [advancedPayload, setAdvancedPayload] = useState(defaultAdvancedPayload);
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<QAAgentRunResponse | null>(null);

  const usedTools = useMemo(() => {
    if (!response) {
      return [];
    }

    return response.steps.map((step) => getStepTitle(step));
  }, [response]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setRequestState("loading");
    setErrorMessage(null);
    setResponse(null);

    try {
      const parsedAdvancedPayload = parseAdvancedPayload(advancedPayload);

      const payload: QAAgentRunRequest = {
        requirement_text: requirementText,
        language,
        top_k: topK,
        chunk_size: 800,
        chunk_overlap: 120,
        max_steps: maxSteps,
        ...parsedAdvancedPayload,
      };

      const result = await runQAAgent(payload);

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
        <form className="console-form-card" onSubmit={(event) => void handleSubmit(event)}>
          <div>
            <span className="eyebrow">Input</span>
            <h2>Executar QA Agent</h2>
            <p>
              Informe um requisito ou cenário de negócio. O console envia o
              payload para <code>POST /agents/qa/run</code>.
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
                    <article className="console-step-card" key={`${index}-${getStepTitle(step)}`}>
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
