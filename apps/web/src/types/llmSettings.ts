import type { JsonValue } from "./qaAgent";

export type LLMProviderStatus = "configured" | "missing_configuration";

export type LLMProvidersResponse = {
  supported_providers: string[];
  active_provider: string;
};

export type LLMHealthResponse = {
  provider: string;
  model?: string | null;
  status: LLMProviderStatus;
  missing_settings: string[];
  safe_metadata: Record<string, string>;
  message: string;
};

export type ProviderSettingsViewModel = {
  provider: string;
  label: string;
  description: string;
  requiredSettings: string[];
  safeNotes: string[];
  metadata?: Record<string, JsonValue>;
};
