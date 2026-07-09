from ai_api.config import Settings
from ai_api.llm.schemas import LLMHealthResponse, LLMProvidersResponse


SUPPORTED_LLM_PROVIDERS = ["fake", "openai", "ollama"]


def get_llm_providers_status(settings: Settings) -> LLMProvidersResponse:
    return LLMProvidersResponse(
        supported_providers=SUPPORTED_LLM_PROVIDERS,
        active_provider=settings.llm_provider,
    )


def get_llm_health_status(settings: Settings) -> LLMHealthResponse:
    if settings.llm_provider == "fake":
        return LLMHealthResponse(
            provider="fake",
            model="fake-llm-v1",
            status="configured",
            message="Fake LLM provider is configured.",
        )

    if settings.llm_provider == "openai":
        missing_settings = []

        if not settings.openai_api_key:
            missing_settings.append("OPENAI_API_KEY")

        if not settings.openai_model:
            missing_settings.append("OPENAI_MODEL")

        return LLMHealthResponse(
            provider="openai",
            model=settings.openai_model,
            status=(
                "missing_configuration"
                if missing_settings
                else "configured"
            ),
            missing_settings=missing_settings,
            message=(
                "OpenAI provider is missing required settings."
                if missing_settings
                else "OpenAI provider is configured."
            ),
        )

    if settings.llm_provider == "ollama":
        missing_settings = []

        if not settings.ollama_base_url.strip():
            missing_settings.append("OLLAMA_BASE_URL")

        if not settings.ollama_model.strip():
            missing_settings.append("OLLAMA_MODEL")

        return LLMHealthResponse(
            provider="ollama",
            model=settings.ollama_model,
            status=(
                "missing_configuration"
                if missing_settings
                else "configured"
            ),
            missing_settings=missing_settings,
            safe_metadata={
                "base_url": settings.ollama_base_url,
            },
            message=(
                "Ollama provider is missing required settings."
                if missing_settings
                else "Ollama provider is configured."
            ),
        )

    return LLMHealthResponse(
        provider=settings.llm_provider,
        status="missing_configuration",
        message="Unsupported LLM provider.",
    )
