from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from ai_api.agents.schemas import AgentRunStatus, QAAgentRunResponse


QAAgentEvaluationStatus = Literal[
    "passed",
    "warning",
    "failed",
]


class QAAgentEvaluationMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    status: QAAgentEvaluationStatus
    score: float = Field(ge=0.0, le=1.0)
    details: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QAAgentEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_response: QAAgentRunResponse
    expected_status: AgentRunStatus | None = None
    expect_data_validation: bool | None = None
    expected_data_row_count: int | None = Field(default=None, ge=0)
    expected_data_columns: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QAAgentEvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: QAAgentEvaluationStatus
    score: float = Field(ge=0.0, le=1.0)
    metrics: list[QAAgentEvaluationMetric]
    metadata: dict[str, Any] = Field(default_factory=dict)


class QAAgentEvaluationService:
    def evaluate(
        self,
        request: QAAgentEvaluationRequest,
    ) -> QAAgentEvaluationResponse:
        metrics = [
            self._evaluate_status_alignment(request),
            self._evaluate_requirement_analysis(request.agent_response),
            self._evaluate_data_validation_selection(request),
            self._evaluate_data_validation_evidence(request),
            self._evaluate_result_shape(request),
            self._evaluate_tool_trace(request),
        ]

        final_status = self._resolve_final_status(metrics)
        score = sum(metric.score for metric in metrics) / len(metrics)

        return QAAgentEvaluationResponse(
            status=final_status,
            score=round(score, 4),
            metrics=metrics,
            metadata={
                **request.metadata,
                "evaluator": "qa-agent-evaluator-v1",
                "metric_count": len(metrics),
                "expected_status": request.expected_status,
                "expect_data_validation": request.expect_data_validation,
            },
        )

    def _evaluate_status_alignment(
        self,
        request: QAAgentEvaluationRequest,
    ) -> QAAgentEvaluationMetric:
        actual_status = request.agent_response.status

        if request.expected_status is None:
            return QAAgentEvaluationMetric(
                name="status_alignment",
                status="passed",
                score=1.0,
                details=(
                    "No expected status was provided. Actual status was "
                    f"{actual_status}."
                ),
                metadata={
                    "actual_status": actual_status,
                },
            )

        if actual_status == request.expected_status:
            return QAAgentEvaluationMetric(
                name="status_alignment",
                status="passed",
                score=1.0,
                details="QA Agent status matches the expected status.",
                metadata={
                    "expected_status": request.expected_status,
                    "actual_status": actual_status,
                },
            )

        return QAAgentEvaluationMetric(
            name="status_alignment",
            status="failed",
            score=0.0,
            details="QA Agent status does not match the expected status.",
            metadata={
                "expected_status": request.expected_status,
                "actual_status": actual_status,
            },
        )

    def _evaluate_requirement_analysis(
        self,
        agent_response: QAAgentRunResponse,
    ) -> QAAgentEvaluationMetric:
        requirement_analysis = agent_response.requirement_analysis

        if not requirement_analysis:
            return QAAgentEvaluationMetric(
                name="requirement_analysis",
                status="failed",
                score=0.0,
                details="Requirement analysis output is missing.",
            )

        summary = requirement_analysis.get("summary")

        if isinstance(summary, str) and summary.strip():
            return QAAgentEvaluationMetric(
                name="requirement_analysis",
                status="passed",
                score=1.0,
                details="Requirement analysis output contains a summary.",
                metadata={
                    "available_keys": sorted(requirement_analysis.keys()),
                },
            )

        return QAAgentEvaluationMetric(
            name="requirement_analysis",
            status="warning",
            score=0.5,
            details=(
                "Requirement analysis output exists, but the summary is "
                "missing or blank."
            ),
            metadata={
                "available_keys": sorted(requirement_analysis.keys()),
            },
        )

    def _evaluate_data_validation_selection(
        self,
        request: QAAgentEvaluationRequest,
    ) -> QAAgentEvaluationMetric:
        selection = request.agent_response.data_validation_selection

        if request.expect_data_validation is None:
            return QAAgentEvaluationMetric(
                name="data_validation_selection",
                status="passed",
                score=1.0,
                details="No data validation selection expectation was provided.",
                metadata={
                    "selection": selection,
                },
            )

        if request.expect_data_validation is True:
            if (
                selection is not None
                and selection.get("decision") == "selected"
            ):
                return QAAgentEvaluationMetric(
                    name="data_validation_selection",
                    status="passed",
                    score=1.0,
                    details="Data validation was selected as expected.",
                    metadata={
                        "selection": selection,
                    },
                )

            return QAAgentEvaluationMetric(
                name="data_validation_selection",
                status="failed",
                score=0.0,
                details="Data validation was expected but was not selected.",
                metadata={
                    "selection": selection,
                },
            )

        if selection is None or selection.get("decision") == "skipped":
            return QAAgentEvaluationMetric(
                name="data_validation_selection",
                status="passed",
                score=1.0,
                details="Data validation was not selected, as expected.",
                metadata={
                    "selection": selection,
                },
            )

        return QAAgentEvaluationMetric(
            name="data_validation_selection",
            status="failed",
            score=0.0,
            details="Data validation was selected but was expected to be skipped.",
            metadata={
                "selection": selection,
            },
        )

    def _evaluate_data_validation_evidence(
        self,
        request: QAAgentEvaluationRequest,
    ) -> QAAgentEvaluationMetric:
        data_validation = request.agent_response.data_validation

        if request.expect_data_validation is None:
            return QAAgentEvaluationMetric(
                name="data_validation_evidence",
                status="passed",
                score=1.0,
                details="No data validation evidence expectation was provided.",
                metadata={
                    "has_data_validation": data_validation is not None,
                },
            )

        if request.expect_data_validation is False:
            if data_validation is None:
                return QAAgentEvaluationMetric(
                    name="data_validation_evidence",
                    status="passed",
                    score=1.0,
                    details="No data validation evidence was returned, as expected.",
                )

            return QAAgentEvaluationMetric(
                name="data_validation_evidence",
                status="failed",
                score=0.0,
                details="Data validation evidence was returned unexpectedly.",
                metadata={
                    "data_validation_status": data_validation.get("status"),
                },
            )

        if data_validation is None:
            return QAAgentEvaluationMetric(
                name="data_validation_evidence",
                status="failed",
                score=0.0,
                details="Data validation evidence is missing.",
            )

        evidence = data_validation.get("evidence")

        if (
            isinstance(evidence, dict)
            and evidence.get("row_count") is not None
            and evidence.get("column_count") is not None
        ):
            return QAAgentEvaluationMetric(
                name="data_validation_evidence",
                status="passed",
                score=1.0,
                details="Data validation evidence is present.",
                metadata={
                    "row_count": evidence.get("row_count"),
                    "column_count": evidence.get("column_count"),
                },
            )

        return QAAgentEvaluationMetric(
            name="data_validation_evidence",
            status="failed",
            score=0.0,
            details="Data validation was returned but evidence is incomplete.",
            metadata={
                "evidence": evidence,
            },
        )

    def _evaluate_result_shape(
        self,
        request: QAAgentEvaluationRequest,
    ) -> QAAgentEvaluationMetric:
        expected_row_count = request.expected_data_row_count
        expected_columns = request.expected_data_columns

        if expected_row_count is None and not expected_columns:
            return QAAgentEvaluationMetric(
                name="result_shape",
                status="passed",
                score=1.0,
                details="No expected data result shape was provided.",
            )

        data_validation = request.agent_response.data_validation

        if data_validation is None:
            return QAAgentEvaluationMetric(
                name="result_shape",
                status="failed",
                score=0.0,
                details="Expected data result shape cannot be evaluated without data validation output.",
            )

        execution = (
            data_validation
            .get("workflow", {})
            .get("execution", {})
        )

        rows = execution.get("rows", [])

        if not isinstance(rows, list):
            return QAAgentEvaluationMetric(
                name="result_shape",
                status="failed",
                score=0.0,
                details="Execution rows are not represented as a list.",
                metadata={
                    "rows_type": type(rows).__name__,
                },
            )

        actual_row_count = len(rows)
        actual_columns = self._extract_column_names(execution=execution, rows=rows)

        failures: list[str] = []

        if (
            expected_row_count is not None
            and actual_row_count != expected_row_count
        ):
            failures.append(
                "row_count"
            )

        missing_columns = [
            column
            for column in expected_columns
            if column not in actual_columns
        ]

        if missing_columns:
            failures.append(
                "columns"
            )

        if not failures:
            return QAAgentEvaluationMetric(
                name="result_shape",
                status="passed",
                score=1.0,
                details="Data validation result shape matches expectations.",
                metadata={
                    "expected_row_count": expected_row_count,
                    "actual_row_count": actual_row_count,
                    "expected_columns": expected_columns,
                    "actual_columns": actual_columns,
                },
            )

        return QAAgentEvaluationMetric(
            name="result_shape",
            status="failed",
            score=0.0,
            details="Data validation result shape does not match expectations.",
            metadata={
                "failed_checks": failures,
                "expected_row_count": expected_row_count,
                "actual_row_count": actual_row_count,
                "expected_columns": expected_columns,
                "actual_columns": actual_columns,
                "missing_columns": missing_columns,
            },
        )

    def _evaluate_tool_trace(
        self,
        request: QAAgentEvaluationRequest,
    ) -> QAAgentEvaluationMetric:
        step_names = [
            step.name
            for step in request.agent_response.steps
        ]

        missing_steps: list[str] = []

        if "tool_call:requirements.analyze" not in step_names:
            missing_steps.append("tool_call:requirements.analyze")

        if (
            request.expect_data_validation is True
            and "tool_call:data_analysis.agent.run" not in step_names
        ):
            missing_steps.append("tool_call:data_analysis.agent.run")

        if (
            request.expect_data_validation is False
            and "tool_call:data_analysis.agent.run" in step_names
        ):
            return QAAgentEvaluationMetric(
                name="tool_trace",
                status="failed",
                score=0.0,
                details="Data Analyst Agent tool was called unexpectedly.",
                metadata={
                    "step_names": step_names,
                },
            )

        if not missing_steps:
            return QAAgentEvaluationMetric(
                name="tool_trace",
                status="passed",
                score=1.0,
                details="Expected tool trace was found.",
                metadata={
                    "step_names": step_names,
                },
            )

        return QAAgentEvaluationMetric(
            name="tool_trace",
            status="failed",
            score=0.0,
            details="Expected tool trace is missing required steps.",
            metadata={
                "missing_steps": missing_steps,
                "step_names": step_names,
            },
        )

    def _extract_column_names(
        self,
        execution: dict[str, Any],
        rows: list[Any],
    ) -> list[str]:
        columns = execution.get("columns", [])

        if isinstance(columns, list) and columns:
            column_names = []

            for column in columns:
                if isinstance(column, dict) and isinstance(
                    column.get("name"),
                    str,
                ):
                    column_names.append(column["name"])

            if column_names:
                return sorted(column_names)

        if rows and isinstance(rows[0], dict):
            return sorted(rows[0].keys())

        return []

    def _resolve_final_status(
        self,
        metrics: list[QAAgentEvaluationMetric],
    ) -> QAAgentEvaluationStatus:
        if any(metric.status == "failed" for metric in metrics):
            return "failed"

        if any(metric.status == "warning" for metric in metrics):
            return "warning"

        return "passed"
