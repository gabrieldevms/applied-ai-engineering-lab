from ai_api.llm import FakeLLMProvider, LLMMessage, LLMProvider


def generate_with_provider(provider: LLMProvider) -> str:
    response = provider.generate(
        messages=[
            LLMMessage(
                role="user",
                content="Analyze this requirement.",
            )
        ]
    )

    return response.content


def test_fake_llm_provider_should_generate_response() -> None:
    provider = FakeLLMProvider()

    response = provider.generate(
        messages=[
            LLMMessage(
                role="system",
                content="You are a helpful AI assistant.",
            ),
            LLMMessage(
                role="user",
                content="Analyze this requirement.",
            ),
        ]
    )

    assert response.provider == "fake"
    assert response.model == "fake-llm-v1"
    assert response.content == "Fake LLM response for: Analyze this requirement."
    assert response.usage is not None
    assert response.usage.total_tokens > 0


def test_fake_llm_provider_should_follow_llm_provider_contract() -> None:
    provider = FakeLLMProvider()

    content = generate_with_provider(provider)

    assert content == "Fake LLM response for: Analyze this requirement."
