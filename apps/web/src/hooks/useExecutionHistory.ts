import { useCallback, useEffect, useState } from "react";
import { getExecutionHistory } from "../api/executionHistoryApi";
import type {
  AIExecutionHistoryResponse,
  ExecutionHistoryFilters,
} from "../types/executionHistory";

type ExecutionHistoryRequestState = {
  isLoading: boolean;
  errorMessage: string | null;
};

type ExecutionHistoryState = {
  history: AIExecutionHistoryResponse | null;
  filters: ExecutionHistoryFilters;
  requestState: ExecutionHistoryRequestState;
  updateFilters: (filters: ExecutionHistoryFilters) => void;
  refreshHistory: () => Promise<void>;
};

const defaultFilters: ExecutionHistoryFilters = {
  executionType: "",
  status: "",
  component: "",
  runId: "",
  limit: 20,
};

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao carregar o histórico de execuções.";
}

export function useExecutionHistory(): ExecutionHistoryState {
  const [history, setHistory] = useState<AIExecutionHistoryResponse | null>(
    null,
  );
  const [filters, setFilters] = useState<ExecutionHistoryFilters>(
    defaultFilters,
  );
  const [requestState, setRequestState] =
    useState<ExecutionHistoryRequestState>({
      isLoading: true,
      errorMessage: null,
    });

  useEffect(() => {
    let shouldIgnore = false;

    getExecutionHistory(filters)
      .then((response) => {
        if (shouldIgnore) {
          return;
        }

        setHistory(response);
        setRequestState({
          isLoading: false,
          errorMessage: null,
        });
      })
      .catch((error: unknown) => {
        if (shouldIgnore) {
          return;
        }

        setRequestState({
          isLoading: false,
          errorMessage: getErrorMessage(error),
        });
      });

    return () => {
      shouldIgnore = true;
    };
  }, [filters]);

  const updateFilters = useCallback((nextFilters: ExecutionHistoryFilters) => {
    setRequestState({
      isLoading: true,
      errorMessage: null,
    });
    setFilters(nextFilters);
  }, []);

  const refreshHistory = useCallback(async () => {
    setRequestState({
      isLoading: true,
      errorMessage: null,
    });

    try {
      const response = await getExecutionHistory(filters);
      setHistory(response);
      setRequestState({
        isLoading: false,
        errorMessage: null,
      });
    } catch (error) {
      setRequestState({
        isLoading: false,
        errorMessage: getErrorMessage(error),
      });
    }
  }, [filters]);

  return {
    history,
    filters,
    requestState,
    updateFilters,
    refreshHistory,
  };
}
