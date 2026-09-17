import { useEffect, useState } from "react";
import { getQualityScorecards } from "../api/productionObservabilityApi";
import type { QualityScorecardsResponse } from "../types/productionObservability";

export function useQualityScorecards(refreshKey: string | null) {
  const [scorecards, setScorecards] = useState<QualityScorecardsResponse | null>(null);
  const [error, setError] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);

  useEffect(() => {
    if (!refreshKey) {
      return;
    }

    let cancelled = false;
    getQualityScorecards()
      .then((response) => {
        if (!cancelled) {
          setScorecards(response);
          setError(false);
          setLastUpdatedAt(new Date().toISOString());
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(true);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  return { scorecards, error, lastUpdatedAt };
}
