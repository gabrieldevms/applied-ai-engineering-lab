import type { JsonValue } from "./qaAgent";

export type DataAnalystAgentStatus = "completed" | "blocked";

export type SQLValidationStatus = "approved" | "blocked";

export type SQLExecutionStatus = "executed" | "blocked";

export type SQLWorkflowStatus = "executed" | "blocked";

export type DatabaseColumn = {
  name: string;
  data_type: string;
  description?: string | null;
  nullable?: boolean;
  primary_key?: boolean;
  foreign_key?: string | null;
  metadata?: Record<string, JsonValue>;
};

export type DatabaseTable = {
  name: string;
  description?: string | null;
  columns: DatabaseColumn[];
  metadata?: Record<string, JsonValue>;
};

export type DatabaseSchema = {
  name: string;
  description?: string | null;
  tables: DatabaseTable[];
  metadata?: Record<string, JsonValue>;
};

export type DatabaseTableData = {
  table_name: string;
  rows: Record<string, JsonValue>[];
  metadata?: Record<string, JsonValue>;
};

export type SQLSafetyViolation = {
  rule: string;
  message: string;
  severity: string;
  metadata: Record<string, JsonValue>;
};

export type SQLValidationResponse = {
  status: SQLValidationStatus;
  sql: string;
  normalized_sql: string;
  violations: SQLSafetyViolation[];
  metadata: Record<string, JsonValue>;
};

export type SQLGenerationCandidate = {
  sql: string;
  explanation: string;
  assumptions: string[];
  metadata: Record<string, JsonValue>;
};

export type NaturalLanguageSQLRequest = {
  question: string;
  database_schema: DatabaseSchema;
  language: string;
  metadata: Record<string, JsonValue>;
};

export type SQLGenerationResponse = {
  status: SQLValidationStatus;
  request: NaturalLanguageSQLRequest;
  candidate: SQLGenerationCandidate;
  validation: SQLValidationResponse;
  metadata: Record<string, JsonValue>;
};

export type SQLResultColumn = {
  name: string;
  data_type?: string | null;
  metadata: Record<string, JsonValue>;
};

export type SQLQueryEvidence = {
  query: string;
  row_count: number;
  column_count: number;
  truncated: boolean;
  metadata: Record<string, JsonValue>;
};

export type SQLExecutionResponse = {
  status: SQLExecutionStatus;
  sql: string;
  normalized_sql: string;
  validation: SQLValidationResponse;
  columns: SQLResultColumn[];
  rows: Record<string, JsonValue>[];
  row_count: number;
  truncated: boolean;
  evidence: SQLQueryEvidence;
  metadata: Record<string, JsonValue>;
};

export type SQLWorkflowResponse = {
  status: SQLWorkflowStatus;
  generation: SQLGenerationResponse;
  execution?: SQLExecutionResponse | null;
  evidence?: SQLQueryEvidence | null;
  metadata: Record<string, JsonValue>;
};

export type DataAnalystAgentTraceStep = {
  step: string;
  status: string;
  message: string;
  metadata: Record<string, JsonValue>;
};

export type DataAnalystAgentRequest = {
  objective: string;
  database_schema: DatabaseSchema;
  table_data?: DatabaseTableData[];
  language?: string;
  max_rows?: number;
  metadata?: Record<string, JsonValue>;
};

export type DataAnalystAgentResponse = {
  status: DataAnalystAgentStatus;
  agent_name: string;
  objective: string;
  answer: string;
  workflow: SQLWorkflowResponse;
  evidence?: SQLQueryEvidence | null;
  trace: DataAnalystAgentTraceStep[];
  metadata: Record<string, JsonValue>;
};
