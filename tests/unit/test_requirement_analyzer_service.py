import pytest

from ai_api.llm import FakeLLMProvider
from ai_api.requirements import (
    RequirementAnalysisError,
    RequirementAnalyzerService,
)


VALID_REQUIREMENT_ANALYSIS_JSON = """
{
  "summary": "O cliente deseja renegociar uma dívida e gerar um novo boleto.",
  "business_rules": [
    "O cliente deve possuir uma dívida elegível para renegociação.",
    "O sistema deve gerar um novo boleto após a renegociação."
  ],
  "acceptance_criteria": [
    "A renegociação deve ser concluída com sucesso.",
    "O boleto gerado deve conter valor e vencimento válidos."
  ],
  "risks": [
    {
      "title": "Falha no registro do boleto",
      "description": "O boleto pode ser gerado, mas falhar no registro bancário.",
      "severity": "high"
    }
  ],
  "open_questions": [
    "Qual é o prazo máximo permitido para vencimento do novo boleto?"
  ],
  "positive_test_scenarios": [
    "Cliente com dívida elegível renegocia e gera boleto com sucesso."
  ],
  "negative_test_scenarios": [
    "Cliente com dívida inelegível tenta realizar renegociação."
  ],
  "edge_cases": [
    "Cliente tenta renegociar no dia de vencimento original da dívida."
  ],
  "automation_opportunities": [
    "Automatizar validação da API de geração de boleto."
  ]
}
""".strip()


def test_requirement_analyzer_service_should_return_structured_analysis() -> None:
    provider = FakeLLMProvider(response_content=VALID_REQUIREMENT_ANALYSIS_JSON)
    service = RequirementAnalyzerService(llm_provider=provider)

    response = service.analyze(
        requirement_text="Como cliente, quero renegociar minha dívida para gerar um novo boleto."
    )

    assert response.summary.startswith("O cliente deseja renegociar")
    assert len(response.business_rules) == 2
    assert len(response.acceptance_criteria) == 2
    assert len(response.risks) == 1
    assert response.risks[0].severity == "high"
    assert response.open_questions[0].startswith("Qual é o prazo máximo")


def test_requirement_analyzer_service_should_raise_error_for_invalid_json() -> None:
    provider = FakeLLMProvider(response_content="not a json")
    service = RequirementAnalyzerService(llm_provider=provider)

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response is not a valid JSON object.",
    ):
        service.analyze(
            requirement_text="Como cliente, quero consultar meus boletos em aberto."
        )


def test_requirement_analyzer_service_should_raise_error_for_invalid_schema() -> None:
    provider = FakeLLMProvider(
        response_content='{"summary": "", "risks": [{"severity": "critical"}]}'
    )
    service = RequirementAnalyzerService(llm_provider=provider)

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response does not match the requirement analysis schema.",
    ):
        service.analyze(
            requirement_text="Como cliente, quero consultar meus boletos em aberto."
        )
