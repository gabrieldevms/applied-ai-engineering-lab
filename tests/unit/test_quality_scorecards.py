import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from ai_api.evals import (
    AIAgentExecutionRecordRequest,
    AIAgentExecutionTelemetryService,
    AIMultiAgentExecutionRecordRequest,
    AIMultiAgentExecutionTelemetryService,
    AIRetrievalQualityRecordRequest,
    AIRetrievalQualityTelemetryService,
    AIUsageRecordRequest,
    AIUsageTrackingService,
    CIEvaluationPipelineRunResponse,
    EvaluationTelemetryRecordRequest,
    EvaluationTelemetryService,
)
from ai_api.evals.artifacts import EvaluationArtifactService
from ai_api.evals.quality_scorecards import (
    AIQualityScorecardService,
    get_quality_scorecard_service,
)
from ai_api.main import app
from ai_api.readiness import ReadinessChecks, ReadinessResponse


def _service(tmp_path: Path, ready: bool = True) -> AIQualityScorecardService:
    return AIQualityScorecardService(
        evaluation_service=EvaluationTelemetryService(),
        retrieval_service=AIRetrievalQualityTelemetryService(),
        agent_service=AIAgentExecutionTelemetryService(),
        multi_agent_service=AIMultiAgentExecutionTelemetryService(),
        usage_service=AIUsageTrackingService(),
        artifact_service=EvaluationArtifactService(tmp_path),
        readiness_report=ReadinessResponse(
            status="ready" if ready else "not_ready",
            checks=ReadinessChecks(
                settings="ok",
                provider="ok" if ready else "failed",
                storage="ok",
            ),
        ),
    )


def _sections(service: AIQualityScorecardService, now: datetime):
    return {section.name: section for section in service.get_scorecards(now).sections}


def test_scorecards_make_missing_data_and_readiness_explicit(tmp_path: Path) -> None:
    now = datetime(2026, 9, 17, tzinfo=UTC)
    scorecards = _service(tmp_path, ready=False).get_scorecards(now)
    sections = {section.name: section for section in scorecards.sections}

    assert len(sections) == 6
    assert all(
        section.status == "no_data"
        for name, section in sections.items()
        if name != "operational_readiness"
    )
    assert sections["operational_readiness"].status == "critical"
    assert sections["operational_readiness"].metrics["provider_ok"] == 0
    assert all(section.trend.signal == "insufficient_data" for section in sections.values())
    assert scorecards.latest_evaluation_artifact is None


def test_retrieval_trend_compares_explicit_seven_day_windows(tmp_path: Path) -> None:
    now = datetime(2026, 9, 17, tzinfo=UTC)
    service = _service(tmp_path)
    failed = service.retrieval_service.record(
        AIRetrievalQualityRecordRequest(
            component="rag", operation="rag_retrieve", query="secret query",
            retrieved_chunks_count=0, expected_min_retrieved_chunks=1,
        )
    )
    failed.recorded_at = (now - timedelta(days=8)).isoformat()
    passed = service.retrieval_service.record(
        AIRetrievalQualityRecordRequest(
            component="rag", operation="rag_retrieve", query="another secret",
            retrieved_chunks_count=2, relevant_chunks_count=2,
            citation_count=1, average_similarity_score=0.9,
            expected_min_retrieved_chunks=1,
        )
    )
    passed.recorded_at = (now - timedelta(days=1)).isoformat()

    section = _sections(service, now)["retrieval_quality"]
    assert section.status == "healthy"
    assert section.trend.signal == "improving"
    assert section.trend.recent_count == 1
    assert section.trend.previous_count == 1
    assert section.trend.recent_adverse_rate == 0
    assert section.trend.previous_adverse_rate == 1
    assert section.metrics["record_count"] == 2
    assert "secret query" not in section.model_dump_json()


def test_trend_reports_degrading_stable_and_insufficient_data() -> None:
    now = datetime(2026, 9, 17, tzinfo=UTC)
    previous = now - timedelta(days=8)
    recent = now - timedelta(days=1)
    trend = AIQualityScorecardService._trend

    assert trend([(previous, "passed"), (recent, "failed")], now).signal == (
        "degrading"
    )
    assert trend([(previous, "warning"), (recent, "failed")], now).signal == (
        "stable"
    )
    assert trend([(recent, "passed")], now).signal == "insufficient_data"
    assert trend([(previous, "passed"), (recent, "skipped")], now).signal == (
        "insufficient_data"
    )


