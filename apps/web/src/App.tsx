import { useState } from "react";
import { AppShell } from "./components/layout/AppShell";
import { CommandCenterPage } from "./pages/CommandCenterPage";
import { EvaluationCenterPage } from "./pages/EvaluationCenterPage";
import { MultiAgentCopilotConsolePage } from "./pages/MultiAgentCopilotConsolePage";
import { ObservabilityCenterPage } from "./pages/ObservabilityCenterPage";
import { ProductPlaceholderPage } from "./pages/ProductPlaceholderPage";
import { QAAgentConsolePage } from "./pages/QAAgentConsolePage";
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

    return <ProductPlaceholderPage page={activePage} />;
  }

  return (
    <AppShell activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </AppShell>
  );
}
