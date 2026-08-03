import json
from ai_api.config import Settings
from ai_api.llm.status import get_llm_health_status


def test_openai_health_status_does_not_expose_api_key_value_or_env_var_name() -> None:
    settings = Settings(
        llm_provider="openai",
        openai_api_key="sk-test-secret-value",
        openai_model="gpt-test-model",
    )

    response = get_llm_health_status(settings)
    payload = response.model_dump(mode="json")
    serialized_payload = json.dumps(payload)

    assert response.status == "configured"
    assert response.configured is True
    assert "sk-test-secret-value" not in serialized_payload
    assert "OPENAI_API_KEY" not in serialized_payload
    assert "api_key" not in serialized_payload.lower()
    assert response.safe_metadata["secrets_exposed"] == "false"
    assert any(
        field.name == "credentials"
        and field.configured is True
        and field.sensitive is True
        for field in response.safe_settings
    )


def test_openai_missing_configuration_uses_safe_logical_names() -> None:
    settings = Settings(
        llm_provider="openai",
        openai_api_key="",
        openai_model="",
    )

    response = get_llm_health_status(settings)
    payload = response.model_dump(mode="json")
    serialized_payload = json.dumps(payload)

    assert response.status == "missing_configuration"
    assert response.configured is False
    assert response.missing_settings == ["credentials", "model"]
    assert "OPENAI_API_KEY" not in serialized_payload
    assert "api_key" not in serialized_payload.lower()


def test_ollama_health_status_does_not_expose_raw_base_url() -> None:
    settings = Settings(
        llm_provider="ollama",
        ollama_base_url="http://internal-ollama-host:11434",
        ollama_model="llama3.1",
    )

    response = get_llm_health_status(settings)
    payload = response.model_dump(mode="json")
    serialized_payload = json.dumps(payload)

    assert response.status == "configured"
    assert response.configured is True
    assert "http://internal-ollama-host:11434" not in serialized_payload
    assert response.safe_metadata["base_url_configured"] == "true"
    assert response.safe_metadata["secrets_exposed"] == "false"


def test_fake_provider_status_is_safe_by_default() -> None:
    settings = Settings(llm_provider="fake")

    response = get_llm_health_status(settings)

    assert response.status == "configured"
    assert response.configured is True
    assert response.safe_metadata["external_network_access"] == "false"
    assert response.safe_metadata["secrets_required"] == "false"
    assert response.safe_metadata["secrets_exposed"] == "false"
