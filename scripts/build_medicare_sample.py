"""Build small Massachusetts-only Medicare Part D files in data/medicare/ for our 150 drugs.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe scripts\\build_medicare_sample.py [--download]

Source: CMS "Quarterly Prescription Drug Plan Formulary, Pharmacy Network, and Pricing Information"
(data.cms.gov), newest 2026 release. The big zip (about 2.5 GB) goes to data/raw/ (git-ignored).
The pharmacy network files inside it are not needed and are skipped.

Outputs (all small):
  plans_ma.csv              one row per plan segment offered in Massachusetts (premium, deductible, ...)
  formulary_ma.csv          our drugs on those plans' formularies: tier, PA / step therapy / quantity limit
  cost_sharing_ma.csv       copay / coinsurance by tier for those plans
  insulin_cost_ma.csv       insulin cost sharing for those plans
  plan_drug_cost_ma.csv     each plan's price for a typical 30-day amount of each drug (from the pricing file)
  avg_monthly_cost_ma.csv   average of those plan prices per drug
  source.json               which file and date this came from
"""

import csv
import io
import json
import statistics
import sys
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "medicare"
CATALOG = "https://data.cms.gov/data.json"
TITLE = "Quarterly Prescription Drug Plan Formulary, Pharmacy Network, and Pricing Information"
PLAN_YEAR = "2026"


def newest_release() -> tuple[str, str]:
    """Newest release whose zip name is for plan year 2026 (SPUF_2026_*.zip)."""
    cat = httpx.get(CATALOG, timeout=120).json()
    best = None
    for ds in cat["dataset"]:
        if not ds["title"].startswith(TITLE):
            continue
        for dist in ds.get("distribution", []):
            url = dist.get("downloadURL") or ""
            if f"SPUF_{PLAN_YEAR}_" in url and (best is None or url.rsplit("_", 1)[-1] > best[0].rsplit("_", 1)[-1]):
                best = (url, ds["title"])
    return best


def rows_from(outer: zipfile.ZipFile, prefix: str):
    """Yield dict rows from the pipe-delimited text file inside the nested zip whose name starts with prefix."""
    name = next(n for n in outer.namelist() if n.lower().startswith(prefix))
    inner = zipfile.ZipFile(io.BytesIO(outer.read(name)))
    txt = next(n for n in inner.namelist() if n.lower().endswith(".txt"))
    with inner.open(txt) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter="|")


