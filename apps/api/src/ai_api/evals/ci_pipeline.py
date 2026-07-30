from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from ai_api.evals.agent_tool_evaluation import (
    AgentRegressionEvaluationService,
    build_default_agent_regression_suite,
    ToolCallingEvaluationService,
    build_default_tool_calling_evaluation_suite,
)
from ai_api.evals.llm_as_judge import (
    LLMAsJudgeEvaluationService,
    build_default_llm_as_judge_evaluation_suite,
)
from ai_api.evals.llm_rag_evaluation import (
    LLMOutputEvaluationService,
    RAGRegressionEvaluationService,
    build_default_llm_output_evaluation_suite,
    build_default_rag_regression_suite,
)
from ai_api.evals.multi_agent_regression import (
    MultiAgentCopilotRegressionEvaluationService,
    build_default_multi_agent_copilot_regression_suite,
)
from ai_api.evals.prompt_regression import (
    PromptRegressionEvaluationService,
    build_default_prompt_regression_suite,
)
from ai_api.evals.runner import GoldenEvaluationDatasetRunnerService
from ai_api.evals.schemas import (
    AgentRegressionRunRequest,
    CIEvaluationPipelineRunRequest,
    CIEvaluationPipelineRunResponse,
    CIEvaluationPipelineStageResult,
    GoldenEvaluationDatasetRunRequest,
    LLMAsJudgeEvaluationRunRequest,
    LLMOutputEvaluationRunRequest,
    MultiAgentCopilotRegressionRunRequest,
    PromptRegressionRunRequest,
    RAGRegressionRunRequest,
    ToolCallingEvaluationRunRequest,
)


