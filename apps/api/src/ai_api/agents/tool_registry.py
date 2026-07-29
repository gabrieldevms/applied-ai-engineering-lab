from collections.abc import Sequence
from ai_api.agents.schemas import ToolDefinition, ToolRegistryResponse


DEFAULT_TOOL_DEFINITIONS = [
    ToolDefinition(
        name="rag.retrieve",
        description="Retrieve relevant document chunks for a query.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Pergunta ou busca em linguagem natural.",
                },
                "documents": {
                    "type": "array",
                    "description": "Documentos usados como base de recuperação.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Quantidade máxima de chunks recuperados.",
                },
            },
            "required": ["query", "documents"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "retrieved_chunks": {
                    "type": "array",
                    "description": "Chunks mais relevantes encontrados.",
                }
            },
        },
        metadata={
            "category": "rag",
            "safe_by_default": True,
            "requires_llm": False,
        },
    ),
    ToolDefinition(
        name="rag.answer",
        description="Generate an answer using retrieved RAG context.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Pergunta a ser respondida.",
                },
                "documents": {
                    "type": "array",
                    "description": "Documentos usados como fonte de contexto.",
                },
                "language": {
                    "type": "string",
                    "description": "Idioma esperado para a resposta.",
                },
            },
            "required": ["query", "documents"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Resposta gerada com base no contexto.",
                },
                "citations": {
                    "type": "array",
                    "description": "Fontes utilizadas na resposta.",
                },
            },
        },
        metadata={
            "category": "rag",
            "safe_by_default": True,
            "requires_llm": True,
        },
    ),
    ToolDefinition(
        name="requirements.analyze",
        description="Analyze a software requirement and identify rules, risks and test scenarios.",
        input_schema={
            "type": "object",
            "properties": {
                "requirement_text": {
                    "type": "string",
                    "description": "Texto do requisito a ser analisado.",
                },
                "language": {
                    "type": "string",
                    "description": "Idioma esperado para a análise.",
                },
            },
            "required": ["requirement_text"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Resumo do requisito.",
                },
                "business_rules": {
                    "type": "array",
                    "description": "Regras de negócio identificadas.",
                },
                "risks": {
                    "type": "array",
                    "description": "Riscos identificados.",
                },
                "acceptance_criteria": {
                    "type": "array",
                    "description": "Critérios de aceite sugeridos.",
                },
            },
        },
        metadata={
            "category": "qa",
            "safe_by_default": True,
            "requires_llm": True,
        },
    ),
    ToolDefinition(
        name="data_analysis.agent.run",
        description=(
            "Run the Data Analyst Agent for natural-language SQL analysis, "
            "read-only validation, controlled execution and evidence generation."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "objective": {
                    "type": "string",
                    "description": "Objetivo ou pergunta de análise de dados.",
                },
                "database_schema": {
                    "type": "object",
                    "description": "Schema do banco com tabelas e colunas disponíveis.",
                },
                "table_data": {
                    "type": "array",
                    "description": "Dados controlados usados para execução em memória.",
                },
                "language": {
                    "type": "string",
                    "description": "Idioma esperado para a resposta.",
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Quantidade máxima de linhas retornadas.",
                },
                "metadata": {
                    "type": "object",
                    "description": "Metadados opcionais da execução.",
                },
            },
            "required": ["objective", "database_schema"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Status final do Data Analyst Agent.",
                },
                "answer": {
                    "type": "string",
                    "description": "Resposta final em linguagem natural.",
                },
                "workflow": {
                    "type": "object",
                    "description": "Workflow SQL completo com geração, execução e validação.",
                },
                "evidence": {
                    "type": "object",
                    "description": "Evidência da consulta executada, quando disponível.",
                },
                "trace": {
                    "type": "array",
                    "description": "Trace de execução do agente.",
                },
            },
        },
        metadata={
            "category": "data_analysis",
            "safe_by_default": True,
            "requires_llm": True,
            "specialized_agent": "data-analyst-agent-v1",
            "execution_mode": "controlled_in_memory_sqlite",
        },
    ),
]


class ToolRegistry:
    def __init__(
        self,
        tools: Sequence[ToolDefinition] | None = None,
    ) -> None:
        self._tools: dict[str, ToolDefinition] = {}

        selected_tools = (
            DEFAULT_TOOL_DEFINITIONS
            if tools is None
            else tools
        )

        for tool in selected_tools:
            self.register(tool)

    def register(self, tool: ToolDefinition) -> None:
        tool_name = tool.name.strip()

        if tool_name in self._tools:
            raise ValueError(f"Tool already registered: {tool_name}")

        self._tools[tool_name] = tool

    def get(self, tool_name: str) -> ToolDefinition | None:
        cleaned_tool_name = tool_name.strip()

        if not cleaned_tool_name:
            raise ValueError("tool_name cannot be blank")

        return self._tools.get(cleaned_tool_name)

    def list_tools(self) -> list[ToolDefinition]:
        return [
            self._tools[tool_name]
            for tool_name in sorted(self._tools)
        ]

    def describe(self) -> ToolRegistryResponse:
        tools = self.list_tools()

        return ToolRegistryResponse(
            total_tools=len(tools),
            tools=tools,
            metadata={
                "registry": "agent-tool-registry-v1",
                "default_tools_loaded": True,
            },
        )

    def count(self) -> int:
        return len(self._tools)
