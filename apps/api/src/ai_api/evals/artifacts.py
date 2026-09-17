"""Safe, persistent summaries of completed deterministic evaluation runs."""

import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from time import time_ns
from typing import Literal
from uuid import uuid4

from fastapi import Depends
from pydantic import BaseModel, Field

from ai_api.config import Settings, get_settings
from ai_api.evals.schemas import (
    CIEvaluationPipelineRunResponse,
    CIEvaluationPipelineStageName,
    CIEvaluationPipelineStatus,
)


ArtifactSource = Literal["api", "script"]
ARTIFACT_ID_PATTERN = re.compile(r"[0-9a-f]{32}\Z")
_artifact_id_lock = Lock()
_last_artifact_timestamp_ns = 0


def _new_artifact_id() -> tuple[str, datetime]:
    global _last_artifact_timestamp_ns
    with _artifact_id_lock:
        timestamp_ns = max(time_ns(), _last_artifact_timestamp_ns + 1)
        _last_artifact_timestamp_ns = timestamp_ns
    artifact_id = f"{timestamp_ns:016x}{uuid4().hex[:16]}"
    created_at = datetime.fromtimestamp(timestamp_ns / 1_000_000_000, UTC)
    return artifact_id, created_at


class EvaluationArtifactStage(BaseModel):
    name: CIEvaluationPipelineStageName
    status: CIEvaluationPipelineStatus
    score: float | None = Field(default=None, ge=0.0, le=1.0)


class EvaluationArtifactSummary(BaseModel):
    artifact_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    created_at: datetime
    source: ArtifactSource
    status: CIEvaluationPipelineStatus
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    stage_count: int = Field(ge=0)
    passed_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)


class EvaluationArtifact(EvaluationArtifactSummary):
    should_fail_ci: bool
    stages: list[EvaluationArtifactStage]
    risks: list[str]
    recommendations: list[str]


class EvaluationArtifactList(BaseModel):
    artifacts: list[EvaluationArtifactSummary]
    total: int = Field(ge=0)


class EvaluationArtifactService:
    def __init__(self, storage_base_dir: str | Path) -> None:
        self.directory = Path(storage_base_dir) / "evaluation-artifacts"

    def save_pipeline(
        self,
        response: CIEvaluationPipelineRunResponse,
        source: ArtifactSource,
    ) -> EvaluationArtifact:
        artifact_id, created_at = _new_artifact_id()
        artifact = EvaluationArtifact(
            artifact_id=artifact_id,
            created_at=created_at,
            source=source,
            status=response.status,
            score=response.score,
            stage_count=response.stage_count,
            passed_count=response.passed_count,
            warning_count=response.warning_count,
            failed_count=response.failed_count,
            should_fail_ci=response.should_fail_ci,
            stages=[
                EvaluationArtifactStage(
                    name=stage.name,
                    status=stage.status,
                    score=stage.score,
                )
                for stage in response.stages
            ],
            risks=[
                f"{stage.name} returned {stage.status}."
                for stage in response.stages
                if stage.status in {"warning", "failed"}
            ],
            recommendations=(
                ["Review failed evaluation stages before promotion."]
                if response.failed_count
                else ["Review warning evaluation stages before promotion."]
                if response.warning_count
                else []
            ),
        )

        self.directory.mkdir(parents=True, exist_ok=True)
        destination = self.directory / f"{artifact.artifact_id}.json"
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.directory,
                prefix=".artifact-",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(artifact.model_dump_json(indent=2))
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, destination)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        return artifact

    def get(self, artifact_id: str) -> EvaluationArtifact | None:
        if ARTIFACT_ID_PATTERN.fullmatch(artifact_id) is None:
            raise ValueError("Invalid evaluation artifact ID.")
        path = self.directory / f"{artifact_id}.json"
        if not path.is_file():
            return None
        return EvaluationArtifact.model_validate_json(path.read_text(encoding="utf-8"))

    def list_artifacts(self, limit: int = 20) -> EvaluationArtifactList:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        if not self.directory.is_dir():
            return EvaluationArtifactList(artifacts=[], total=0)
        artifacts = [
            EvaluationArtifact.model_validate_json(path.read_text(encoding="utf-8"))
            for path in self.directory.glob("[0-9a-f]" * 32 + ".json")
        ]
        artifacts.sort(key=lambda item: item.artifact_id, reverse=True)
        return EvaluationArtifactList(
            artifacts=[
                EvaluationArtifactSummary.model_validate(item)
                for item in artifacts[:limit]
            ],
            total=len(artifacts),
        )

    def latest(self) -> EvaluationArtifact | None:
        items = self.list_artifacts(limit=1).artifacts
        return self.get(items[0].artifact_id) if items else None


def get_evaluation_artifact_service(
    settings: Settings = Depends(get_settings),
) -> EvaluationArtifactService:
    return EvaluationArtifactService(settings.storage_base_dir)
