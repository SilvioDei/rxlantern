"""Read-only data routes for the website (no model calls, no login): pharmacies, drugs, vaccines, site info."""

from fastapi import APIRouter, HTTPException

from backend import community, config, tools

router = APIRouter(prefix="/api")
INSURANCE_TYPES = ["masshealth", "medicare", "commercial", "uninsured"]


def _boston_date(iso: str | None) -> str:
    """UTC timestamp -> the Boston calendar date it was checked."""
    from datetime import datetime
    try:
        return datetime.fromisoformat(iso).astimezone(tools.BOSTON_TZ).date().isoformat()
    except (TypeError, ValueError):
        return tools.NF


def _list(v):
    return v if isinstance(v, list) else []


@router.get("/meta")
def meta() -> dict:
    """App name and the small lists the forms need."""
    pharms = tools._pharmacies()
    drugs = tools._rows("SELECT id, display_name, controlled FROM drugs")
    return {
        "app_name": config.APP_NAME,
        "languages": ["en", "es"],
        "insurance_types": INSURANCE_TYPES,
        "neighborhoods": sorted({p["neighborhood"] for p in pharms}),
        "pharmacies": [{"id": p["id"], "name": p["name"], "address": p["address"], "neighborhood": p["neighborhood"]}
                       for p in sorted(pharms, key=lambda p: (p["neighborhood"], p["name"]))],
        "drugs": [{"id": d["id"], "name": d["display_name"], "controlled": bool(d["controlled"])} for d in drugs],
        "vaccines": [{"id": v["id"], "name": v["name"]} for v in tools._rows("SELECT id, name FROM vaccines")],
    }


def _pharmacy_brief(p: dict, lang: str) -> dict:
    st = tools.open_status(p["id"], lang)
    return {
        "id": p["id"], "name": p["name"], "type": p["type"], "address": p["address"], "phone": p["phone"],
        "neighborhood": p["neighborhood"], "latitude": p["latitude"], "longitude": p["longitude"],
        "open_now": st["open_now"], "status": st["status"], "closes_at": st.get("closes_at"),
        "opens_next": st.get("opens_next"), "delivery": p["delivery"], "drive_thru": p["drive_thru"],
        "wheelchair_accessible": p["wheelchair_accessible"], "languages": p["languages"],
        "vaccines": _list(p["vaccines_routine"]) + _list(p["vaccines_travel"]),
        "website": p["website"], "checked_date": p["checked_date"],
    }


@router.get("/pharmacies")
def pharmacies(lang: str = "en") -> dict:
    return {"pharmacies": [_pharmacy_brief(p, lang) for p in tools._pharmacies()],
            "note": "Languages spoken and wheelchair access are 'not found' on the pharmacies' public pages."}


@router.get("/pharmacies/{pharmacy_id}")
def pharmacy(pharmacy_id: str, lang: str = "en") -> dict:
    d = tools.pharmacy_details(pharmacy_id, lang)
    if d.get("found") is False:
        raise HTTPException(404, "Pharmacy not found.")
    p = tools._pharmacy(pharmacy_id)
    names = {r["id"]: r["display_name"] for r in tools._rows("SELECT id, display_name FROM drugs")}
    reports = community.stock_summary(pharmacy_id)
    for x in reports["drugs"]:
        x["drug"] = names.get(x["drug_id"], x["drug_id"])
    return d | {"brief": _pharmacy_brief(p, lang), "nearby_clinics": p["nearby_clinics"],
                "stock_reports": reports, "reviews": community.review_summary(pharmacy_id)}


@router.get("/drugs")
def drugs(lang: str = "en") -> dict:
    """The 25 drugs with FDA shortage status (saved snapshot, with date) and fresh community reports."""
    rows = tools._rows("SELECT d.id, d.display_name, d.controlled, d.strength, d.dosage_form, s.status, s.summary, "
                       "s.checked_at, s.source FROM drugs d JOIN shortages s ON s.drug_id = d.id")
    pharms = tools._pharmacies()
    out = []
    for r in rows:
        item = {"id": r["id"], "name": r["display_name"], "strength": r["strength"], "form": r["dosage_form"],
                "controlled": bool(r["controlled"]), "shortage_status": r["status"], "shortage_summary": r["summary"],
                "checked_date": _boston_date(r["checked_at"]), "source": r["source"]}
        if r["controlled"]:
            item["community"] = {"refused": True, "message": community.CONTROLLED_MESSAGE}
            item["call_script"] = tools.call_script(r["id"], lang=lang)["call_script"]
        else:
            fresh = []
            for p in pharms:
                s = community.stock_summary(p["id"], r["id"])
                if s["drugs"]:
                    fresh.append({"pharmacy_id": p["id"], "pharmacy": f"{p['name']}, {p['address']}", **s["drugs"][0]})
            item["community"] = {"reports": fresh, "reminder": community.CALL_TO_CONFIRM}
        out.append(item)
    return {"drugs": sorted(out, key=lambda x: (not x["controlled"], x["name"])),
            "source": tools.SHORTAGE_PAGE}


@router.get("/vaccines")
def vaccines() -> dict:
    """Each vaccine, which pharmacies list it on their own pages, and coverage by insurance type."""
    pharms = tools._pharmacies()
    out = []
    for v in tools._rows("SELECT * FROM vaccines"):
        label = next((k for k, vid in tools.VACCINE_IDS.items() if vid == v["id"]), v["name"])
        offering = [{"id": p["id"], "name": p["name"], "address": p["address"], "neighborhood": p["neighborhood"]}
                    for p in pharms if any(label.lower() in x.lower()
                                           for x in _list(p["vaccines_routine"]) + _list(p["vaccines_travel"]))]
        out.append({"id": v["id"], "name": v["name"], "group": v["vaccine_group"],
                    "pharmacies": offering, "medicare": tools._j(v["medicare"]), "masshealth": tools._j(v["masshealth"]),
                    "commercial": tools._j(v["commercial"]), "notes": tools._j(v["notes"]),
                    "certified_sites_only": bool(v["certified_sites_only"]), "clinic_finder": v["clinic_finder"],
                    "checked_date": v["checked_date"]})
    return {"vaccines": out,
            "note": "Pharmacies are listed only if their own page names the vaccine. Others may still offer it."}


@router.get("/drugs/{drug_id}/call-script")
def drug_call_script(drug_id: str, lang: str = "en") -> dict:
    return tools.call_script(drug_id, lang=lang)
