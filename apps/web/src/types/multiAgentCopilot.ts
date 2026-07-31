import type { JsonValue } from "./qaAgent";

export type MultiAgentQACopilotStatus =
  | "completed"
  | "failed"
  | "partial"
  | "blocked";

export type MultiAgentStepStatus =
  | "completed"
  | "failed"
  | "skipped"
  | "blocked"
  | "warning";

export type MultiAgentFailureStrategy =
  | "stop_on_failure"
  | "continue_with_warnings";

export type MultiAgentRoleName =
  | "orchestrator"
  | "requirement_analyst"
  | "functional_qa"
  | "test_automation"
  | "reviewer"
  | "report";

export type MultiAgentRoleDescriptor = {
  name: MultiAgentRoleName;
  title: string;
  responsibility: string;
  inputs: string[];
  outputs: string[];
  metadata: Record<string, JsonValue>;
};

export type MultiAgentMessage = {
  sender: MultiAgentRoleName;
  recipient: string;
  content: string;
  metadata: Record<string, JsonValue>;
};

export type MultiAgentArtifact = {
  name: string;
  produced_by: MultiAgentRoleName;
  content: Record<string, JsonValue>;
  metadata: Record<string, JsonValue>;
};

export type MultiAgentSharedState = {
  objective: string;
  requirement_text: string;
  language: string;
  context: Record<string, JsonValue>;
  artifacts: MultiAgentArtifact[];
  messages: MultiAgentMessage[];
  metadata: Record<string, JsonValue>;
};

export type MultiAgentTaskResult = {
  agent_name: MultiAgentRoleName;
  status: MultiAgentStepStatus;
  summary: string;
  artifacts: MultiAgentArtifact[];
  messages: MultiAgentMessage[];
  metadata: Record<string, JsonValue>;
};

export type MultiAgentFinalReport = {
  summary: string;
  requirement_understanding: string[];
  functional_coverage: string[];
  automation_strategy: string[];
  data_validation_evidence: string[];
  review_notes: string[];
  next_steps: string[];
  metadata: Record<string, JsonValue>;
};

export type MultiAgentTraceStep = {
  step_name: string;
  agent_name: MultiAgentRoleName;
  status: MultiAgentStepStatus;
  summary: string;
  metadata: Record<string, JsonValue>;
};

export type MultiAgentContractCheckResult = {
  contract_name: string;
  status: string;
  source_agent: MultiAgentRoleName;
  target_agent: MultiAgentRoleName | "shared_state";
  missing_artifacts: string[];
  message_found: boolean;
  summary: string;
  metadata: Record<string, JsonValue>;
};

export type MultiAgentContractValidationResponse = {
  status: string;
  total_contracts: number;
  passed_contracts: number;
  warning_contracts: number;
  failed_contracts: number;
  checks: MultiAgentContractCheckResult[];
  metadata: Record<string, JsonValue>;
};

export type MultiAgentFailureRecord = {
  agent_name: MultiAgentRoleName;
  error_type: string;
  message: string;
  severity: string;
  metadata: Record<string, JsonValue>;
};

export type MultiAgentConflictRecord = {
  conflict_type: string;
  severity: string;
  artifact_name?: string | null;
  involved_agents: MultiAgentRoleName[];
  summary: string;
  metadata: Record<string, JsonValue>;
};

export type MultiAgentConflictAnalysisResponse = {
  status: string;
  conflict_count: number;
  warning_count: number;
  critical_count: number;
  conflicts: MultiAgentConflictRecord[];
  metadata: Record<string, JsonValue>;
};

export type MultiAgentQACopilotRequest = {
  requirement_text: string;
  objective?: string | null;
  language?: string;
  context?: Record<string, JsonValue>;
  data_validation?: Record<string, JsonValue> | null;
  max_agents?: number;
  failure_strategy?: MultiAgentFailureStrategy;
  metadata?: Record<string, JsonValue>;
};

export type MultiAgentQACopilotResponse = {
  status: MultiAgentQACopilotStatus;
  copilot_name: string;
  objective: string;
  roles: MultiAgentRoleDescriptor[];
  shared_state: MultiAgentSharedState;
  task_results: MultiAgentTaskResult[];
  final_report: MultiAgentFinalReport;
  trace: MultiAgentTraceStep[];
  contract_validation?: MultiAgentContractValidationResponse | null;
  failures: MultiAgentFailureRecord[];
  conflict_analysis?: MultiAgentConflictAnalysisResponse | null;
  metadata: Record<string, JsonValue>;
};
