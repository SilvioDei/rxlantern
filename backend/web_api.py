"""Read-only data routes for the website. No model calls. Every page loads from the database and our own tools
(FDA shortage data is refreshed in the background, see shortage_refresh.py). The one exception is /api/other-drug:
a medicine outside RxLantern's list has no saved data, so its FDA shortage status is looked up live."""

import json
from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, HTTPException

from backend import community, config, sample_data, tools

router = APIRouter(prefix="/api")
INSURANCE_TYPES = ["masshealth", "medicare", "commercial", "uninsured"]


def _boston_date(iso: str | None) -> str:
    """UTC timestamp -> the Boston calendar date it was checked."""
    try:
        return datetime.fromisoformat(iso).astimezone(tools.BOSTON_TZ).date().isoformat()
    except (TypeError, ValueError):
        return tools.NF


def _list(v):
    return v if isinstance(v, list) else []


@lru_cache(maxsize=1)
def _plans() -> dict:
    return json.loads((config.DATA_DIR / "insurance_plans.json").read_text(encoding="utf-8"))


def _plan(plan_id: str | None, insurance: str | None) -> dict | None:
    """The chosen plan's official pharmacy finder and member services number (MassHealth/Medicare by type)."""
    plans = {p["id"]: p for p in _plans()["plans"]}
    if insurance in ("masshealth", "medicare"):
        return plans[insurance]
    if insurance == "commercial":
        return plans.get(plan_id or "") or plans["other_commercial"]
    return None


def _drug_rows() -> list[dict]:
    return tools._rows("SELECT * FROM drugs")


