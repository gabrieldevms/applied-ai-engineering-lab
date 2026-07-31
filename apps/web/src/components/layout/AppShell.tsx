import type { ReactNode } from "react";
import { navigationItems } from "../../i18n/ptBr";
import type { AppPage } from "../../types/navigation";

type AppShellProps = {
  activePage: AppPage;
  children: ReactNode;
  onNavigate: (page: AppPage) => void;
};

export function AppShell({ activePage, children, onNavigate }: AppShellProps) {
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
          {navigationItems.map((item) => {
            const isActive = item.page === activePage;

            return (
              <button
                aria-current={isActive ? "page" : undefined}
                className={isActive ? "nav-item active" : "nav-item"}
                key={item.page}
                onClick={() => onNavigate(item.page)}
                type="button"
              >
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
