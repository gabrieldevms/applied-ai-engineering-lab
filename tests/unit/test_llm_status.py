from ai_api.config import Settings
from ai_api.llm import get_llm_health_status, get_llm_providers_status


def test_llm_providers_status_should_return_supported_and_active_provider() -> None:
    settings = Settings(_env_file=None, llm_provider="ollama")

    response = get_llm_providers_status(settings)

    assert response.active_provider == "ollama"
    assert response.supported_providers == ["fake", "openai", "ollama"]


def test_llm_health_status_should_return_fake_as_configured() -> None:
    settings = Settings(_env_file=None)

    response = get_llm_health_status(settings)

    assert response.provider == "fake"
    assert response.model == "fake-llm-v1"
    assert response.status == "configured"
    assert response.missing_settings == []


def test_llm_health_status_should_detect_missing_openai_settings() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="openai",
        openai_api_key=None,
        openai_model=None,
    )

    response = get_llm_health_status(settings)

    assert response.provider == "openai"
    assert response.status == "missing_configuration"
    assert response.missing_settings == ["OPENAI_API_KEY", "OPENAI_MODEL"]


def test_llm_health_status_should_return_openai_as_configured() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="openai",
        openai_api_key="fake-key",
        openai_model="gpt-5.4-mini",
    )

    response = get_llm_health_status(settings)

    assert response.provider == "openai"
    assert response.model == "gpt-5.4-mini"
    assert response.status == "configured"
    assert response.missing_settings == []


def test_llm_health_status_should_return_ollama_as_configured() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="ollama",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.1",
    )

    response = get_llm_health_status(settings)

    assert response.provider == "ollama"
    assert response.model == "llama3.1"
    assert response.status == "configured"
    assert response.safe_metadata["base_url"] == "http://localhost:11434"
