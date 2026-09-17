"""Deterministic read model over existing telemetry and artifacts.

Trend compares adverse-event rates (warning or failed) in [now-7d, now]
and [now-14d, now-7d). Both windows need at least one completed event.
Summary metrics are cumulative; section status uses the latest recent result.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

from fastapi import Depends
from pydantic import BaseModel, Field

from ai_api.evals.agent_execution_metrics import AIAgentExecutionTelemetryService
from ai_api.evals.artifacts import (
    EvaluationArtifactService,
    EvaluationArtifactSummary,
    get_evaluation_artifact_service,
)
from ai_api.evals.dependencies import (
    get_ai_agent_execution_telemetry_service,
    get_ai_multi_agent_execution_telemetry_service,
    get_ai_retrieval_quality_telemetry_service,
    get_ai_usage_tracking_service,
    get_evaluation_telemetry_service,
)
from ai_api.evals.multi_agent_execution_metrics import (
    AIMultiAgentExecutionTelemetryService,
)
from ai_api.evals.retrieval_quality import AIRetrievalQualityTelemetryService
from ai_api.evals.schemas import (
    AIAgentExecutionSummaryRequest,
    AIMultiAgentExecutionSummaryRequest,
    AIRetrievalQualitySummaryRequest,
    AIUsageSummaryRequest,
    EvaluationTelemetrySummaryRequest,
)
from ai_api.evals.telemetry import EvaluationTelemetryService
from ai_api.evals.usage_tracking import AIUsageTrackingService
from ai_api.readiness import ReadinessResponse, get_readiness_report


ScorecardStatus = Literal["healthy", "warning", "critical", "no_data"]
TrendSignal = Literal["improving", "stable", "degrading", "insufficient_data"]
ScorecardName = Literal[
    "evaluation_quality",
    "retrieval_quality",
    "agent_reliability",
    "multi_agent_reliability",
    "usage_cost",
    "operational_readiness",
]
WINDOW_DAYS = 7


class QualityTrend(BaseModel):
    signal: TrendSignal
    window_days: int = WINDOW_DAYS
    recent_count: int = Field(ge=0)
    previous_count: int = Field(ge=0)
    recent_adverse_rate: float | None = Field(default=None, ge=0, le=1)
    previous_adverse_rate: float | None = Field(default=None, ge=0, le=1)


class QualityScorecardSection(BaseModel):
    name: ScorecardName
    title: str
    status: ScorecardStatus
    latest_observed_at: datetime | None
    metrics: dict[str, int | float | None]
    trend: QualityTrend
    notes: list[str] = Field(default_factory=list)


class QualityScorecardsResponse(BaseModel):
    generated_at: datetime
    sections: list[QualityScorecardSection]
    latest_evaluation_artifact: EvaluationArtifactSummary | None = None


class AIQualityScorecardService:
    def __init__(
        self,
        evaluation_service: EvaluationTelemetryService,
        retrieval_service: AIRetrievalQualityTelemetryService,
        agent_service: AIAgentExecutionTelemetryService,
        multi_agent_service: AIMultiAgentExecutionTelemetryService,
        usage_service: AIUsageTrackingService,
        artifact_service: EvaluationArtifactService,
        readiness_report: ReadinessResponse,
    ) -> None:
        self.evaluation_service = evaluation_service
        self.retrieval_service = retrieval_service
        self.agent_service = agent_service
        self.multi_agent_service = multi_agent_service
        self.usage_service = usage_service
        self.artifact_service = artifact_service
        self.readiness_report = readiness_report

    def get_scorecards(self, now: datetime | None = None) -> QualityScorecardsResponse:
        generated_at = now or datetime.now(UTC)
        if generated_at.tzinfo is None:
            raise ValueError("now must include a timezone")
        generated_at = generated_at.astimezone(UTC)

        artifacts = self.artifact_service.list_artifacts(limit=1)
        latest_artifact = artifacts.artifacts[0] if artifacts.artifacts else None

        evaluation_events = self.evaluation_service.event_store.list_events()
        retrieval_records = self.retrieval_service.record_store.list_records()
        agent_records = self.agent_service.record_store.list_records()
        multi_agent_records = self.multi_agent_service.record_store.list_records()
        usage_records = self.usage_service.record_store.list_records()

        evaluation_summary = self.evaluation_service.summarize(
            EvaluationTelemetrySummaryRequest(events=evaluation_events)
        )
        retrieval_summary = self.retrieval_service.summarize(
            AIRetrievalQualitySummaryRequest(records=retrieval_records)
        )
        agent_summary = self.agent_service.summarize(
            AIAgentExecutionSummaryRequest(records=agent_records)
        )
        multi_agent_summary = self.multi_agent_service.summarize(
            AIMultiAgentExecutionSummaryRequest(records=multi_agent_records)
        )
        usage_summary = self.usage_service.summarize(
            AIUsageSummaryRequest(records=usage_records)
        )

        evaluation_samples = self._samples(evaluation_events)
        if latest_artifact is not None:
            evaluation_samples.append(
                (latest_artifact.created_at, latest_artifact.status)
            )
        evaluation_samples.sort(key=lambda item: item[0])

        sections = [
            self._quality_section(
                name="evaluation_quality",
                title="Evaluation quality",
                samples=evaluation_samples,
                trend_samples=self._samples(evaluation_events),
                summary=evaluation_summary,
                metric_keys=(
                    "event_count", "completed_count", "warning_count",
                    "failed_count", "average_score",
                ),
                now=generated_at,
                extra_metrics={"artifact_count": artifacts.total},
            ),
            self._quality_section(
                name="retrieval_quality",
                title="Retrieval quality",
                samples=self._samples(retrieval_records),
                summary=retrieval_summary,
                metric_keys=(
                    "record_count", "passed_count", "warning_count",
                    "failed_count", "average_quality_score",
                ),
                now=generated_at,
            ),
            self._quality_section(
                name="agent_reliability",
                title="Agent reliability",
                samples=self._samples(agent_records),
                summary=agent_summary,
                metric_keys=(
                    "record_count", "passed_count", "warning_count",
                    "failed_count", "total_retries", "total_fallbacks",
                    "average_quality_score",
                ),
                now=generated_at,
            ),
            self._quality_section(
                name="multi_agent_reliability",
                title="Multi-agent reliability",
                samples=self._samples(multi_agent_records),
                summary=multi_agent_summary,
                metric_keys=(
                    "record_count", "passed_count", "warning_count",
                    "failed_count", "total_retries", "total_fallbacks",
                    "average_quality_score",
                ),
                now=generated_at,
            ),
            self._usage_section(usage_records, usage_summary, generated_at),
            self._readiness_section(generated_at),
        ]
        return QualityScorecardsResponse(
            generated_at=generated_at,
            sections=sections,
            latest_evaluation_artifact=latest_artifact,
        )

    @staticmethod
    def _samples(records: list[Any]) -> list[tuple[datetime, str]]:
        samples: list[tuple[datetime, str]] = []
        for record in records:
            timestamp = AIQualityScorecardService._parse_timestamp(
                getattr(record, "recorded_at", None)
            )
            if timestamp is not None:
                samples.append((timestamp, record.status))
        return samples

    @staticmethod
    def _parse_timestamp(raw_timestamp: str | None) -> datetime | None:
        if raw_timestamp is None:
            return None
        try:
            timestamp = datetime.fromisoformat(raw_timestamp)
        except ValueError:
            return None
        return timestamp.astimezone(UTC) if timestamp.tzinfo is not None else None

    @staticmethod
    def _metric_subset(
        summary: Any, keys: tuple[str, ...]
    ) -> dict[str, int | float | None]:
        return {key: getattr(summary, key) for key in keys}

    def _quality_section(
        self,
        name: ScorecardName,
        title: str,
        samples: list[tuple[datetime, str]],
        summary: Any,
        metric_keys: tuple[str, ...],
        now: datetime,
        trend_samples: list[tuple[datetime, str]] | None = None,
        extra_metrics: dict[str, int | float | None] | None = None,
    ) -> QualityScorecardSection:
        recent_cutoff = now - timedelta(days=WINDOW_DAYS)
        dated = sorted(
            (sample for sample in samples if sample[0] <= now),
            key=lambda item: item[0],
        )
        meaningful = [
            sample for sample in dated
            if sample[1] in {"passed", "completed", "warning", "failed"}
        ]
        recent = [sample for sample in meaningful if sample[0] >= recent_cutoff]
        latest = dated[-1] if dated else None
        status = self._status(recent[-1][1]) if recent else "no_data"
        metrics = self._metric_subset(summary, metric_keys)
        metrics.update(extra_metrics or {})
        return QualityScorecardSection(
            name=name,
            title=title,
            status=status,
            latest_observed_at=latest[0] if latest else None,
            metrics=metrics,
            trend=self._trend(
                trend_samples if trend_samples is not None else samples, now
            ),
            notes=(
                ["No observations in the recent seven-day window."]
                if status == "no_data"
                else []
            ),
        )

    def _usage_section(
        self, records: list[Any], summary: Any, now: datetime
    ) -> QualityScorecardSection:
        dated = []
        for record in records:
            timestamp = self._parse_timestamp(record.recorded_at)
            if timestamp is not None and timestamp <= now:
                dated.append((timestamp, record))
        dated.sort(key=lambda item: item[0])
        recent = [
            item for item in dated
            if now - timedelta(days=WINDOW_DAYS) <= item[0] <= now
        ]
        latest = dated[-1] if dated else None
        if not recent:
            status: ScorecardStatus = "no_data"
        elif any(item[1].total_cost_usd is None for item in recent):
            status = "warning"
        else:
            status = "healthy"
        return QualityScorecardSection(
            name="usage_cost",
            title="Usage and cost",
            status=status,
            latest_observed_at=latest[0] if latest else None,
            metrics=self._metric_subset(
                summary, ("record_count", "total_tokens", "total_cost_usd")
            ),
            trend=QualityTrend(
                signal="insufficient_data",
                recent_count=len(recent),
                previous_count=sum(
                    now - timedelta(days=2 * WINDOW_DAYS) <= item[0]
                    < now - timedelta(days=WINDOW_DAYS)
                    for item in dated
                ),
            ),
            notes=(
                ["No observations in the recent seven-day window."]
                if status == "no_data"
                else ["Cost estimates are missing for at least one recent record."]
                if status == "warning"
                else ["Cost movement is not a quality trend."]
            ),
        )

    def _readiness_section(self, now: datetime) -> QualityScorecardSection:
        status: ScorecardStatus = (
            "healthy" if self.readiness_report.status == "ready" else "critical"
        )
        checks = self.readiness_report.checks
        return QualityScorecardSection(
            name="operational_readiness",
            title="Operational readiness",
            status=status,
            latest_observed_at=now,
            metrics={
                "settings_ok": int(checks.settings == "ok"),
                "provider_ok": int(checks.provider == "ok"),
                "storage_ok": int(checks.storage in {"ok", "skipped"}),
            },
            trend=QualityTrend(
                signal="insufficient_data", recent_count=1, previous_count=0
            ),
            notes=["Readiness is a local snapshot, not a Prometheus query."],
        )

    @staticmethod
    def _status(raw_status: str) -> ScorecardStatus:
        return {
            "passed": "healthy",
            "completed": "healthy",
            "warning": "warning",
            "failed": "critical",
        }.get(raw_status, "no_data")

    @staticmethod
    def _trend(samples: list[tuple[datetime, str]], now: datetime) -> QualityTrend:
        recent_start = now - timedelta(days=WINDOW_DAYS)
        previous_start = now - timedelta(days=2 * WINDOW_DAYS)
        meaningful = [
            (timestamp, status) for timestamp, status in samples
            if status in {"passed", "completed", "warning", "failed"}
        ]
        recent = [
            status for timestamp, status in meaningful
            if recent_start <= timestamp <= now
        ]
        previous = [
            status for timestamp, status in meaningful
            if previous_start <= timestamp < recent_start
        ]
        if not recent or not previous:
            return QualityTrend(
                signal="insufficient_data",
                recent_count=len(recent),
                previous_count=len(previous),
            )
        recent_rate = sum(status in {"warning", "failed"} for status in recent) / len(
            recent
        )
        previous_rate = sum(
            status in {"warning", "failed"} for status in previous
        ) / len(previous)
        if recent_rate < previous_rate:
            signal: TrendSignal = "improving"
        elif recent_rate > previous_rate:
            signal = "degrading"
        else:
            signal = "stable"
        return QualityTrend(
            signal=signal,
            recent_count=len(recent),
            previous_count=len(previous),
            recent_adverse_rate=recent_rate,
            previous_adverse_rate=previous_rate,
        )


def get_quality_scorecard_service(
    evaluation_service: Annotated[
        EvaluationTelemetryService, Depends(get_evaluation_telemetry_service)
    ],
    retrieval_service: Annotated[
        AIRetrievalQualityTelemetryService,
        Depends(get_ai_retrieval_quality_telemetry_service),
    ],
    agent_service: Annotated[
        AIAgentExecutionTelemetryService,
        Depends(get_ai_agent_execution_telemetry_service),
    ],
    multi_agent_service: Annotated[
        AIMultiAgentExecutionTelemetryService,
        Depends(get_ai_multi_agent_execution_telemetry_service),
    ],
    usage_service: Annotated[
        AIUsageTrackingService, Depends(get_ai_usage_tracking_service)
    ],
    artifact_service: Annotated[
        EvaluationArtifactService, Depends(get_evaluation_artifact_service)
    ],
    readiness_report: Annotated[ReadinessResponse, Depends(get_readiness_report)],
) -> AIQualityScorecardService:
    return AIQualityScorecardService(
        evaluation_service,
        retrieval_service,
        agent_service,
        multi_agent_service,
        usage_service,
        artifact_service,
        readiness_report,
    )