# Names patients know, shown in the search box. Both amoxicillin forms share one name, so the patient picks the form.
MEDICINE_LABELS = {
    "adderall_xr_30": "Adderall XR (amphetamine salts)", "concerta_18": "Concerta (methylphenidate)",
    "atorvastatin_20": "Atorvastatin (Lipitor)", "lisinopril_10": "Lisinopril (Zestril, Prinivil)",
    "levothyroxine_50": "Levothyroxine (Synthroid)", "metformin_500": "Metformin",
    "amlodipine_5": "Amlodipine (Norvasc)", "omeprazole_20": "Omeprazole (Prilosec)",
    "sertraline_50": "Sertraline (Zoloft)", "amoxicillin_500": "Amoxicillin", "amoxicillin_susp_400": "Amoxicillin",
    "ozempic_05": "Ozempic (semaglutide)", "mounjaro_5": "Mounjaro (tirzepatide)", "eliquis_5": "Eliquis (apixaban)",
    "humira_40": "Humira (adalimumab)", "dupixent_300": "Dupixent (dupilumab)",
    "albuterol_hfa": "Albuterol inhaler (ProAir, Ventolin)", "lantus_solostar": "Insulin glargine (Lantus)",
    "sumatriptan_50": "Sumatriptan (Imitrex)", "latanoprost_0005": "Latanoprost eye drops (Xalatan)",
    "fluticasone_nasal_50": "Fluticasone nasal spray (Flonase)", "triamcinolone_cream_01": "Triamcinolone cream",
    "epinephrine_03": "Epinephrine auto-injector (EpiPen, Auvi-Q)", "nicotine_patch_21": "Nicotine patch",
    "paxlovid": "Paxlovid (nirmatrelvir and ritonavir)",
    # Step 7c: 125 more. Forms of the same medicine share one name (for example amoxicillin capsules and liquids).
    "amoxicillin_susp_250": "Amoxicillin",
    "wegovy_24": "Wegovy (semaglutide)", "rybelsus_7": "Rybelsus (semaglutide tablets)",
    "zepbound_25": "Zepbound (tirzepatide)", "trulicity_15": "Trulicity (dulaglutide)", "victoza_18": "Victoza (liraglutide)",
    "jardiance_10": "Jardiance (empagliflozin)", "farxiga_10": "Farxiga (dapagliflozin)", "januvia_100": "Januvia (sitagliptin)",
    "glipizide_5": "Glipizide (Glucotrol)", "pioglitazone_30": "Pioglitazone (Actos)", "metformin_er_500": "Metformin",
    "humalog_kwikpen": "Insulin lispro (Humalog, Admelog)", "novolog_flexpen": "Insulin aspart (NovoLog)",
    "tresiba_flextouch": "Insulin degludec (Tresiba)", "toujeo_solostar": "Toujeo (insulin glargine 300 units/mL)",
    "insulin_nph_pen": "Insulin NPH (Humulin N, Novolin N)",
    "advair_diskus_250": "Advair Diskus (fluticasone and salmeterol)", "symbicort_160": "Symbicort (budesonide and formoterol)",
    "trelegy_100": "Trelegy Ellipta", "spiriva_handihaler": "Spiriva HandiHaler (tiotropium)",
    "flovent_hfa_110": "Flovent HFA (fluticasone inhaler)", "albuterol_neb_25": "Albuterol nebulizer solution",
    "duoneb": "DuoNeb (ipratropium and albuterol nebulizer)", "budesonide_neb_05": "Budesonide nebulizer (Pulmicort Respules)",
    "montelukast_10": "Montelukast (Singulair)", "montelukast_chew_5": "Montelukast (Singulair)",
    "benzonatate_100": "Benzonatate (Tessalon Perles)", "naloxone_nasal_4": "Naloxone nasal spray (Narcan)",
    "oseltamivir_75": "Oseltamivir (Tamiflu)", "oseltamivir_susp": "Oseltamivir (Tamiflu)",
    "amox_clav_875": "Amoxicillin-clavulanate (Augmentin)", "amox_clav_susp_400": "Amoxicillin-clavulanate (Augmentin)",
    "azithromycin_250": "Azithromycin (Zithromax, Z-Pak)", "azithromycin_susp_200": "Azithromycin (Zithromax, Z-Pak)",
    "cephalexin_500": "Cephalexin (Keflex)", "cephalexin_susp_250": "Cephalexin (Keflex)", "cefdinir_susp_250": "Cefdinir (Omnicef)",
    "doxycycline_100": "Doxycycline", "smx_tmp_ds": "Sulfamethoxazole-trimethoprim (Bactrim)",
    "smx_tmp_susp": "Sulfamethoxazole-trimethoprim (Bactrim)", "nitrofurantoin_100": "Nitrofurantoin (Macrobid)",
    "ciprofloxacin_500": "Ciprofloxacin (Cipro)", "metronidazole_500": "Metronidazole (Flagyl)",
    "penicillin_vk_500": "Penicillin VK", "fluconazole_150": "Fluconazole (Diflucan)", "valacyclovir_1g": "Valacyclovir (Valtrex)",
    "mupirocin_2": "Mupirocin ointment (Bactroban)",
    "losartan_50": "Losartan (Cozaar)", "metoprolol_succ_er_50": "Metoprolol succinate ER (Toprol XL)",
    "metoprolol_tart_25": "Metoprolol tartrate (Lopressor)", "rosuvastatin_10": "Rosuvastatin (Crestor)",
    "hydrochlorothiazide_25": "Hydrochlorothiazide (HCTZ)", "simvastatin_20": "Simvastatin (Zocor)",
    "pravastatin_40": "Pravastatin (Pravachol)", "furosemide_20": "Furosemide (Lasix)", "carvedilol_125": "Carvedilol (Coreg)",
    "spironolactone_25": "Spironolactone (Aldactone)", "clopidogrel_75": "Clopidogrel (Plavix)", "valsartan_160": "Valsartan (Diovan)",
    "ezetimibe_10": "Ezetimibe (Zetia)", "propranolol_10": "Propranolol (Inderal)", "xarelto_20": "Xarelto (rivaroxaban)",
    "warfarin_5": "Warfarin (Coumadin, Jantoven)", "entresto_49_51": "Entresto (sacubitril and valsartan)",
    "repatha_140": "Repatha (evolocumab)", "brilinta_90": "Brilinta (ticagrelor)", "nitroglycerin_sl_04": "Nitroglycerin (Nitrostat)",
    "escitalopram_10": "Escitalopram (Lexapro)", "bupropion_xl_150": "Bupropion XL (Wellbutrin XL)", "fluoxetine_20": "Fluoxetine (Prozac)",
    "trazodone_50": "Trazodone", "duloxetine_60": "Duloxetine (Cymbalta)", "buspirone_10": "Buspirone (Buspar)",
    "venlafaxine_er_75": "Venlafaxine ER (Effexor XR)", "hydroxyzine_25": "Hydroxyzine (Atarax)",
    "quetiapine_25": "Quetiapine (Seroquel)", "aripiprazole_5": "Aripiprazole (Abilify)", "lamotrigine_100": "Lamotrigine (Lamictal)",
    "alprazolam_05": "Alprazolam (Xanax)", "clonazepam_05": "Clonazepam (Klonopin)", "lorazepam_05": "Lorazepam (Ativan)",
    "zolpidem_10": "Zolpidem (Ambien)", "adderall_ir_10": "Adderall (amphetamine salts, immediate release)",
    "vyvanse_30": "Vyvanse (lisdexamfetamine)", "methylphenidate_10": "Ritalin (methylphenidate)",
    "focalin_xr_10": "Focalin XR (dexmethylphenidate)", "atomoxetine_40": "Atomoxetine (Strattera)",
    "guanfacine_er_1": "Guanfacine ER (Intuniv)", "hydrocodone_apap_5_325": "Hydrocodone-acetaminophen (Norco)",
    "oxycodone_5": "Oxycodone (Roxicodone)", "oxycodone_apap_5_325": "Oxycodone-acetaminophen (Percocet)",
    "tramadol_50": "Tramadol (Ultram)", "gabapentin_300": "Gabapentin (Neurontin)", "pregabalin_75": "Pregabalin (Lyrica)",
    "buprenorphine_naloxone_8_2": "Buprenorphine-naloxone (Suboxone)", "meloxicam_15": "Meloxicam (Mobic)",
    "ibuprofen_800": "Ibuprofen 800 mg (Motrin)", "cyclobenzaprine_10": "Cyclobenzaprine (Flexeril)",
    "diclofenac_gel_1": "Diclofenac gel (Voltaren)", "phentermine_375": "Phentermine (Adipex-P)",
    "testosterone_cyp_200": "Testosterone cypionate (Depo-Testosterone)", "pantoprazole_40": "Pantoprazole (Protonix)",
    "famotidine_20": "Famotidine (Pepcid)", "ondansetron_odt_4": "Ondansetron (Zofran)", "linzess_145": "Linzess (linaclotide)",
    "prednisone_20": "Prednisone", "prednisolone_soln_15": "Prednisolone liquid (Orapred, Millipred)",
    "methylprednisolone_4_pack": "Methylprednisolone (Medrol Dosepak)", "allopurinol_100": "Allopurinol (Zyloprim)",
    "colchicine_06": "Colchicine (Colcrys)", "estradiol_1": "Estradiol (Estrace)",
    "norgestimate_ee": "Birth control: norgestimate-ethinyl estradiol (Sprintec)",
    "medroxyprogesterone_inj_150": "Depo-Provera (medroxyprogesterone shot)", "finasteride_5": "Finasteride (Proscar)",
    "tamsulosin_04": "Tamsulosin (Flomax)", "alendronate_70": "Alendronate (Fosamax)", "levetiracetam_500": "Levetiracetam (Keppra)",
    "truvada_prep": "Truvada (emtricitabine and tenofovir, PrEP)", "biktarvy": "Biktarvy",
    "enbrel_50": "Enbrel (etanercept)", "nurtec_75": "Nurtec ODT (rimegepant)", "timolol_eye_05": "Timolol eye drops (Timoptic)",
    "clobetasol_cream_005": "Clobetasol cream (Temovate)", "ergocalciferol_50000": "Vitamin D 50,000 units (ergocalciferol)",
}


