from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from ai_api.data_analysis.schemas import (
    DatabaseSchema,
    DatabaseTableData,
    SQLQueryEvidence,
    SQLWorkflowRequest,
    SQLWorkflowResponse,
)
from ai_api.data_analysis.services import DataAnalystSQLWorkflowService


DataAnalystAgentStatus = Literal[
    "completed",
    "blocked",
]


class DataAnalystAgentTraceStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: str = Field(min_length=1)
    status: str = Field(min_length=1)
    message: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataAnalystAgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(min_length=1)
    database_schema: DatabaseSchema
    table_data: list[DatabaseTableData] = Field(default_factory=list)
    language: str = "pt-BR"
    max_rows: int = Field(default=100, ge=1, le=1000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective", "language")
    @classmethod
    def text_fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("value cannot be blank")

        return cleaned_value


class DataAnalystAgentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: DataAnalystAgentStatus
    agent_name: str
    objective: str
    answer: str
    workflow: SQLWorkflowResponse
    evidence: SQLQueryEvidence | None = None
    trace: list[DataAnalystAgentTraceStep] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataAnalystAgentService:
    agent_name = "data-analyst-agent-v1"

    def __init__(
        self,
        sql_workflow_service: DataAnalystSQLWorkflowService,
    ) -> None:
        self.sql_workflow_service = sql_workflow_service

    def run(
        self,
        request: DataAnalystAgentRequest,
    ) -> DataAnalystAgentResponse:
        trace: list[DataAnalystAgentTraceStep] = [
            DataAnalystAgentTraceStep(
                step="request_received",
                status="completed",
                message="Data analysis request received.",
                metadata={
                    "language": request.language,
                    "max_rows": request.max_rows,
                },
            )
        ]

        workflow_request = SQLWorkflowRequest(
            question=request.objective,
            database_schema=request.database_schema,
            table_data=request.table_data,
            language=request.language,
            max_rows=request.max_rows,
            metadata={
                **request.metadata,
                "agent_name": self.agent_name,
            },
        )

        trace.append(
            DataAnalystAgentTraceStep(
                step="sql_workflow_started",
                status="completed",
                message="SQL generation and execution workflow started.",
                metadata={},
            )
        )

        workflow = self.sql_workflow_service.run(workflow_request)

        if workflow.status == "blocked":
            trace.append(
                DataAnalystAgentTraceStep(
                    step="sql_workflow_blocked",
                    status="blocked",
                    message="Generated SQL was blocked by safety validation.",
                    metadata={
                        "generation_status": workflow.generation.status,
                    },
                )
            )

            return DataAnalystAgentResponse(
                status="blocked",
                agent_name=self.agent_name,
                objective=request.objective,
                answer=(
                    "A consulta gerada foi bloqueada pela validação de "
                    "segurança e não foi executada."
                ),
                workflow=workflow,
                evidence=None,
                trace=trace,
                metadata={
                    "agent": self.agent_name,
                    "executed": False,
                    "workflow_status": workflow.status,
                },
            )

        execution = workflow.execution

        row_count = execution.row_count if execution is not None else 0
        column_count = (
            execution.evidence.column_count
            if execution is not None
            else 0
        )

        trace.append(
            DataAnalystAgentTraceStep(
                step="sql_workflow_completed",
                status="completed",
                message="SQL workflow completed successfully.",
                metadata={
                    "row_count": row_count,
                    "column_count": column_count,
                },
            )
        )

        return DataAnalystAgentResponse(
            status="completed",
            agent_name=self.agent_name,
            objective=request.objective,
            answer=(
                "A análise foi concluída com sucesso. "
                f"A consulta foi gerada, validada e executada. "
                f"Foram retornadas {row_count} linha(s) "
                f"e {column_count} coluna(s)."
            ),
            workflow=workflow,
            evidence=workflow.evidence,
            trace=trace,
            metadata={
                "agent": self.agent_name,
                "executed": True,
                "workflow_status": workflow.status,
            },
        )
