from ai_api.agents import ToolExecutionService, get_qa_agent_service
from ai_api.data_analysis.dependencies import get_data_analyst_agent_service
from ai_api.evals.agent_tool_evaluation import (
    AgentRegressionEvaluationService,
    AgentRegressionSuiteService,
    ToolCallingEvaluationService,
    ToolCallingEvaluationSuiteService,
)
from ai_api.evals.instrumentation import EvaluationTelemetryInstrumentationService
from ai_api.evals.llm_rag_evaluation import (
    LLMOutputEvaluationService,
    LLMOutputEvaluationSuiteService,
    RAGRegressionEvaluationService,
    RAGRegressionSuiteService,
)
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
from ai_api.evals.multi_agent_regression import (
    MultiAgentCopilotRegressionEvaluationService,
    MultiAgentCopilotRegressionSuiteService,
)
from ai_api.evals.llm_as_judge import (
    LLMAsJudgeEvaluationService,
    LLMAsJudgeEvaluationSuiteService,
)
from ai_api.evals.ci_pipeline import CIEvaluationPipelineService
from ai_api.evals.usage_tracking import AIUsageTrackingService
from ai_api.evals.retrieval_quality import AIRetrievalQualityTelemetryService
from ai_api.evals.agent_execution_metrics import AIAgentExecutionTelemetryService
from ai_api.evals.multi_agent_execution_metrics import (
    AIMultiAgentExecutionTelemetryService,
)
from ai_api.evals.observability_dashboard import AIObservabilityDashboardService
from ai_api.evals.execution_history import AIExecutionHistoryService
from ai_api.config import get_settings


_ai_usage_tracking_service = AIUsageTrackingService.from_settings(
    get_settings(),
)

_evaluation_telemetry_service = EvaluationTelemetryService.from_settings(
    get_settings(),
)

_ai_retrieval_quality_telemetry_service = (
    AIRetrievalQualityTelemetryService.from_settings(
        get_settings(),
    )
)

_ai_agent_execution_telemetry_service = (
    AIAgentExecutionTelemetryService.from_settings(
        get_settings(),
    )
)

_ai_multi_agent_execution_telemetry_service = (
    AIMultiAgentExecutionTelemetryService.from_settings(
        get_settings(),
    )
)


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


def get_evaluation_telemetry_instrumentation_service() -> (
    EvaluationTelemetryInstrumentationService
):
    return EvaluationTelemetryInstrumentationService(
        telemetry_service=get_evaluation_telemetry_service(),
    )


def get_llm_output_evaluation_suite_service() -> LLMOutputEvaluationSuiteService:
    return LLMOutputEvaluationSuiteService()


def get_llm_output_evaluation_service() -> LLMOutputEvaluationService:
    return LLMOutputEvaluationService()


def get_rag_regression_suite_service() -> RAGRegressionSuiteService:
    return RAGRegressionSuiteService()


def get_rag_regression_evaluation_service() -> RAGRegressionEvaluationService:
    return RAGRegressionEvaluationService()


def get_agent_regression_suite_service() -> AgentRegressionSuiteService:
    return AgentRegressionSuiteService()


def get_agent_regression_evaluation_service() -> AgentRegressionEvaluationService:
    return AgentRegressionEvaluationService()


def get_tool_calling_evaluation_suite_service() -> ToolCallingEvaluationSuiteService:
    return ToolCallingEvaluationSuiteService()


def get_tool_calling_evaluation_service() -> ToolCallingEvaluationService:
    return ToolCallingEvaluationService()


def get_multi_agent_copilot_regression_suite_service() -> (
    MultiAgentCopilotRegressionSuiteService
):
    return MultiAgentCopilotRegressionSuiteService()


def get_multi_agent_copilot_regression_evaluation_service() -> (
    MultiAgentCopilotRegressionEvaluationService
):
    return MultiAgentCopilotRegressionEvaluationService()


def get_llm_as_judge_evaluation_suite_service() -> (
    LLMAsJudgeEvaluationSuiteService
):
    return LLMAsJudgeEvaluationSuiteService()


def get_llm_as_judge_evaluation_service() -> LLMAsJudgeEvaluationService:
    return LLMAsJudgeEvaluationService()


def get_ci_evaluation_pipeline_service() -> CIEvaluationPipelineService:
    return CIEvaluationPipelineService()


def get_ai_usage_tracking_service() -> AIUsageTrackingService:
    return _ai_usage_tracking_service


def get_ai_retrieval_quality_telemetry_service() -> (
    AIRetrievalQualityTelemetryService
):
    return _ai_retrieval_quality_telemetry_service


def get_ai_agent_execution_telemetry_service() -> (
    AIAgentExecutionTelemetryService
):
    return _ai_agent_execution_telemetry_service


def get_ai_multi_agent_execution_telemetry_service() -> (
    AIMultiAgentExecutionTelemetryService
):
    return _ai_multi_agent_execution_telemetry_service


def get_ai_observability_dashboard_service() -> (
    AIObservabilityDashboardService
):
    return AIObservabilityDashboardService(
        evaluation_telemetry_service=get_evaluation_telemetry_service(),
        usage_tracking_service=get_ai_usage_tracking_service(),
        retrieval_quality_service=get_ai_retrieval_quality_telemetry_service(),
        agent_execution_service=get_ai_agent_execution_telemetry_service(),
        multi_agent_execution_service=get_ai_multi_agent_execution_telemetry_service(),
    )


def get_ai_execution_history_service() -> AIExecutionHistoryService:
    return AIExecutionHistoryService(
        evaluation_telemetry_service=get_evaluation_telemetry_service(),
        usage_tracking_service=get_ai_usage_tracking_service(),
        retrieval_quality_service=get_ai_retrieval_quality_telemetry_service(),
        agent_execution_service=get_ai_agent_execution_telemetry_service(),
        multi_agent_execution_service=get_ai_multi_agent_execution_telemetry_service(),
    )
