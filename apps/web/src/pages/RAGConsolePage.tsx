import { useMemo, useState } from "react";
import { generateRAGAnswer, retrieveRAGContext } from "../api/ragApi";
import { recordAIRetrievalQualityTelemetry } from "../api/retrievalQualityTelemetryApi";
import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import type {
  RAGAnswerRequest,
  RAGAnswerResponse,
  RetrievalRequest,
  RetrievalResponse,
  SemanticSearchDocument,
  SourceCitation,
  VectorSearchResult,
} from "../types/rag";
import type { AIRetrievalQualityRecordRequest } from "../types/retrievalQualityTelemetry";

type RequestState = "idle" | "retrieving" | "answering" | "error";
type TelemetryState = "idle" | "recording" | "recorded" | "failed";

const defaultQuery =
  "Quais regras, riscos e cenários de teste são relevantes para a renegociação de dívida com emissão de boleto?";

const defaultDocumentsJson = `[
  {
    "source": "requirements/debt-renegotiation.md",
    "title": "Debt renegotiation requirement",
    "document_text": "Como cliente autenticado, quero renegociar uma dívida em atraso para gerar um novo acordo com parcelas, vencimento e emissão de boleto. A dívida deve estar vencida, o cliente deve estar autenticado, o acordo deve recalcular parcelas e vencimentos, e o boleto deve ser emitido após a confirmação da renegociação. O sistema deve impedir renegociação de dívida já quitada, dívida não vencida ou cliente não autenticado.",
    "metadata": {
      "domain": "banking",
      "product_area": "debt_renegotiation"
    }
  },
  {
    "source": "qa-notes/boleto-validation.md",
    "title": "Boleto validation notes",
    "document_text": "A emissão de boleto deve validar valor, vencimento, identificação do acordo, status de registro e integração com o provedor bancário. Riscos relevantes incluem divergência de valor, boleto não registrado, vencimento incorreto, falha de integração e inconsistência entre acordo e cobrança.",
    "metadata": {
      "domain": "banking",
      "topic": "boleto"
    }
  }
]`;

function parseDocumentsJson(value: string): SemanticSearchDocument[] {
  const parsedValue = JSON.parse(value) as unknown;

  if (!Array.isArray(parsedValue)) {
    throw new Error("O campo documents precisa ser um array JSON.");
  }

  const documents = parsedValue as SemanticSearchDocument[];

  if (documents.length === 0) {
    throw new Error("Informe pelo menos um documento.");
  }

  for (const document of documents) {
    if (
      !document ||
      typeof document !== "object" ||
      typeof document.source !== "string" ||
      typeof document.document_text !== "string"
    ) {
      throw new Error(
        "Cada documento precisa conter source e document_text como texto.",
      );
    }
  }

  return documents;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao executar o RAG Console.";
}

function generateConsoleRunId(operation: string): string {
  return `rag-console-${operation}-${Date.now()}-${Math.round(
    Math.random() * 10000,
  )}`;
}

function formatScore(score: number): string {
  return score.toFixed(4);
}

function getChunkTitle(chunk: VectorSearchResult): string {
  const title = chunk.metadata.title;

  if (typeof title === "string" && title.trim()) {
    return title;
  }

  const source = chunk.metadata.source;

  if (typeof source === "string" && source.trim()) {
    return source;
  }

  return chunk.record_id;
}

function getChunkSource(chunk: VectorSearchResult): string | null {
  const source = chunk.metadata.source;

  if (typeof source === "string" && source.trim()) {
    return source;
  }

  return null;
}

function getCitationTitle(citation: SourceCitation): string {
  return citation.title || citation.source;
}

function buildBasePayload(
  query: string,
  documents: SemanticSearchDocument[],
  topK: number,
  chunkSize: number,
  chunkOverlap: number,
): RetrievalRequest {
  return {
    query,
    documents,
    top_k: topK,
    chunk_size: chunkSize,
    chunk_overlap: chunkOverlap,
  };
}

