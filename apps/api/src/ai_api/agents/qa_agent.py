from ai_api.agents.runtime import AgentRuntime
from ai_api.agents.schemas import (
    AgentRunResponse,
    AgentToolCall,
    QAAgentRunResponse,
)
from ai_api.rag.schemas import SemanticSearchDocument


class QAAgentService:
    def __init__(
        self,
        agent_runtime: AgentRuntime | None = None,
    ) -> None:
        self.agent_runtime = agent_runtime or AgentRuntime()

    def run(
        self,
        requirement_text: str,
        knowledge_documents: list[SemanticSearchDocument] | None = None,
        language: str = "pt-BR",
        top_k: int = 3,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
        max_steps: int = 5,
        metadata: dict | None = None,
    ) -> QAAgentRunResponse:
        cleaned_requirement = requirement_text.strip()
        documents = knowledge_documents or []

        if not cleaned_requirement:
            raise ValueError("requirement_text cannot be blank")

        tool_calls = self._build_tool_calls(
            requirement_text=cleaned_requirement,
            knowledge_documents=documents,
            language=language,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        agent_run = self.agent_runtime.run(
            objective="Analisar requisito de software com foco em qualidade, riscos e cenários de teste.",
            context=self._build_context(documents),
            max_steps=max_steps,
            metadata={
                **(metadata or {}),
                "agent_type": "qa-agent-v1",
                "language": language,
                "knowledge_documents": len(documents),
                "requested_tools": [
                    tool_call.tool_name
                    for tool_call in tool_calls
                ],
            },
            tool_calls=tool_calls,
        )

        return QAAgentRunResponse(
            run_id=agent_run.run_id,
            status=agent_run.status,
            final_answer=agent_run.final_answer,
            requirement_analysis=self._extract_tool_output(
                agent_run=agent_run,
                tool_name="requirements.analyze",
            ),
            retrieved_context=self._extract_optional_tool_output(
                agent_run=agent_run,
                tool_name="rag.retrieve",
            ),
            steps=agent_run.steps,
            metadata={
                **agent_run.metadata,
                "qa_agent": "qa-agent-v1",
            },
        )

    def _build_tool_calls(
        self,
        requirement_text: str,
        knowledge_documents: list[SemanticSearchDocument],
        language: str,
        top_k: int,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[AgentToolCall]:
        tool_calls: list[AgentToolCall] = []

        if knowledge_documents:
            tool_calls.append(
                AgentToolCall(
                    tool_name="rag.retrieve",
                    arguments={
                        "query": requirement_text,
                        "documents": [
                            document.model_dump(mode="json")
                            for document in knowledge_documents
                        ],
                        "top_k": top_k,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                    },
                    metadata={
                        "reason": "retrieve supporting knowledge for QA analysis",
                    },
                )
            )

        tool_calls.append(
            AgentToolCall(
                tool_name="requirements.analyze",
                arguments={
                    "requirement_text": requirement_text,
                    "language": language,
                },
                metadata={
                    "reason": "analyze requirement from a QA perspective",
                },
            )
        )

        return tool_calls

    def _build_context(
        self,
        knowledge_documents: list[SemanticSearchDocument],
    ) -> str | None:
        if not knowledge_documents:
            return None

        return (
            "Documentos de apoio foram fornecidos para recuperação de contexto "
            "antes da análise de qualidade."
        )

    def _extract_tool_output(
        self,
        agent_run: AgentRunResponse,
        tool_name: str,
    ) -> dict:
        output = self._extract_optional_tool_output(
            agent_run=agent_run,
            tool_name=tool_name,
        )

        return output or {}

    def _extract_optional_tool_output(
        self,
        agent_run: AgentRunResponse,
        tool_name: str,
    ) -> dict | None:
        step_name = f"tool_call:{tool_name}"

        for step in agent_run.steps:
            if step.name == step_name and step.status == "completed":
                tool_output = step.output.get("output")

                if isinstance(tool_output, dict):
                    return tool_output

        return None
