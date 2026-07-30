from typing import Any
from fastapi.testclient import TestClient
from ai_api.evals import (
    AIMultiAgentExecutionRecord,
    AIMultiAgentExecutionRecordsResponse,
    AIMultiAgentExecutionSummaryResponse,
    get_ai_multi_agent_execution_telemetry_service,
)
from ai_api.main import app


class StubAIMultiAgentExecutionTelemetryService:
    def __init__(self) -> None:
        self.last_record_request: Any | None = None
        self.last_summary_request: Any | None = None

    def record(self, request: Any) -> AIMultiAgentExecutionRecord:
        self.last_record_request = request

        return AIMultiAgentExecutionRecord(
            record_id="multi-agent-execution-record-001",
            component=request.component,
            operation=request.operation,
            workflow_name=request.workflow_name,
            run_status=request.run_status,
            status="passed",
            duration_ms=request.duration_ms,
            agent_count=request.agent_count,
            completed_agent_count=request.completed_agent_count,
            failed_agent_count=request.failed_agent_count,
            skipped_agent_count=request.skipped_agent_count,
            task_count=request.task_count,
            successful_task_count=request.successful_task_count,
            failed_task_count=request.failed_task_count,
            artifact_count=request.artifact_count,
            expected_min_artifacts=request.expected_min_artifacts,
            handoff_count=request.handoff_count,
            failed_handoff_count=request.failed_handoff_count,
            contract_check_count=request.contract_check_count,
            passed_contract_check_count=request.passed_contract_check_count,
            failed_contract_check_count=request.failed_contract_check_count,
            conflict_count=request.conflict_count,
            critical_conflict_count=request.critical_conflict_count,
            failure_count=request.failure_count,
            error_count=request.error_count,
            final_report_section_count=request.final_report_section_count,
            expected_min_final_report_sections=(
                request.expected_min_final_report_sections
            ),
            data_validation_evidence_count=request.data_validation_evidence_count,
            require_data_validation_evidence=request.require_data_validation_evidence,
            retry_count=request.retry_count,
            fallback_count=request.fallback_count,
            agent_success_rate=1.0,
            task_success_rate=1.0,
            handoff_success_rate=1.0,
            contract_success_rate=1.0,
            artifact_coverage_score=1.0,
            final_report_coverage_score=1.0,
            data_validation_score=1.0
            if request.require_data_validation_evidence
            else None,
            quality_score=1.0,
            max_duration_ms=request.max_duration_ms,
            max_failed_agents=request.max_failed_agents,
            max_failed_tasks=request.max_failed_tasks,
            max_failed_handoffs=request.max_failed_handoffs,
            max_failed_contract_checks=request.max_failed_contract_checks,
            max_critical_conflicts=request.max_critical_conflicts,
            max_failures=request.max_failures,
            max_errors=request.max_errors,
            min_quality_score=request.min_quality_score,
            risks=[
                "No multi-agent execution risks detected.",
            ],
            recorded_at="2026-07-30T20:00:00+00:00",
            metadata={
                "source": "stub-multi-agent-execution-service",
            },
        )

    def list_records(
        self,
        component: str | None = None,
        workflow_name: str | None = None,
        operation: str | None = None,
        status: str | None = None,
        run_status: str | None = None,
        limit: int = 100,
    ) -> AIMultiAgentExecutionRecordsResponse:
        return AIMultiAgentExecutionRecordsResponse(
            records=[
                AIMultiAgentExecutionRecord(
                    record_id="multi-agent-execution-record-001",
                    component="multi_agent",
                    operation="qa_copilot_run",
                    workflow_name="multi-agent-qa-copilot-v1",
                    run_status="completed",
                    status="passed",
                    duration_ms=1000.0,
                    agent_count=6,
                    completed_agent_count=6,
                    failed_agent_count=0,
                    skipped_agent_count=0,
                    task_count=6,
                    successful_task_count=6,
                    failed_task_count=0,
                    artifact_count=6,
                    expected_min_artifacts=6,
                    handoff_count=5,
                    failed_handoff_count=0,
                    contract_check_count=6,
                    passed_contract_check_count=6,
                    failed_contract_check_count=0,
                    conflict_count=0,
                    critical_conflict_count=0,
                    failure_count=0,
                    error_count=0,
                    final_report_section_count=6,
                    expected_min_final_report_sections=6,
                    data_validation_evidence_count=1,
                    require_data_validation_evidence=True,
                    retry_count=0,
                    fallback_count=0,
                    agent_success_rate=1.0,
                    task_success_rate=1.0,
                    handoff_success_rate=1.0,
                    contract_success_rate=1.0,
                    artifact_coverage_score=1.0,
                    final_report_coverage_score=1.0,
                    data_validation_score=1.0,
                    quality_score=1.0,
                    max_failed_agents=0,
                    max_failed_tasks=0,
                    max_failed_handoffs=0,
                    max_failed_contract_checks=0,
                    max_critical_conflicts=0,
                    max_failures=0,
                    max_errors=0,
                    min_quality_score=0.7,
                    risks=[
                        "No multi-agent execution risks detected.",
                    ],
                    recorded_at="2026-07-30T20:00:00+00:00",
                )
            ],
            count=1,
            metadata={
                "component": component,
                "workflow_name": workflow_name,
                "operation": operation,
                "status": status,
                "run_status": run_status,
                "limit": limit,
            },
        )

    def summarize(self, request: Any) -> AIMultiAgentExecutionSummaryResponse:
        self.last_summary_request = request

        return AIMultiAgentExecutionSummaryResponse(
            record_count=1,
            passed_count=1,
            warning_count=0,
            failed_count=0,
            total_agents=6,
            total_completed_agents=6,
            total_failed_agents=0,
            total_skipped_agents=0,
            total_tasks=6,
            total_successful_tasks=6,
            total_failed_tasks=0,
            total_artifacts=6,
            total_handoffs=5,
            total_failed_handoffs=0,
            total_contract_checks=6,
            total_passed_contract_checks=6,
            total_failed_contract_checks=0,
            total_conflicts=0,
            total_critical_conflicts=0,
            total_failures=0,
            total_errors=0,
            total_final_report_sections=6,
            total_data_validation_evidence=1,
            total_retries=0,
            total_fallbacks=0,
            average_duration_ms=1000.0,
            average_agent_success_rate=1.0,
            average_task_success_rate=1.0,
            average_handoff_success_rate=1.0,
            average_contract_success_rate=1.0,
            average_artifact_coverage_score=1.0,
            average_final_report_coverage_score=1.0,
            average_data_validation_score=1.0,
            average_quality_score=1.0,
            component_coverage={
                "multi_agent": 1,
            },
            workflow_coverage={
                "multi-agent-qa-copilot-v1": 1,
            },
            operation_coverage={
                "qa_copilot_run": 1,
            },
            run_status_coverage={
                "completed": 1,
            },
            risks=[
                "No multi-agent execution risks detected.",
            ],
            metadata={
                "source": "stub-multi-agent-execution-service",
            },
        )