function getSimilarityScores(chunks: VectorSearchResult[]): number[] {
  return chunks
    .map((chunk) => chunk.score)
    .filter((score) => Number.isFinite(score));
}

function getAverageScore(scores: number[]): number | null {
  if (scores.length === 0) {
    return null;
  }

  return Number(
    (scores.reduce((total, score) => total + score, 0) / scores.length).toFixed(
      4,
    ),
  );
}

function getUniqueSources(
  chunks: VectorSearchResult[],
  citations: SourceCitation[] = [],
): Set<string> {
  const sources = new Set<string>();

  for (const chunk of chunks) {
    const source = getChunkSource(chunk);

    if (source) {
      sources.add(source);
    }
  }

  for (const citation of citations) {
    if (citation.source.trim()) {
      sources.add(citation.source);
    }
  }

  return sources;
}

function getRequiredSources(documents: SemanticSearchDocument[]): Set<string> {
  return new Set(
    documents
      .map((document) => document.source)
      .filter((source) => source.trim().length > 0),
  );
}

function getMatchedRequiredSourceCount(
  documents: SemanticSearchDocument[],
  chunks: VectorSearchResult[],
  citations: SourceCitation[] = [],
): number {
  const requiredSources = getRequiredSources(documents);
  const retrievedSources = getUniqueSources(chunks, citations);

  return [...requiredSources].filter((source) => retrievedSources.has(source))
    .length;
}

function buildRetrievalTelemetryPayload(
  payload: RetrievalRequest,
  result: RetrievalResponse,
  runId: string,
): AIRetrievalQualityRecordRequest {
  const scores = getSimilarityScores(result.retrieved_chunks);
  const requiredSources = getRequiredSources(payload.documents);
  const uniqueSources = getUniqueSources(result.retrieved_chunks);

  return {
    component: "rag",
    operation: "rag_console_retrieve",
    query: result.query,
    requested_top_k: payload.top_k ?? result.total_retrieved_chunks,
    retrieved_chunks_count: result.total_retrieved_chunks,
    relevant_chunks_count: result.total_retrieved_chunks,
    citation_count: 0,
    unique_source_count: uniqueSources.size,
    required_source_count: requiredSources.size,
    matched_required_source_count: getMatchedRequiredSourceCount(
      payload.documents,
      result.retrieved_chunks,
    ),
    min_similarity_score: scores.length > 0 ? Math.min(...scores) : null,
    max_similarity_score: scores.length > 0 ? Math.max(...scores) : null,
    average_similarity_score: getAverageScore(scores),
    expected_min_retrieved_chunks: 1,
    expected_min_citations: 0,
    min_quality_score: 0.2,
    run_id: runId,
    metadata: {
      source: "ai-quality-command-center",
      console: "rag",
      telemetry_source: "frontend_console",
      retrieval_mode: "retrieve_context",
      document_count: payload.documents.length,
      chunk_size: payload.chunk_size ?? 0,
      chunk_overlap: payload.chunk_overlap ?? 0,
      total_indexed_chunks: result.total_indexed_chunks,
      frontend_console_run_id: runId,
    },
  };
}

function buildAnswerTelemetryPayload(
  payload: RAGAnswerRequest,
  result: RAGAnswerResponse,
  runId: string,
): AIRetrievalQualityRecordRequest {
  const scores = getSimilarityScores(result.context_chunks);
  const requiredSources = getRequiredSources(payload.documents);
  const uniqueSources = getUniqueSources(result.context_chunks, result.citations);

  return {
    component: "rag",
    operation: "rag_console_answer",
    query: result.query,
    requested_top_k: payload.top_k ?? result.total_context_chunks,
    retrieved_chunks_count: result.total_context_chunks,
    relevant_chunks_count: result.total_context_chunks,
    citation_count: result.citations.length,
    unique_source_count: uniqueSources.size,
    required_source_count: requiredSources.size,
    matched_required_source_count: getMatchedRequiredSourceCount(
      payload.documents,
      result.context_chunks,
      result.citations,
    ),
    min_similarity_score: scores.length > 0 ? Math.min(...scores) : null,
    max_similarity_score: scores.length > 0 ? Math.max(...scores) : null,
    average_similarity_score: getAverageScore(scores),
    expected_min_retrieved_chunks: 1,
    expected_min_citations: 1,
    min_quality_score: 0.2,
    run_id: runId,
    metadata: {
      source: "ai-quality-command-center",
      console: "rag",
      telemetry_source: "frontend_console",
      retrieval_mode: "answer_generation",
      provider: result.provider,
      model: result.model,
      document_count: payload.documents.length,
      chunk_size: payload.chunk_size ?? 0,
      chunk_overlap: payload.chunk_overlap ?? 0,
      language: payload.language ?? "unknown",
      answer_length: result.answer.length,
      frontend_console_run_id: runId,
    },
  };
}

