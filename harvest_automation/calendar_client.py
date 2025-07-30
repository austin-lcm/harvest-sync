import re
from collections import defaultdict
from datetime import datetime
from typing import Iterable
from zoneinfo import ZoneInfo

import httpx
from icalendar import Calendar
from recurring_ical_events import (
    of as rrule_of,
)

from .classify import is_billable
from .config import load_config
from .models import EventBlock

_cfg = load_config()
_TZ  = ZoneInfo(_cfg.timezone)
_JIRA_RE = re.compile(r"\b[A-Z]{2,}-\d+\b")
_CLONE_LOWER = _cfg.clone_tag.lower()
_SKIP_LOWER = tuple(kw.lower() for kw in _cfg.skip_keywords)
_BILL_LOWER = tuple(kw.lower() for kw in _cfg.billable_keywords)
_NONBILL_LOWER = tuple(kw.lower() for kw in _cfg.nonbill_keywords)
_DEFAULT_BILL  = _cfg.default_billable

async def _download(url: str) -> str:
    async with httpx.AsyncClient(timeout=10) as cli:
        res = await cli.get(url)
        res.raise_for_status()
        return res.text


def _extract_jira(title: str) -> str:
    m = _JIRA_RE.search(title)
    return m.group(0) if m else _cfg.default_jira


def _normalise(dtobj: datetime) -> datetime:
    if dtobj.tzinfo is None:
        return dtobj.replace(tzinfo=_TZ)
    return dtobj.astimezone(_TZ)


def _build_block(ev, billable: bool) -> EventBlock:
    """Create an EventBlock from a raw VEVENT."""
    return EventBlock(
        begin=_normalise(ev.decoded("dtstart")),
        end=_normalise(ev.decoded("dtend")),
        title=(ev.get("SUMMARY") or "").strip(),
        jira_key=_extract_jira(ev.get("SUMMARY") or ""),
        billable=billable,
    )


def _dedupe_clones(blocks: Iterable[EventBlock]) -> list[EventBlock]:
    grouped: dict[tuple, list[EventBlock]] = defaultdict(list)
    for blk in blocks:
        key = (
            blk.begin.date(),
            blk.begin.time(),
            blk.end.time(),
            blk.title.lower().replace(_CLONE_LOWER, "").strip(),
        )
        grouped[key].append(blk)

    deduped: list[EventBlock] = []
    for group in grouped.values():
        group.sort(key=lambda b: _CLONE_LOWER in b.title.lower())
        deduped.append(group[0])
    return deduped


async def fetch_events(
    start: datetime,
    end: datetime,
    *,
    ics_url: str | None = None,
) -> list[EventBlock]:
    """Return EventBlocks within [start, end] - already de-duplicated."""
    raw_ics = await _download(ics_url or _cfg.ics_url)
    cal = Calendar.from_ical(raw_ics)

    blocks = []
    for ev in rrule_of(cal).between(start, end):
        title_l = (ev.get("SUMMARY") or "").strip().lower()

        if any(sk in title_l for sk in _SKIP_LOWER):
            continue

        billable = is_billable(title_l, _BILL_LOWER, _NONBILL_LOWER, _DEFAULT_BILL)
        blocks.append(_build_block(ev, billable))

    return _dedupe_clones(blocks)