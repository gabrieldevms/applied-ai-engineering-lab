from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from ai_api.data_analysis.schemas import (
    SQLWorkflowRequest,
    SQLWorkflowResponse,
    SQLWorkflowStatus,
)
from ai_api.data_analysis.services import DataAnalystSQLWorkflowService


SQLRegressionCheckStatus = Literal[
    "passed",
    "failed",
]

SQLRegressionScenarioStatus = Literal[
    "passed",
    "failed",
]


class SQLRegressionExpectedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_status: SQLWorkflowStatus | None = None
    expected_row_count: int | None = Field(default=None, ge=0)
    expected_columns: list[str] = Field(default_factory=list)
    expected_rows: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLRegressionScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(default="")
    request: SQLWorkflowRequest
    expected_result: SQLRegressionExpectedResult
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLRegressionCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    status: SQLRegressionCheckStatus
    details: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLRegressionScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    name: str
    status: SQLRegressionScenarioStatus
    checks: list[SQLRegressionCheckResult]
    workflow_response: SQLWorkflowResponse
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLRegressionSuiteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suite_name: str = Field(default="sql-workflow-regression-suite")
    scenarios: list[SQLRegressionScenario] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLRegressionSuiteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suite_name: str
    status: SQLRegressionScenarioStatus
    total_scenarios: int = Field(ge=0)
    passed_scenarios: int = Field(ge=0)
    failed_scenarios: int = Field(ge=0)
    results: list[SQLRegressionScenarioResult]
    metadata: dict[str, Any] = Field(default_factory=dict)


