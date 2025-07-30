from datetime import date
from typing import Any

import httpx

from .config import load_config

_cfg = load_config()
_BASE = "https://api.harvestapp.com/v2"

_HEADERS = {
    "Authorization": f"Bearer {_cfg.harvest_token}",
    "Harvest-Account-Id": str(_cfg.harvest_account),
    "User-Agent": "harvest_automation/0.3",
    "Content-Type": "application/json",
}


class HarvestClient:
    def __init__(self) -> None:
        self._cli = httpx.AsyncClient(headers=_HEADERS, timeout=20)

    async def close(self) -> None:
        await self._cli.aclose()

    async def verify_duration_mode(self) -> None:
        r = await self._cli.get(f"{_BASE}/company")
        r.raise_for_status()
        if r.json().get("wants_timestamp_timers", True):
            raise RuntimeError(
                "Harvest account is configured for start/end timers."
            )

    async def list_entries(self, start: date, end: date) ->  list[dict[str, Any]]:
        url = f"{_BASE}/time_entries"
        params: dict[str, Any] = {"from": str(start), "to": str(end), "per_page": 2000}
        entries: list[dict[str, Any]] = []

        while url:
            r = await self._cli.get(url, params=params)
            r.raise_for_status()
            payload = r.json()
            entries.extend(payload["time_entries"])
            url = payload["links"]["next"]
            params = None  # params only on first request
        return entries

    async def create_entry(self, payload: dict[str, Any]) -> None:
        r = await self._cli.post(f"{_BASE}/time_entries", json=payload)
        r.raise_for_status()

    async def patch_hours(self, entry_id: int, hours: float) -> None:
        r = await self._cli.patch(
            f"{_BASE}/time_entries/{entry_id}", json={"hours": hours}
        )
        r.raise_for_status()
