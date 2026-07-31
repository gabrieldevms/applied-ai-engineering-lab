import { useMemo } from "react";
import { MetricCard } from "../components/ui/MetricCard";
import { SectionPanel } from "../components/ui/SectionPanel";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useObservabilityDashboard } from "../hooks/useObservabilityDashboard";
import {
  translateDashboardText,
  translateMetricKey,
  translateStatus,
} from "../i18n/ptBr";
import type {
  DashboardMetricValue,
  ObservabilityDashboardSection,
} from "../types/observability";

const evaluationSuites = [
  {
    name: "Golden Dataset",
    description:
      "Dataset de referência para validar comportamento esperado dos workflows de IA.",
    status: "Foundation ready",
  },
  {
    name: "Prompt Regression",
    description:
      "Validação de regressão para mudanças em prompts, templates e contratos de saída.",
    status: "Foundation ready",
  },
  {
    name: "LLM Output Evaluation",
    description:
      "Avaliação de qualidade, estrutura e consistência das respostas geradas por LLMs.",
    status: "Foundation ready",
  },
  {
    name: "RAG Regression",
    description:
      "Validação de retrieval, qualidade de contexto, citações e respostas fundamentadas.",
    status: "Foundation ready",
  },
  {
    name: "Agent Regression",
    description:
      "Avaliação de agentes, uso de ferramentas, rastreabilidade e limites de segurança.",
    status: "Foundation ready",
  },
  {
    name: "Multi-Agent Regression",
    description:
      "Avaliação do QA Copilot multiagente, contratos entre agentes e relatório final.",
    status: "Foundation ready",
  },
  {
    name: "Tool-calling Evaluation",
    description:
      "Validação de seleção, execução e segurança no uso de ferramentas por agentes.",
    status: "Foundation ready",
  },
  {
    name: "LLM-as-judge Prototype",
    description:
      "Protótipo de avaliação assistida por LLM para apoiar análise qualitativa.",
    status: "Prototype",
  },
];

function findEvaluationSection(
  sections: ObservabilityDashboardSection[],
): ObservabilityDashboardSection | null {
  return (
    sections.find((section) => section.name === "evaluation_telemetry") ?? null
  );
}

