import { useEffect, useMemo, useState } from "react";
import { getObservabilityDashboard } from "../api/observabilityDashboardApi";
import { MetricCard } from "../components/ui/MetricCard";
import { SectionPanel } from "../components/ui/SectionPanel";
import { StatusBadge } from "../components/ui/StatusBadge";
import { translateDashboardText } from "../i18n/ptBr";
import type { ObservabilityDashboardResponse } from "../types/observability";

type RequestState = "idle" | "loading" | "success" | "error";

function getSectionCountByStatus(
  dashboard: ObservabilityDashboardResponse | null,
  status: string,
): number {
  if (!dashboard) {
    return 0;
  }

  return dashboard.sections.filter((section) => section.status === status).length;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao carregar o dashboard.";
}

export function CommandCenterPage() {
  const [dashboard, setDashboard] =
    useState<ObservabilityDashboardResponse | null>(null);
  const [requestState, setRequestState] = useState<RequestState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let shouldIgnoreResult = false;

    getObservabilityDashboard()
      .then((response) => {
        if (shouldIgnoreResult) {
          return;
        }

        setDashboard(response);
        setRequestState("success");
      })
      .catch((error: unknown) => {
        if (shouldIgnoreResult) {
          return;
        }

        setRequestState("error");
        setErrorMessage(getErrorMessage(error));
      });

    return () => {
      shouldIgnoreResult = true;
    };
  }, []);

  async function refreshDashboard() {
    setRequestState("loading");
    setErrorMessage(null);

    try {
      const response = await getObservabilityDashboard();

      setDashboard(response);
      setRequestState("success");
    } catch (error) {
      setRequestState("error");
      setErrorMessage(getErrorMessage(error));
    }
  }

  const summaryMetrics = useMemo(() => {
    return [
      {
        label: "Seções",
        value: dashboard?.sections.length ?? 0,
        description: "Seções retornadas pelo backend",
      },
      {
        label: "Saudáveis",
        value: getSectionCountByStatus(dashboard, "healthy"),
        description: "Seções sem riscos relevantes",
      },
      {
        label: "Alertas",
        value: getSectionCountByStatus(dashboard, "warning"),
        description: "Seções que precisam de atenção",
      },
      {
        label: "Críticas",
        value: getSectionCountByStatus(dashboard, "critical"),
        description: "Seções com sinais de falha",
      },
    ];
  }, [dashboard]);

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Fundação do M8</span>
          <h1>AI Quality Command Center</h1>
          <p>
            Uma base de frontend para acompanhar qualidade de IA, sinais de
            avaliação, métricas de observabilidade, riscos e recomendações do
            Applied AI Engineering Lab.
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
              : "Atualizar dashboard"}
          </button>
        </div>
      </section>

      {requestState === "error" ? (
        <section className="alert-card">
          <strong>O dashboard do backend ainda não está disponível.</strong>
          <p>
            Inicie a API com{" "}
            <code>
              uv run uvicorn ai_api.main:app --reload --app-dir apps/api/src
            </code>{" "}
            e tente novamente.
          </p>
          <small>{errorMessage}</small>
        </section>
      ) : null}

      <section className="metrics-grid">
        {summaryMetrics.map((metric) => (
          <MetricCard
            description={metric.description}
            key={metric.label}
            label={metric.label}
            value={metric.value}
          />
        ))}
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

          <section className="section-grid">
            {dashboard.sections.map((section) => (
              <SectionPanel key={section.name} section={section} />
            ))}
          </section>
        </>
      ) : (
        <section className="empty-state">
          <h2>Nenhum dado carregado ainda</h2>
          <p>
            O Command Center exibirá os dados de observabilidade do backend
            quando o endpoint de dashboard responder com sucesso.
          </p>
        </section>
      )}
    </div>
  );
}
