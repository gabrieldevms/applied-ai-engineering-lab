import { getJson } from "./httpClient";
import type {
  LLMHealthResponse,
  LLMProvidersResponse,
} from "../types/llmSettings";

export function getLLMProviders(): Promise<LLMProvidersResponse> {
  return getJson<LLMProvidersResponse>("/api/llm/providers");
}

export function getLLMHealth(): Promise<LLMHealthResponse> {
  return getJson<LLMHealthResponse>("/api/llm/health");
}
