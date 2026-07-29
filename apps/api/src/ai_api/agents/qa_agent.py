from ai_api.agents.qa_data_validation_selection import (
    QADataValidationSelectionResult,
    QADataValidationSelector,
)
from ai_api.agents.runtime import AgentRuntime
from ai_api.agents.schemas import (
    AgentRunResponse,
    AgentToolCall,
    QAAgentDataValidationRequest,
    QAAgentRunResponse,
)
from ai_api.rag.schemas import SemanticSearchDocument


class QAAgentService:
    def __init__(
        self,
        agent_runtime: AgentRuntime | None = None,
        data_validation_selector: QADataValidationSelector | None = None,
    ) -> None:
        self.agent_runtime = agent_runtime or AgentRuntime()
        self.data_validation_selector = (
            data_validation_selector
            or QADataValidationSelector()
        )

    def run(
        self,
        requirement_text: str,
        knowledge_documents: list[SemanticSearchDocument] | None = None,
        data_validation: QAAgentDataValidationRequest | None = None,
        language: str = "pt-BR",
        top_k: int = 3,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
        max_steps: int = 6,
        metadata: dict | None = None,
    ) -> QAAgentRunResponse:
        cleaned_requirement = requirement_text.strip()
        documents = knowledge_documents or []

        if not cleaned_requirement:
            raise ValueError("requirement_text cannot be blank")

        data_validation_selection = self._select_data_validation(
            requirement_text=cleaned_requirement,
            data_validation=data_validation,
        )

        selected_data_validation = (
            data_validation
            if (
                data_validation is not None
                and data_validation_selection is not None
                and data_validation_selection.decision == "selected"
            )
            else None
        )

        tool_calls = self._build_tool_calls(
            requirement_text=cleaned_requirement,
            knowledge_documents=documents,
            data_validation=selected_data_validation,
            language=language,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        agent_run = self.agent_runtime.run(
            objective=(
                "Analisar requisito de software com foco em qualidade, "
                "riscos, cenários de teste e evidências de dados quando "
                "aplicável."
            ),
            context=self._build_context(
                knowledge_documents=documents,
                data_validation=selected_data_validation,
                data_validation_selection=data_validation_selection,
            ),
            max_steps=max_steps,
            metadata={
                **(metadata or {}),
                "agent_type": "qa-agent-v1",
                "language": language,
                "knowledge_documents": len(documents),
                "data_validation_available": data_validation is not None,
                "data_validation_selected": (
                    selected_data_validation is not None
                ),
                "data_validation_mode": (
                    data_validation.mode
                    if data_validation is not None
                    else "not_provided"
                ),
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
            data_validation_selection=(
                data_validation_selection.model_dump(mode="json")
                if data_validation_selection is not None
                else None
            ),
            data_validation=self._extract_optional_tool_output(
                agent_run=agent_run,
                tool_name="data_analysis.agent.run",
            ),
            steps=agent_run.steps,
            metadata={
                **agent_run.metadata,
                "qa_agent": "qa-agent-v1",
            },
        )

    def _select_data_validation(
        self,
        requirement_text: str,
        data_validation: QAAgentDataValidationRequest | None,
    ) -> QADataValidationSelectionResult | None:
        if data_validation is None:
            return None

        if data_validation.mode == "disabled":
            return QADataValidationSelectionResult(
                decision="skipped",
                reason="Data validation was disabled by request mode.",
                matched_signals=[],
                confidence=1.0,
            )

        if data_validation.mode == "required":
            return QADataValidationSelectionResult(
                decision="selected",
                reason="Data validation was selected because request mode is required.",
                matched_signals=["required_mode"],
                confidence=1.0,
            )

        return self.data_validation_selector.select(
            requirement_text=requirement_text,
        )

    def _build_tool_calls(
        self,
        requirement_text: str,
        knowledge_documents: list[SemanticSearchDocument],
        data_validation: QAAgentDataValidationRequest | None,
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

        if data_validation is not None:
            objective = (
                data_validation.objective
                or (
                    "Validar dados relacionados ao seguinte requisito: "
                    f"{requirement_text}"
                )
            )

            tool_calls.append(
                AgentToolCall(
                    tool_name="data_analysis.agent.run",
                    arguments={
                        "objective": objective,
                        "database_schema": (
                            data_validation.database_schema.model_dump(
                                mode="json"
                            )
                        ),
                        "table_data": [
                            table_data.model_dump(mode="json")
                            for table_data in data_validation.table_data
                        ],
                        "language": language,
                        "max_rows": data_validation.max_rows,
                        "metadata": {
                            **data_validation.metadata,
                            "requested_by": "qa-agent-v1",
                            "source": "qa_agent_data_validation",
                            "selection_mode": data_validation.mode,
                        },
                    },
                    metadata={
                        "reason": (
                            "validate data evidence using the Data Analyst Agent"
                        ),
                    },
                )
            )

        return tool_calls

    def _build_context(
        self,
        knowledge_documents: list[SemanticSearchDocument],
        data_validation: QAAgentDataValidationRequest | None,
        data_validation_selection: QADataValidationSelectionResult | None,
    ) -> str | None:
        context_parts: list[str] = []

        if knowledge_documents:
            context_parts.append(
                "Documentos de apoio foram fornecidos para recuperação de "
                "contexto antes da análise de qualidade."
            )

        if data_validation_selection is not None:
            context_parts.append(
                "A seleção de validação de dados foi avaliada com decisão: "
                f"{data_validation_selection.decision}."
            )

        if data_validation is not None:
            context_parts.append(
                "Uma validação de dados foi selecionada e será executada "
                "por meio do Data Analyst Agent."
            )

        if not context_parts:
            return None

        return " ".join(context_parts)

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
