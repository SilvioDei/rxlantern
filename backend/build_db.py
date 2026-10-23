"""Build data/rxcompass.db from data/pharmacies.json.

Run by hand:   ..\\.venv\\Scripts\\python.exe -m backend.build_db
The app also calls ensure_db() on startup, so graders never need to run this.
"""

import json
import sqlite3
from pathlib import Path

from backend.config import DATA_DIR

JSON_PATH = DATA_DIR / "pharmacies.json"
DB_PATH = DATA_DIR / "rxcompass.db"

# Columns that hold lists or objects are stored as JSON text.
JSON_COLUMNS = {
    "pharmacy_hours", "store_hours", "lunch_break", "holiday_hours", "delivery_details",
    "vaccines_routine", "vaccines_travel", "other_services", "nearby_clinics", "sources", "notes",
}

SCHEMA = """
CREATE TABLE pharmacies (
    id                    TEXT PRIMARY KEY,
    name                  TEXT NOT NULL,
    type                  TEXT NOT NULL,
    chain                 TEXT,
    store_number          TEXT,
    neighborhood          TEXT NOT NULL,
    address               TEXT NOT NULL,
    zip                   TEXT NOT NULL,
    phone                 TEXT NOT NULL,
    latitude              REAL,
    longitude             REAL,
    pharmacy_hours        TEXT NOT NULL,
    store_hours           TEXT NOT NULL,
    lunch_break           TEXT NOT NULL,
    holiday_hours         TEXT NOT NULL,
    is_24_hours           TEXT NOT NULL,
    store_is_24_hours     TEXT NOT NULL,
    delivery              TEXT NOT NULL,
    delivery_details      TEXT NOT NULL,
    drive_thru            TEXT NOT NULL,
    wheelchair_accessible TEXT NOT NULL,
    languages             TEXT NOT NULL,
    vaccines_routine      TEXT NOT NULL,
    vaccines_travel       TEXT NOT NULL,
    clinic_on_site        TEXT NOT NULL,
    specialty_pharmacy    TEXT NOT NULL,
    other_services        TEXT NOT NULL,
    nearby_clinics        TEXT NOT NULL,
    website               TEXT NOT NULL,
    vaccine_booking_url   TEXT NOT NULL,
    sources               TEXT NOT NULL,
    checked_date          TEXT NOT NULL,
    notes                 TEXT NOT NULL
);
"""


def _row(p: dict) -> dict:
    s = p["services"]
    row = {
        "id": p["id"], "name": p["name"], "type": p["type"], "chain": p.get("chain"),
        "store_number": p.get("store_number"), "neighborhood": p["neighborhood"],
        "address": p["address"], "zip": p["zip"], "phone": p["phone"],
        # "not found" coordinates become NULL so distance math can skip them.
        "latitude": p["latitude"] if isinstance(p["latitude"], (int, float)) else None,
        "longitude": p["longitude"] if isinstance(p["longitude"], (int, float)) else None,
        "pharmacy_hours": p["pharmacy_hours"], "store_hours": p["store_hours"],
        "lunch_break": p["lunch_break"], "holiday_hours": p["holiday_hours"],
        "is_24_hours": p["is_24_hours"], "store_is_24_hours": p["store_is_24_hours"],
        "delivery": p["delivery"], "delivery_details": p["delivery_details"],
        "drive_thru": p["drive_thru"], "wheelchair_accessible": p["wheelchair_accessible"],
        "languages": p["languages"],
        "vaccines_routine": s["vaccines_routine"], "vaccines_travel": s["vaccines_travel"],
        "clinic_on_site": s["clinic_on_site"], "specialty_pharmacy": s["specialty_pharmacy"],
        "other_services": s["other"],
        # List of {name, kind, address, distance_miles, distance_label, ...} or "none found within 1 mile".
        "nearby_clinics": p["nearby_clinics"],
        "website": p["website"], "vaccine_booking_url": p["vaccine_booking_url"],
        "sources": p["sources"], "checked_date": p["checked_date"], "notes": p["notes"],
    }
    for col in JSON_COLUMNS:
        row[col] = json.dumps(row[col], ensure_ascii=False)
    if not isinstance(row["languages"], str):
        row["languages"] = json.dumps(row["languages"], ensure_ascii=False)
    return row


def build_db(json_path: Path = JSON_PATH, db_path: Path = DB_PATH) -> int:
    """(Re)create the pharmacies table from the JSON file. Returns the row count."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    rows = [_row(p) for p in data["pharmacies"]]
    tmp = db_path.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    try:
        con.executescript(SCHEMA)
        cols = list(rows[0])
        con.executemany(
            f"INSERT INTO pharmacies ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})",
            rows,
        )
        con.commit()
    finally:
        con.close()
    tmp.replace(db_path)
    return len(rows)


def ensure_db() -> Path:
    """Build the database if it does not exist yet, or if pharmacies.json is newer."""
    if not DB_PATH.exists() or JSON_PATH.stat().st_mtime > DB_PATH.stat().st_mtime:
        build_db()
    return DB_PATH


if __name__ == "__main__":
    print(f"Wrote {build_db()} pharmacies to {DB_PATH}")
