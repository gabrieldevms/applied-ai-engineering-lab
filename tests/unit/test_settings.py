import pytest
from pydantic import ValidationError
from ai_api.config import Settings


SETTINGS_ENV_VARS = [
    "APP_ENV",
    "LLM_PROVIDER",
    "REQUIREMENT_ANALYSIS_RETRY_ATTEMPTS",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OLLAMA_TIMEOUT_SECONDS",
    "EMBEDDING_PROVIDER",
    "EMBEDDING_DIMENSIONS",
    "STORAGE_BACKEND",
    "STORAGE_BASE_DIR",
]


@pytest.fixture(autouse=True)
def clear_settings_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_var in SETTINGS_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)


def test_settings_should_use_fake_provider_by_default() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_env == "local"
    assert settings.llm_provider == "fake"
    assert settings.requirement_analysis_retry_attempts == 2
    assert settings.embedding_provider == "fake"
    assert settings.embedding_dimensions == 32
    assert settings.storage_backend == "local_jsonl"
    assert settings.storage_base_dir == ".data"


def test_settings_should_accept_openai_provider() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="openai",
        openai_api_key="fake-key",
        openai_model="fake-model",
    )

    assert settings.llm_provider == "openai"
    assert settings.openai_api_key == "fake-key"
    assert settings.openai_model == "fake-model"


def test_settings_should_accept_ollama_provider() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="ollama",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.1",
        ollama_timeout_seconds=120,
    )

    assert settings.llm_provider == "ollama"
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_model == "llama3.1"
    assert settings.ollama_timeout_seconds == 120


def test_settings_should_reject_invalid_provider() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_provider="invalid-provider")


def test_settings_should_reject_invalid_retry_attempts() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, requirement_analysis_retry_attempts=0)


def test_settings_should_accept_embedding_settings() -> None:
    settings = Settings(
        _env_file=None,
        embedding_provider="fake",
        embedding_dimensions=64,
    )

    assert settings.embedding_provider == "fake"
    assert settings.embedding_dimensions == 64


def test_settings_should_reject_invalid_embedding_dimensions() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, embedding_dimensions=0)
