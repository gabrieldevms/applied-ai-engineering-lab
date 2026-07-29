from ai_api.agents import QADataValidationSelector


def test_selector_should_select_data_validation_for_financial_data_requirement() -> None:
    selector = QADataValidationSelector()

    result = selector.select(
        "Como QA, preciso validar o saldo final por conta considerando "
        "depósitos e retiradas."
    )

    assert result.decision == "selected"
    assert "saldo" in result.matched_signals
    assert "conta" in result.matched_signals
    assert "depósito" in result.matched_signals
    assert result.confidence > 0


def test_selector_should_skip_data_validation_when_requirement_has_no_data_signals() -> None:
    selector = QADataValidationSelector()

    result = selector.select(
        "Como usuário, quero alterar o tema visual da aplicação para modo escuro."
    )

    assert result.decision == "skipped"
    assert result.matched_signals == []
    assert result.confidence == 0


def test_selector_should_select_data_validation_for_sql_requirement() -> None:
    selector = QADataValidationSelector()

    result = selector.select(
        "Validar via SQL se a tabela de pagamentos possui registros corretos."
    )

    assert result.decision == "selected"
    assert "sql" in result.matched_signals
    assert "tabela" in result.matched_signals
    assert "pagamentos" in result.matched_signals
