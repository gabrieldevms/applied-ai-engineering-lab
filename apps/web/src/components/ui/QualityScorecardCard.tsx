import { translateMetricKey } from "../../i18n/ptBr";
import type { QualityScorecardSection } from "../../types/productionObservability";
import { formatObservedAt } from "../../utils/formatObservedAt";
import { StatusBadge } from "./StatusBadge";

const titleLabels: Record<string, string> = {
  evaluation_quality: "Qualidade da avaliação",
  retrieval_quality: "Qualidade da recuperação",
  agent_reliability: "Confiabilidade dos agentes",
  multi_agent_reliability: "Confiabilidade multiagente",
  usage_cost: "Uso e custo",
  operational_readiness: "Prontidão operacional",
};

const trendLabels = {
  improving: "Melhorando",
  stable: "Estável",
  degrading: "Piorando",
  insufficient_data: "Dados insuficientes",
};

const noteLabels: Record<string, string> = {
  "No observations in the recent seven-day window.":
    "Sem observações nos últimos sete dias.",
  "Cost estimates are missing for at least one recent record.":
    "Faltam estimativas de custo em pelo menos um registro recente.",
  "Cost movement is not a quality trend.":
    "A variação de custo não representa tendência de qualidade.",
  "Readiness is a local snapshot, not a Prometheus query.":
    "A prontidão é uma leitura local, sem consulta ao Prometheus.",
};

function formatMetric(key: string, value: number | null): string {
  if (value === null) {
    return "N/D";
  }
  if (key.endsWith("_ok")) {
    return value === 1 ? "Sim" : "Não";
  }
  return Number.isInteger(value) ? String(value) : value.toFixed(4);
}

export function QualityScorecardCard({
  section,
}: {
  section: QualityScorecardSection;
}) {
  const visibleMetrics = Object.entries(section.metrics);

  return (
    <article className="quality-scorecard">
      <header className="section-header">
        <h3>{titleLabels[section.name] ?? section.title}</h3>
        <StatusBadge status={section.status} />
      </header>
      <p className="quality-freshness">
        Última observação: {formatObservedAt(section.latest_observed_at)}
      </p>
      <div className="quality-metrics">
        {visibleMetrics.map(([key, value]) => (
          <div className="compact-metric" key={key}>
            <span>{translateMetricKey(key)}</span>
            <strong>{formatMetric(key, value)}</strong>
          </div>
        ))}
      </div>
      <p className={`quality-trend quality-trend-${section.trend.signal}`}>
        {section.name === "usage_cost" || section.name === "operational_readiness"
          ? "Tendência de qualidade: "
          : "Tendência de alertas e falhas: "}
        <strong>{trendLabels[section.trend.signal]}</strong>
        <small>
          {section.trend.recent_count} registro(s) nos últimos {section.trend.window_days} dias · {section.trend.previous_count} no período anterior
        </small>
        {section.trend.recent_adverse_rate !== null && section.trend.previous_adverse_rate !== null ? (
          <small>
            Alertas/falhas: {(section.trend.recent_adverse_rate * 100).toFixed(0)}% agora · {(section.trend.previous_adverse_rate * 100).toFixed(0)}% antes
          </small>
        ) : null}
      </p>
      {section.notes.length > 0 ? (
        <ul className="quality-notes">
          {section.notes.map((note) => (
            <li key={note}>{noteLabels[note] ?? note}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}
