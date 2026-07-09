import pytest
from ai_api.requirements import build_requirement_analysis_messages


def test_build_requirement_analysis_messages_should_create_system_and_user_messages() -> None:
    messages = build_requirement_analysis_messages(
        requirement_text="Como cliente, quero renegociar minha dívida para gerar um novo boleto.",
        language="pt-BR",
    )

    assert len(messages) == 2

    system_message = messages[0]
    user_message = messages[1]

    assert system_message.role == "system"
    assert "QA Engineer Sênior" in system_message.content
    assert "JSON válido" in system_message.content
    assert "português do Brasil" in system_message.content

    assert user_message.role == "user"
    assert "Idioma da resposta: pt-BR" in user_message.content
    assert "renegociar minha dívida" in user_message.content


def test_build_requirement_analysis_messages_should_use_portuguese_by_default() -> None:
    messages = build_requirement_analysis_messages(
        requirement_text="Como usuário, quero consultar meus boletos em aberto.",
    )

    user_message = messages[1]

    assert "Idioma da resposta: pt-BR" in user_message.content
    assert "consultar meus boletos em aberto" in user_message.content


def test_build_requirement_analysis_messages_should_reject_empty_requirement() -> None:
    with pytest.raises(ValueError, match="requirement_text cannot be empty"):
        build_requirement_analysis_messages(requirement_text="   ")
