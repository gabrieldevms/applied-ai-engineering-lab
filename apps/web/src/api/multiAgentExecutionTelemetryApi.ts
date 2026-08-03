import { postJson } from "./httpClient";
import type {
  AIMultiAgentExecutionRecord,
  AIMultiAgentExecutionRecordRequest,
} from "../types/multiAgentExecutionTelemetry";

export function recordAIMultiAgentExecutionTelemetry(
  payload: AIMultiAgentExecutionRecordRequest,
): Promise<AIMultiAgentExecutionRecord> {
  return postJson<
    AIMultiAgentExecutionRecordRequest,
    AIMultiAgentExecutionRecord
  >("/api/observability/multi-agent-execution/records", payload);
}
