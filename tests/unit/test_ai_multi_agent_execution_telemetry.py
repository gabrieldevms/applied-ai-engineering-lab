import pytest
from pydantic import ValidationError
from ai_api.evals import (
    AIMultiAgentExecutionRecord,
    AIMultiAgentExecutionRecordRequest,
    AIMultiAgentExecutionSummaryRequest,
    AIMultiAgentExecutionTelemetryService,
)


def test_multi_agent_execution_service_should_record_passed_metrics() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    record = service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=2500.0,
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
            max_duration_ms=3000.0,
            run_id="multi-agent-run-001",
            metadata={
                "source": "unit-test",
            },
        )
    )

    assert record.record_id
    assert record.status == "passed"
    assert record.run_status == "completed"
    assert record.workflow_name == "multi-agent-qa-copilot-v1"
    assert record.agent_success_rate == 1.0
    assert record.task_success_rate == 1.0
    assert record.handoff_success_rate == 1.0
    assert record.contract_success_rate == 1.0
    assert record.artifact_coverage_score == 1.0
    assert record.final_report_coverage_score == 1.0
    assert record.data_validation_score == 1.0
    assert record.quality_score == 1.0
    assert record.risks == [
        "No multi-agent execution risks detected.",
    ]
    assert record.metadata["multi_agent_execution_schema_version"] == "0.1.0"
    assert record.metadata["source"] == "unit-test"


def test_multi_agent_execution_service_should_warn_when_duration_exceeds_limit() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    record = service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=4500.0,
            agent_count=2,
            completed_agent_count=2,
            task_count=2,
            successful_task_count=2,
            max_duration_ms=1000.0,
        )
    )

    assert record.status == "warning"
    assert record.quality_score == 1.0
    assert record.risks == [
        "Multi-agent execution duration exceeded the configured maximum.",
    ]


def test_multi_agent_execution_service_should_warn_when_agent_is_skipped() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    record = service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=1000.0,
            agent_count=3,
            completed_agent_count=2,
            skipped_agent_count=1,
            task_count=2,
            successful_task_count=2,
        )
    )

    assert record.status == "warning"
    assert "One or more agents were skipped." in record.risks


def test_multi_agent_execution_service_should_fail_when_run_status_failed() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    record = service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="failed",
            duration_ms=800.0,
            agent_count=6,
            completed_agent_count=3,
            failed_agent_count=3,
            max_failed_agents=0,
            task_count=6,
            successful_task_count=3,
            failed_task_count=3,
            max_failed_tasks=0,
            failure_count=1,
            max_failures=0,
            error_count=1,
            max_errors=0,
        )
    )

    assert record.status == "failed"
    assert record.quality_score < 0.7
    assert record.risks == [
        "Multi-agent run ended with a non-success terminal status.",
        "Failed agent count exceeded the configured maximum.",
        "Failed task count exceeded the configured maximum.",
        "Failure count exceeded the configured maximum.",
        "Error count exceeded the configured maximum.",
        "Multi-agent execution quality score is below the configured minimum.",
    ]


def test_multi_agent_execution_service_should_fail_when_contract_or_conflict_limits_are_exceeded() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    record = service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=1200.0,
            agent_count=6,
            completed_agent_count=6,
            task_count=6,
            successful_task_count=6,
            contract_check_count=6,
            passed_contract_check_count=4,
            failed_contract_check_count=2,
            max_failed_contract_checks=0,
            conflict_count=2,
            critical_conflict_count=1,
            max_critical_conflicts=0,
        )
    )

    assert record.status == "failed"
    assert "Failed contract check count exceeded the configured maximum." in record.risks
    assert "Critical conflict count exceeded the configured maximum." in record.risks


def test_multi_agent_execution_service_should_fail_when_required_outputs_are_missing() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    record = service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=900.0,
            agent_count=6,
            completed_agent_count=6,
            task_count=6,
            successful_task_count=6,
            artifact_count=3,
            expected_min_artifacts=6,
            final_report_section_count=2,
            expected_min_final_report_sections=6,
            require_data_validation_evidence=True,
            data_validation_evidence_count=0,
        )
    )

    assert record.status == "failed"
    assert "Artifact count is below the expected minimum." in record.risks
    assert "Final report section count is below the expected minimum." in record.risks
    assert "Data validation evidence was required but not provided." in record.risks


def test_multi_agent_execution_service_should_list_records_with_filters() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=500.0,
        )
    )
    service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="regression_run",
            workflow_name="multi-agent-regression-v1",
            run_status="failed",
            duration_ms=300.0,
        )
    )

    response = service.list_records(
        workflow_name="multi-agent-regression-v1",
    )

    assert response.count == 1
    assert response.records[0].workflow_name == "multi-agent-regression-v1"
    assert response.records[0].run_status == "failed"
    assert response.metadata["total_stored_records"] == 2