class SQLWorkflowRegressionService:
    def __init__(
        self,
        workflow_service: DataAnalystSQLWorkflowService,
    ) -> None:
        self.workflow_service = workflow_service

    def run_suite(
        self,
        request: SQLRegressionSuiteRequest,
    ) -> SQLRegressionSuiteResponse:
        results = [
            self.run_scenario(scenario)
            for scenario in request.scenarios
        ]

        failed_scenarios = [
            result
            for result in results
            if result.status == "failed"
        ]

        return SQLRegressionSuiteResponse(
            suite_name=request.suite_name,
            status="failed" if failed_scenarios else "passed",
            total_scenarios=len(results),
            passed_scenarios=len(results) - len(failed_scenarios),
            failed_scenarios=len(failed_scenarios),
            results=results,
            metadata={
                **request.metadata,
                "runner": "sql-workflow-regression-service-v1",
            },
        )

    def run_scenario(
        self,
        scenario: SQLRegressionScenario,
    ) -> SQLRegressionScenarioResult:
        workflow_response = self.workflow_service.run(
            scenario.request,
        )

        checks = [
            self._check_status(
                workflow_response=workflow_response,
                expected_result=scenario.expected_result,
            ),
            self._check_row_count(
                workflow_response=workflow_response,
                expected_result=scenario.expected_result,
            ),
            self._check_columns(
                workflow_response=workflow_response,
                expected_result=scenario.expected_result,
            ),
            self._check_rows(
                workflow_response=workflow_response,
                expected_result=scenario.expected_result,
            ),
        ]

        failed_checks = [
            check
            for check in checks
            if check.status == "failed"
        ]

        return SQLRegressionScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="failed" if failed_checks else "passed",
            checks=checks,
            workflow_response=workflow_response,
            metadata={
                **scenario.metadata,
                "failed_check_count": len(failed_checks),
                "check_count": len(checks),
            },
        )

    def _check_status(
        self,
        workflow_response: SQLWorkflowResponse,
        expected_result: SQLRegressionExpectedResult,
    ) -> SQLRegressionCheckResult:
        expected_status = expected_result.expected_status

        if expected_status is None:
            return SQLRegressionCheckResult(
                name="status",
                status="passed",
                details="No expected workflow status was provided.",
                metadata={
                    "actual_status": workflow_response.status,
                },
            )

        if workflow_response.status == expected_status:
            return SQLRegressionCheckResult(
                name="status",
                status="passed",
                details="Workflow status matches the expected status.",
                metadata={
                    "expected_status": expected_status,
                    "actual_status": workflow_response.status,
                },
            )

        return SQLRegressionCheckResult(
            name="status",
            status="failed",
            details="Workflow status does not match the expected status.",
            metadata={
                "expected_status": expected_status,
                "actual_status": workflow_response.status,
            },
        )

    def _check_row_count(
        self,
        workflow_response: SQLWorkflowResponse,
        expected_result: SQLRegressionExpectedResult,
    ) -> SQLRegressionCheckResult:
        expected_row_count = expected_result.expected_row_count

        if expected_row_count is None:
            return SQLRegressionCheckResult(
                name="row_count",
                status="passed",
                details="No expected row count was provided.",
            )

        rows = workflow_response.execution.rows
        actual_row_count = len(rows)

        if actual_row_count == expected_row_count:
            return SQLRegressionCheckResult(
                name="row_count",
                status="passed",
                details="Execution row count matches the expected value.",
                metadata={
                    "expected_row_count": expected_row_count,
                    "actual_row_count": actual_row_count,
                },
            )

        return SQLRegressionCheckResult(
            name="row_count",
            status="failed",
            details="Execution row count does not match the expected value.",
            metadata={
                "expected_row_count": expected_row_count,
                "actual_row_count": actual_row_count,
            },
        )

    def _check_columns(
        self,
        workflow_response: SQLWorkflowResponse,
        expected_result: SQLRegressionExpectedResult,
    ) -> SQLRegressionCheckResult:
        expected_columns = expected_result.expected_columns

        if not expected_columns:
            return SQLRegressionCheckResult(
                name="columns",
                status="passed",
                details="No expected columns were provided.",
            )

        actual_columns = self._extract_actual_columns(
            workflow_response,
        )

        missing_columns = [
            column
            for column in expected_columns
            if column not in actual_columns
        ]

        if not missing_columns:
            return SQLRegressionCheckResult(
                name="columns",
                status="passed",
                details="Execution columns include all expected columns.",
                metadata={
                    "expected_columns": expected_columns,
                    "actual_columns": actual_columns,
                },
            )

        return SQLRegressionCheckResult(
            name="columns",
            status="failed",
            details="Execution columns are missing expected columns.",
            metadata={
                "expected_columns": expected_columns,
                "actual_columns": actual_columns,
                "missing_columns": missing_columns,
            },
        )

    def _check_rows(
        self,
        workflow_response: SQLWorkflowResponse,
        expected_result: SQLRegressionExpectedResult,
    ) -> SQLRegressionCheckResult:
        expected_rows = expected_result.expected_rows

        if not expected_rows:
            return SQLRegressionCheckResult(
                name="rows",
                status="passed",
                details="No expected rows were provided.",
            )

        actual_rows = workflow_response.execution.rows

        if actual_rows == expected_rows:
            return SQLRegressionCheckResult(
                name="rows",
                status="passed",
                details="Execution rows match the expected rows exactly.",
                metadata={
                    "expected_rows": expected_rows,
                    "actual_rows": actual_rows,
                },
            )

        return SQLRegressionCheckResult(
            name="rows",
            status="failed",
            details="Execution rows do not match the expected rows.",
            metadata={
                "expected_rows": expected_rows,
                "actual_rows": actual_rows,
            },
        )

    def _extract_actual_columns(
        self,
        workflow_response: SQLWorkflowResponse,
    ) -> list[str]:
        columns = [
            column.name
            for column in workflow_response.execution.columns
        ]

        if columns:
            return sorted(columns)

        rows = workflow_response.execution.rows

        if rows:
            first_row = rows[0]

            if isinstance(first_row, dict):
                return sorted(first_row.keys())

        return []
