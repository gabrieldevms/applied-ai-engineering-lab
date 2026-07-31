import { useMemo, useState } from "react";
import { generateRAGAnswer, retrieveRAGContext } from "../api/ragApi";
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

type RequestState = "idle" | "retrieving" | "answering" | "error";

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

export function RAGConsolePage() {
  const [query, setQuery] = useState(defaultQuery);
  const [documentsJson, setDocumentsJson] = useState(defaultDocumentsJson);
  const [language, setLanguage] = useState("pt-BR");
  const [topK, setTopK] = useState(3);
  const [chunkSize, setChunkSize] = useState(800);
  const [chunkOverlap, setChunkOverlap] = useState(120);
  const [requestState, setRequestState] = useState<RequestState>("idle");
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

  async function handleRetrieveContext() {
    setRequestState("retrieving");
    setErrorMessage(null);
    setRetrievalResponse(null);

    try {
      const documents = parseDocumentsJson(documentsJson);
      const payload = buildBasePayload(
        query,
        documents,
        topK,
        chunkSize,
        chunkOverlap,
      );

      const result = await retrieveRAGContext(payload);

      setRetrievalResponse(result);
      setRequestState("idle");
    } catch (error) {
      setRequestState("error");
      setErrorMessage(getErrorMessage(error));
    }
  }

  async function handleGenerateAnswer() {
    setRequestState("answering");
    setErrorMessage(null);
    setAnswerResponse(null);

    try {
      const documents = parseDocumentsJson(documentsJson);
      const basePayload = buildBasePayload(
        query,
        documents,
        topK,
        chunkSize,
        chunkOverlap,
      );

      const payload: RAGAnswerRequest = {
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
    } catch (error) {
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
              <code>POST /rag/retrieve</code> ou <code>POST /rag/answer</code>.
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