def _medicine_label(d: dict) -> str:
    return MEDICINE_LABELS.get(d["id"], d["display_name"])


@router.get("/meta")
def meta() -> dict:
    """App name and the small lists the forms need (drug names for the search box, plans, neighborhoods)."""
    pharms = tools._pharmacies()
    drugs = []
    for d in _drug_rows():
        brands = tools._j(d["brand_names"])
        drugs.append({"id": d["id"], "name": d["display_name"], "controlled": bool(d["controlled"]),
                      "generic": d["generic_name"], "brands": brands if isinstance(brands, list) else [],
                      "strength": d["strength"], "form": d["dosage_form"], "medicine": d["generic_name"],
                      "medicine_label": _medicine_label(d)})
    return {
        "app_name": config.APP_NAME,
        "languages": ["en", "es"],
        "insurance_types": INSURANCE_TYPES,
        "plans": [{"id": p["id"], "name": p["name"], "type": p["type"]} for p in _plans()["plans"]],
        "neighborhoods": sorted({p["neighborhood"] for p in pharms}),
        "pharmacies": [{"id": p["id"], "name": p["name"], "address": p["address"], "neighborhood": p["neighborhood"],
                        "phone": p["phone"]}
                       for p in sorted(pharms, key=lambda p: (p["neighborhood"], p["name"]))],
        "drugs": drugs,
        "vaccines": [{"id": v["id"], "name": v["name"]} for v in tools._rows("SELECT id, name FROM vaccines")],
        "sample_data": sample_data.enabled(),
    }


