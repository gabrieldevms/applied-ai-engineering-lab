import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useLLMSettings } from "../hooks/useLLMSettings";
import type {
  LLMHealthResponse,
  ProviderSettingsViewModel,
} from "../types/llmSettings";

const providerCatalog: ProviderSettingsViewModel[] = [
  {
    provider: "fake",
    label: "Fake LLM",
    description:
      "Provider determinístico usado para desenvolvimento local, testes automatizados e fluxos sem dependência externa.",
    requiredSettings: [],
    safeNotes: [
      "Não exige secrets.",
      "Ideal para testes determinísticos.",
      "Não representa qualidade real de resposta de um modelo externo.",
    ],
  },
  {
    provider: "openai",
    label: "OpenAI",
    description:
      "Provider externo para execução real de chamadas LLM usando a configuração segura do backend.",
    requiredSettings: ["OPENAI_API_KEY", "OPENAI_MODEL"],
    safeNotes: [
      "A chave deve ficar somente no backend.",
      "A UI não deve exibir secrets.",
      "A troca de modelo deve respeitar estratégia de configuração por ambiente.",
    ],
  },
  {
    provider: "ollama",
    label: "Ollama",
    description:
      "Provider local para execução de modelos via Ollama, útil para desenvolvimento, privacidade local e experimentação offline.",
    requiredSettings: ["OLLAMA_BASE_URL", "OLLAMA_MODEL"],
    safeNotes: [
      "Não exige chave externa.",
      "Depende do serviço Ollama estar ativo.",
      "O modelo configurado precisa estar disponível localmente.",
    ],
  },
];

function getProviderLabel(provider: string): string {
  return (
    providerCatalog.find((item) => item.provider === provider)?.label ??
    provider
  );
}

function getStatusDescription(health: LLMHealthResponse | null): string {
  if (!health) {
    return "Status ainda não carregado.";
  }

  if (health.status === "configured") {
    return "Provider configurado para uso pelo backend.";
  }

  return "Provider com configuração incompleta.";
}

function getActiveProviderCard(
  health: LLMHealthResponse | null,
): ProviderSettingsViewModel | null {
  if (!health) {
    return null;
  }

  return (
    providerCatalog.find((item) => item.provider === health.provider) ?? null
  );
}

function renderRequiredSettings(provider: ProviderSettingsViewModel) {
  if (provider.requiredSettings.length === 0) {
    return <p className="muted">Nenhuma variável obrigatória para este provider.</p>;
  }

  return (
    <ul className="provider-settings-list">
      {provider.requiredSettings.map((setting) => (
        <li key={setting}>
          <code>{setting}</code>
        </li>
      ))}
    </ul>
  );
}

function renderProviderStatus(
  provider: ProviderSettingsViewModel,
  health: LLMHealthResponse | null,
) {
  if (!health || health.provider !== provider.provider) {
    return <span className="status-badge status-empty">available</span>;
  }

  if (health.status === "configured") {
    return <span className="status-badge status-healthy">active</span>;
  }

  return <span className="status-badge status-warning">missing config</span>;
}

