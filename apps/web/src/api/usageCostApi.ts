import { getJson, postJson } from "./httpClient";
import type {
  AIUsageRecord,
  AIUsageRecordRequest,
  AIUsageRecordsResponse,
  AIUsageSummaryResponse,
} from "../types/usageCost";

export function getAIUsageRecords(): Promise<AIUsageRecordsResponse> {
  return getJson<AIUsageRecordsResponse>("/api/observability/usage/records");
}

export function getAIUsageSummary(): Promise<AIUsageSummaryResponse> {
  return getJson<AIUsageSummaryResponse>("/api/observability/usage/summary");
}

export function recordAIUsage(
  payload: AIUsageRecordRequest,
): Promise<AIUsageRecord> {
  return postJson<AIUsageRecordRequest, AIUsageRecord>(
    "/api/observability/usage/records",
    payload,
  );
}
