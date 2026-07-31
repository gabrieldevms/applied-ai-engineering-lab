import { postJson } from "./httpClient";
import type {
  DataAnalystAgentRequest,
  DataAnalystAgentResponse,
} from "../types/dataAnalyst";

export function runDataAnalystAgent(
  payload: DataAnalystAgentRequest,
): Promise<DataAnalystAgentResponse> {
  return postJson<DataAnalystAgentRequest, DataAnalystAgentResponse>(
    "/api/data-analysis/agent/run",
    payload,
  );
}