@router.get("/location")
def location(place: str) -> dict:
    """ZIP code or Boston neighborhood -> a center point (from our ZIP table). Nothing is saved."""
    loc = tools.resolve_location(place)
    if not loc.get("found"):
        return {"found": False, "message": loc.get("message"), "known_neighborhoods": loc.get("known_neighborhoods")}
    return {k: loc[k] for k in ("found", "label", "latitude", "longitude", "source", "checked_date")}


def _today_counter(p: dict, at: datetime) -> dict:
    """Today's counter hours (lunch break cut out) and the latest closing minute, for 'open latest' sorting."""
    iv = tools._intervals(p, tools.DAYS[at.weekday()])
    if iv is None:
        return {"counter_today": tools.NF, "closes_latest_minutes": None}
    if not iv:
        return {"counter_today": "closed", "closes_latest_minutes": -1}
    text = ", ".join(f"{tools._fmt_time(tools._hm(s))}-{tools._fmt_time(tools._hm(e))}" for s, e in iv)
    return {"counter_today": text, "closes_latest_minutes": max(e for _, e in iv)}


def _store_today(p: dict, at: datetime) -> str:
    week = tools._week(p["store_hours"])
    return week[tools.DAY_NAMES["en"][at.weekday()]] if isinstance(week, dict) else tools.NF


def _pharmacy_brief(p: dict, lang: str, at: datetime | None = None) -> dict:
    at = at or tools.now_boston()
    st = tools.open_status(p["id"], lang, at)
    dd = p["delivery_details"] if isinstance(p["delivery_details"], dict) else {}
    return {
        "id": p["id"], "name": p["name"], "type": p["type"], "address": p["address"], "phone": p["phone"],
        "neighborhood": p["neighborhood"], "latitude": p["latitude"], "longitude": p["longitude"],
        "open_now": st["open_now"], "status": st["status"], "closes_at": st.get("closes_at"),
        "closes_for": st.get("closes_for"), "opens_next": st.get("opens_next"),
        **_today_counter(p, at), "store_today": _store_today(p, at),
        "delivery": p["delivery"], "delivery_summary": dd.get("same_day") or dd.get("cost") or None,
        "drive_thru": p["drive_thru"], "languages": p["languages"],
        "vaccines": _list(p["vaccines_routine"]) + _list(p["vaccines_travel"]),
        "website": p["website"], "vaccine_booking_url": p["vaccine_booking_url"], "checked_date": p["checked_date"],
        "hours_source": p["sources"].get("pharmacy_hours", p["website"]) if isinstance(p["sources"], dict) else p["website"],
    }


