import { useCallback, useEffect, useState } from "react";
import {
  getAIUsageRecords,
  getAIUsageSummary,
  recordAIUsage,
} from "../api/usageCostApi";
import type {
  AIUsageRecordRequest,
  AIUsageRecordsResponse,
  AIUsageSummaryResponse,
} from "../types/usageCost";

type UsageCostRequestState = "loading" | "success" | "error";

type UsageCostState = {
  recordsResponse: AIUsageRecordsResponse | null;
  summary: AIUsageSummaryResponse | null;
  requestState: UsageCostRequestState;
  errorMessage: string | null;
  refresh: () => void;
  recordDemoUsage: () => Promise<void>;
};

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao carregar usage/cost.";
}

function loadUsageCost(): Promise<
  [AIUsageRecordsResponse, AIUsageSummaryResponse]
> {
  return Promise.all([getAIUsageRecords(), getAIUsageSummary()]);
}

function buildDemoUsageRecord(): AIUsageRecordRequest {
  return {
    provider: "fake",
    model_name: "fake-llm-v1",
    component: "agent",
    operation: "qa_agent_console_demo",
    prompt_tokens: 820,
    completion_tokens: 260,
    embedding_tokens: 0,
    input_cost_per_1k_tokens_usd: 0.0005,
    output_cost_per_1k_tokens_usd: 0.0015,
    embedding_cost_per_1k_tokens_usd: null,
    currency: "USD",
    run_id: `demo-run-${Date.now()}`,
    trace_id: `demo-trace-${Date.now()}`,
    metadata: {
      source: "ai-quality-command-center",
      console: "usage-cost",
      demo_record: true,
    },
  };
}

export function useUsageCost(): UsageCostState {
  const [recordsResponse, setRecordsResponse] =
    useState<AIUsageRecordsResponse | null>(null);
  const [summary, setSummary] = useState<AIUsageSummaryResponse | null>(null);
  const [requestState, setRequestState] =
    useState<UsageCostRequestState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSuccess = useCallback(
    ([recordsResult, summaryResult]: [
      AIUsageRecordsResponse,
      AIUsageSummaryResponse,
    ]) => {
      setRecordsResponse(recordsResult);
      setSummary(summaryResult);
      setRequestState("success");
    },
    [],
  );

  const handleError = useCallback((error: unknown) => {
    setRequestState("error");
    setErrorMessage(getErrorMessage(error));
  }, []);

  const refresh = useCallback(() => {
    setRequestState("loading");
    setErrorMessage(null);

    loadUsageCost().then(handleSuccess).catch(handleError);
  }, [handleError, handleSuccess]);

  const recordDemoUsage = useCallback(async () => {
    setRequestState("loading");
    setErrorMessage(null);

    try {
      await recordAIUsage(buildDemoUsageRecord());
      const usageCost = await loadUsageCost();
      handleSuccess(usageCost);
    } catch (error) {
      handleError(error);
    }
  }, [handleError, handleSuccess]);

  useEffect(() => {
    loadUsageCost().then(handleSuccess).catch(handleError);
  }, [handleError, handleSuccess]);

  return {
    recordsResponse,
    summary,
    requestState,
    errorMessage,
    refresh,
    recordDemoUsage,
  };
}
