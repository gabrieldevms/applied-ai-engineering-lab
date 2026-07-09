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


def test_requirement_analyzer_service_should_not_retry_when_first_attempt_is_valid() -> None:
    provider = FakeLLMProvider(response_content=VALID_REQUIREMENT_ANALYSIS_JSON)
    service = RequirementAnalyzerService(
        llm_provider=provider,
        retry_config=RetryConfig(max_attempts=3),
    )

    response = service.analyze(
        requirement_text="Como cliente, quero renegociar minha dívida."
    )

    assert response.summary.startswith("O cliente deseja renegociar")
    assert provider.calls == 1


def test_requirement_analyzer_service_should_retry_until_valid_response() -> None:
    provider = FakeLLMProvider(
        response_contents=[
            "not a json",
            VALID_REQUIREMENT_ANALYSIS_JSON,
        ]
    )
    service = RequirementAnalyzerService(
        llm_provider=provider,
        retry_config=RetryConfig(max_attempts=2),
    )

    response = service.analyze(
        requirement_text="Como cliente, quero renegociar minha dívida."
    )

    assert response.summary.startswith("O cliente deseja renegociar")
    assert provider.calls == 2


def test_requirement_analyzer_service_should_raise_error_after_max_attempts() -> None:
    provider = FakeLLMProvider(
        response_contents=[
            "not a json",
            "still not a json",
        ]
    )
    service = RequirementAnalyzerService(
        llm_provider=provider,
        retry_config=RetryConfig(max_attempts=2),
    )

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response is not a valid JSON object.",
    ):
        service.analyze(
            requirement_text="Como cliente, quero consultar meus boletos."
        )

    assert provider.calls == 2


def test_retry_config_should_reject_invalid_max_attempts() -> None:
    with pytest.raises(
        ValueError,
        match="max_attempts must be greater than or equal to 1",
    ):
        RetryConfig(max_attempts=0)
