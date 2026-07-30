from typing import Any
from ai_api.evals.schemas import (
    AIEvaluationReportAggregationRequest,
    AIEvaluationReportAggregationResponse,
    AIEvaluationReportSection,
    GoldenEvaluationDatasetRunResponse,
    PromptRegressionRunResponse,
)


class AIEvaluationReportAggregationService:
    def aggregate(
        self,
        request: AIEvaluationReportAggregationRequest,
    ) -> AIEvaluationReportAggregationResponse:
        sections: list[AIEvaluationReportSection] = []

        if request.golden_dataset_run is not None:
            sections.append(
                self._build_golden_dataset_section(request.golden_dataset_run)
            )

        if request.prompt_regression_run is not None:
            sections.append(
                self._build_prompt_regression_section(
                    request.prompt_regression_run
                )
            )

        if request.multi_agent_qa_copilot_evaluation is not None:
            sections.append(
                self._build_multi_agent_copilot_section(
                    request.multi_agent_qa_copilot_evaluation
                )
            )

        status = self._resolve_report_status(sections)
        score = self._calculate_report_score(sections)

        return AIEvaluationReportAggregationResponse(
            status=status,
            score=score,
            summary=self._build_summary(
                status=status,
                score=score,
                sections=sections,
            ),
            sections=sections,
            recommendations=self._build_recommendations(sections),
            metadata={
                "aggregator": "ai-evaluation-report-aggregator-v1",
                "section_count": len(sections),
                "passed_sections": self._count_sections(sections, "passed"),
                "warning_sections": self._count_sections(sections, "warning"),
                "failed_sections": self._count_sections(sections, "failed"),
                **request.metadata,
            },
        )

    @staticmethod
    def _build_golden_dataset_section(
        run: GoldenEvaluationDatasetRunResponse,
    ) -> AIEvaluationReportSection:
        denominator = max(run.scenario_count, 1)
        score = round(run.passed_count / denominator, 4)

        highlights = [
            f"Dataset: {run.dataset_name} v{run.dataset_version}.",
            f"Scenarios selected: {run.scenario_count}.",
            f"Scenarios executed: {run.executed_count}.",
            f"Scenarios passed: {run.passed_count}.",
        ]

        risks: list[str] = []

        if run.failed_count > 0:
            risks.append(
                f"{run.failed_count} golden dataset scenario(s) failed."
            )

        if run.warning_count > 0:
            risks.append(
                f"{run.warning_count} golden dataset scenario(s) returned warning."
            )

        if run.skipped_count > 0:
            risks.append(
                f"{run.skipped_count} golden dataset scenario(s) were skipped."
            )

        return AIEvaluationReportSection(
            name="golden_dataset",
            status=run.status,
            score=score,
            summary=(
                "Golden dataset run aggregated with deterministic scenario "
                "execution results."
            ),
            highlights=highlights,
            risks=risks,
            metrics={
                "scenario_count": run.scenario_count,
                "executed_count": run.executed_count,
                "passed_count": run.passed_count,
                "warning_count": run.warning_count,
                "failed_count": run.failed_count,
                "skipped_count": run.skipped_count,
            },
            metadata={
                "dataset_name": run.dataset_name,
                "dataset_version": run.dataset_version,
                "source_status": run.status,
            },
        )

    @staticmethod
    def _build_prompt_regression_section(
        run: PromptRegressionRunResponse,
    ) -> AIEvaluationReportSection:
        denominator = max(run.case_count, 1)
        score = round(run.passed_count / denominator, 4)

        highlights = [
            f"Suite: {run.suite_name} v{run.suite_version}.",
            f"Cases selected: {run.case_count}.",
            f"Cases passed: {run.passed_count}.",
        ]

        risks: list[str] = []

        if run.failed_count > 0:
            risks.append(
                f"{run.failed_count} prompt regression case(s) failed."
            )

        if run.warning_count > 0:
            risks.append(
                f"{run.warning_count} prompt regression case(s) returned warning."
            )

        return AIEvaluationReportSection(
            name="prompt_regression",
            status=run.status,
            score=score,
            summary=(
                "Prompt regression run aggregated with deterministic output "
                "validation results."
            ),
            highlights=highlights,
            risks=risks,
            metrics={
                "case_count": run.case_count,
                "passed_count": run.passed_count,
                "warning_count": run.warning_count,
                "failed_count": run.failed_count,
            },
            metadata={
                "suite_name": run.suite_name,
                "suite_version": run.suite_version,
                "source_status": run.status,
            },
        )

    @staticmethod
    def _build_multi_agent_copilot_section(
        evaluation: dict[str, Any],
    ) -> AIEvaluationReportSection:
        status = evaluation.get("status", "failed")
        score = float(evaluation.get("score", 0.0))
        metrics = evaluation.get("metrics", [])

        failed_metrics = [
            metric.get("name", "unknown")
            for metric in metrics
            if metric.get("status") == "failed"
        ]
        warning_metrics = [
            metric.get("name", "unknown")
            for metric in metrics
            if metric.get("status") == "warning"
        ]

        risks: list[str] = []

        if failed_metrics:
            risks.append(
                "Failed Multi-Agent QA Copilot evaluation metrics: "
                + ", ".join(failed_metrics)
                + "."
            )

        if warning_metrics:
            risks.append(
                "Warning Multi-Agent QA Copilot evaluation metrics: "
                + ", ".join(warning_metrics)
                + "."
            )

        metadata = evaluation.get("metadata", {})

        return AIEvaluationReportSection(
            name="multi_agent_qa_copilot",
            status=status,
            score=score,
            summary=(
                "Multi-Agent QA Copilot evaluation aggregated with deterministic "
                "quality metrics."
            ),
            highlights=[
                f"Copilot evaluation status: {status}.",
                f"Copilot evaluation score: {score}.",
                f"Metrics evaluated: {len(metrics)}.",
            ],
            risks=risks,
            metrics={
                "metric_count": len(metrics),
                "passed_metrics": metadata.get("passed_metrics", 0),
                "warning_metrics": metadata.get("warning_metrics", 0),
                "failed_metrics": metadata.get("failed_metrics", 0),
                "quality_gate": metadata.get("quality_gate", "unknown"),
            },
            metadata={
                "source_status": status,
                "evaluator": metadata.get("evaluator", "unknown"),
            },
        )

    @staticmethod
    def _build_summary(
        status: str,
        score: float,
        sections: list[AIEvaluationReportSection],
    ) -> str:
        if status == "passed":
            return (
                "AI evaluation report passed. All aggregated evaluation sections "
                f"are healthy with overall score {score}."
            )

        if status == "warning":
            return (
                "AI evaluation report completed with warnings. One or more "
                f"evaluation sections need attention. Overall score: {score}."
            )

        failed_sections = [
            section.name
            for section in sections
            if section.status == "failed"
        ]

        return (
            "AI evaluation report failed. Critical issues were found in: "
            + ", ".join(failed_sections)
            + f". Overall score: {score}."
        )

    @staticmethod
    def _build_recommendations(
        sections: list[AIEvaluationReportSection],
    ) -> list[str]:
        recommendations: list[str] = []

        section_by_name = {
            section.name: section
            for section in sections
        }

        golden_dataset = section_by_name.get("golden_dataset")
        prompt_regression = section_by_name.get("prompt_regression")
        multi_agent = section_by_name.get("multi_agent_qa_copilot")

        if golden_dataset and golden_dataset.status != "passed":
            recommendations.append(
                "Investigate failed, warning or skipped golden dataset scenarios before expanding evaluation coverage."
            )

        if prompt_regression and prompt_regression.status != "passed":
            recommendations.append(
                "Review prompt outputs that failed deterministic structure, marker or JSON-key checks."
            )

        if multi_agent and multi_agent.status != "passed":
            recommendations.append(
                "Review Multi-Agent QA Copilot metrics and fix failures related to roles, trace, contracts, conflicts, report quality or data evidence."
            )

        if not recommendations:
            recommendations.extend(
                [
                    "Keep the golden dataset stable and versioned.",
                    "Add more edge-case scenarios before enabling stricter CI gates.",
                    "Use aggregated reports as a baseline for future LLMOps dashboards.",
                ]
            )

        return recommendations

    @staticmethod
    def _resolve_report_status(
        sections: list[AIEvaluationReportSection],
    ) -> str:
        if any(section.status == "failed" for section in sections):
            return "failed"

        if any(section.status == "warning" for section in sections):
            return "warning"

        return "passed"

    @staticmethod
    def _calculate_report_score(
        sections: list[AIEvaluationReportSection],
    ) -> float:
        if not sections:
            return 0.0

        total_score = sum(section.score for section in sections)

        return round(total_score / len(sections), 4)

    @staticmethod
    def _count_sections(
        sections: list[AIEvaluationReportSection],
        status: str,
    ) -> int:
        return len(
            [
                section
                for section in sections
                if section.status == status
            ]
        )
