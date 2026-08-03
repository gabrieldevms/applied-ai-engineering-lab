import { postJson } from "./httpClient";
import type {
  AIRetrievalQualityRecord,
  AIRetrievalQualityRecordRequest,
} from "../types/retrievalQualityTelemetry";

export function recordAIRetrievalQualityTelemetry(
  payload: AIRetrievalQualityRecordRequest,
): Promise<AIRetrievalQualityRecord> {
  return postJson<AIRetrievalQualityRecordRequest, AIRetrievalQualityRecord>(
    "/api/observability/retrieval-quality/records",
    payload,
  );
}
