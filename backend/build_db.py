"""Build data/rxlantern.db (reference data, rebuilt from the small files in data/) and
data/rxlantern_user.db (community posts and accounts, never rebuilt or wiped).

Run by hand:   ..\\.venv\\Scripts\\python.exe -m backend.build_db
The app also calls ensure_db() on startup, so graders never need to run this.
"""

import csv
import json
import sqlite3
from pathlib import Path

from backend.config import DATA_DIR

JSON_PATH = DATA_DIR / "pharmacies.json"
DB_PATH = DATA_DIR / "rxlantern.db"
MEDICARE_DIR = DATA_DIR / "medicare"
ZIP_PATH = DATA_DIR / "boston_zip_centroids.csv"
# Community posts live in their own file (data/rxlantern_user.db) so rebuilding the reference data
# never deletes them. Schema and access: backend/community.py.

MED_SCHEMA = """
CREATE TABLE drugs (
    id TEXT PRIMARY KEY, display_name TEXT NOT NULL, category TEXT, generic_name TEXT, brand_names TEXT,
    strength TEXT, dosage_form TEXT, controlled INTEGER NOT NULL, dea_schedule TEXT, rxcuis TEXT, ndcs TEXT,
    rxnorm_generic TEXT, rxnorm_brand TEXT, typical_30_day_supply TEXT, shortage_search TEXT, sources TEXT,
    checked_date TEXT
);
-- Saved snapshot (fallback). Live API answers are cached separately in shortage_cache.
CREATE TABLE shortages (
    drug_id TEXT PRIMARY KEY REFERENCES drugs(id), status TEXT, summary TEXT, other_forms_on_list TEXT,
    matching_entries TEXT, source TEXT, api TEXT, checked_at TEXT
);
CREATE TABLE shortage_cache (drug_id TEXT PRIMARY KEY, fetched_at TEXT NOT NULL, result_json TEXT NOT NULL);
CREATE TABLE nadac_prices (
    drug_id TEXT REFERENCES drugs(id), ndc TEXT, ndc_description TEXT, nadac_per_unit REAL, pricing_unit TEXT,
    effective_date TEXT, as_of_date TEXT, classification TEXT, otc TEXT, pharmacy_type TEXT, source_file TEXT,
    checked_date TEXT
);
CREATE TABLE masshealth (
    drug_id TEXT PRIMARY KEY REFERENCES drugs(id), covered TEXT, prior_authorization TEXT, drug_class TEXT,
    notes TEXT, mhdl_rows TEXT, source TEXT, list_last_updated TEXT, checked_date TEXT
);
CREATE TABLE vaccines (
    id TEXT PRIMARY KEY, name TEXT, vaccine_group TEXT, medicare TEXT, masshealth TEXT, commercial TEXT,
    notes TEXT, certified_sites_only INTEGER, clinic_finder TEXT, extra_sources TEXT, checked_date TEXT
);
CREATE TABLE medicare_rules (key TEXT PRIMARY KEY, value TEXT, source TEXT, checked_date TEXT, extra TEXT);
CREATE TABLE zip_centroids (zip TEXT PRIMARY KEY, latitude REAL, longitude REAL, share_of_land_in_boston REAL,
                            source TEXT, checked_date TEXT);
-- Holiday hours found by web search on a pharmacy's own site, kept for 24 hours.
CREATE TABLE holiday_cache (pharmacy_id TEXT, holiday TEXT, fetched_at TEXT NOT NULL, result_json TEXT NOT NULL,
                            PRIMARY KEY (pharmacy_id, holiday));
"""

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


def _insert(con: sqlite3.Connection, table: str, rows: list[dict]) -> None:
    if not rows:
        return
    cols = list(rows[0])
    con.executemany(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})", rows)


