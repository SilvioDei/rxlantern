# Medication data check

Checked: 2026-10-23. For pharmacist review. Every fact lists its source.

- **NADAC** is what pharmacies pay to buy the drug (CMS survey), not the patient's price. The 30-day estimate = NADAC per unit x the amount shown. It leaves out the pharmacy's dispensing fee and markup.
- **Medicare counts** are Massachusetts Part D plans (stand-alone PDPs and Medicare Advantage drug plans) in the CMS 2026 quarterly file; 96 plan segments in total.
- **MassHealth** status is from the MassHealth Drug List (last updated 10/05/26). Rule: any drug not on the list requires prior authorization (PA).
- **Shortage** status is from the openFDA drug shortages API (snapshot 2026-10-23).

## 2026 Medicare Part D rules

- **Yearly out-of-pocket cap for covered Part D drugs:** $2,100 in 2026 ($2,400 in 2027). — <https://www.medicare.gov/drug-coverage-part-d/costs-for-medicare-drug-coverage>
- **Highest Part D deductible a plan may charge:** $615 in 2026 ($700 in 2027) — <https://www.medicare.gov/drug-coverage-part-d/costs-for-medicare-drug-coverage>
- **Insulin cap:** No more than $35 for a one-month supply of each Part B- or Part D-covered insulin product, and no deductible for insulin. — <https://www.medicare.gov/coverage/insulin>
- **Drugs with a Medicare negotiated price (Maximum Fair Price) starting January 1, 2026:** Eliquis, Jardiance, Xarelto, Januvia, Farxiga, Entresto, Enbrel, Imbruvica, Stelara, Fiasp / NovoLog insulin aspart products — <https://www.cms.gov/files/document/infographic-negotiated-prices-maximum-fair-prices.pdf>
- **Which of the 25 RxLantern drugs have a negotiated price in 2026:** Eliquis (apixaban) - CMS lists a 56% discount off the 2023 list price for a 30-day supply — <https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026>
- **When the 2026 negotiated prices start:** January 1, 2026 — <https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026>

## Summary

| Drug | Shortage | NADAC 30-day est. | MassHealth PA | MA Medicare plans covering |
|---|---|---|---|---|
| Adderall XR 30 mg ER capsule | not found on FDA shortage list | $14.28 (generic) | only in some cases: < 3 years or >= 21 years; or > 2 units/day | 95 of 96 |
| Concerta 18 mg ER tablet | in shortage | $18.29 (generic) | only in some cases: < 3 years or >= 21 years; or > 2 units/day | 45 of 96 |
| Atorvastatin 20 mg tablet | not found on FDA shortage list | $0.86 (generic) | only in some cases: > 1.5 units/day | 96 of 96 |
| Lisinopril 10 mg tablet | not found on FDA shortage list | $0.54 (generic) | no | 96 of 96 |
| Levothyroxine 50 mcg tablet | not found on FDA shortage list | $1.20 (generic) | no | 96 of 96 |
| Metformin 500 mg tablet | not found on FDA shortage list | $0.89 (generic) | no | 96 of 96 |
| Amlodipine 5 mg tablet | not found on FDA shortage list | $0.30 (generic) | no | 96 of 96 |
| Omeprazole 20 mg DR capsule | not found on FDA shortage list | $0.91 (generic) | only in some cases: > 4 units/day | 96 of 96 |
| Sertraline 50 mg tablet | not found on FDA shortage list | $1.05 (generic) | only in some cases: < 6 years | 96 of 96 |
| Amoxicillin 500 mg capsule | not found on FDA shortage list | $2.38 (generic) | no | 96 of 96 |
| Ozempic (semaglutide) 0.5 mg pen | not found on FDA shortage list | $996.07 (brand) | yes | 96 of 96 |
| Mounjaro (tirzepatide) 5 mg pen | not found on FDA shortage list | $1,077.39 (brand) | yes | 95 of 96 |
| Eliquis (apixaban) 5 mg tablet | not found on FDA shortage list | $331.29 (brand) | no | 96 of 96 |
| Humira (adalimumab) 40 mg pen | not found on FDA shortage list | $6,735.70 (brand) | yes | 62 of 96 |
| Dupixent (dupilumab) 300 mg pen | not found on FDA shortage list | $4,035.76 (brand) | yes | 96 of 96 |
| Albuterol HFA 90 mcg inhaler | not found on FDA shortage list | $32.98 (generic) | yes | 96 of 96 |
| Insulin glargine (Lantus SoloStar) pen | not found on FDA shortage list | $92.46 (brand) | no | 95 of 96 |
| Amoxicillin 400 mg/5 mL oral suspension | not found on FDA shortage list | $3.92 (generic) | no | 96 of 96 |
| Sumatriptan 50 mg tablet | not found on FDA shortage list | $2.81 (generic) | only in some cases: > 16 units/30 days | 96 of 96 |
| Latanoprost 0.005% eye drops | not found on FDA shortage list | $3.93 (generic) | no | 96 of 96 |
| Fluticasone 50 mcg nasal spray | not found on FDA shortage list | $7.09 (generic) | only in some cases: > 1 inhaler/30 days | 96 of 96 |
| Triamcinolone 0.1% cream | not found on FDA shortage list | $1.34 (generic) | no | 96 of 96 |
| Epinephrine 0.3 mg auto-injector | not found on FDA shortage list | $268.72 (generic) | no | 96 of 96 |
| Nicotine 21 mg patch | not found on FDA shortage list | $55.62 (generic) | no | 0 of 96 |
| Paxlovid dose pack | not found on FDA shortage list | $1,477.18 (brand) | only in some cases: < 12 years; or > 30 units/claim | 96 of 96 |

