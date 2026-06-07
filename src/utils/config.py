from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_config(env: str = "dev", config_dir: Path | None = None) -> dict[str, Any]:
    directory = config_dir or PROJECT_ROOT / "configs"
    config_path = directory / f"{env}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    return config


def resolve_project_path(path: str | Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)
    return str(PROJECT_ROOT / candidate)


def resolve_paths(config: dict[str, Any]) -> dict[str, str]:
    return {
        name: resolve_project_path(path)
        for name, path in config.get("paths", {}).items()
    }
