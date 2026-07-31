import { useState } from "react";
import { AppShell } from "./components/layout/AppShell";
import { CommandCenterPage } from "./pages/CommandCenterPage";
import { EvaluationCenterPage } from "./pages/EvaluationCenterPage";
import { ObservabilityCenterPage } from "./pages/ObservabilityCenterPage";
import { ProductPlaceholderPage } from "./pages/ProductPlaceholderPage";
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

    return <ProductPlaceholderPage page={activePage} />;
  }

  return (
    <AppShell activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </AppShell>
  );
}
