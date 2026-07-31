import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useObservabilityDashboard } from "../hooks/useObservabilityDashboard";
import {
  translateDashboardText,
  translateSectionName,
  translateStatus,
} from "../i18n/ptBr";
import type {
  DashboardSectionStatus,
  DashboardStatus,
  ObservabilityDashboardSection,
} from "../types/observability";

type SectionStatusCount = Record<DashboardSectionStatus, number>;

function buildStatusCounts(
  sections: ObservabilityDashboardSection[],
): SectionStatusCount {
  return sections.reduce<SectionStatusCount>(
    (accumulator, section) => {
      accumulator[section.status] += 1;
      return accumulator;
    },
    {
      healthy: 0,
      warning: 0,
      critical: 0,
      empty: 0,
    },
  );
}

function getSectionsWithRisks(
  sections: ObservabilityDashboardSection[],
): ObservabilityDashboardSection[] {
  return sections.filter((section) => section.risks.length > 0);
}

function getSectionsWithRecommendations(
  sections: ObservabilityDashboardSection[],
): ObservabilityDashboardSection[] {
  return sections.filter((section) => section.recommendations.length > 0);
}

function getAttentionSections(
  sections: ObservabilityDashboardSection[],
): ObservabilityDashboardSection[] {
  return sections.filter((section) =>
    ["warning", "critical", "empty"].includes(section.status),
  );
}

function getReleaseSignal(status: DashboardStatus): string {
  if (status === "healthy") {
    return "Sinal saudável para demonstração controlada.";
  }

  if (status === "warning") {
    return "Sinal com atenção: revisar riscos e recomendações antes de usar como evidência.";
  }

  if (status === "critical") {
    return "Sinal crítico: há riscos relevantes para tratar antes de decisão de release.";
  }

  return "Sinal sem dados suficientes: registre observabilidade antes de usar como evidência.";
}

function renderTextList(title: string, items: string[], emptyMessage: string) {
  return (
    <article className="risk-panel-card">
      <h2>{title}</h2>

      {items.length === 0 ? (
        <p className="muted">{emptyMessage}</p>
      ) : (
        <ul className="risk-list">
          {items.map((item) => (
            <li key={item}>{translateDashboardText(item)}</li>
          ))}
        </ul>
      )}
    </article>
  );
}