function formatMetricValue(value: DashboardMetricValue | undefined): string {
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

function getMetric(
  section: ObservabilityDashboardSection | null,
  key: string,
): string {
  return formatMetricValue(section?.metrics[key]);
}

function getEvaluationSignal(
  section: ObservabilityDashboardSection | null,
): {
  title: string;
  description: string;
} {
  if (!section) {
    return {
      title: "Sem dados",
      description:
        "A seção de evaluation telemetry ainda não foi retornada pelo backend dashboard.",
    };
  }

  if (section.status === "healthy") {
    return {
      title: "Evaluation signal saudável",
      description:
        "Os sinais de avaliação disponíveis não indicam riscos relevantes neste momento.",
    };
  }

  if (section.status === "warning") {
    return {
      title: "Evaluation signal com atenção",
      description:
        "Existem pontos de atenção que devem ser revisados antes de usar os resultados como critério forte de release.",
    };
  }

  if (section.status === "critical") {
    return {
      title: "Evaluation signal crítico",
      description:
        "Foram encontrados sinais críticos. A recomendação é investigar antes de avançar com decisões de release.",
    };
  }

  return {
    title: "Evaluation signal sem dados",
    description:
      "Ainda não há dados suficientes para usar a avaliação como sinal confiável de qualidade.",
  };
}

export function EvaluationCenterPage() {
  const { dashboard, errorMessage, refreshDashboard, requestState } =
    useObservabilityDashboard();

  const evaluationSection = useMemo(() => {
    return findEvaluationSection(dashboard?.sections ?? []);
  }, [dashboard]);

  const evaluationSignal = useMemo(() => {
    return getEvaluationSignal(evaluationSection);
  }, [evaluationSection]);

  const visibleMetrics = useMemo(() => {
    if (!evaluationSection) {
      return [];
    }

    return Object.entries(evaluationSection.metrics).filter(([, value]) => {
      return value !== null && value !== undefined;
    });
  }, [evaluationSection]);

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Evaluation</span>
          <h1>Evaluation Center</h1>
          <p>
            Uma área dedicada para acompanhar sinais de avaliação, regressões,
            quality gates e confiabilidade dos workflows de IA do projeto.
          </p>
        </div>

        <div className="hero-actions">
          {evaluationSection ? (
            <StatusBadge status={evaluationSection.status} />
          ) : null}

          <button
            className="primary-button"
            disabled={requestState === "loading"}
            onClick={() => void refreshDashboard()}
            type="button"
          >
            {requestState === "loading"
              ? "Atualizando..."
              : "Atualizar evaluation"}
          </button>
        </div>
      </section>

      {requestState === "error" ? (
        <section className="alert-card">
          <strong>Não foi possível carregar o Evaluation Center.</strong>
          <p>
            Verifique se a API está rodando e se o endpoint{" "}
            <code>/observability/dashboard</code> está disponível.
          </p>
          <small>{errorMessage}</small>
        </section>
      ) : null}

      <section className="metrics-grid">
        <MetricCard
          description="Status da seção de evaluation telemetry"
          label="Status"
          value={
            evaluationSection
              ? translateStatus(evaluationSection.status)
              : "Carregando"
          }
        />
        <MetricCard
          description="Registros de avaliação observados"
          label="Registros"
          value={getMetric(evaluationSection, "record_count")}
        />
        <MetricCard
          description="Alertas identificados nos sinais de avaliação"
          label="Alertas"
          value={getMetric(evaluationSection, "warning_count")}
        />
        <MetricCard
          description="Falhas identificadas nos sinais de avaliação"
          label="Falhas"
          value={getMetric(evaluationSection, "failed_count")}
        />
      </section>

      <section className="evaluation-signal-card">
        <div>
          <span className="eyebrow">Release signal</span>
          <h2>{evaluationSignal.title}</h2>
          <p>{evaluationSignal.description}</p>
        </div>

        <div className="evaluation-signal-meta">
          <strong>{evaluationSuites.length}</strong>
          <span>suites mapeadas</span>
        </div>
      </section>

      {evaluationSection ? (
        <>
          <section className="content-grid">
            <article className="insight-card">
              <h2>Riscos de evaluation</h2>
              <ul>
                {evaluationSection.risks.map((risk) => (
                  <li key={risk}>{translateDashboardText(risk)}</li>
                ))}
              </ul>
            </article>

            <article className="insight-card">
              <h2>Recomendações</h2>
              <ul>
                {evaluationSection.recommendations.map((recommendation) => (
                  <li key={recommendation}>
                    {translateDashboardText(recommendation)}
                  </li>
                ))}
              </ul>
            </article>
          </section>

          <SectionPanel section={evaluationSection} />

          <section className="evaluation-details-card">
            <div>
              <span className="eyebrow">Telemetry details</span>
              <h2>Métricas disponíveis</h2>
            </div>

            {visibleMetrics.length > 0 ? (
              <div className="evaluation-metrics-table">
                {visibleMetrics.map(([key, value]) => (
                  <div className="evaluation-metric-row" key={key}>
                    <span>{translateMetricKey(key)}</span>
                    <strong>{formatMetricValue(value)}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">
                Nenhuma métrica de evaluation telemetry disponível ainda.
              </p>
            )}
          </section>
        </>
      ) : (
        <section className="empty-state">
          <h2>Nenhum dado de evaluation carregado ainda</h2>
          <p>
            O Evaluation Center será preenchido quando o backend dashboard
            retornar a seção de evaluation telemetry.
          </p>
        </section>
      )}

      <section className="evaluation-suite-grid">
        {evaluationSuites.map((suite) => (
          <article className="evaluation-suite-card" key={suite.name}>
            <span className="eyebrow">{suite.status}</span>
            <h3>{suite.name}</h3>
            <p>{suite.description}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
