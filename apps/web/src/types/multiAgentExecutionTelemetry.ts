import type { JsonValue } from "./qaAgent";
import type { AIUsageComponent } from "./usageCost";

export type AIMultiAgentTelemetryRunStatus =
  | "completed"
  | "partial"
  | "failed"
  | "blocked"
  | "cancelled";

export type AIMultiAgentExecutionRecordRequest = {
  component?: AIUsageComponent;
  operation: string;
  workflow_name: string;
  run_status: AIMultiAgentTelemetryRunStatus;
  duration_ms?: number | null;

  agent_count?: number;
  completed_agent_count?: number;
  failed_agent_count?: number;
  skipped_agent_count?: number;

  task_count?: number;
  successful_task_count?: number;
  failed_task_count?: number;

  artifact_count?: number;
  expected_min_artifacts?: number;

  handoff_count?: number;
  failed_handoff_count?: number;

  contract_check_count?: number;
  passed_contract_check_count?: number;
  failed_contract_check_count?: number;

  conflict_count?: number;
  critical_conflict_count?: number;

  failure_count?: number;
  error_count?: number;

  final_report_section_count?: number;
  expected_min_final_report_sections?: number;

  data_validation_evidence_count?: number;
  require_data_validation_evidence?: boolean;

  retry_count?: number;
  fallback_count?: number;

  max_duration_ms?: number | null;
  max_failed_agents?: number;
  max_failed_tasks?: number;
  max_failed_handoffs?: number;
  max_failed_contract_checks?: number;
  max_critical_conflicts?: number;
  max_failures?: number;
  max_errors?: number;
  min_quality_score?: number;

  run_id?: string | null;
  trace_id?: string | null;
  metadata?: Record<string, JsonValue>;
};

export type AIMultiAgentExecutionRecord = {
  record_id: string;
  component: AIUsageComponent;
  operation: string;
  workflow_name: string;
  run_status: AIMultiAgentTelemetryRunStatus;
  status: "passed" | "warning" | "failed";
  duration_ms?: number | null;

  agent_count: number;
  completed_agent_count: number;
  failed_agent_count: number;
  skipped_agent_count: number;

  task_count: number;
  successful_task_count: number;
  failed_task_count: number;

  artifact_count: number;
  expected_min_artifacts: number;

  handoff_count: number;
  failed_handoff_count: number;

  contract_check_count: number;
  passed_contract_check_count: number;
  failed_contract_check_count: number;

  conflict_count: number;
  critical_conflict_count: number;

  failure_count: number;
  error_count: number;

  final_report_section_count: number;
  expected_min_final_report_sections: number;

  data_validation_evidence_count: number;
  require_data_validation_evidence: boolean;

  retry_count: number;
  fallback_count: number;

  agent_success_rate?: number | null;
  task_success_rate?: number | null;
  handoff_success_rate?: number | null;
  contract_success_rate?: number | null;
  artifact_coverage_score?: number | null;
  final_report_coverage_score?: number | null;
  data_validation_score?: number | null;
  quality_score?: number | null;

  max_duration_ms?: number | null;
  max_failed_agents: number;
  max_failed_tasks: number;
  max_failed_handoffs: number;
  max_failed_contract_checks: number;
  max_critical_conflicts: number;
  max_failures: number;
  max_errors: number;
  min_quality_score: number;

  risks: string[];
  recorded_at: string;
  run_id?: string | null;
  trace_id?: string | null;
  metadata: Record<string, JsonValue>;
};