def _parse_at(at: str | None) -> datetime | None:
    """Optional 'check hours at this Boston time' (used by the tests to see a closed pharmacy)."""
    if not at:
        return None
    try:
        dt = datetime.fromisoformat(at)
    except ValueError as e:
        raise HTTPException(400, "Use YYYY-MM-DDTHH:MM for 'at'.") from e
    return dt.replace(tzinfo=tools.BOSTON_TZ) if dt.tzinfo is None else dt.astimezone(tools.BOSTON_TZ)


def with_languages(briefs: list[dict]) -> list[dict]:
    """Add the languages patients reported in reviews (Step 7c part 2), real and sample kept apart."""
    from backend.insights import pharmacy_extras
    x = pharmacy_extras()
    for b in briefs:
        b["reported_languages"] = x["reported_languages"].get(b["id"], {})
        b["sample_reported_languages"] = x["sample_reported_languages"].get(b["id"], {})
    return briefs


@router.get("/pharmacies")
def pharmacies(lang: str = "en") -> dict:
    return {"pharmacies": with_languages([_pharmacy_brief(p, lang) for p in tools._pharmacies()]),
            "note": "Languages spoken are 'not found' on the pharmacies' public pages."}


def _drug_names() -> dict[str, str]:
    return {r["id"]: r["display_name"] for r in tools._rows("SELECT id, display_name FROM drugs")}


@router.get("/pharmacies/{pharmacy_id}")
def pharmacy(pharmacy_id: str, lang: str = "en") -> dict:
    d = tools.pharmacy_details(pharmacy_id, lang)
    if d.get("found") is False:
        raise HTTPException(404, "Pharmacy not found.")
    p = tools._pharmacy(pharmacy_id)
    names = _drug_names()
    reports = community.stock_summary(pharmacy_id)
    for x in reports["drugs"]:
        x["drug"] = names.get(x["drug_id"], x["drug_id"])
    samples = sample_data.report_summary(pharmacy_id)
    for x in samples:
        x["drug"] = names.get(x["drug_id"], x["drug_id"])
    return d | {"brief": with_languages([_pharmacy_brief(p, lang)])[0], "nearby_clinics": p["nearby_clinics"],
                "stock_reports": reports, "sample_reports": samples,
                "reviews": community.review_summary(pharmacy_id), "sample_reviews": sample_data.reviews(pharmacy_id),
                "holidays": tools.upcoming_holidays(7)}


@router.get("/drugs")
def drugs(lang: str = "en") -> dict:
    """Shortage watch: the 150 drugs with FDA status (from the database, refreshed daily in the background), FDA's
    estimate if it gave one, and community report counts (non-controlled only). Real and sample counts stay apart."""
    real = community.fresh_report_counts_by_drug()
    samples: dict[str, dict] = {}
    for s in sample_data.reports():
        x = samples.setdefault(s["drug_id"], {"in_stock_reports": 0, "out_of_stock_reports": 0})
        x["in_stock_reports" if s["in_stock"] else "out_of_stock_reports"] += 1
    out = []
    with tools._connect() as con:  # one connection for all 150 drugs (the page must load in under 2 seconds)
        shortages = {r["id"]: tools.shortage_from_db(r["id"], con) for r in _drug_rows()}
    for r in _drug_rows():
        sh = shortages[r["id"]]
        item = {"id": r["id"], "name": r["display_name"], "strength": r["strength"], "form": r["dosage_form"],
                "controlled": bool(r["controlled"]), "shortage_status": sh["status"], "shortage_summary": sh["summary"],
                "fda_estimate": sh["fda_estimate"], "fda_updated": sh["fda_updated"],
                "checked_date": sh["checked_date"], "source": sh["source"],
                "call_script": tools.call_script(r["id"], lang=lang, drug=r)["call_script"]}
        if r["controlled"]:
            item["community"] = {"refused": True, "message": community.CONTROLLED_MESSAGE}
        else:
            item["community"] = {"real": real.get(r["id"]), "sample": samples.get(r["id"]),
                                 "reminder": community.CALL_TO_CONFIRM}
        out.append(item)
    return {"drugs": sorted(out, key=lambda x: (x["shortage_status"] != "in shortage", x["name"])),
            "source": tools.SHORTAGE_PAGE, "sample_data": sample_data.enabled()}


