import { useCallback, useEffect, useState } from "react";
import { getLLMHealth, getLLMProviders } from "../api/llmSettingsApi";
import type {
  LLMHealthResponse,
  LLMProvidersResponse,
} from "../types/llmSettings";

type LLMSettingsRequestState = "loading" | "success" | "error";

type LLMSettingsState = {
  providers: LLMProvidersResponse | null;
  health: LLMHealthResponse | null;
  requestState: LLMSettingsRequestState;
  errorMessage: string | null;
  refresh: () => void;
};

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "Erro inesperado ao carregar configurações de provider.";
}

function loadLLMSettings(): Promise<[LLMProvidersResponse, LLMHealthResponse]> {
  return Promise.all([getLLMProviders(), getLLMHealth()]);
}

export function useLLMSettings(): LLMSettingsState {
  const [providers, setProviders] = useState<LLMProvidersResponse | null>(null);
  const [health, setHealth] = useState<LLMHealthResponse | null>(null);
  const [requestState, setRequestState] =
    useState<LLMSettingsRequestState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSettingsSuccess = useCallback(
    ([providersResponse, healthResponse]: [
      LLMProvidersResponse,
      LLMHealthResponse,
    ]) => {
      setProviders(providersResponse);
      setHealth(healthResponse);
      setRequestState("success");
    },
    [],
  );

  const handleSettingsError = useCallback((error: unknown) => {
    setRequestState("error");
    setErrorMessage(getErrorMessage(error));
  }, []);

  const refresh = useCallback(() => {
    setRequestState("loading");
    setErrorMessage(null);

    loadLLMSettings().then(handleSettingsSuccess).catch(handleSettingsError);
  }, [handleSettingsError, handleSettingsSuccess]);

  useEffect(() => {
    loadLLMSettings().then(handleSettingsSuccess).catch(handleSettingsError);
  }, [handleSettingsError, handleSettingsSuccess]);

  return {
    providers,
    health,
    requestState,
    errorMessage,
    refresh,
  };
}
