export type LLMProviderStatus = "configured" | "missing_configuration";

export type LLMSafeConfigurationField = {
  name: string;
  label: string;
  required: boolean;
  configured: boolean;
  sensitive: boolean;
};

export type LLMProvidersResponse = {
  supported_providers: string[];
  active_provider: string;
};

export type LLMHealthResponse = {
  provider: string;
  model: string | null;
  status: LLMProviderStatus;
  configured: boolean;
  missing_settings: string[];
  safe_settings: LLMSafeConfigurationField[];
  safe_metadata: Record<string, string>;
  message: string;
  security_note: string;
};

export type ProviderSettingsViewModel = {
  provider: string;
  label: string;
  description: string;
  requiredSettings: string[];
  safeNotes: string[];
};
