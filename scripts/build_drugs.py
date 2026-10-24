"""Build data/drugs.json: our 25 drugs matched to RxNorm (NLM) names, RxCUIs, and NDCs.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe scripts\\build_drugs.py
Uses the free RxNav REST API (https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html). No key needed.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import httpx

RXNAV = "https://rxnav.nlm.nih.gov/REST"
OUT = Path(__file__).resolve().parent.parent / "data" / "drugs.json"

# id, display name, category, search term, regex for the generic RxNorm concept(s) (SCD or GPCK),
# strength, dosage form, controlled schedule, and the amount used for 30-day cost estimates
# (units are NADAC pricing units: EA = each, ML, GM).
DRUGS = [
    ("adderall_xr_30", "Adderall XR 30 mg ER capsule", "controlled", "amphetamine",
     r"^24 HR amphetamine aspartate 7\.5 MG / amphetamine sulfate 7\.5 MG / dextroamphetamine saccharate 7\.5 MG / dextroamphetamine sulfate 7\.5 MG Extended Release Oral Capsule$",
     "30 mg (mixed amphetamine salts)", "extended-release capsule", "C-II", {"units": 30, "nadac_unit": "EA", "basis": "30 capsules (1 a day)"}),
    ("concerta_18", "Concerta 18 mg ER tablet", "controlled", "methylphenidate",
     r"^24 HR methylphenidate hydrochloride 18 MG Extended Release Oral Tablet$",
     "18 mg", "extended-release tablet", "C-II", {"units": 30, "nadac_unit": "EA", "basis": "30 tablets (1 a day)"}),
    ("atorvastatin_20", "Atorvastatin 20 mg tablet", "common", "atorvastatin", r"^atorvastatin 20 MG Oral Tablet$",
     "20 mg", "tablet", None, {"units": 30, "nadac_unit": "EA", "basis": "30 tablets (1 a day)"}),
    ("lisinopril_10", "Lisinopril 10 mg tablet", "common", "lisinopril", r"^lisinopril 10 MG Oral Tablet$",
     "10 mg", "tablet", None, {"units": 30, "nadac_unit": "EA", "basis": "30 tablets (1 a day)"}),
    ("levothyroxine_50", "Levothyroxine 50 mcg tablet", "common", "levothyroxine", r"^levothyroxine sodium 0\.05 MG Oral Tablet$",
     "50 mcg", "tablet", None, {"units": 30, "nadac_unit": "EA", "basis": "30 tablets (1 a day)"}),
    ("metformin_500", "Metformin 500 mg tablet", "common", "metformin", r"^metformin hydrochloride 500 MG Oral Tablet$",
     "500 mg", "tablet", None, {"units": 60, "nadac_unit": "EA", "basis": "60 tablets (1 twice a day)"}),
    ("amlodipine_5", "Amlodipine 5 mg tablet", "common", "amlodipine", r"^amlodipine 5 MG Oral Tablet$",
     "5 mg", "tablet", None, {"units": 30, "nadac_unit": "EA", "basis": "30 tablets (1 a day)"}),
    ("omeprazole_20", "Omeprazole 20 mg DR capsule", "common", "omeprazole", r"^omeprazole 20 MG Delayed Release Oral Capsule$",
     "20 mg", "delayed-release capsule", None, {"units": 30, "nadac_unit": "EA", "basis": "30 capsules (1 a day)"}),
    ("sertraline_50", "Sertraline 50 mg tablet", "common", "sertraline", r"^sertraline 50 MG Oral Tablet$",
     "50 mg", "tablet", None, {"units": 30, "nadac_unit": "EA", "basis": "30 tablets (1 a day)"}),
    ("amoxicillin_500", "Amoxicillin 500 mg capsule", "common", "amoxicillin", r"^amoxicillin 500 MG Oral Capsule$",
     "500 mg", "capsule", None, {"units": 30, "nadac_unit": "EA", "basis": "30 capsules (a typical 10-day course, 3 a day)"}),
    ("ozempic_05", "Ozempic (semaglutide) 0.5 mg pen", "expensive", "semaglutide",
     r"^0\.25 MG, 0\.5 MG Dose 3 ML semaglutide 0\.68 MG/ML Pen Injector$",
     "0.5 mg per weekly dose (2 mg/3 mL pen)", "pen injector", None, {"units": 3, "nadac_unit": "ML", "basis": "1 pen (3 mL), about 1 month at 0.5 mg weekly"}),
    ("mounjaro_5", "Mounjaro (tirzepatide) 5 mg pen", "expensive", "tirzepatide", r"^0\.5 ML tirzepatide 10 MG/ML Auto-Injector$",
     "5 mg/0.5 mL", "single-dose pen (auto-injector)", None, {"units": 2, "nadac_unit": "ML", "basis": "4 single-dose pens (0.5 mL each), 1 a week"}),
    ("eliquis_5", "Eliquis (apixaban) 5 mg tablet", "expensive", "apixaban", r"^apixaban 5 MG Oral Tablet$",
     "5 mg", "tablet", None, {"units": 60, "nadac_unit": "EA", "basis": "60 tablets (1 twice a day)"}),
    ("humira_40", "Humira (adalimumab) 40 mg pen", "expensive", "adalimumab", r"^0\.4 ML adalimumab 100 MG/ML Auto-Injector$",
     "40 mg/0.4 mL", "pen (auto-injector)", None, {"units": 2, "nadac_unit": "EA", "basis": "2 pens (every other week)"}),
    ("dupixent_300", "Dupixent (dupilumab) 300 mg pen", "expensive", "dupilumab", r"^2 ML dupilumab 150 MG/ML Auto-Injector$",
     "300 mg/2 mL", "pen (auto-injector)", None, {"units": 4, "nadac_unit": "ML", "basis": "2 pens (2 mL each), every other week"}),
    ("albuterol_hfa", "Albuterol HFA 90 mcg inhaler", "other", "albuterol",
     r"^NDA0\d+ 200 ACTUAT albuterol 0\.09 MG/ACTUAT Metered Dose Inhaler$",
     "90 mcg per puff (200 puffs)", "metered-dose inhaler", None, {"units": 18, "nadac_unit": "GM", "basis": "1 inhaler (18 g size; some brands are 6.7 g or 8.5 g)"}),
    ("lantus_solostar", "Insulin glargine (Lantus SoloStar) pen", "other", "insulin glargine", r"^3 ML insulin glargine 100 UNT/ML Pen Injector$",
     "100 units/mL, 3 mL pen", "pen injector", None, {"units": 15, "nadac_unit": "ML", "basis": "1 box of 5 pens (3 mL each)"}),
    ("amoxicillin_susp_400", "Amoxicillin 400 mg/5 mL oral suspension", "other", "amoxicillin", r"^amoxicillin 80 MG/ML Oral Suspension$",
     "400 mg/5 mL", "oral suspension", None, {"units": 100, "nadac_unit": "ML", "basis": "1 bottle (100 mL)"}),
    ("sumatriptan_50", "Sumatriptan 50 mg tablet", "other", "sumatriptan", r"^sumatriptan 50 MG Oral Tablet$",
     "50 mg", "tablet", None, {"units": 9, "nadac_unit": "EA", "basis": "9 tablets"}),
    ("latanoprost_0005", "Latanoprost 0.005% eye drops", "other", "latanoprost", r"^latanoprost 0\.05 MG/ML Ophthalmic Solution$",
     "0.005% (50 mcg/mL)", "eye drops (solution)", None, {"units": 2.5, "nadac_unit": "ML", "basis": "1 bottle (2.5 mL)"}),
    ("fluticasone_nasal_50", "Fluticasone 50 mcg nasal spray", "other", "fluticasone",
     r"^(\d+ ACTUAT )?fluticasone propionate 0\.05 MG/ACTUAT (Metered Dose )?Nasal Spray$",
     "50 mcg per spray", "nasal spray", None, {"units": 16, "nadac_unit": "GM", "basis": "1 bottle (16 g, about 120 sprays)"}),
    ("triamcinolone_cream_01", "Triamcinolone 0.1% cream", "other", "triamcinolone", r"^triamcinolone acetonide 1 MG/ML Topical Cream$",
     "0.1%", "cream", None, {"units": 30, "nadac_unit": "GM", "basis": "1 tube (30 g)"}),
    ("epinephrine_03", "Epinephrine 0.3 mg auto-injector", "other", "epinephrine", r"^(A?NDA\d+ )?0\.3 ML epinephrine 1 MG/ML Auto-Injector$",
     "0.3 mg/0.3 mL", "auto-injector", None, {"units": 2, "nadac_unit": "EA", "basis": "1 two-pack of auto-injectors"}),
    ("nicotine_patch_21", "Nicotine 21 mg patch", "other", "nicotine", r"^24 HR nicotine 0\.875 MG/HR Transdermal System$",
     "21 mg/24 hours", "transdermal patch", None, {"units": 28, "nadac_unit": "EA", "basis": "28 patches"}),
    ("paxlovid", "Paxlovid dose pack", "other", "nirmatrelvir",
     r"^\{20 \(nirmatrelvir 150 MG Oral Tablet\) / 10 \(ritonavir 100 MG Oral Tablet\) \} Pack$",
     "nirmatrelvir 300 mg + ritonavir 100 mg twice daily", "dose pack (5 days)", None, {"units": 30, "nadac_unit": "EA", "basis": "1 five-day dose pack (30 tablets)"}),
]


# For brand-name items, keep only that brand's products (e.g. Mounjaro, not Zepbound, which shares
# the same RxNorm generic concept). Others keep every single-drug brand (SBD), not combination packs.
BRAND_ONLY = {"adderall_xr_30": "Adderall", "concerta_18": "Concerta", "ozempic_05": "Ozempic",
              "mounjaro_5": "Mounjaro", "eliquis_5": "Eliquis", "humira_40": "Humira", "dupixent_300": "Dupixent",
              "lantus_solostar": "Lantus", "paxlovid": "Paxlovid 5-Day"}


def get(client, path, **params):
    r = client.get(f"{RXNAV}{path}", params=params)
    r.raise_for_status()
    return r.json()


def concepts(client, term):
    d = get(client, "/drugs.json", name=term)
    out = []
    for g in (d.get("drugGroup", {}).get("conceptGroup") or []):
        for p in g.get("conceptProperties") or []:
            out.append({"rxcui": p["rxcui"], "name": p["name"], "tty": g["tty"]})
    return out


def related(client, rxcui, ttys):
    d = get(client, f"/rxcui/{rxcui}/related.json", tty=" ".join(ttys))
    out = []
    for g in d.get("relatedGroup", {}).get("conceptGroup") or []:
        for p in g.get("conceptProperties") or []:
            out.append({"rxcui": p["rxcui"], "name": p["name"], "tty": g["tty"]})
    return out


def ndcs(client, rxcui):
    d = get(client, f"/rxcui/{rxcui}/ndcs.json")
    return sorted(set((d.get("ndcGroup", {}).get("ndcList") or {}).get("ndc") or []))


def main():
    today = date.today().isoformat()
    drugs = []
    with httpx.Client(timeout=60) as c:
        for did, display, cat, term, pattern, strength, form, schedule, supply in DRUGS:
            all_c = concepts(c, term)
            generic = [x for x in all_c if x["tty"] in ("SCD", "GPCK") and re.search(pattern, x["name"])]
            if not generic:
                print(f"!! no RxNorm match for {did}", file=sys.stderr)
                drugs.append({"id": did, "display_name": display, "rxnorm": "not found"})
                continue
            brands, brand_names, products = [], set(), []
            for g in generic:
                g["ndcs"] = ndcs(c, g["rxcui"])
                want_tty = "BPCK" if g["tty"] == "GPCK" else "SBD"
                for b in related(c, g["rxcui"], [want_tty]):
                    if b["tty"] != want_tty or b["rxcui"] in {x["rxcui"] for x in brands}:
                        continue
                    if did in BRAND_ONLY and not b["name"].endswith(f"[{BRAND_ONLY[did]}]"):
                        continue
                    b["ndcs"] = ndcs(c, b["rxcui"])
                    brands.append(b)
                    m = re.search(r"\[([^\]]+)\]\s*$", b["name"])
                    if m:
                        brand_names.add(m.group(1))
                ing = related(c, g["rxcui"], ["IN", "MIN"])
                products.extend(i["name"] for i in ing)
            all_ndcs = sorted({n for x in generic + brands for n in x["ndcs"]})
            drugs.append({
                "id": did,
                "display_name": display,
                "category": cat,
                "generic_name": " / ".join(sorted(set(products))) or "not found",
                "brand_names": sorted(brand_names) or "not found",
                "strength": strength,
                "dosage_form": form,
                "controlled": schedule is not None,
                "dea_schedule": schedule or "not controlled",
                "rxnorm_generic": [{k: g[k] for k in ("rxcui", "tty", "name")} | {"ndc_count": len(g["ndcs"])} for g in generic],
                "rxnorm_brand": [{k: b[k] for k in ("rxcui", "tty", "name")} | {"ndc_count": len(b["ndcs"])} for b in brands],
                "rxcuis": [x["rxcui"] for x in generic + brands],
                "ndcs": all_ndcs,
                "typical_30_day_supply": supply,
                "shortage_search": term,
                "sources": {
                    "rxnorm": f"{RXNAV}/drugs.json?name={term.replace(' ', '+')}",
                    "ndcs": f"{RXNAV}/rxcui/<rxcui>/ndcs.json (one call per RxCUI listed)",
                    "brand_names": f"{RXNAV}/rxcui/<generic rxcui>/related.json?tty=SBD+BPCK",
                    "dea_schedule": "https://www.deadiversion.usdoj.gov/schedules/orangebook/c_cs_alpha.pdf" if schedule else None,
                    "typical_30_day_supply": "RxLantern assumption for cost estimates only (not a dosing instruction)",
                },
                "checked_date": today,
            })
            print(f"{did:22} generic={[g['rxcui'] for g in generic]} brands={sorted(brand_names)} ndcs={len(all_ndcs)}")
    OUT.write_text(json.dumps({"checked_date": today, "source": "RxNorm / RxNav API, U.S. National Library of Medicine",
                               "count": len(drugs), "drugs": drugs}, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
