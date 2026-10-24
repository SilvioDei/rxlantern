"""Build data/masshealth.json from saved MassHealth Drug List (MHDL) search pages, for all of RxLantern's drugs.

The 25 Step 3 drugs use the hand-checked row patterns in PICK. The drugs added in Step 7c use OVERRIDE when a
pharmacist-checked pattern is needed, otherwise auto_pick(): the brand's own row for brand-only products (Wegovy,
Victoza, ...), else the generic row whose wording best fits our dosage form. Every MHDL row used is saved in
"mhdl_rows" so it can be checked, and new drugs carry "match": "rule-based" for review.

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
from build_drugs import BRAND_ONLY  # noqa: E402
from fetch_masshealth import search_terms  # noqa: E402

# When the MHDL website could not be reached, a drug without a saved page keeps its earlier checked result (if any);
# otherwise it gets this status. Never a guess.
NOT_CHECKED = "not checked yet: the MassHealth Drug List website was unavailable on {date}"

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


# Step 7c drugs whose MHDL row needs a fixed pattern (checked by hand against the saved pages).
OVERRIDE: dict[str, list[str]] = {}

# Words in an MHDL row that tell its dosage form, and the words that mean "a different form".
FORMS = {
    "suspension": ["suspension", "liquid", "oral solution", "syrup"], "solution": ["solution", "liquid", "syrup"],
    "inhaler": ["inhaler", "inhalation", "diskus", "ellipta", "handihaler", "aerosol"],
    "nebulizer": ["inhalation solution", "inhalation suspension", "nebuliz", "respules"],
    "pen": ["pen", "injector", "injection", "kwikpen", "flexpen", "solostar", "flextouch"],
    "injection": ["injection", "vial", "syringe"], "cream": ["cream"], "ointment": ["ointment"], "gel": ["gel"],
    "patch": ["patch", "transdermal"], "nasal": ["nasal"], "eye": ["ophthalmic", "eye"], "film": ["film"],
    "chewable": ["chewable"], "disintegrating": ["disintegrating", "odt"],
    "tablet": ["tablet"], "capsule": ["capsule"],
}
ORAL_SOLID = ("tablet", "capsule")
OTHER_FORM_WORDS = ["suspension", "solution", "syrup", "injection", "cream", "ointment", "gel", "patch", "nasal",
                    "ophthalmic", "inhaler", "inhalation", "chewable", "film", "lotion", "foam", "suppository",
                    "extended-release", "delayed-release"]


def form_key(d: dict) -> str:
    f = d["dosage_form"].lower()
    for k in ("nebulizer", "inhaler", "suspension", "solution", "chewable", "disintegrating", "film", "patch", "cream",
              "ointment", "gel", "nasal", "eye", "pen", "injection", "capsule", "tablet"):
        if k in f or (k == "pen" and "auto-injector" in f) or (k == "inhaler" and "inhalation" in f):
            return k
    return "tablet"


def auto_pick(d: dict, table: list[list[str]], term: str) -> list[list[str]]:
    """The MHDL row(s) for a Step 7c drug, by simple rules (see the module docstring)."""
    brands = [b for b in (d["brand_names"] if isinstance(d["brand_names"], list) else []) if len(b) > 2]
    term = term.replace("_", " ").lower()
    want = form_key(d)
    extended = "extended" in d["dosage_form"] or "ER " in d["display_name"] or " XL " in d["display_name"]
    combo = " / " in d["rxnorm_generic"][0]["name"] and not d["id"].startswith("adderall")
    scored = []
    for r in table:
        name = r[0].lower()
        if d["id"] in BRAND_ONLY:
            if not name.startswith(BRAND_ONLY[d["id"]].lower().split()[0]):
                continue
            score = 10
        elif name.startswith(term):
            score = 6
        elif any(name.startswith(b.lower()) for b in brands) and term in name:
            score = 4
        else:
            continue
        if ("/" in name or " and " in name) != combo:
            score -= 5
        words = FORMS.get(want, [])
        if any(w in name for w in words):
            score += 2
        elif want in ORAL_SOLID and any(w in name for w in OTHER_FORM_WORDS if w not in ("extended-release", "delayed-release")):
            score -= 3
        elif want not in ORAL_SOLID and any(w in name for w in OTHER_FORM_WORDS):
            score -= 2
        if ("extended-release" in name or " er" in name or " xl" in name or " xr" in name) != extended:
            score -= 2
        scored.append((score, -len(name), r))
    if not scored:
        return []
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best = scored[0][0]
    return [r for sc, _, r in scored if sc == best][:2] if best > 0 else []


def pa_text(cell: str) -> str:
    if not cell:
        return "no"
    if cell.strip() == "PA":
        return "yes"
    return "only in some cases: " + re.sub(r"^PA\s*", "", cell).replace(" and PA ", "; or ").replace("≥", ">=")


def main() -> None:
    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"drugs": []}
    kept = {x["drug_id"]: x for x in previous["drugs"] if not str(x.get("covered", "")).startswith("not checked yet")}
    pages = [p for p in RAW.glob("*.html") if not p.name.startswith("vax_")] if RAW.exists() else []
    updated_text = None
    for p in pages:
        m = re.search(r"Last updated\s*([\d/]+)", p.read_text(encoding="utf-8"))
        if m:
            updated_text = m.group(1)
            break
    out = []
    drugs = json.loads((ROOT / "data" / "drugs.json").read_text(encoding="utf-8"))["drugs"]
    terms = search_terms()
    for d in drugs:
        drug_id = d["id"]
        match = "hand-checked (Step 3)"
        if drug_id in PICK:
            term, patterns = PICK[drug_id]
        else:
            term = terms[drug_id].replace(" ", "_")
            patterns = OVERRIDE.get(drug_id, [])
            match = "hand-checked (Step 7c)" if patterns else "rule-based (Step 7c): please review"
        if not (RAW / f"{term}.html").exists():
            if drug_id in kept:  # earlier checked result (e.g. the 25 Step 3 drugs, checked 2026-10-23)
                out.append(kept[drug_id])
                print(f"{drug_id:28} kept the earlier result (checked {kept[drug_id]['checked_date']})")
            else:
                status = NOT_CHECKED.format(date=date.today().isoformat())
                out.append({"drug_id": drug_id, "covered": status, "prior_authorization": status,
                            "notes": ["MassHealth coverage not checked yet. Call the pharmacy or MassHealth to confirm."],
                            "mhdl_rows": [], "match": "not checked", "source": SEARCH_URL + term.replace("_", "+"),
                            "checked_date": date.today().isoformat()})
                print(f"{drug_id:28} NOT CHECKED (no saved MHDL page)")
            continue
        table = rows(RAW / f"{term}.html")
        if patterns:
            picked = [r for r in table if any(re.search(p, r[0]) for p in patterns)]
        else:
            picked = auto_pick(d, table, term)
            patterns = ["^" + re.escape(picked[0][0]) + "$"] if picked else []
        url = SEARCH_URL + term.replace("_", "+")
        if not picked:
            out.append({"drug_id": drug_id, "covered": "not found", "prior_authorization": "not found",
                        "notes": ["Not on the MassHealth Drug List search. The list says any drug not on it requires PA."],
                        "mhdl_rows": [], "match": match, "source": url, "checked_date": date.today().isoformat()})
            print(f"{drug_id:28} NOT FOUND  ({len(table)} rows on the '{term}' page)")
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
            "match": match,
            "source": url,
            "checked_date": date.today().isoformat(),
        })
        print(f"{drug_id:28} {main_row[0][:70]:70} | PA={out[-1]['prior_authorization'][:40]} codes={codes}")
    OUT.write_text(json.dumps({
        "source": "MassHealth Drug List (Executive Office of Health and Human Services)",
        "source_url": "https://mhdl.pharmacy.services.conduent.com/MHDL/",
        "list_last_updated": updated_text or previous.get("list_last_updated", "not found"),
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
