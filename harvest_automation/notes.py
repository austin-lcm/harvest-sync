from __future__ import annotations

from zoneinfo import ZoneInfo

from .config import load_config
from .models import EventBlock

_cfg = load_config()
_TZ = ZoneInfo(_cfg.timezone)
_MAX_LEN = 280


def build_note(block: EventBlock) -> str:
    """
    Build the Harvest “notes” field.  ⚠️ Ensure that your note_template in
    config.toml **no longer references `{participants}`.**
    """
    start = block.begin.astimezone(_TZ)
    end = block.end.astimezone(_TZ)

    note = _cfg.note_template.format(
        date=start.strftime(_cfg.date_format),
        start=start.strftime(_cfg.time_format),
        title=block.title,
        jira=block.jira_key,
        end=end.strftime(_cfg.time_format),
    )
    return note[:_MAX_LEN]


def note_key(note: str) -> str:
    *prefix, _ = note.rsplit(_cfg.key_separator, maxsplit=1)
    return _cfg.key_separator.join(prefix)
