DEFAULT_REQUIREMENT_ANALYSIS_RESPONSE_JSON = """
{
  "summary": "O cliente deseja renegociar uma dívida e gerar um novo boleto.",
  "business_rules": [
    "O cliente deve possuir uma dívida elegível para renegociação.",
    "O sistema deve gerar um novo boleto após a conclusão da renegociação."
  ],
  "acceptance_criteria": [
    "A renegociação deve ser concluída com sucesso.",
    "O boleto gerado deve conter valor, vencimento e identificação válidos."
  ],
  "risks": [
    {
      "title": "Falha no registro do boleto",
      "description": "O boleto pode ser gerado pela aplicação, mas falhar no registro bancário.",
      "severity": "high"
    }
  ],
  "open_questions": [
    "Qual é o prazo máximo permitido para vencimento do novo boleto?",
    "Quais dívidas são elegíveis para renegociação?"
  ],
  "positive_test_scenarios": [
    "Cliente com dívida elegível realiza a renegociação e gera boleto com sucesso."
  ],
  "negative_test_scenarios": [
    "Cliente com dívida inelegível tenta realizar renegociação."
  ],
  "edge_cases": [
    "Cliente tenta renegociar no dia de vencimento original da dívida."
  ],
  "automation_opportunities": [
    "Automatizar a validação da API de geração de boleto.",
    "Automatizar cenários de elegibilidade e inelegibilidade da dívida."
  ]
}
""".strip()
