import { postJson } from "./httpClient";
import type {
  AIAgentExecutionRecord,
  AIAgentExecutionRecordRequest,
} from "../types/agentExecutionTelemetry";

export function recordAIAgentExecutionTelemetry(
  payload: AIAgentExecutionRecordRequest,
): Promise<AIAgentExecutionRecord> {
  return postJson<AIAgentExecutionRecordRequest, AIAgentExecutionRecord>(
    "/api/observability/agent-execution/records",
    payload,
  );
}
