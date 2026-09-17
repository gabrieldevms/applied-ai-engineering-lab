import { translateStatus } from "../../i18n/ptBr";
import type {
  DashboardSectionStatus,
  DashboardStatus,
} from "../../types/observability";
import type { QualityStatus } from "../../types/productionObservability";

type StatusBadgeProps = {
  status: DashboardStatus | DashboardSectionStatus | QualityStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`status-badge status-${status}`}>
      {translateStatus(status)}
    </span>
  );
}