# ----------------------------------------------------------------------------- results page
@lru_cache(maxsize=64)
def _coverage_cached(drug_id: str, insurance: str) -> str:
    """Coverage facts for one drug and insurance type (reference data only changes on rebuild)."""
    nadac = tools.nadac_cost(drug_id)
    estimate = next((nadac[k] for k in ("generic", "brand") if isinstance(nadac.get(k), dict)), None)
    base = {"insurance": insurance, "nadac": {
        "estimate": estimate["estimate"] if estimate else None, "kind": "generic" if isinstance(nadac.get("generic"), dict) else "brand",
        "amount": nadac["amount"], "label": tools.NADAC_LABEL, "as_of": nadac["as_of"], "source": nadac["source"],
        "checked_date": nadac["checked_date"]}}
    if insurance == "masshealth":
        m = tools.masshealth_coverage(drug_id)
        base["masshealth"] = {k: m[k] for k in ("covered", "prior_authorization", "notes", "list_last_updated",
                                                 "source", "checked_date")}
    elif insurance == "medicare":
        m = tools.medicare_coverage(drug_id)
        est = m.get("your_monthly_cost_estimate")
        base["medicare"] = {
            "plans_in_massachusetts": m["plans_in_massachusetts"], "plans_covering": m["plans_covering"],
            "monthly_estimate": est if isinstance(est, dict) else None,
            "plans_with_prior_authorization": m["plans_with_prior_authorization"],
            "yearly_cap": m["rules_2026"]["yearly_out_of_pocket_cap"]["value"],
            "insulin_cap": m["rules_2026"].get("insulin_cap", {}).get("value"),
            "negotiated_price": bool(m["rules_2026"].get("negotiated_price_2026")),
            "amount": m["amount_used_for_estimates"], "note": m["note"], "source": m["source"],
            "rules_source": m["rules_2026"]["yearly_out_of_pocket_cap"]["source"], "checked_date": m["checked_date"]}
    elif insurance == "commercial":
        base["commercial"] = {"coverage": tools.NF, "answer": "RxLantern does not have commercial plans' drug lists. "
                              "Check with your plan.", "checked_date": tools.today()}
    return json.dumps(base)


@router.get("/results")
def results(drug_id: str, insurance: str = "", plan: str = "", lang: str = "en", at: str | None = None) -> dict:
    """The results page: one drug, every pharmacy (the browser sorts by distance from the patient's place, so a
    'Use my location' position never reaches the server), shortage status, coverage, and community posts."""
    rows = tools._rows("SELECT * FROM drugs WHERE id = ?", (drug_id,))
    if not rows:
        raise HTTPException(404, "That medicine is not in RxLantern yet. Please call the pharmacy.")
    d = rows[0]
    when = _parse_at(at) or tools.now_boston()
    insurance = insurance if insurance in INSURANCE_TYPES else ""
    controlled = bool(d["controlled"])
    real_reports = {} if controlled else community.fresh_reports_by_pharmacy(d["id"])
    sample_reports = {} if controlled else {x["pharmacy_id"]: x for x in sample_data.report_summary(drug_id=d["id"])}
    stats = community.review_stats_all()
    sample_reviews: dict[str, list] = {}
    for r in sample_data.reviews():
        sample_reviews.setdefault(r["pharmacy_id"], []).append(r)
    pharms = []
    for p in tools._pharmacies():
        b = _pharmacy_brief(p, lang, when)
        b["reviews"] = stats.get(p["id"], {"reviews": 0, "average_rating": None, "average_wait_minutes": None})
        b["sample_reviews"] = len(sample_reviews.get(p["id"], []))
        if not controlled:
            b["reports"] = real_reports.get(p["id"])
            b["sample_report"] = sample_reports.get(p["id"])
        pharms.append(b)
    supply = tools._j(d["typical_30_day_supply"])
    return {
        "drug": {"id": d["id"], "name": d["display_name"], "strength": d["strength"], "form": d["dosage_form"],
                 "controlled": controlled, "amount": supply.get("basis") if isinstance(supply, dict) else None},
        "shortage": tools.shortage_from_db(d["id"]),
        "coverage": json.loads(_coverage_cached(d["id"], insurance)),
        "plan": _plan(plan, insurance),
        "call_script": tools.call_script(d["id"], lang=lang)["call_script"],
        "controlled_message": community.CONTROLLED_MESSAGE if controlled else None,
        "holidays": tools.upcoming_holidays(7, when),
        "checked_at": when.strftime("%Y-%m-%d %H:%M"), "pharmacies": with_languages(pharms),
        "reminder": community.CALL_TO_CONFIRM, "report_window_hours": community.REPORT_WINDOW_HOURS,
        "sample_data": sample_data.enabled(),
    }


