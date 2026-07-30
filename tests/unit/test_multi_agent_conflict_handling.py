from ai_api.multi_agent import (
    MultiAgentArtifact,
    MultiAgentConflictDetector,
    MultiAgentSharedState,
)


def test_multi_agent_conflict_detector_should_pass_when_no_conflicts_exist() -> None:
    detector = MultiAgentConflictDetector()

    shared_state = MultiAgentSharedState(
        objective="Validate QA workflow.",
        requirement_text="Como QA, preciso validar uma regra.",
        artifacts=[
            MultiAgentArtifact(
                name="requirement_analysis",
                produced_by="requirement_analyst_agent",
                content={
                    "summary": "Requirement understood.",
                },
            ),
            MultiAgentArtifact(
                name="functional_test_strategy",
                produced_by="functional_qa_agent",
                content={
                    "positive_scenarios": [],
                },
            ),
        ],
    )

    response = detector.detect(shared_state)

    assert response.status == "passed"
    assert response.conflict_count == 0
    assert response.warning_count == 0
    assert response.critical_count == 0


def test_multi_agent_conflict_detector_should_warn_for_duplicate_equivalent_artifacts() -> None:
    detector = MultiAgentConflictDetector()

    shared_state = MultiAgentSharedState(
        objective="Validate QA workflow.",
        requirement_text="Como QA, preciso validar uma regra.",
        artifacts=[
            MultiAgentArtifact(
                name="shared_summary",
                produced_by="requirement_analyst_agent",
                content={
                    "summary": "Same content.",
                },
            ),
            MultiAgentArtifact(
                name="shared_summary",
                produced_by="functional_qa_agent",
                content={
                    "summary": "Same content.",
                },
            ),
        ],
    )

    response = detector.detect(shared_state)

    assert response.status == "warning"
    assert response.conflict_count == 1
    assert response.warning_count == 1
    assert response.critical_count == 0
    assert response.conflicts[0].artifact_name == "shared_summary"
    assert response.conflicts[0].severity == "warning"


def test_multi_agent_conflict_detector_should_fail_for_conflicting_artifacts() -> None:
    detector = MultiAgentConflictDetector()

    shared_state = MultiAgentSharedState(
        objective="Validate QA workflow.",
        requirement_text="Como QA, preciso validar uma regra.",
        artifacts=[
            MultiAgentArtifact(
                name="requirement_analysis",
                produced_by="requirement_analyst_agent",
                content={
                    "summary": "Requirement is ready.",
                },
            ),
            MultiAgentArtifact(
                name="requirement_analysis",
                produced_by="functional_qa_agent",
                content={
                    "summary": "Requirement is not ready.",
                },
            ),
        ],
    )

    response = detector.detect(shared_state)

    assert response.status == "failed"
    assert response.conflict_count == 1
    assert response.warning_count == 0
    assert response.critical_count == 1
    assert response.conflicts[0].artifact_name == "requirement_analysis"
    assert response.conflicts[0].severity == "critical"
    assert "requirement_analyst_agent" in response.conflicts[0].involved_agents
    assert "functional_qa_agent" in response.conflicts[0].involved_agents
