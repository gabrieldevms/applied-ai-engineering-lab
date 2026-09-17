import { getJson } from "./httpClient";
import type {
  EvaluationArtifact,
  EvaluationArtifactList,
  QualityScorecardsResponse,
} from "../types/productionObservability";

export function getQualityScorecards(): Promise<QualityScorecardsResponse> {
  return getJson<QualityScorecardsResponse>("/api/observability/quality-scorecards");
}

export function getEvaluationArtifacts(): Promise<EvaluationArtifactList> {
  return getJson<EvaluationArtifactList>("/api/evals/artifacts");
}

export function getEvaluationArtifact(artifactId: string): Promise<EvaluationArtifact> {
  return getJson<EvaluationArtifact>(`/api/evals/artifacts/${encodeURIComponent(artifactId)}`);
}