# ----------------------------------------------------------------------------- community page
@router.get("/community")
def community_feed() -> dict:
    """Latest stock reports (last 72 hours) and reviews across all pharmacies, with each pharmacy's neighborhood and
    average rating (real reviews only, from 3 reviews up) so the page can search and sort them. Real and sample
    posts stay apart."""
    names = _drug_names()
    pharms = {p["id"]: p for p in tools._pharmacies()}
    stats = community.review_stats_all()

    def label(x: dict) -> dict:
        p = pharms.get(x["pharmacy_id"], {})
        return x | {"pharmacy": p.get("name", x["pharmacy_id"]), "address": p.get("address", ""),
                    "neighborhood": p.get("neighborhood", ""), "drug": names.get(x.get("drug_id"), x.get("drug_id")),
                    "pharmacy_rating": stats.get(x["pharmacy_id"], {}).get("average_rating")}

    return {"reports": [label(x) for x in community.latest_reports(limit=300)],
            "reviews": [label(x) for x in community.latest_reviews(limit=200)],
            "sample_reports": [label(x) for x in sample_data.reports()],
            "sample_reviews": [label(x) for x in sample_data.reviews()],
            "sample_data": sample_data.enabled(), "window_hours": community.REPORT_WINDOW_HOURS,
            "reminder": community.CALL_TO_CONFIRM}


# ----------------------------------------------------------------------------- vaccines
@router.get("/vaccines")
def vaccines() -> dict:
    """Each vaccine, which pharmacies list it on their own pages (with booking links), and coverage by insurance."""
    pharms = tools._pharmacies()
    out = []
    for v in tools._rows("SELECT * FROM vaccines"):
        label = next((k for k, vid in tools.VACCINE_IDS.items() if vid == v["id"]), v["name"])
        offering = [{"id": p["id"], "name": p["name"], "address": p["address"], "neighborhood": p["neighborhood"],
                     "phone": p["phone"], "latitude": p["latitude"], "longitude": p["longitude"],
                     "booking_url": p["vaccine_booking_url"]}
                    for p in pharms if any(label.lower() in x.lower()
                                           for x in _list(p["vaccines_routine"]) + _list(p["vaccines_travel"]))]
        out.append({"id": v["id"], "name": v["name"], "group": v["vaccine_group"],
                    "pharmacies": offering, "medicare": tools._j(v["medicare"]), "masshealth": tools._j(v["masshealth"]),
                    "commercial": tools._j(v["commercial"]), "notes": tools._j(v["notes"]),
                    "certified_sites_only": bool(v["certified_sites_only"]), "clinic_finder": v["clinic_finder"],
                    "checked_date": v["checked_date"]})
    return {"vaccines": out,
            "note": "Pharmacies are listed only if their own page names the vaccine. Others may still offer it."}


@router.get("/other-drug")
def other_drug(name: str, lang: str = "en") -> dict:
    """A medicine that is not in RxLantern's list: live FDA shortage status (openFDA, saved for 24 hours) and a call
    script. This is the one page route that calls an outside API, because there is no saved data for such a medicine.
    Coverage and cost are not shown: those exist only for the medicines in the list."""
    return tools.other_drug_shortage(name[:60], "es" if lang == "es" else "en")


