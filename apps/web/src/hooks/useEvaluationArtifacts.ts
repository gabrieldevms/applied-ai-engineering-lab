import { useEffect, useState } from "react";
import {
  getEvaluationArtifact,
  getEvaluationArtifacts,
} from "../api/productionObservabilityApi";
import type {
  EvaluationArtifact,
  EvaluationArtifactList,
} from "../types/productionObservability";

export function useEvaluationArtifacts(refreshKey: string | null) {
  const [artifactList, setArtifactList] = useState<EvaluationArtifactList | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [artifact, setArtifact] = useState<EvaluationArtifact | null>(null);
  const [listError, setListError] = useState(false);
  const [detailError, setDetailError] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);

  useEffect(() => {
    if (!refreshKey) {
      return;
    }

    let cancelled = false;
    getEvaluationArtifacts()
      .then((response) => {
        if (!cancelled) {
          setArtifactList(response);
          setSelectedId((current) =>
            current && response.artifacts.some((item) => item.artifact_id === current)
              ? current
              : (response.artifacts[0]?.artifact_id ?? null),
          );
          setListError(false);
          setLastUpdatedAt(new Date().toISOString());
        }
      })
      .catch(() => {
        if (!cancelled) {
          setListError(true);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  useEffect(() => {
    if (!selectedId) {
      return;
    }

    let cancelled = false;
    getEvaluationArtifact(selectedId)
      .then((response) => {
        if (!cancelled) {
          setArtifact(response);
          setDetailError(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDetailError(true);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedId, refreshKey]);

  return {
    artifactList,
    selectedId,
    selectArtifact: setSelectedId,
    artifact: artifact?.artifact_id === selectedId ? artifact : null,
    listError,
    detailError,
    lastUpdatedAt,
  };
}
