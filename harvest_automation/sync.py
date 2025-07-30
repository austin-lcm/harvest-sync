import logging
from datetime import date, datetime
from zoneinfo import ZoneInfo

from .calendar_client import fetch_events
from .config import load_config
from .harvest_client import HarvestClient
from .models import EventBlock
from .notes import build_note, note_key
from .overlap import split_overlaps

# ────────────────────────── logger ───────────────────────────
logger = logging.getLogger("harvest_automation.sync")
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)-5s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

_cfg = load_config()
_TZ = ZoneInfo(_cfg.timezone)

# ────────────────────────── helpers ──────────────────────────
async def _fetch_existing_entries(
    hc: HarvestClient,
    start: date,
    end: date,
) -> tuple[set[tuple[str, str]], dict[tuple[str, str], dict]]:
    """Return (approved_keys, editable_rows) from Harvest in one pass."""
    rows = await hc.list_entries(start, end)
    approved = {
        (row["spent_date"], note_key(row["notes"]))
        for row in rows
        if row.get("approval_status") == "approved"
    }
    editable = {
        (row["spent_date"], note_key(row["notes"])): row
        for row in rows
        if row.get("approval_status") != "approved"
    }
    logger.info(
        "Fetched %d Harvest rows (%d approved, %d editable)",
        len(rows),
        len(approved),
        len(editable),
    )
    return approved, editable


async def _collect_calendar_blocks(
    start: date,
    end: date,
) -> list[EventBlock]:
    """Return cleaned calendar blocks inside the EST window [start, end]."""
    start_dt = datetime.combine(start, datetime.min.time(), _TZ)
    end_dt = datetime.combine(end, datetime.max.time(), _TZ)
    raw_blocks = await fetch_events(start_dt, end_dt)
    blocks = split_overlaps(raw_blocks)
    logger.info("%d calendar events after de-overlap", len(blocks))
    return blocks


def _hours_between(blk: EventBlock) -> float:
    """Return duration of the event in hours (rounded 2 dp)."""
    return round((blk.end - blk.begin).total_seconds() / 3600, 2)


async def _post_or_patch(
    hc: HarvestClient,
    payload: dict,
    existing_row: dict | None,
    dry_run: bool,
) -> None:
    """Create or update a Harvest entry."""
    if existing_row is None:
        if dry_run:
            logger.info("  → [dry-run] WOULD POST: %s", payload)
        else:
            logger.info("  → POSTing new entry")
            await hc.create_entry(payload)
        return

    delta = abs(existing_row["hours"] - payload["hours"])
    if delta < 0.05:
        logger.info("  → No change; hours already %.2f", existing_row["hours"])
        return

    if dry_run:
        logger.info(
            "  → [dry-run] WOULD PATCH id=%s: %.2f → %.2f",
            existing_row["id"],
            existing_row["hours"],
            payload["hours"],
        )
    else:
        logger.info(
            "  → PATCH id=%s: %.2f → %.2f",
            existing_row["id"],
            existing_row["hours"],
            payload["hours"],
        )
        await hc.patch_hours(existing_row["id"], payload["hours"])


async def _handle_block(
    blk: EventBlock,
    approved: set[tuple[str, str]],
    editable: dict[tuple[str, str], dict],
    hc: HarvestClient,
    dry_run: bool,
) -> None:
    """Process one EventBlock: skip, post, or patch."""
    if not blk.billable:
        logger.info("Skipping non-billable: %s", blk.title)
        return

    note = build_note(blk)
    key = (blk.begin.date().isoformat(), note_key(note))

    logger.info(
        "Event: %s | %s → %s | jira=%s | key=%s",
        blk.title,
        blk.begin.astimezone(_TZ).strftime(_cfg.time_format),
        blk.end.astimezone(_TZ).strftime(_cfg.time_format),
        blk.jira_key,
        key,
    )

    if key in approved:
        logger.info("  → Already approved; skipping")
        return

    payload = {
        "project_id": _cfg.default_project,
        "task_id": _cfg.default_task,
        "spent_date": key[0],
        "hours": _hours_between(blk),
        "notes": note,
    }
    await _post_or_patch(hc, payload, editable.get(key), dry_run)


# ─────────────────────────── sync ────────────────────────────
async def sync(
    start: date,
    end: date,
    *,
    dry_run: bool = False,
) -> None:
    """Main orchestration entry-point."""
    logger.info("Sync: %s → %s  (dry-run=%s)", start, end, dry_run)
    hc = HarvestClient()
    try:
        await hc.verify_duration_mode()
        approved, editable = await _fetch_existing_entries(hc, start, end)
        blocks = await _collect_calendar_blocks(start, end)

        for blk in blocks:
            await _handle_block(blk, approved, editable, hc, dry_run)
    finally:
        await hc.close()
        logger.info("Sync complete ✅")
