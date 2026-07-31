import { postJson } from "./httpClient";
import type {
  MultiAgentQACopilotRequest,
  MultiAgentQACopilotResponse,
} from "../types/multiAgentCopilot";

export function runMultiAgentQACopilot(
  payload: MultiAgentQACopilotRequest,
): Promise<MultiAgentQACopilotResponse> {
  return postJson<MultiAgentQACopilotRequest, MultiAgentQACopilotResponse>(
    "/api/multi-agent/qa-copilot/run",
    payload,
  );
}
