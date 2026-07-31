import { useEffect, useState } from "react";
import { getObservabilityDashboard } from "../api/observabilityDashboardApi";
import type { ObservabilityDashboardResponse } from "../types/observability";

type RequestState = "idle" | "loading" | "success" | "error";

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

  useEffect(() => {
    let shouldIgnoreResult = false;

    getObservabilityDashboard()
      .then((response) => {
        if (shouldIgnoreResult) {
          return;
        }

        setDashboard(response);
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

  async function refreshDashboard() {
    setRequestState("loading");
    setErrorMessage(null);

    try {
      const response = await getObservabilityDashboard();

      setDashboard(response);
      setRequestState("success");
    } catch (error) {
      setRequestState("error");
      setErrorMessage(getErrorMessage(error));
    }
  }

  return {
    dashboard,
    requestState,
    errorMessage,
    refreshDashboard,
  };
}
