from ai_api.agents import ToolExecutionService, get_qa_agent_service
from ai_api.data_analysis.dependencies import get_data_analyst_agent_service
from ai_api.evals.prompt_regression import (
    PromptRegressionEvaluationService,
    PromptRegressionSuiteService,
)
from ai_api.evals.reporting import AIEvaluationReportAggregationService
from ai_api.evals.runner import GoldenEvaluationDatasetRunnerService
from ai_api.evals.services import (
    GoldenEvaluationDatasetService,
    GoldenEvaluationDatasetValidationService,
)
from ai_api.evals.telemetry import EvaluationTelemetryService
from ai_api.multi_agent import get_multi_agent_qa_copilot_service
from ai_api.requirements.dependencies import get_requirement_analyzer_service


_evaluation_telemetry_service = EvaluationTelemetryService()


def get_golden_evaluation_dataset_service() -> GoldenEvaluationDatasetService:
    return GoldenEvaluationDatasetService()


def get_golden_evaluation_dataset_validation_service() -> (
    GoldenEvaluationDatasetValidationService
):
    return GoldenEvaluationDatasetValidationService()


def get_golden_evaluation_dataset_runner_service() -> (
    GoldenEvaluationDatasetRunnerService
):
    return GoldenEvaluationDatasetRunnerService(
        requirement_analyzer_service=get_requirement_analyzer_service(),
        tool_execution_service=ToolExecutionService(),
        qa_agent_service=get_qa_agent_service(),
        data_analyst_agent_service=get_data_analyst_agent_service(),
        multi_agent_qa_copilot_service=get_multi_agent_qa_copilot_service(),
    )


def get_prompt_regression_suite_service() -> PromptRegressionSuiteService:
    return PromptRegressionSuiteService()


def get_prompt_regression_evaluation_service() -> (
    PromptRegressionEvaluationService
):
    return PromptRegressionEvaluationService()


def get_ai_evaluation_report_aggregation_service() -> (
    AIEvaluationReportAggregationService
):
    return AIEvaluationReportAggregationService()


def get_evaluation_telemetry_service() -> EvaluationTelemetryService:
    return _evaluation_telemetry_service
