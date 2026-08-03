import { useMemo, useState } from "react";
import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useExecutionHistory } from "../hooks/useExecutionHistory";
import type {
  AIExecutionHistoryRecord,
  ExecutionHistoryFilters,
  ExecutionHistoryType,
} from "../types/executionHistory";
import type { DashboardStatus } from "../types/observability";

const executionTypeLabels: Record<ExecutionHistoryType, string> = {
  evaluation_telemetry: "Telemetria de avaliação",
  usage: "Uso e custos",
  retrieval_quality: "Qualidade de recuperação",
  agent_execution: "Execução de agente",
  multi_agent_execution: "Execução multiagente",
};

const statusBadgeMap: Record<string, DashboardStatus> = {
  passed: "healthy",
  completed: "healthy",
  recorded: "healthy",
  warning: "warning",
  failed: "critical",
  blocked: "critical",
  cancelled: "critical",
};

type JsonViewerValue =
  | string
  | number
  | boolean
  | null
  | JsonViewerValue[]
  | { [key: string]: JsonViewerValue };

function formatExecutionType(type: string): string {
  return (
    executionTypeLabels[type as ExecutionHistoryType] ??
    type.replaceAll("_", " ")
  );
}

function formatDateTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(date);
}

function formatDuration(value?: number | null): string {
  if (value === null || value === undefined) {
    return "N/A";
  }

  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)}s`;
  }

  return `${value.toFixed(0)}ms`;
}

function formatQualityScore(value?: number | null): string {
  if (value === null || value === undefined) {
    return "N/A";
  }

  return `${Math.round(value * 100)}%`;
}

function toBadgeStatus(status: string): DashboardStatus {
  return statusBadgeMap[status] ?? "warning";
}

function getLatestRecordedAt(records: AIExecutionHistoryRecord[]): string {
  if (records.length === 0) {
    return "Sem registros";
  }

  return formatDateTime(records[0].recorded_at);
}

function getAverageQuality(records: AIExecutionHistoryRecord[]): string {
  const qualityScores = records
    .map((record) => record.quality_score)
    .filter((value): value is number => value !== null && value !== undefined);

  if (qualityScores.length === 0) {
    return "N/A";
  }

  const average =
    qualityScores.reduce((total, value) => total + value, 0) /
    qualityScores.length;

  return `${Math.round(average * 100)}%`;
}

function toJsonViewerValue(value: unknown): JsonViewerValue {
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }

  if (Array.isArray(value)) {
    return value.map((item) => toJsonViewerValue(item));
  }

  if (typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => [
        key,
        toJsonViewerValue(item),
      ]),
    );
  }

  return String(value);
}

function renderRecordsTable(
  records: AIExecutionHistoryRecord[],
  selectedExecutionId: string | null,
  onSelectRecord: (record: AIExecutionHistoryRecord) => void,
) {
  if (records.length === 0) {
    return (
      <article className="execution-history-empty">
        <h2>Nenhuma execução encontrada</h2>
        <p>
          Registre eventos de observabilidade ou ajuste os filtros para
          visualizar o histórico unificado de execuções.
        </p>
      </article>
    );
  }

  return (
    <div className="execution-history-table-wrapper">
      <table className="execution-history-table">
        <thead>
          <tr>
            <th>Quando</th>
            <th>Tipo</th>
            <th>Status</th>
            <th>Componente</th>
            <th>Operação</th>
            <th>Qualidade</th>
            <th>Duração</th>
            <th>Resumo</th>
            <th>Detalhes</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record) => (
            <tr
              className={
                record.execution_id === selectedExecutionId
                  ? "execution-history-row is-selected"
                  : "execution-history-row"
              }
              key={record.execution_id}
            >
              <td>{formatDateTime(record.recorded_at)}</td>
              <td>{formatExecutionType(record.execution_type)}</td>
              <td>
                <StatusBadge status={toBadgeStatus(record.status)} />
                <span className="execution-history-status-text">
                  {record.status}
                </span>
              </td>
              <td>{record.component}</td>
              <td>{record.operation}</td>
              <td>{formatQualityScore(record.quality_score)}</td>
              <td>{formatDuration(record.duration_ms)}</td>
              <td>
                <strong>{record.title}</strong>
                <p>{record.summary}</p>
                {record.run_id ? (
                  <code className="execution-history-run-id">
                    run_id: {record.run_id}
                  </code>
                ) : null}
              </td>
              <td>
                <button
                  className="execution-history-detail-button"
                  onClick={() => onSelectRecord(record)}
                  type="button"
                >
                  Ver detalhes
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderSelectedRecordDetails(
  selectedRecord: AIExecutionHistoryRecord | null,
  onClearSelection: () => void,
) {
  if (!selectedRecord) {
    return (
      <section className="execution-history-details-empty">
        <span className="eyebrow">Run details</span>
        <h2>Nenhuma execução selecionada</h2>
        <p>
          Selecione uma linha da timeline para inspecionar metadata, IDs,
          status, duração, qualidade e sinais técnicos da execução.
        </p>
      </section>
    );
  }

  return (
    <section className="execution-history-details-panel">
      <div className="execution-history-details-header">
        <div>
          <span className="eyebrow">Run details</span>
          <h2>{selectedRecord.title}</h2>
          <p>{selectedRecord.summary}</p>
        </div>

        <div className="execution-history-details-actions">
          <StatusBadge status={toBadgeStatus(selectedRecord.status)} />
          <button
            className="execution-history-detail-button"
            onClick={onClearSelection}
            type="button"
          >
            Limpar seleção
          </button>
        </div>
      </div>

      <section className="metrics-grid">
        <MetricCard
          description="Status operacional consolidado"
          label="Status"
          value={selectedRecord.status}
        />
        <MetricCard
          description="Tipo de registro no histórico"
          label="Tipo"
          value={formatExecutionType(selectedRecord.execution_type)}
        />
        <MetricCard
          description="Componente responsável pela execução"
          label="Componente"
          value={selectedRecord.component}
        />
        <MetricCard
          description="Operação registrada na telemetria"
          label="Operação"
          value={selectedRecord.operation}
        />
      </section>

      <section className="metrics-grid">
        <MetricCard
          description="Duração registrada para a execução"
          label="Duração"
          value={formatDuration(selectedRecord.duration_ms)}
        />
        <MetricCard
          description="Quality score calculado pelo backend"
          label="Qualidade"
          value={formatQualityScore(selectedRecord.quality_score)}
        />
        <MetricCard
          description="Timestamp da execução"
          label="Registrado em"
          value={formatDateTime(selectedRecord.recorded_at)}
        />
        <MetricCard
          description="Identificador de correlação da execução"
          label="Run ID"
          value={selectedRecord.run_id ?? "N/A"}
        />
      </section>

      <section className="execution-history-details-meta-grid">
        <article>
          <span>Execution ID</span>
          <code>{selectedRecord.execution_id}</code>
        </article>

        <article>
          <span>Source record ID</span>
          <code>{selectedRecord.source_record_id}</code>
        </article>

        <article>
          <span>Run ID</span>
          <code>{selectedRecord.run_id ?? "N/A"}</code>
        </article>

        <article>
          <span>Recorded at</span>
          <code>{selectedRecord.recorded_at}</code>
        </article>
      </section>

      <section className="content-grid">
        <JsonViewer
          title="Selected execution metadata"
          value={toJsonViewerValue(selectedRecord.metadata)}
        />

        <JsonViewer
          title="Selected execution record"
          value={toJsonViewerValue(selectedRecord)}
        />
      </section>
    </section>
  );
}

export function ExecutionHistoryPage() {
  const { history, filters, requestState, updateFilters, refreshHistory } =
    useExecutionHistory();
  const [selectedExecutionId, setSelectedExecutionId] = useState<string | null>(
    null,
  );

  const records = useMemo(() => history?.records ?? [], [history]);

  const selectedRecord = useMemo(() => {
    if (!selectedExecutionId) {
      return null;
    }

    return (
      records.find((record) => record.execution_id === selectedExecutionId) ??
      null
    );
  }, [records, selectedExecutionId]);

  const summaryCards = useMemo(
    () => [
      {
        label: "Execuções listadas",
        value: String(history?.count ?? 0),
        description: "Registros retornados pelo endpoint de histórico.",
      },
      {
        label: "Última execução",
        value: getLatestRecordedAt(records),
        description: "Registro mais recente no histórico atual.",
      },
      {
        label: "Qualidade média",
        value: getAverageQuality(records),
        description: "Média dos registros que possuem quality score.",
      },
      {
        label: "Modo",
        value: String(history?.metadata.history_mode ?? "read model"),
        description: "Histórico consolidado a partir da observabilidade.",
      },
    ],
    [history, records],
  );

  function handleFilterChange(
    key: keyof ExecutionHistoryFilters,
    value: string,
  ) {
    setSelectedExecutionId(null);
    updateFilters({
      ...filters,
      [key]: key === "limit" ? Number(value) : value,
    });
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <span className="eyebrow">Execution History</span>
          <h1>Histórico de execuções</h1>
          <p>
            Linha do tempo operacional que consolida telemetria, usage,
            qualidade de recuperação, execução de agentes e execução multiagente
            em uma única visão.
          </p>
        </div>

        <button
          className="primary-button"
          disabled={requestState.isLoading}
          onClick={() => void refreshHistory()}
          type="button"
        >
          {requestState.isLoading ? "Atualizando..." : "Atualizar histórico"}
        </button>
      </header>

      {requestState.errorMessage ? (
        <section className="error-card">
          <strong>Não foi possível carregar o histórico.</strong>
          <p>
            Verifique se a API está rodando e se o endpoint{" "}
            <code>GET /observability/execution-history</code> está disponível.
          </p>
          <code>{requestState.errorMessage}</code>
        </section>
      ) : null}

      <section className="execution-history-filters">
        <label>
          Tipo de execução
          <select
            value={filters.executionType}
            onChange={(event) =>
              handleFilterChange("executionType", event.target.value)
            }
          >
            <option value="">Todos</option>
            <option value="evaluation_telemetry">Telemetria de avaliação</option>
            <option value="usage">Uso e custos</option>
            <option value="retrieval_quality">Qualidade de recuperação</option>
            <option value="agent_execution">Execução de agente</option>
            <option value="multi_agent_execution">Execução multiagente</option>
          </select>
        </label>

        <label>
          Status
          <select
            value={filters.status}
            onChange={(event) =>
              handleFilterChange("status", event.target.value)
            }
          >
            <option value="">Todos</option>
            <option value="passed">passed</option>
            <option value="warning">warning</option>
            <option value="failed">failed</option>
            <option value="completed">completed</option>
            <option value="recorded">recorded</option>
          </select>
        </label>

        <label>
          Componente
          <select
            value={filters.component}
            onChange={(event) =>
              handleFilterChange("component", event.target.value)
            }
          >
            <option value="">Todos</option>
            <option value="evaluation">evaluation</option>
            <option value="llm">llm</option>
            <option value="rag">rag</option>
            <option value="agent">agent</option>
            <option value="multi_agent">multi_agent</option>
          </select>
        </label>

        <label>
          Run ID
          <input
            placeholder="manual-multi-agent-run-001"
            value={filters.runId}
            onChange={(event) =>
              handleFilterChange("runId", event.target.value)
            }
          />
        </label>

        <label>
          Limite
          <select
            value={filters.limit}
            onChange={(event) =>
              handleFilterChange("limit", event.target.value)
            }
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>
      </section>

      <section className="metrics-grid">
        {summaryCards.map((card) => (
          <MetricCard
            description={card.description}
            key={card.label}
            label={card.label}
            value={card.value}
          />
        ))}
      </section>

      <section className="execution-history-panel">
        <div className="execution-history-panel-header">
          <div>
            <span className="eyebrow">Operational timeline</span>
            <h2>Últimas execuções</h2>
          </div>
          <code>GET /observability/execution-history</code>
        </div>

        {requestState.isLoading && !history ? (
          <p className="muted">Carregando histórico de execuções...</p>
        ) : (
          renderRecordsTable(records, selectedExecutionId, (record) =>
            setSelectedExecutionId(record.execution_id),
          )
        )}
      </section>

      {renderSelectedRecordDetails(selectedRecord, () =>
        setSelectedExecutionId(null),
      )}

      <JsonViewer
        title="Execution History Response"
        value={toJsonViewerValue(history ?? {})}
      />
    </div>
  );
}
