"""Daily background refresh of FDA shortage data.

Pages never call openFDA while a patient waits: they read the newest saved result from the database
(tools.shortage_from_db). This thread refreshes that saved result at most once a day. If openFDA is down,
the last saved result (or the snapshot that ships in data/) stays in place.
"""

import json
import threading
import time
from datetime import datetime, timedelta, timezone

import httpx

from backend import tools

REFRESH_EVERY = timedelta(hours=24)
CHECK_EVERY_SECONDS = 3600
_started = False


def last_refresh() -> datetime | None:
    """Oldest saved openFDA result across our drugs (None if any drug was never refreshed)."""
    rows = tools._rows("SELECT d.id, c.fetched_at FROM drugs d LEFT JOIN shortage_cache c ON c.drug_id = d.id")
    if not rows or any(r["fetched_at"] is None for r in rows):
        return None
    return min(datetime.fromisoformat(r["fetched_at"]) for r in rows)


def refresh_if_due() -> str:
    """Refresh every drug from openFDA if the saved data is more than a day old. Returns what happened."""
    last = last_refresh()
    if last is not None and datetime.now(timezone.utc) - last < REFRESH_EVERY:
        return f"fresh (last refresh {last.isoformat(timespec='minutes')})"
    done = 0
    with httpx.Client(timeout=30) as client:
        for drug in tools._rows("SELECT * FROM drugs"):
            try:
                result = tools.fetch_fda_shortage(drug, client)
            except httpx.HTTPError:
                return f"openFDA unavailable after {done} drugs; kept the saved data"
            with tools._connect() as con:
                con.execute("INSERT OR REPLACE INTO shortage_cache (drug_id, fetched_at, result_json) VALUES (?, ?, ?)",
                            (drug["id"], result["checked_at"], json.dumps(result)))
                con.commit()
            done += 1
            time.sleep(0.3)  # gentle on the free API
    return f"refreshed {done} drugs"


def _loop() -> None:
    while True:
        try:
            refresh_if_due()
        except Exception:  # noqa: BLE001 - a failed refresh must never stop the app
            pass
        time.sleep(CHECK_EVERY_SECONDS)


def start() -> None:
    """Start the background thread once (daemon: it stops with the app)."""
    global _started
    if not _started:
        _started = True
        threading.Thread(target=_loop, name="fda-shortage-refresh", daemon=True).start()