function buildFailureTelemetryPayload(
  payload: RetrievalRequest | RAGAnswerRequest,
  error: unknown,
  operation: "rag_console_retrieve" | "rag_console_answer",
  runId: string,
): AIRetrievalQualityRecordRequest {
  return {
    component: "rag",
    operation,
    query: payload.query,
    requested_top_k: payload.top_k ?? 0,
    retrieved_chunks_count: 0,
    relevant_chunks_count: 0,
    citation_count: 0,
    unique_source_count: 0,
    required_source_count: payload.documents.length,
    matched_required_source_count: 0,
    min_similarity_score: null,
    max_similarity_score: null,
    average_similarity_score: null,
    expected_min_retrieved_chunks: 1,
    expected_min_citations: operation === "rag_console_answer" ? 1 : 0,
    min_quality_score: 0.2,
    run_id: runId,
    metadata: {
      source: "ai-quality-command-center",
      console: "rag",
      telemetry_source: "frontend_console",
      failure_mode: "rag_console_request_failed",
      error_message: getErrorMessage(error),
      document_count: payload.documents.length,
      chunk_size: payload.chunk_size ?? 0,
      chunk_overlap: payload.chunk_overlap ?? 0,
      frontend_console_run_id: runId,
    },
  };
}

function getTelemetryMessage(state: TelemetryState): string {
  if (state === "recording") {
    return "Registrando telemetria de retrieval quality...";
  }

  if (state === "recorded") {
    return "Telemetria registrada. A consulta RAG já pode aparecer no Histórico de Execuções.";
  }

  if (state === "failed") {
    return "A consulta foi processada, mas não foi possível registrar a telemetria de retrieval quality automaticamente.";
  }

  return "";
}

