from ai_api.evals import (
    AIAgentExecutionRecordRequest,
    AIAgentExecutionTelemetryService,
    AIMultiAgentExecutionRecordRequest,
    AIMultiAgentExecutionTelemetryService,
    AIObservabilityDashboardService,
    AIRetrievalQualityRecordRequest,
    AIRetrievalQualityTelemetryService,
    AIUsageRecordRequest,
    AIUsageTrackingService,
)


def test_observability_dashboard_should_return_empty_when_no_records_exist() -> None:
    dashboard_service = AIObservabilityDashboardService(
        usage_tracking_service=AIUsageTrackingService(),
        retrieval_quality_service=AIRetrievalQualityTelemetryService(),
        agent_execution_service=AIAgentExecutionTelemetryService(),
        multi_agent_execution_service=AIMultiAgentExecutionTelemetryService(),
    )

    dashboard = dashboard_service.get_dashboard()

    assert dashboard.status == "empty"
    assert len(dashboard.sections) == 4
    assert dashboard.metadata["dashboard_type"] == (
        "backend_observability_read_model"
    )
    assert dashboard.metadata["future_frontend"] == "AI Quality Command Center"

    assert [
        section.status
        for section in dashboard.sections
    ] == [
        "empty",
        "empty",
        "empty",
        "empty",
    ]

    assert (
        "Record representative observability events before using the dashboard as a release signal."
        in dashboard.recommendations
    )


def test_observability_dashboard_should_return_healthy_when_all_sections_are_healthy() -> None:
    usage_service = AIUsageTrackingService()
    retrieval_quality_service = AIRetrievalQualityTelemetryService()
    agent_execution_service = AIAgentExecutionTelemetryService()
    multi_agent_execution_service = AIMultiAgentExecutionTelemetryService()

    usage_service.record(
        AIUsageRecordRequest(
            provider="openai",
            model_name="test-model",
            component="llm",
            operation="requirement_analysis",
            prompt_tokens=1000,
            completion_tokens=500,
            input_cost_per_1k_tokens_usd=0.01,
            output_cost_per_1k_tokens_usd=0.03,
        )
    )
    retrieval_quality_service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Quando o boleto deve ser registrado?",
            retrieved_chunks_count=3,
            relevant_chunks_count=3,
            citation_count=2,
            unique_source_count=2,
            average_similarity_score=0.9,
            expected_min_citations=1,
        )
    )
    agent_execution_service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=1000.0,
            step_count=2,
            successful_step_count=2,
            tool_call_count=1,
            successful_tool_call_count=1,
        )
    )
    multi_agent_execution_service.record(
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

    dashboard_service = AIObservabilityDashboardService(
        usage_tracking_service=usage_service,
        retrieval_quality_service=retrieval_quality_service,
        agent_execution_service=agent_execution_service,
        multi_agent_execution_service=multi_agent_execution_service,
    )

    dashboard = dashboard_service.get_dashboard()

    assert dashboard.status == "healthy"
    assert len(dashboard.sections) == 4
    assert dashboard.global_risks == [
        "No global observability risks detected.",
    ]

    section_statuses = {
        section.name: section.status
        for section in dashboard.sections
    }

    assert section_statuses == {
        "usage": "healthy",
        "retrieval_quality": "healthy",
        "agent_execution": "healthy",
        "multi_agent_execution": "healthy",
    }


def test_observability_dashboard_should_return_warning_when_a_section_has_risk() -> None:
    usage_service = AIUsageTrackingService()
    retrieval_quality_service = AIRetrievalQualityTelemetryService()
    agent_execution_service = AIAgentExecutionTelemetryService()
    multi_agent_execution_service = AIMultiAgentExecutionTelemetryService()

    usage_service.record(
        AIUsageRecordRequest(
            provider="unknown",
            model_name="unknown-model",
            component="llm",
            operation="llm_call",
            prompt_tokens=100,
            completion_tokens=50,
        )
    )

    retrieval_quality_service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_answer",
            query="Query",
            retrieved_chunks_count=1,
            relevant_chunks_count=1,
            citation_count=1,
            average_similarity_score=0.8,
        )
    )

    agent_execution_service.record(
        AIAgentExecutionRecordRequest(
            component="agent",
            operation="qa_agent_run",
            agent_name="qa-agent-v1",
            run_status="completed",
            duration_ms=500.0,
            step_count=1,
            successful_step_count=1,
        )
    )

    multi_agent_execution_service.record(
        AIMultiAgentExecutionRecordRequest(
            component="multi_agent",
            operation="qa_copilot_run",
            workflow_name="multi-agent-qa-copilot-v1",
            run_status="completed",
            duration_ms=1000.0,
            agent_count=1,
            completed_agent_count=1,
            task_count=1,
            successful_task_count=1,
        )
    )

    dashboard_service = AIObservabilityDashboardService(
        usage_tracking_service=usage_service,
        retrieval_quality_service=retrieval_quality_service,
        agent_execution_service=agent_execution_service,
        multi_agent_execution_service=multi_agent_execution_service,
    )

    dashboard = dashboard_service.get_dashboard()

    assert dashboard.status == "warning"

    section_statuses = {
        section.name: section.status
        for section in dashboard.sections
    }

    assert section_statuses["usage"] == "warning"

    assert any(
        "usage record(s) do not have cost data" in risk
        for risk in dashboard.global_risks
    )


def test_observability_dashboard_should_return_critical_when_a_section_has_failures() -> None:
    retrieval_quality_service = AIRetrievalQualityTelemetryService()

    retrieval_quality_service.record(
        AIRetrievalQualityRecordRequest(
            component="rag",
            operation="rag_retrieve",
            query="Query",
            retrieved_chunks_count=0,
            expected_min_retrieved_chunks=1,
        )
    )

    dashboard_service = AIObservabilityDashboardService(
        retrieval_quality_service=retrieval_quality_service,
    )

    dashboard = dashboard_service.get_dashboard()

    assert dashboard.status == "critical"
    assert dashboard.sections[0].name == "retrieval_quality"
    assert dashboard.sections[0].status == "critical"
    assert any(
        "Retrieval quality metrics: 1 retrieval quality record(s) failed." in risk
        for risk in dashboard.global_risks
    )


def test_observability_dashboard_should_mark_section_as_critical_when_summary_fails() -> None:
    class BrokenSummaryService:
        def summarize(self, request: object) -> object:
            raise RuntimeError("summary failed")

    dashboard_service = AIObservabilityDashboardService(
        usage_tracking_service=BrokenSummaryService(),
    )

    dashboard = dashboard_service.get_dashboard()

    assert dashboard.status == "critical"
    assert dashboard.sections[0].name == "usage"
    assert dashboard.sections[0].status == "critical"
    assert "summary failed" in dashboard.sections[0].risks[0]