def test_record_multi_agent_execution_endpoint_should_return_record() -> None:
    service = StubAIMultiAgentExecutionTelemetryService()
    app.dependency_overrides[
        get_ai_multi_agent_execution_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/multi-agent-execution/records",
            json={
                "component": "multi_agent",
                "operation": "qa_copilot_run",
                "workflow_name": "multi-agent-qa-copilot-v1",
                "run_status": "completed",
                "duration_ms": 2500.0,
                "agent_count": 6,
                "completed_agent_count": 6,
                "failed_agent_count": 0,
                "skipped_agent_count": 0,
                "task_count": 6,
                "successful_task_count": 6,
                "failed_task_count": 0,
                "artifact_count": 6,
                "expected_min_artifacts": 6,
                "handoff_count": 5,
                "failed_handoff_count": 0,
                "contract_check_count": 6,
                "passed_contract_check_count": 6,
                "failed_contract_check_count": 0,
                "final_report_section_count": 6,
                "expected_min_final_report_sections": 6,
                "data_validation_evidence_count": 1,
                "require_data_validation_evidence": True,
                "metadata": {
                    "source": "api-test"
                }
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_id"] == "multi-agent-execution-record-001"
        assert body["component"] == "multi_agent"
        assert body["operation"] == "qa_copilot_run"
        assert body["workflow_name"] == "multi-agent-qa-copilot-v1"
        assert body["run_status"] == "completed"
        assert body["status"] == "passed"
        assert body["quality_score"] == 1.0

        assert service.last_record_request is not None
        assert service.last_record_request.workflow_name == (
            "multi-agent-qa-copilot-v1"
        )
    finally:
        app.dependency_overrides.clear()


def test_list_multi_agent_execution_records_endpoint_should_return_records() -> None:
    app.dependency_overrides[
        get_ai_multi_agent_execution_telemetry_service
    ] = lambda: StubAIMultiAgentExecutionTelemetryService()

    try:
        client = TestClient(app)

        response = client.get(
            "/observability/multi-agent-execution/records?workflow_name=multi-agent-qa-copilot-v1&status=passed&limit=10"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["count"] == 1
        assert body["records"][0]["workflow_name"] == "multi-agent-qa-copilot-v1"
        assert body["metadata"]["workflow_name"] == "multi-agent-qa-copilot-v1"
        assert body["metadata"]["status"] == "passed"
        assert body["metadata"]["limit"] == 10
    finally:
        app.dependency_overrides.clear()


def test_summarize_multi_agent_execution_endpoint_should_return_summary() -> None:
    service = StubAIMultiAgentExecutionTelemetryService()
    app.dependency_overrides[
        get_ai_multi_agent_execution_telemetry_service
    ] = lambda: service

    try:
        client = TestClient(app)

        response = client.post(
            "/observability/multi-agent-execution/summary",
            json={
                "metadata": {
                    "source": "api-test"
                }
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["passed_count"] == 1
        assert body["average_quality_score"] == 1.0
        assert body["workflow_coverage"]["multi-agent-qa-copilot-v1"] == 1

        assert service.last_summary_request is not None
        assert service.last_summary_request.metadata["source"] == "api-test"
    finally:
        app.dependency_overrides.clear()


def test_summarize_stored_multi_agent_execution_endpoint_should_return_summary() -> None:
    app.dependency_overrides[
        get_ai_multi_agent_execution_telemetry_service
    ] = lambda: StubAIMultiAgentExecutionTelemetryService()

    try:
        client = TestClient(app)

        response = client.get("/observability/multi-agent-execution/summary")

        assert response.status_code == 200

        body = response.json()

        assert body["record_count"] == 1
        assert body["total_agents"] == 6
        assert body["average_agent_success_rate"] == 1.0
    finally:
        app.dependency_overrides.clear()


def test_record_multi_agent_execution_endpoint_should_reject_invalid_run_status() -> None:
    client = TestClient(app)

    response = client.post(
        "/observability/multi-agent-execution/records",
        json={
            "component": "multi_agent",
            "operation": "qa_copilot_run",
            "workflow_name": "multi-agent-qa-copilot-v1",
            "run_status": "invalid-status",
        },
    )

    assert response.status_code == 422
