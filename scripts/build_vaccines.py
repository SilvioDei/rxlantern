"""Build data/vaccines.json: who pays for each vaccine (Medicare, MassHealth, commercial).

Run from the repository folder:  ..\\.venv\\Scripts\\python.exe scripts\\build_vaccines.py
Facts below were read from official pages on the checked date. MassHealth rows come from the saved
MassHealth Drug List searches in data/raw/masshealth/vax_*.html (scripts/fetch_masshealth.py pattern).
Vaccine rules changed in 2025-2026: re-check before relying on this.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mh_parse import rows  # noqa: E402

CHECKED = "2026-10-23"
NF = "not found"
RAW = ROOT / "data" / "raw" / "masshealth"
MHDL = "https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor="

CDC_PAY = "https://www.cdc.gov/vaccines-adults/recommended-vaccines/how-to-pay-adult-vaccines.html"
CMS_MLN = "https://www.cms.gov/files/document/mln908764-medicare-part-d-vaccines.pdf"
HC_GOV = "https://www.healthcare.gov/preventive-care-adults/"
YELLOW_BOOK_TRAVEL = ("https://www.cdc.gov/yellow-book/hcp/preparing-international-travelers/"
                      "travel-health-advice-for-resource-limited-travelers.html")
MEDICARE_TRAVEL = "https://www.medicare.gov/coverage/travel-outside-the-u.s."
YF_FINDER = "https://wwwnc.cdc.gov/travel/yellow-fever-vaccination-clinics/search"

PART_B_COST = "$0 if the provider accepts Medicare assignment (no deductible or coinsurance for Part B vaccines)"
PART_D_COST = "$0 for ACIP-recommended adult vaccines, even before the deductible"

COMMERCIAL_LISTED = {
    "coverage": "Listed on HealthCare.gov's adult preventive services list. Marketplace plans and many other plans must cover it.",
    "cost": "No copay or coinsurance from an in-network provider, even before the deductible. HealthCare.gov adds: '$0 cost isn't guaranteed in all cases.'",
    "source": HC_GOV,
}
COMMERCIAL_NOT_LISTED = {
    "coverage": "Not on HealthCare.gov's adult preventive services list. Coverage depends on the plan: not found.",
    "cost": NF,
    "source": HC_GOV,
}

# Massachusetts rules. mass.gov returned 'access denied' (HTTP 403) to RxLantern's tools, so the project owner
# looked these up; recorded as "verified via web search, 2026-10-23".
MA_BULLETIN = "https://www.mass.gov/doc/bulletin-2025-03-coverage-for-vaccines-issued-september-3-2025/download"
MA_FAQ = "https://www.mass.gov/info-details/frequently-asked-questions-about-vaccinations"
MA_DPH_LIST = "https://www.mass.gov/info-details/dph-recommended-guidance-for-vaccines"
MA_VERIFIED = "verified via web search, 2026-10-23 (mass.gov could not be opened directly)"
LARGE_EMPLOYER_WARNING = ("If your plan is through a large employer, check with your plan, because it may not have "
                          "to follow the Massachusetts rule.")
MA_RULE = {
    "rule": "Massachusetts Bulletin 2025-03 (Division of Insurance and Department of Public Health, issued September 3, 2025)",
    "coverage": ("Insurers must cover vaccines recommended by the Massachusetts Department of Public Health (DPH), "
                 "not only CDC recommendations."),
    "cost": "No cost-sharing and no utilization management (no prior authorization delays) for covered routine vaccines.",
    "applies_to": ("Fully insured health plans issued under Massachusetts law (for example Blue Cross Blue Shield of "
                   "Massachusetts and HMOs). Group Insurance Commission (GIC) plans and MassHealth also cover vaccines "
                   "according to DPH guidelines."),
    "does_not_apply_to": "Self-insured employer plans are not required to follow the bulletin.",
    "patient_message": LARGE_EMPLOYER_WARNING,
    "brands": "Insurers may cover only certain brands, as long as at least one product covers each DPH-recommended vaccine.",
    "dph_recommended_list": MA_DPH_LIST,
    "sources": [MA_BULLETIN, MA_FAQ, MA_DPH_LIST],
    "verification": MA_VERIFIED,
    "checked_date": "2026-10-23",
}
MA_TRAVEL = {
    "rule": "Not part of Massachusetts Bulletin 2025-03",
    "coverage": ("The bulletin covers routine vaccines only. Travel vaccines (hepatitis A for travel, typhoid, yellow "
                 "fever) are not part of it. Check with your plan."),
    "cost": "Check with your plan.",
    "patient_message": "Check with your plan.",
    "sources": [MA_BULLETIN],
    "verification": MA_VERIFIED,
    "checked_date": "2026-10-23",
}

VACCINES = [
    {"id": "flu", "name": "Flu (influenza)", "group": "routine", "mhdl_terms": ["influenza"],
     "medicare": {"part": "B", "coverage": "Part B covers the flu shot, usually once per flu season.", "cost": PART_B_COST,
                  "source": "https://www.medicare.gov/coverage/flu-vaccines"},
     "commercial": COMMERCIAL_LISTED,
     "notes": ["CDC recommends a flu vaccine every year for everyone 6 months and older (updated Sept 1, 2026).",
               "MassHealth pays pharmacies for seasonal flu vaccine without PA (MassHealth Drug List footnote 1)."],
     "extra_sources": ["https://www.cdc.gov/flu/hcp/vax-summary/index.html"]},
    {"id": "covid19", "name": "COVID-19", "group": "routine", "mhdl_terms": ["comirnaty", "spikevax"],
     "medicare": {"part": "B", "coverage": "Part B covers FDA-approved or authorized COVID-19 vaccines.", "cost": PART_B_COST,
                  "source": "https://www.medicare.gov/coverage/covid-19-vaccine"},
     "commercial": COMMERCIAL_NOT_LISTED,
     "notes": ["CDC (updated Sept 23, 2026): a 2026-2027 COVID-19 vaccine is recommended for all adults 18 and older.",
               "CDC says the July 2025 schedule's COVID-19 advice stays in effect 'because of legal uncertainties and inquiries.'",
               "Medicare.gov still names the 2025-2026 formula; CDC names 2026-2027 vaccines."],
     "extra_sources": ["https://www.cdc.gov/covid/hcp/vaccine-considerations/routine-guidance.html"]},
    {"id": "hepb", "name": "Hepatitis B", "group": "routine", "mhdl_terms": ["hepatitis"], "mhdl_filter": "hepatitis B",
     "medicare": {"part": "B (for some people)", "coverage": "Part B covers it if you are at medium or high risk, never finished the series, or don't know your history. Others: Part D.",
                  "cost": PART_B_COST, "source": "https://www.medicare.gov/coverage/hepatitis-b-vaccines"},
     "commercial": COMMERCIAL_LISTED,
     "notes": ["CDC: hepatitis B vaccine for all adults 19-59; adults 60+ with risk factors should get it."],
     "extra_sources": ["https://www.cdc.gov/hepatitis-b/hcp/vaccine-administration/index.html", CMS_MLN]},
    {"id": "shingles", "name": "Shingles (Shingrix)", "group": "routine", "mhdl_terms": ["shingrix"],
     "medicare": {"part": "D", "coverage": "Part D (Medicare drug coverage) covers the shingles vaccine.", "cost": PART_D_COST,
                  "source": "https://www.medicare.gov/coverage/shingles-vaccines"},
     "commercial": COMMERCIAL_LISTED,
     "notes": ["CDC: 2 doses of Shingrix for adults 50+, and adults 19+ with weakened immune systems."],
     "extra_sources": ["https://www.cdc.gov/shingles/hcp/vaccine-considerations/index.html"]},
    {"id": "rsv", "name": "RSV", "group": "routine", "mhdl_terms": ["respiratory_syncytial"],
     "medicare": {"part": "D", "coverage": "Part D covers the RSV vaccine.", "cost": PART_D_COST,
                  "source": "https://www.medicare.gov/coverage/respiratory-syncytial-virus-rsv-shot"},
     "commercial": COMMERCIAL_NOT_LISTED,
     "notes": ["CDC: one dose for all adults 75+, and adults 50-74 at higher risk (updated Feb 24, 2026)."],
     "extra_sources": ["https://www.cdc.gov/rsv/hcp/vaccine-clinical-guidance/adults.html"]},
    {"id": "pneumococcal", "name": "Pneumococcal (pneumonia)", "group": "routine", "mhdl_terms": ["pneumococcal"],
     "medicare": {"part": "B", "coverage": "Part B covers pneumococcal vaccines.", "cost": PART_B_COST,
                  "source": "https://www.medicare.gov/coverage/pneumococcal-vaccines"},
     "commercial": COMMERCIAL_LISTED,
     "notes": ["CDC: PCV15, PCV20, or PCV21 for all adults 50 and older; younger adults based on health conditions (updated Feb 25, 2026)."],
     "extra_sources": ["https://www.cdc.gov/pneumococcal/hcp/vaccine-recommendations/index.html"]},
    {"id": "tdap", "name": "Tdap (tetanus, diphtheria, whooping cough)", "group": "routine", "mhdl_terms": ["tetanus"],
     "mhdl_filter": "pertussis",
     "medicare": {"part": "D (Part B if given to treat an injury)", "coverage": "Part D covers Tdap. A tetanus shot given to treat an injury or exposure is covered by Part B.",
                  "cost": PART_D_COST, "source": "https://www.medicare.gov/coverage/tdap-vaccines"},
     "commercial": COMMERCIAL_LISTED,
     "notes": ["CDC adult schedule: 1 dose of Tdap, then a Td or Tdap booster every 10 years, and Tdap in each pregnancy."],
     "extra_sources": [CMS_MLN]},
    {"id": "hepa", "name": "Hepatitis A", "group": "travel", "mhdl_terms": ["hepatitis"], "mhdl_filter": "hepatitis A",
     "medicare": {"part": "D (Part B only if given after an exposure)", "coverage": "Part D covers commercially available vaccines needed to prevent illness. Part B covers it only to treat an exposure.",
                  "cost": "$0 under Part D if ACIP recommends it for you; otherwise the plan may charge a copay (CMS)",
                  "source": CMS_MLN},
     "commercial": {"coverage": "Hepatitis A is on HealthCare.gov's adult preventive list ('recommended populations vary'). Coverage for travel only: not found.",
                    "cost": "No copay or coinsurance in-network for covered preventive services; '$0 cost isn't guaranteed in all cases.'",
                    "source": HC_GOV},
     "notes": ["CDC: travelers to countries where hepatitis A is common should get vaccinated."],
     "extra_sources": ["https://www.cdc.gov/hepatitis-a/vaccination/index.html", YELLOW_BOOK_TRAVEL]},
    {"id": "typhoid", "name": "Typhoid", "group": "travel", "mhdl_terms": ["typhoid"],
     "medicare": {"part": NF, "coverage": "No Medicare or CMS page names typhoid. Part D covers commercially available vaccines needed to prevent illness, but a typhoid-specific rule was not found.",
                  "cost": NF, "source": CMS_MLN},
     "commercial": COMMERCIAL_NOT_LISTED,
     "notes": ["CDC: oral (4 capsules, ages 6+) or shot (ages 2+), at least 2 weeks before travel."],
     "extra_sources": ["https://www.cdc.gov/typhoid-fever/prevention/index.html", YELLOW_BOOK_TRAVEL]},
    {"id": "yellowfever", "name": "Yellow fever", "group": "travel", "mhdl_terms": ["yellow_fever"],
     "medicare": {"part": "D", "coverage": "Medicare.gov: Part D covers ACIP-recommended vaccines you may need before travel outside the U.S., such as yellow fever.",
                  "cost": "Part D won't charge a copay or deductible for vaccines ACIP recommends", "source": MEDICARE_TRAVEL},
     "commercial": COMMERCIAL_NOT_LISTED,
     "certified_sites_only": True,
     "clinic_finder": YF_FINDER,
     "notes": ["Yellow fever vaccine is given ONLY at certified (designated) yellow fever vaccination centers. Most pharmacies cannot give it.",
               "Find a certified clinic with CDC's search tool: " + YF_FINDER,
               "For people 9 months and older traveling to at-risk areas of Africa and South America."],
     "extra_sources": ["https://www.cdc.gov/yellow-fever/hcp/vaccine/index.html", "https://www.cdc.gov/yellow-fever/vaccine/index.html"]},
]


def masshealth(v: dict) -> dict:
    listed, url = [], None
    for term in v["mhdl_terms"]:
        url = url or MHDL + term.replace("_", "+")
        path = RAW / f"vax_{term}.html"
        for r in rows(path) if path.exists() else []:
            if v.get("mhdl_filter") and v["mhdl_filter"] not in r[0]:
                continue
            if "immune globulin" in r[0] or "Non-Drug" in r[0]:
                continue
            listed.append({"product": r[0], "pa": r[1] or "no PA", "codes": r[3]})
    if not listed:
        return {"coverage": NF, "cost": NF, "products": [], "source": url}
    pa = [p for p in listed if p["pa"] != "no PA"]
    cov = "Listed on the MassHealth Drug List" + (" (some products need PA for certain ages: "
                                                  + "; ".join(f"{p['product'].split(' (')[0]} {p['pa']}" for p in pa) + ")"
                                                  if pa else ", no PA.")
    return {
        "coverage": cov,
        "cost": "CDC: most adults with Medicaid get all CDC-recommended vaccines at no cost.",
        "products": listed,
        "rule": ("MassHealth does not pay for vaccines that are free through local boards of health or the Mass. "
                 "Department of Public Health (products marked '1'); flu vaccine is paid at pharmacies without PA."),
        "source": url,
        "cost_source": CDC_PAY,
    }


def main() -> None:
    out = []
    for v in VACCINES:
        rec = {k: v[k] for k in v if not k.startswith("mhdl_")}
        rec["masshealth"] = masshealth(v)
        rec["commercial"] = dict(rec["commercial"]) | {"massachusetts": MA_TRAVEL if v["group"] == "travel" else MA_RULE}
        rec["masshealth"]["dph_rule"] = {"says": "MassHealth covers vaccines according to DPH guidelines.",
                                         "source": MA_FAQ, "verification": MA_VERIFIED}
        if v["group"] == "travel":
            rec["notes"] = rec["notes"] + ["Travel vaccines are often not covered by insurance. CDC: 'many health insurance plans "
                                           "provide no or limited coverage for travel immunizations.' Call your plan first."]
        rec["checked_date"] = CHECKED
        out.append(rec)
        print(f"{v['id']:13} medicare={rec['medicare']['part']:40} masshealth_products={len(rec['masshealth']['products'])}")
    (ROOT / "data" / "vaccines.json").write_text(json.dumps({
        "checked_date": CHECKED,
        "warning": "Vaccine rules changed in 2025-2026. Re-check official sources before relying on this.",
        "general_sources": [
            {"url": CDC_PAY, "says": "Private plans must cover certain vaccines with no copay in-network; Part B covers COVID-19, flu, pneumococcal, hepatitis B for people at increased risk; Part D makes all other CDC-recommended adult vaccines available at no cost; most adults with Medicaid get all CDC-recommended vaccines at no cost. (Updated Sept 2, 2026)"},
            {"url": CMS_MLN, "says": "Part D covers all commercially available vaccines not covered by Part B; $0 for ACIP-recommended adult vaccines; non-ACIP-recommended vaccines may have cost sharing."},
            {"url": HC_GOV, "says": "Adult immunizations plans must cover: chickenpox, diphtheria, flu, hepatitis A, hepatitis B, HPV, measles, meningococcal, mumps, whooping cough, pneumococcal, rubella, shingles, tetanus."},
            {"url": "https://www.cdc.gov/vaccines/hcp/imz-schedules/adult-age.html", "says": "Adult schedule page still shows the 2025 schedule (addendum July 2, 2025); no 2026 adult schedule found."},
        ],
        "massachusetts_rule": MA_RULE,
        "not_checked": ["mass.gov pages could not be opened directly (HTTP 403). The Massachusetts rule above was "
                        + MA_VERIFIED + ".",
                        "MassHealth pharmacy bulletins on mass.gov could not be opened (HTTP 403)."],
        "yellow_fever_clinic_finder": YF_FINDER,
        "vaccines": out,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
