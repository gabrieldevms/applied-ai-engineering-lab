import type { ReactNode } from "react";
import { navigationLabels } from "../../i18n/ptBr";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">AI</span>
          <div>
            <strong>Quality Command Center</strong>
            <small>Applied AI Engineering Lab</small>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="Navegação principal">
          {navigationLabels.map((item) => (
            <button
              className={item === "Overview" ? "nav-item active" : "nav-item"}
              key={item}
              type="button"
            >
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
