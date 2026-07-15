DEFAULT_AGENT_PLAN_RESPONSE_JSON = """
{
  "summary": "Plano estruturado para executar o objetivo informado com controle e rastreabilidade.",
  "steps": [
    {
      "step_id": "plan-step-1",
      "objective": "Entender o objetivo solicitado pelo usuário.",
      "tool_name": null,
      "arguments": {},
      "rationale": "Antes de executar ferramentas, o agente deve compreender o objetivo."
    },
    {
      "step_id": "plan-step-2",
      "objective": "Analisar o requisito informado com foco em qualidade.",
      "tool_name": "requirements.analyze",
      "arguments": {
        "requirement_text": "Como cliente, quero renegociar minha dívida para gerar um boleto atualizado.",
        "language": "pt-BR"
      },
      "rationale": "A análise de requisitos é útil para identificar regras, riscos e cenários de teste."
    },
    {
      "step_id": "plan-step-3",
      "objective": "Consolidar o resultado em uma resposta rastreável.",
      "tool_name": null,
      "arguments": {},
      "rationale": "O agente deve apresentar um resultado final claro e auditável."
    }
  ]
}
""".strip()
