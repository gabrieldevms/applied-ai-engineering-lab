from ai_api.config import Settings
from ai_api.llm.schemas import (
    LLMHealthResponse,
    LLMProvidersResponse,
    LLMSafeConfigurationField,
)


SUPPORTED_LLM_PROVIDERS = ["fake", "openai", "ollama"]


def get_llm_providers_status(settings: Settings) -> LLMProvidersResponse:
    return LLMProvidersResponse(
        supported_providers=SUPPORTED_LLM_PROVIDERS,
        active_provider=settings.llm_provider,
    )


def get_llm_health_status(settings: Settings) -> LLMHealthResponse:
    if settings.llm_provider == "fake":
        return _get_fake_provider_status()

    if settings.llm_provider == "openai":
        return _get_openai_provider_status(settings)

    if settings.llm_provider == "ollama":
        return _get_ollama_provider_status(settings)

    return LLMHealthResponse(
        provider=settings.llm_provider,
        status="missing_configuration",
        configured=False,
        missing_settings=["supported_provider"],
        safe_settings=[],
        safe_metadata={
            "configuration_scope": "backend_owned",
            "secrets_exposed": "false",
        },
        message="Unsupported LLM provider.",
    )


def _get_fake_provider_status() -> LLMHealthResponse:
    return LLMHealthResponse(
        provider="fake",
        model="fake-llm-v1",
        status="configured",
        configured=True,
        safe_settings=[
            LLMSafeConfigurationField(
                name="provider_mode",
                label="Fake provider mode",
                required=True,
                configured=True,
                sensitive=False,
            )
        ],
        safe_metadata={
            "configuration_scope": "backend_owned",
            "external_network_access": "false",
            "secrets_required": "false",
            "secrets_exposed": "false",
        },
        message="Fake LLM provider is configured.",
    )


def _get_openai_provider_status(settings: Settings) -> LLMHealthResponse:
    credential_configured = _is_configured(settings.openai_api_key)
    model_configured = _is_configured(settings.openai_model)

    missing_settings = []

    if not credential_configured:
        missing_settings.append("credentials")

    if not model_configured:
        missing_settings.append("model")

    configured = len(missing_settings) == 0

    return LLMHealthResponse(
        provider="openai",
        model=settings.openai_model if model_configured else None,
        status="configured" if configured else "missing_configuration",
        configured=configured,
        missing_settings=missing_settings,
        safe_settings=[
            LLMSafeConfigurationField(
                name="credentials",
                label="OpenAI backend credentials",
                required=True,
                configured=credential_configured,
                sensitive=True,
            ),
            LLMSafeConfigurationField(
                name="model",
                label="OpenAI model identifier",
                required=True,
                configured=model_configured,
                sensitive=False,
            ),
        ],
        safe_metadata={
            "configuration_scope": "backend_owned",
            "external_network_access": "true",
            "secrets_required": "true",
            "secrets_exposed": "false",
        },
        message=(
            "OpenAI provider is missing required backend configuration."
            if missing_settings
            else "OpenAI provider is configured."
        ),
    )


def _get_ollama_provider_status(settings: Settings) -> LLMHealthResponse:
    base_url_configured = _is_configured(settings.ollama_base_url)
    model_configured = _is_configured(settings.ollama_model)

    missing_settings = []

    if not base_url_configured:
        missing_settings.append("base_url")

    if not model_configured:
        missing_settings.append("model")

    configured = len(missing_settings) == 0

    return LLMHealthResponse(
        provider="ollama",
        model=settings.ollama_model if model_configured else None,
        status="configured" if configured else "missing_configuration",
        configured=configured,
        missing_settings=missing_settings,
        safe_settings=[
            LLMSafeConfigurationField(
                name="base_url",
                label="Ollama backend base URL",
                required=True,
                configured=base_url_configured,
                sensitive=False,
            ),
            LLMSafeConfigurationField(
                name="model",
                label="Ollama local model",
                required=True,
                configured=model_configured,
                sensitive=False,
            ),
        ],
        safe_metadata={
            "configuration_scope": "backend_owned",
            "external_network_access": "local_or_configured",
            "base_url_configured": str(base_url_configured).lower(),
            "secrets_required": "false",
            "secrets_exposed": "false",
        },
        message=(
            "Ollama provider is missing required backend configuration."
            if missing_settings
            else "Ollama provider is configured."
        ),
    )


def _is_configured(value: str | None) -> bool:
    return bool(value and value.strip())
