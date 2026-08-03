import { JsonViewer } from "../components/ui/JsonViewer";
import { MetricCard } from "../components/ui/MetricCard";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useLLMSettings } from "../hooks/useLLMSettings";
import type {
  LLMHealthResponse,
  LLMSafeConfigurationField,
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
      "Não chama serviços externos.",
      "Não representa a qualidade real de resposta de um modelo externo.",
    ],
  },
  {
    provider: "openai",
    label: "OpenAI",
    description:
      "Provider externo para execução real de chamadas LLM usando configuração segura do backend.",
    requiredSettings: [
      "Credencial backend configurada",
      "Modelo backend configurado",
    ],
    safeNotes: [
      "A credencial deve ficar somente no backend.",
      "A UI não exibe API keys, tokens ou valores de env vars.",
      "A troca de modelo deve respeitar estratégia de configuração por ambiente.",
      "O uso pode gerar custo em provedor externo.",
    ],
  },
  {
    provider: "ollama",
    label: "Ollama",
    description:
      "Provider local para execução de modelos via Ollama, útil para desenvolvimento, privacidade local e experimentação offline.",
    requiredSettings: [
      "Base URL backend configurada",
      "Modelo local configurado",
    ],
    safeNotes: [
      "Não exige chave externa.",
      "Depende do serviço Ollama estar ativo.",
      "A UI não exibe a URL interna configurada.",
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
    return (
      <p className="muted">Nenhuma configuração obrigatória para este provider.</p>
    );
  }

  return (
    <ul className="provider-settings-list">
      {provider.requiredSettings.map((setting) => (
        <li key={setting}>{setting}</li>
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

function renderSafeSettings(settings: LLMSafeConfigurationField[]) {
  if (settings.length === 0) {
    return <p className="muted">Nenhum campo de configuração retornado.</p>;
  }

  return (
    <ul className="provider-settings-list">
      {settings.map((setting) => (
        <li key={setting.name}>
          <strong>{setting.label}</strong>{" "}
          <span>
            — {setting.configured ? "configurado" : "pendente"}
            {setting.sensitive ? " · sensível · valor oculto" : ""}
          </span>
        </li>
      ))}
    </ul>
  );
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
            estratégia segura de configuração. Esta tela é read-only e não altera
            secrets, credenciais ou variáveis de ambiente.
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
            <StatusBadge
              status={health.status === "configured" ? "healthy" : "warning"}
            />
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
            <span>
              Configured:{" "}
              <strong>{health?.configured ? "yes" : "no"}</strong>
            </span>
          </div>

          {health && health.missing_settings.length > 0 ? (
            <div className="provider-warning-panel">
              <span className="eyebrow">Missing safe settings</span>
              <ul>
                {health.missing_settings.map((setting) => (
                  <li key={setting}>{setting}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {health ? (
            <div>
              <span className="eyebrow">Safe configuration fields</span>
              {renderSafeSettings(health.safe_settings)}
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
            como API keys, tokens e valores de variáveis de ambiente não devem ser
            enviados para o frontend nem editados diretamente pela UI nesta etapa
            do M8.
          </p>

          <ul className="provider-settings-list">
            <li>Configuração real deve ser feita por variáveis de ambiente.</li>
            <li>Secrets devem ficar no backend ou em secret manager.</li>
            <li>A UI pode mostrar status, modelo e campos lógicos ausentes.</li>
            <li>Valores sensíveis devem ser ocultados mesmo quando configurados.</li>
            <li>Alterações write-enabled devem exigir autenticação e auditoria.</li>
          </ul>

          {health ? <p className="muted">{health.security_note}</p> : null}
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
                  <span className="eyebrow">Required safe settings</span>
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
        <JsonViewer title="Sanitized health response" value={health} />
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
