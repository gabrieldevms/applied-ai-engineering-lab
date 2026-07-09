import pytest
from ai_api.requirements import (
    RequirementAnalysisError,
    parse_requirement_analysis_response,
)


VALID_LLM_RESPONSE = """
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


def test_parse_requirement_analysis_response_should_accept_valid_llm_response() -> None:
    response = parse_requirement_analysis_response(VALID_LLM_RESPONSE)

    assert response.summary.startswith("O cliente deseja renegociar")
    assert len(response.business_rules) == 1
    assert len(response.risks) == 1
    assert response.risks[0].severity == "high"


def test_parse_requirement_analysis_response_should_reject_invalid_json() -> None:
    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response is not a valid JSON object.",
    ):
        parse_requirement_analysis_response("not a json")


def test_parse_requirement_analysis_response_should_reject_empty_summary() -> None:
    invalid_response = """
    {
      "summary": "",
      "business_rules": [],
      "acceptance_criteria": [],
      "risks": [],
      "open_questions": [],
      "positive_test_scenarios": [],
      "negative_test_scenarios": [],
      "edge_cases": [],
      "automation_opportunities": []
    }
    """

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response does not match the requirement analysis schema.",
    ):
        parse_requirement_analysis_response(invalid_response)


def test_parse_requirement_analysis_response_should_reject_invalid_risk_severity() -> None:
    invalid_response = """
    {
      "summary": "Resumo válido.",
      "business_rules": [],
      "acceptance_criteria": [],
      "risks": [
        {
          "title": "Risco inválido",
          "description": "A severidade não é aceita.",
          "severity": "critical"
        }
      ],
      "open_questions": [],
      "positive_test_scenarios": [],
      "negative_test_scenarios": [],
      "edge_cases": [],
      "automation_opportunities": []
    }
    """

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response does not match the requirement analysis schema.",
    ):
        parse_requirement_analysis_response(invalid_response)


def test_parse_requirement_analysis_response_should_reject_unexpected_fields() -> None:
    invalid_response = """
    {
      "summary": "Resumo válido.",
      "business_rules": [],
      "acceptance_criteria": [],
      "risks": [],
      "open_questions": [],
      "positive_test_scenarios": [],
      "negative_test_scenarios": [],
      "edge_cases": [],
      "automation_opportunities": [],
      "unexpected_field": "This field should not be accepted."
    }
    """

    with pytest.raises(
        RequirementAnalysisError,
        match="LLM response does not match the requirement analysis schema.",
    ):
        parse_requirement_analysis_response(invalid_response)
