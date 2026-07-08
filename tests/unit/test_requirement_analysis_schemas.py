import pytest
from pydantic import ValidationError

from ai_api.requirements import (
    RequirementAnalysisRequest,
    RequirementAnalysisResponse,
    RequirementRisk,
)


def test_requirement_analysis_request_should_strip_requirement_text() -> None:
    request = RequirementAnalysisRequest(
        requirement_text="  Como cliente, quero renegociar minha dívida para gerar um novo boleto.  ",
    )

    assert request.requirement_text == (
        "Como cliente, quero renegociar minha dívida para gerar um novo boleto."
    )
    assert request.language == "pt-BR"


def test_requirement_analysis_request_should_accept_custom_language() -> None:
    request = RequirementAnalysisRequest(
        requirement_text="Como cliente, quero consultar meus boletos em aberto.",
        language="en",
    )

    assert request.requirement_text == (
        "Como cliente, quero consultar meus boletos em aberto."
    )
    assert request.language == "en"


def test_requirement_analysis_request_should_reject_blank_requirement_text() -> None:
    with pytest.raises(ValidationError):
        RequirementAnalysisRequest(requirement_text="   ")


def test_requirement_risk_should_accept_valid_severity() -> None:
    risk = RequirementRisk(
        title="Falha no registro do boleto",
        description="O boleto gerado pode falhar durante o registro bancário.",
        severity="high",
    )

    assert risk.severity == "high"


def test_requirement_risk_should_reject_invalid_severity() -> None:
    with pytest.raises(ValidationError):
        RequirementRisk(
            title="Risco inválido",
            description="Uma severidade inválida não deve ser aceita.",
            severity="critical",
        )


def test_requirement_analysis_response_should_represent_structured_analysis() -> None:
    response = RequirementAnalysisResponse(
        summary="O cliente pode renegociar uma dívida e gerar um novo boleto.",
        business_rules=[
            "O cliente deve possuir uma dívida elegível para renegociação.",
            "Um novo boleto deve ser gerado após a renegociação.",
        ],
        acceptance_criteria=[
            "O cliente consegue concluir a renegociação com sucesso.",
            "O sistema retorna um boleto válido após a renegociação.",
        ],
        risks=[
            RequirementRisk(
                title="Valor incorreto no boleto",
                description="O boleto gerado pode apresentar um valor diferente do valor renegociado.",
                severity="high",
            )
        ],
        open_questions=[
            "Qual é a data máxima permitida para vencimento do novo boleto?",
        ],
        positive_test_scenarios=[
            "Cliente com dívida elegível realiza a renegociação com sucesso.",
        ],
        negative_test_scenarios=[
            "Cliente com dívida inelegível tenta realizar a renegociação.",
        ],
        edge_cases=[
            "Cliente tenta renegociar a dívida na data de vencimento original.",
        ],
        automation_opportunities=[
            "Automatizar a validação da API de geração de boleto.",
        ],
    )

    assert response.summary.startswith("O cliente pode renegociar")
    assert len(response.business_rules) == 2
    assert len(response.risks) == 1
    assert response.risks[0].severity == "high"
    assert (
        response.open_questions[0]
        == "Qual é a data máxima permitida para vencimento do novo boleto?"
    )
