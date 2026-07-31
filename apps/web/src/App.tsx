import { AppShell } from "./components/layout/AppShell";
import { CommandCenterPage } from "./pages/CommandCenterPage";

export default function App() {
  return (
    <AppShell>
      <CommandCenterPage />
    </AppShell>
  );
}
