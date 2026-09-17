import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ai_api.evals import CIEvaluationPipelineRunResponse, CIEvaluationPipelineStageResult
from ai_api.evals.artifacts import EvaluationArtifactService, get_evaluation_artifact_service
from ai_api.evals.dependencies import (
    get_ci_evaluation_pipeline_service,
    get_evaluation_telemetry_instrumentation_service,
)
from ai_api.main import app


def _response(secret: str = "private-prompt") -> CIEvaluationPipelineRunResponse:
    return CIEvaluationPipelineRunResponse(
        status="warning",
        score=0.75,
        stage_count=1,
        passed_count=0,
        warning_count=1,
        failed_count=0,
        should_fail_ci=True,
        stages=[
            CIEvaluationPipelineStageResult(
                name="prompt_regression",
                status="warning",
                score=0.75,
                summary=secret,
                output={"prompt": secret, "results": [{"raw": secret}]},
                metadata={"credential": secret},
            )
        ],
        metadata={"run_id": secret, "provider_url": secret},
    )


def test_artifacts_are_sanitized_atomic_and_persistent(tmp_path: Path) -> None:
    service = EvaluationArtifactService(tmp_path)
    artifact = service.save_pipeline(_response(), source="script")
    stored_files = list((tmp_path / "evaluation-artifacts").glob("*.json"))

    assert len(stored_files) == 1
    assert stored_files[0].name == f"{artifact.artifact_id}.json"
    assert not list((tmp_path / "evaluation-artifacts").glob("*.tmp"))
    assert "private-prompt" not in stored_files[0].read_text(encoding="utf-8")
    assert artifact.risks == ["prompt_regression returned warning."]
    assert artifact.recommendations == [
        "Review warning evaluation stages before promotion."
    ]
    assert EvaluationArtifactService(tmp_path).get(artifact.artifact_id) == artifact


def test_artifact_listing_latest_missing_and_id_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = EvaluationArtifactService(tmp_path)
    assert service.list_artifacts().model_dump() == {"artifacts": [], "total": 0}
    assert service.latest() is None
    assert service.get("0" * 32) is None

    monkeypatch.setattr("ai_api.evals.artifacts.time_ns", lambda: 1)
    first = service.save_pipeline(_response(), source="api")
    second = service.save_pipeline(_response(), source="script")
    listed = service.list_artifacts(limit=1)

    assert listed.total == 2
    assert [item.artifact_id for item in listed.artifacts] == [second.artifact_id]
    assert service.latest() == second
    assert service.get(first.artifact_id) == first
    with pytest.raises(ValueError, match="Invalid evaluation artifact ID"):
        service.get("../private")
    with pytest.raises(ValueError, match="Invalid evaluation artifact ID"):
        service.get("A" * 32)
    with pytest.raises(ValueError, match="limit"):
        service.list_artifacts(limit=0)


class _PipelineStub:
    def run(self, _request: object) -> CIEvaluationPipelineRunResponse:
        return _response()


class _InstrumentationStub:
    def instrument(self, **kwargs: object) -> CIEvaluationPipelineRunResponse:
        operation = kwargs["operation"]
        assert callable(operation)
        return operation()


def test_artifact_api_persists_pipeline_and_rejects_unsafe_ids(tmp_path: Path) -> None:
    service = EvaluationArtifactService(tmp_path)
    app.dependency_overrides[get_evaluation_artifact_service] = lambda: service
    app.dependency_overrides[get_ci_evaluation_pipeline_service] = _PipelineStub
    app.dependency_overrides[get_evaluation_telemetry_instrumentation_service] = (
        _InstrumentationStub
    )
    try:
        client = TestClient(app)
        assert client.get("/evals/artifacts").json() == {"artifacts": [], "total": 0}
        assert client.get("/evals/artifacts/latest").status_code == 404

        pipeline = client.post("/evals/ci/pipeline/run", json={})
        assert pipeline.status_code == 200
        assert pipeline.json()["status"] == "warning"

        listed = client.get("/evals/artifacts")
        assert listed.status_code == 200
        assert listed.json()["total"] == 1
        artifact_id = listed.json()["artifacts"][0]["artifact_id"]
        detail = client.get(f"/evals/artifacts/{artifact_id}")
        assert detail.status_code == 200
        assert detail.json()["source"] == "api"
        assert detail.json()["stages"][0] == {
            "name": "prompt_regression",
            "status": "warning",
            "score": 0.75,
        }
        assert client.get("/evals/artifacts/latest").json() == detail.json()
        assert client.get(f"/evals/artifacts/{'0' * 32}").status_code == 404
        assert client.get("/evals/artifacts/unsafe-id").status_code == 422
        assert client.get("/evals/artifacts/..%2Fprivate").status_code in {404, 422}
        assert client.get("/evals/artifacts?limit=0").status_code == 422
        assert "private-prompt" not in json.dumps(detail.json())
    finally:
        app.dependency_overrides.clear()


def test_pipeline_script_keeps_report_and_creates_safe_artifact(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    report_path = tmp_path / "pipeline-report.json"
    environment = os.environ.copy()
    environment["STORAGE_BASE_DIR"] = str(tmp_path)
    completed = subprocess.run(
        [
            sys.executable,
            str(project_root / "scripts" / "run_ai_evaluation_pipeline.py"),
            "--output",
            str(report_path),
            "--fail-on-warning",
        ],
        cwd=project_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert report_path.is_file()
    assert json.loads(report_path.read_text(encoding="utf-8"))["stage_count"] == 8
    artifact = EvaluationArtifactService(tmp_path).latest()
    assert artifact is not None
    assert artifact.source == "script"
    assert artifact.status == "passed"
    assert artifact.stage_count == 8
