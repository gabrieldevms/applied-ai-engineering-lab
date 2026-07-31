import { translateStatus } from "../../i18n/ptBr";
import type {
  DashboardSectionStatus,
  DashboardStatus,
} from "../../types/observability";

type StatusBadgeProps = {
  status: DashboardStatus | DashboardSectionStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`status-badge status-${status}`}>
      {translateStatus(status)}
    </span>
  );
}