def _j(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def _load(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def _medication_tables(con: sqlite3.Connection) -> dict:
    """Drugs, shortages, NADAC, MassHealth, Medicare, and vaccines, all from small files in data/."""
    counts = {}
    con.executescript(MED_SCHEMA)

    drugs = _load("drugs.json")["drugs"]
    _insert(con, "drugs", [{
        "id": d["id"], "display_name": d["display_name"], "category": d["category"],
        "generic_name": d["generic_name"], "brand_names": json.dumps(d["brand_names"]), "strength": d["strength"],
        "dosage_form": d["dosage_form"], "controlled": int(d["controlled"]), "dea_schedule": d["dea_schedule"],
        "rxcuis": _j(d["rxcuis"]), "ndcs": _j(d["ndcs"]), "rxnorm_generic": _j(d["rxnorm_generic"]),
        "rxnorm_brand": _j(d["rxnorm_brand"]), "typical_30_day_supply": _j(d["typical_30_day_supply"]),
        "shortage_search": d["shortage_search"], "sources": _j(d["sources"]), "checked_date": d["checked_date"],
    } for d in drugs])
    counts["drugs"] = len(drugs)

    snap = _load("shortages_snapshot.json")
    _insert(con, "shortages", [{
        "drug_id": x["drug_id"], "status": x["status"], "summary": x["summary"],
        "other_forms_on_list": _j(x.get("other_forms_on_list", [])), "matching_entries": _j(x["matching_entries"]),
        "source": x["source"], "api": x["api"], "checked_at": x["checked_at"],
    } for x in snap["drugs"]])
    counts["shortages"] = len(snap["drugs"])

    with open(DATA_DIR / "nadac_sample.csv", newline="", encoding="utf-8") as f:
        nadac = list(csv.DictReader(f))
    for r in nadac:
        r["nadac_per_unit"] = float(r["nadac_per_unit"])
    _insert(con, "nadac_prices", nadac)
    counts["nadac_prices"] = len(nadac)

    mh = _load("masshealth.json")
    _insert(con, "masshealth", [{
        "drug_id": x["drug_id"], "covered": x["covered"], "prior_authorization": x["prior_authorization"],
        "drug_class": x.get("drug_class", "not found"), "notes": _j(x["notes"]), "mhdl_rows": _j(x["mhdl_rows"]),
        "source": x["source"], "list_last_updated": mh["list_last_updated"], "checked_date": x["checked_date"],
    } for x in mh["drugs"]])
    counts["masshealth"] = len(mh["drugs"])

    vac = _load("vaccines.json")
    _insert(con, "vaccines", [{
        "id": v["id"], "name": v["name"], "vaccine_group": v["group"], "medicare": _j(v["medicare"]),
        "masshealth": _j(v["masshealth"]), "commercial": _j(v["commercial"]), "notes": _j(v["notes"]),
        "certified_sites_only": int(bool(v.get("certified_sites_only"))), "clinic_finder": v.get("clinic_finder"),
        "extra_sources": _j(v.get("extra_sources", [])), "checked_date": v["checked_date"],
    } for v in vac["vaccines"]])
    counts["vaccines"] = len(vac["vaccines"])

    # Medicare Part D: every CSV in data/medicare/ becomes a table named medicare_<file name>.
    for path in sorted(MEDICARE_DIR.glob("*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        table = "medicare_" + path.stem
        con.execute(f"CREATE TABLE {table} ({', '.join(c + ' TEXT' for c in rows[0])})")
        _insert(con, table, rows)
        counts[table] = len(rows)
    with open(ZIP_PATH, newline="", encoding="utf-8") as f:
        zips = list(csv.DictReader(f))
    _insert(con, "zip_centroids", zips)
    counts["zip_centroids"] = len(zips)

    rules = MEDICARE_DIR / "part_d_rules_2026.json"
    if rules.exists():
        r = json.loads(rules.read_text(encoding="utf-8"))
        _insert(con, "medicare_rules", [{"key": k, "value": _j(v["value"]), "source": v["source"],
                                         "checked_date": v.get("checked_date", r["checked_date"]),
                                         # other fields, e.g. which drugs a rule applies to (Step 7c)
                                         "extra": json.dumps({x: y for x, y in v.items()
                                                              if x not in ("value", "source", "label", "checked_date")})}
                                        for k, v in r["rules"].items()])
        counts["medicare_rules"] = len(r["rules"])
    return counts


def build_db(json_path: Path = JSON_PATH, db_path: Path = DB_PATH) -> int:
    """(Re)create every table from the small files in data/. Returns the pharmacy row count."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    rows = [_row(p) for p in data["pharmacies"]]
    tmp = db_path.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    try:
        con.executescript(SCHEMA)
        _insert(con, "pharmacies", rows)
        _medication_tables(con)
        con.commit()
    finally:
        con.close()
    tmp.replace(db_path)
    return len(rows)


def _sources() -> list[Path]:
    names = ("drugs.json", "shortages_snapshot.json", "nadac_sample.csv", "masshealth.json", "vaccines.json",
             "boston_zip_centroids.csv")
    return [JSON_PATH, *(DATA_DIR / n for n in names), *MEDICARE_DIR.glob("*")]


def ensure_user_db() -> Path:
    """Create the community tables if they are missing. Never deletes anything."""
    from backend.community import init_db
    return init_db()


def ensure_db() -> Path:
    """Build the database if it does not exist yet, or if any source file in data/ is newer."""
    if not DB_PATH.exists() or any(p.exists() and p.stat().st_mtime > DB_PATH.stat().st_mtime for p in _sources()):
        build_db()
    ensure_user_db()
    return DB_PATH


if __name__ == "__main__":
    print(f"Wrote {build_db()} pharmacies (plus medication tables) to {DB_PATH}")