function renderSectionRiskCard(section: ObservabilityDashboardSection) {
  return (
    <article className="risk-section-card" key={section.name}>
      <div className="risk-section-header">
        <div>
          <span className="eyebrow">{section.name}</span>
          <h3>{translateSectionName(section.name)}</h3>
        </div>

        <StatusBadge status={section.status} />
      </div>

      <div className="risk-section-content">
        <div>
          <span className="eyebrow">Riscos</span>
          {section.risks.length === 0 ? (
            <p className="muted">Nenhum risco específico retornado.</p>
          ) : (
            <ul className="risk-list">
              {section.risks.map((risk) => (
                <li key={risk}>{translateDashboardText(risk)}</li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <span className="eyebrow">Recomendações</span>
          {section.recommendations.length === 0 ? (
            <p className="muted">Nenhuma recomendação específica retornada.</p>
          ) : (
            <ul className="risk-list">
              {section.recommendations.map((recommendation) => (
                <li key={recommendation}>
                  {translateDashboardText(recommendation)}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </article>
  );
}

function renderSectionMatrix(sections: ObservabilityDashboardSection[]) {
  if (sections.length === 0) {
    return <p className="muted">Nenhuma seção retornada pelo dashboard.</p>;
  }

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Área</th>
            <th>Status</th>
            <th>Riscos</th>
            <th>Recomendações</th>
          </tr>
        </thead>
        <tbody>
          {sections.map((section) => (
            <tr key={section.name}>
              <td>{translateSectionName(section.name)}</td>
              <td>{translateStatus(section.status)}</td>
              <td>{section.risks.length}</td>
              <td>{section.recommendations.length}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function RiskCenterPage() {
  const { dashboard, errorMessage, refreshDashboard, requestState } =
    useObservabilityDashboard();

  const sections = dashboard?.sections ?? [];
  const statusCounts = buildStatusCounts(sections);
  const sectionsWithRisks = getSectionsWithRisks(sections);
  const sectionsWithRecommendations = getSectionsWithRecommendations(sections);
  const attentionSections = getAttentionSections(sections);

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Risk Center</span>
          <h1>Central de Riscos</h1>
          <p>
            Consolide riscos, recomendações e sinais de atenção gerados pela
            camada de observabilidade da plataforma. Esta visão ajuda a
            transformar métricas em decisão.
          </p>
        </div>

        <button
          className="secondary-button"
          disabled={requestState === "loading"}
          onClick={refreshDashboard}
          type="button"
        >
          {requestState === "loading" ? "Atualizando..." : "Atualizar riscos"}
        </button>
      </section>

      {requestState === "error" ? (
        <article className="alert-card">
          <strong>Não foi possível carregar a Central de Riscos.</strong>
          <p>Verifique se a API está rodando e se o dashboard está disponível.</p>
          <small>{errorMessage}</small>
        </article>
      ) : null}

      <section className="risk-signal-card">
        <div>
          <span className="eyebrow">Release signal</span>
          <h2>
            {dashboard
              ? translateStatus(dashboard.status)
              : "Carregando sinal"}
          </h2>
          <p>
            {dashboard
              ? getReleaseSignal(dashboard.status)
              : "Aguardando resposta do dashboard."}
          </p>
        </div>

        {dashboard ? (
          <StatusBadge status={dashboard.status} />
        ) : (
          <span className="status-badge status-empty">loading</span>
        )}
      </section>

      <section className="metrics-grid">
        <MetricCard
          description="Riscos globais retornados pelo dashboard"
          label="Global risks"
          value={dashboard?.global_risks.length ?? 0}
        />
        <MetricCard
          description="Recomendações globais retornadas pelo dashboard"
          label="Recommendations"
          value={dashboard?.recommendations.length ?? 0}
        />
        <MetricCard
          description="Seções com warning, critical ou empty"
          label="Attention areas"
          value={attentionSections.length}
        />
        <MetricCard
          description="Seções sem dados suficientes"
          label="Empty sections"
          value={statusCounts.empty}
        />
      </section>

      <section className="risk-status-grid">
        <article className="risk-status-card">
          <span className="eyebrow">Status distribution</span>
          <h2>Distribuição por status</h2>

          <div className="risk-status-list">
            <div>
              <span>Saudáveis</span>
              <strong>{statusCounts.healthy}</strong>
            </div>
            <div>
              <span>Atenção</span>
              <strong>{statusCounts.warning}</strong>
            </div>
            <div>
              <span>Críticas</span>
              <strong>{statusCounts.critical}</strong>
            </div>
            <div>
              <span>Sem dados</span>
              <strong>{statusCounts.empty}</strong>
            </div>
          </div>
        </article>

        {renderTextList(
          "Riscos globais",
          dashboard?.global_risks ?? [],
          "Nenhum risco global retornado.",
        )}

        {renderTextList(
          "Recomendações globais",
          dashboard?.recommendations ?? [],
          "Nenhuma recomendação global retornada.",
        )}
      </section>

      <section className="console-steps-card">
        <div>
          <span className="eyebrow">Attention areas</span>
          <h2>Áreas que precisam de atenção</h2>
          <p className="muted">
            Seções com status warning, critical ou empty indicam pontos que
            precisam de dados, investigação ou melhoria antes de serem usados
            como sinal de decisão.
          </p>
        </div>

        {attentionSections.length === 0 ? (
          <section className="empty-state">
            <h2>Nenhuma área em atenção</h2>
            <p>Todas as seções retornadas estão saudáveis.</p>
          </section>
        ) : (
          <div className="risk-section-grid">
            {attentionSections.map(renderSectionRiskCard)}
          </div>
        )}
      </section>

      <section className="console-steps-card">
        <div>
          <span className="eyebrow">Risk matrix</span>
          <h2>Matriz de riscos e recomendações</h2>
          <p className="muted">
            Visão resumida das seções do dashboard, status, quantidade de riscos
            e quantidade de recomendações.
          </p>
        </div>

        {renderSectionMatrix(sections)}
      </section>

      <section className="content-grid">
        <JsonViewer title="Sections with risks" value={sectionsWithRisks} />
        <JsonViewer
          title="Sections with recommendations"
          value={sectionsWithRecommendations}
        />
      </section>

      <JsonViewer title="Dashboard metadata" value={dashboard?.metadata} />
    </div>
  );
}
