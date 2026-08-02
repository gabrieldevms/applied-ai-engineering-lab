from ai_api.evals.agent_execution_metrics import AIAgentExecutionTelemetryService
from ai_api.evals.execution_history import AIExecutionHistoryService
from ai_api.evals.multi_agent_execution_metrics import (
    AIMultiAgentExecutionTelemetryService,
)
from ai_api.evals.retrieval_quality import AIRetrievalQualityTelemetryService
from ai_api.evals.schemas import (
    AIAgentExecutionRecordRequest,
    AIMultiAgentExecutionRecordRequest,
    AIRetrievalQualityRecordRequest,
    AIUsageRecordRequest,
    EvaluationTelemetryRecordRequest,
)
from ai_api.evals.telemetry import EvaluationTelemetryService
from ai_api.evals.usage_tracking import AIUsageTrackingService


def test_execution_history_service_should_consolidate_observability_records() -> None:
    evaluation_service = EvaluationTelemetryService()
    usage_service = AIUsageTrackingService()
    retrieval_service = AIRetrievalQualityTelemetryService()
    agent_service = AIAgentExecutionTelemetryService()
    multi_agent_service = AIMultiAgentExecutionTelemetryService()

    evaluation_service.record(
        EvaluationTelemetryRecordRequest(
            event_type="golden_dataset_run",
            component="evaluation",
            status="completed",
            source="unit-test",
            duration_ms=100.0,
            score=1.0,
            run_id="run-001",
        )
    )
    usage_service.record(
        AIUsageRecordRequest(
            provider="fake",
            model_name="fake-llm-v1",
            component="llm",
            operation="requirement_analysis",
            prompt_tokens=100,
            completion_tokens=50,
            run_id="run-001",
        )
    )
    retrieval_service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Query",
            retrieved_chunks_count=2,
            relevant_chunks_count=2,
            citation_count=1,
            unique_source_count=1,
            average_similarity_score=0.9,
            run_id="run-001",
        )
    )
    agent_service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=500.0,
            step_count=2,
            successful_step_count=2,
            tool_call_count=1,
            successful_tool_call_count=1,
            run_id="run-001",
        )
    )
    multi_agent_service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=1000.0,
            agent_count=2,
            completed_agent_count=2,
            task_count=2,
            successful_task_count=2,
            artifact_count=2,
            expected_min_artifacts=2,
            final_report_section_count=2,
            expected_min_final_report_sections=2,
            run_id="run-001",
        )
    )

    service = AIExecutionHistoryService(
        evaluation_telemetry_service=evaluation_service,
        usage_tracking_service=usage_service,
        retrieval_quality_service=retrieval_service,
        agent_execution_service=agent_service,
        multi_agent_execution_service=multi_agent_service,
    )

    response = service.list_history(limit=10)

    execution_types = {
        record.execution_type
        for record in response.records
    }

    assert response.count == 5
    assert execution_types == {
        "evaluation_telemetry",
        "usage",
        "retrieval_quality",
        "agent_execution",
        "multi_agent_execution",
    }
    assert response.metadata["history_mode"] == "observability_read_model"


def test_execution_history_service_should_filter_by_execution_type() -> None:
    agent_service = AIAgentExecutionTelemetryService()
    multi_agent_service = AIMultiAgentExecutionTelemetryService()

    agent_service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            run_id="agent-run-001",
        )
    )
    multi_agent_service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            run_id="multi-agent-run-001",
        )
    )

    service = AIExecutionHistoryService(
        agent_execution_service=agent_service,
        multi_agent_execution_service=multi_agent_service,
    )

    response = service.list_history(
        execution_type="agent_execution",
        limit=10,
    )

    assert response.count == 1
    assert response.records[0].execution_type == "agent_execution"
    assert response.records[0].run_id == "agent-run-001"


def test_execution_history_service_should_filter_by_status_component_and_run_id() -> None:
    agent_service = AIAgentExecutionTelemetryService()

    agent_service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            run_id="agent-run-001",
        )
    )
    agent_service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="data_agent_run",
            agent_name="data-analyst-agent-v1",
            run_status="failed",
            run_id="agent-run-002",
        )
    )

    service = AIExecutionHistoryService(
        agent_execution_service=agent_service,
    )

    response = service.list_history(
        status="failed",
        component="agent",
        run_id="agent-run-002",
        limit=10,
    )

    assert response.count == 1
    assert response.records[0].status == "failed"
    assert response.records[0].component == "agent"
    assert response.records[0].run_id == "agent-run-002"


def test_execution_history_service_should_apply_limit() -> None:
    usage_service = AIUsageTrackingService()

    usage_service.record(
        AIUsageRecordRequest(
            provider="fake",
            model_name="fake-llm-v1",
            component="llm",
            operation="operation_1",
            prompt_tokens=10,
        )
    )
    usage_service.record(
        AIUsageRecordRequest(
            provider="fake",
            model_name="fake-llm-v1",
            component="llm",
            operation="operation_2",
            prompt_tokens=20,
        )
    )

    service = AIExecutionHistoryService(
        usage_tracking_service=usage_service,
    )

    response = service.list_history(limit=1)

    assert response.count == 1
    assert response.metadata["total_filtered_records"] == 2


def test_execution_history_service_should_reject_invalid_limit() -> None:
    service = AIExecutionHistoryService()

    try:
        service.list_history(limit=0)
    except ValueError as error:
        assert str(error) == "limit must be greater than zero"
    else:
        raise AssertionError("Expected ValueError")
