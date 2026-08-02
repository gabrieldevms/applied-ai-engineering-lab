import { getJson } from "./httpClient";
import type {
  AIExecutionHistoryResponse,
  ExecutionHistoryFilters,
} from "../types/executionHistory";

function buildQueryString(filters: ExecutionHistoryFilters): string {
  const params = new URLSearchParams();

  if (filters.executionType) {
    params.set("execution_type", filters.executionType);
  }

  if (filters.status) {
    params.set("status", filters.status);
  }

  if (filters.component) {
    params.set("component", filters.component);
  }

  if (filters.runId) {
    params.set("run_id", filters.runId);
  }

  params.set("limit", String(filters.limit));

  return params.toString();
}

export function getExecutionHistory(
  filters: ExecutionHistoryFilters,
): Promise<AIExecutionHistoryResponse> {
  const queryString = buildQueryString(filters);

  return getJson<AIExecutionHistoryResponse>(
    `/api/observability/execution-history?${queryString}`,
  );
}
