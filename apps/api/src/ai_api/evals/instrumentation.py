from collections.abc import Callable
from datetime import UTC, datetime
from time import perf_counter
from typing import Any, TypeVar
from ai_api.evals.schemas import EvaluationTelemetryRecordRequest
from ai_api.evals.telemetry import EvaluationTelemetryService


T = TypeVar("T")


class EvaluationTelemetryInstrumentationService:
    def __init__(
        self,
        telemetry_service: EvaluationTelemetryService,
    ) -> None:
        self.telemetry_service = telemetry_service

    def instrument(
        self,
        event_type: str,
        component: str,
        source: str,
        operation: Callable[[], T],
        run_id: str | None = None,
        scenario_id: str | None = None,
        case_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> T:
        started_at = self._utc_now()
        started_perf_counter = perf_counter()

        try:
            result = operation()
            finished_at = self._utc_now()
            duration_ms = self._calculate_duration_ms(started_perf_counter)

            self.telemetry_service.record(
                EvaluationTelemetryRecordRequest(
                    event_type=event_type,
                    component=component,
                    status=self._resolve_telemetry_status(result),
                    source=source,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                    score=self._extract_score(result),
                    run_id=run_id,
                    scenario_id=scenario_id,
                    case_id=case_id,
                    metadata={
                        "instrumentation": (
                            "latency-error-telemetry-instrumentation-v1"
                        ),
                        "result_type": result.__class__.__name__,
                        "result_status": self._extract_result_status(result),
                        **(metadata or {}),
                    },
                )
            )

            return result

        except Exception as error:
            finished_at = self._utc_now()
            duration_ms = self._calculate_duration_ms(started_perf_counter)

            self.telemetry_service.record(
                EvaluationTelemetryRecordRequest(
                    event_type=event_type,
                    component=component,
                    status="failed",
                    source=source,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                    score=0.0,
                    run_id=run_id,
                    scenario_id=scenario_id,
                    case_id=case_id,
                    error_message=str(error),
                    metadata={
                        "instrumentation": (
                            "latency-error-telemetry-instrumentation-v1"
                        ),
                        "error_type": error.__class__.__name__,
                        **(metadata or {}),
                    },
                )
            )

            raise

    @staticmethod
    def _resolve_telemetry_status(result: Any) -> str:
        result_status = EvaluationTelemetryInstrumentationService._extract_result_status(
            result
        )

        if result_status in {"completed", "passed", "valid"}:
            return "completed"

        if result_status == "warning":
            return "warning"

        if result_status in {"failed", "invalid"}:
            return "failed"

        if result_status == "skipped":
            return "skipped"

        return "completed"

    @staticmethod
    def _extract_result_status(result: Any) -> str | None:
        return getattr(result, "status", None)

    @staticmethod
    def _extract_score(result: Any) -> float | None:
        direct_score = getattr(result, "score", None)

        if direct_score is not None:
            return float(direct_score)

        passed_count = getattr(result, "passed_count", None)

        if passed_count is None:
            return None

        denominator = getattr(result, "scenario_count", None)

        if denominator is None:
            denominator = getattr(result, "case_count", None)

        if denominator is None or denominator == 0:
            return None

        return round(float(passed_count) / float(denominator), 4)

    @staticmethod
    def _calculate_duration_ms(
        started_perf_counter: float,
    ) -> float:
        return round((perf_counter() - started_perf_counter) * 1000, 4)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
