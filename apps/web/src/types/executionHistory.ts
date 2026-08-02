export type ExecutionHistoryType =
  | "evaluation_telemetry"
  | "usage"
  | "retrieval_quality"
  | "agent_execution"
  | "multi_agent_execution";

export type AIExecutionHistoryRecord = {
  execution_id: string;
  execution_type: ExecutionHistoryType;
  title: string;
  status: string;
  component: string;
  operation: string;
  run_id?: string | null;
  recorded_at: string;
  duration_ms?: number | null;
  quality_score?: number | null;
  summary: string;
  source_record_id: string;
  metadata: Record<string, unknown>;
};

export type AIExecutionHistoryResponse = {
  records: AIExecutionHistoryRecord[];
  count: number;
  metadata: Record<string, unknown>;
};

export type ExecutionHistoryFilters = {
  executionType: string;
  status: string;
  component: string;
  runId: string;
  limit: number;
};
