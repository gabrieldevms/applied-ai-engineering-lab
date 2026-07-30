from datetime import UTC, datetime
from uuid import uuid4
from ai_api.evals.schemas import (
    AIUsageRecord,
    AIUsageRecordRequest,
    AIUsageRecordsResponse,
    AIUsageSummaryRequest,
    AIUsageSummaryResponse,
)


class AIUsageTrackingService:
    def __init__(self) -> None:
        self._records: list[AIUsageRecord] = []

    def record(
        self,
        request: AIUsageRecordRequest,
    ) -> AIUsageRecord:
        total_tokens = self._calculate_total_tokens(request)
        input_cost_usd = self._calculate_token_cost(
            token_count=request.prompt_tokens,
            cost_per_1k_tokens=request.input_cost_per_1k_tokens_usd,
        )
        output_cost_usd = self._calculate_token_cost(
            token_count=request.completion_tokens,
            cost_per_1k_tokens=request.output_cost_per_1k_tokens_usd,
        )
        embedding_cost_usd = self._calculate_token_cost(
            token_count=request.embedding_tokens,
            cost_per_1k_tokens=request.embedding_cost_per_1k_tokens_usd,
        )
        total_cost_usd = self._resolve_total_cost(
            provided_total_cost_usd=request.total_cost_usd,
            input_cost_usd=input_cost_usd,
            output_cost_usd=output_cost_usd,
            embedding_cost_usd=embedding_cost_usd,
        )

        record = AIUsageRecord(
            record_id=str(uuid4()),
            provider=request.provider,
            model_name=request.model_name,
            component=request.component,
            operation=request.operation,
            prompt_tokens=request.prompt_tokens,
            completion_tokens=request.completion_tokens,
            embedding_tokens=request.embedding_tokens,
            total_tokens=total_tokens,
            input_cost_per_1k_tokens_usd=request.input_cost_per_1k_tokens_usd,
            output_cost_per_1k_tokens_usd=request.output_cost_per_1k_tokens_usd,
            embedding_cost_per_1k_tokens_usd=request.embedding_cost_per_1k_tokens_usd,
            input_cost_usd=input_cost_usd,
            output_cost_usd=output_cost_usd,
            embedding_cost_usd=embedding_cost_usd,
            total_cost_usd=total_cost_usd,
            currency=request.currency,
            recorded_at=self._utc_now(),
            run_id=request.run_id,
            trace_id=request.trace_id,
            metadata={
                "usage_schema_version": "0.1.0",
                "pricing_mode": "caller_provided",
                **request.metadata,
            },
        )

        self._records.append(record)

        return record

    def list_records(
        self,
        provider: str | None = None,
        component: str | None = None,
        model_name: str | None = None,
        limit: int = 100,
    ) -> AIUsageRecordsResponse:
        filtered_records = self._records

        if provider is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.provider == provider
            ]

        if component is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.component == component
            ]

        if model_name is not None:
            filtered_records = [
                record
                for record in filtered_records
                if record.model_name == model_name
            ]

        limited_records = filtered_records[-limit:]

        return AIUsageRecordsResponse(
            records=limited_records,
            count=len(limited_records),
            metadata={
                "source": "ai-usage-tracking-service",
                "total_stored_records": len(self._records),
                "applied_filters": {
                    "provider": provider,
                    "component": component,
                    "model_name": model_name,
                    "limit": limit,
                },
            },
        )

    def summarize(
        self,
        request: AIUsageSummaryRequest,
    ) -> AIUsageSummaryResponse:
        records = request.records if request.records is not None else self._records

        total_cost_usd = self._sum_costs(records)
        record_count_with_cost = len(
            [
                record
                for record in records
                if record.total_cost_usd is not None
            ]
        )

        average_cost_usd = None

        if total_cost_usd is not None and record_count_with_cost > 0:
            average_cost_usd = round(total_cost_usd / record_count_with_cost, 8)

        return AIUsageSummaryResponse(
            record_count=len(records),
            total_prompt_tokens=sum(record.prompt_tokens for record in records),
            total_completion_tokens=sum(
                record.completion_tokens
                for record in records
            ),
            total_embedding_tokens=sum(
                record.embedding_tokens
                for record in records
            ),
            total_tokens=sum(record.total_tokens for record in records),
            total_cost_usd=total_cost_usd,
            average_cost_usd=average_cost_usd,
            provider_coverage=self._build_coverage(
                values=[
                    record.provider
                    for record in records
                ]
            ),
            model_coverage=self._build_coverage(
                values=[
                    record.model_name
                    for record in records
                ]
            ),
            component_coverage=self._build_coverage(
                values=[
                    record.component
                    for record in records
                ]
            ),
            operation_coverage=self._build_coverage(
                values=[
                    record.operation
                    for record in records
                ]
            ),
            risks=self._build_risks(records),
            metadata={
                "summarizer": "ai-usage-summary-v1",
                "source": "stored_records"
                if request.records is None
                else "request_records",
                **request.metadata,
            },
        )

    def clear(self) -> None:
        self._records.clear()

    @staticmethod
    def _calculate_total_tokens(
        request: AIUsageRecordRequest,
    ) -> int:
        if request.total_tokens is not None:
            return request.total_tokens

        return (
            request.prompt_tokens
            + request.completion_tokens
            + request.embedding_tokens
        )

    @staticmethod
    def _calculate_token_cost(
        token_count: int,
        cost_per_1k_tokens: float | None,
    ) -> float | None:
        if cost_per_1k_tokens is None:
            return None

        return round((token_count / 1000) * cost_per_1k_tokens, 8)

    @staticmethod
    def _resolve_total_cost(
        provided_total_cost_usd: float | None,
        input_cost_usd: float | None,
        output_cost_usd: float | None,
        embedding_cost_usd: float | None,
    ) -> float | None:
        if provided_total_cost_usd is not None:
            return provided_total_cost_usd

        cost_parts = [
            cost
            for cost in [
                input_cost_usd,
                output_cost_usd,
                embedding_cost_usd,
            ]
            if cost is not None
        ]

        if not cost_parts:
            return None

        return round(sum(cost_parts), 8)

    @staticmethod
    def _sum_costs(
        records: list[AIUsageRecord],
    ) -> float | None:
        costs = [
            record.total_cost_usd
            for record in records
            if record.total_cost_usd is not None
        ]

        if not costs:
            return None

        return round(sum(costs), 8)

    @staticmethod
    def _build_coverage(
        values: list[str],
    ) -> dict[str, int]:
        coverage: dict[str, int] = {}

        for value in values:
            coverage[value] = coverage.get(value, 0) + 1

        return coverage

    @staticmethod
    def _build_risks(
        records: list[AIUsageRecord],
    ) -> list[str]:
        risks: list[str] = []

        if not records:
            risks.append("No AI usage records available.")
            return risks

        records_without_cost = [
            record
            for record in records
            if record.total_cost_usd is None
        ]

        records_without_tokens = [
            record
            for record in records
            if record.total_tokens == 0
        ]

        if records_without_cost:
            risks.append(
                f"{len(records_without_cost)} usage record(s) do not have cost data."
            )

        if records_without_tokens:
            risks.append(
                f"{len(records_without_tokens)} usage record(s) have zero total tokens."
            )

        if not risks:
            risks.append("No AI usage risks detected.")

        return risks

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat()
