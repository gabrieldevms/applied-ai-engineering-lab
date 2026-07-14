from ai_api.config import Settings
from ai_api.llm.fake_provider import FakeLLMProvider
from ai_api.llm.ollama_provider import OllamaProvider
from ai_api.llm.openai_provider import OpenAIProvider
from ai_api.llm.providers import LLMProvider


def build_llm_provider(
    settings: Settings,
    fake_response_content: str | None = None,
) -> LLMProvider:
    if settings.llm_provider == "fake":
        return FakeLLMProvider(
            response_content=fake_response_content,
        )

    if settings.llm_provider == "openai":
        if not settings.openai_api_key or not settings.openai_api_key.strip():
            raise ValueError("OPENAI_API_KEY must be configured.")

        if not settings.openai_model or not settings.openai_model.strip():
            raise ValueError("OPENAI_MODEL must be configured.")

        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    if settings.llm_provider == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )

    raise ValueError(
        f"Unsupported LLM provider configured: {settings.llm_provider}"
    )
