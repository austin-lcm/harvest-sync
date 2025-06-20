from __future__ import annotations

import asyncio
from datetime import date as _date
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import typer

from .config import load_config
from .sync import sync

app = typer.Typer()
_cfg = load_config()
_TZ = ZoneInfo(_cfg.timezone)


def _most_recent_monday(today: _date) -> _date:
    """Mon = 0; subtract weekday to get Monday."""
    return today - timedelta(days=today.weekday())


def _default_range() -> tuple[_date, _date]:
    """Return (Monday_of_this_week, today)."""
    today_est = datetime.now(_TZ).date()
    return _most_recent_monday(today_est), today_est


@app.command()
def run(
    start_date: Optional[datetime] = typer.Option(
        None,
        "--start-date",
        help="Start date YYYY-MM-DD (defaults to most recent Monday)",
    ),
    end_date: Optional[datetime] = typer.Option(
        None,
        "--end-date",
        help="End date YYYY-MM-DD (defaults to today)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Log actions without writing to Harvest",
    ),
) -> None:
    """
    Synchronise calendar events to Harvest.
    Dates are parsed as datetime (ISO-8601); only the .date() part is used.
    """
    # Determine span as dates
    if start_date:
        start_date = start_date.date()
        end_date = (end_date or datetime.now(_TZ)).date()
    else:
        start_date, end_date = _default_range()

    typer.echo(f"Syncing {start_date} → {end_date}  (dry-run={dry_run})")
    asyncio.run(sync(start_date, end_date, dry_run=dry_run))


if __name__ == "__main__":
    app()
