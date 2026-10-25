"""Build data/savings.json: for each of RxLantern's drugs, links (never prices) to its GoodRx page and TrumpRx.gov page
when the drug is listed there, and, for brand-name drugs, the manufacturer's official savings program.

Run from the repository folder:  ..\\.venv\\Scripts\\python.exe scripts\\build_savings.py
Needs Playwright's Chromium (TrumpRx and the manufacturer sites only load in a real browser).

- GoodRx: "listed" = the drug's page is in GoodRx's own sitemap of drug price pages
  (https://www.goodrx.com/sitemaps/drug-price.xml). We link to the page and never copy prices.
- TrumpRx.gov: "listed" = the drug has a product page on https://trumprx.gov/browse ("Presidential deals" or
  "Standard prices"). TrumpRx does not list controlled substances; RxLantern never links them there anyway.
- Manufacturer savings: we open the brand's official website (MAKER_SITES) and take the link whose text is about
  savings, a copay card, or cost support. The page it points to is the source, with the date checked.
  "not found" when the site has no such link.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "savings"
OUT = ROOT / "data" / "savings.json"
GOODRX_SITEMAP = "https://www.goodrx.com/sitemaps/drug-price.xml"
TRUMPRX_BROWSE = "https://trumprx.gov/browse"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36")
NOTE = ("Discount cards and coupons usually mean paying cash outside your insurance, so the cost may not count toward "
        "your deductible. Manufacturer copay cards generally can't be used with Medicare or MassHealth.")

# Page names on GoodRx / TrumpRx when the simple rule (the medicine's own name) does not give the right page.
# None = the drug is not on that site (checked by hand).
GOODRX = {
    "adderall_xr_30": "adderall-xr", "concerta_18": "concerta", "humira_40": "humira", "lantus_solostar": "lantus",
    "albuterol_hfa": "albuterol", "amoxicillin_susp_400": "amoxicillin", "amoxicillin_susp_250": "amoxicillin",
    "fluticasone_nasal_50": "fluticasone-propionate", "triamcinolone_cream_01": "triamcinolone", "epinephrine_03": "epinephrine-epipen",
    "nicotine_patch_21": "nicotine", "metformin_er_500": "metformin-er-glucophage-xr", "humalog_kwikpen": "humalog",
    "novolog_flexpen": "novolog", "tresiba_flextouch": "tresiba", "toujeo_solostar": "toujeo",
    "insulin_nph_pen": "humulin-n", "advair_diskus_250": "advair", "symbicort_160": "symbicort",
    "trelegy_100": "trelegy-ellipta", "spiriva_handihaler": "spiriva-handihaler", "flovent_hfa_110": "flovent",
    "albuterol_neb_25": "albuterol", "duoneb": "ipratropium-albuterol", "budesonide_neb_05": "budesonide",
    "montelukast_chew_5": "montelukast", "naloxone_nasal_4": "narcan", "oseltamivir_susp": "oseltamivir",
    "amox_clav_875": "augmentin", "amox_clav_susp_400": "augmentin",
    "azithromycin_susp_200": "azithromycin", "cephalexin_susp_250": "cephalexin", "cefdinir_susp_250": "cefdinir",
    "smx_tmp_ds": "sulfamethoxazole-trimethoprim", "smx_tmp_susp": "sulfamethoxazole-trimethoprim",
    "penicillin_vk_500": "penicillin-v-potassium", "metoprolol_succ_er_50": "metoprolol-er",
    "metoprolol_tart_25": "metoprolol", "bupropion_xl_150": "bupropion-xl", "venlafaxine_er_75": "venlafaxine",
    "adderall_ir_10": "adderall", "methylphenidate_10": "methylphenidate", "focalin_xr_10": "focalin-xr",
    "guanfacine_er_1": "guanfacine-er", "hydrocodone_apap_5_325": "hydrocodone-acetaminophen",
    "oxycodone_apap_5_325": "oxycodone-acetaminophen", "buprenorphine_naloxone_8_2": "buprenorphine-naloxone",
    "diclofenac_gel_1": "voltaren-gel", "testosterone_cyp_200": "testosterone-cypionate",
    "ondansetron_odt_4": "ondansetron", "prednisolone_soln_15": "prednisolone", "methylprednisolone_4_pack": "medrol",
    "norgestimate_ee": "sprintec", "medroxyprogesterone_inj_150": "depo-provera", "truvada_prep": "truvada",
    "timolol_eye_05": "timolol", "clobetasol_cream_005": "clobetasol", "ergocalciferol_50000": "vitamin-d2",
    "doxycycline_100": "doxycycline-hyclate", "nitroglycerin_sl_04": "nitroglycerin", "valacyclovir_1g": "valacyclovir",
    "mupirocin_2": "mupirocin", "paxlovid": "paxlovid", "tamsulosin_04": "flomax", "hydroxyzine_25": "hydroxyzine-hydrochloride", "ezetimibe_10": "zetia", "hydrochlorothiazide_25": "microzide",
}
TRUMPRX = {
    "humira_40": "humira-pen", "humalog_kwikpen": "insulin-lispro", "lantus_solostar": "lantus",
    "novolog_flexpen": "novolog", "albuterol_hfa": "albuterol-hfa", "albuterol_neb_25": "albuterol-sulfate",
    "duoneb": "ipratropium-albuterol", "amox_clav_875": "amoxicillin-pot-clavulanate",
    "amox_clav_susp_400": "amoxicillin-pot-clavulanate", "amoxicillin_500": "amoxicillin-trihydrate",
    "amoxicillin_susp_400": "amoxicillin-trihydrate", "amoxicillin_susp_250": "amoxicillin-trihydrate",
    "fluticasone_nasal_50": "fluticasone-propionate", "flovent_hfa_110": "fluticasone-propionate-hfa",
    "advair_diskus_250": "fluticasone-salmeterol", "symbicort_160": "budesonide-formoterol-fumarate",
    "spiriva_handihaler": "tiotropium-bromide-inhalation-powder", "budesonide_neb_05": "budesonide",
    "triamcinolone_cream_01": "triamcinolone-acetonide-topical", "metformin_er_500": "metformin-hcl",
    "metoprolol_succ_er_50": None, "metoprolol_tart_25": "metoprolol-tartrate", "venlafaxine_er_75": "venlafaxine-hcl-er",
    "bupropion_xl_150": "bupropion-xl", "doxycycline_100": "doxycycline-hyclate", "smx_tmp_ds": "sulfamethoxazole-trimethoprim",
    "smx_tmp_susp": "sulfamethoxazole-trimethoprim", "nitrofurantoin_100": "nitrofurantoin-mono-macro",
    "penicillin_vk_500": "penicillin-v-potassium", "guanfacine_er_1": None, "medroxyprogesterone_inj_150": "medroxyprogesterone-acetate",
    "methylprednisolone_4_pack": "methylprednisolone", "norgestimate_ee": "norgestimate-ethinyl-estradiol",
    "truvada_prep": "emtricitabine-tenofovir-df", "entresto_49_51": "sacubitril-valsartan", "xarelto_20": "xarelto",
    "januvia_100": "januvia", "farxiga_10": "farxiga", "clobetasol_cream_005": "clobetasol-propionate-emollient",
    "diclofenac_gel_1": None, "prednisolone_soln_15": "prednisolone-sodium-phosphate", "timolol_eye_05": None,
    "oseltamivir_susp": "oseltamivir", "oseltamivir_75": "oseltamivir-phosphate", "ondansetron_odt_4": "ondansetron",
    "cephalexin_susp_250": "cephalexin", "azithromycin_susp_200": "azithromycin", "cefdinir_susp_250": "cefdinir",
    "montelukast_chew_5": None, "montelukast_10": None, "escitalopram_10": "escitalopram-oxalate",
    "pantoprazole_40": "pantoprazole-sodium", "hydroxyzine_25": "hydroxyzine-hcl", "trazodone_50": "trazodone",
    "quetiapine_25": "quetiapine-fumarate", "buspirone_10": "buspirone-hcl", "propranolol_10": "propranolol-hcl",
    "cyclobenzaprine_10": "cyclobenzaprine", "tamsulosin_04": "tamsulosin", "alendronate_70": "alendronate-sodium",
    "pioglitazone_30": "pioglitazone", "glipizide_5": "glipizide", "levothyroxine_50": "levothyroxine",
}

# Brand-name drugs and the brand's official website, where we look for the savings program link.
MAKER_SITES = {
    "adderall_xr_30": "https://www.adderallxr.com/", "concerta_18": "https://www.concerta.net/",
    "ozempic_05": "https://www.ozempic.com/", "mounjaro_5": "https://mounjaro.lilly.com/",
    "eliquis_5": "https://www.eliquis.com/", "humira_40": "https://www.humira.com/",
    "dupixent_300": "https://www.dupixent.com/", "lantus_solostar": "https://www.lantus.com/",
    "paxlovid": "https://www.paxlovid.com/", "wegovy_24": "https://www.wegovy.com/",
    "rybelsus_7": "https://www.rybelsus.com/", "zepbound_25": "https://zepbound.lilly.com/",
    "trulicity_15": "https://www.trulicity.com/", "victoza_18": "https://www.victoza.com/",
    "jardiance_10": "https://www.jardiance.com/", "farxiga_10": "https://www.farxiga.com/",
    "januvia_100": "https://www.januvia.com/", "humalog_kwikpen": "https://www.humalog.com/",
    "novolog_flexpen": "https://www.novolog.com/", "tresiba_flextouch": "https://www.tresiba.com/",
    "toujeo_solostar": "https://www.toujeo.com/", "advair_diskus_250": "https://www.advair.com/",
    "symbicort_160": "https://www.symbicort.com/", "trelegy_100": "https://www.trelegy.com/",
    "spiriva_handihaler": "https://www.spiriva.com/", "flovent_hfa_110": "https://www.flovent.com/",
    "xarelto_20": "https://www.xarelto-us.com/", "entresto_49_51": "https://www.entresto.com/",
    "repatha_140": "https://www.repatha.com/", "brilinta_90": "https://www.brilinta.com/",
    "vyvanse_30": "https://www.vyvanse.com/", "focalin_xr_10": "https://www.focalinxr.com/",
    "linzess_145": "https://www.linzess.com/", "truvada_prep": "https://www.truvada.com/",
    "biktarvy": "https://www.biktarvy.com/", "enbrel_50": "https://www.enbrel.com/",
    "nurtec_75": "https://www.nurtec.com/", "naloxone_nasal_4": "https://www.narcan.com/",
}
# Official programs the brand site does not link from its home page, opened and checked by hand on 2026-10-24
# (the page loaded on the maker's own program site and describes a savings or co-pay program).
MAKER_VERIFIED = {
    "truvada_prep": {"url": "https://www.gileadadvancingaccess.com/copay-savings-card",
                     "link_text": "Gilead Advancing Access Co-pay Savings Program"},
    "humalog_kwikpen": {"url": "https://insulins.lilly.com/lilly-insulin-value-program",
                        "link_text": "Lilly Insulin Value Program"},
}
SAVINGS_WORDS = re.compile(r"sav(e|ings)|co-?pay|cost|afford|pay as little|financial (help|support|assistance)", re.I)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def goodrx_pages() -> set[str]:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / "goodrx-drug-price.xml"
    if not path.exists():
        r = httpx.get(GOODRX_SITEMAP, timeout=120, headers={"User-Agent": UA})
        r.raise_for_status()
        path.write_text(r.text, encoding="utf-8")
    return set(re.findall(r"<loc>https://www\.goodrx\.com/([^<]+)</loc>", path.read_text(encoding="utf-8")))


def browser_page(p):
    b = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
    return b, b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}).new_page()


def trumprx_pages(p) -> dict[str, str]:
    """TrumpRx product page names -> tab ('Presidential deals' or 'Standard prices')."""
    path = RAW / "trumprx.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    b, pg = browser_page(p)
    out = {}
    for tab in ("Presidential deals", "Standard prices"):
        pg.goto(TRUMPRX_BROWSE, timeout=60000)
        pg.wait_for_timeout(4000)
        if tab == "Standard prices":
            pg.get_by_text("Standard prices", exact=True).last.click()
            pg.wait_for_timeout(3000)
        stale = 0
        for _ in range(200):
            n = len(out)
            for h in pg.eval_on_selector_all("a[href*='/p/']", "els => els.map(e => e.href)"):
                out.setdefault(h.rsplit("/p/", 1)[1].split("?")[0], tab)
            nxt = pg.locator("button[aria-label*='Next'], a[aria-label*='Next'], button:has-text('Next')")
            try:
                if nxt.count() and nxt.first.is_enabled():
                    nxt.first.click(timeout=3000)
                    pg.wait_for_timeout(1500)
                else:
                    pg.mouse.wheel(0, 5000)
                    pg.wait_for_timeout(1000)
            except Exception:  # noqa: BLE001 - end of the list
                pass
            stale = stale + 1 if len(out) == n else 0
            if stale >= 4:
                break
    b.close()
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def maker_programs(p, today: str) -> dict[str, dict]:
    path = RAW / "makers.json"
    out = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    todo = {d: s for d, s in MAKER_SITES.items() if d not in out or out[d].get("error")}
    if not todo:
        return out
    b, first = browser_page(p)
    ctx = first.context
    for did, site in todo.items():
        rec = {"site": site, "url": "not found", "link_text": None, "checked_date": today}
        pg = ctx.new_page()  # a fresh tab per site, so one slow site cannot break the next one
        try:
            pg.goto(site, timeout=45000, wait_until="domcontentloaded")
            pg.wait_for_timeout(3500)
            home = pg.url
            host = re.sub(r"^www\.", "", httpx.URL(home).host)
            best = None
            for text, href in pg.eval_on_selector_all("a[href]", "els => els.map(e => [e.innerText.trim(), e.href])"):
                t = " ".join(text.split())[:90]
                if not href.startswith("http") or href.endswith("#") or not SAVINGS_WORDS.search(t + " " + href):
                    continue
                if re.search(r"pdf$|prescribing|medication guide|important safety", href + t, re.I):
                    continue
                score = (3 if re.search(r"sav|co-?pay", t, re.I) else 1) + (1 if host.split(".")[-2] in href else 0)
                if best is None or score > best[0]:
                    best = (score, t, href)
            rec["home"] = home
            if best:
                rec.update(url=best[2], link_text=best[1])
        except Exception as e:  # noqa: BLE001 - site down or blocked: "not found", never a guess
            rec["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        finally:
            pg.close()
        out[did] = rec
        print(f"{did:24} {rec['url'][:90]}  [{rec.get('link_text')}]")
    b.close()
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def main() -> None:
    from playwright.sync_api import sync_playwright

    today = date.today().isoformat()
    drugs = json.loads((ROOT / "data" / "drugs.json").read_text(encoding="utf-8"))["drugs"]
    gx = goodrx_pages()
    with sync_playwright() as p:
        trx = trumprx_pages(p)
        makers = maker_programs(p, today)
    rows, missing = [], []
    for d in drugs:
        did = d["id"]
        base = slug(re.sub(r"\(.*?\)", "", d["display_name"]).split(" ")[0])
        cands = [GOODRX[did]] if did in GOODRX else [base]
        g = next((c for c in cands if c and c in gx), None)
        if did in TRUMPRX:
            t = TRUMPRX[did] if TRUMPRX[did] in trx else None
        else:
            t = base if base in trx else None
        if d["controlled"]:
            t = None  # TrumpRx does not list controlled substances; never link them there
        m = makers.get(did)
        if m and m["url"] == "not found" and did in MAKER_VERIFIED:
            m = m | MAKER_VERIFIED[did] | {"home": MAKER_VERIFIED[did]["url"]}
        rows.append({
            "drug_id": did,
            "goodrx": {"url": f"https://www.goodrx.com/{g}" if g else None, "listed": bool(g),
                       "source": GOODRX_SITEMAP, "checked_date": today},
            "trumprx": {"url": f"https://trumprx.gov/p/{t}" if t else None, "listed": bool(t),
                        "list": trx.get(t) if t else None, "source": TRUMPRX_BROWSE, "checked_date": today},
            "manufacturer": None if m is None else {
                "url": m["url"], "link_text": m.get("link_text"), "brand_site": m["site"],
                "source": m.get("home", m["site"]) if m["url"] != "not found" else m["site"],
                "checked_date": m["checked_date"]},
        })
        if not g:
            missing.append(f"GoodRx: {did} (tried {cands})")
    OUT.write_text(json.dumps({
        "checked_date": today, "note": NOTE,
        "sources": {"goodrx": GOODRX_SITEMAP, "trumprx": TRUMPRX_BROWSE,
                    "manufacturer": "each brand's official website (see brand_site)"},
        "rule": "Links only. RxLantern never copies or shows GoodRx or TrumpRx prices.",
        "drugs": rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(missing) or "GoodRx: all found")
    print(f"TrumpRx listed: {sum(r['trumprx']['listed'] for r in rows)}; makers found: "
          f"{sum(1 for r in rows if r['manufacturer'] and r['manufacturer']['url'] != 'not found')} of {len(MAKER_SITES)}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
