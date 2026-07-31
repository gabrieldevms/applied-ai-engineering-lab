import { postJson } from "./httpClient";
import type { QAAgentRunRequest, QAAgentRunResponse } from "../types/qaAgent";

export function runQAAgent(
  payload: QAAgentRunRequest,
): Promise<QAAgentRunResponse> {
  return postJson<QAAgentRunRequest, QAAgentRunResponse>(
    "/api/agents/qa/run",
    payload,
  );
}
