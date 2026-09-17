export type QualityStatus = "healthy" | "warning" | "critical" | "no_data";
export type TrendSignal = "improving" | "stable" | "degrading" | "insufficient_data";
export type EvaluationStatus = "passed" | "warning" | "failed";

export type EvaluationArtifactSummary = {
  artifact_id: string;
  created_at: string;
  source: "api" | "script";
  status: EvaluationStatus;
  score: number | null;
  stage_count: number;
  passed_count: number;
  warning_count: number;
  failed_count: number;
};

export type EvaluationArtifact = EvaluationArtifactSummary & {
  should_fail_ci: boolean;
  stages: { name: string; status: EvaluationStatus; score: number | null }[];
  risks: string[];
  recommendations: string[];
};

export type EvaluationArtifactList = {
  artifacts: EvaluationArtifactSummary[];
  total: number;
};

export type QualityScorecardSection = {
  name: string;
  title: string;
  status: QualityStatus;
  latest_observed_at: string | null;
  metrics: Record<string, number | null>;
  trend: {
    signal: TrendSignal;
    window_days: number;
    recent_count: number;
    previous_count: number;
    recent_adverse_rate: number | null;
    previous_adverse_rate: number | null;
  };
  notes: string[];
};

export type QualityScorecardsResponse = {
  generated_at: string;
  sections: QualityScorecardSection[];
  latest_evaluation_artifact: EvaluationArtifactSummary | null;
};
