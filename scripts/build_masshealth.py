"""Build data/masshealth.json from saved MassHealth Drug List (MHDL) search pages.

Run from rxcompass/:
  ..\\.venv\\Scripts\\python.exe scripts\\fetch_masshealth.py   (saves pages to data/raw/masshealth/)
  ..\\.venv\\Scripts\\python.exe scripts\\build_masshealth.py
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mh_parse import rows  # noqa: E402

RAW = ROOT / "data" / "raw" / "masshealth"
OUT = ROOT / "data" / "masshealth.json"
SEARCH_URL = "https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor="

# Footnote codes, quoted (shortened) from the MHDL footnotes shown under every search result.
CODES = {
    "#": "Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice.",
    "BP": "Brand preferred over generics: MassHealth wants the brand tried first.",
    "PD": "Preferred drug in its class.",
    "M90": "Mandatory 90-day supply after a first fill of up to 30 days.",
    "A90": "Up to a 90-day supply is allowed.",
    "*": "The generic OTC (and generic prescription) versions are payable without PA.",
    "MB": "Given by a health care professional; not paid at a retail pharmacy.",
}

# Which MHDL row(s) apply to our exact drug. Pattern is matched against the drug column.
PICK = {
    "adderall_xr_30": ("amphetamine", [r"^Adderall XR ", r"^amphetamine salts extended-release;"]),
    "concerta_18": ("methylphenidate", [r"^Concerta "]),
    "atorvastatin_20": ("atorvastatin", [r"^Lipitor \(atorvastatin 10 mg, 20 mg, 40 mg tablet\)"]),
    "lisinopril_10": ("lisinopril", [r"^lisinopril$", r"^Zestril "]),
    "levothyroxine_50": ("levothyroxine", [r"^levothyroxine$", r"^Synthroid "]),
    "metformin_500": ("metformin", [r"^metformin immediate-release 500 mg"]),
    "amlodipine_5": ("amlodipine", [r"^Norvasc \(amlodipine tablet\)"]),
    "omeprazole_20": ("omeprazole", [r"^omeprazole 20 mg capsule"]),
    "sertraline_50": ("sertraline", [r"^Zoloft \(sertraline oral concentrate, tablet\)"]),
    "amoxicillin_500": ("amoxicillin", [r"^amoxicillin$"]),
    "ozempic_05": ("semaglutide", [r"^Ozempic "]),
    "mounjaro_5": ("tirzepatide", [r"^Mounjaro "]),
    "eliquis_5": ("apixaban", [r"^Eliquis "]),
    "humira_40": ("adalimumab", [r"^Humira \(adalimumab\)", r"^Hadlima ", r"^adalimumab-adaz, unbranded"]),
    "dupixent_300": ("dupilumab", [r"^Dupixent "]),
    "albuterol_hfa": ("albuterol", [r"^albuterol inhaler$", r"^Ventolin \(albuterol inhaler"]),
    "lantus_solostar": ("insulin_glargine", [r"^Lantus "]),
    "amoxicillin_susp_400": ("amoxicillin", [r"^amoxicillin$"]),
    "sumatriptan_50": ("sumatriptan", [r"^Imitrex \(sumatriptan tablet\)"]),
    "latanoprost_0005": ("latanoprost", [r"^Xalatan "]),
    "fluticasone_nasal_50": ("fluticasone", [r"^fluticasone propionate 50 mcg nasal spray"]),
    "triamcinolone_cream_01": ("triamcinolone", [r"^triamcinolone 0\.1% cream$"]),
    "epinephrine_03": ("epinephrine", [r"^epinephrine auto-injection$", r"^Epipen \(epinephrine 0\.3 mg"]),
    "nicotine_patch_21": ("nicotine", [r"^nicotine gum, lozenge, patch"]),
    "paxlovid": ("nirmatrelvir", [r"^Paxlovid \(nirmatrelvir / ritonavir 300-100 mg\)"]),
}

# Plain-language notes a pharmacist reviewed against the rows above (no medical advice).
EXTRA_NOTES = {
    "atorvastatin_20": "Generic atorvastatin is covered. PA is needed only above 1.5 tablets a day. Brand Lipitor needs PA.",
    "amlodipine_5": "Generic amlodipine is covered without PA. Brand Norvasc needs PA.",
    "sertraline_50": "Generic sertraline tablets are covered; PA is needed for children under 6. Brand Zoloft needs PA.",
    "sumatriptan_50": "Generic sumatriptan tablets are covered up to 16 tablets per 30 days; more needs PA. Brand Imitrex needs PA.",
    "latanoprost_0005": "Generic latanoprost is covered without PA. Brand Xalatan needs PA.",
    "albuterol_hfa": "Ventolin HFA (brand) is the preferred inhaler with no PA. Other albuterol HFA inhalers need PA.",
    "humira_40": "Humira needs PA. Hadlima and unbranded adalimumab-adaz are the preferred adalimumab products (also PA).",
    "lantus_solostar": "Lantus (brand) is preferred and covered without PA. Other insulin glargine products need PA.",
    "concerta_18": "Brand Concerta is preferred over generics. PA is needed for ages under 3 or 21 and older, or above 2 tablets a day.",
    "adderall_xr_30": "Covered. PA is needed for ages under 3 or 21 and older, or above 2 capsules a day.",
    "nicotine_patch_21": "Generic nicotine patches (OTC) are payable without PA.",
    "epinephrine_03": "Generic epinephrine auto-injectors are covered without PA. Brand EpiPen needs PA.",
    "paxlovid": "Covered. PA is needed for children under 12, or above 30 tablets per claim.",
    "fluticasone_nasal_50": "Covered. PA is needed above 1 bottle per 30 days.",
    "omeprazole_20": "Covered. PA is needed above 4 capsules a day.",
}


def pa_text(cell: str) -> str:
    if not cell:
        return "no"
    if cell.strip() == "PA":
        return "yes"
    return "only in some cases: " + re.sub(r"^PA\s*", "", cell).replace(" and PA ", "; or ").replace("≥", ">=")


def main() -> None:
    page = (RAW / "atorvastatin.html").read_text(encoding="utf-8")
    updated = re.search(r"Last updated\s*([\d/]+)", page)
    out = []
    for drug_id, (term, patterns) in PICK.items():
        table = rows(RAW / f"{term}.html")
        picked = [r for r in table if any(re.search(p, r[0]) for p in patterns)]
        url = SEARCH_URL + term.replace("_", "+")
        if not picked:
            out.append({"drug_id": drug_id, "covered": "not found", "prior_authorization": "not found",
                        "notes": ["Not on the MassHealth Drug List search. The list says any drug not on it requires PA."],
                        "mhdl_rows": [], "source": url, "checked_date": date.today().isoformat()})
            continue
        main_row = next((r for r in picked if re.search(patterns[0], r[0])), picked[0])
        codes = [c.strip() for c in main_row[3].split(",") if c.strip()]
        notes = [EXTRA_NOTES[drug_id]] if drug_id in EXTRA_NOTES else []
        notes += [f"{c}: {CODES[c]}" for c in codes if c in CODES]
        out.append({
            "drug_id": drug_id,
            "covered": "yes (on the MassHealth Drug List)",
            "prior_authorization": pa_text(main_row[1]),
            "drug_class": main_row[2],
            "notes": notes,
            "mhdl_rows": [{"drug": r[0], "pa_status": r[1] or "(none)", "class": r[2], "codes": r[3]} for r in picked],
            "source": url,
            "checked_date": date.today().isoformat(),
        })
        print(f"{drug_id:22} PA={out[-1]['prior_authorization'][:60]:60} codes={codes}")
    OUT.write_text(json.dumps({
        "source": "MassHealth Drug List (Executive Office of Health and Human Services)",
        "source_url": "https://mhdl.pharmacy.services.conduent.com/MHDL/",
        "list_last_updated": updated.group(1) if updated else "not found",
        "checked_date": date.today().isoformat(),
        "general_rules": [
            "Any drug that does not appear on the MassHealth Drug List requires prior authorization (PA).",
            "PA applies to both the brand-name drug and its FDA A-rated generic for listed products.",
            "Members in a MassHealth ACO or MCO plan: the same unified pharmacy list applies to most drugs.",
        ],
        "vaccines_rule": ("MassHealth does not pay for vaccines that are free through local boards of health or the "
                          "Massachusetts Department of Public Health (130 CMR 406.413(C)). MassHealth pays pharmacies "
                          "for seasonal flu vaccine without PA if the vaccine is not available free of cost. "
                          "(MassHealth Drug List footnote 1)"),
        "drugs": out,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