export function ProviderSettingsPage() {
  const { errorMessage, health, providers, refresh, requestState } =
    useLLMSettings();

  const activeProvider = getActiveProviderCard(health);

  return (
    <div className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Configurações de provider</span>
          <h1>Configurações de Provider e Modelo</h1>
          <p>
            Visualize o provider LLM ativo, modelo configurado, health check e
            estratégia segura de configuração. Esta tela é read-only e não
            altera secrets ou variáveis de ambiente.
          </p>
        </div>

        <button
          className="secondary-button"
          disabled={requestState === "loading"}
          onClick={refresh}
          type="button"
        >
          {requestState === "loading" ? "Atualizando..." : "Atualizar status"}
        </button>
      </section>

      {requestState === "error" ? (
        <article className="alert-card">
          <strong>Não foi possível carregar configurações de provider.</strong>
          <p>Verifique se a API está rodando e se os endpoints LLM respondem.</p>
          <small>{errorMessage}</small>
        </article>
      ) : null}

      <section className="metrics-grid">
        <MetricCard
          description="Provider atualmente selecionado no backend"
          label="Active provider"
          value={providers?.active_provider ?? "loading"}
        />
        <MetricCard
          description="Modelo configurado para o provider ativo"
          label="Active model"
          value={health?.model ?? "not_configured"}
        />
        <MetricCard
          description={getStatusDescription(health)}
          label="Health status"
          value={health?.status ?? "loading"}
        />
        <MetricCard
          description="Providers suportados pela abstração LLM"
          label="Supported providers"
          value={providers?.supported_providers.length ?? 0}
        />
      </section>

      <section className="provider-settings-grid">
        <article className="provider-settings-card provider-settings-card-highlight">
          <div>
            <span className="eyebrow">Active configuration</span>
            <h2>{health ? getProviderLabel(health.provider) : "Carregando"}</h2>
            <p>{health?.message ?? "Carregando health check do provider."}</p>
          </div>

          {health ? (
            <StatusBadge status={health.status === "configured" ? "healthy" : "warning"} />
          ) : (
            <span className="status-badge status-empty">loading</span>
          )}

          <div className="provider-settings-meta">
            <span>
              Provider: <strong>{health?.provider ?? "-"}</strong>
            </span>
            <span>
              Model: <strong>{health?.model ?? "not_configured"}</strong>
            </span>
          </div>

          {health && health.missing_settings.length > 0 ? (
            <div className="provider-warning-panel">
              <span className="eyebrow">Missing settings</span>
              <ul>
                {health.missing_settings.map((setting) => (
                  <li key={setting}>
                    <code>{setting}</code>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {health ? (
            <JsonViewer title="Safe metadata" value={health.safe_metadata} />
          ) : null}
        </article>

        <article className="provider-settings-card">
          <span className="eyebrow">Safe configuration strategy</span>
          <h2>Estratégia segura</h2>
          <p>
            Esta tela mostra apenas dados seguros retornados pelo backend. Secrets
            como API keys não devem ser enviados para o frontend nem editados
            diretamente pela UI nesta etapa do M8.
          </p>

          <ul className="provider-settings-list">
            <li>Configuração real deve ser feita por variáveis de ambiente.</li>
            <li>Secrets devem ficar no backend ou em secret manager.</li>
            <li>A UI pode mostrar status, modelo e campos ausentes.</li>
            <li>Alterações write-enabled devem exigir autenticação e auditoria.</li>
          </ul>
        </article>
      </section>

      <section className="console-steps-card">
        <div>
          <span className="eyebrow">Provider catalog</span>
          <h2>Providers suportados</h2>
          <p className="muted">
            Catálogo read-only baseado nos providers suportados pela abstração
            atual do backend.
          </p>
        </div>

        <div className="provider-catalog-grid">
          {providerCatalog.map((provider) => {
            const isSupported =
              providers?.supported_providers.includes(provider.provider) ?? false;

            return (
              <article className="provider-catalog-card" key={provider.provider}>
                <div className="provider-catalog-header">
                  <div>
                    <span className="eyebrow">{provider.provider}</span>
                    <h3>{provider.label}</h3>
                  </div>

                  {renderProviderStatus(provider, health)}
                </div>

                <p>{provider.description}</p>

                <div>
                  <span className="eyebrow">Required settings</span>
                  {renderRequiredSettings(provider)}
                </div>

                <div>
                  <span className="eyebrow">Safe notes</span>
                  <ul className="provider-settings-list">
                    {provider.safeNotes.map((note) => (
                      <li key={note}>{note}</li>
                    ))}
                  </ul>
                </div>

                <small>
                  {isSupported
                    ? "Provider suportado pelo backend atual."
                    : "Provider não retornado pela API atual."}
                </small>
              </article>
            );
          })}
        </div>
      </section>

      <section className="content-grid">
        <JsonViewer title="Providers response" value={providers} />
        <JsonViewer title="Health response" value={health} />
      </section>

      {activeProvider ? (
        <section className="empty-state">
          <h2>Próximo passo planejado</h2>
          <p>
            Evoluir esta tela para permitir configuração controlada de provider e
            modelo somente depois da fundação de segurança, autenticação,
            autorização, audit logs e secrets management.
          </p>
        </section>
      ) : null}
    </div>
  );
}
