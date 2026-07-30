from datetime import UTC, datetime
from typing import Any
from ai_api.evals.schemas import (
    AIAgentExecutionSummaryRequest,
    AIMultiAgentExecutionSummaryRequest,
    AIObservabilityDashboardResponse,
    AIObservabilityDashboardSection,
    AIRetrievalQualitySummaryRequest,
    AIUsageSummaryRequest,
    EvaluationTelemetrySummaryRequest,
)


class AIObservabilityDashboardService:
    def __init__(
        self,
        evaluation_telemetry_service: Any | None = None,
        usage_tracking_service: Any | None = None,
        retrieval_quality_service: Any | None = None,
        agent_execution_service: Any | None = None,
        multi_agent_execution_service: Any | None = None,
    ) -> None:
        self._evaluation_telemetry_service = evaluation_telemetry_service
        self._usage_tracking_service = usage_tracking_service
        self._retrieval_quality_service = retrieval_quality_service
        self._agent_execution_service = agent_execution_service
        self._multi_agent_execution_service = multi_agent_execution_service

    def get_dashboard(self) -> AIObservabilityDashboardResponse:
        sections = [
            self._build_evaluation_telemetry_section(),
            self._build_usage_section(),
            self._build_retrieval_quality_section(),
            self._build_agent_execution_section(),
            self._build_multi_agent_execution_section(),
        ]

        available_sections = [
            section
            for section in sections
            if section is not None
        ]

        return AIObservabilityDashboardResponse(
            status=self._resolve_dashboard_status(available_sections),
            generated_at=self._utc_now(),
            sections=available_sections,
            global_risks=self._build_global_risks(available_sections),
            recommendations=self._build_global_recommendations(
                available_sections
            ),
            metadata={
                "dashboard_schema_version": "0.1.0",
                "dashboard_type": "backend_observability_read_model",
                "future_frontend": "AI Quality Command Center",
                "section_count": len(available_sections),
            },
        )

    def _build_evaluation_telemetry_section(
        self,
    ) -> AIObservabilityDashboardSection | None:
        if self._evaluation_telemetry_service is None:
            return None

        return self._build_summary_section(
            name="evaluation_telemetry",
            title="Structured AI execution telemetry",
            service=self._evaluation_telemetry_service,
            request=EvaluationTelemetrySummaryRequest(),
            count_keys=[
                "record_count",
                "event_count",
                "total_events",
                "count",
            ],
            failure_keys=[
                "failed_count",
                "failure_count",
                "error_count",
                "total_errors",
            ],
            warning_keys=[
                "warning_count",
                "fallback_count",
                "total_fallbacks",
            ],
        )

    def _build_usage_section(
        self,
    ) -> AIObservabilityDashboardSection | None:
        if self._usage_tracking_service is None:
            return None

        return self._build_summary_section(
            name="usage",
            title="Token and cost usage",
            service=self._usage_tracking_service,
            request=AIUsageSummaryRequest(),
            count_keys=[
                "record_count",
            ],
            failure_keys=[],
            warning_keys=[],
        )

    def _build_retrieval_quality_section(
        self,
    ) -> AIObservabilityDashboardSection | None:
        if self._retrieval_quality_service is None:
            return None

        return self._build_summary_section(
            name="retrieval_quality",
            title="Retrieval quality metrics",
            service=self._retrieval_quality_service,
            request=AIRetrievalQualitySummaryRequest(),
            count_keys=[
                "record_count",
            ],
            failure_keys=[
                "failed_count",
            ],
            warning_keys=[
                "warning_count",
            ],
        )

    def _build_agent_execution_section(
        self,
    ) -> AIObservabilityDashboardSection | None:
        if self._agent_execution_service is None:
            return None

        return self._build_summary_section(
            name="agent_execution",
            title="Agent execution metrics",
            service=self._agent_execution_service,
            request=AIAgentExecutionSummaryRequest(),
            count_keys=[
                "record_count",
            ],
            failure_keys=[
                "failed_count",
                "total_errors",
            ],
            warning_keys=[
                "warning_count",
                "total_retries",
                "total_fallbacks",
            ],
        )

    def _build_multi_agent_execution_section(
        self,
    ) -> AIObservabilityDashboardSection | None:
        if self._multi_agent_execution_service is None:
            return None

        return self._build_summary_section(
            name="multi_agent_execution",
            title="Multi-agent execution metrics",
            service=self._multi_agent_execution_service,
            request=AIMultiAgentExecutionSummaryRequest(),
            count_keys=[
                "record_count",
            ],
            failure_keys=[
                "failed_count",
                "total_failures",
                "total_errors",
                "total_critical_conflicts",
            ],
            warning_keys=[
                "warning_count",
                "total_retries",
                "total_fallbacks",
            ],
        )

    def _build_summary_section(
        self,
        name: str,
        title: str,
        service: Any,
        request: Any,
        count_keys: list[str],
        failure_keys: list[str],
        warning_keys: list[str],
    ) -> AIObservabilityDashboardSection:
        try:
            summary = self._summarize_service(
                service=service,
                request=request,
            )
            metrics = self._to_dict(summary)
            risks = self._extract_meaningful_risks(metrics)
            status = self._resolve_section_status(
                metrics=metrics,
                risks=risks,
                count_keys=count_keys,
                failure_keys=failure_keys,
                warning_keys=warning_keys,
            )

            return AIObservabilityDashboardSection(
                name=name,
                title=title,
                status=status,
                metrics=metrics,
                risks=risks
                if risks
                else [
                    f"No {name.replace('_', ' ')} risks detected.",
                ],
                recommendations=self._build_section_recommendations(
                    section_title=title,
                    status=status,
                    risks=risks,
                ),
                metadata={
                    "source": "observability-dashboard-service",
                    "summary_mode": "stored_records",
                },
            )
        except Exception as exc:
            return AIObservabilityDashboardSection(
                name=name,
                title=title,
                status="critical",
                metrics={},
                risks=[
                    f"Failed to build dashboard section: {type(exc).__name__}: {exc}",
                ],
                recommendations=[
                    f"Investigate the {title} summary service before relying on this dashboard section.",
                ],
                metadata={
                    "source": "observability-dashboard-service",
                    "summary_mode": "error",
                },
            )

    @staticmethod
    def _summarize_service(
        service: Any,
        request: Any,
    ) -> Any:
        try:
            return service.summarize(request)
        except TypeError:
            return service.summarize()

    @staticmethod
    def _to_dict(value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        if hasattr(value, "model_dump"):
            return value.model_dump()

        return {
            "value": str(value),
        }

    @staticmethod
    def _resolve_section_status(
        metrics: dict[str, Any],
        risks: list[str],
        count_keys: list[str],
        failure_keys: list[str],
        warning_keys: list[str],
    ) -> str:
        record_count = AIObservabilityDashboardService._first_number(
            metrics=metrics,
            keys=count_keys,
        )

        if record_count == 0:
            return "empty"

        failure_count = AIObservabilityDashboardService._sum_numbers(
            metrics=metrics,
            keys=failure_keys,
        )
        warning_count = AIObservabilityDashboardService._sum_numbers(
            metrics=metrics,
            keys=warning_keys,
        )

        if failure_count > 0:
            return "critical"

        if warning_count > 0 or risks:
            return "warning"

        return "healthy"

    @staticmethod
    def _resolve_dashboard_status(
        sections: list[AIObservabilityDashboardSection],
    ) -> str:
        if not sections:
            return "empty"

        non_empty_sections = [
            section
            for section in sections
            if section.status != "empty"
        ]

        if not non_empty_sections:
            return "empty"

        if any(section.status == "critical" for section in sections):
            return "critical"

        if any(section.status in {"warning", "empty"} for section in sections):
            return "warning"

        return "healthy"

    @staticmethod
    def _extract_meaningful_risks(
        metrics: dict[str, Any],
    ) -> list[str]:
        raw_risks = metrics.get("risks", [])

        if not isinstance(raw_risks, list):
            return []

        meaningful_risks: list[str] = []

        for risk in raw_risks:
            if not isinstance(risk, str):
                continue

            normalized_risk = risk.strip()

            if not normalized_risk:
                continue

            if (
                normalized_risk.startswith("No ")
                and (
                    "risks detected" in normalized_risk
                    or "records available" in normalized_risk
                    or "events available" in normalized_risk
                )
            ):
                continue

            meaningful_risks.append(normalized_risk)

        return meaningful_risks

    @staticmethod
    def _build_global_risks(
        sections: list[AIObservabilityDashboardSection],
    ) -> list[str]:
        risks: list[str] = []

        for section in sections:
            if section.status == "empty":
                risks.append(
                    f"{section.title} has no recorded observability data."
                )
                continue

            for risk in section.risks:
                if (
                    risk.startswith("No ")
                    and "risks detected" in risk
                ):
                    continue

                risks.append(f"{section.title}: {risk}")

        if not risks:
            risks.append("No global observability risks detected.")

        return risks

    @staticmethod
    def _build_global_recommendations(
        sections: list[AIObservabilityDashboardSection],
    ) -> list[str]:
        if not sections:
            return [
                "Enable observability services before relying on dashboard output.",
            ]

        recommendations: list[str] = []

        if any(section.status == "critical" for section in sections):
            recommendations.append(
                "Prioritize critical observability sections before expanding new AI capabilities."
            )

        if any(section.status == "warning" for section in sections):
            recommendations.append(
                "Review warning sections and decide whether thresholds or execution behavior need adjustment."
            )

        if any(section.status == "empty" for section in sections):
            recommendations.append(
                "Record representative observability events before using the dashboard as a release signal."
            )

        if not recommendations:
            recommendations.append(
                "Observability indicators are healthy. Continue monitoring trends across evaluation and agent workflows."
            )

        return recommendations

    @staticmethod
    def _build_section_recommendations(
        section_title: str,
        status: str,
        risks: list[str],
    ) -> list[str]:
        if status == "critical":
            return [
                f"Investigate critical risks in {section_title}.",
                "Avoid treating the current AI workflow as release-ready until the critical signals are understood.",
            ]

        if status == "warning":
            return [
                f"Review warning signals in {section_title}.",
                "Check whether the current thresholds match the expected quality bar.",
            ]

        if status == "empty":
            return [
                f"Record data for {section_title} before using this section for decision-making.",
            ]

        if risks:
            return [
                f"Review detected risks in {section_title}.",
            ]

        return [
            f"Continue monitoring {section_title} over time.",
        ]

    @staticmethod
    def _first_number(
        metrics: dict[str, Any],
        keys: list[str],
    ) -> float:
        for key in keys:
            value = metrics.get(key)

            if isinstance(value, int | float):
                return float(value)

        return 0.0

    @staticmethod
    def _sum_numbers(
        metrics: dict[str, Any],
        keys: list[str],
    ) -> float:
        total = 0.0

        for key in keys:
            value = metrics.get(key)

            if isinstance(value, int | float):
                total += float(value)

        return total

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
