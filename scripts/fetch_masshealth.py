"""Fetch MassHealth Drug List (MHDL) search results for our 25 drugs into data/raw/masshealth/.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe scripts\\fetch_masshealth.py
Then scripts\\build_masshealth.py turns the saved pages into data/masshealth.json.
"""

import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "masshealth"
MHDL = "https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RxLantern student project"}

# Search words typed into the MHDL search box (brand or generic, whichever the list uses).
SEARCH = {
    "adderall_xr_30": ["amphetamine"], "concerta_18": ["methylphenidate"], "atorvastatin_20": ["atorvastatin"],
    "lisinopril_10": ["lisinopril"], "levothyroxine_50": ["levothyroxine"], "metformin_500": ["metformin"],
    "amlodipine_5": ["amlodipine"], "omeprazole_20": ["omeprazole"], "sertraline_50": ["sertraline"],
    "amoxicillin_500": ["amoxicillin"], "ozempic_05": ["semaglutide"], "mounjaro_5": ["tirzepatide"],
    "eliquis_5": ["apixaban"], "humira_40": ["adalimumab"], "dupixent_300": ["dupilumab"],
    "albuterol_hfa": ["albuterol"], "lantus_solostar": ["insulin glargine"], "amoxicillin_susp_400": ["amoxicillin"],
    "sumatriptan_50": ["sumatriptan"], "latanoprost_0005": ["latanoprost"], "fluticasone_nasal_50": ["fluticasone"],
    "triamcinolone_cream_01": ["triamcinolone"], "epinephrine_03": ["epinephrine"], "nicotine_patch_21": ["nicotine"],
    "paxlovid": ["nirmatrelvir"],
}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    terms = sorted({t for ts in SEARCH.values() for t in ts})
    with httpx.Client(timeout=60, headers=UA, follow_redirects=True) as c:
        for t in terms:
            r = c.get(MHDL, params={"searchFor": t})
            r.raise_for_status()
            (RAW / f"{t.replace(' ', '_')}.html").write_text(r.text, encoding="utf-8")
            print(t, r.status_code, len(r.text))
    (RAW / "search_terms.json").write_text(json.dumps(SEARCH, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
