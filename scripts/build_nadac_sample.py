"""Build data/nadac_sample.csv: latest weekly NADAC prices for our 150 drugs only.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe scripts\\build_nadac_sample.py [--download]

NADAC = National Average Drug Acquisition Cost (CMS / data.medicaid.gov): the average price
pharmacies pay to buy a drug. It is not what a patient pays at the counter.
The full yearly file (updated weekly) goes to data/raw/ (git-ignored); only matching rows are kept.
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "nadac_sample.csv"
CATALOG = "https://data.medicaid.gov/api/1/metastore/schemas/dataset/items?show-reference-ids=false"


def latest_nadac_url() -> tuple[str, str]:
    """Find the newest 'NADAC (National Average Drug Acquisition Cost) <year>' dataset."""
    items = httpx.get(CATALOG, timeout=120).json()
    best = None
    for ds in items:
        title = ds.get("title", "")
        if title.startswith("NADAC (National Average Drug Acquisition Cost) "):
            year = title.rsplit(" ", 1)[-1]
            if year.isdigit() and (best is None or int(year) > int(best[0])):
                url = (ds["distribution"][0].get("data") or ds["distribution"][0])["downloadURL"]
                best = (year, url, ds.get("modified", ""))
    return best[1], f"{best[0]} (catalog modified {best[2]})"


def main() -> None:
    url, label = latest_nadac_url()
    raw = RAW / Path(url).name
    if "--download" in sys.argv or not raw.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        print(f"downloading {url}")
        with httpx.stream("GET", url, timeout=600, follow_redirects=True) as r, open(raw, "wb") as f:
            r.raise_for_status()
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)

    drugs = json.loads((ROOT / "data" / "drugs.json").read_text(encoding="utf-8"))["drugs"]
    ndc_to_drug = {ndc: d["id"] for d in drugs for ndc in d["ndcs"]}

    with open(raw, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["NDC"].zfill(11) in ndc_to_drug]
    # The yearly file holds every week; keep only the newest weekly "As of Date".
    as_of = max(datetime.strptime(r["As of Date"], "%m/%d/%Y") for r in rows)
    latest = [r for r in rows if datetime.strptime(r["As of Date"], "%m/%d/%Y") == as_of]

    cols = ["drug_id", "ndc", "ndc_description", "nadac_per_unit", "pricing_unit", "effective_date",
            "as_of_date", "classification", "otc", "pharmacy_type", "source_file", "checked_date"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sorted(latest, key=lambda r: (ndc_to_drug[r["NDC"].zfill(11)], r["NDC"])):
            w.writerow({
                "drug_id": ndc_to_drug[r["NDC"].zfill(11)],
                "ndc": r["NDC"].zfill(11),
                "ndc_description": r["NDC Description"],
                "nadac_per_unit": r["NADAC Per Unit"],
                "pricing_unit": r["Pricing Unit"],
                "effective_date": r["Effective Date"],
                "as_of_date": r["As of Date"],
                "classification": r["Classification for Rate Setting"],
                "otc": r["OTC"],
                "pharmacy_type": r["Pharmacy Type Indicator"],
                "source_file": url,
                "checked_date": date.today().isoformat(),
            })
    found = sorted({ndc_to_drug[r["NDC"].zfill(11)] for r in latest})
    missing = [d["id"] for d in drugs if d["id"] not in found]
    print(f"NADAC {label}; as of {as_of:%m/%d/%Y}: {len(latest)} rows for {len(found)} drugs -> {OUT}")
    print("no NADAC rows:", missing or "none")


if __name__ == "__main__":
    main()
