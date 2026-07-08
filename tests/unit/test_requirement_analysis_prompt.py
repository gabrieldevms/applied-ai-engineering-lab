import pytest

from ai_api.requirements import build_requirement_analysis_messages


def test_build_requirement_analysis_messages_should_create_system_and_user_messages() -> None:
    messages = build_requirement_analysis_messages(
        requirement_text="As a customer, I want to renegotiate my debt and generate a new payment slip.",
        language="en",
    )

    assert len(messages) == 2

    system_message = messages[0]
    user_message = messages[1]

    assert system_message.role == "system"
    assert "senior QA Engineer" in system_message.content
    assert "valid JSON object" in system_message.content

    assert user_message.role == "user"
    assert "Response language: en" in user_message.content
    assert "renegotiate my debt" in user_message.content


def test_build_requirement_analysis_messages_should_support_portuguese_response_language() -> None:
    messages = build_requirement_analysis_messages(
        requirement_text="Como cliente, quero renegociar minha dívida para gerar um novo boleto.",
        language="pt-BR",
    )

    user_message = messages[1]

    assert "Response language: pt-BR" in user_message.content
    assert "renegociar minha dívida" in user_message.content


def test_build_requirement_analysis_messages_should_reject_empty_requirement() -> None:
    with pytest.raises(ValueError, match="requirement_text cannot be empty"):
        build_requirement_analysis_messages(requirement_text="   ")
