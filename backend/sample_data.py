"""Sample stock reports and reviews for demonstration (graders clone the repo with an empty database).

Rules:
- Shown only when config.SHOW_SAMPLE_DATA is on.
- Never written to the database, so they can never be counted together with real posts.
- Every item has "sample": True and is shown with a "Sample" badge; the author is "RxLantern sample",
  never a made-up patient name, and every comment starts with "Sample post:".
- Times are relative to now, so sample reports always fall inside the 72-hour window.
- No controlled drugs (Adderall XR, Concerta), same as real reports.
"""

from datetime import datetime, timedelta, timezone

from backend import config

SAMPLE_AUTHOR = "RxLantern sample"

# (pharmacy_id, drug_id, in_stock, hours_ago)
_REPORTS = [
    ("cvs-2283", "ozempic_05", True, 3),
    ("community-care-pharmacy", "ozempic_05", False, 9),
    ("stopandshop-0429", "amoxicillin_susp_400", True, 5),
    ("cvs-10174", "albuterol_hfa", True, 2),
    ("walgreens-3135", "eliquis_5", True, 20),
    ("cvs-5874", "mounjaro_5", False, 30),
    ("gary-drug", "epinephrine_03", True, 12),
]

# (pharmacy_id, rating, wait_minutes, days_ago, comment, visit_time, staff languages)
# Step 7c part 2: the three Chinatown reviews 7, 14, and 21 days ago fall on the same weekday and part of the day,
# so "Best time to go" has a sample slot; several reviews tick "Staff spoke my language".
_REVIEWS = [
    ("cvs-2283", 4, 15, 2, "Sample post: staff explained when my refill would be ready.", "afternoon", ["Haitian Creole"]),
    ("community-care-pharmacy", 5, 5, 4, "Sample post: quick pickup, and they offered delivery.", "morning", ["Spanish"]),
    ("walgreens-3135", 3, 30, 6, "Sample post: busy at lunchtime, so calling ahead helped.", "afternoon", []),
    ("cvs-10174", 4, 10, 3, "Sample post: short line in the evening.", "evening", []),
    ("stopandshop-0429", 2, 40, 5, "Sample post: long line on Saturday morning.", "morning", []),
    ("cvs-5874", 5, 8, 7, "Sample post: the pharmacist explained everything in Cantonese.", "morning", ["Cantonese"]),
    ("cvs-5874", 4, 12, 14, "Sample post: short wait before work.", "morning", ["Cantonese", "Mandarin"]),
    ("cvs-5874", 4, 10, 21, "Sample post: quick and friendly.", "morning", []),
]

# (drug_id, neighborhood, searches this week) for the "For pharmacies" page. The last one is under 5, so it is hidden.
_SEARCHES = [
    ("ozempic_05", "Dorchester", 15), ("amoxicillin_susp_400", "Mattapan", 9), ("albuterol_hfa", "Chinatown", 7),
    ("wegovy_24", "Back Bay", 6), ("cefdinir_susp_250", "East Boston", 3),
]


def enabled() -> bool:
    return bool(config.SHOW_SAMPLE_DATA)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def reports(pharmacy_id: str | None = None, drug_id: str | None = None, now: datetime | None = None) -> list[dict]:
    """Individual sample reports, newest first."""
    if not enabled():
        return []
    now = now or datetime.now(timezone.utc)
    out = [{"sample": True, "pharmacy_id": p, "drug_id": d, "in_stock": s,
            "reported_at": _iso(now - timedelta(hours=h)), "by": SAMPLE_AUTHOR}
           for p, d, s, h in _REPORTS
           if (pharmacy_id is None or p == pharmacy_id) and (drug_id is None or d == drug_id)]
    return sorted(out, key=lambda r: r["reported_at"], reverse=True)


def report_summary(pharmacy_id: str | None = None, drug_id: str | None = None) -> list[dict]:
    """Sample reports grouped like community.stock_summary (one row per pharmacy and drug), kept separate."""
    rows: dict[tuple, dict] = {}
    for r in reports(pharmacy_id, drug_id):
        x = rows.setdefault((r["pharmacy_id"], r["drug_id"]), {
            "sample": True, "pharmacy_id": r["pharmacy_id"], "drug_id": r["drug_id"], "in_stock_reports": 0,
            "out_of_stock_reports": 0, "latest_report": r["reported_at"]})
        x["in_stock_reports" if r["in_stock"] else "out_of_stock_reports"] += 1
        x["latest_report"] = max(x["latest_report"], r["reported_at"])
    for x in rows.values():
        x["conflicting"] = x["in_stock_reports"] > 0 and x["out_of_stock_reports"] > 0
    return list(rows.values())


def reviews(pharmacy_id: str | None = None, now: datetime | None = None) -> list[dict]:
    """Sample reviews, newest first. Never included in averages."""
    if not enabled():
        return []
    today = (now or datetime.now(timezone.utc)).date()
    out = [{"sample": True, "pharmacy_id": p, "rating": r, "wait_minutes": w,
            "visit_date": (today - timedelta(days=d)).isoformat(), "visit_time": t, "languages": langs,
            "comment": c, "by": SAMPLE_AUTHOR}
           for p, r, w, d, c, t, langs in _REVIEWS if pharmacy_id is None or p == pharmacy_id]
    return sorted(out, key=lambda r: r["visit_date"], reverse=True)


def searches() -> list[dict]:
    """Sample weekly search counts (this week), shown apart from real counts with a Sample badge."""
    if not enabled():
        return []
    return [{"sample": True, "drug_id": d, "neighborhood": n, "count": c} for d, n, c in _SEARCHES]
