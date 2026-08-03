import type { JsonValue } from "./qaAgent";
import type { AIUsageComponent } from "./usageCost";

export type AIAgentTelemetryRunStatus =
  | "completed"
  | "partial"
  | "failed"
  | "blocked"
  | "cancelled";

export type AIAgentExecutionRecordRequest = {
  component?: AIUsageComponent;
  operation: string;
  agent_name: string;
  run_status: AIAgentTelemetryRunStatus;
  duration_ms?: number | null;
  step_count?: number;
  successful_step_count?: number;
  failed_step_count?: number;
  tool_call_count?: number;
  successful_tool_call_count?: number;
  failed_tool_call_count?: number;
  retry_count?: number;
  fallback_count?: number;
  error_count?: number;
  human_approval_request_count?: number;
  human_approval_granted_count?: number;
  max_duration_ms?: number | null;
  max_failed_steps?: number;
  max_failed_tool_calls?: number;
  max_error_count?: number;
  min_quality_score?: number;
  run_id?: string | null;
  trace_id?: string | null;
  metadata?: Record<string, JsonValue>;
};

export type AIAgentExecutionRecord = {
  record_id: string;
  component: AIUsageComponent;
  operation: string;
  agent_name: string;
  run_status: AIAgentTelemetryRunStatus;
  status: "passed" | "warning" | "failed";
  duration_ms?: number | null;
  step_count: number;
  successful_step_count: number;
  failed_step_count: number;
  tool_call_count: number;
  successful_tool_call_count: number;
  failed_tool_call_count: number;
  retry_count: number;
  fallback_count: number;
  error_count: number;
  human_approval_request_count: number;
  human_approval_granted_count: number;
  step_success_rate?: number | null;
  tool_success_rate?: number | null;
  human_approval_rate?: number | null;
  quality_score?: number | null;
  max_duration_ms?: number | null;
  max_failed_steps: number;
  max_failed_tool_calls: number;
  max_error_count: number;
  min_quality_score: number;
  risks: string[];
  recorded_at: string;
  run_id?: string | null;
  trace_id?: string | null;
  metadata: Record<string, JsonValue>;
};
