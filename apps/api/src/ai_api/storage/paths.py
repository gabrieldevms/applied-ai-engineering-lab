from pathlib import Path
from ai_api.config import Settings


def get_storage_base_dir(settings: Settings) -> Path:
    return Path(settings.storage_base_dir)


def resolve_storage_path(
    settings: Settings,
    relative_path: str | Path,
) -> Path:
    path = Path(relative_path)

    if path.is_absolute():
        return path

    return get_storage_base_dir(settings) / path


def ensure_parent_dir(path: str | Path) -> Path:
    normalized_path = Path(path)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)

    return normalized_path
