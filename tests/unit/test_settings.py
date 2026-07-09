import pytest
from pydantic import ValidationError
from ai_api.config import Settings


def test_settings_should_use_fake_provider_by_default() -> None:
    settings = Settings()

    assert settings.app_env == "local"
    assert settings.llm_provider == "fake"
    assert settings.requirement_analysis_retry_attempts == 2


def test_settings_should_accept_openai_provider() -> None:
    settings = Settings(
        llm_provider="openai",
        openai_api_key="fake-key",
        openai_model="fake-model",
    )

    assert settings.llm_provider == "openai"
    assert settings.openai_api_key == "fake-key"
    assert settings.openai_model == "fake-model"


def test_settings_should_reject_invalid_provider() -> None:
    with pytest.raises(ValidationError):
        Settings(llm_provider="invalid-provider")


def test_settings_should_reject_invalid_retry_attempts() -> None:
    with pytest.raises(ValidationError):
        Settings(requirement_analysis_retry_attempts=0)
