from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class EventBlock:
    begin: datetime          # tz-aware
    end: datetime
    title: str
    jira_key: str
    billable: bool


@dataclass(slots=True, frozen=True)
class TimeEntry:
    id: int | None
    spent_date: str            # YYYY-MM-DD
    hours: float
    notes: str
    approval_status: str | None = None
