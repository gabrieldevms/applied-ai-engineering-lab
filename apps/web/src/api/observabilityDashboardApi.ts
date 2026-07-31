import { getJson } from "./httpClient";
import type { ObservabilityDashboardResponse } from "../types/observability";

export function getObservabilityDashboard(): Promise<ObservabilityDashboardResponse> {
  return getJson<ObservabilityDashboardResponse>("/api/observability/dashboard");
}