def test_multi_agent_execution_service_should_summarize_stored_records() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=2000.0,
            agent_count=6,
            completed_agent_count=6,
            task_count=6,
            successful_task_count=6,
            artifact_count=6,
            expected_min_artifacts=6,
            handoff_count=5,
            failed_handoff_count=0,
            contract_check_count=6,
            passed_contract_check_count=6,
            final_report_section_count=6,
            expected_min_final_report_sections=6,
        )
    )
    service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=4000.0,
            agent_count=6,
            completed_agent_count=5,
            skipped_agent_count=1,
            task_count=6,
            successful_task_count=5,
            artifact_count=5,
            expected_min_artifacts=5,
            handoff_count=5,
            failed_handoff_count=1,
            max_failed_handoffs=1,
            contract_check_count=6,
            passed_contract_check_count=5,
            failed_contract_check_count=1,
            max_failed_contract_checks=1,
            final_report_section_count=5,
            expected_min_final_report_sections=5,
            retry_count=1,
            min_quality_score=0.7,
        )
    )

    response = service.summarize(AIMultiAgentExecutionSummaryRequest())

    assert response.record_count == 2
    assert response.passed_count == 1
    assert response.warning_count == 1
    assert response.failed_count == 0
    assert response.total_agents == 12
    assert response.total_completed_agents == 11
    assert response.total_failed_agents == 0
    assert response.total_skipped_agents == 1
    assert response.total_tasks == 12
    assert response.total_successful_tasks == 11
    assert response.total_failed_tasks == 0
    assert response.total_artifacts == 11
    assert response.total_handoffs == 10
    assert response.total_failed_handoffs == 1
    assert response.total_contract_checks == 12
    assert response.total_passed_contract_checks == 11
    assert response.total_failed_contract_checks == 1
    assert response.total_final_report_sections == 11
    assert response.total_retries == 1
    assert response.total_fallbacks == 0
    assert response.average_duration_ms == 3000.0
    assert response.average_agent_success_rate == 0.9166
    assert response.average_task_success_rate == 0.9166
    assert response.average_handoff_success_rate == 0.9
    assert response.average_contract_success_rate == 0.9166
    assert response.average_artifact_coverage_score == 1.0
    assert response.average_final_report_coverage_score == 1.0
    assert response.average_quality_score == 0.95
    assert response.workflow_coverage["multi-agent-qa-copilot-v1"] == 2
    assert response.operation_coverage["qa_copilot_run"] == 2
    assert response.run_status_coverage["completed"] == 2
    assert response.risks == [
        "1 multi-agent execution record(s) returned warning.",
    ]


def test_multi_agent_execution_service_should_summarize_request_records() -> None:
    service = AIMultiAgentExecutionTelemetryService()

    record = AIMultiAgentExecutionRecord(
        record_id="multi-agent-execution-record-001",
        component="multi_agent",
        operation="qa_copilot_run",
        workflow_name="multi-agent-qa-copilot-v1",
        run_status="completed",
        status="passed",
        duration_ms=1000.0,
        agent_count=1,
        completed_agent_count=1,
        failed_agent_count=0,
        skipped_agent_count=0,
        task_count=1,
        successful_task_count=1,
        failed_task_count=0,
        artifact_count=1,
        expected_min_artifacts=1,
        handoff_count=0,
        failed_handoff_count=0,
        contract_check_count=1,
        passed_contract_check_count=1,
        failed_contract_check_count=0,
        conflict_count=0,
        critical_conflict_count=0,
        failure_count=0,
        error_count=0,
        final_report_section_count=1,
        expected_min_final_report_sections=1,
        data_validation_evidence_count=0,
        require_data_validation_evidence=False,
        retry_count=0,
        fallback_count=0,
        agent_success_rate=1.0,
        task_success_rate=1.0,
        contract_success_rate=1.0,
        artifact_coverage_score=1.0,
        final_report_coverage_score=1.0,
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

    response = service.summarize(
        AIMultiAgentExecutionSummaryRequest(
            records=[
                record,
            ],
            metadata={
                "source": "request-summary-test",
            },
        )
    )

    assert response.record_count == 1
    assert response.passed_count == 1
    assert response.average_quality_score == 1.0
    assert response.metadata["source"] == "request-summary-test"


def test_multi_agent_execution_request_should_reject_blank_workflow_name() -> None:
    with pytest.raises(ValidationError):
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="   ",
            run_status="completed",
        )


def test_multi_agent_execution_request_should_reject_negative_agent_count() -> None:
    with pytest.raises(ValidationError):
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            agent_count=-1,
        )
