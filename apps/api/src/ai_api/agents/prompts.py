from collections.abc import Sequence
from ai_api.agents.schemas import ToolDefinition
from ai_api.llm import LLMMessage


AGENT_PLANNER_SYSTEM_PROMPT = """
Você é um planejador de agentes de IA.

Sua função é criar um plano estruturado, seguro e rastreável para um agente executar um objetivo.

Regras:
- Não execute ferramentas.
- Apenas planeje.
- Use somente ferramentas listadas como disponíveis.
- Se nenhuma ferramenta for necessária, use tool_name como null.
- Não invente nomes de ferramentas.
- Respeite o limite máximo de passos.
- Responda somente com JSON válido.
- Não inclua markdown.
""".strip()


def build_agent_planning_messages(
    objective: str,
    context: str | None = None,
    available_tools: Sequence[ToolDefinition] | None = None,
    max_steps: int = 5,
    language: str = "pt-BR",
) -> list[LLMMessage]:
    cleaned_objective = objective.strip()

    if not cleaned_objective:
        raise ValueError("objective cannot be blank")

    tools = list(available_tools or [])

    formatted_tools = "\n".join(
        _format_tool(tool)
        for tool in tools
    )

    if not formatted_tools:
        formatted_tools = "Nenhuma ferramenta disponível."

    formatted_context = context.strip() if context else "Nenhum contexto adicional fornecido."

    user_prompt = f"""
Idioma esperado: {language}

Objetivo:
{cleaned_objective}

Contexto:
{formatted_context}

Ferramentas disponíveis:
{formatted_tools}

Limite máximo de passos:
{max_steps}

Retorne um JSON exatamente neste formato:

{{
  "summary": "Resumo breve do plano.",
  "steps": [
    {{
      "step_id": "plan-step-1",
      "objective": "Objetivo do passo.",
      "tool_name": null,
      "arguments": {{}},
      "rationale": "Justificativa do passo."
    }}
  ]
}}
""".strip()

    return [
        LLMMessage(role="system", content=AGENT_PLANNER_SYSTEM_PROMPT),
        LLMMessage(role="user", content=user_prompt),
    ]


def _format_tool(tool: ToolDefinition) -> str:
    return (
        f"- name: {tool.name}\n"
        f"  description: {tool.description}\n"
        f"  metadata: {tool.metadata}"
    )
