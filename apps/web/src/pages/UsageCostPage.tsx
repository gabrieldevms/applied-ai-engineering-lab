import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import { useUsageCost } from "../hooks/useUsageCost";
import type { AIUsageRecord } from "../types/usageCost";

function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "-";
  }

  return new Intl.NumberFormat("en-US").format(value);
}

function formatUsd(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "-";
  }

  return new Intl.NumberFormat("en-US", {
    currency: "USD",
    maximumFractionDigits: 8,
    minimumFractionDigits: 2,
    style: "currency",
  }).format(value);
}

function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("pt-BR");
}

function getCoverageEntries(coverage: Record<string, number>) {
  return Object.entries(coverage).sort((left, right) => right[1] - left[1]);
}

function renderCoverageCard(title: string, coverage: Record<string, number>) {
  const entries = getCoverageEntries(coverage);

  return (
    <article className="usage-coverage-card">
      <h3>{title}</h3>

      {entries.length === 0 ? (
        <p className="muted">Nenhum dado disponível.</p>
      ) : (
        <div className="usage-coverage-list">
          {entries.map(([name, count]) => (
            <div className="usage-coverage-row" key={name}>
              <span>{name}</span>
              <strong>{count}</strong>
            </div>
          ))}
        </div>
      )}
    </article>
  );
}

function renderRecordCost(record: AIUsageRecord): string {
  if (record.total_cost_usd === null || record.total_cost_usd === undefined) {
    return "-";
  }

  return formatUsd(record.total_cost_usd);
}

function renderRecordsTable(records: AIUsageRecord[]) {
  if (records.length === 0) {
    return (
      <section className="empty-state">
        <h2>Nenhum usage record registrado</h2>
        <p>
          Use o botão de demo para registrar um usage record em memória e
          visualizar tokens, custos e coverage.
        </p>
      </section>
    );
  }

  const latestRecords = [...records].reverse().slice(0, 20);

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Recorded at</th>
            <th>Provider</th>
            <th>Model</th>
            <th>Component</th>
            <th>Operation</th>
            <th>Total tokens</th>
            <th>Total cost</th>
          </tr>
        </thead>
        <tbody>
          {latestRecords.map((record) => (
            <tr key={record.record_id}>
              <td>{formatDate(record.recorded_at)}</td>
              <td>{record.provider}</td>
              <td>{record.model_name}</td>
              <td>{record.component}</td>
              <td>{record.operation}</td>
              <td>{formatNumber(record.total_tokens)}</td>
              <td>{renderRecordCost(record)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function UsageCostPage() {
  const {
    errorMessage,
    recordDemoUsage,
    recordsResponse,
    refresh,
    requestState,
    summary,
  } = useUsageCost();

  const records = recordsResponse?.records ?? [];

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">LLMOps</span>
          <h1>Uso e Custos</h1>
          <p>
            Visualize tokens, custos estimados, coverage por provider/modelo e
            riscos de usage tracking. Esta tela usa os endpoints de observability
            do backend e ainda trabalha com registros em memória.
          </p>
        </div>

        <div className="console-action-row">
          <button
            className="secondary-button"
            disabled={requestState === "loading"}
            onClick={refresh}
            type="button"
          >
            {requestState === "loading" ? "Atualizando..." : "Atualizar"}
          </button>

          <button
            className="primary-button"
            disabled={requestState === "loading"}
            onClick={() => void recordDemoUsage()}
            type="button"
          >
            Registrar demo usage
          </button>
        </div>
      </section>

      {requestState === "error" ? (
        <article className="alert-card">
          <strong>Não foi possível carregar usage/cost.</strong>
          <p>
            Verifique se a API está rodando e se os endpoints de usage tracking
            estão respondendo.
          </p>
          <small>{errorMessage}</small>
        </article>
      ) : null}

      <section className="metrics-grid">
        <MetricCard
          description="Total de registros de uso armazenados no backend em memória"
          label="Usage records"
          value={summary?.record_count ?? 0}
        />
        <MetricCard
          description="Soma de tokens de prompt"
          label="Prompt tokens"
          value={formatNumber(summary?.total_prompt_tokens ?? 0)}
        />
        <MetricCard
          description="Soma de tokens de completion"
          label="Completion tokens"
          value={formatNumber(summary?.total_completion_tokens ?? 0)}
        />
        <MetricCard
          description="Soma total de tokens"
          label="Total tokens"
          value={formatNumber(summary?.total_tokens ?? 0)}
        />
        <MetricCard
          description="Custo total estimado em USD"
          label="Total cost"
          value={formatUsd(summary?.total_cost_usd)}
        />
        <MetricCard
          description="Custo médio por registro com custo disponível"
          label="Average cost"
          value={formatUsd(summary?.average_cost_usd)}
        />
      </section>

      <section className="usage-cost-grid">
        <article className="usage-cost-card">
          <span className="eyebrow">Token distribution</span>
          <h2>Distribuição de tokens</h2>

          <div className="usage-token-grid">
            <div>
              <span>Prompt</span>
              <strong>{formatNumber(summary?.total_prompt_tokens ?? 0)}</strong>
            </div>
            <div>
              <span>Completion</span>
              <strong>
                {formatNumber(summary?.total_completion_tokens ?? 0)}
              </strong>
            </div>
            <div>
              <span>Embedding</span>
              <strong>
                {formatNumber(summary?.total_embedding_tokens ?? 0)}
              </strong>
            </div>
          </div>
        </article>

        <article className="usage-cost-card">
          <span className="eyebrow">Usage risks</span>
          <h2>Riscos e sinais</h2>

          {summary?.risks.length ? (
            <ul className="usage-risk-list">
              {summary.risks.map((risk) => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
          ) : (
            <p className="muted">Nenhum risco retornado pelo backend.</p>
          )}
        </article>
      </section>

      <section className="usage-coverage-grid">
        {renderCoverageCard("Provider coverage", summary?.provider_coverage ?? {})}
        {renderCoverageCard("Model coverage", summary?.model_coverage ?? {})}
        {renderCoverageCard(
          "Component coverage",
          summary?.component_coverage ?? {},
        )}
        {renderCoverageCard(
          "Operation coverage",
          summary?.operation_coverage ?? {},
        )}
      </section>

      <section className="console-steps-card">
        <div>
          <span className="eyebrow">Stored records</span>
          <h2>Últimos usage records</h2>
          <p className="muted">
            Os registros abaixo vêm de{" "}
            <code>GET /observability/usage/records</code>. Nesta etapa, eles
            ficam em memória no backend.
          </p>
        </div>

        {renderRecordsTable(records)}
      </section>

      <section className="content-grid">
        <JsonViewer title="Usage summary" value={summary} />
        <JsonViewer title="Usage records response" value={recordsResponse} />
      </section>
    </div>
  );
}