class CIEvaluationPipelineService:
    def __init__(
        self,
        golden_dataset_runner_service: GoldenEvaluationDatasetRunnerService | None = None,
        prompt_regression_service: PromptRegressionEvaluationService | None = None,
        llm_output_evaluation_service: LLMOutputEvaluationService | None = None,
        rag_regression_service: RAGRegressionEvaluationService | None = None,
        agent_regression_service: AgentRegressionEvaluationService | None = None,
        tool_calling_evaluation_service: ToolCallingEvaluationService | None = None,
        multi_agent_copilot_regression_service: (
            MultiAgentCopilotRegressionEvaluationService | None
        ) = None,
        llm_as_judge_evaluation_service: LLMAsJudgeEvaluationService | None = None,
    ) -> None:
        self.golden_dataset_runner_service = (
            golden_dataset_runner_service or GoldenEvaluationDatasetRunnerService()
        )
        self.prompt_regression_service = (
            prompt_regression_service or PromptRegressionEvaluationService()
        )
        self.llm_output_evaluation_service = (
            llm_output_evaluation_service or LLMOutputEvaluationService()
        )
        self.rag_regression_service = (
            rag_regression_service or RAGRegressionEvaluationService()
        )
        self.agent_regression_service = (
            agent_regression_service or AgentRegressionEvaluationService()
        )
        self.tool_calling_evaluation_service = (
            tool_calling_evaluation_service or ToolCallingEvaluationService()
        )
        self.multi_agent_copilot_regression_service = (
            multi_agent_copilot_regression_service
            or MultiAgentCopilotRegressionEvaluationService()
        )
        self.llm_as_judge_evaluation_service = (
            llm_as_judge_evaluation_service or LLMAsJudgeEvaluationService()
        )

    def run(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineRunResponse:
        started_at = self._utc_now()
        started_perf_counter = perf_counter()

        stages: list[CIEvaluationPipelineStageResult] = []

        if request.include_golden_dataset_smoke:
            stages.append(self._run_golden_dataset_smoke_stage(request))

        if request.include_prompt_regression:
            stages.append(self._run_prompt_regression_stage(request))

        if request.include_llm_output_evaluation:
            stages.append(self._run_llm_output_evaluation_stage(request))

        if request.include_rag_regression:
            stages.append(self._run_rag_regression_stage(request))

        if request.include_agent_regression:
            stages.append(self._run_agent_regression_stage(request))

        if request.include_tool_calling_evaluation:
            stages.append(self._run_tool_calling_evaluation_stage(request))

        if request.include_multi_agent_copilot_regression:
            stages.append(self._run_multi_agent_copilot_regression_stage(request))

        if request.include_llm_as_judge_evaluation:
            stages.append(self._run_llm_as_judge_evaluation_stage(request))

        failed_count = self._count_stages(stages, "failed")
        warning_count = self._count_stages(stages, "warning")
        passed_count = self._count_stages(stages, "passed")

        status = self._resolve_status(
            failed_count=failed_count,
            warning_count=warning_count,
        )
        should_fail_ci = status == "failed" or (
            request.fail_on_warning and status == "warning"
        )

        return CIEvaluationPipelineRunResponse(
            status=status,
            score=self._calculate_score(stages),
            stage_count=len(stages),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            should_fail_ci=should_fail_ci,
            stages=stages,
            metadata={
                "runner": "ci-evaluation-pipeline-v1",
                "execution_mode": "deterministic_ci_evaluation",
                "started_at": started_at,
                "finished_at": self._utc_now(),
                "duration_ms": self._calculate_duration_ms(started_perf_counter),
                "fail_on_warning": request.fail_on_warning,
                "external_llm_required": False,
                **request.metadata,
            },
        )

    def _run_golden_dataset_smoke_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.golden_dataset_runner_service.run(
            GoldenEvaluationDatasetRunRequest(
                scenario_ids=[
                    "MCP-001",
                ],
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="golden_dataset_smoke",
            summary="Golden dataset smoke scenario executed through the CI pipeline.",
            output=output,
        )

    def _run_prompt_regression_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.prompt_regression_service.run(
            PromptRegressionRunRequest(
                suite=build_default_prompt_regression_suite(),
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="prompt_regression",
            summary="Prompt regression suite executed through the CI pipeline.",
            output=output,
        )

    def _run_llm_output_evaluation_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.llm_output_evaluation_service.run(
            LLMOutputEvaluationRunRequest(
                suite=build_default_llm_output_evaluation_suite(),
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="llm_output_evaluation",
            summary="LLM output evaluation suite executed through the CI pipeline.",
            output=output,
        )

    def _run_rag_regression_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.rag_regression_service.run(
            RAGRegressionRunRequest(
                suite=build_default_rag_regression_suite(),
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="rag_regression",
            summary="RAG regression suite executed through the CI pipeline.",
            output=output,
        )

    def _run_agent_regression_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.agent_regression_service.run(
            AgentRegressionRunRequest(
                suite=build_default_agent_regression_suite(),
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="agent_regression",
            summary="Agent regression suite executed through the CI pipeline.",
            output=output,
        )

    def _run_tool_calling_evaluation_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.tool_calling_evaluation_service.run(
            ToolCallingEvaluationRunRequest(
                suite=build_default_tool_calling_evaluation_suite(),
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="tool_calling_evaluation",
            summary="Tool-calling evaluation suite executed through the CI pipeline.",
            output=output,
        )

    def _run_multi_agent_copilot_regression_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.multi_agent_copilot_regression_service.run(
            MultiAgentCopilotRegressionRunRequest(
                suite=build_default_multi_agent_copilot_regression_suite(),
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="multi_agent_copilot_regression",
            summary=(
                "Multi-Agent QA Copilot regression suite executed through "
                "the CI pipeline."
            ),
            output=output,
        )

    def _run_llm_as_judge_evaluation_stage(
        self,
        request: CIEvaluationPipelineRunRequest,
    ) -> CIEvaluationPipelineStageResult:
        output = self.llm_as_judge_evaluation_service.run(
            LLMAsJudgeEvaluationRunRequest(
                suite=build_default_llm_as_judge_evaluation_suite(),
                metadata={
                    "source": "ci-evaluation-pipeline",
                    **request.metadata,
                },
            )
        )

        return self._build_stage_result(
            name="llm_as_judge_evaluation",
            summary="LLM-as-judge evaluation suite executed through the CI pipeline.",
            output=output,
        )

    def _build_stage_result(
        self,
        name: str,
        summary: str,
        output: Any,
    ) -> CIEvaluationPipelineStageResult:
        status = self._extract_status(output)
        score = self._extract_score(output)

        return CIEvaluationPipelineStageResult(
            name=name,
            status=status,
            score=score,
            summary=summary,
            output=self._to_output(output),
            metadata={
                "source_status": status,
                "source_score": score,
            },
        )

    @staticmethod
    def _extract_status(output: Any) -> str:
        status = getattr(output, "status", "failed")

        if status == "passed":
            return "passed"

        if status == "warning":
            return "warning"

        return "failed"

    @staticmethod
    def _extract_score(output: Any) -> float | None:
        direct_score = getattr(output, "score", None)

        if direct_score is not None:
            return float(direct_score)

        average_score = getattr(output, "average_score", None)

        if average_score is not None:
            return float(average_score)

        passed_count = getattr(output, "passed_count", None)
        case_count = getattr(output, "case_count", None)
        scenario_count = getattr(output, "scenario_count", None)

        denominator = case_count or scenario_count

        if passed_count is None or denominator in {None, 0}:
            return None

        return round(float(passed_count) / float(denominator), 4)

    @staticmethod
    def _to_output(output: Any) -> dict[str, Any]:
        if hasattr(output, "model_dump"):
            return output.model_dump(mode="json")

        if isinstance(output, dict):
            return output

        return {
            "value": str(output),
        }

    @staticmethod
    def _resolve_status(
        failed_count: int,
        warning_count: int,
    ) -> str:
        if failed_count > 0:
            return "failed"

        if warning_count > 0:
            return "warning"

        return "passed"

    @staticmethod
    def _calculate_score(
        stages: list[CIEvaluationPipelineStageResult],
    ) -> float | None:
        scores = [
            stage.score
            for stage in stages
            if stage.score is not None
        ]

        if not scores:
            return None

        return round(sum(scores) / len(scores), 4)

    @staticmethod
    def _count_stages(
        stages: list[CIEvaluationPipelineStageResult],
        status: str,
    ) -> int:
        return len(
            [
                stage
                for stage in stages
                if stage.status == status
            ]
        )

    @staticmethod
    def _calculate_duration_ms(
        started_perf_counter: float,
    ) -> float:
        return round((perf_counter() - started_perf_counter) * 1000, 4)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
