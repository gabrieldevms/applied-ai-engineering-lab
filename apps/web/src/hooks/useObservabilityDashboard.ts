import { useCallback, useEffect, useState } from "react";
import { getObservabilityDashboard } from "../api/observabilityDashboardApi";
import type { ObservabilityDashboardResponse } from "../types/observability";

type RequestState = "idle" | "loading" | "refreshing" | "success" | "error";

const defaultRefreshIntervalMs = 30000;

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao carregar o dashboard.";
}

export function useObservabilityDashboard() {
  const [dashboard, setDashboard] =
    useState<ObservabilityDashboardResponse | null>(null);
  const [requestState, setRequestState] = useState<RequestState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(false);
  const [refreshIntervalMs] = useState(defaultRefreshIntervalMs);

  const loadDashboard = useCallback(async (mode: "initial" | "refresh") => {
    setRequestState((currentState) => {
      if (mode === "initial") {
        return "loading";
      }

      return currentState === "loading" ? "loading" : "refreshing";
    });
    setErrorMessage(null);

    try {
      const response = await getObservabilityDashboard();

      setDashboard(response);
      setLastUpdatedAt(new Date().toISOString());
      setRequestState("success");
    } catch (error) {
      setRequestState("error");
      setErrorMessage(getErrorMessage(error));
    }
  }, []);

  useEffect(() => {
    let shouldIgnoreResult = false;

    getObservabilityDashboard()
      .then((response) => {
        if (shouldIgnoreResult) {
          return;
        }

        setDashboard(response);
        setLastUpdatedAt(new Date().toISOString());
        setRequestState("success");
      })
      .catch((error: unknown) => {
        if (shouldIgnoreResult) {
          return;
        }

        setRequestState("error");
        setErrorMessage(getErrorMessage(error));
      });

    return () => {
      shouldIgnoreResult = true;
    };
  }, []);

  useEffect(() => {
    if (!isAutoRefreshEnabled) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      void loadDashboard("refresh");
    }, refreshIntervalMs);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [isAutoRefreshEnabled, loadDashboard, refreshIntervalMs]);

  const refreshDashboard = useCallback(async () => {
    await loadDashboard("refresh");
  }, [loadDashboard]);

  const toggleAutoRefresh = useCallback(() => {
    setIsAutoRefreshEnabled((currentValue) => !currentValue);
  }, []);

  return {
    dashboard,
    requestState,
    errorMessage,
    lastUpdatedAt,
    isAutoRefreshEnabled,
    refreshIntervalMs,
    refreshDashboard,
    toggleAutoRefresh,
  };
}