export function RAGConsolePage() {
  const [query, setQuery] = useState(defaultQuery);
  const [documentsJson, setDocumentsJson] = useState(defaultDocumentsJson);
  const [language, setLanguage] = useState("pt-BR");
  const [topK, setTopK] = useState(3);
  const [chunkSize, setChunkSize] = useState(800);
  const [chunkOverlap, setChunkOverlap] = useState(120);
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [telemetryState, setTelemetryState] = useState<TelemetryState>("idle");
  const [telemetryErrorMessage, setTelemetryErrorMessage] = useState<
    string | null
  >(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [retrievalResponse, setRetrievalResponse] =
    useState<RetrievalResponse | null>(null);
  const [answerResponse, setAnswerResponse] =
    useState<RAGAnswerResponse | null>(null);

  const documentCount = useMemo(() => {
    try {
      return parseDocumentsJson(documentsJson).length;
    } catch {
      return 0;
    }
  }, [documentsJson]);

  async function recordTelemetry(
    payload: AIRetrievalQualityRecordRequest,
  ): Promise<void> {
    setTelemetryState("recording");
    setTelemetryErrorMessage(null);

    try {
      await recordAIRetrievalQualityTelemetry(payload);
      setTelemetryState("recorded");
    } catch (error) {
      setTelemetryState("failed");
      setTelemetryErrorMessage(getErrorMessage(error));
    }
  }

  async function handleRetrieveContext() {
    setRequestState("retrieving");
    setTelemetryState("idle");
    setTelemetryErrorMessage(null);
    setErrorMessage(null);
    setRetrievalResponse(null);

    const runId = generateConsoleRunId("retrieve");
    let payload: RetrievalRequest | null = null;

    try {
      const documents = parseDocumentsJson(documentsJson);
      payload = buildBasePayload(query, documents, topK, chunkSize, chunkOverlap);

      const result = await retrieveRAGContext(payload);

      setRetrievalResponse(result);
      setRequestState("idle");

      await recordTelemetry(
        buildRetrievalTelemetryPayload(payload, result, runId),
      );
    } catch (error) {
      if (payload) {
        await recordTelemetry(
          buildFailureTelemetryPayload(payload, error, "rag_console_retrieve", runId),
        );
      }

      setRequestState("error");
      setErrorMessage(getErrorMessage(error));
    }
  }

  async function handleGenerateAnswer() {
    setRequestState("answering");
    setTelemetryState("idle");
    setTelemetryErrorMessage(null);
    setErrorMessage(null);
    setAnswerResponse(null);

    const runId = generateConsoleRunId("answer");
    let payload: RAGAnswerRequest | null = null;

    try {
      const documents = parseDocumentsJson(documentsJson);
      const basePayload = buildBasePayload(
        query,
        documents,
        topK,
        chunkSize,
        chunkOverlap,
      );

      payload = {
        ...basePayload,
        language,
      };

      const result = await generateRAGAnswer(payload);

      setAnswerResponse(result);
      setRetrievalResponse({
        query: result.query,
        total_indexed_chunks:
          typeof result.metadata.total_indexed_chunks === "number"
            ? result.metadata.total_indexed_chunks
            : result.context_chunks.length,
        total_retrieved_chunks: result.total_context_chunks,
        retrieved_chunks: result.context_chunks,
        metadata: result.metadata,
      });
      setRequestState("idle");

      await recordTelemetry(buildAnswerTelemetryPayload(payload, result, runId));
    } catch (error) {
      if (payload) {
        await recordTelemetry(
          buildFailureTelemetryPayload(payload, error, "rag_console_answer", runId),
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
          <span className="eyebrow">RAG</span>
          <h1>RAG Console</h1>
          <p>
            Execute retrieval e geração de resposta fundamentada usando
            documentos fornecidos pelo usuário, chunks recuperados, citações e
            metadata de contexto.
          </p>
        </div>
      </section>

      <section className="console-layout">
        <form className="console-form-card">
          <div>
            <span className="eyebrow">Input</span>
            <h2>Consultar base de conhecimento</h2>
            <p>
              Informe uma pergunta e documentos em JSON. O console pode chamar{" "}
              <code>POST /rag/retrieve</code> ou <code>POST /rag/answer</code> e
              registra telemetria em{" "}
              <code>POST /observability/retrieval-quality/records</code>.
            </p>
          </div>

          <label className="form-field">
            <span>Query</span>
            <textarea
              onChange={(event) => setQuery(event.target.value)}
              rows={5}
              value={query}
            />
          </label>

          <label className="form-field">
            <span>Documents JSON</span>
            <textarea
              onChange={(event) => setDocumentsJson(event.target.value)}
              rows={14}
              value={documentsJson}
            />
            <small>
              Cada documento precisa conter <code>source</code> e{" "}
              <code>document_text</code>. <code>title</code> e{" "}
              <code>metadata</code> são opcionais.
            </small>
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
              <span>Chunk size</span>
              <input
                min={100}
                max={4000}
                onChange={(event) => setChunkSize(Number(event.target.value))}
                type="number"
                value={chunkSize}
              />
            </label>

            <label className="form-field">
              <span>Chunk overlap</span>
              <input
                min={0}
                max={1000}
                onChange={(event) => setChunkOverlap(Number(event.target.value))}
                type="number"
                value={chunkOverlap}
              />
            </label>
          </div>

          <div className="console-action-row">
            <button
              className="secondary-button"
              disabled={requestState === "retrieving"}
              onClick={() => void handleRetrieveContext()}
              type="button"
            >
              {requestState === "retrieving"
                ? "Recuperando..."
                : "Retrieve context"}
            </button>

            <button
              className="primary-button"
              disabled={requestState === "answering"}
              onClick={() => void handleGenerateAnswer()}
              type="button"
            >
              {requestState === "answering"
                ? "Gerando resposta..."
                : "Generate answer"}
            </button>
          </div>
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
              <strong>Não foi possível executar o RAG Console.</strong>
              <p>
                Verifique o JSON de documentos, os parâmetros de chunking e se a
                API está rodando.
              </p>
              <small>{errorMessage}</small>
            </article>
          ) : null}

          <section className="metrics-grid">
            <MetricCard
              description="Documentos enviados para indexação temporária"
              label="Documents"
              value={documentCount}
            />
            <MetricCard
              description="Chunks indexados pelo retrieval"
              label="Indexed chunks"
              value={retrievalResponse?.total_indexed_chunks ?? 0}
            />
            <MetricCard
              description="Chunks recuperados para a query"
              label="Retrieved chunks"
              value={retrievalResponse?.total_retrieved_chunks ?? 0}
            />
            <MetricCard
              description="Citações retornadas na resposta RAG"
              label="Citations"
              value={answerResponse?.citations.length ?? 0}
            />
          </section>

          {answerResponse ? (
            <article className="console-answer-card">
              <span className="eyebrow">Grounded answer</span>
              <h2>Resposta RAG</h2>
              <p>{answerResponse.answer}</p>

              <div className="rag-provider-meta">
                <span>
                  Provider: <strong>{answerResponse.provider}</strong>
                </span>
                <span>
                  Model: <strong>{answerResponse.model}</strong>
                </span>
              </div>
            </article>
          ) : null}

          {retrievalResponse ? (
            <section className="console-steps-card">
              <div>
                <span className="eyebrow">Retrieval</span>
                <h2>Retrieved chunks</h2>
              </div>

              <div className="rag-chunk-list">
                {retrievalResponse.retrieved_chunks.map((chunk, index) => (
                  <article className="rag-chunk-card" key={chunk.record_id}>
                    <div className="rag-chunk-header">
                      <div>
                        <span className="eyebrow">Chunk {index + 1}</span>
                        <h3>{getChunkTitle(chunk)}</h3>
                      </div>

                      <span className="status-badge status-empty">
                        score {formatScore(chunk.score)}
                      </span>
                    </div>

                    <p>{chunk.text}</p>

                    <JsonViewer title="Chunk metadata" value={chunk.metadata} />
                  </article>
                ))}
              </div>
            </section>
          ) : null}

          {answerResponse ? (
            <>
              <section className="console-steps-card">
                <div>
                  <span className="eyebrow">Sources</span>
                  <h2>Citações</h2>
                </div>

                <div className="rag-citation-grid">
                  {answerResponse.citations.map((citation) => (
                    <article
                      className="rag-citation-card"
                      key={citation.citation_id}
                    >
                      <span className="eyebrow">{citation.citation_id}</span>
                      <h3>{getCitationTitle(citation)}</h3>
                      <p>{citation.excerpt}</p>

                      <small>
                        Source: {citation.source} · Chunk: {citation.chunk_id} ·
                        Score: {formatScore(citation.score)}
                      </small>
                    </article>
                  ))}
                </div>
              </section>

              <section className="content-grid">
                <JsonViewer
                  title="Answer metadata"
                  value={answerResponse.metadata}
                />

                <JsonViewer
                  title="Context chunks"
                  value={answerResponse.context_chunks}
                />
              </section>
            </>
          ) : null}

          {!retrievalResponse && !answerResponse ? (
            <section className="empty-state">
              <h2>Nenhuma consulta realizada ainda</h2>
              <p>
                Execute retrieval para ver chunks relevantes ou gere uma resposta
                RAG para visualizar resposta, fontes, citações e metadata.
              </p>
            </section>
          ) : null}
        </section>
      </section>
    </div>
  );
}
