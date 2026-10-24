"""MassHealth step in one command: fetch the MassHealth Drug List (MHDL) search pages for RxLantern's drugs, then
rebuild data/masshealth.json and output/medication_check.md, then delete the downloaded pages.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe scripts\\fetch_masshealth.py
  --fetch-only   only save the pages to data/raw/masshealth/ (no rebuild, pages kept)

If the MHDL website does not answer, nothing is changed and the script says so (run it again later).
After it finishes, restart the app (or run ..\\.venv\\Scripts\\python.exe -m backend.build_db) so the website uses the
new data. The search word is the drug's main ingredient (the RxNorm search term in data/drugs.json) unless SEARCH
says otherwise.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "masshealth"
MHDL = "https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RxLantern student project"}

# Search words typed into the MHDL search box when the RxNorm term is not the word the list uses.
SEARCH = {
    "paxlovid": "nirmatrelvir", "insulin_nph_pen": "insulin NPH", "penicillin_vk_500": "penicillin",
    "amox_clav_875": "amoxicillin", "amox_clav_susp_400": "amoxicillin", "advair_diskus_250": "salmeterol",
    "symbicort_160": "formoterol", "trelegy_100": "umeclidinium", "duoneb": "albuterol",
    "lantus_solostar": "insulin glargine", "toujeo_solostar": "insulin glargine", "humalog_kwikpen": "insulin lispro",
    "novolog_flexpen": "insulin aspart", "tresiba_flextouch": "insulin degludec", "testosterone_cyp_200": "testosterone",
    "norgestimate_ee": "norgestimate", "medroxyprogesterone_inj_150": "medroxyprogesterone",
    "buprenorphine_naloxone_8_2": "buprenorphine", "hydrocodone_apap_5_325": "hydrocodone",
    "oxycodone_apap_5_325": "oxycodone", "smx_tmp_ds": "sulfamethoxazole", "smx_tmp_susp": "sulfamethoxazole",
    "truvada_prep": "emtricitabine", "biktarvy": "bictegravir", "entresto_49_51": "sacubitril",
}


def search_terms() -> dict[str, str]:
    drugs = json.loads((ROOT / "data" / "drugs.json").read_text(encoding="utf-8"))["drugs"]
    out = {}
    for d in drugs:
        rx_term = re.search(r"name=([^&]+)$", d["sources"]["rxnorm"]).group(1).replace("+", " ")
        out[d["id"]] = SEARCH.get(d["id"], rx_term)
    return out


def fetch() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    search = search_terms()
    with httpx.Client(timeout=60, headers=UA, follow_redirects=True) as c:
        for t in sorted(set(search.values())):
            path = RAW / f"{t.replace(' ', '_')}.html"
            if path.exists():
                continue
            for attempt in range(3):
                try:
                    r = c.get(MHDL, params={"searchFor": t})
                    r.raise_for_status()
                    break
                except httpx.HTTPError:
                    if attempt == 2:
                        raise
                    time.sleep(5)
            if 'id="drug"' not in r.text and "No results" not in r.text and "no drugs" not in r.text.lower():
                print(f"warning: no result table on the page for '{t}'")
            path.write_text(r.text, encoding="utf-8")
            print(t, r.status_code, len(r.text))
            time.sleep(0.5)
    (RAW / "search_terms.json").write_text(json.dumps(search, indent=2), encoding="utf-8")


def main() -> int:
    try:
        fetch()
    except httpx.HTTPError as e:
        print(f"The MassHealth Drug List website did not answer ({type(e).__name__}). Nothing was changed. "
              "Please run this again later.")
        return 1
    if "--fetch-only" in sys.argv:
        return 0
    py = sys.executable
    for script in ("build_masshealth.py", "build_medication_check.py"):
        subprocess.run([py, str(ROOT / "scripts" / script)], check=True, cwd=ROOT)
    # The vaccine pages (vax_*.html) are kept only if build_vaccines.py needs them again; drug pages are removed.
    for f in RAW.glob("*.html"):
        if not f.name.startswith("vax_"):
            f.unlink()
    print("Done. Restart the app so the website uses the new MassHealth data.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
