from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


AIExecutionHistoryType = Literal[
    "evaluation_telemetry",
    "usage",
    "retrieval_quality",
    "agent_execution",
    "multi_agent_execution",
]


class AIExecutionHistoryRecord(BaseModel):
    execution_id: str
    execution_type: AIExecutionHistoryType
    title: str
    status: str
    component: str
    operation: str
    run_id: str | None = None
    recorded_at: str
    duration_ms: float | None = None
    quality_score: float | None = None
    summary: str
    source_record_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIExecutionHistoryResponse(BaseModel):
    records: list[AIExecutionHistoryRecord] = Field(default_factory=list)
    count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIExecutionHistoryService:
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

    def list_history(
        self,
        execution_type: str | None = None,
        status: str | None = None,
        component: str | None = None,
        run_id: str | None = None,
        limit: int = 100,
    ) -> AIExecutionHistoryResponse:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        source_limit = max(limit, 100)

        records = self._build_records(limit=source_limit)

        filtered_records = [
            record
            for record in records
            if self._matches_filters(
                record=record,
                execution_type=execution_type,
                status=status,
                component=component,
                run_id=run_id,
            )
        ]

        sorted_records = sorted(
            filtered_records,
            key=self._recorded_at_sort_key,
            reverse=True,
        )

        limited_records = sorted_records[:limit]

        return AIExecutionHistoryResponse(
            records=limited_records,
            count=len(limited_records),
            metadata={
                "source": "ai-execution-history-service",
                "history_mode": "observability_read_model",
                "total_unfiltered_records": len(records),
                "total_filtered_records": len(filtered_records),
                "applied_filters": {
                    "execution_type": execution_type,
                    "status": status,
                    "component": component,
                    "run_id": run_id,
                    "limit": limit,
                },
            },
        )

    def _build_records(
        self,
        limit: int,
    ) -> list[AIExecutionHistoryRecord]:
        records: list[AIExecutionHistoryRecord] = []

        records.extend(self._build_evaluation_telemetry_records(limit=limit))
        records.extend(self._build_usage_records(limit=limit))
        records.extend(self._build_retrieval_quality_records(limit=limit))
        records.extend(self._build_agent_execution_records(limit=limit))
        records.extend(self._build_multi_agent_execution_records(limit=limit))

        return records

    def _build_evaluation_telemetry_records(
        self,
        limit: int,
    ) -> list[AIExecutionHistoryRecord]:
        if self._evaluation_telemetry_service is None:
            return []

        try:
            response = self._evaluation_telemetry_service.list_events(
                limit=limit,
            )
        except Exception:
            return []

        return [
            AIExecutionHistoryRecord(
                execution_id=f"evaluation_telemetry:{event.event_id}",
                execution_type="evaluation_telemetry",
                title=f"Evaluation telemetry: {event.event_type}",
                status=event.status,
                component=event.component,
                operation=event.event_type,
                run_id=event.run_id,
                recorded_at=event.recorded_at,
                duration_ms=event.duration_ms,
                quality_score=event.score,
                summary=self._build_evaluation_summary(event),
                source_record_id=event.event_id,
                metadata={
                    "source": "evaluation_telemetry",
                    "source_model": event.__class__.__name__,
                    "source_event_type": event.event_type,
                    "source_status": event.status,
                    "scenario_id": event.scenario_id,
                    "case_id": event.case_id,
                    "error_message": event.error_message,
                    "source_metadata": event.metadata,
                },
            )
            for event in response.events
        ]

    def _build_usage_records(
        self,
        limit: int,
    ) -> list[AIExecutionHistoryRecord]:
        if self._usage_tracking_service is None:
            return []

        try:
            response = self._usage_tracking_service.list_records(
                limit=limit,
            )
        except Exception:
            return []

        return [
            AIExecutionHistoryRecord(
                execution_id=f"usage:{record.record_id}",
                execution_type="usage",
                title=f"Usage: {record.component}/{record.operation}",
                status="recorded",
                component=record.component,
                operation=record.operation,
                run_id=record.run_id,
                recorded_at=record.recorded_at,
                duration_ms=None,
                quality_score=None,
                summary=self._build_usage_summary(record),
                source_record_id=record.record_id,
                metadata={
                    "source": "usage_tracking",
                    "source_model": record.__class__.__name__,
                    "provider": record.provider,
                    "model_name": record.model_name,
                    "total_tokens": record.total_tokens,
                    "total_cost_usd": record.total_cost_usd,
                    "currency": record.currency,
                    "source_metadata": record.metadata,
                },
            )
            for record in response.records
        ]

    def _build_retrieval_quality_records(
        self,
        limit: int,
    ) -> list[AIExecutionHistoryRecord]:
        if self._retrieval_quality_service is None:
            return []

        try:
            response = self._retrieval_quality_service.list_records(
                limit=limit,
            )
        except Exception:
            return []

        return [
            AIExecutionHistoryRecord(
                execution_id=f"retrieval_quality:{record.record_id}",
                execution_type="retrieval_quality",
                title=f"Retrieval quality: {record.operation}",
                status=record.status,
                component=record.component,
                operation=record.operation,
                run_id=record.run_id,
                recorded_at=record.recorded_at,
                duration_ms=None,
                quality_score=record.quality_score,
                summary=self._build_retrieval_quality_summary(record),
                source_record_id=record.record_id,
                metadata={
                    "source": "retrieval_quality",
                    "source_model": record.__class__.__name__,
                    "query": record.query,
                    "retrieved_chunks_count": record.retrieved_chunks_count,
                    "citation_count": record.citation_count,
                    "risks": record.risks,
                    "source_metadata": record.metadata,
                },
            )
            for record in response.records
        ]

    def _build_agent_execution_records(
        self,
        limit: int,
    ) -> list[AIExecutionHistoryRecord]:
        if self._agent_execution_service is None:
            return []

        try:
            response = self._agent_execution_service.list_records(
                limit=limit,
            )
        except Exception:
            return []

        return [
            AIExecutionHistoryRecord(
                execution_id=f"agent_execution:{record.record_id}",
                execution_type="agent_execution",
                title=f"Agent execution: {record.agent_name}",
                status=record.status,
                component=record.component,
                operation=record.operation,
                run_id=record.run_id,
                recorded_at=record.recorded_at,
                duration_ms=record.duration_ms,
                quality_score=record.quality_score,
                summary=self._build_agent_execution_summary(record),
                source_record_id=record.record_id,
                metadata={
                    "source": "agent_execution",
                    "source_model": record.__class__.__name__,
                    "agent_name": record.agent_name,
                    "run_status": record.run_status,
                    "risks": record.risks,
                    "source_metadata": record.metadata,
                },
            )
            for record in response.records
        ]

    def _build_multi_agent_execution_records(
        self,
        limit: int,
    ) -> list[AIExecutionHistoryRecord]:
        if self._multi_agent_execution_service is None:
            return []

        try:
            response = self._multi_agent_execution_service.list_records(
                limit=limit,
            )
        except Exception:
            return []

        return [
            AIExecutionHistoryRecord(
                execution_id=f"multi_agent_execution:{record.record_id}",
                execution_type="multi_agent_execution",
                title=f"Multi-agent execution: {record.workflow_name}",
                status=record.status,
                component=record.component,
                operation=record.operation,
                run_id=record.run_id,
                recorded_at=record.recorded_at,
                duration_ms=record.duration_ms,
                quality_score=record.quality_score,
                summary=self._build_multi_agent_execution_summary(record),
                source_record_id=record.record_id,
                metadata={
                    "source": "multi_agent_execution",
                    "source_model": record.__class__.__name__,
                    "workflow_name": record.workflow_name,
                    "run_status": record.run_status,
                    "agent_count": record.agent_count,
                    "task_count": record.task_count,
                    "risks": record.risks,
                    "source_metadata": record.metadata,
                },
            )
            for record in response.records
        ]

    @staticmethod
    def _matches_filters(
        record: AIExecutionHistoryRecord,
        execution_type: str | None,
        status: str | None,
        component: str | None,
        run_id: str | None,
    ) -> bool:
        if execution_type is not None and record.execution_type != execution_type:
            return False

        if status is not None and record.status != status:
            return False

        if component is not None and record.component != component:
            return False

        if run_id is not None and record.run_id != run_id:
            return False

        return True

    @staticmethod
    def _recorded_at_sort_key(
        record: AIExecutionHistoryRecord,
    ) -> datetime:
        try:
            return datetime.fromisoformat(record.recorded_at)
        except ValueError:
            return datetime.min

    @staticmethod
    def _build_evaluation_summary(event: Any) -> str:
        if event.error_message:
            return (
                f"{event.event_type} finished with status {event.status}: "
                f"{event.error_message}"
            )

        if event.score is not None:
            return (
                f"{event.event_type} finished with status {event.status} "
                f"and score {event.score}."
            )

        return f"{event.event_type} finished with status {event.status}."

    @staticmethod
    def _build_usage_summary(record: Any) -> str:
        cost_part = (
            f" and estimated cost {record.total_cost_usd} {record.currency}"
            if record.total_cost_usd is not None
            else ""
        )

        return (
            f"{record.operation} used {record.total_tokens} token(s)"
            f"{cost_part}."
        )

    @staticmethod
    def _build_retrieval_quality_summary(record: Any) -> str:
        return (
            f"{record.operation} retrieved {record.retrieved_chunks_count} "
            f"chunk(s), produced {record.citation_count} citation(s), "
            f"and finished with quality score {record.quality_score}."
        )

    @staticmethod
    def _build_agent_execution_summary(record: Any) -> str:
        return (
            f"{record.agent_name} finished with run status "
            f"{record.run_status}, {record.step_count} step(s), "
            f"{record.tool_call_count} tool call(s), and quality score "
            f"{record.quality_score}."
        )

    @staticmethod
    def _build_multi_agent_execution_summary(record: Any) -> str:
        return (
            f"{record.workflow_name} finished with run status "
            f"{record.run_status}, {record.agent_count} agent(s), "
            f"{record.task_count} task(s), {record.artifact_count} artifact(s), "
            f"and quality score {record.quality_score}."
        )
