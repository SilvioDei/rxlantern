"""Write output/medication_check.md: a "please review first" list, one section per drug, and vaccines,
for pharmacist review.

Run from the repository folder:  ..\\.venv\\Scripts\\python.exe scripts\\build_medication_check.py
Reads only the small files in data/.
"""

import collections
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MED = DATA / "medicare"
NF = "not found"
HIGH_COST = 1000.0   # NADAC 30-day estimates above this go on the review list
LOW_COST = 1.0       # ... and below this


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def money(x):
    return f"${x:,.2f}"


def main() -> None:
    drugs = load("drugs.json")
    shortages = {x["drug_id"]: x for x in load("shortages_snapshot.json")["drugs"]}
    snap_date = load("shortages_snapshot.json")["checked_date"]
    mh = load("masshealth.json")
    mh_by = {x["drug_id"]: x for x in mh["drugs"]}
    nadac = collections.defaultdict(list)
    for r in read_csv(DATA / "nadac_sample.csv"):
        nadac[r["drug_id"]].append(r)
    plans = read_csv(MED / "plans_ma.csv")
    formulary = read_csv(MED / "formulary_ma.csv")
    avg_cost = {r["drug_id"]: r for r in read_csv(MED / "avg_monthly_cost_ma.csv")}
    rules = json.loads((MED / "part_d_rules_2026.json").read_text(encoding="utf-8")) if (MED / "part_d_rules_2026.json").exists() else None

    plans_by_formulary = collections.defaultdict(list)
    for p in plans:
        plans_by_formulary[p["formulary_id"]].append(p)
    n_plans = len(plans)

    ls = drugs.get("list_source", {})
    ds = drugs.get("dea_schedule_source", {})
    out = ["# Medication data check", "",
           f"Checked: {drugs['checked_date']}. For pharmacist review. Every fact lists its source. "
           f"{len(drugs['drugs'])} drugs.", "",
           f"- **Drug list:** the 25 drugs from Step 3 plus 125 chosen from {ls.get('name', NF)} "
           f"(<{ls.get('url', NF)}>; data: {ls.get('underlying_data', NF)}; checked {ls.get('checked_date', NF)}), "
           "adding shortage-prone and high-cost medicines (GLP-1s, inhalers, insulins, children's antibiotic liquids, "
           "ADHD medicines). Names, RxCUIs, and NDCs from RxNorm (RxNav API).",
           f"- **DEA schedule:** from the {ds.get('name', NF)} (<{ds.get('url', NF)}>, last updated "
           f"{ds.get('last_updated', NF)}), matched by RxCUI and package NDC; never typed by hand.",
           "- **NADAC** is what pharmacies pay to buy the drug (CMS survey), not the patient's price. "
           "The 30-day estimate = NADAC per unit x the amount shown. It leaves out the pharmacy's dispensing fee and markup.",
           "- **Medicare counts** are Massachusetts Part D plans (stand-alone PDPs and Medicare Advantage drug plans) "
           f"in the CMS 2026 quarterly file; {n_plans} plan segments in total." if plans else
           "- **Medicare:** Massachusetts plan files not built yet.",
           f"- **MassHealth** status is from the MassHealth Drug List (last updated {mh['list_last_updated']}). "
           "Rule: any drug not on the list requires prior authorization (PA).",
           f"- **Shortage** status is from the openFDA drug shortages API (snapshot {snap_date}).", ""]
    if rules:
        out += ["## 2026 Medicare Part D rules", ""]
        for k, v in rules["rules"].items():
            out.append(f"- **{v['label']}:** {v['value'] if isinstance(v['value'], str) else ', '.join(v['value'])} — <{v['source']}>")
        out.append("")

    summary = ["| Drug | Shortage | NADAC 30-day est. | MassHealth PA | MA Medicare plans covering |", "|---|---|---|---|---|"]
    body = []
    not_checked = []
    review = {"controlled": [], "high": [], "low": [], "no_nadac": [], "no_mh": [], "no_medicare": []}
    for d in drugs["drugs"]:
        did = d["id"]
        sup = d["typical_30_day_supply"]
        sh = shortages[did]
        rows = [r for r in nadac[did] if r["pricing_unit"] == sup["nadac_unit"]]
        gen = [float(r["nadac_per_unit"]) for r in rows if r["classification"] == "G"]
        brand = [float(r["nadac_per_unit"]) for r in rows if r["classification"].startswith("B")]
        price_lines, est, est_value = [], NF, None
        for label, vals in (("Generic", gen), ("Brand", brand)):
            if vals:
                med = statistics.median(vals)
                cost = med * sup["units"]
                price_lines.append(f"{label}: {money(med)} per {sup['nadac_unit']} (median of {len(vals)} NDCs) -> about {money(cost)} for {sup['basis']}")
                if est == NF:
                    est = money(cost) + (" (generic)" if label == "Generic" else " (brand)")
                    est_value = cost
        name = d["display_name"]
        if d["controlled"]:
            chk = d.get("dea_schedule_check", {})
            review["controlled"].append(f"{name}: **{d['dea_schedule']}** (openFDA NDC directory: {chk.get('products_matched', '?')} "
                                        f"products matched; schedules seen {chk.get('schedules_seen', {})}). "
                                        "No pharmacy-level stock reports; shortage status and call script only.")
        if est_value is None:
            review["no_nadac"].append(f"{name}: no NADAC price in the '{sup['nadac_unit']}' unit used for the estimate.")
        elif est_value > HIGH_COST:
            review["high"].append(f"{name}: about {money(est_value)} for {sup['basis']} ({est.split(' ')[-1].strip('()')})")
        elif est_value < LOW_COST:
            review["low"].append(f"{name}: about {money(est_value)} for {sup['basis']}")
        as_of = rows[0]["as_of_date"] if rows else NF
        m = mh_by.get(did, {})
        f_rows = [r for r in formulary if r["drug_id"] == did]
        # A formulary can list the brand and the generic separately; count each plan once, at its lowest tier.
        best_row = {}
        for r in f_rows:
            cur = best_row.get(r["formulary_id"])
            if cur is None or int(r["tier"]) < int(cur["tier"]):
                best_row[r["formulary_id"]] = r
        covering = {(p["contract_id"], p["plan_id"], p["segment_id"]) for f in best_row for p in plans_by_formulary[f]}
        tiers = collections.Counter()
        flags = collections.Counter()
        for f, r in best_row.items():
            k = len(plans_by_formulary[f])
            tiers[r["tier"]] += k
            for fl in ("prior_auth", "step_therapy", "quantity_limit"):
                if r[fl] == "Y":
                    flags[fl] += k
        cov_text = (f"{len(covering)} of {n_plans}" if plans else "not built")
        if str(m.get("covered", "")).startswith("not checked"):
            not_checked.append(name)
        elif m.get("covered", NF) == NF:
            review["no_mh"].append(f"{name}: not found on the MassHealth Drug List search (<{m.get('source', NF)}>). "
                                   "MassHealth rule: drugs not on the list need prior authorization.")
        if plans and not covering:
            review["no_medicare"].append(f"{name}: on no Massachusetts Part D plan formulary in the CMS 2026 file.")
        summary.append(f"| {d['display_name']} | {sh['status']} | {est} | {m.get('prior_authorization', NF)} | {cov_text} |")
        body += [f"## {d['display_name']}", "",
                 f"- **RxNorm:** {d['generic_name']} — brands: {', '.join(d['brand_names']) if isinstance(d['brand_names'], list) else d['brand_names']} — "
                 f"{len(d['rxcuis'])} RxCUIs, {len(d['ndcs'])} NDCs. Controlled: {'yes, ' + d['dea_schedule'] if d['controlled'] else 'no'}.",
                 f"- **FDA shortage:** {sh['status']}. {sh['summary']} (checked {sh.get('checked_date', sh['checked_at'][:10])}, <{sh['source']}>)"]
        if sh["matching_entries"]:
            av = collections.Counter(e["availability"] for e in sh["matching_entries"])
            body.append(f"  - Listed packages by availability: {dict(av)}")
        body.append(f"- **NADAC (as of {as_of}):** " + ("; ".join(price_lines) if price_lines else NF))
        body.append(f"- **MassHealth:** {m.get('covered', NF)}; PA: {m.get('prior_authorization', NF)}. "
                    + " ".join(m.get("notes", [])[:2]) + f" (<{m.get('source', NF)}>)")
        if plans:
            if covering:
                tier_txt = ", ".join(f"tier {t}: {n}" for t, n in sorted(tiers.items()))
                flag_txt = ", ".join(f"{k.replace('_', ' ')}: {n}" for k, n in flags.items()) or "none"
                body.append(f"- **Medicare Part D (Massachusetts):** on the formulary of {len(covering)} of {n_plans} plan segments. "
                            f"Plans by lowest tier for this drug: {tier_txt}. Restrictions on that tier (number of plans): {flag_txt}.")
            else:
                body.append(f"- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.")
            if did in avg_cost:
                a = avg_cost[did]
                body.append(f"  - Average plan cost for {sup['basis']}: {money(float(a['avg_30_day_cost']))} "
                            f"(from {a['plans_with_price']} plans' pricing; this is the plan's drug price, not the patient's share).")
        neg = (rules or {}).get("rules", {}).get("negotiated_prices_2026_our_drugs", {}).get("by_drug", {})
        if did in neg:
            body.append(f"  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: {neg[did]}.")
        body.append("")

    vac = load("vaccines.json")
    ma = vac["massachusetts_rule"]
    vbody = ["## Vaccines", "", f"Checked {vac['checked_date']}. {vac['warning']}", "",
             f"**Massachusetts commercial insurance ({ma['rule']}):** {ma['coverage']} {ma['cost']} "
             f"Applies to: {ma['applies_to']} {ma['does_not_apply_to']} {ma['brands']} "
             f"Patient message: \"{ma['patient_message']}\" DPH list: <{ma['dph_recommended_list']}>. "
             f"Sources: {', '.join('<' + s + '>' for s in ma['sources'])} ({ma['verification']}).", "",
             "| Vaccine | Group | Medicare | MassHealth | Commercial (federal ACA list) | Massachusetts fully insured plans |",
             "|---|---|---|---|---|---|"]
    for v in vac["vaccines"]:
        m = v["commercial"]["massachusetts"]
        ma_cell = ("Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03)"
                   if m is not None and m.get("rule", "").startswith("Massachusetts") else m["coverage"])
        vbody.append(f"| {v['name']} | {v['group']} | Part {v['medicare']['part']}: {v['medicare']['cost']} | "
                     f"{v['masshealth']['coverage']} | {v['commercial']['coverage']} | {ma_cell} |")
    vbody.append("")
    for v in vac["vaccines"]:
        if v["group"] == "travel" or v.get("certified_sites_only"):
            vbody.append(f"- **{v['name']}:** " + " ".join(v["notes"]))
    vbody += ["", "Not checked: " + " ".join(vac["not_checked"]), ""]

    heads = [("controlled", "Controlled drugs (every one flagged; DEA schedule from openFDA)"),
             ("high", f"Very high cost estimates (NADAC 30-day estimate above {money(HIGH_COST)})"),
             ("low", f"Very low cost estimates (NADAC 30-day estimate below {money(LOW_COST)})"),
             ("no_nadac", "No NADAC price for the estimate"),
             ("no_mh", "No MassHealth Drug List match or not checked"),
             ("no_medicare", "No Massachusetts Medicare Part D match")]
    rv = ["## Please review first", "",
          "Unusual items for a pharmacist to check before anything else. NADAC estimates are what pharmacies pay, "
          "not what patients pay.", ""]
    if not_checked:
        review["no_mh"].insert(0, f"{len(not_checked)} drugs: MassHealth coverage not checked yet (the MassHealth Drug "
                                  "List website was unavailable on 2026-10-24). The website tells patients to call the "
                                  "pharmacy or MassHealth. Rerun: scripts/fetch_masshealth.py. Drugs: "
                                  + ", ".join(not_checked) + ".")
    for key, head in heads:
        rv += [f"### {head} ({len(review[key])})", ""] + ([f"- {x}" for x in review[key]] or ["- none"]) + [""]
    text = "\n".join(out + rv + ["## Summary", "", *summary, "", *body, *vbody])
    (ROOT / "output" / "medication_check.md").write_text(text, encoding="utf-8")
    print("wrote output/medication_check.md")


if __name__ == "__main__":
    main()
