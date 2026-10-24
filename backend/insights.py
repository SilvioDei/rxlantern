"""Step 7c part 2 data routes: My medicine list, languages reported by patients, best time to go, the shortage
watchlist, demand signals for pharmacies, the savings finder, and the time-saved counter.

Like web_api.py: no model calls and no outside APIs; everything comes from the database and small files in data/.
Nothing about a person is stored: search counts are (drug, neighborhood, week, number), and the time-saved counter is
one number. Searches and questions from automated tests are never counted (is_automated).
"""

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend import community, config, sample_data, tools

router = APIRouter(prefix="/api")

# Time-saved estimate (baselines measured by the project owner, a Boston pharmacy manager):
PATIENT_MINUTES_PER_QUESTION = 15     # one real call to a Boston pharmacy took a patient about 15 minutes ...
CALLS_PER_QUESTION = 3                # ... and 3 calls
STAFF_MINUTES_PER_CALL = 4            # each "do you have it?" call takes pharmacy staff about 4 minutes
MIN_DEMAND_COUNT = 5                  # demand signals: show only counts of 5 or more
MIN_SLOT_REVIEWS = 3                  # best time to go: at least 3 reviews in a time slot
DAY_NAMES = tools.DAY_NAMES


def is_automated(request: Request) -> bool:
    """Requests from our own tests (Playwright's headless browser, FastAPI's test client, scripts) or marked as tests."""
    ua = (request.headers.get("user-agent") or "").lower()
    return bool(request.headers.get("x-rxlantern-test")) or any(
        w in ua for w in ("headlesschrome", "testclient", "python-httpx", "playwright", "python-requests", "curl/"))


def week_of(dt: datetime | None = None) -> str:
    """Monday of the Boston week, YYYY-MM-DD."""
    d = (dt or tools.now_boston()).astimezone(tools.BOSTON_TZ).date()
    return (d - timedelta(days=d.weekday())).isoformat()


def _drug_names() -> dict[str, str]:
    return {r["id"]: r["display_name"] for r in tools._rows("SELECT id, display_name FROM drugs")}


# ----------------------------------------------------------------------------- languages and best time
def reported_languages(reviews: list[dict]) -> dict[str, dict[str, int]]:
    """pharmacy_id -> {language: number of reviews that ticked it}."""
    out: dict[str, Counter] = defaultdict(Counter)
    for r in reviews:
        for lang in r.get("languages") or []:
            out[r["pharmacy_id"]][lang] += 1
    return {k: dict(v) for k, v in out.items()}


def best_times(reviews: list[dict]) -> list[dict]:
    """Typical wait by weekday and part of the day, only for slots with at least 3 reviews that give a wait."""
    slots: dict[tuple, list[int]] = defaultdict(list)
    for r in reviews:
        if r.get("visit_time") and r.get("wait_minutes") is not None:
            day = datetime.fromisoformat(r["visit_date"]).weekday()
            slots[(day, r["visit_time"])].append(r["wait_minutes"])
    order = {"morning": 0, "afternoon": 1, "evening": 2}
    return [{"weekday": d, "day_en": DAY_NAMES["en"][d], "day_es": DAY_NAMES["es"][d], "time": t,
             "typical_wait_minutes": round(statistics.median(w)), "reviews": len(w)}
            for (d, t), w in sorted(slots.items(), key=lambda x: (x[0][0], order[x[0][1]]))
            if len(w) >= MIN_SLOT_REVIEWS]


def pharmacy_extras(pharmacy_id: str | None = None) -> dict:
    """Languages and best times for one pharmacy (or all), real and sample kept apart."""
    real = community.published_review_details(pharmacy_id)
    sample = sample_data.reviews(pharmacy_id)
    return {"reported_languages": reported_languages(real), "sample_reported_languages": reported_languages(sample),
            "best_times": best_times(real), "sample_best_times": best_times(sample)}


@router.get("/pharmacies/{pharmacy_id}/insights")
def pharmacy_insights(pharmacy_id: str) -> dict:
    if tools._pharmacy(pharmacy_id) is None:
        raise HTTPException(404, "Pharmacy not found.")
    real = community.published_review_details(pharmacy_id)
    sample = sample_data.reviews(pharmacy_id)
    return {"pharmacy_id": pharmacy_id,
            "reported_languages": reported_languages(real).get(pharmacy_id, {}),
            "sample_reported_languages": reported_languages(sample).get(pharmacy_id, {}),
            "best_times": best_times(real), "sample_best_times": best_times(sample),
            "min_reviews_per_slot": MIN_SLOT_REVIEWS, "source": "RxLantern community reviews",
            "note": "Reported by patients, not by the pharmacy. Call to confirm."}


