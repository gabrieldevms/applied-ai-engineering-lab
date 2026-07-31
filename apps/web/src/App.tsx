import { useState } from "react";
import { AppShell } from "./components/layout/AppShell";
import { CommandCenterPage } from "./pages/CommandCenterPage";
import { DataAnalystConsolePage } from "./pages/DataAnalystConsolePage";
import { EvaluationCenterPage } from "./pages/EvaluationCenterPage";
import { MultiAgentCopilotConsolePage } from "./pages/MultiAgentCopilotConsolePage";
import { ObservabilityCenterPage } from "./pages/ObservabilityCenterPage";
import { ProductPlaceholderPage } from "./pages/ProductPlaceholderPage";
import { ProviderSettingsPage } from "./pages/ProviderSettingsPage";
import { QAAgentConsolePage } from "./pages/QAAgentConsolePage";
import { RAGConsolePage } from "./pages/RAGConsolePage";
import type { AppPage } from "./types/navigation";

export default function App() {
  const [activePage, setActivePage] = useState<AppPage>("overview");

  function renderPage() {
    if (activePage === "overview") {
      return <CommandCenterPage />;
    }

    if (activePage === "observability") {
      return <ObservabilityCenterPage />;
    }

    if (activePage === "evaluation") {
      return <EvaluationCenterPage />;
    }

    if (activePage === "qa-agent") {
      return <QAAgentConsolePage />;
    }

    if (activePage === "multi-agent-copilot") {
      return <MultiAgentCopilotConsolePage />;
    }

    if (activePage === "rag") {
      return <RAGConsolePage />;
    }

    if (activePage === "data-analyst") {
      return <DataAnalystConsolePage />;
    }

    if (activePage === "provider-settings") {
      return <ProviderSettingsPage />;
    }

    return <ProductPlaceholderPage page={activePage} />;
  }

  return (
    <AppShell activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </AppShell>
  );
}
