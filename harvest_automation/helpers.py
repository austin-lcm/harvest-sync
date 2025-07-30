# harvest_automation/helpers.py
import asyncio
import json
import logging
from datetime import date, datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from harvest_automation.harvest_client import HarvestClient

_TZ_ET = ZoneInfo("America/New_York")
_LOGGER = logging.getLogger(__name__)


def _default_span(tz: ZoneInfo = _TZ_ET) -> tuple[date, date]:
    """Return (most-recent Monday, today) in *tz*."""
    today = datetime.now(tz).date()
    monday = today - timedelta(days=today.weekday())  # Monday == 0
    return monday, today


async def _pull_entries(start: date, end: date) -> list[dict]:
    """Internal async fetch using existing HarvestClient."""
    client = HarvestClient()
    try:
        await client.verify_duration_mode()
        return await client.list_entries(start, end)
    finally:
        await client.close()


def fetch_entries_pretty(
    *,
    start: Optional[date] = None,
    end: Optional[date] = None,
    tz: ZoneInfo = _TZ_ET,
) -> str:
    """
    Return Harvest time-entries as nicely-formatted JSON.

    Defaults:
      • start → most-recent Monday (or today if today *is* Monday)  
      • end   → today at 23 : 59 : 59 in Eastern Time
    """
    # Resolve dates
    if start is None and end is None:
        start, end = _default_span(tz)
    else:
        start = start or _default_span(tz)[0]
        end = end or datetime.now(tz).date()

    _LOGGER.info("Harvest pull: %s → %s", start, end)

    # Fire the async call synchronously for CLI convenience
    entries = asyncio.run(_pull_entries(start, end))

    # Pretty-print and return
    return json.dumps(entries, indent=2, sort_keys=True, default=str)