# ----------------------------------------------------------------------------- my medicine list
@router.get("/my-list")
def my_list(drug_ids: str, lang: str = "en") -> dict:
    """2 to 5 of our drugs -> FDA status per drug and, per pharmacy, recent community reports for each drug.
    The browser adds distance (the patient's location never reaches the server) and ranks the list."""
    ids = list(dict.fromkeys(x for x in drug_ids.split(",") if x))[:5]
    rows = {r["id"]: r for r in tools._rows("SELECT * FROM drugs")}
    ids = [i for i in ids if i in rows]
    if len(ids) < 2:
        raise HTTPException(400, "Please add 2 to 5 medicines from RxLantern's list.")
    drugs, real, sample = [], {}, {}
    for i in ids:
        d = rows[i]
        sh = tools.shortage_from_db(i)
        drugs.append({"id": i, "name": d["display_name"], "controlled": bool(d["controlled"]),
                      "shortage_status": sh["status"], "fda_estimate": sh["fda_estimate"],
                      "checked_date": sh["checked_date"], "source": sh["source"]})
        if not d["controlled"]:  # never stock reports for controlled medicines
            real[i] = community.fresh_reports_by_pharmacy(i)
            sample[i] = {x["pharmacy_id"]: x for x in sample_data.report_summary(drug_id=i)}
    from backend.web_api import _pharmacy_brief, with_languages
    out = []
    for p in tools._pharmacies():
        b = _pharmacy_brief(p, lang)
        per, sper = {}, {}
        for i in ids:
            r = real.get(i, {}).get(p["id"])
            if r:
                per[i] = {"in_stock_reports": r["in_stock_reports"], "out_of_stock_reports": r["out_of_stock_reports"],
                          "latest_report": r["latest_report"]}
            s = sample.get(i, {}).get(p["id"])
            if s:
                sper[i] = {"in_stock_reports": s["in_stock_reports"], "out_of_stock_reports": s["out_of_stock_reports"]}
        # "Reported in stock" = the newest real reports lean in stock (more in-stock than out-of-stock people).
        in_stock = [i for i, r in per.items() if r["in_stock_reports"] > r["out_of_stock_reports"]]
        out_stock = [i for i, r in per.items() if r["out_of_stock_reports"] >= r["in_stock_reports"]]
        b.update(reports=per, sample_reports=sper, reported_in_stock=in_stock, reported_out=out_stock,
                 sample_reported_in_stock=[i for i, r in sper.items() if r["in_stock_reports"] > r["out_of_stock_reports"]],
                 score_base=3 * len(in_stock) - 2 * len(out_stock) + (1 if b["open_now"] else 0))
        out.append(b)
    out = with_languages(out)
    shortages = sum(d["shortage_status"] == "in shortage" for d in drugs)
    return {"drugs": drugs, "pharmacies": out, "shortages": shortages, "reminder": community.CALL_TO_CONFIRM,
            "window_hours": community.REPORT_WINDOW_HOURS, "sample_data": sample_data.enabled(),
            "ranking": "More medicines reported in stock (last 72 hours) first, then fewer reported out of stock, "
                       "open now, and distance. Reports are from patients and can be wrong: call to confirm."}


# ----------------------------------------------------------------------------- shortage watchlist
@router.get("/watch-updates")
def watch_updates(drug_ids: str, since: str) -> dict:
    """New real 'in stock' reports for the starred drugs since the patient's last visit (inside the 72-hour window).
    The browser keeps only the ones near the patient's saved place."""
    try:
        t = datetime.fromisoformat(since)
    except ValueError as e:
        raise HTTPException(400, "Use an ISO date and time for 'since'.") from e
    t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    rows = {r["id"]: r for r in tools._rows("SELECT id, display_name, controlled FROM drugs")}
    ids = [i for i in dict.fromkeys(drug_ids.split(",")) if i in rows and not rows[i]["controlled"]][:30]
    pharms = {p["id"]: p for p in tools._pharmacies()}
    reports = []
    for r in community.reports_since(ids, t):
        p = pharms.get(r["pharmacy_id"], {})
        reports.append(r | {"drug": rows[r["drug_id"]]["display_name"], "pharmacy": p.get("name"),
                            "address": p.get("address"), "neighborhood": p.get("neighborhood"),
                            "latitude": p.get("latitude"), "longitude": p.get("longitude")})
    return {"reports": reports, "since": t.isoformat(), "reminder": community.CALL_TO_CONFIRM}


# ----------------------------------------------------------------------------- demand signals
class SearchCountBody(BaseModel):
    drug_id: str = Field(max_length=40)
    place: str = Field(max_length=40, description="ZIP code or Boston neighborhood the patient typed (never GPS)")


