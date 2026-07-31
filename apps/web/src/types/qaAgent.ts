export type JsonPrimitive = string | number | boolean | null;

export type JsonValue =
  | JsonPrimitive
  | JsonValue[]
  | { [key: string]: JsonValue };

export type AgentRunStatus =
  | "completed"
  | "failed"
  | "blocked"
  | "requires_approval";

export type QAAgentRunRequest = {
  requirement_text: string;
  knowledge_documents?: JsonValue[];
  data_validation?: JsonValue | null;
  language?: string;
  top_k?: number;
  chunk_size?: number;
  chunk_overlap?: number;
  max_steps?: number;
  metadata?: Record<string, JsonValue>;
};

export type AgentStep = {
  step_id?: string;
  tool_name?: string | null;
  status?: string;
  input?: JsonValue;
  output?: JsonValue;
  error?: string | null;
  metadata?: Record<string, JsonValue>;
  [key: string]: JsonValue | undefined;
};

export type QAAgentRunResponse = {
  run_id: string;
  status: AgentRunStatus;
  final_answer: string;
  requirement_analysis: Record<string, JsonValue>;
  retrieved_context?: Record<string, JsonValue> | null;
  data_validation_selection?: Record<string, JsonValue> | null;
  data_validation?: Record<string, JsonValue> | null;
  steps: AgentStep[];
  metadata: Record<string, JsonValue>;
};
