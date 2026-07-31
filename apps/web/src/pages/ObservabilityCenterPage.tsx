import { useMemo, useState } from "react";
import { MetricCard } from "../components/ui/MetricCard";
import { SectionPanel } from "../components/ui/SectionPanel";
import { StatusBadge } from "../components/ui/StatusBadge";
import { translateDashboardText, translateStatus } from "../i18n/ptBr";
import { useObservabilityDashboard } from "../hooks/useObservabilityDashboard";
import type {
  DashboardSectionStatus,
  ObservabilityDashboardSection,
} from "../types/observability";

type StatusFilter = DashboardSectionStatus | "all";

const statusFilters: {
  label: string;
  value: StatusFilter;
}[] = [
  {
    label: "Todas",
    value: "all",
  },
  {
    label: "Saudáveis",
    value: "healthy",
  },
  {
    label: "Atenção",
    value: "warning",
  },
  {
    label: "Críticas",
    value: "critical",
  },
  {
    label: "Sem dados",
    value: "empty",
  },
];

function countSectionsByStatus(
  sections: ObservabilityDashboardSection[],
  status: DashboardSectionStatus,
): number {
  return sections.filter((section) => section.status === status).length;
}

function getRiskCount(sections: ObservabilityDashboardSection[]): number {
  return sections.reduce((total, section) => {
    return total + section.risks.length;
  }, 0);
}

function getRecommendationCount(
  sections: ObservabilityDashboardSection[],
): number {
  return sections.reduce((total, section) => {
    return total + section.recommendations.length;
  }, 0);
}

export function ObservabilityCenterPage() {
  const { dashboard, errorMessage, refreshDashboard, requestState } =
    useObservabilityDashboard();
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");

  const filteredSections = useMemo(() => {
    if (!dashboard) {
      return [];
    }

    if (statusFilter === "all") {
      return dashboard.sections;
    }

    return dashboard.sections.filter((section) => {
      return section.status === statusFilter;
    });
  }, [dashboard, statusFilter]);

  const sections = dashboard?.sections ?? [];

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Observability</span>
          <h1>Observability Center</h1>
          <p>
            Uma visão dedicada para acompanhar saúde, riscos, recomendações e
            sinais operacionais dos workflows de IA do projeto.
          </p>
        </div>

        <div className="hero-actions">
          {dashboard ? <StatusBadge status={dashboard.status} /> : null}

          <button
            className="primary-button"
            disabled={requestState === "loading"}
            onClick={() => void refreshDashboard()}
            type="button"
          >
            {requestState === "loading"
              ? "Atualizando..."
              : "Atualizar observability"}
          </button>
        </div>
      </section>

      {requestState === "error" ? (
        <section className="alert-card">
          <strong>Não foi possível carregar o Observability Center.</strong>
          <p>
            Verifique se a API está rodando e se o endpoint{" "}
            <code>/observability/dashboard</code> está disponível.
          </p>
          <small>{errorMessage}</small>
        </section>
      ) : null}

      <section className="metrics-grid">
        <MetricCard
          description="Status consolidado retornado pelo backend"
          label="Status geral"
          value={dashboard ? translateStatus(dashboard.status) : "Carregando"}
        />
        <MetricCard
          description="Áreas de observabilidade monitoradas"
          label="Seções"
          value={sections.length}
        />
        <MetricCard
          description="Riscos agregados nas seções"
          label="Riscos"
          value={dashboard?.global_risks.length ?? 0}
        />
        <MetricCard
          description="Recomendações geradas pelo dashboard"
          label="Recomendações"
          value={dashboard?.recommendations.length ?? 0}
        />
      </section>

      <section className="metrics-grid">
        <MetricCard
          description="Seções sem riscos relevantes"
          label="Saudáveis"
          value={countSectionsByStatus(sections, "healthy")}
        />
        <MetricCard
          description="Seções com pontos de atenção"
          label="Atenção"
          value={countSectionsByStatus(sections, "warning")}
        />
        <MetricCard
          description="Seções com sinais críticos"
          label="Críticas"
          value={countSectionsByStatus(sections, "critical")}
        />
        <MetricCard
          description="Seções ainda sem dados registrados"
          label="Sem dados"
          value={countSectionsByStatus(sections, "empty")}
        />
      </section>

      {dashboard ? (
        <>
          <section className="content-grid">
            <article className="insight-card">
              <h2>Riscos globais</h2>
              <ul>
                {dashboard.global_risks.map((risk) => (
                  <li key={risk}>{translateDashboardText(risk)}</li>
                ))}
              </ul>
            </article>

            <article className="insight-card">
              <h2>Recomendações</h2>
              <ul>
                {dashboard.recommendations.map((recommendation) => (
                  <li key={recommendation}>
                    {translateDashboardText(recommendation)}
                  </li>
                ))}
              </ul>
            </article>
          </section>

          <section className="observability-toolbar">
            <div>
              <span className="eyebrow">Filtros</span>
              <h2>Seções de observabilidade</h2>
            </div>

            <div className="filter-group" aria-label="Filtrar por status">
              {statusFilters.map((filter) => (
                <button
                  className={
                    filter.value === statusFilter
                      ? "filter-button active"
                      : "filter-button"
                  }
                  key={filter.value}
                  onClick={() => setStatusFilter(filter.value)}
                  type="button"
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </section>

          <section className="observability-summary-card">
            <div>
              <strong>{filteredSections.length}</strong>
              <span>seções exibidas</span>
            </div>
            <div>
              <strong>{getRiskCount(filteredSections)}</strong>
              <span>riscos nas seções filtradas</span>
            </div>
            <div>
              <strong>{getRecommendationCount(filteredSections)}</strong>
              <span>recomendações nas seções filtradas</span>
            </div>
          </section>

          <section className="section-grid">
            {filteredSections.map((section) => (
              <SectionPanel key={section.name} section={section} />
            ))}
          </section>
        </>
      ) : (
        <section className="empty-state">
          <h2>Nenhum dado carregado ainda</h2>
          <p>
            O Observability Center será preenchido quando o backend dashboard
            responder com sucesso.
          </p>
        </section>
      )}
    </div>
  );
}
