import type { JsonValue } from "./qaAgent";

export type AIUsageProvider =
  | "openai"
  | "ollama"
  | "anthropic"
  | "google"
  | "fake"
  | "unknown";

export type AIUsageComponent =
  | "api"
  | "evaluation"
  | "llm"
  | "rag"
  | "agent"
  | "multi_agent"
  | "tool"
  | "mcp";

export type AIUsageRecordRequest = {
  provider?: AIUsageProvider;
  model_name: string;
  component: AIUsageComponent;
  operation: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  embedding_tokens?: number;
  total_tokens?: number | null;
  input_cost_per_1k_tokens_usd?: number | null;
  output_cost_per_1k_tokens_usd?: number | null;
  embedding_cost_per_1k_tokens_usd?: number | null;
  total_cost_usd?: number | null;
  currency?: string;
  run_id?: string | null;
  trace_id?: string | null;
  metadata?: Record<string, JsonValue>;
};

export type AIUsageRecord = {
  record_id: string;
  provider: AIUsageProvider;
  model_name: string;
  component: AIUsageComponent;
  operation: string;
  prompt_tokens: number;
  completion_tokens: number;
  embedding_tokens: number;
  total_tokens: number;
  input_cost_per_1k_tokens_usd?: number | null;
  output_cost_per_1k_tokens_usd?: number | null;
  embedding_cost_per_1k_tokens_usd?: number | null;
  input_cost_usd?: number | null;
  output_cost_usd?: number | null;
  embedding_cost_usd?: number | null;
  total_cost_usd?: number | null;
  currency: string;
  recorded_at: string;
  run_id?: string | null;
  trace_id?: string | null;
  metadata: Record<string, JsonValue>;
};

export type AIUsageRecordsResponse = {
  records: AIUsageRecord[];
  count: number;
  metadata: Record<string, JsonValue>;
};

export type AIUsageSummaryRequest = {
  records?: AIUsageRecord[] | null;
  metadata?: Record<string, JsonValue>;
};

export type AIUsageSummaryResponse = {
  record_count: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_embedding_tokens: number;
  total_tokens: number;
  total_cost_usd?: number | null;
  average_cost_usd?: number | null;
  provider_coverage: Record<string, number>;
  model_coverage: Record<string, number>;
  component_coverage: Record<string, number>;
  operation_coverage: Record<string, number>;
  risks: string[];
  metadata: Record<string, JsonValue>;
};
