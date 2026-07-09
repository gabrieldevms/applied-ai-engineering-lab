import pytest
from ai_api.llm import LLMMessage, LLMProviderError, OllamaProvider


class FakeHTTPResponse:
    def __init__(
        self,
        data: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        self.data = data or {}
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error

    def json(self) -> dict:
        return self.data


class FakeHTTPClient:
    def __init__(self, response: FakeHTTPResponse) -> None:
        self.response = response
        self.post_path = None
        self.post_json = None

    def post(self, path: str, json: dict) -> FakeHTTPResponse:
        self.post_path = path
        self.post_json = json

        return self.response


def test_ollama_provider_should_generate_llm_response() -> None:
    client = FakeHTTPClient(
        response=FakeHTTPResponse(
            data={
                "message": {
                    "role": "assistant",
                    "content": '{"summary": "ok"}',
                },
                "prompt_eval_count": 10,
                "eval_count": 20,
            }
        )
    )

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="llama3.1",
        client=client,
    )

    response = provider.generate(
        [
            LLMMessage(role="system", content="Você é um assistente de QA."),
            LLMMessage(role="user", content="Analise este requisito."),
        ]
    )

    assert response.content == '{"summary": "ok"}'
    assert response.provider == "ollama"
    assert response.model == "llama3.1"
    assert response.usage is not None
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 20
    assert response.usage.total_tokens == 30
    assert client.post_path == "/api/chat"
    assert client.post_json is not None
    assert client.post_json["model"] == "llama3.1"
    assert client.post_json["stream"] is False
    assert client.post_json["format"] == "json"
    assert client.post_json["options"]["temperature"] == 0
    assert client.post_json["messages"][0]["role"] == "system"
    assert client.post_json["messages"][1]["role"] == "user"


def test_ollama_provider_should_raise_error_when_request_fails() -> None:
    client = FakeHTTPClient(
        response=FakeHTTPResponse(
            error=RuntimeError("connection error"),
        )
    )

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="llama3.1",
        client=client,
    )

    with pytest.raises(
        LLMProviderError,
        match="Ollama provider request failed.",
    ):
        provider.generate(
            [
                LLMMessage(role="user", content="Analise este requisito."),
            ]
        )


def test_ollama_provider_should_raise_error_when_response_has_no_message() -> None:
    client = FakeHTTPClient(
        response=FakeHTTPResponse(
            data={},
        )
    )

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="llama3.1",
        client=client,
    )

    with pytest.raises(
        LLMProviderError,
        match="Ollama response did not contain a message object.",
    ):
        provider.generate(
            [
                LLMMessage(role="user", content="Analise este requisito."),
            ]
        )


def test_ollama_provider_should_raise_error_when_response_has_no_content() -> None:
    client = FakeHTTPClient(
        response=FakeHTTPResponse(
            data={
                "message": {
                    "role": "assistant",
                    "content": "",
                }
            },
        )
    )

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="llama3.1",
        client=client,
    )

    with pytest.raises(
        LLMProviderError,
        match="Ollama response did not contain message content.",
    ):
        provider.generate(
            [
                LLMMessage(role="user", content="Analise este requisito."),
            ]
        )


def test_ollama_provider_should_reject_empty_base_url() -> None:
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        OllamaProvider(base_url=" ", model="llama3.1")


def test_ollama_provider_should_reject_empty_model() -> None:
    with pytest.raises(ValueError, match="model cannot be empty"):
        OllamaProvider(base_url="http://localhost:11434", model=" ")