@router.get("/drugs/{drug_id}/call-script")
def drug_call_script(drug_id: str, lang: str = "en") -> dict:
    return tools.call_script(drug_id, lang=lang)


# ----------------------------------------------------------------------------- about & privacy
def _savings_checked() -> str:
    path = config.DATA_DIR / "savings.json"
    return json.loads(path.read_text(encoding="utf-8")).get("checked_date", tools.NF) if path.exists() else tools.NF


@router.get("/about")
def about() -> dict:
    """Where every piece of data comes from, with the date it was checked."""
    def first(sql: str):
        rows = tools._rows(sql)
        return rows[0] if rows else {}
    ph = first("SELECT MAX(checked_date) AS d FROM pharmacies")
    dr = first("SELECT MAX(checked_date) AS d FROM drugs")
    na = first("SELECT MAX(as_of_date) AS as_of, MAX(checked_date) AS d, MAX(source_file) AS src FROM nadac_prices")
    mh = first("SELECT MAX(list_last_updated) AS upd, MAX(checked_date) AS d FROM masshealth")
    va = first("SELECT MAX(checked_date) AS d FROM vaccines")
    zp = first("SELECT MAX(checked_date) AS d, MAX(source) AS src FROM zip_centroids")
    md = json.loads((config.DATA_DIR / "medicare" / "source.json").read_text(encoding="utf-8"))
    sh = [tools.shortage_from_db(r["id"]) for r in tools._rows("SELECT id FROM drugs")]
    return {"app_name": config.APP_NAME, "sources": [
        {"key": "pharmacies", "source": "Each pharmacy's own website or store page (20 Boston pharmacies)",
         "url": None, "checked_date": ph.get("d")},
        {"key": "drugs", "source": "RxNorm, National Library of Medicine (150 drugs)",
         "url": "https://rxnav.nlm.nih.gov/", "checked_date": dr.get("d")},
        {"key": "shortages", "source": "FDA Drug Shortages (openFDA), refreshed in the background at most once a day",
         "url": tools.SHORTAGE_PAGE, "checked_date": max((s["checked_date"] for s in sh), default=tools.NF)},
        {"key": "nadac", "source": f"NADAC (National Average Drug Acquisition Cost), Medicaid.gov, prices as of {na.get('as_of')}",
         "url": "https://data.medicaid.gov/", "checked_date": na.get("d")},
        {"key": "masshealth", "source": f"MassHealth Drug List (list updated {mh.get('upd')})",
         "url": "https://mhdl.pharmacy.services.conduent.com/MHDL/", "checked_date": mh.get("d")},
        {"key": "medicare", "source": f"CMS Medicare Part D plan files: {md.get('dataset', '')}",
         "url": "https://data.cms.gov/", "checked_date": md.get("checked_date")},
        {"key": "vaccines", "source": "CDC, CMS, Medicare.gov, and Mass.gov (including Bulletin 2025-03)",
         "url": "https://www.mass.gov/info-details/dph-recommended-guidance-for-vaccines", "checked_date": va.get("d")},
        {"key": "insurance", "source": "Each insurance plan's own website (pharmacy finders and member services numbers)",
         "url": None, "checked_date": _plans()["checked_date"]},
        {"key": "zips", "source": "U.S. Census Bureau ZIP code (ZCTA) center points",
         "url": (zp.get("src") or "").split(" ; ")[0] or None, "checked_date": zp.get("d")},
        {"key": "savings", "source": "GoodRx drug-page sitemap and TrumpRx.gov medication list (links only, no prices); "
                                     "each brand's official website for manufacturer savings programs",
         "url": "https://trumprx.gov/browse", "checked_date": _savings_checked()},
        {"key": "holidays", "source": "U.S. federal holidays (OPM) and Massachusetts legal holidays (Mass.gov)",
         "url": tools.HOLIDAY_SOURCE.split(" ; ")[0], "checked_date": "2026-10-23"},
    ], "plans": _plans()["plans"], "sample_data": sample_data.enabled()}
