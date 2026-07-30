import json
from collections import defaultdict
from ai_api.multi_agent.schemas import (
    MultiAgentArtifact,
    MultiAgentConflictAnalysisResponse,
    MultiAgentConflictRecord,
    MultiAgentSharedState,
)


class MultiAgentConflictDetector:
    def detect(
        self,
        shared_state: MultiAgentSharedState,
    ) -> MultiAgentConflictAnalysisResponse:
        conflicts = self._detect_duplicate_artifact_conflicts(
            artifacts=shared_state.artifacts,
        )

        warning_count = len(
            [
                conflict
                for conflict in conflicts
                if conflict.severity == "warning"
            ]
        )
        critical_count = len(
            [
                conflict
                for conflict in conflicts
                if conflict.severity == "critical"
            ]
        )

        if critical_count > 0:
            status = "failed"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "passed"

        return MultiAgentConflictAnalysisResponse(
            status=status,
            conflict_count=len(conflicts),
            warning_count=warning_count,
            critical_count=critical_count,
            conflicts=conflicts,
            metadata={
                "detector": "multi-agent-conflict-detector-v1",
            },
        )

    def _detect_duplicate_artifact_conflicts(
        self,
        artifacts: list[MultiAgentArtifact],
    ) -> list[MultiAgentConflictRecord]:
        artifacts_by_name: dict[str, list[MultiAgentArtifact]] = defaultdict(list)

        for artifact in artifacts:
            artifacts_by_name[artifact.name].append(artifact)

        conflicts: list[MultiAgentConflictRecord] = []

        for artifact_name, artifact_group in artifacts_by_name.items():
            if len(artifact_group) <= 1:
                continue

            involved_agents = sorted(
                {
                    artifact.produced_by
                    for artifact in artifact_group
                }
            )
            serialized_contents = {
                json.dumps(
                    artifact.content,
                    sort_keys=True,
                    default=str,
                    ensure_ascii=False,
                )
                for artifact in artifact_group
            }

            if len(serialized_contents) > 1:
                severity = "critical"
                summary = (
                    "Conflicting artifacts with the same name were produced "
                    "with different content."
                )
            else:
                severity = "warning"
                summary = (
                    "Duplicate artifacts with the same name were produced, "
                    "but their content is equivalent."
                )

            conflicts.append(
                MultiAgentConflictRecord(
                    conflict_type="duplicate_artifact_name",
                    severity=severity,
                    artifact_name=artifact_name,
                    involved_agents=involved_agents,
                    summary=summary,
                    metadata={
                        "artifact_count": len(artifact_group),
                    },
                )
            )

        return conflicts
