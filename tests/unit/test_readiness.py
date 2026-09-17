from pathlib import Path

from fastapi.testclient import TestClient

from ai_api.config import Settings
from ai_api.main import app
from ai_api.readiness import evaluate_readiness, get_readiness_report


def test_ready_endpoint_should_report_local_fake_configuration(tmp_path: Path) -> None:
    app.dependency_overrides[get_readiness_report] = lambda: evaluate_readiness(
        lambda: Settings(_env_file=None, storage_base_dir=str(tmp_path))
    )
    try:
        response = TestClient(app).get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"settings": "ok", "provider": "ok", "storage": "ok"},
    }


def test_ready_endpoint_should_return_503_without_exposing_secrets(tmp_path: Path) -> None:
    secret = "never-return-this-secret"
    app.dependency_overrides[get_readiness_report] = lambda: evaluate_readiness(
        lambda: Settings(
            _env_file=None,
            storage_base_dir=str(tmp_path),
            llm_provider="openai",
            openai_api_key=secret,
            openai_model=None,
        )
    )
    try:
        response = TestClient(app).get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"settings": "ok", "provider": "failed", "storage": "ok"},
    }
    assert secret not in response.text


def test_readiness_should_fail_safely_when_settings_are_invalid() -> None:
    def invalid_settings() -> Settings:
        return Settings(_env_file=None, llm_provider="invalid")  # type: ignore[arg-type]

    report = evaluate_readiness(invalid_settings)

    assert report.model_dump() == {
        "status": "not_ready",
        "checks": {"settings": "failed", "provider": "skipped", "storage": "skipped"},
    }


def test_readiness_should_reject_missing_storage_root(tmp_path: Path) -> None:
    report = evaluate_readiness(
        lambda: Settings(_env_file=None, storage_base_dir=str(tmp_path / "missing"))
    )

    assert report.status == "not_ready"
    assert report.checks.storage == "failed"


def test_readiness_should_reject_missing_agent_log_directory(tmp_path: Path) -> None:
    report = evaluate_readiness(
        lambda: Settings(
            _env_file=None,
            storage_base_dir=str(tmp_path),
            agent_execution_log_path=str(tmp_path / "missing" / "agent-log.jsonl"),
        )
    )

    assert report.status == "not_ready"
    assert report.checks.storage == "failed"


def test_readiness_should_reject_incomplete_selected_provider(tmp_path: Path) -> None:
    secret = "never-return-this-secret"
    report = evaluate_readiness(
        lambda: Settings(
            _env_file=None,
            storage_base_dir=str(tmp_path),
            llm_provider="openai",
            openai_api_key=secret,
            openai_model=None,
        )
    )

    assert report.status == "not_ready"
    assert report.checks.provider == "failed"
    assert secret not in report.model_dump_json()


def test_readiness_should_allow_memory_storage_without_local_directory() -> None:
    report = evaluate_readiness(
        lambda: Settings(
            _env_file=None,
            storage_backend="memory",
            storage_base_dir="missing-directory",
        )
    )

    assert report.status == "ready"
    assert report.checks.storage == "skipped"


def test_readiness_should_not_require_ollama_network_availability() -> None:
    report = evaluate_readiness(
        lambda: Settings(
            _env_file=None,
            storage_backend="memory",
            llm_provider="ollama",
            ollama_base_url="http://unavailable.example.invalid:11434",
            ollama_model="local-model",
        )
    )

    assert report.status == "ready"
    assert report.checks.provider == "ok"
