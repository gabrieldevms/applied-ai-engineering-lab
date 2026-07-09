from types import SimpleNamespace

import pytest

from ai_api.llm import LLMMessage, LLMProviderError, OpenAIProvider


class FakeResponsesResource:
    def __init__(
        self,
        output_text: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.output_text = output_text
        self.error = error
        self.create_kwargs = None

    def create(self, **kwargs):
        self.create_kwargs = kwargs

        if self.error is not None:
            raise self.error

        return SimpleNamespace(
            output_text=self.output_text,
            usage=SimpleNamespace(
                input_tokens=10,
                output_tokens=20,
                total_tokens=30,
            ),
        )


class FakeOpenAIClient:
    def __init__(self, responses: FakeResponsesResource) -> None:
        self.responses = responses


def test_openai_provider_should_generate_llm_response() -> None:
    responses = FakeResponsesResource(output_text='{"summary": "ok"}')
    client = FakeOpenAIClient(responses=responses)

    provider = OpenAIProvider(
        api_key="fake-api-key",
        model="fake-model",
        client=client,
    )

    response = provider.generate(
        [
            LLMMessage(role="system", content="Você é um assistente de QA."),
            LLMMessage(role="user", content="Analise este requisito."),
        ]
    )

    assert response.content == '{"summary": "ok"}'
    assert response.provider == "openai"
    assert response.model == "fake-model"
    assert response.usage is not None
    assert response.usage.total_tokens == 30

    assert responses.create_kwargs is not None
    assert responses.create_kwargs["model"] == "fake-model"
    assert "SYSTEM:" in responses.create_kwargs["input"]
    assert "USER:" in responses.create_kwargs["input"]


def test_openai_provider_should_raise_error_when_response_has_no_output_text() -> None:
    responses = FakeResponsesResource(output_text=None)
    client = FakeOpenAIClient(responses=responses)

    provider = OpenAIProvider(
        api_key="fake-api-key",
        model="fake-model",
        client=client,
    )

    with pytest.raises(
        LLMProviderError,
        match="OpenAI response did not contain output text.",
    ):
        provider.generate(
            [
                LLMMessage(role="user", content="Analise este requisito."),
            ]
        )


def test_openai_provider_should_raise_error_when_request_fails() -> None:
    responses = FakeResponsesResource(error=RuntimeError("network error"))
    client = FakeOpenAIClient(responses=responses)

    provider = OpenAIProvider(
        api_key="fake-api-key",
        model="fake-model",
        client=client,
    )

    with pytest.raises(
        LLMProviderError,
        match="OpenAI provider request failed.",
    ):
        provider.generate(
            [
                LLMMessage(role="user", content="Analise este requisito."),
            ]
        )


def test_openai_provider_should_reject_empty_api_key() -> None:
    with pytest.raises(ValueError, match="api_key cannot be empty"):
        OpenAIProvider(api_key=" ", model="fake-model")


def test_openai_provider_should_reject_empty_model() -> None:
    with pytest.raises(ValueError, match="model cannot be empty"):
        OpenAIProvider(api_key="fake-api-key", model=" ")
