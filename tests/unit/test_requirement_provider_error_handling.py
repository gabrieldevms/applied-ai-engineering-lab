import pytest

from ai_api.llm import FakeLLMProvider, LLMProviderError
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


class FailingLLMProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, messages):
        self.calls += 1
        raise LLMProviderError("Provider failed.")


def test_requirement_analyzer_service_should_retry_provider_errors() -> None:
    primary_provider = FailingLLMProvider()

    service = RequirementAnalyzerService(
        llm_provider=primary_provider,
        retry_config=RetryConfig(max_attempts=2),
    )

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM provider failed.",
    ):
        service.analyze(
            requirement_text="Como cliente, quero renegociar minha dívida."
        )

    assert primary_provider.calls == 2


def test_requirement_analyzer_service_should_use_fallback_after_provider_error() -> None:
    primary_provider = FailingLLMProvider()
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
