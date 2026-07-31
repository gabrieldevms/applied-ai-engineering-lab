import {
  translateDashboardText,
  translateMetricKey,
  translateSectionName,
  translateSectionTitle,
} from "../../i18n/ptBr";
import type { ObservabilityDashboardSection } from "../../types/observability";
import { StatusBadge } from "./StatusBadge";

type SectionPanelProps = {
  section: ObservabilityDashboardSection;
};

const highlightedMetricKeys = [
  "record_count",
  "passed_count",
  "warning_count",
  "failed_count",
  "total_tokens",
  "total_cost_usd",
  "average_quality_score",
  "average_duration_ms",
];

function formatMetricValue(value: unknown): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }

  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "boolean") {
    return value ? "Sim" : "Não";
  }

  if (value === null || value === undefined) {
    return "N/A";
  }

  return JSON.stringify(value);
}

export function SectionPanel({ section }: SectionPanelProps) {
  const visibleMetrics = Object.entries(section.metrics).filter(([key, value]) => {
    return highlightedMetricKeys.includes(key) && value !== null;
  });

  return (
    <article className="section-panel">
      <header className="section-header">
        <div>
          <span className="eyebrow">{translateSectionName(section.name)}</span>
          <h3>{translateSectionTitle(section.name, section.title)}</h3>
        </div>

        <StatusBadge status={section.status} />
      </header>

      {visibleMetrics.length > 0 ? (
        <div className="compact-metrics">
          {visibleMetrics.map(([key, value]) => (
            <div className="compact-metric" key={key}>
              <span>{translateMetricKey(key)}</span>
              <strong>{formatMetricValue(value)}</strong>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">Nenhuma métrica destacada disponível ainda.</p>
      )}

      <div className="section-lists">
        <div>
          <h4>Riscos</h4>
          <ul>
            {section.risks.map((risk) => (
              <li key={risk}>{translateDashboardText(risk)}</li>
            ))}
          </ul>
        </div>

        <div>
          <h4>Recomendações</h4>
          <ul>
            {section.recommendations.map((recommendation) => (
              <li key={recommendation}>
                {translateDashboardText(recommendation)}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </article>
  );
}