def write(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


def main() -> None:
    url, title = newest_release()
    raw = RAW / Path(url).name
    if "--download" in sys.argv or not raw.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        print(f"downloading {url} (about 2.5 GB)")
        with httpx.stream("GET", url, timeout=3600, follow_redirects=True) as r, open(raw, "wb") as f:
            r.raise_for_status()
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
    print(f"reading {raw.name} ({title})")

    drugs = json.loads((ROOT / "data" / "drugs.json").read_text(encoding="utf-8"))["drugs"]
    rxcui_to_drug = {rx: d["id"] for d in drugs for rx in d["rxcuis"]}
    ndc_to_drug = {n: d["id"] for d in drugs for n in d["ndcs"]}
    supply = {d["id"]: d["typical_30_day_supply"] for d in drugs}

    outer = zipfile.ZipFile(raw)

    # Counties in Massachusetts, from the geographic locator file.
    ma_counties = {r["COUNTY_CODE"]: r["COUNTY"] for r in rows_from(outer, "geographic locator")
                   if r.get("STATENAME", "").strip().lower() == "massachusetts"}
    ma_pdp_regions = {r["PDP_REGION_CODE"] for r in rows_from(outer, "geographic locator")
                      if r.get("STATENAME", "").strip().lower() == "massachusetts"}

    # Plans available in Massachusetts: MA-PD plans by county; stand-alone PDPs by PDP region.
    plans: dict[tuple, dict] = {}
    for r in rows_from(outer, "plan information"):
        if r["PLAN_SUPPRESSED_YN"] == "Y":
            continue
        is_pdp = r["CONTRACT_ID"].startswith("S")
        in_ma = (r["PDP_REGION_CODE"].strip() in ma_pdp_regions) if is_pdp else (r["COUNTY_CODE"] in ma_counties)
        if not in_ma:
            continue
        key = (r["CONTRACT_ID"], r["PLAN_ID"], r["SEGMENT_ID"])
        p = plans.setdefault(key, {
            "contract_id": r["CONTRACT_ID"], "plan_id": r["PLAN_ID"], "segment_id": r["SEGMENT_ID"],
            "contract_name": r["CONTRACT_NAME"].strip(), "plan_name": r["PLAN_NAME"].strip(),
            "plan_type": "PDP (stand-alone drug plan)" if is_pdp else "Medicare Advantage with drug coverage",
            "formulary_id": r["FORMULARY_ID"], "premium": r["PREMIUM"].strip(), "deductible": r["DEDUCTIBLE"].strip(),
            "snp": r["SNP"].strip(), "counties": set(),
        })
        p["counties"].add("all (statewide PDP region)" if is_pdp else ma_counties[r["COUNTY_CODE"]])
    plan_rows = []
    for p in plans.values():
        c = p.pop("counties")
        p["ma_counties"] = "; ".join(sorted(c))
        p["available_in_boston"] = "Y" if (p["plan_type"].startswith("PDP") or any("suffolk" in x.lower() for x in c)) else "N"
        plan_rows.append(p)
    plan_rows.sort(key=lambda p: (p["plan_type"], p["contract_id"], p["plan_id"], p["segment_id"]))
    formularies = {p["formulary_id"] for p in plan_rows}
    plan_keys = set(plans)
    print(f"{len(plan_rows)} plan segments, {len(formularies)} formularies in Massachusetts")

    form_rows, seen = [], set()
    for r in rows_from(outer, "basic drugs formulary"):
        if r["FORMULARY_ID"] in formularies and r["RXCUI"] in rxcui_to_drug:
            k = (r["FORMULARY_ID"], r["RXCUI"])
            if k in seen:
                continue
            seen.add(k)
            form_rows.append({
                "formulary_id": r["FORMULARY_ID"], "drug_id": rxcui_to_drug[r["RXCUI"]], "rxcui": r["RXCUI"],
                "tier": r["TIER_LEVEL_VALUE"], "prior_auth": r["PRIOR_AUTHORIZATION_YN"],
                "step_therapy": r["STEP_THERAPY_YN"], "quantity_limit": r["QUANTITY_LIMIT_YN"],
                "quantity_limit_amount": r["QUANTITY_LIMIT_AMOUNT"].strip(), "quantity_limit_days": r["QUANTITY_LIMIT_DAYS"].strip(),
                "selected_drug": r.get("SELECTED_DRUG_YN", ""),
            })

    def keyed(prefix):
        return [r for r in rows_from(outer, prefix) if (r["CONTRACT_ID"], r["PLAN_ID"], r["SEGMENT_ID"]) in plan_keys]

    cost_rows = [{k.lower(): v.strip() for k, v in r.items()} for r in keyed("beneficiary cost")]
    insulin_rows = [{k.lower(): v.strip() for k, v in r.items()} for r in keyed("insulin beneficiary cost")]

    # Pricing: each plan's unit cost per NDC (30-day supply). Keep the lowest-cost NDC per plan and drug.
    best = {}
    for r in rows_from(outer, "pricing file"):
        if r["DAYS_SUPPLY"] != "30" or r["NDC"] not in ndc_to_drug:
            continue
        pk = (r["CONTRACT_ID"], r["PLAN_ID"], r["SEGMENT_ID"])
        if pk not in plan_keys:
            continue
        did = ndc_to_drug[r["NDC"]]
        cost = float(r["UNIT_COST"])
        k = pk + (did,)
        if k not in best or cost < best[k][0]:
            best[k] = (cost, r["NDC"])
    plan_cost_rows = []
    per_drug = defaultdict(list)
    for (c, p, s, did), (unit, ndc) in sorted(best.items()):
        est = unit * supply[did]["units"]
        plan_cost_rows.append({"contract_id": c, "plan_id": p, "segment_id": s, "drug_id": did, "ndc": ndc,
                               "unit_cost": f"{unit:.4f}", "units": supply[did]["units"],
                               "est_30_day_cost": f"{est:.2f}", "basis": supply[did]["basis"]})
        per_drug[did].append(est)
    avg_rows = [{"drug_id": did, "plans_with_price": len(v), "avg_30_day_cost": f"{statistics.mean(v):.2f}",
                 "min_30_day_cost": f"{min(v):.2f}", "max_30_day_cost": f"{max(v):.2f}",
                 "basis": supply[did]["basis"]} for did, v in sorted(per_drug.items())]

    write("plans_ma.csv", plan_rows)
    write("formulary_ma.csv", form_rows)
    write("cost_sharing_ma.csv", cost_rows)
    write("insulin_cost_ma.csv", insulin_rows)
    write("plan_drug_cost_ma.csv", plan_cost_rows)
    write("avg_monthly_cost_ma.csv", avg_rows)
    (OUT / "source.json").write_text(json.dumps({
        "dataset": title, "file": url, "plan_year": PLAN_YEAR, "checked_date": date.today().isoformat(),
        "filters": "Plans offered in Massachusetts (MA-PD by county, PDP by region); only RxLantern's 150 drugs.",
        "note": "Plan unit costs are what the plan pays for the drug, not the member's share. Member share depends on tier "
                "(cost_sharing_ma.csv), deductible, and the 2026 $2,100 out-of-pocket cap.",
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