## Adderall XR 30 mg ER capsule

- **RxNorm:** amphetamine / amphetamine aspartate / amphetamine sulfate / dextroamphetamine saccharate / dextroamphetamine sulfate / dextroamphetamine — brands: Adderall — 2 RxCUIs, 27 NDCs. Controlled: yes, C-II.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Tablet (current shortage). Those are different products. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.48 per EA (median of 11 NDCs) -> about $14.28 for 30 capsules (1 a day); Brand: $6.81 per EA (median of 1 NDCs) -> about $204.23 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 2 units/day. Covered. PA is needed for ages under 3 or 21 and older, or above 2 capsules a day. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amphetamine>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 17, tier 3: 37, tier 4: 29. Restrictions on that tier (number of plans): quantity limit: 72, prior auth: 17.
  - Average plan cost for 30 capsules (1 a day): $40.52 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Concerta 18 mg ER tablet

- **RxNorm:** methylphenidate — brands: Concerta — 2 RxCUIs, 23 NDCs. Controlled: yes, C-II.
- **FDA shortage:** in shortage. FDA lists a current shortage for 8 package(s) of this exact drug and strength. Some makers may still have it. Call the pharmacy to check. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'Available': 17, 'Limited Availability': 7, 'Unavailable': 1}
- **NADAC (as of 10/21/2026):** Generic: $0.61 per EA (median of 5 NDCs) -> about $18.29 for 30 tablets (1 a day); Brand: $12.33 per EA (median of 1 NDCs) -> about $369.80 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 2 units/day. Brand Concerta is preferred over generics. PA is needed for ages under 3 or 21 and older, or above 2 tablets a day. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=methylphenidate>)
- **Medicare Part D (Massachusetts):** on the formulary of 45 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 7, tier 2: 7, tier 3: 4, tier 4: 27. Restrictions on that tier (number of plans): quantity limit: 21.
  - Average plan cost for 30 tablets (1 a day): $46.67 (from 45 plans' pricing; this is the plan's drug price, not the patient's share).

## Atorvastatin 20 mg tablet

- **RxNorm:** atorvastatin — brands: Lipitor — 2 RxCUIs, 408 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 69 NDCs) -> about $0.86 for 30 tablets (1 a day); Brand: $19.06 per EA (median of 1 NDCs) -> about $571.75 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 1.5 units/day. Generic atorvastatin is covered. PA is needed only above 1.5 tablets a day. Brand Lipitor needs PA. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=atorvastatin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): quantity limit: 35.
  - Average plan cost for 30 tablets (1 a day): $5.75 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Lisinopril 10 mg tablet

- **RxNorm:** lisinopril — brands: Prinivil, Zestril — 3 RxCUIs, 250 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 34 NDCs) -> about $0.54 for 30 tablets (1 a day); Brand: $12.52 per EA (median of 1 NDCs) -> about $375.73 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=lisinopril>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): quantity limit: 17.
  - Average plan cost for 30 tablets (1 a day): $3.40 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Levothyroxine 50 mcg tablet