def _neighborhood(place: str) -> str | None:
    """The Boston neighborhood of the nearest RxLantern pharmacy to a ZIP code or neighborhood."""
    loc = tools.resolve_location(place)
    if not loc.get("found"):
        return None
    near = min(tools._pharmacies(), key=lambda p: tools.miles(loc["latitude"], loc["longitude"], p["latitude"], p["longitude"]))
    return near["neighborhood"]


@router.post("/search-count")
def search_count(body: SearchCountBody, request: Request) -> dict:
    """Count one search, anonymously: drug, neighborhood, week. Tests are never counted."""
    if is_automated(request):
        return {"counted": False, "reason": "automated test"}
    if not tools._rows("SELECT id FROM drugs WHERE id = ?", (body.drug_id,)):
        raise HTTPException(404, "Unknown medicine.")
    hood = _neighborhood(body.place)
    if hood is None:
        return {"counted": False, "reason": "place not found"}
    community.count_search(body.drug_id, hood, week_of())
    return {"counted": True}


@router.get("/demand")
def demand() -> dict:
    """Search counts for the last 4 weeks, only counts of 5 or more. Sample counts are shown apart."""
    now = tools.now_boston()
    weeks = [week_of(now - timedelta(weeks=k)) for k in range(4)]
    names = _drug_names()
    rows = [r | {"drug": names.get(r["drug_id"], r["drug_id"])} for r in community.search_counts(weeks)
            if r["count"] >= MIN_DEMAND_COUNT]
    rows.sort(key=lambda r: (r["week"], r["count"]), reverse=True)
    samples = [r | {"drug": names.get(r["drug_id"], r["drug_id"]), "week": weeks[0]} for r in sample_data.searches()
               if r["count"] >= MIN_DEMAND_COUNT]
    return {"rows": rows, "sample_rows": samples, "weeks": weeks, "min_count": MIN_DEMAND_COUNT,
            "sample_data": sample_data.enabled(),
            "note": ("Counts of searches on RxLantern by medicine, Boston neighborhood, and week. Nothing about the "
                     "person searching is stored (no account, no IP address, no exact location). Counts under "
                     f"{MIN_DEMAND_COUNT} are not shown. Searches by automated tests are not counted.")}


# ----------------------------------------------------------------------------- savings finder
@lru_cache(maxsize=1)
def _savings() -> dict:
    path = config.DATA_DIR / "savings.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"drugs": [], "note": ""}


@router.get("/savings/{drug_id}")
def savings(drug_id: str, insurance: str = "") -> dict:
    """Links (never prices) to GoodRx and TrumpRx.gov when the drug is listed there, and the maker's savings
    program for brand drugs. Medicare and MassHealth patients see only the note."""
    rows = tools._rows("SELECT id, display_name, controlled FROM drugs WHERE id = ?", (drug_id,))
    if not rows:
        raise HTTPException(404, "That medicine is not in RxLantern's list.")
    d = rows[0]
    s = _savings()
    rec = next((x for x in s["drugs"] if x["drug_id"] == drug_id), None)
    base = {"drug_id": drug_id, "note": s.get("note", ""), "checked_date": s.get("checked_date")}
    if insurance in ("medicare", "masshealth") or rec is None:
        return base | {"show_links": False}
    trx = rec["trumprx"] if rec["trumprx"]["listed"] and not d["controlled"] else None
    return base | {"show_links": True, "goodrx": rec["goodrx"] if rec["goodrx"]["listed"] else None,
                   "trumprx": trx, "trumprx_controlled": bool(d["controlled"]),
                   "manufacturer": rec["manufacturer"], "rule": s.get("rule")}


# ----------------------------------------------------------------------------- time saved
def count_real_question(request: Request, completed: bool) -> None:
    if completed and not is_automated(request):
        community.bump_counter("questions_answered")


@router.get("/impact")
def impact() -> dict:
    q = community.read_counter("questions_answered")
    return {"questions": q, "patient_minutes": q * PATIENT_MINUTES_PER_QUESTION,
            "staff_minutes": q * CALLS_PER_QUESTION * STAFF_MINUTES_PER_CALL,
            "baselines": {"patient_minutes_per_question": PATIENT_MINUTES_PER_QUESTION,
                          "calls_per_question": CALLS_PER_QUESTION, "staff_minutes_per_call": STAFF_MINUTES_PER_CALL,
                          "source": "Measured by the RxLantern project owner: one real call to a Boston pharmacy took a "
                                    "patient about 15 minutes and 3 calls; a pharmacy manager's estimate of about 4 "
                                    "minutes of staff time per 'do you have it?' call."},
            "counts": "Only real chat questions answered by RxLantern (not tests, not sample data).",
            "label": "estimate"}
