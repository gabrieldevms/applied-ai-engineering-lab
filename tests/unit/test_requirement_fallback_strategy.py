import pytest

from ai_api.llm import FakeLLMProvider
from ai_api.requirements import (
    RequirementAnalysisError,
    RequirementAnalyzerService,
    RetryConfig,
)


VALID_REQUIREMENT_ANALYSIS_JSON = """
{
  "summary": "O cliente deseja renegociar uma dívida e gerar um novo boleto.",
  "business_rules": [
    "O cliente deve possuir uma dívida elegível para renegociação."
  ],
  "acceptance_criteria": [
    "A renegociação deve ser concluída com sucesso."
  ],
  "risks": [
    {
      "title": "Falha no registro do boleto",
      "description": "O boleto pode falhar durante o registro bancário.",
      "severity": "high"
    }
  ],
  "open_questions": [
    "Qual é o prazo máximo para vencimento do novo boleto?"
  ],
  "positive_test_scenarios": [
    "Cliente com dívida elegível renegocia com sucesso."
  ],
  "negative_test_scenarios": [
    "Cliente com dívida inelegível tenta renegociar."
  ],
  "edge_cases": [
    "Cliente tenta renegociar no dia do vencimento original."
  ],
  "automation_opportunities": [
    "Automatizar validação da API de geração de boleto."
  ]
}
""".strip()


def test_requirement_analyzer_service_should_not_use_fallback_when_primary_succeeds() -> None:
    primary_provider = FakeLLMProvider(
        response_content=VALID_REQUIREMENT_ANALYSIS_JSON
    )
    fallback_provider = FakeLLMProvider(
        response_content=VALID_REQUIREMENT_ANALYSIS_JSON
    )

    service = RequirementAnalyzerService(
        llm_provider=primary_provider,
        fallback_provider=fallback_provider,
        retry_config=RetryConfig(max_attempts=2),
    )

    response = service.analyze(
        requirement_text="Como cliente, quero renegociar minha dívida."
    )

    assert response.summary.startswith("O cliente deseja renegociar")
    assert primary_provider.calls == 1
    assert fallback_provider.calls == 0


def test_requirement_analyzer_service_should_use_fallback_when_primary_fails() -> None:
    primary_provider = FakeLLMProvider(response_content="not a json")
    fallback_provider = FakeLLMProvider(
        response_content=VALID_REQUIREMENT_ANALYSIS_JSON
    )

    service = RequirementAnalyzerService(
        llm_provider=primary_provider,
        fallback_provider=fallback_provider,
        retry_config=RetryConfig(max_attempts=2),
    )

    response = service.analyze(
        requirement_text="Como cliente, quero renegociar minha dívida."
    )

    assert response.summary.startswith("O cliente deseja renegociar")
    assert primary_provider.calls == 2
    assert fallback_provider.calls == 1


def test_requirement_analyzer_service_should_raise_error_when_primary_and_fallback_fail() -> None:
    primary_provider = FakeLLMProvider(response_content="not a json")
    fallback_provider = FakeLLMProvider(response_content="still not a json")

    service = RequirementAnalyzerService(
        llm_provider=primary_provider,
        fallback_provider=fallback_provider,
        retry_config=RetryConfig(max_attempts=2),
    )

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response is not a valid JSON object.",
    ):
        service.analyze(
            requirement_text="Como cliente, quero consultar meus boletos."
        )

    assert primary_provider.calls == 2
    assert fallback_provider.calls == 2