- **RxNorm:** levothyroxine — brands: Euthyrox, Levo-T, Levoxyl, Synthroid, Unithroid — 6 RxCUIs, 166 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 27 NDCs) -> about $1.20 for 30 tablets (1 a day); Brand: $1.66 per EA (median of 6 NDCs) -> about $49.86 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=levothyroxine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 82, tier 2: 14. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $4.69 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Metformin 500 mg tablet

- **RxNorm:** metformin — brands: not found — 1 RxCUIs, 507 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.01 per EA (median of 57 NDCs) -> about $0.89 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=metformin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): quantity limit: 52.
  - Average plan cost for 60 tablets (1 twice a day): $5.56 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amlodipine 5 mg tablet

- **RxNorm:** amlodipine — brands: Norvasc — 2 RxCUIs, 293 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.01 per EA (median of 35 NDCs) -> about $0.30 for 30 tablets (1 a day); Brand: $8.69 per EA (median of 6 NDCs) -> about $260.85 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic amlodipine is covered without PA. Brand Norvasc needs PA. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amlodipine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $2.84 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Omeprazole 20 mg DR capsule

- **RxNorm:** omeprazole — brands: Prilosec — 2 RxCUIs, 660 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 43 NDCs) -> about $0.91 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 4 units/day. Covered. PA is needed above 4 capsules a day. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=omeprazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 61, tier 2: 35. Restrictions on that tier (number of plans): quantity limit: 26.
  - Average plan cost for 30 capsules (1 a day): $4.56 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Sertraline 50 mg tablet

- **RxNorm:** sertraline — brands: Zoloft — 2 RxCUIs, 327 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 41 NDCs) -> about $1.05 for 30 tablets (1 a day); Brand: $14.92 per EA (median of 3 NDCs) -> about $447.53 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. Generic sertraline tablets are covered; PA is needed for children under 6. Brand Zoloft needs PA. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sertraline>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): quantity limit: 23.
  - Average plan cost for 30 tablets (1 a day): $3.85 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amoxicillin 500 mg capsule

