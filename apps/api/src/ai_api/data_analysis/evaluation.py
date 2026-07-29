from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from ai_api.data_analysis.agent import (
    DataAnalystAgentResponse,
    DataAnalystAgentStatus,
)


DataAnalystEvaluationStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class DataAnalystAgentEvaluationMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    status: DataAnalystEvaluationStatus
    score: float = Field(ge=0.0, le=1.0)
    message: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataAnalystAgentEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_response: DataAnalystAgentResponse
    expected_status: DataAnalystAgentStatus | None = None
    expected_row_count: int | None = Field(default=None, ge=0)
    expected_columns: list[str] = Field(default_factory=list)
    expected_language: str = "pt-BR"
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataAnalystAgentEvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: DataAnalystEvaluationStatus
    score: float = Field(ge=0.0, le=1.0)
    metrics: list[DataAnalystAgentEvaluationMetric]
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataAnalystAgentEvaluationService:
    evaluator_name = "data-analyst-agent-evaluator-v1"

    def evaluate(
        self,
        request: DataAnalystAgentEvaluationRequest,
    ) -> DataAnalystAgentEvaluationResponse:
        metrics = [
            self._evaluate_status_alignment(request),
            self._evaluate_sql_safety(request.agent_response),
            self._evaluate_execution_control(request.agent_response),
            self._evaluate_evidence(request.agent_response),
            self._evaluate_result_shape(request),
            self._evaluate_language(request),
        ]

        score = round(
            sum(metric.score for metric in metrics) / len(metrics),
            4,
        )

        status = self._resolve_status(metrics)

        return DataAnalystAgentEvaluationResponse(
            status=status,
            score=score,
            metrics=metrics,
            metadata={
                "evaluator": self.evaluator_name,
                "metric_count": len(metrics),
                "failed_metric_count": len(
                    [
                        metric
                        for metric in metrics
                        if metric.status == "failed"
                    ]
                ),
                "warning_metric_count": len(
                    [
                        metric
                        for metric in metrics
                        if metric.status == "warning"
                    ]
                ),
            },
        )

    def _evaluate_status_alignment(
        self,
        request: DataAnalystAgentEvaluationRequest,
    ) -> DataAnalystAgentEvaluationMetric:
        if request.expected_status is None:
            return DataAnalystAgentEvaluationMetric(
                name="status_alignment",
                status="passed",
                score=1.0,
                message="No expected status was provided.",
                metadata={
                    "actual_status": request.agent_response.status,
                },
            )

        if request.agent_response.status == request.expected_status:
            return DataAnalystAgentEvaluationMetric(
                name="status_alignment",
                status="passed",
                score=1.0,
                message="Agent status matches the expected status.",
                metadata={
                    "expected_status": request.expected_status,
                    "actual_status": request.agent_response.status,
                },
            )

        return DataAnalystAgentEvaluationMetric(
            name="status_alignment",
            status="failed",
            score=0.0,
            message="Agent status does not match the expected status.",
            metadata={
                "expected_status": request.expected_status,
                "actual_status": request.agent_response.status,
            },
        )

    def _evaluate_sql_safety(
        self,
        agent_response: DataAnalystAgentResponse,
    ) -> DataAnalystAgentEvaluationMetric:
        generation = agent_response.workflow.generation

        if agent_response.status == "completed":
            if (
                generation.status == "approved"
                and generation.validation.status == "approved"
            ):
                return DataAnalystAgentEvaluationMetric(
                    name="sql_safety",
                    status="passed",
                    score=1.0,
                    message="Generated SQL was approved by safety validation.",
                    metadata={
                        "generation_status": generation.status,
                        "validation_status": generation.validation.status,
                    },
                )

            return DataAnalystAgentEvaluationMetric(
                name="sql_safety",
                status="failed",
                score=0.0,
                message="Completed agent response contains non-approved SQL.",
                metadata={
                    "generation_status": generation.status,
                    "validation_status": generation.validation.status,
                },
            )

        if agent_response.status == "blocked":
            if (
                generation.status == "blocked"
                or generation.validation.status == "blocked"
            ):
                return DataAnalystAgentEvaluationMetric(
                    name="sql_safety",
                    status="passed",
                    score=1.0,
                    message="Unsafe generated SQL was blocked.",
                    metadata={
                        "generation_status": generation.status,
                        "validation_status": generation.validation.status,
                    },
                )

            return DataAnalystAgentEvaluationMetric(
                name="sql_safety",
                status="failed",
                score=0.0,
                message="Blocked agent response does not contain blocked SQL validation.",
                metadata={
                    "generation_status": generation.status,
                    "validation_status": generation.validation.status,
                },
            )

        return DataAnalystAgentEvaluationMetric(
            name="sql_safety",
            status="failed",
            score=0.0,
            message="Unknown agent status for SQL safety evaluation.",
            metadata={
                "agent_status": agent_response.status,
            },
        )

    def _evaluate_execution_control(
        self,
        agent_response: DataAnalystAgentResponse,
    ) -> DataAnalystAgentEvaluationMetric:
        workflow = agent_response.workflow

        if agent_response.status == "blocked":
            if workflow.execution is None and workflow.evidence is None:
                return DataAnalystAgentEvaluationMetric(
                    name="execution_control",
                    status="passed",
                    score=1.0,
                    message="Blocked workflow was not executed.",
                    metadata={
                        "executed": False,
                    },
                )

            return DataAnalystAgentEvaluationMetric(
                name="execution_control",
                status="failed",
                score=0.0,
                message="Blocked workflow should not contain execution output.",
                metadata={
                    "has_execution": workflow.execution is not None,
                    "has_evidence": workflow.evidence is not None,
                },
            )

        if workflow.execution is not None and workflow.execution.status == "executed":
            return DataAnalystAgentEvaluationMetric(
                name="execution_control",
                status="passed",
                score=1.0,
                message="Approved workflow was executed.",
                metadata={
                    "execution_status": workflow.execution.status,
                },
            )

        return DataAnalystAgentEvaluationMetric(
            name="execution_control",
            status="failed",
            score=0.0,
            message="Completed workflow does not contain executed SQL output.",
            metadata={
                "has_execution": workflow.execution is not None,
            },
        )

    def _evaluate_evidence(
        self,
        agent_response: DataAnalystAgentResponse,
    ) -> DataAnalystAgentEvaluationMetric:
        if agent_response.status == "blocked":
            if agent_response.evidence is None:
                return DataAnalystAgentEvaluationMetric(
                    name="evidence",
                    status="passed",
                    score=1.0,
                    message="Blocked response correctly returned no execution evidence.",
                    metadata={},
                )

            return DataAnalystAgentEvaluationMetric(
                name="evidence",
                status="failed",
                score=0.0,
                message="Blocked response should not include execution evidence.",
                metadata={},
            )

        if agent_response.evidence is None:
            return DataAnalystAgentEvaluationMetric(
                name="evidence",
                status="failed",
                score=0.0,
                message="Completed response should include execution evidence.",
                metadata={},
            )

        return DataAnalystAgentEvaluationMetric(
            name="evidence",
            status="passed",
            score=1.0,
            message="Completed response includes execution evidence.",
            metadata={
                "row_count": agent_response.evidence.row_count,
                "column_count": agent_response.evidence.column_count,
                "truncated": agent_response.evidence.truncated,
            },
        )

    def _evaluate_result_shape(
        self,
        request: DataAnalystAgentEvaluationRequest,
    ) -> DataAnalystAgentEvaluationMetric:
        agent_response = request.agent_response

        if agent_response.status != "completed":
            return DataAnalystAgentEvaluationMetric(
                name="result_shape",
                status="passed",
                score=1.0,
                message="No result shape evaluation was required for a blocked response.",
                metadata={
                    "agent_status": agent_response.status,
                },
            )

        execution = agent_response.workflow.execution

        if execution is None:
            return DataAnalystAgentEvaluationMetric(
                name="result_shape",
                status="failed",
                score=0.0,
                message="Completed response does not contain execution results.",
                metadata={},
            )

        failures: list[str] = []

        if (
            request.expected_row_count is not None
            and execution.row_count != request.expected_row_count
        ):
            failures.append("row_count_mismatch")

        actual_columns = [
            column.name
            for column in execution.columns
        ]

        missing_columns = [
            expected_column
            for expected_column in request.expected_columns
            if expected_column not in actual_columns
        ]

        if missing_columns:
            failures.append("missing_columns")

        if failures:
            return DataAnalystAgentEvaluationMetric(
                name="result_shape",
                status="failed",
                score=0.0,
                message="Execution result shape does not match expectations.",
                metadata={
                    "failures": failures,
                    "expected_row_count": request.expected_row_count,
                    "actual_row_count": execution.row_count,
                    "expected_columns": request.expected_columns,
                    "actual_columns": actual_columns,
                    "missing_columns": missing_columns,
                },
            )

        return DataAnalystAgentEvaluationMetric(
            name="result_shape",
            status="passed",
            score=1.0,
            message="Execution result shape matches expectations.",
            metadata={
                "expected_row_count": request.expected_row_count,
                "actual_row_count": execution.row_count,
                "expected_columns": request.expected_columns,
                "actual_columns": actual_columns,
            },
        )

    def _evaluate_language(
        self,
        request: DataAnalystAgentEvaluationRequest,
    ) -> DataAnalystAgentEvaluationMetric:
        expected_language = request.expected_language.strip()

        if not expected_language:
            return DataAnalystAgentEvaluationMetric(
                name="language",
                status="warning",
                score=0.5,
                message="Expected language was blank.",
                metadata={},
            )

        if expected_language.lower().startswith("pt"):
            if self._looks_like_portuguese(
                request.agent_response.answer
            ):
                return DataAnalystAgentEvaluationMetric(
                    name="language",
                    status="passed",
                    score=1.0,
                    message="Agent answer appears to follow the expected Portuguese language.",
                    metadata={
                        "expected_language": expected_language,
                    },
                )

            return DataAnalystAgentEvaluationMetric(
                name="language",
                status="warning",
                score=0.5,
                message="Agent answer may not follow the expected Portuguese language.",
                metadata={
                    "expected_language": expected_language,
                    "answer": request.agent_response.answer,
                },
            )

        return DataAnalystAgentEvaluationMetric(
            name="language",
            status="passed",
            score=1.0,
            message="Language evaluation is currently enforced for Portuguese only.",
            metadata={
                "expected_language": expected_language,
            },
        )

    def _looks_like_portuguese(
        self,
        text: str,
    ) -> bool:
        normalized_text = text.lower()

        portuguese_markers = [
            "análise",
            "consulta",
            "segurança",
            "executada",
            "linha",
            "coluna",
            "não",
            "foi",
            "com sucesso",
        ]

        return any(
            marker in normalized_text
            for marker in portuguese_markers
        )

    def _resolve_status(
        self,
        metrics: list[DataAnalystAgentEvaluationMetric],
    ) -> DataAnalystEvaluationStatus:
        if any(metric.status == "failed" for metric in metrics):
            return "failed"

        if any(metric.status == "warning" for metric in metrics):
            return "warning"

        return "passed"
