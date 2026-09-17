from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryFile
from typing import Literal

from pydantic import BaseModel, ValidationError

from ai_api.config import Settings, get_settings
from ai_api.llm import get_llm_health_status


CheckStatus = Literal["ok", "failed", "skipped"]


class ReadinessChecks(BaseModel):
    settings: CheckStatus
    provider: CheckStatus
    storage: CheckStatus


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    checks: ReadinessChecks


def get_readiness_report() -> ReadinessResponse:
    return evaluate_readiness()


def evaluate_readiness(
    settings_loader: Callable[[], Settings] = get_settings,
) -> ReadinessResponse:
    try:
        settings = settings_loader()
    except (ValidationError, OSError):
        return ReadinessResponse(
            status="not_ready",
            checks=ReadinessChecks(
                settings="failed", provider="skipped", storage="skipped"
            ),
        )

    provider_status: CheckStatus = (
        "ok" if get_llm_health_status(settings).configured else "failed"
    )
    storage_status: CheckStatus = (
        "skipped"
        if settings.storage_backend == "memory"
        else "ok" if _storage_paths_are_writable(settings) else "failed"
    )

    return ReadinessResponse(
        status=(
            "ready"
            if provider_status == "ok" and storage_status in {"ok", "skipped"}
            else "not_ready"
        ),
        checks=ReadinessChecks(
            settings="ok", provider=provider_status, storage=storage_status
        ),
    )


def _storage_paths_are_writable(settings: Settings) -> bool:
    try:
        for directory in (
            Path(settings.storage_base_dir),
            Path(settings.agent_execution_log_path).parent,
        ):
            if not directory.is_dir():
                return False
            with TemporaryFile(dir=directory):
                pass
    except (OSError, ValueError):
        return False

    return True