- **RxNorm:** amoxicillin — brands: Trimox — 2 RxCUIs, 427 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.08 per EA (median of 19 NDCs) -> about $2.38 for 30 capsules (a typical 10-day course, 3 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amoxicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 70, tier 2: 26. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 capsules (a typical 10-day course, 3 a day): $4.08 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Ozempic (semaglutide) 0.5 mg pen

- **RxNorm:** semaglutide — brands: Ozempic — 2 RxCUIs, 5 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $332.02 per ML (median of 2 NDCs) -> about $996.07 for 1 pen (3 mL), about 1 month at 0.5 mg weekly
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=semaglutide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 83, tier 6: 1. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 73.
  - Average plan cost for 1 pen (3 mL), about 1 month at 0.5 mg weekly: $998.21 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Mounjaro (tirzepatide) 5 mg pen

- **RxNorm:** tirzepatide — brands: Mounjaro — 2 RxCUIs, 3 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $538.70 per ML (median of 1 NDCs) -> about $1,077.39 for 4 single-dose pens (0.5 mL each), 1 a week
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=tirzepatide>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 82, tier 6: 1. Restrictions on that tier (number of plans): prior auth: 95, quantity limit: 72.
  - Average plan cost for 4 single-dose pens (0.5 mL each), 1 a week: $1,080.20 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Eliquis (apixaban) 5 mg tablet

- **RxNorm:** apixaban — brands: Eliquis — 2 RxCUIs, 23 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $5.52 per EA (median of 3 NDCs) -> about $331.29 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. BP: Brand preferred over generics: MassHealth wants the brand tried first. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=apixaban>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 66.
  - Average plan cost for 60 tablets (1 twice a day): $248.71 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Eliquis has a Medicare negotiated price (Maximum Fair Price) starting January 1, 2026.

## Humira (adalimumab) 40 mg pen

- **RxNorm:** adalimumab — brands: Humira — 2 RxCUIs, 6 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $3,367.85 per EA (median of 1 NDCs) -> about $6,735.70 for 2 pens (every other week)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. Humira needs PA. Hadlima and unbranded adalimumab-adaz are the preferred adalimumab products (also PA). (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=adalimumab>)
- **Medicare Part D (Massachusetts):** on the formulary of 62 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 5: 50. Restrictions on that tier (number of plans): prior auth: 62, quantity limit: 62.
  - Average plan cost for 2 pens (every other week): $6,666.18 (from 62 plans' pricing; this is the plan's drug price, not the patient's share).

## Dupixent (dupilumab) 300 mg pen

- **RxNorm:** dupilumab — brands: Dupixent — 2 RxCUIs, 4 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $1,008.94 per ML (median of 1 NDCs) -> about $4,035.76 for 2 pens (2 mL each), every other week
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=dupilumab>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 5: 84. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 73.
  - Average plan cost for 2 pens (2 mL each), every other week: $4,073.75 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Albuterol HFA 90 mcg inhaler

- **RxNorm:** albuterol — brands: ProAir, Proventil, Ventolin — 6 RxCUIs, 60 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.83 per GM (median of 12 NDCs) -> about $32.98 for 1 inhaler (18 g size; some brands are 6.7 g or 8.5 g); Brand: $3.03 per GM (median of 1 NDCs) -> about $54.61 for 1 inhaler (18 g size; some brands are 6.7 g or 8.5 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. Ventolin HFA (brand) is the preferred inhaler with no PA. Other albuterol HFA inhalers need PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=albuterol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 69, tier 3: 15. Restrictions on that tier (number of plans): quantity limit: 79.
  - Average plan cost for 1 inhaler (18 g size; some brands are 6.7 g or 8.5 g): $32.53 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Insulin glargine (Lantus SoloStar) pen

- **RxNorm:** insulin glargine — brands: Lantus — 2 RxCUIs, 10 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $6.16 per ML (median of 1 NDCs) -> about $92.46 for 1 box of 5 pens (3 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Lantus (brand) is preferred and covered without PA. Other insulin glargine products need PA. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=insulin+glargine>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 83. Restrictions on that tier (number of plans): quantity limit: 7.
  - Average plan cost for 1 box of 5 pens (3 mL each): $93.79 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Amoxicillin 400 mg/5 mL oral suspension

- **RxNorm:** amoxicillin — brands: not found — 1 RxCUIs, 62 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per ML (median of 18 NDCs) -> about $3.92 for 1 bottle (100 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amoxicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 62, tier 2: 34. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (100 mL): $4.92 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Sumatriptan 50 mg tablet

- **RxNorm:** sumatriptan — brands: Imitrex — 2 RxCUIs, 57 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.31 per EA (median of 13 NDCs) -> about $2.81 for 9 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 16 units/30 days. Generic sumatriptan tablets are covered up to 16 tablets per 30 days; more needs PA. Brand Imitrex needs PA. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sumatriptan>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 16, tier 2: 80. Restrictions on that tier (number of plans): quantity limit: 73.
  - Average plan cost for 9 tablets: $6.55 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Latanoprost 0.005% eye drops

- **RxNorm:** latanoprost — brands: Iyuzeh, Xalatan — 3 RxCUIs, 26 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.57 per ML (median of 10 NDCs) -> about $3.93 for 1 bottle (2.5 mL); Brand: $108.34 per ML (median of 1 NDCs) -> about $270.86 for 1 bottle (2.5 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic latanoprost is covered without PA. Brand Xalatan needs PA. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=latanoprost>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 68, tier 2: 28. Restrictions on that tier (number of plans): quantity limit: 15.
  - Average plan cost for 1 bottle (2.5 mL): $6.17 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Fluticasone 50 mcg nasal spray

- **RxNorm:** fluticasone — brands: Aller-Flo, Clarispray, Flonase, Fluticare, Nasopro 24 — 6 RxCUIs, 307 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.44 per GM (median of 6 NDCs) -> about $7.09 for 1 bottle (16 g, about 120 sprays)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 1 inhaler/30 days. Covered. PA is needed above 1 bottle per 30 days. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=fluticasone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 48, tier 2: 48. Restrictions on that tier (number of plans): quantity limit: 71.
  - Average plan cost for 1 bottle (16 g, about 120 sprays): $10.74 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Triamcinolone 0.1% cream

- **RxNorm:** triamcinolone — brands: Triderm — 2 RxCUIs, 151 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per GM (median of 31 NDCs) -> about $1.34 for 1 tube (30 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=triamcinolone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 29, tier 2: 66, tier 3: 1. Restrictions on that tier (number of plans): quantity limit: 36.
  - Average plan cost for 1 tube (30 g): $2.26 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Epinephrine 0.3 mg auto-injector

- **RxNorm:** epinephrine — brands: Auvi-Q, Epipen — 5 RxCUIs, 36 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $134.36 per EA (median of 6 NDCs) -> about $268.72 for 1 two-pack of auto-injectors; Brand: $309.38 per EA (median of 2 NDCs) -> about $618.75 for 1 two-pack of auto-injectors
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic epinephrine auto-injectors are covered without PA. Brand EpiPen needs PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=epinephrine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 3: 74. Restrictions on that tier (number of plans): quantity limit: 61.
  - Average plan cost for 1 two-pack of auto-injectors: $255.16 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Nicotine 21 mg patch

- **RxNorm:** nicotine — brands: Habitrol, Nicduic, Nicoderm C-Q — 4 RxCUIs, 120 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.99 per EA (median of 28 NDCs) -> about $55.62 for 28 patches
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic nicotine patches (OTC) are payable without PA. *: The generic OTC (and generic prescription) versions are payable without PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=nicotine>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Paxlovid dose pack

- **RxNorm:** nirmatrelvir / ritonavir — brands: Paxlovid 5-Day — 2 RxCUIs, 8 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-23, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $49.24 per EA (median of 1 NDCs) -> about $1,477.18 for 1 five-day dose pack (30 tablets)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 12 years; or > 30 units/claim. Covered. PA is needed for children under 12, or above 30 tablets per claim. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=nirmatrelvir>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 23, tier 3: 39, tier 5: 22. Restrictions on that tier (number of plans): quantity limit: 96.
  - Average plan cost for 1 five-day dose pack (30 tablets): $1,498.36 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Vaccines

Checked 2026-10-23. Vaccine rules changed in 2025-2026. Re-check official sources before relying on this.

**Massachusetts commercial insurance (Massachusetts Bulletin 2025-03 (Division of Insurance and Department of Public Health, issued September 3, 2025)):** Insurers must cover vaccines recommended by the Massachusetts Department of Public Health (DPH), not only CDC recommendations. No cost-sharing and no utilization management (no prior authorization delays) for covered routine vaccines. Applies to: Fully insured health plans issued under Massachusetts law (for example Blue Cross Blue Shield of Massachusetts and HMOs). Group Insurance Commission (GIC) plans and MassHealth also cover vaccines according to DPH guidelines. Self-insured employer plans are not required to follow the bulletin. Insurers may cover only certain brands, as long as at least one product covers each DPH-recommended vaccine. Patient message: "If your plan is through a large employer, check with your plan, because it may not have to follow the Massachusetts rule." DPH list: <https://www.mass.gov/info-details/dph-recommended-guidance-for-vaccines>. Sources: <https://www.mass.gov/doc/bulletin-2025-03-coverage-for-vaccines-issued-september-3-2025/download>, <https://www.mass.gov/info-details/frequently-asked-questions-about-vaccinations>, <https://www.mass.gov/info-details/dph-recommended-guidance-for-vaccines> (verified via web search, 2026-10-23 (mass.gov could not be opened directly)).

| Vaccine | Group | Medicare | MassHealth | Commercial (federal ACA list) | Massachusetts fully insured plans |
|---|---|---|---|---|---|
| Flu (influenza) | routine | Part B: $0 if the provider accepts Medicare assignment (no deductible or coinsurance for Part B vaccines) | Listed on the MassHealth Drug List (some products need PA for certain ages: Fluad PA < 65 years; Flumist PA; Fluzone PA < 65 years; Mflusiva PA < 50 years) | Listed on HealthCare.gov's adult preventive services list. Marketplace plans and many other plans must cover it. | Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03) |
| COVID-19 | routine | Part B: $0 if the provider accepts Medicare assignment (no deductible or coinsurance for Part B vaccines) | Listed on the MassHealth Drug List, no PA. | Not on HealthCare.gov's adult preventive services list. Coverage depends on the plan: not found. | Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03) |
| Hepatitis B | routine | Part B (for some people): $0 if the provider accepts Medicare assignment (no deductible or coinsurance for Part B vaccines) | Listed on the MassHealth Drug List, no PA. | Listed on HealthCare.gov's adult preventive services list. Marketplace plans and many other plans must cover it. | Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03) |
| Shingles (Shingrix) | routine | Part D: $0 for ACIP-recommended adult vaccines, even before the deductible | Listed on the MassHealth Drug List (some products need PA for certain ages: Shingrix PA < 50 years) | Listed on HealthCare.gov's adult preventive services list. Marketplace plans and many other plans must cover it. | Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03) |
| RSV | routine | Part D: $0 for ACIP-recommended adult vaccines, even before the deductible | Listed on the MassHealth Drug List (some products need PA for certain ages: Abrysvo PA < 18 years; Arexvy PA < 50 years; Mresvia PA < 18 years) | Not on HealthCare.gov's adult preventive services list. Coverage depends on the plan: not found. | Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03) |
| Pneumococcal (pneumonia) | routine | Part B: $0 if the provider accepts Medicare assignment (no deductible or coinsurance for Part B vaccines) | Listed on the MassHealth Drug List, no PA. | Listed on HealthCare.gov's adult preventive services list. Marketplace plans and many other plans must cover it. | Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03) |
| Tdap (tetanus, diphtheria, whooping cough) | routine | Part D (Part B if given to treat an injury): $0 for ACIP-recommended adult vaccines, even before the deductible | Listed on the MassHealth Drug List, no PA. | Listed on HealthCare.gov's adult preventive services list. Marketplace plans and many other plans must cover it. | Covered if DPH recommends it; no cost-sharing, no PA (Bulletin 2025-03) |
| Hepatitis A | travel | Part D (Part B only if given after an exposure): $0 under Part D if ACIP recommends it for you; otherwise the plan may charge a copay (CMS) | Listed on the MassHealth Drug List, no PA. | Hepatitis A is on HealthCare.gov's adult preventive list ('recommended populations vary'). Coverage for travel only: not found. | The bulletin covers routine vaccines only. Travel vaccines (hepatitis A for travel, typhoid, yellow fever) are not part of it. Check with your plan. |
| Typhoid | travel | Part not found: not found | Listed on the MassHealth Drug List, no PA. | Not on HealthCare.gov's adult preventive services list. Coverage depends on the plan: not found. | The bulletin covers routine vaccines only. Travel vaccines (hepatitis A for travel, typhoid, yellow fever) are not part of it. Check with your plan. |
| Yellow fever | travel | Part D: Part D won't charge a copay or deductible for vaccines ACIP recommends | Listed on the MassHealth Drug List, no PA. | Not on HealthCare.gov's adult preventive services list. Coverage depends on the plan: not found. | The bulletin covers routine vaccines only. Travel vaccines (hepatitis A for travel, typhoid, yellow fever) are not part of it. Check with your plan. |

- **Hepatitis A:** CDC: travelers to countries where hepatitis A is common should get vaccinated. Travel vaccines are often not covered by insurance. CDC: 'many health insurance plans provide no or limited coverage for travel immunizations.' Call your plan first.
- **Typhoid:** CDC: oral (4 capsules, ages 6+) or shot (ages 2+), at least 2 weeks before travel. Travel vaccines are often not covered by insurance. CDC: 'many health insurance plans provide no or limited coverage for travel immunizations.' Call your plan first.
- **Yellow fever:** Yellow fever vaccine is given ONLY at certified (designated) yellow fever vaccination centers. Most pharmacies cannot give it. Find a certified clinic with CDC's search tool: https://wwwnc.cdc.gov/travel/yellow-fever-vaccination-clinics/search For people 9 months and older traveling to at-risk areas of Africa and South America. Travel vaccines are often not covered by insurance. CDC: 'many health insurance plans provide no or limited coverage for travel immunizations.' Call your plan first.

Not checked: mass.gov pages could not be opened directly (HTTP 403). The Massachusetts rule above was verified via web search, 2026-10-23 (mass.gov could not be opened directly). MassHealth pharmacy bulletins on mass.gov could not be opened (HTTP 403).