def test_stale_quality_records_show_no_current_data(tmp_path: Path) -> None:
    now = datetime(2026, 9, 17, tzinfo=UTC)
    service = _service(tmp_path)
    event = service.evaluation_service.record(
        EvaluationTelemetryRecordRequest(
            event_type="evaluation_run", component="evaluation",
            status="completed", source="test",
        )
    )
    event.recorded_at = (now - timedelta(days=20)).isoformat()

    section = _sections(service, now)["evaluation_quality"]
    assert section.status == "no_data"
    assert section.latest_observed_at == now - timedelta(days=20)
    assert section.metrics["event_count"] == 1


def test_agent_and_multi_agent_failures_are_critical(tmp_path: Path) -> None:
    service = _service(tmp_path)
    now = datetime.now(UTC) + timedelta(seconds=1)
    service.agent_service.record(
        AIAgentExecutionRecordRequest(
            component="agent", operation="qa_agent_run", agent_name="qa-agent-v1",
            run_status="failed", step_count=2, successful_step_count=1,
            failed_step_count=1, max_failed_steps=0,
        )
    )
    service.multi_agent_service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent", operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1", run_status="failed",
            agent_count=2, completed_agent_count=1, failed_agent_count=1,
            max_failed_agents=0, task_count=2, successful_task_count=1,
            failed_task_count=1, max_failed_tasks=0,
        )
    )

    sections = _sections(service, now)
    assert sections["agent_reliability"].status == "critical"
    assert sections["agent_reliability"].metrics["failed_count"] == 1
    assert sections["multi_agent_reliability"].status == "critical"
    assert sections["multi_agent_reliability"].metrics["failed_count"] == 1


def test_evaluation_artifact_and_telemetry_use_safe_latest_state(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    service = _service(tmp_path)
    event = service.evaluation_service.record(
        EvaluationTelemetryRecordRequest(
            event_type="ci_evaluation_pipeline_run", component="evaluation",
            status="failed", source="private-provider-url",
            error_message="secret error", metadata={"prompt": "private prompt"},
        )
    )
    event.recorded_at = (now - timedelta(days=8)).isoformat()
    artifact = service.artifact_service.save_pipeline(
        CIEvaluationPipelineRunResponse(
            status="passed", score=1, stage_count=0, passed_count=0,
            warning_count=0, failed_count=0, should_fail_ci=False,
            metadata={"credential": "private credential"},
        ),
        source="api",
    )

    response = service.get_scorecards(now + timedelta(seconds=1))
    section = {item.name: item for item in response.sections}["evaluation_quality"]
    assert section.status == "healthy"
    assert section.metrics["artifact_count"] == 1
    assert section.trend.signal == "insufficient_data"
    assert response.latest_evaluation_artifact is not None
    assert response.latest_evaluation_artifact.artifact_id == artifact.artifact_id
    serialized = response.model_dump_json()
    assert "private-provider-url" not in serialized
    assert "secret error" not in serialized
    assert "private prompt" not in serialized
    assert "private credential" not in serialized


def test_usage_missing_cost_is_warning_and_does_not_invent_quality_trend(
    tmp_path: Path,
) -> None:
    now = datetime.now(UTC)
    service = _service(tmp_path)
    service.usage_service.record(
        AIUsageRecordRequest(
            provider="unknown", model_name="private-model", component="llm",
            operation="llm_call", prompt_tokens=100, completion_tokens=50,
        )
    )
    section = _sections(service, now + timedelta(seconds=1))["usage_cost"]

    assert section.status == "warning"
    assert section.metrics["total_tokens"] == 150
    assert section.trend.signal == "insufficient_data"
    assert "private-model" not in section.model_dump_json()


def test_quality_scorecards_api_preserves_existing_dashboard_contract(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    app.dependency_overrides[get_quality_scorecard_service] = lambda: service
    try:
        client = TestClient(app)
        response = client.get("/observability/quality-scorecards")
        dashboard = client.get("/observability/dashboard")
        assert response.status_code == 200
        assert [section["name"] for section in response.json()["sections"]] == [
            "evaluation_quality", "retrieval_quality", "agent_reliability",
            "multi_agent_reliability", "usage_cost", "operational_readiness",
        ]
        assert dashboard.status_code == 200
        assert "sections" in dashboard.json()
        assert "latest_evaluation_artifact" in response.json()
        json.dumps(response.json())
    finally:
        app.dependency_overrides.clear()
