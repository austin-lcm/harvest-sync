# harvest_automation/config.py
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Final

_CFG_PATH_ENV: Final[str] = "CONFIG_PATH"
# repo root = …/harvest-sync
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_ROOT_CFG:   Final[Path] = _REPO_ROOT / "config.toml"
_HOME_CFG:   Final[Path] = Path("~/.config/harvest_automation/config.toml").expanduser()


@dataclass(frozen=True, slots=True)
class Config:
    # Harvest
    harvest_token: str
    harvest_account: int

    # Calendar
    ics_url: str

    # Default mappings
    default_project: int
    default_task: int
    nonbill_project: int
    nonbill_task: int

    # Business rules
    default_jira: str
    clone_tag: str
    skip_keywords: tuple[str, ...]
    billable_keywords: tuple[str, ...]
    nonbill_keywords: tuple[str, ...]
    default_billable: bool

    # Note-building
    note_template: str
    date_format: str
    time_format: str
    key_separator: str

    # TZ
    timezone: str = "America/New_York"


def _discover_cfg_path() -> Path:
    """Return the first existing config.toml path in priority order."""
    explicit = os.getenv(_CFG_PATH_ENV)
    if explicit:
        return Path(explicit).expanduser()

    for candidate in (_ROOT_CFG, _HOME_CFG):
        if candidate.exists():
            return candidate

    # If nothing found, raise a clear error early.
    raise FileNotFoundError(
        "No config.toml found. "
        "Set CONFIG_PATH or create one at project-root or ~/.config/harvest_automation."
    )


def load_config() -> Config:
    cfg_path = _discover_cfg_path()
    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    return Config(**data)
