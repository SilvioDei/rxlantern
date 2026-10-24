# Medication data check

Checked: 2026-10-24. For pharmacist review. Every fact lists its source. 150 drugs.

- **Drug list:** the 25 drugs from Step 3 plus 125 chosen from ClinCalc DrugStats Database, The Top 300 of 2024 (version 2026.08, updated August 9, 2026) (<https://clincalc.com/DrugStats/Top300Drugs.aspx>; data: Medical Expenditure Panel Survey (MEPS) 2024, Agency for Healthcare Research and Quality (AHRQ); checked 2026-10-24), adding shortage-prone and high-cost medicines (GLP-1s, inhalers, insulins, children's antibiotic liquids, ADHD medicines). Names, RxCUIs, and NDCs from RxNorm (RxNav API).
- **DEA schedule:** from the openFDA NDC directory (<https://open.fda.gov/apis/drug/ndc/>, last updated 2026-10-23), matched by RxCUI and package NDC; never typed by hand.
- **NADAC** is what pharmacies pay to buy the drug (CMS survey), not the patient's price. The 30-day estimate = NADAC per unit x the amount shown. It leaves out the pharmacy's dispensing fee and markup.
- **Medicare counts** are Massachusetts Part D plans (stand-alone PDPs and Medicare Advantage drug plans) in the CMS 2026 quarterly file; 96 plan segments in total.
- **MassHealth** status is from the MassHealth Drug List (last updated 10/05/26). Rule: any drug not on the list requires prior authorization (PA).
- **Shortage** status is from the openFDA drug shortages API (snapshot 2026-10-24).

## 2026 Medicare Part D rules

- **Yearly out-of-pocket cap for covered Part D drugs:** $2,100 in 2026 ($2,400 in 2027). — <https://www.medicare.gov/drug-coverage-part-d/costs-for-medicare-drug-coverage>
- **Highest Part D deductible a plan may charge:** $615 in 2026 ($700 in 2027) — <https://www.medicare.gov/drug-coverage-part-d/costs-for-medicare-drug-coverage>
- **Insulin cap:** No more than $35 for a one-month supply of each Part B- or Part D-covered insulin product, and no deductible for insulin. — <https://www.medicare.gov/coverage/insulin>
- **Drugs with a Medicare negotiated price (Maximum Fair Price) starting January 1, 2026:** Eliquis, Jardiance, Xarelto, Januvia, Farxiga, Entresto, Enbrel, Imbruvica, Stelara, Fiasp / NovoLog insulin aspart products — <https://www.cms.gov/files/document/infographic-negotiated-prices-maximum-fair-prices.pdf>
- **Which RxLantern drugs have a Medicare negotiated price in 2026:** Eliquis (apixaban): 56% off the 2023 list price for a 30-day supply, Januvia (sitagliptin): 79% off the 2023 list price for a 30-day supply, NovoLog / Fiasp insulin aspart products: 76% off the 2023 list price for a 30-day supply, Farxiga (dapagliflozin): 68% off the 2023 list price for a 30-day supply, Enbrel (etanercept): 67% off the 2023 list price for a 30-day supply, Jardiance (empagliflozin): 66% off the 2023 list price for a 30-day supply, Xarelto (rivaroxaban): 62% off the 2023 list price for a 30-day supply, Entresto (sacubitril/valsartan): 53% off the 2023 list price for a 30-day supply — <https://www.cms.gov/files/document/infographic-negotiated-prices-maximum-fair-prices.pdf>
- **When the 2026 negotiated prices start:** January 1, 2026 — <https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026>

## Please review first

Unusual items for a pharmacist to check before anything else. NADAC estimates are what pharmacies pay, not what patients pay.

### Controlled drugs (every one flagged; DEA schedule from openFDA) (18)

- Adderall XR 30 mg ER capsule: **C-II** (openFDA NDC directory: 76 products matched; schedules seen {'CII': 76}). No pharmacy-level stock reports; shortage status and call script only.
- Concerta 18 mg ER tablet: **C-II** (openFDA NDC directory: 40 products matched; schedules seen {'CII': 40}). No pharmacy-level stock reports; shortage status and call script only.
- Alprazolam 0.5 mg tablet: **C-IV** (openFDA NDC directory: 66 products matched; schedules seen {'CIV': 66}). No pharmacy-level stock reports; shortage status and call script only.
- Clonazepam 0.5 mg tablet: **C-IV** (openFDA NDC directory: 75 products matched; schedules seen {'CIV': 75}). No pharmacy-level stock reports; shortage status and call script only.
- Lorazepam 0.5 mg tablet: **C-IV** (openFDA NDC directory: 67 products matched; schedules seen {'CIV': 67}). No pharmacy-level stock reports; shortage status and call script only.
- Zolpidem 10 mg tablet: **C-IV** (openFDA NDC directory: 66 products matched; schedules seen {'CIV': 66}). No pharmacy-level stock reports; shortage status and call script only.
- Amphetamine salts (Adderall) 10 mg tablet: **C-II** (openFDA NDC directory: 111 products matched; schedules seen {'CII': 111}). No pharmacy-level stock reports; shortage status and call script only.
- Lisdexamfetamine (Vyvanse) 30 mg capsule: **C-II** (openFDA NDC directory: 119 products matched; schedules seen {'CII': 119}). No pharmacy-level stock reports; shortage status and call script only.
- Methylphenidate (Ritalin) 10 mg tablet: **C-II** (openFDA NDC directory: 42 products matched; schedules seen {'CII': 42}). No pharmacy-level stock reports; shortage status and call script only.
- Dexmethylphenidate ER (Focalin XR) 10 mg capsule: **C-II** (openFDA NDC directory: 54 products matched; schedules seen {'CII': 54}). No pharmacy-level stock reports; shortage status and call script only.
- Hydrocodone/acetaminophen 5/325 mg tablet: **C-II** (openFDA NDC directory: 101 products matched; schedules seen {'CII': 101}). No pharmacy-level stock reports; shortage status and call script only.
- Oxycodone 5 mg tablet: **C-II** (openFDA NDC directory: 86 products matched; schedules seen {'CII': 86}). No pharmacy-level stock reports; shortage status and call script only.
- Oxycodone/acetaminophen (Percocet) 5/325 mg tablet: **C-II** (openFDA NDC directory: 82 products matched; schedules seen {'CII': 82}). No pharmacy-level stock reports; shortage status and call script only.
- Tramadol 50 mg tablet: **C-IV** (openFDA NDC directory: 65 products matched; schedules seen {'CIV': 65}). No pharmacy-level stock reports; shortage status and call script only.
- Pregabalin (Lyrica) 75 mg capsule: **C-V** (openFDA NDC directory: 373 products matched; schedules seen {'CV': 373}). No pharmacy-level stock reports; shortage status and call script only.
- Buprenorphine/naloxone (Suboxone) 8/2 mg film: **C-III** (openFDA NDC directory: 27 products matched; schedules seen {'CIII': 27}). No pharmacy-level stock reports; shortage status and call script only.
- Phentermine 37.5 mg tablet: **C-IV** (openFDA NDC directory: 51 products matched; schedules seen {'CIV': 51}). No pharmacy-level stock reports; shortage status and call script only.
- Testosterone cypionate 200 mg/mL injection: **C-III** (openFDA NDC directory: 60 products matched; schedules seen {'none': 1, 'CIII': 59}). No pharmacy-level stock reports; shortage status and call script only.

### Very high cost estimates (NADAC 30-day estimate above $1,000.00) (9)

- Mounjaro (tirzepatide) 5 mg pen: about $1,077.39 for 4 single-dose pens (0.5 mL each), 1 a week (brand)
- Humira (adalimumab) 40 mg pen: about $6,735.70 for 2 pens (every other week) (brand)
- Dupixent (dupilumab) 300 mg pen: about $4,035.76 for 2 pens (2 mL each), every other week (brand)
- Paxlovid dose pack: about $1,477.18 for 1 five-day dose pack (30 tablets) (brand)
- Wegovy (semaglutide) 2.4 mg pen: about $1,306.72 for 4 single-dose pens (0.75 mL each), 1 a week (brand)
- Zepbound (tirzepatide) 2.5 mg pen: about $1,052.46 for 4 single-dose pens (0.5 mL each), 1 a week (brand)
- Biktarvy (bictegravir/emtricitabine/tenofovir alafenamide) tablet: about $4,102.59 for 30 tablets (1 a day) (brand)
- Enbrel (etanercept) 50 mg pen: about $8,334.50 for 4 pens (1 a week) (brand)
- Nurtec ODT (rimegepant) 75 mg: about $1,029.30 for 8 tablets (brand)

### Very low cost estimates (NADAC 30-day estimate below $1.00) (24)

- Atorvastatin 20 mg tablet: about $0.86 for 30 tablets (1 a day)
- Lisinopril 10 mg tablet: about $0.54 for 30 tablets (1 a day)
- Metformin 500 mg tablet: about $0.89 for 60 tablets (1 twice a day)
- Amlodipine 5 mg tablet: about $0.30 for 30 tablets (1 a day)
- Omeprazole 20 mg DR capsule: about $0.91 for 30 capsules (1 a day)
- Sulfamethoxazole/trimethoprim DS 800/160 mg tablet (Bactrim DS): about $0.91 for 20 tablets (a 10-day course, 2 a day)
- Fluconazole 150 mg tablet: about $0.51 for 1 tablet
- Losartan 50 mg tablet: about $0.99 for 30 tablets (1 a day)
- Metoprolol tartrate 25 mg tablet: about $0.96 for 60 tablets (1 twice a day)
- Hydrochlorothiazide 25 mg tablet: about $0.34 for 30 tablets (1 a day)
- Simvastatin 20 mg tablet: about $0.97 for 30 tablets (1 a day)
- Furosemide 20 mg tablet: about $0.75 for 30 tablets (1 a day)
- Fluoxetine 20 mg capsule: about $0.88 for 30 capsules (1 a day)
- Trazodone 50 mg tablet: about $0.90 for 30 tablets (1 a day)
- Hydroxyzine HCl 25 mg tablet: about $0.97 for 30 tablets
- Quetiapine 25 mg tablet: about $0.63 for 30 tablets (1 a day)
- Alprazolam 0.5 mg tablet: about $0.68 for 30 tablets
- Clonazepam 0.5 mg tablet: about $0.59 for 30 tablets
- Tramadol 50 mg tablet: about $0.78 for 30 tablets
- Meloxicam 15 mg tablet: about $0.55 for 30 tablets (1 a day)
- Cyclobenzaprine 10 mg tablet: about $0.52 for 30 tablets
- Prednisone 20 mg tablet: about $0.65 for 10 tablets
- Allopurinol 100 mg tablet: about $0.94 for 30 tablets (1 a day)
- Vitamin D2 (ergocalciferol) 50,000 unit capsule: about $0.46 for 4 capsules (1 a week)

### No NADAC price for the estimate (0)

- none

### No MassHealth Drug List match or not checked (2)

- Benzonatate 100 mg capsule: not found on the MassHealth Drug List search (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=benzonatate>). MassHealth rule: drugs not on the list need prior authorization.
- Phentermine 37.5 mg tablet: not found on the MassHealth Drug List search (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=phentermine>). MassHealth rule: drugs not on the list need prior authorization.

### No Massachusetts Medicare Part D match (8)

- Nicotine 21 mg patch: on no Massachusetts Part D plan formulary in the CMS 2026 file.
- Rybelsus (semaglutide) 7 mg tablet: on no Massachusetts Part D plan formulary in the CMS 2026 file.
- Zepbound (tirzepatide) 2.5 mg pen: on no Massachusetts Part D plan formulary in the CMS 2026 file.
- Benzonatate 100 mg capsule: on no Massachusetts Part D plan formulary in the CMS 2026 file.
- Naloxone 4 mg nasal spray (Narcan): on no Massachusetts Part D plan formulary in the CMS 2026 file.
- Diclofenac 1% gel: on no Massachusetts Part D plan formulary in the CMS 2026 file.
- Phentermine 37.5 mg tablet: on no Massachusetts Part D plan formulary in the CMS 2026 file.
- Vitamin D2 (ergocalciferol) 50,000 unit capsule: on no Massachusetts Part D plan formulary in the CMS 2026 file.

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
| Wegovy (semaglutide) 2.4 mg pen | not found on FDA shortage list | $1,306.72 (brand) | yes | 8 of 96 |
| Rybelsus (semaglutide) 7 mg tablet | shortage resolved or discontinued | $995.84 (brand) | yes | 0 of 96 |
| Zepbound (tirzepatide) 2.5 mg pen | not found on FDA shortage list | $1,052.46 (brand) | yes | 0 of 96 |
| Trulicity (dulaglutide) 1.5 mg pen | not found on FDA shortage list | $975.24 (brand) | yes | 93 of 96 |
| Victoza (liraglutide) pen | in shortage | $173.31 (generic) | yes | 18 of 96 |
| Jardiance (empagliflozin) 10 mg tablet | not found on FDA shortage list | $335.67 (brand) | no | 96 of 96 |
| Farxiga (dapagliflozin) 10 mg tablet | not found on FDA shortage list | $5.53 (generic) | no | 96 of 96 |
| Januvia (sitagliptin) 100 mg tablet | not found on FDA shortage list | $115.48 (generic) | yes | 96 of 96 |
| Glipizide 5 mg tablet | not found on FDA shortage list | $1.97 (generic) | no | 96 of 96 |
| Pioglitazone 30 mg tablet | not found on FDA shortage list | $2.90 (generic) | no | 96 of 96 |
| Metformin ER 500 mg tablet | not found on FDA shortage list | $1.70 (generic) | no | 96 of 96 |
| Insulin lispro (Humalog KwikPen) pen | shortage resolved or discontinued | $152.87 (generic) | no | 78 of 96 |
| Insulin aspart (NovoLog FlexPen) pen | not found on FDA shortage list | $134.41 (generic) | yes | 96 of 96 |
| Insulin degludec (Tresiba FlexTouch) pen | not found on FDA shortage list | $170.86 (generic) | yes | 36 of 96 |
| Toujeo SoloStar (insulin glargine 300 units/mL) pen | not found on FDA shortage list | $121.44 (generic) | yes | 96 of 96 |
| Insulin NPH (Humulin N / Novolin N) pen | not found on FDA shortage list | $111.39 (brand) | no | 96 of 96 |
| Fluticasone/salmeterol (Advair Diskus) 250/50 inhaler | not found on FDA shortage list | $72.47 (generic) | no | 90 of 96 |
| Budesonide/formoterol (Symbicort) 160/4.5 inhaler | not found on FDA shortage list | $176.65 (generic) | no | 96 of 96 |
| Trelegy Ellipta 100/62.5/25 inhaler | not found on FDA shortage list | $334.56 (brand) | yes | 96 of 96 |
| Tiotropium (Spiriva HandiHaler) 18 mcg capsules | not found on FDA shortage list | $356.89 (generic) | no | 44 of 96 |
| Fluticasone (Flovent HFA) 110 mcg inhaler | not found on FDA shortage list | $162.76 (generic) | only in some cases: >= 12 years | 33 of 96 |
| Albuterol 2.5 mg/3 mL nebulizer solution | not found on FDA shortage list | $4.61 (generic) | no | 96 of 96 |
| Ipratropium/albuterol (DuoNeb) nebulizer solution | not found on FDA shortage list | $6.88 (generic) | no | 96 of 96 |
| Budesonide 0.5 mg/2 mL nebulizer suspension (Pulmicort Respules) | not found on FDA shortage list | $37.60 (generic) | only in some cases: >= 13 years | 96 of 96 |
| Montelukast 10 mg tablet | shortage resolved or discontinued | $1.30 (generic) | no | 96 of 96 |
| Montelukast 5 mg chewable tablet (children) | shortage resolved or discontinued | $2.17 (generic) | no | 96 of 96 |
| Benzonatate 100 mg capsule | not found on FDA shortage list | $1.85 (generic) | not found | 0 of 96 |
| Naloxone 4 mg nasal spray (Narcan) | not found on FDA shortage list | $33.53 (generic) | no | 0 of 96 |
| Oseltamivir (Tamiflu) 75 mg capsule | not found on FDA shortage list | $7.98 (generic) | only in some cases: > 10 units/ claim; or > 20 units/ 365 days | 96 of 96 |
| Oseltamivir (Tamiflu) 6 mg/mL oral suspension | not found on FDA shortage list | $9.33 (generic) | only in some cases: > 180 mL/ claim; or > 360 mL/ 365 days | 96 of 96 |
| Amoxicillin 250 mg/5 mL oral suspension | not found on FDA shortage list | $2.49 (generic) | no | 96 of 96 |
| Amoxicillin/clavulanate (Augmentin) 875/125 mg tablet | not found on FDA shortage list | $5.64 (generic) | no | 96 of 96 |
| Amoxicillin/clavulanate 400/57 mg per 5 mL oral suspension | not found on FDA shortage list | $6.45 (generic) | no | 96 of 96 |
| Azithromycin (Z-Pak) 250 mg tablet | shortage resolved or discontinued | $1.63 (generic) | no | 96 of 96 |
| Azithromycin 200 mg/5 mL oral suspension | shortage resolved or discontinued | $3.58 (generic) | no | 96 of 96 |
| Cephalexin 500 mg capsule | not found on FDA shortage list | $3.27 (generic) | no | 96 of 96 |
| Cephalexin 250 mg/5 mL oral suspension | not found on FDA shortage list | $5.85 (generic) | no | 96 of 96 |
| Cefdinir 250 mg/5 mL oral suspension | not found on FDA shortage list | $6.88 (generic) | no | 96 of 96 |
| Doxycycline hyclate 100 mg capsule | not found on FDA shortage list | $2.16 (generic) | no | 96 of 96 |
| Sulfamethoxazole/trimethoprim DS 800/160 mg tablet (Bactrim DS) | not found on FDA shortage list | $0.91 (generic) | no | 96 of 96 |
| Sulfamethoxazole/trimethoprim 200/40 mg per 5 mL oral suspension | not found on FDA shortage list | $5.53 (generic) | no | 96 of 96 |
| Nitrofurantoin (Macrobid) 100 mg capsule | not found on FDA shortage list | $2.72 (generic) | no | 96 of 96 |
| Ciprofloxacin 500 mg tablet | not found on FDA shortage list | $1.69 (generic) | no | 96 of 96 |
| Metronidazole 500 mg tablet | not found on FDA shortage list | $1.46 (generic) | no | 96 of 96 |
| Penicillin VK 500 mg tablet | not found on FDA shortage list | $3.91 (generic) | no | 96 of 96 |
| Fluconazole 150 mg tablet | not found on FDA shortage list | $0.51 (generic) | no | 96 of 96 |
| Valacyclovir 1 g tablet | not found on FDA shortage list | $12.71 (generic) | no | 96 of 96 |
| Mupirocin 2% ointment | not found on FDA shortage list | $3.19 (generic) | no | 96 of 96 |
| Losartan 50 mg tablet | not found on FDA shortage list | $0.99 (generic) | no | 96 of 96 |
| Metoprolol succinate ER 50 mg tablet | shortage resolved or discontinued | $1.48 (generic) | no | 96 of 96 |
| Metoprolol tartrate 25 mg tablet | not found on FDA shortage list | $0.96 (generic) | no | 96 of 96 |
| Rosuvastatin 10 mg tablet | not found on FDA shortage list | $1.07 (generic) | only in some cases: > 1.5 units/day | 96 of 96 |
| Hydrochlorothiazide 25 mg tablet | not found on FDA shortage list | $0.34 (generic) | no | 96 of 96 |
| Simvastatin 20 mg tablet | not found on FDA shortage list | $0.97 (generic) | only in some cases: > 1.5 units/day | 96 of 96 |
| Pravastatin 40 mg tablet | not found on FDA shortage list | $2.37 (generic) | only in some cases: > 1.5 units/day | 96 of 96 |
| Furosemide 20 mg tablet | in shortage | $0.75 (generic) | no | 96 of 96 |
| Carvedilol 12.5 mg tablet | not found on FDA shortage list | $1.28 (generic) | no | 96 of 96 |
| Spironolactone 25 mg tablet | shortage resolved or discontinued | $1.28 (generic) | no | 96 of 96 |
| Clopidogrel 75 mg tablet | not found on FDA shortage list | $1.41 (generic) | no | 96 of 96 |
| Valsartan 160 mg tablet | shortage resolved or discontinued | $3.17 (generic) | no | 96 of 96 |
| Ezetimibe 10 mg tablet | not found on FDA shortage list | $2.11 (generic) | no | 96 of 96 |
| Propranolol 10 mg tablet | not found on FDA shortage list | $2.78 (generic) | no | 96 of 96 |
| Xarelto (rivaroxaban) 20 mg tablet | shortage resolved or discontinued | $586.18 (brand) | no | 96 of 96 |
| Warfarin 5 mg tablet | not found on FDA shortage list | $2.67 (generic) | no | 96 of 96 |
| Entresto (sacubitril/valsartan) 49/51 mg tablet | not found on FDA shortage list | $32.56 (generic) | only in some cases: > 2 units/day | 96 of 96 |
| Repatha (evolocumab) 140 mg pen | not found on FDA shortage list | $564.02 (brand) | yes | 94 of 96 |
| Brilinta (ticagrelor) 90 mg tablet | not found on FDA shortage list | $14.57 (generic) | no | 96 of 96 |
| Nitroglycerin 0.4 mg sublingual tablet | not found on FDA shortage list | $3.24 (generic) | no | 96 of 96 |
| Escitalopram 10 mg tablet | not found on FDA shortage list | $1.17 (generic) | only in some cases: < 6 years | 96 of 96 |
| Bupropion XL 150 mg tablet | not found on FDA shortage list | $2.35 (generic) | only in some cases: < 6 years; or > 1 unit/day | 96 of 96 |
| Fluoxetine 20 mg capsule | not found on FDA shortage list | $0.88 (generic) | only in some cases: < 6 years | 96 of 96 |
| Trazodone 50 mg tablet | not found on FDA shortage list | $0.90 (generic) | only in some cases: < 6 years | 96 of 96 |
| Duloxetine 60 mg DR capsule | not found on FDA shortage list | $4.10 (generic) | only in some cases: < 6 years | 96 of 96 |
| Buspirone 10 mg tablet | not found on FDA shortage list | $1.66 (generic) | only in some cases: < 6 years | 96 of 96 |
| Venlafaxine ER 75 mg capsule | not found on FDA shortage list | $2.40 (generic) | only in some cases: < 6 years | 96 of 96 |
| Hydroxyzine HCl 25 mg tablet | not found on FDA shortage list | $0.97 (generic) | no | 96 of 96 |
| Quetiapine 25 mg tablet | not found on FDA shortage list | $0.63 (generic) | only in some cases: < 10 years; or > 3 units/day | 96 of 96 |
| Aripiprazole 5 mg tablet | not found on FDA shortage list | $3.50 (generic) | only in some cases: < 10 years; or > 2 units/day | 96 of 96 |
| Lamotrigine 100 mg tablet | not found on FDA shortage list | $1.45 (generic) | only in some cases: < 6 years | 96 of 96 |
| Alprazolam 0.5 mg tablet | not found on FDA shortage list | $0.68 (generic) | only in some cases: < 6 years | 96 of 96 |
| Clonazepam 0.5 mg tablet | in shortage | $0.59 (generic) | only in some cases: < 6 years | 96 of 96 |
| Lorazepam 0.5 mg tablet | not found on FDA shortage list | $1.09 (generic) | only in some cases: < 6 years | 96 of 96 |
| Zolpidem 10 mg tablet | not found on FDA shortage list | $1.17 (generic) | only in some cases: < 6 years; or > 1 unit/day | 96 of 96 |
| Amphetamine salts (Adderall) 10 mg tablet | in shortage | $13.63 (generic) | only in some cases: < 3 years or >= 21 years; or > 3 units/day | 96 of 96 |
| Lisdexamfetamine (Vyvanse) 30 mg capsule | in shortage | $86.54 (generic) | only in some cases: < 3 years or >= 21 years; or > 2 units/day | 33 of 96 |
| Methylphenidate (Ritalin) 10 mg tablet | not found on FDA shortage list | $8.98 (generic) | only in some cases: < 3 years or >= 21 years; or > 3 units/day | 96 of 96 |
| Dexmethylphenidate ER (Focalin XR) 10 mg capsule | not found on FDA shortage list | $41.78 (generic) | only in some cases: < 3 years or >= 21 years; or > 2 units/day | 58 of 96 |
| Atomoxetine (Strattera) 40 mg capsule | not found on FDA shortage list | $13.34 (generic) | only in some cases: < 6 years | 96 of 96 |
| Guanfacine ER (Intuniv) 1 mg tablet | shortage resolved or discontinued | $3.97 (generic) | only in some cases: < 3 years | 95 of 96 |
| Hydrocodone/acetaminophen 5/325 mg tablet | not found on FDA shortage list | $2.64 (generic) | only in some cases: > 120 mg/day hydrocodone; or > 4 g/day acetaminophen | 96 of 96 |
| Oxycodone 5 mg tablet | not found on FDA shortage list | $1.85 (generic) | only in some cases: > 80 mg/day | 96 of 96 |
| Oxycodone/acetaminophen (Percocet) 5/325 mg tablet | shortage resolved or discontinued | $2.36 (generic) | only in some cases: > 80 mg/day oxycodone; or > 4 g/day acetaminophen | 96 of 96 |
| Tramadol 50 mg tablet | not found on FDA shortage list | $0.78 (generic) | only in some cases: < 12 years; or > 400 mg/day | 96 of 96 |
| Gabapentin 300 mg capsule | not found on FDA shortage list | $2.95 (generic) | only in some cases: < 6 years; or > 3600 mg/day | 96 of 96 |
| Pregabalin (Lyrica) 75 mg capsule | not found on FDA shortage list | $3.34 (generic) | only in some cases: < 6 years; or > 600 mg/day | 96 of 96 |
| Buprenorphine/naloxone (Suboxone) 8/2 mg film | not found on FDA shortage list | $58.45 (generic) | only in some cases: > 32 mg/day | 89 of 96 |
| Meloxicam 15 mg tablet | not found on FDA shortage list | $0.55 (generic) | no | 96 of 96 |
| Ibuprofen 800 mg tablet | not found on FDA shortage list | $5.00 (generic) | no | 96 of 96 |
| Cyclobenzaprine 10 mg tablet | not found on FDA shortage list | $0.52 (generic) | only in some cases: < 15 years | 96 of 96 |
| Diclofenac 1% gel | not found on FDA shortage list | $8.05 (generic) | no | 0 of 96 |
| Phentermine 37.5 mg tablet | not found on FDA shortage list | $2.21 (generic) | not found | 0 of 96 |
| Testosterone cypionate 200 mg/mL injection | not found on FDA shortage list | $11.01 (generic) | yes | 95 of 96 |
| Pantoprazole 40 mg DR tablet | not found on FDA shortage list | $1.10 (generic) | only in some cases: > 4 units/day | 96 of 96 |
| Famotidine 20 mg tablet | not found on FDA shortage list | $1.69 (generic) | no | 96 of 96 |
| Ondansetron 4 mg orally disintegrating tablet | not found on FDA shortage list | $2.46 (generic) | no | 96 of 96 |
| Linzess (linaclotide) 145 mcg capsule | not found on FDA shortage list | $270.56 (brand) | yes | 96 of 96 |
| Prednisone 20 mg tablet | not found on FDA shortage list | $0.65 (generic) | no | 96 of 96 |
| Prednisolone 15 mg/5 mL oral solution | not found on FDA shortage list | $54.01 (generic) | no | 96 of 96 |
| Methylprednisolone 4 mg dose pack (Medrol) | not found on FDA shortage list | $3.03 (generic) | no | 96 of 96 |
| Allopurinol 100 mg tablet | shortage resolved or discontinued | $0.94 (generic) | no | 96 of 96 |
| Colchicine 0.6 mg tablet | not found on FDA shortage list | $7.13 (generic) | no | 96 of 96 |
| Estradiol 1 mg tablet | not found on FDA shortage list | $1.90 (generic) | no | 96 of 96 |
| Norgestimate/ethinyl estradiol (Sprintec) birth control pack | not found on FDA shortage list | $3.11 (generic) | no | 73 of 96 |
| Medroxyprogesterone (Depo-Provera) 150 mg/mL injection | not found on FDA shortage list | $23.04 (generic) | no | 96 of 96 |
| Finasteride 5 mg tablet | not found on FDA shortage list | $2.06 (generic) | no | 96 of 96 |
| Tamsulosin 0.4 mg capsule | not found on FDA shortage list | $1.47 (generic) | no | 96 of 96 |
| Alendronate 70 mg tablet (weekly) | not found on FDA shortage list | $1.03 (generic) | no | 96 of 96 |
| Levetiracetam 500 mg tablet | not found on FDA shortage list | $4.33 (generic) | no | 96 of 96 |
| Emtricitabine/tenofovir DF (Truvada) 200/300 mg tablet | not found on FDA shortage list | $15.79 (generic) | no | 96 of 96 |
| Biktarvy (bictegravir/emtricitabine/tenofovir alafenamide) tablet | not found on FDA shortage list | $4,102.59 (brand) | no | 96 of 96 |
| Enbrel (etanercept) 50 mg pen | not found on FDA shortage list | $8,334.50 (brand) | yes | 96 of 96 |
| Nurtec ODT (rimegepant) 75 mg | not found on FDA shortage list | $1,029.30 (brand) | yes | 85 of 96 |
| Timolol 0.5% eye drops | not found on FDA shortage list | $4.11 (generic) | no | 96 of 96 |
| Clobetasol 0.05% cream | not found on FDA shortage list | $5.10 (generic) | no | 94 of 96 |
| Vitamin D2 (ergocalciferol) 50,000 unit capsule | not found on FDA shortage list | $0.46 (generic) | no | 0 of 96 |

## Adderall XR 30 mg ER capsule

- **RxNorm:** amphetamine / amphetamine aspartate / amphetamine sulfate / dextroamphetamine saccharate / dextroamphetamine sulfate / dextroamphetamine — brands: Adderall — 2 RxCUIs, 27 NDCs. Controlled: yes, C-II.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Tablet (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.48 per EA (median of 11 NDCs) -> about $14.28 for 30 capsules (1 a day); Brand: $6.81 per EA (median of 1 NDCs) -> about $204.23 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 2 units/day. Covered. PA is needed for ages under 3 or 21 and older, or above 2 capsules a day. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amphetamine>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 17, tier 3: 37, tier 4: 29. Restrictions on that tier (number of plans): quantity limit: 72, prior auth: 17.
  - Average plan cost for 30 capsules (1 a day): $40.52 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Concerta 18 mg ER tablet

- **RxNorm:** methylphenidate — brands: Concerta — 2 RxCUIs, 23 NDCs. Controlled: yes, C-II.
- **FDA shortage:** in shortage. FDA lists a current shortage for 8 package(s) of this exact drug and strength. Some makers may still have it. Call the pharmacy to check. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'Available': 17, 'Limited Availability': 7, 'Unavailable': 1}
- **NADAC (as of 10/21/2026):** Generic: $0.61 per EA (median of 5 NDCs) -> about $18.29 for 30 tablets (1 a day); Brand: $12.33 per EA (median of 1 NDCs) -> about $369.80 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 2 units/day. Brand Concerta is preferred over generics. PA is needed for ages under 3 or 21 and older, or above 2 tablets a day. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=methylphenidate>)
- **Medicare Part D (Massachusetts):** on the formulary of 45 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 7, tier 2: 7, tier 3: 4, tier 4: 27. Restrictions on that tier (number of plans): quantity limit: 21.
  - Average plan cost for 30 tablets (1 a day): $46.67 (from 45 plans' pricing; this is the plan's drug price, not the patient's share).

## Atorvastatin 20 mg tablet

- **RxNorm:** atorvastatin — brands: Lipitor — 2 RxCUIs, 408 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 69 NDCs) -> about $0.86 for 30 tablets (1 a day); Brand: $19.06 per EA (median of 1 NDCs) -> about $571.75 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 1.5 units/day. Generic atorvastatin is covered. PA is needed only above 1.5 tablets a day. Brand Lipitor needs PA. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=atorvastatin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): quantity limit: 35.
  - Average plan cost for 30 tablets (1 a day): $5.75 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Lisinopril 10 mg tablet

- **RxNorm:** lisinopril — brands: Prinivil, Zestril — 3 RxCUIs, 250 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 34 NDCs) -> about $0.54 for 30 tablets (1 a day); Brand: $12.52 per EA (median of 1 NDCs) -> about $375.73 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=lisinopril>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): quantity limit: 17.
  - Average plan cost for 30 tablets (1 a day): $3.40 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Levothyroxine 50 mcg tablet

- **RxNorm:** levothyroxine — brands: Euthyrox, Levo-T, Levoxyl, Synthroid, Unithroid — 6 RxCUIs, 166 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 27 NDCs) -> about $1.20 for 30 tablets (1 a day); Brand: $1.66 per EA (median of 6 NDCs) -> about $49.86 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=levothyroxine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 82, tier 2: 14. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $4.69 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Metformin 500 mg tablet

- **RxNorm:** metformin — brands: not found — 1 RxCUIs, 507 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.01 per EA (median of 57 NDCs) -> about $0.89 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=metformin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): quantity limit: 52.
  - Average plan cost for 60 tablets (1 twice a day): $5.56 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amlodipine 5 mg tablet

- **RxNorm:** amlodipine — brands: Norvasc — 2 RxCUIs, 293 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.01 per EA (median of 35 NDCs) -> about $0.30 for 30 tablets (1 a day); Brand: $8.69 per EA (median of 6 NDCs) -> about $260.85 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic amlodipine is covered without PA. Brand Norvasc needs PA. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amlodipine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $2.84 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Omeprazole 20 mg DR capsule

- **RxNorm:** omeprazole — brands: Prilosec — 2 RxCUIs, 660 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 43 NDCs) -> about $0.91 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 4 units/day. Covered. PA is needed above 4 capsules a day. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=omeprazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 61, tier 2: 35. Restrictions on that tier (number of plans): quantity limit: 26.
  - Average plan cost for 30 capsules (1 a day): $4.56 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Sertraline 50 mg tablet

- **RxNorm:** sertraline — brands: Zoloft — 2 RxCUIs, 327 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 41 NDCs) -> about $1.05 for 30 tablets (1 a day); Brand: $14.92 per EA (median of 3 NDCs) -> about $447.53 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. Generic sertraline tablets are covered; PA is needed for children under 6. Brand Zoloft needs PA. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sertraline>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): quantity limit: 23.
  - Average plan cost for 30 tablets (1 a day): $3.85 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amoxicillin 500 mg capsule

- **RxNorm:** amoxicillin — brands: Trimox — 2 RxCUIs, 427 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.08 per EA (median of 19 NDCs) -> about $2.38 for 30 capsules (a typical 10-day course, 3 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amoxicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 70, tier 2: 26. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 capsules (a typical 10-day course, 3 a day): $4.08 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Ozempic (semaglutide) 0.5 mg pen

- **RxNorm:** semaglutide — brands: Ozempic — 2 RxCUIs, 5 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $332.02 per ML (median of 2 NDCs) -> about $996.07 for 1 pen (3 mL), about 1 month at 0.5 mg weekly
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=semaglutide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 83, tier 6: 1. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 73.
  - Average plan cost for 1 pen (3 mL), about 1 month at 0.5 mg weekly: $998.21 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Mounjaro (tirzepatide) 5 mg pen

- **RxNorm:** tirzepatide — brands: Mounjaro — 2 RxCUIs, 3 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $538.70 per ML (median of 1 NDCs) -> about $1,077.39 for 4 single-dose pens (0.5 mL each), 1 a week
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=tirzepatide>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 82, tier 6: 1. Restrictions on that tier (number of plans): prior auth: 95, quantity limit: 72.
  - Average plan cost for 4 single-dose pens (0.5 mL each), 1 a week: $1,080.20 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Eliquis (apixaban) 5 mg tablet

- **RxNorm:** apixaban — brands: Eliquis — 2 RxCUIs, 23 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $5.52 per EA (median of 3 NDCs) -> about $331.29 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. BP: Brand preferred over generics: MassHealth wants the brand tried first. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=apixaban>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 66.
  - Average plan cost for 60 tablets (1 twice a day): $248.71 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: Eliquis (apixaban): 56% off the 2023 list price for a 30-day supply.

## Humira (adalimumab) 40 mg pen

- **RxNorm:** adalimumab — brands: Humira — 2 RxCUIs, 6 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $3,367.85 per EA (median of 1 NDCs) -> about $6,735.70 for 2 pens (every other week)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. Humira needs PA. Hadlima and unbranded adalimumab-adaz are the preferred adalimumab products (also PA). (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=adalimumab>)
- **Medicare Part D (Massachusetts):** on the formulary of 62 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 5: 50. Restrictions on that tier (number of plans): prior auth: 62, quantity limit: 62.
  - Average plan cost for 2 pens (every other week): $6,666.18 (from 62 plans' pricing; this is the plan's drug price, not the patient's share).

## Dupixent (dupilumab) 300 mg pen

- **RxNorm:** dupilumab — brands: Dupixent — 2 RxCUIs, 4 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $1,008.94 per ML (median of 1 NDCs) -> about $4,035.76 for 2 pens (2 mL each), every other week
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=dupilumab>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 5: 84. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 73.
  - Average plan cost for 2 pens (2 mL each), every other week: $4,073.75 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Albuterol HFA 90 mcg inhaler

- **RxNorm:** albuterol — brands: ProAir, Proventil, Ventolin — 6 RxCUIs, 60 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.83 per GM (median of 12 NDCs) -> about $32.98 for 1 inhaler (18 g size; some brands are 6.7 g or 8.5 g); Brand: $3.03 per GM (median of 1 NDCs) -> about $54.61 for 1 inhaler (18 g size; some brands are 6.7 g or 8.5 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. Ventolin HFA (brand) is the preferred inhaler with no PA. Other albuterol HFA inhalers need PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=albuterol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 69, tier 3: 15. Restrictions on that tier (number of plans): quantity limit: 79.
  - Average plan cost for 1 inhaler (18 g size; some brands are 6.7 g or 8.5 g): $32.53 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Insulin glargine (Lantus SoloStar) pen

- **RxNorm:** insulin glargine — brands: Lantus — 2 RxCUIs, 10 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $6.16 per ML (median of 1 NDCs) -> about $92.46 for 1 box of 5 pens (3 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Lantus (brand) is preferred and covered without PA. Other insulin glargine products need PA. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=insulin+glargine>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 83. Restrictions on that tier (number of plans): quantity limit: 7.
  - Average plan cost for 1 box of 5 pens (3 mL each): $93.79 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Amoxicillin 400 mg/5 mL oral suspension

- **RxNorm:** amoxicillin — brands: not found — 1 RxCUIs, 62 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per ML (median of 18 NDCs) -> about $3.92 for 1 bottle (100 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amoxicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 62, tier 2: 34. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (100 mL): $4.92 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Sumatriptan 50 mg tablet

- **RxNorm:** sumatriptan — brands: Imitrex — 2 RxCUIs, 57 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.31 per EA (median of 13 NDCs) -> about $2.81 for 9 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 16 units/30 days. Generic sumatriptan tablets are covered up to 16 tablets per 30 days; more needs PA. Brand Imitrex needs PA. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sumatriptan>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 16, tier 2: 80. Restrictions on that tier (number of plans): quantity limit: 73.
  - Average plan cost for 9 tablets: $6.55 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Latanoprost 0.005% eye drops

- **RxNorm:** latanoprost — brands: Iyuzeh, Xalatan — 3 RxCUIs, 26 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.57 per ML (median of 10 NDCs) -> about $3.93 for 1 bottle (2.5 mL); Brand: $108.34 per ML (median of 1 NDCs) -> about $270.86 for 1 bottle (2.5 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic latanoprost is covered without PA. Brand Xalatan needs PA. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=latanoprost>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 68, tier 2: 28. Restrictions on that tier (number of plans): quantity limit: 15.
  - Average plan cost for 1 bottle (2.5 mL): $6.17 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Fluticasone 50 mcg nasal spray

- **RxNorm:** fluticasone — brands: Aller-Flo, Clarispray, Flonase, Fluticare, Nasopro 24 — 6 RxCUIs, 307 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.44 per GM (median of 6 NDCs) -> about $7.09 for 1 bottle (16 g, about 120 sprays)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 1 inhaler/30 days. Covered. PA is needed above 1 bottle per 30 days. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=fluticasone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 48, tier 2: 48. Restrictions on that tier (number of plans): quantity limit: 71.
  - Average plan cost for 1 bottle (16 g, about 120 sprays): $10.74 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Triamcinolone 0.1% cream

- **RxNorm:** triamcinolone — brands: Triderm — 2 RxCUIs, 151 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per GM (median of 31 NDCs) -> about $1.34 for 1 tube (30 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=triamcinolone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 29, tier 2: 66, tier 3: 1. Restrictions on that tier (number of plans): quantity limit: 36.
  - Average plan cost for 1 tube (30 g): $2.26 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Epinephrine 0.3 mg auto-injector

- **RxNorm:** epinephrine — brands: Auvi-Q, Epipen — 5 RxCUIs, 36 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $134.36 per EA (median of 6 NDCs) -> about $268.72 for 1 two-pack of auto-injectors; Brand: $309.38 per EA (median of 2 NDCs) -> about $618.75 for 1 two-pack of auto-injectors
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic epinephrine auto-injectors are covered without PA. Brand EpiPen needs PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=epinephrine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 3: 74. Restrictions on that tier (number of plans): quantity limit: 61.
  - Average plan cost for 1 two-pack of auto-injectors: $255.16 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Nicotine 21 mg patch

- **RxNorm:** nicotine — brands: Habitrol, Nicduic, Nicoderm C-Q — 4 RxCUIs, 120 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.99 per EA (median of 28 NDCs) -> about $55.62 for 28 patches
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. Generic nicotine patches (OTC) are payable without PA. *: The generic OTC (and generic prescription) versions are payable without PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=nicotine>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Paxlovid dose pack

- **RxNorm:** nirmatrelvir / ritonavir — brands: Paxlovid 5-Day — 2 RxCUIs, 8 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $49.24 per EA (median of 1 NDCs) -> about $1,477.18 for 1 five-day dose pack (30 tablets)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 12 years; or > 30 units/claim. Covered. PA is needed for children under 12, or above 30 tablets per claim. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=nirmatrelvir>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 23, tier 3: 39, tier 5: 22. Restrictions on that tier (number of plans): quantity limit: 96.
  - Average plan cost for 1 five-day dose pack (30 tablets): $1,498.36 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Wegovy (semaglutide) 2.4 mg pen

- **RxNorm:** semaglutide — brands: Wegovy — 2 RxCUIs, 2 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $435.57 per ML (median of 1 NDCs) -> about $1,306.72 for 4 single-dose pens (0.75 mL each), 1 a week
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=semaglutide>)
- **Medicare Part D (Massachusetts):** on the formulary of 8 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 1, tier 5: 7. Restrictions on that tier (number of plans): prior auth: 8, quantity limit: 8.
  - Average plan cost for 4 single-dose pens (0.75 mL each), 1 a week: $1,319.10 (from 8 plans' pricing; this is the plan's drug price, not the patient's share).

## Rybelsus (semaglutide) 7 mg tablet

- **RxNorm:** semaglutide — brands: Rybelsus — 2 RxCUIs, 3 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 3}
- **NADAC (as of 10/21/2026):** Brand: $33.19 per EA (median of 1 NDCs) -> about $995.84 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=semaglutide>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Zepbound (tirzepatide) 2.5 mg pen

- **RxNorm:** tirzepatide — brands: Zepbound — 2 RxCUIs, 3 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $526.23 per ML (median of 1 NDCs) -> about $1,052.46 for 4 single-dose pens (0.5 mL each), 1 a week
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=tirzepatide>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Trulicity (dulaglutide) 1.5 mg pen

- **RxNorm:** dulaglutide — brands: Trulicity — 2 RxCUIs, 5 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $487.62 per ML (median of 1 NDCs) -> about $975.24 for 4 single-dose pens (0.5 mL each), 1 a week
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=dulaglutide>)
- **Medicare Part D (Massachusetts):** on the formulary of 93 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 80, tier 6: 1. Restrictions on that tier (number of plans): prior auth: 93, quantity limit: 70.
  - Average plan cost for 4 single-dose pens (0.5 mL each), 1 a week: $979.63 (from 93 plans' pricing; this is the plan's drug price, not the patient's share).

## Victoza (liraglutide) pen

- **RxNorm:** liraglutide — brands: Victoza — 2 RxCUIs, 33 NDCs. Controlled: no.
- **FDA shortage:** in shortage. FDA lists a current shortage for 2 package(s) of this exact drug and strength. Some makers may still have it. Call the pharmacy to check. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'Available': 6, 'Limited Availability': 2}
- **NADAC (as of 10/21/2026):** Generic: $28.89 per ML (median of 14 NDCs) -> about $173.31 for 2 pens (3 mL each), about 1 month at 1.2 mg a day; Brand: $87.75 per ML (median of 2 NDCs) -> about $526.53 for 2 pens (3 mL each), about 1 month at 1.2 mg a day
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=liraglutide>)
- **Medicare Part D (Massachusetts):** on the formulary of 18 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 3, tier 3: 15. Restrictions on that tier (number of plans): prior auth: 18, quantity limit: 18.
  - Average plan cost for 2 pens (3 mL each), about 1 month at 1.2 mg a day: $399.46 (from 18 plans' pricing; this is the plan's drug price, not the patient's share).

## Jardiance (empagliflozin) 10 mg tablet

- **RxNorm:** empagliflozin — brands: Jardiance — 2 RxCUIs, 11 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $11.19 per EA (median of 3 NDCs) -> about $335.67 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=empagliflozin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 73.
  - Average plan cost for 30 tablets (1 a day): $203.82 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: Jardiance (empagliflozin): 66% off the 2023 list price for a 30-day supply.

## Farxiga (dapagliflozin) 10 mg tablet

- **RxNorm:** dapagliflozin — brands: Farxiga — 2 RxCUIs, 56 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.18 per EA (median of 20 NDCs) -> about $5.53 for 30 tablets (1 a day); Brand: $12.08 per EA (median of 3 NDCs) -> about $362.29 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=dapagliflozin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 29, tier 2: 8, tier 3: 59. Restrictions on that tier (number of plans): quantity limit: 67.
  - Average plan cost for 30 tablets (1 a day): $85.58 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: Farxiga (dapagliflozin): 68% off the 2023 list price for a 30-day supply.

## Januvia (sitagliptin) 100 mg tablet

- **RxNorm:** sitagliptin — brands: Januvia, Zituvio — 4 RxCUIs, 36 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $3.85 per EA (median of 8 NDCs) -> about $115.48 for 30 tablets (1 a day); Brand: $10.55 per EA (median of 6 NDCs) -> about $316.50 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sitagliptin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 19, tier 2: 10, tier 3: 67. Restrictions on that tier (number of plans): quantity limit: 73.
  - Average plan cost for 30 tablets (1 a day): $124.24 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: Januvia (sitagliptin): 79% off the 2023 list price for a 30-day supply.

## Glipizide 5 mg tablet

- **RxNorm:** glipizide — brands: Glucotrol — 2 RxCUIs, 210 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 20 NDCs) -> about $1.97 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=glipizide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 91, tier 2: 5. Restrictions on that tier (number of plans): quantity limit: 52.
  - Average plan cost for 60 tablets (1 twice a day): $7.06 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Pioglitazone 30 mg tablet

- **RxNorm:** pioglitazone — brands: Actos — 2 RxCUIs, 128 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.10 per EA (median of 21 NDCs) -> about $2.90 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=pioglitazone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 92, tier 2: 4. Restrictions on that tier (number of plans): quantity limit: 59.
  - Average plan cost for 30 tablets (1 a day): $9.70 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Metformin ER 500 mg tablet

- **RxNorm:** metformin — brands: Glucophage — 2 RxCUIs, 413 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 31 NDCs) -> about $1.70 for 60 tablets (2 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=metformin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): quantity limit: 59.
  - Average plan cost for 60 tablets (2 a day): $6.41 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Insulin lispro (Humalog KwikPen) pen

- **RxNorm:** insulin lispro — brands: Admelog, Humalog — 3 RxCUIs, 11 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 2}
- **NADAC (as of 10/21/2026):** Generic: $10.19 per ML (median of 1 NDCs) -> about $152.87 for 1 box of 5 pens (3 mL each); Brand: $11.14 per ML (median of 2 NDCs) -> about $167.03 for 1 box of 5 pens (3 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=insulin+lispro>)
- **Medicare Part D (Massachusetts):** on the formulary of 78 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 66. Restrictions on that tier (number of plans): quantity limit: 7.
  - Average plan cost for 1 box of 5 pens (3 mL each): $160.49 (from 78 plans' pricing; this is the plan's drug price, not the patient's share).

## Insulin aspart (NovoLog FlexPen) pen

- **RxNorm:** insulin aspart, human — brands: NovoLog — 2 RxCUIs, 14 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $8.96 per ML (median of 1 NDCs) -> about $134.41 for 1 box of 5 pens (3 mL each); Brand: $8.93 per ML (median of 1 NDCs) -> about $134.01 for 1 box of 5 pens (3 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=insulin+aspart>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 4.
  - Average plan cost for 1 box of 5 pens (3 mL each): $133.82 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: NovoLog / Fiasp insulin aspart products: 76% off the 2023 list price for a 30-day supply.

## Insulin degludec (Tresiba FlexTouch) pen

- **RxNorm:** insulin degludec — brands: Tresiba — 2 RxCUIs, 7 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $11.39 per ML (median of 1 NDCs) -> about $170.86 for 1 box of 5 pens (3 mL each); Brand: $9.03 per ML (median of 1 NDCs) -> about $135.52 for 1 box of 5 pens (3 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=insulin+degludec>)
- **Medicare Part D (Massachusetts):** on the formulary of 36 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 8, tier 3: 28. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 box of 5 pens (3 mL each): $135.49 (from 36 plans' pricing; this is the plan's drug price, not the patient's share).

## Toujeo SoloStar (insulin glargine 300 units/mL) pen

- **RxNorm:** insulin glargine — brands: Toujeo — 2 RxCUIs, 7 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $26.99 per ML (median of 1 NDCs) -> about $121.44 for 1 box of 3 pens (1.5 mL each); Brand: $91.28 per ML (median of 1 NDCs) -> about $410.75 for 1 box of 3 pens (1.5 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=insulin+glargine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 4.
  - Average plan cost for 1 box of 3 pens (1.5 mL each): $401.78 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Insulin NPH (Humulin N / Novolin N) pen

- **RxNorm:** insulin isophane — brands: Humulin N, Novolin N — 3 RxCUIs, 7 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $7.43 per ML (median of 2 NDCs) -> about $111.39 for 1 box of 5 pens (3 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=insulin+NPH>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 8.
  - Average plan cost for 1 box of 5 pens (3 mL each): $106.41 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Fluticasone/salmeterol (Advair Diskus) 250/50 inhaler

- **RxNorm:** fluticasone / fluticasone / salmeterol / salmeterol — brands: Advair, Wixela — 3 RxCUIs, 16 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.21 per EA (median of 5 NDCs) -> about $72.47 for 1 inhaler (60 puffs); Brand: $3.12 per EA (median of 1 NDCs) -> about $187.31 for 1 inhaler (60 puffs)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. BP: Brand preferred over generics: MassHealth wants the brand tried first. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=fluticasone>)
- **Medicare Part D (Massachusetts):** on the formulary of 90 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 21, tier 3: 57. Restrictions on that tier (number of plans): quantity limit: 90.
  - Average plan cost for 1 inhaler (60 puffs): $98.52 (from 90 plans' pricing; this is the plan's drug price, not the patient's share).

## Budesonide/formoterol (Symbicort) 160/4.5 inhaler

- **RxNorm:** budesonide / budesonide / formoterol / formoterol — brands: Breyna, Symbicort — 3 RxCUIs, 9 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $17.32 per GM (median of 3 NDCs) -> about $176.65 for 1 inhaler (120 puffs, 10.2 g); Brand: $21.98 per GM (median of 1 NDCs) -> about $224.20 for 1 inhaler (120 puffs, 10.2 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. BP: Brand preferred over generics: MassHealth wants the brand tried first. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=budesonide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 3: 50, tier 4: 24. Restrictions on that tier (number of plans): quantity limit: 96.
  - Average plan cost for 1 inhaler (120 puffs, 10.2 g): $211.79 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Trelegy Ellipta 100/62.5/25 inhaler

- **RxNorm:** fluticasone / fluticasone / umeclidinium / vilanterol / umeclidinium / vilanterol — brands: Trelegy — 2 RxCUIs, 1 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $11.15 per EA (median of 1 NDCs) -> about $334.56 for 1 inhaler (30 puffs)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=fluticasone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 96.
  - Average plan cost for 1 inhaler (30 puffs): $339.29 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Tiotropium (Spiriva HandiHaler) 18 mcg capsules

- **RxNorm:** tiotropium — brands: Spiriva — 2 RxCUIs, 8 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $11.90 per EA (median of 1 NDCs) -> about $356.89 for 30 capsules (1 a day); Brand: $10.61 per EA (median of 3 NDCs) -> about $318.34 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. BP: Brand preferred over generics: MassHealth wants the brand tried first. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=tiotropium>)
- **Medicare Part D (Massachusetts):** on the formulary of 44 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 3, tier 3: 37, tier 4: 4. Restrictions on that tier (number of plans): quantity limit: 44.
  - Average plan cost for 30 capsules (1 a day): $359.91 (from 44 plans' pricing; this is the plan's drug price, not the patient's share).

## Fluticasone (Flovent HFA) 110 mcg inhaler

- **RxNorm:** fluticasone — brands: Flovent — 2 RxCUIs, 5 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $13.56 per GM (median of 1 NDCs) -> about $162.76 for 1 inhaler (12 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: >= 12 years. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=fluticasone>)
- **Medicare Part D (Massachusetts):** on the formulary of 33 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 7, tier 3: 7, tier 4: 19. Restrictions on that tier (number of plans): quantity limit: 33, step therapy: 23.
  - Average plan cost for 1 inhaler (12 g): $244.28 (from 33 plans' pricing; this is the plan's drug price, not the patient's share).

## Albuterol 2.5 mg/3 mL nebulizer solution

- **RxNorm:** albuterol — brands: not found — 1 RxCUIs, 76 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per ML (median of 19 NDCs) -> about $4.61 for 1 box (25 vials of 3 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=albuterol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 79, tier 3: 2, tier 4: 3. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 12.
  - Average plan cost for 1 box (25 vials of 3 mL): $10.46 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Ipratropium/albuterol (DuoNeb) nebulizer solution

- **RxNorm:** albuterol / albuterol / ipratropium / ipratropium — brands: not found — 1 RxCUIs, 54 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.08 per ML (median of 22 NDCs) -> about $6.88 for 30 vials (3 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=albuterol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 27, tier 2: 66, tier 3: 3. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 12.
  - Average plan cost for 30 vials (3 mL each): $13.72 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Budesonide 0.5 mg/2 mL nebulizer suspension (Pulmicort Respules)

- **RxNorm:** budesonide — brands: Pulmicort — 2 RxCUIs, 37 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.63 per ML (median of 15 NDCs) -> about $37.60 for 30 vials (2 mL each); Brand: $4.91 per ML (median of 1 NDCs) -> about $294.47 for 30 vials (2 mL each)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: >= 13 years. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=budesonide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 3: 8, tier 4: 66. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 13.
  - Average plan cost for 30 vials (2 mL each): $74.30 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Montelukast 10 mg tablet

- **RxNorm:** montelukast — brands: Singulair — 2 RxCUIs, 168 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 1}
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 31 NDCs) -> about $1.30 for 30 tablets (1 a day); Brand: $9.23 per EA (median of 2 NDCs) -> about $276.82 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=montelukast>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 64, tier 2: 32. Restrictions on that tier (number of plans): quantity limit: 36.
  - Average plan cost for 30 tablets (1 a day): $6.10 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Montelukast 5 mg chewable tablet (children)

- **RxNorm:** montelukast — brands: Singulair — 2 RxCUIs, 78 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 1}
- **NADAC (as of 10/21/2026):** Generic: $0.07 per EA (median of 18 NDCs) -> about $2.17 for 30 chewable tablets (1 a day); Brand: $9.27 per EA (median of 1 NDCs) -> about $278.22 for 30 chewable tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=montelukast>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 42, tier 2: 47, tier 3: 7. Restrictions on that tier (number of plans): quantity limit: 36.
  - Average plan cost for 30 chewable tablets (1 a day): $5.48 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Benzonatate 100 mg capsule

- **RxNorm:** benzonatate — brands: Tessalon Perles — 2 RxCUIs, 350 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per EA (median of 24 NDCs) -> about $1.85 for 30 capsules
- **MassHealth:** not found; PA: not found. Not on the MassHealth Drug List (website search and the October 01, 2026 PDF). The List says any drug not on it requires PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=benzonatate>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Naloxone 4 mg nasal spray (Narcan)

- **RxNorm:** naloxone — brands: Narcan — 2 RxCUIs, 51 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $16.77 per EA (median of 7 NDCs) -> about $33.53 for 1 two-pack; Brand: $16.08 per EA (median of 2 NDCs) -> about $32.15 for 1 two-pack
- **MassHealth:** yes (on the MassHealth Drug List); PA: no.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=naloxone>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Oseltamivir (Tamiflu) 75 mg capsule

- **RxNorm:** oseltamivir — brands: Tamiflu — 2 RxCUIs, 73 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.80 per EA (median of 13 NDCs) -> about $7.98 for 10 capsules (one 5-day course); Brand: $14.52 per EA (median of 1 NDCs) -> about $145.19 for 10 capsules (one 5-day course)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 10 units/ claim; or > 20 units/ 365 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=oseltamivir>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 32, tier 3: 50, tier 4: 2. Restrictions on that tier (number of plans): quantity limit: 66.
  - Average plan cost for 10 capsules (one 5-day course): $16.98 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Oseltamivir (Tamiflu) 6 mg/mL oral suspension

- **RxNorm:** oseltamivir — brands: Tamiflu — 2 RxCUIs, 34 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.16 per ML (median of 11 NDCs) -> about $9.33 for 1 bottle (60 mL); Brand: $2.43 per ML (median of 1 NDCs) -> about $145.98 for 1 bottle (60 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 180 mL/ claim; or > 360 mL/ 365 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=oseltamivir>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 32, tier 3: 42, tier 4: 10. Restrictions on that tier (number of plans): quantity limit: 66.
  - Average plan cost for 1 bottle (60 mL): $25.03 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amoxicillin 250 mg/5 mL oral suspension

- **RxNorm:** amoxicillin — brands: Amoxi Drop — 2 RxCUIs, 58 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per ML (median of 12 NDCs) -> about $2.49 for 1 bottle (100 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amoxicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 69, tier 2: 27. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (100 mL): $3.84 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amoxicillin/clavulanate (Augmentin) 875/125 mg tablet

- **RxNorm:** amoxicillin / amoxicillin / clavulanate / clavulanate — brands: Augmentin — 2 RxCUIs, 287 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.28 per EA (median of 16 NDCs) -> about $5.64 for 20 tablets (a 10-day course, 2 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amoxicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 82, tier 4: 2. Restrictions on that tier (number of plans): none.
  - Average plan cost for 20 tablets (a 10-day course, 2 a day): $9.99 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amoxicillin/clavulanate 400/57 mg per 5 mL oral suspension

- **RxNorm:** amoxicillin / amoxicillin / clavulanate / clavulanate — brands: Augmentin — 2 RxCUIs, 55 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per ML (median of 17 NDCs) -> about $6.45 for 1 bottle (100 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amoxicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 75, tier 3: 7, tier 4: 2. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (100 mL): $11.09 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Azithromycin (Z-Pak) 250 mg tablet

- **RxNorm:** azithromycin — brands: Z-PAK, Zithromax — 4 RxCUIs, 214 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 2}
- **NADAC (as of 10/21/2026):** Generic: $0.27 per EA (median of 28 NDCs) -> about $1.63 for 6 tablets (a 5-day pack)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=azithromycin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 61, tier 2: 35. Restrictions on that tier (number of plans): none.
  - Average plan cost for 6 tablets (a 5-day pack): $2.97 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Azithromycin 200 mg/5 mL oral suspension

- **RxNorm:** azithromycin — brands: Zithromax — 2 RxCUIs, 74 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 2}
- **NADAC (as of 10/21/2026):** Generic: $0.24 per ML (median of 19 NDCs) -> about $3.58 for 1 bottle (15 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=azithromycin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 27, tier 2: 36, tier 3: 30, tier 4: 3. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (15 mL): $4.55 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Cephalexin 500 mg capsule

- **RxNorm:** cephalexin — brands: Keflex — 2 RxCUIs, 487 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.12 per EA (median of 17 NDCs) -> about $3.27 for 28 capsules (a 7-day course, 4 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=cephalexin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 51, tier 2: 45. Restrictions on that tier (number of plans): none.
  - Average plan cost for 28 capsules (a 7-day course, 4 a day): $5.29 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Cephalexin 250 mg/5 mL oral suspension

- **RxNorm:** cephalexin — brands: not found — 1 RxCUIs, 46 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per ML (median of 10 NDCs) -> about $5.85 for 1 bottle (100 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=cephalexin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 56, tier 3: 26, tier 4: 2. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (100 mL): $9.48 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Cefdinir 250 mg/5 mL oral suspension

- **RxNorm:** cefdinir — brands: not found — 1 RxCUIs, 40 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.11 per ML (median of 8 NDCs) -> about $6.88 for 1 bottle (60 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=cefdinir>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 51, tier 3: 30, tier 4: 3. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (60 mL): $16.16 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Doxycycline hyclate 100 mg capsule

- **RxNorm:** doxycycline — brands: Morgidox, Vibramycin — 3 RxCUIs, 326 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.11 per EA (median of 21 NDCs) -> about $2.16 for 20 capsules (a 10-day course, 2 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=doxycycline>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 54, tier 3: 29, tier 4: 1. Restrictions on that tier (number of plans): none.
  - Average plan cost for 20 capsules (a 10-day course, 2 a day): $4.61 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Sulfamethoxazole/trimethoprim DS 800/160 mg tablet (Bactrim DS)

- **RxNorm:** sulfamethoxazole / sulfamethoxazole / trimethoprim / trimethoprim — brands: Bactrim — 2 RxCUIs, 337 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.05 per EA (median of 12 NDCs) -> about $0.91 for 20 tablets (a 10-day course, 2 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sulfamethoxazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 82, tier 2: 14. Restrictions on that tier (number of plans): none.
  - Average plan cost for 20 tablets (a 10-day course, 2 a day): $2.75 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Sulfamethoxazole/trimethoprim 200/40 mg per 5 mL oral suspension

- **RxNorm:** sulfamethoxazole / sulfamethoxazole / trimethoprim / trimethoprim — brands: Sulfatrim — 2 RxCUIs, 39 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per ML (median of 5 NDCs) -> about $5.53 for 1 bottle (100 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sulfamethoxazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 32, tier 3: 40, tier 4: 12. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (100 mL): $9.07 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Nitrofurantoin (Macrobid) 100 mg capsule

- **RxNorm:** nitrofurantoin / nitrofurantoin, macrocrystals / nitrofurantoin, monohydrate — brands: Macrobid — 2 RxCUIs, 244 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.27 per EA (median of 13 NDCs) -> about $2.72 for 10 capsules (a 5-day course, 2 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=nitrofurantoin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 37, tier 3: 45, tier 4: 2. Restrictions on that tier (number of plans): none.
  - Average plan cost for 10 capsules (a 5-day course, 2 a day): $4.66 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Ciprofloxacin 500 mg tablet

- **RxNorm:** ciprofloxacin — brands: Cipro — 2 RxCUIs, 552 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.12 per EA (median of 26 NDCs) -> about $1.69 for 14 tablets (a 7-day course, 2 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=ciprofloxacin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 82, tier 2: 14. Restrictions on that tier (number of plans): none.
  - Average plan cost for 14 tablets (a 7-day course, 2 a day): $3.40 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Metronidazole 500 mg tablet

- **RxNorm:** metronidazole — brands: not found — 1 RxCUIs, 378 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.10 per EA (median of 26 NDCs) -> about $1.46 for 14 tablets (a 7-day course, 2 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=metronidazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 30, tier 2: 66. Restrictions on that tier (number of plans): none.
  - Average plan cost for 14 tablets (a 7-day course, 2 a day): $3.03 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Penicillin VK 500 mg tablet

- **RxNorm:** penicillin V — brands: not found — 1 RxCUIs, 143 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.10 per EA (median of 11 NDCs) -> about $3.91 for 40 tablets (a 10-day course, 4 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=penicillin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 65, tier 2: 31. Restrictions on that tier (number of plans): none.
  - Average plan cost for 40 tablets (a 10-day course, 4 a day): $6.30 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Fluconazole 150 mg tablet

- **RxNorm:** fluconazole — brands: Diflucan — 2 RxCUIs, 126 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.51 per EA (median of 13 NDCs) -> about $0.51 for 1 tablet
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=fluconazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 35, tier 2: 61. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 tablet: $1.10 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Valacyclovir 1 g tablet

- **RxNorm:** valacyclovir — brands: Valtrex — 2 RxCUIs, 272 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.42 per EA (median of 23 NDCs) -> about $12.71 for 30 tablets; Brand: $20.24 per EA (median of 2 NDCs) -> about $607.32 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=valacyclovir>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 54, tier 3: 30. Restrictions on that tier (number of plans): quantity limit: 30.
  - Average plan cost for 30 tablets: $17.04 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Mupirocin 2% ointment

- **RxNorm:** mupirocin — brands: Bactroban, Centany, Muricin — 4 RxCUIs, 76 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.15 per GM (median of 8 NDCs) -> about $3.19 for 1 tube (22 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=mupirocin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 22, tier 2: 74. Restrictions on that tier (number of plans): quantity limit: 89.
  - Average plan cost for 1 tube (22 g): $6.94 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Losartan 50 mg tablet

- **RxNorm:** losartan — brands: Cozaar — 2 RxCUIs, 259 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 41 NDCs) -> about $0.99 for 30 tablets (1 a day); Brand: $4.49 per EA (median of 2 NDCs) -> about $134.78 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=losartan>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): quantity limit: 25.
  - Average plan cost for 30 tablets (1 a day): $5.42 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Metoprolol succinate ER 50 mg tablet

- **RxNorm:** metoprolol — brands: Toprol — 2 RxCUIs, 249 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 7}
- **NADAC (as of 10/21/2026):** Generic: $0.05 per EA (median of 46 NDCs) -> about $1.48 for 30 tablets (1 a day); Brand: $1.39 per EA (median of 1 NDCs) -> about $41.56 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=metoprolol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 51, tier 2: 45. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $5.42 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Metoprolol tartrate 25 mg tablet

- **RxNorm:** metoprolol — brands: not found — 1 RxCUIs, 251 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 25 NDCs) -> about $0.96 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=metoprolol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): none.
  - Average plan cost for 60 tablets (1 twice a day): $5.43 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Rosuvastatin 10 mg tablet

- **RxNorm:** rosuvastatin — brands: Crestor — 2 RxCUIs, 251 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 44 NDCs) -> about $1.07 for 30 tablets (1 a day); Brand: $8.81 per EA (median of 1 NDCs) -> about $264.18 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 1.5 units/day. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=rosuvastatin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 92, tier 2: 2, tier 3: 2. Restrictions on that tier (number of plans): quantity limit: 52.
  - Average plan cost for 30 tablets (1 a day): $6.71 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Hydrochlorothiazide 25 mg tablet

- **RxNorm:** hydrochlorothiazide — brands: not found — 1 RxCUIs, 276 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Tablet (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.01 per EA (median of 23 NDCs) -> about $0.34 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=hydrochlorothiazide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $1.25 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Simvastatin 20 mg tablet

- **RxNorm:** simvastatin — brands: Zocor — 2 RxCUIs, 194 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 23 NDCs) -> about $0.97 for 30 tablets (1 a day); Brand: $9.73 per EA (median of 2 NDCs) -> about $291.83 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 1.5 units/day. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=simvastatin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): quantity limit: 60.
  - Average plan cost for 30 tablets (1 a day): $4.74 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Pravastatin 40 mg tablet

- **RxNorm:** pravastatin — brands: Pravachol — 2 RxCUIs, 178 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.08 per EA (median of 21 NDCs) -> about $2.37 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 1.5 units/day. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=pravastatin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 92, tier 2: 4. Restrictions on that tier (number of plans): quantity limit: 43.
  - Average plan cost for 30 tablets (1 a day): $8.72 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Furosemide 20 mg tablet

- **RxNorm:** furosemide — brands: Lasix — 2 RxCUIs, 247 NDCs. Controlled: no.
- **FDA shortage:** in shortage. FDA lists a current shortage for 1 package(s) of this exact drug and strength. Some makers may still have it. Call the pharmacy to check. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'Available': 2, 'Limited Availability': 1}
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 16 NDCs) -> about $0.75 for 30 tablets (1 a day); Brand: $0.75 per EA (median of 1 NDCs) -> about $22.46 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=furosemide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $2.10 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Carvedilol 12.5 mg tablet

- **RxNorm:** carvedilol — brands: Coreg — 2 RxCUIs, 157 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 20 NDCs) -> about $1.28 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=carvedilol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): none.
  - Average plan cost for 60 tablets (1 twice a day): $6.52 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Spironolactone 25 mg tablet

- **RxNorm:** spironolactone — brands: Aldactone — 2 RxCUIs, 245 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 2}
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 34 NDCs) -> about $1.28 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=spironolactone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 72, tier 2: 24. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $4.06 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Clopidogrel 75 mg tablet

- **RxNorm:** clopidogrel — brands: Plavix — 2 RxCUIs, 199 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.05 per EA (median of 41 NDCs) -> about $1.41 for 30 tablets (1 a day); Brand: $8.21 per EA (median of 1 NDCs) -> about $246.20 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=clopidogrel>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 93, tier 2: 3. Restrictions on that tier (number of plans): quantity limit: 36.
  - Average plan cost for 30 tablets (1 a day): $6.86 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Valsartan 160 mg tablet

- **RxNorm:** valsartan — brands: Diovan — 2 RxCUIs, 129 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 1}
- **NADAC (as of 10/21/2026):** Generic: $0.11 per EA (median of 18 NDCs) -> about $3.17 for 30 tablets (1 a day); Brand: $10.04 per EA (median of 1 NDCs) -> about $301.10 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=valsartan>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 91, tier 2: 4, tier 3: 1. Restrictions on that tier (number of plans): quantity limit: 59.
  - Average plan cost for 30 tablets (1 a day): $13.39 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Ezetimibe 10 mg tablet

- **RxNorm:** ezetimibe — brands: Zetia — 2 RxCUIs, 148 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.07 per EA (median of 33 NDCs) -> about $2.11 for 30 tablets (1 a day); Brand: $13.94 per EA (median of 1 NDCs) -> about $418.31 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=ezetimibe>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 31, tier 2: 58, tier 3: 4, tier 4: 3. Restrictions on that tier (number of plans): quantity limit: 50.
  - Average plan cost for 30 tablets (1 a day): $8.77 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Propranolol 10 mg tablet

- **RxNorm:** propranolol — brands: not found — 1 RxCUIs, 130 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.05 per EA (median of 23 NDCs) -> about $2.78 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=propranolol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 27, tier 2: 67, tier 3: 2. Restrictions on that tier (number of plans): none.
  - Average plan cost for 60 tablets (1 twice a day): $7.03 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Xarelto (rivaroxaban) 20 mg tablet

- **RxNorm:** rivaroxaban — brands: Xarelto — 2 RxCUIs, 24 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 1}
- **NADAC (as of 10/21/2026):** Brand: $19.54 per EA (median of 5 NDCs) -> about $586.18 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. BP: Brand preferred over generics: MassHealth wants the brand tried first. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=rivaroxaban>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 84. Restrictions on that tier (number of plans): quantity limit: 66.
  - Average plan cost for 30 tablets (1 a day): $206.43 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: Xarelto (rivaroxaban): 62% off the 2023 list price for a 30-day supply.

## Warfarin 5 mg tablet

- **RxNorm:** warfarin — brands: Coumadin, Jantoven — 3 RxCUIs, 153 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.09 per EA (median of 17 NDCs) -> about $2.67 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=warfarin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $3.98 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Entresto (sacubitril/valsartan) 49/51 mg tablet

- **RxNorm:** sacubitril / sacubitril / valsartan / valsartan — brands: Entresto — 2 RxCUIs, 90 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.54 per EA (median of 34 NDCs) -> about $32.56 for 60 tablets (1 twice a day); Brand: $11.56 per EA (median of 2 NDCs) -> about $693.67 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 2 units/day. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=sacubitril>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 3: 74. Restrictions on that tier (number of plans): quantity limit: 60.
  - Average plan cost for 60 tablets (1 twice a day): $149.42 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: Entresto (sacubitril/valsartan): 53% off the 2023 list price for a 30-day supply.

## Repatha (evolocumab) 140 mg pen

- **RxNorm:** evolocumab — brands: Repatha — 2 RxCUIs, 11 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $282.01 per ML (median of 2 NDCs) -> about $564.02 for 2 pens (every other week)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=evolocumab>)
- **Medicare Part D (Massachusetts):** on the formulary of 94 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 82. Restrictions on that tier (number of plans): quantity limit: 58, prior auth: 78.
  - Average plan cost for 2 pens (every other week): $569.31 (from 94 plans' pricing; this is the plan's drug price, not the patient's share).

## Brilinta (ticagrelor) 90 mg tablet

- **RxNorm:** ticagrelor — brands: Brilinta — 2 RxCUIs, 82 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.24 per EA (median of 21 NDCs) -> about $14.57 for 60 tablets (1 twice a day); Brand: $7.42 per EA (median of 2 NDCs) -> about $444.90 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=ticagrelor>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 3: 61, tier 4: 13. Restrictions on that tier (number of plans): quantity limit: 25.
  - Average plan cost for 60 tablets (1 twice a day): $152.81 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Nitroglycerin 0.4 mg sublingual tablet

- **RxNorm:** nitroglycerin — brands: Nitrostat — 2 RxCUIs, 82 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.13 per EA (median of 23 NDCs) -> about $3.24 for 25 tablets (1 bottle)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=nitroglycerin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 14, tier 2: 72, tier 3: 10. Restrictions on that tier (number of plans): none.
  - Average plan cost for 25 tablets (1 bottle): $6.40 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Escitalopram 10 mg tablet

- **RxNorm:** escitalopram — brands: Lexapro — 2 RxCUIs, 224 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 22 NDCs) -> about $1.17 for 30 tablets (1 a day); Brand: $15.43 per EA (median of 1 NDCs) -> about $462.77 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=escitalopram>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 62, tier 2: 33, tier 4: 1. Restrictions on that tier (number of plans): quantity limit: 16.
  - Average plan cost for 30 tablets (1 a day): $5.17 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Bupropion XL 150 mg tablet

- **RxNorm:** bupropion — brands: Wellbutrin — 2 RxCUIs, 303 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.08 per EA (median of 51 NDCs) -> about $2.35 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years; or > 1 unit/day. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=bupropion>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 73, tier 3: 11. Restrictions on that tier (number of plans): quantity limit: 50.
  - Average plan cost for 30 tablets (1 a day): $7.35 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Fluoxetine 20 mg capsule

- **RxNorm:** fluoxetine — brands: Prozac — 2 RxCUIs, 287 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 30 NDCs) -> about $0.88 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=fluoxetine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 93, tier 2: 3. Restrictions on that tier (number of plans): quantity limit: 23.
  - Average plan cost for 30 capsules (1 a day): $2.78 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Trazodone 50 mg tablet

- **RxNorm:** trazodone — brands: not found — 1 RxCUIs, 243 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 28 NDCs) -> about $0.90 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=trazodone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 72, tier 2: 24. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $3.55 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Duloxetine 60 mg DR capsule

- **RxNorm:** duloxetine — brands: Cymbalta — 2 RxCUIs, 281 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.14 per EA (median of 23 NDCs) -> about $4.10 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=duloxetine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 74, tier 3: 10. Restrictions on that tier (number of plans): quantity limit: 96.
  - Average plan cost for 30 capsules (1 a day): $8.46 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Buspirone 10 mg tablet

- **RxNorm:** buspirone — brands: not found — 1 RxCUIs, 283 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 29 NDCs) -> about $1.66 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=buspirone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 41, tier 2: 55. Restrictions on that tier (number of plans): none.
  - Average plan cost for 60 tablets (1 twice a day): $6.58 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Venlafaxine ER 75 mg capsule

- **RxNorm:** venlafaxine — brands: Effexor — 2 RxCUIs, 251 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.08 per EA (median of 32 NDCs) -> about $2.40 for 30 capsules (1 a day); Brand: $19.81 per EA (median of 2 NDCs) -> about $594.38 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=venlafaxine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 22, tier 2: 54, tier 3: 20. Restrictions on that tier (number of plans): quantity limit: 23.
  - Average plan cost for 30 capsules (1 a day): $7.79 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Hydroxyzine HCl 25 mg tablet

- **RxNorm:** hydroxyzine — brands: not found — 1 RxCUIs, 300 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 25 NDCs) -> about $0.97 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=hydroxyzine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 33, tier 3: 21, tier 4: 30. Restrictions on that tier (number of plans): prior auth: 48.
  - Average plan cost for 30 tablets: $3.60 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Quetiapine 25 mg tablet

- **RxNorm:** quetiapine — brands: Seroquel — 2 RxCUIs, 159 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 23 NDCs) -> about $0.63 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 10 years; or > 3 units/day. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=quetiapine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 75, tier 3: 8, tier 4: 1. Restrictions on that tier (number of plans): quantity limit: 88, prior auth: 4.
  - Average plan cost for 30 tablets (1 a day): $3.52 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Aripiprazole 5 mg tablet

- **RxNorm:** aripiprazole — brands: Abilify — 2 RxCUIs, 157 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.12 per EA (median of 32 NDCs) -> about $3.50 for 30 tablets (1 a day); Brand: $18.68 per EA (median of 1 NDCs) -> about $560.39 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 10 years; or > 2 units/day. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=aripiprazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 43, tier 3: 26, tier 4: 15. Restrictions on that tier (number of plans): quantity limit: 60, prior auth: 4.
  - Average plan cost for 30 tablets (1 a day): $10.06 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Lamotrigine 100 mg tablet

- **RxNorm:** lamotrigine — brands: Lamictal, Subvenite — 3 RxCUIs, 131 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.05 per EA (median of 21 NDCs) -> about $1.45 for 30 tablets (1 a day); Brand: $10.91 per EA (median of 1 NDCs) -> about $327.44 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=lamotrigine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 44, tier 2: 52. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $4.11 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Alprazolam 0.5 mg tablet

- **RxNorm:** alprazolam — brands: Xanax — 2 RxCUIs, 188 NDCs. Controlled: yes, C-IV.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 18 NDCs) -> about $0.68 for 30 tablets; Brand: $7.03 per EA (median of 3 NDCs) -> about $210.77 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=alprazolam>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 23, tier 2: 64, tier 3: 7, tier 4: 2. Restrictions on that tier (number of plans): prior auth: 24, quantity limit: 73.
  - Average plan cost for 30 tablets: $2.89 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Clonazepam 0.5 mg tablet

- **RxNorm:** clonazepam — brands: Klonopin — 2 RxCUIs, 263 NDCs. Controlled: yes, C-IV.
- **FDA shortage:** in shortage. FDA lists a current shortage for 1 package(s) of this exact drug and strength. Some makers may still have it. Call the pharmacy to check. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'Available': 39, 'Unavailable': 1}
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 20 NDCs) -> about $0.59 for 30 tablets; Brand: $2.68 per EA (median of 1 NDCs) -> about $80.41 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=clonazepam>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 38, tier 2: 33, tier 3: 25. Restrictions on that tier (number of plans): quantity limit: 66.
  - Average plan cost for 30 tablets: $1.84 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Lorazepam 0.5 mg tablet

- **RxNorm:** lorazepam — brands: Ativan — 2 RxCUIs, 237 NDCs. Controlled: yes, C-IV.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 17 NDCs) -> about $1.09 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=lorazepam>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 23, tier 2: 70, tier 3: 2, tier 4: 1. Restrictions on that tier (number of plans): quantity limit: 73, prior auth: 11.
  - Average plan cost for 30 tablets: $3.84 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Zolpidem 10 mg tablet

- **RxNorm:** zolpidem — brands: Ambien — 2 RxCUIs, 277 NDCs. Controlled: yes, C-IV.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 12 NDCs) -> about $1.17 for 30 tablets; Brand: $22.61 per EA (median of 2 NDCs) -> about $678.40 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years; or > 1 unit/day. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=zolpidem>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 19, tier 2: 76, tier 3: 1. Restrictions on that tier (number of plans): quantity limit: 73, prior auth: 24.
  - Average plan cost for 30 tablets: $3.89 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Amphetamine salts (Adderall) 10 mg tablet

- **RxNorm:** amphetamine / amphetamine aspartate / amphetamine sulfate / dextroamphetamine saccharate / dextroamphetamine sulfate / dextroamphetamine — brands: Adderall — 2 RxCUIs, 49 NDCs. Controlled: yes, C-II.
- **FDA shortage:** in shortage. FDA lists a current shortage for 28 package(s) of this exact drug and strength. Some makers may still have it. Call the pharmacy to check. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'Available': 40, 'Unavailable': 19, 'Limited Availability': 9}
- **NADAC (as of 10/21/2026):** Generic: $0.23 per EA (median of 15 NDCs) -> about $13.63 for 60 tablets (1 twice a day); Brand: $12.20 per EA (median of 1 NDCs) -> about $731.97 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 3 units/day. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=amphetamine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 46, tier 3: 38. Restrictions on that tier (number of plans): quantity limit: 73, prior auth: 17.
  - Average plan cost for 60 tablets (1 twice a day): $21.59 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Lisdexamfetamine (Vyvanse) 30 mg capsule

- **RxNorm:** lisdexamfetamine — brands: Vyvanse — 2 RxCUIs, 23 NDCs. Controlled: yes, C-II.
- **FDA shortage:** in shortage. FDA lists a current shortage for 34 package(s) of this exact drug and strength. Some makers may still have it. Call the pharmacy to check. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'Limited Availability': 34, 'Available': 50}
- **NADAC (as of 10/21/2026):** Generic: $2.88 per EA (median of 17 NDCs) -> about $86.54 for 30 capsules (1 a day); Brand: $12.34 per EA (median of 1 NDCs) -> about $370.28 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 2 units/day. BP: Brand preferred over generics: MassHealth wants the brand tried first. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=lisdexamfetamine>)
- **Medicare Part D (Massachusetts):** on the formulary of 33 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 2, tier 3: 4, tier 4: 27. Restrictions on that tier (number of plans): quantity limit: 17.
  - Average plan cost for 30 capsules (1 a day): $203.98 (from 33 plans' pricing; this is the plan's drug price, not the patient's share).

## Methylphenidate (Ritalin) 10 mg tablet

- **RxNorm:** methylphenidate — brands: Ritalin — 2 RxCUIs, 37 NDCs. Controlled: yes, C-II.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Film, Extended Release, Tablet (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.15 per EA (median of 11 NDCs) -> about $8.98 for 60 tablets (1 twice a day); Brand: $1.13 per EA (median of 1 NDCs) -> about $68.09 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 3 units/day. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=methylphenidate>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 53, tier 3: 31. Restrictions on that tier (number of plans): quantity limit: 73, prior auth: 21.
  - Average plan cost for 60 tablets (1 twice a day): $14.24 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Dexmethylphenidate ER (Focalin XR) 10 mg capsule

- **RxNorm:** dexmethylphenidate — brands: Focalin — 2 RxCUIs, 14 NDCs. Controlled: yes, C-II.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.39 per EA (median of 6 NDCs) -> about $41.78 for 30 capsules (1 a day); Brand: $4.76 per EA (median of 2 NDCs) -> about $142.71 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years or >= 21 years; or > 2 units/day. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=dexmethylphenidate>)
- **Medicare Part D (Massachusetts):** on the formulary of 58 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 5, tier 3: 4, tier 4: 49. Restrictions on that tier (number of plans): quantity limit: 15.
  - Average plan cost for 30 capsules (1 a day): $57.53 (from 58 plans' pricing; this is the plan's drug price, not the patient's share).

## Atomoxetine (Strattera) 40 mg capsule

- **RxNorm:** atomoxetine — brands: Strattera — 2 RxCUIs, 48 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.44 per EA (median of 14 NDCs) -> about $13.34 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=atomoxetine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 3: 19, tier 4: 55. Restrictions on that tier (number of plans): quantity limit: 96.
  - Average plan cost for 30 capsules (1 a day): $38.13 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Guanfacine ER (Intuniv) 1 mg tablet

- **RxNorm:** guanfacine — brands: Intuniv — 2 RxCUIs, 47 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 4}
- **NADAC (as of 10/21/2026):** Generic: $0.13 per EA (median of 8 NDCs) -> about $3.97 for 30 tablets (1 a day); Brand: $9.35 per EA (median of 1 NDCs) -> about $280.56 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 3 years. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=guanfacine>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 25, tier 3: 38, tier 4: 20. Restrictions on that tier (number of plans): prior auth: 24, quantity limit: 67.
  - Average plan cost for 30 tablets (1 a day): $12.24 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Hydrocodone/acetaminophen 5/325 mg tablet

- **RxNorm:** acetaminophen / acetaminophen / hydrocodone / hydrocodone — brands: Norco — 2 RxCUIs, 337 NDCs. Controlled: yes, C-II.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.13 per EA (median of 32 NDCs) -> about $2.64 for 20 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 120 mg/day hydrocodone; or > 4 g/day acetaminophen.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=hydrocodone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 19, tier 2: 37, tier 3: 37, tier 4: 3. Restrictions on that tier (number of plans): quantity limit: 88.
  - Average plan cost for 20 tablets: $3.58 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Oxycodone 5 mg tablet

- **RxNorm:** oxycodone — brands: Oxaydo, Roxicodone — 3 RxCUIs, 130 NDCs. Controlled: yes, C-II.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.09 per EA (median of 18 NDCs) -> about $1.85 for 20 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 80 mg/day. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=oxycodone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 40, tier 3: 42, tier 4: 2. Restrictions on that tier (number of plans): quantity limit: 88.
  - Average plan cost for 20 tablets: $2.92 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Oxycodone/acetaminophen (Percocet) 5/325 mg tablet

- **RxNorm:** acetaminophen / acetaminophen / oxycodone / oxycodone — brands: Endocet, Percocet — 3 RxCUIs, 218 NDCs. Controlled: yes, C-II.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 5}
- **NADAC (as of 10/21/2026):** Generic: $0.12 per EA (median of 28 NDCs) -> about $2.36 for 20 tablets; Brand: $29.32 per EA (median of 1 NDCs) -> about $586.31 for 20 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 80 mg/day oxycodone; or > 4 g/day acetaminophen.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=oxycodone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 40, tier 3: 39, tier 4: 5. Restrictions on that tier (number of plans): quantity limit: 88.
  - Average plan cost for 20 tablets: $3.53 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Tramadol 50 mg tablet

- **RxNorm:** tramadol — brands: Ultram — 2 RxCUIs, 650 NDCs. Controlled: yes, C-IV.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 29 NDCs) -> about $0.78 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 12 years; or > 400 mg/day.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=tramadol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 38, tier 2: 57, tier 3: 1. Restrictions on that tier (number of plans): quantity limit: 88.
  - Average plan cost for 30 tablets: $2.52 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Gabapentin 300 mg capsule

- **RxNorm:** gabapentin — brands: Neurontin, Relgaabi — 3 RxCUIs, 775 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 55 NDCs) -> about $2.95 for 90 capsules (1 three times a day); Brand: $7.36 per EA (median of 2 NDCs) -> about $662.81 for 90 capsules (1 three times a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years; or > 3600 mg/day. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=gabapentin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 22, tier 2: 64, tier 3: 10. Restrictions on that tier (number of plans): quantity limit: 56.
  - Average plan cost for 90 capsules (1 three times a day): $9.14 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Pregabalin (Lyrica) 75 mg capsule

- **RxNorm:** pregabalin — brands: Lyrica — 2 RxCUIs, 291 NDCs. Controlled: yes, C-V.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per EA (median of 30 NDCs) -> about $3.34 for 60 capsules (1 twice a day); Brand: $9.67 per EA (median of 3 NDCs) -> about $580.27 for 60 capsules (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 6 years; or > 600 mg/day. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=pregabalin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 40, tier 3: 41, tier 4: 3. Restrictions on that tier (number of plans): quantity limit: 73, prior auth: 24.
  - Average plan cost for 60 capsules (1 twice a day): $8.86 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Buprenorphine/naloxone (Suboxone) 8/2 mg film

- **RxNorm:** buprenorphine / buprenorphine / naloxone / naloxone — brands: Suboxone — 2 RxCUIs, 23 NDCs. Controlled: yes, C-III.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $1.95 per EA (median of 8 NDCs) -> about $58.45 for 30 films (1 a day); Brand: $8.59 per EA (median of 2 NDCs) -> about $257.68 for 30 films (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 32 mg/day. BP: Brand preferred over generics: MassHealth wants the brand tried first. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=buprenorphine>)
- **Medicare Part D (Massachusetts):** on the formulary of 89 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 40, tier 4: 30, tier 6: 7. Restrictions on that tier (number of plans): quantity limit: 28.
  - Average plan cost for 30 films (1 a day): $84.33 (from 89 plans' pricing; this is the plan's drug price, not the patient's share).

## Meloxicam 15 mg tablet

- **RxNorm:** meloxicam — brands: Mobic — 2 RxCUIs, 363 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 23 NDCs) -> about $0.55 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=meloxicam>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 96. Restrictions on that tier (number of plans): quantity limit: 15.
  - Average plan cost for 30 tablets (1 a day): $2.39 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Ibuprofen 800 mg tablet

- **RxNorm:** ibuprofen — brands: Ibu, Samson 8 — 3 RxCUIs, 684 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per EA (median of 39 NDCs) -> about $5.00 for 90 tablets (up to 3 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. *: The generic OTC (and generic prescription) versions are payable without PA. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=ibuprofen>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 92, tier 2: 4. Restrictions on that tier (number of plans): quantity limit: 4.
  - Average plan cost for 90 tablets (up to 3 a day): $7.75 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Cyclobenzaprine 10 mg tablet

- **RxNorm:** cyclobenzaprine — brands: not found — 1 RxCUIs, 695 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.02 per EA (median of 43 NDCs) -> about $0.52 for 30 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: < 15 years. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=cyclobenzaprine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 19, tier 2: 52, tier 3: 19, tier 4: 6. Restrictions on that tier (number of plans): prior auth: 52, quantity limit: 24.
  - Average plan cost for 30 tablets: $2.93 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Diclofenac 1% gel

- **RxNorm:** diclofenac — brands: Aleve Arthritis Pain, Voltaren — 3 RxCUIs, 253 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.08 per GM (median of 22 NDCs) -> about $8.05 for 1 tube (100 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. *: The generic OTC (and generic prescription) versions are payable without PA. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=diclofenac>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Phentermine 37.5 mg tablet

- **RxNorm:** phentermine — brands: Adipex-P — 2 RxCUIs, 282 NDCs. Controlled: yes, C-IV.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.07 per EA (median of 12 NDCs) -> about $2.21 for 30 tablets (1 a day)
- **MassHealth:** not found; PA: not found. Not on the MassHealth Drug List (website search and the October 01, 2026 PDF). The List says any drug not on it requires PA. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=phentermine>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

## Testosterone cypionate 200 mg/mL injection

- **RxNorm:** testosterone — brands: Azmiro, Depo-testosterone — 4 RxCUIs, 72 NDCs. Controlled: yes, C-III.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $11.01 per ML (median of 21 NDCs) -> about $11.01 for 1 mL
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=testosterone>)
- **Medicare Part D (Massachusetts):** on the formulary of 95 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 65, tier 3: 18. Restrictions on that tier (number of plans): prior auth: 37.
  - Average plan cost for 1 mL: $7.24 (from 95 plans' pricing; this is the plan's drug price, not the patient's share).

## Pantoprazole 40 mg DR tablet

- **RxNorm:** pantoprazole — brands: Protonix — 2 RxCUIs, 287 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.04 per EA (median of 40 NDCs) -> about $1.10 for 30 tablets (1 a day); Brand: $14.24 per EA (median of 1 NDCs) -> about $427.18 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: only in some cases: > 4 units/day. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=pantoprazole>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 50, tier 2: 46. Restrictions on that tier (number of plans): quantity limit: 50.
  - Average plan cost for 30 tablets (1 a day): $5.48 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Famotidine 20 mg tablet

- **RxNorm:** famotidine — brands: Calmicid, Pepcid, Zantac Reformulated Aug 2022 — 4 RxCUIs, 694 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 62 NDCs) -> about $1.69 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. *: The generic OTC (and generic prescription) versions are payable without PA. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=famotidine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 54, tier 2: 34, tier 3: 7, tier 4: 1. Restrictions on that tier (number of plans): none.
  - Average plan cost for 60 tablets (1 twice a day): $8.45 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Ondansetron 4 mg orally disintegrating tablet

- **RxNorm:** ondansetron — brands: not found — 1 RxCUIs, 216 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.12 per EA (median of 14 NDCs) -> about $2.46 for 20 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=ondansetron>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 79, tier 3: 5. Restrictions on that tier (number of plans): prior auth: 90, quantity limit: 17.
  - Average plan cost for 20 tablets: $6.88 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Linzess (linaclotide) 145 mcg capsule

- **RxNorm:** linaclotide — brands: Linzess — 2 RxCUIs, 3 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $9.02 per EA (median of 1 NDCs) -> about $270.56 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes.  (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=linaclotide>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 78, tier 4: 6. Restrictions on that tier (number of plans): quantity limit: 73.
  - Average plan cost for 30 capsules (1 a day): $275.23 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Prednisone 20 mg tablet

- **RxNorm:** prednisone — brands: Deltasone — 2 RxCUIs, 531 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per EA (median of 30 NDCs) -> about $0.65 for 10 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=prednisone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 89, tier 2: 7. Restrictions on that tier (number of plans): prior auth: 31.
  - Average plan cost for 10 tablets: $1.49 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Prednisolone 15 mg/5 mL oral solution

- **RxNorm:** prednisolone — brands: not found — 1 RxCUIs, 53 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.54 per ML (median of 13 NDCs) -> about $54.01 for 100 mL
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=prednisolone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 19, tier 2: 53, tier 4: 24. Restrictions on that tier (number of plans): prior auth: 24.
  - Average plan cost for 100 mL: $71.04 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Methylprednisolone 4 mg dose pack (Medrol)

- **RxNorm:** methylprednisolone — brands: Medrol Dosepak — 2 RxCUIs, 42 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. FDA does list other forms or strengths of the same medicine: Injection (current shortage). Those are different products. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.14 per EA (median of 5 NDCs) -> about $3.03 for 1 dose pack (21 tablets); Brand: $0.29 per EA (median of 1 NDCs) -> about $6.12 for 1 dose pack (21 tablets)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=methylprednisolone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 84. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 dose pack (21 tablets): $5.85 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Allopurinol 100 mg tablet

- **RxNorm:** allopurinol — brands: Zyloprim — 2 RxCUIs, 250 NDCs. Controlled: no.
- **FDA shortage:** shortage resolved or discontinued. FDA has past shortage entries for this drug, but none are current. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
  - Listed packages by availability: {'not found': 4}
- **NADAC (as of 10/21/2026):** Generic: $0.03 per EA (median of 40 NDCs) -> about $0.94 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=allopurinol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 71, tier 2: 25. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $3.80 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Colchicine 0.6 mg tablet

- **RxNorm:** colchicine — brands: Colcrys — 2 RxCUIs, 116 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.12 per EA (median of 29 NDCs) -> about $7.13 for 60 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=colchicine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 25, tier 3: 49, tier 4: 10. Restrictions on that tier (number of plans): quantity limit: 55.
  - Average plan cost for 60 tablets: $31.43 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Estradiol 1 mg tablet

- **RxNorm:** estradiol — brands: Estrace — 2 RxCUIs, 102 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.06 per EA (median of 12 NDCs) -> about $1.90 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=estradiol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 58, tier 2: 37, tier 4: 1. Restrictions on that tier (number of plans): none.
  - Average plan cost for 30 tablets (1 a day): $4.95 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Norgestimate/ethinyl estradiol (Sprintec) birth control pack

- **RxNorm:** ethinyl estradiol / ethinyl estradiol / norgestimate / inert ingredients / norgestimate — brands: Estarylla 28 Day, Femynor 28 Day, Mili 28 Day, Mono-Linyah 28 Day, Nymyo 28 Day, Previfem 28 Day, Sprintec 28 Day, VyLibra 28 Day — 9 RxCUIs, 41 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.11 per EA (median of 13 NDCs) -> about $3.11 for 1 pack (28 tablets)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=ethinyl+estradiol>)
- **Medicare Part D (Massachusetts):** on the formulary of 73 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 8, tier 2: 40, tier 3: 24, tier 4: 1. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 pack (28 tablets): $5.99 (from 73 plans' pricing; this is the plan's drug price, not the patient's share).

## Medroxyprogesterone (Depo-Provera) 150 mg/mL injection

- **RxNorm:** medroxyprogesterone — brands: Depo-Provera — 4 RxCUIs, 52 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $23.04 per ML (median of 17 NDCs) -> about $23.04 for 1 shot (1 mL, every 3 months); Brand: $51.19 per ML (median of 2 NDCs) -> about $51.19 for 1 shot (1 mL, every 3 months)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=medroxyprogesterone>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 49, tier 3: 35. Restrictions on that tier (number of plans): quantity limit: 19.
  - Average plan cost for 1 shot (1 mL, every 3 months): $35.90 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Finasteride 5 mg tablet

- **RxNorm:** finasteride — brands: Proscar — 2 RxCUIs, 180 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.07 per EA (median of 26 NDCs) -> about $2.06 for 30 tablets (1 a day); Brand: $5.70 per EA (median of 2 NDCs) -> about $171.05 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=finasteride>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 64, tier 2: 32. Restrictions on that tier (number of plans): quantity limit: 48.
  - Average plan cost for 30 tablets (1 a day): $7.59 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Tamsulosin 0.4 mg capsule

- **RxNorm:** tamsulosin — brands: Flomax — 2 RxCUIs, 268 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.05 per EA (median of 26 NDCs) -> about $1.47 for 30 capsules (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=tamsulosin>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 42, tier 2: 54. Restrictions on that tier (number of plans): quantity limit: 33.
  - Average plan cost for 30 capsules (1 a day): $6.50 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Alendronate 70 mg tablet (weekly)

- **RxNorm:** alendronate — brands: Fosamax — 2 RxCUIs, 55 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.26 per EA (median of 8 NDCs) -> about $1.03 for 4 tablets (1 a week); Brand: $38.70 per EA (median of 1 NDCs) -> about $154.82 for 4 tablets (1 a week)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=alendronate>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 93, tier 2: 3. Restrictions on that tier (number of plans): quantity limit: 50.
  - Average plan cost for 4 tablets (1 a week): $4.84 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Levetiracetam 500 mg tablet

- **RxNorm:** levetiracetam — brands: Keppra, Roweepra — 3 RxCUIs, 202 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.07 per EA (median of 36 NDCs) -> about $4.33 for 60 tablets (1 twice a day); Brand: $9.92 per EA (median of 1 NDCs) -> about $594.96 for 60 tablets (1 twice a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=levetiracetam>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 63, tier 3: 21. Restrictions on that tier (number of plans): none.
  - Average plan cost for 60 tablets (1 twice a day): $9.52 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Emtricitabine/tenofovir DF (Truvada) 200/300 mg tablet

- **RxNorm:** emtricitabine / emtricitabine / tenofovir disoproxil / tenofovir disoproxil — brands: Truvada — 2 RxCUIs, 65 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.53 per EA (median of 10 NDCs) -> about $15.79 for 30 tablets (1 a day); Brand: $59.59 per EA (median of 1 NDCs) -> about $1,787.78 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. #: Brand-name drug with FDA A-rated generics: PA is required for the brand; the generic is the covered choice. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=emtricitabine>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 10, tier 4: 74. Restrictions on that tier (number of plans): quantity limit: 56.
  - Average plan cost for 30 tablets (1 a day): $199.68 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Biktarvy (bictegravir/emtricitabine/tenofovir alafenamide) tablet

- **RxNorm:** bictegravir / bictegravir / emtricitabine / tenofovir alafenamide / emtricitabine / tenofovir alafenamide — brands: Biktarvy — 2 RxCUIs, 5 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $136.75 per EA (median of 2 NDCs) -> about $4,102.59 for 30 tablets (1 a day)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=bictegravir>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 5: 84. Restrictions on that tier (number of plans): quantity limit: 40.
  - Average plan cost for 30 tablets (1 a day): $4,105.89 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Enbrel (etanercept) 50 mg pen

- **RxNorm:** etanercept — brands: Enbrel — 2 RxCUIs, 5 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $2,083.62 per ML (median of 1 NDCs) -> about $8,334.50 for 4 pens (1 a week)
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=etanercept>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 5: 84. Restrictions on that tier (number of plans): prior auth: 96, quantity limit: 96.
  - Average plan cost for 4 pens (1 a week): $2,335.07 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).
  - Medicare negotiated price (Maximum Fair Price) starting January 1, 2026: Enbrel (etanercept): 67% off the 2023 list price for a 30-day supply.

## Nurtec ODT (rimegepant) 75 mg

- **RxNorm:** rimegepant — brands: Nurtec — 2 RxCUIs, 5 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Brand: $128.66 per EA (median of 1 NDCs) -> about $1,029.30 for 8 tablets
- **MassHealth:** yes (on the MassHealth Drug List); PA: yes. PD: Preferred drug in its class. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=rimegepant>)
- **Medicare Part D (Massachusetts):** on the formulary of 85 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 3: 27, tier 4: 21, tier 5: 25. Restrictions on that tier (number of plans): prior auth: 85, quantity limit: 62.
  - Average plan cost for 8 tablets: $1,047.87 (from 85 plans' pricing; this is the plan's drug price, not the patient's share).

## Timolol 0.5% eye drops

- **RxNorm:** timolol — brands: Timoptic — 2 RxCUIs, 39 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.82 per ML (median of 23 NDCs) -> about $4.11 for 1 bottle (5 mL)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=timolol>)
- **Medicare Part D (Massachusetts):** on the formulary of 96 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 95, tier 2: 1. Restrictions on that tier (number of plans): none.
  - Average plan cost for 1 bottle (5 mL): $6.14 (from 96 plans' pricing; this is the plan's drug price, not the patient's share).

## Clobetasol 0.05% cream

- **RxNorm:** clobetasol — brands: Temovate — 2 RxCUIs, 107 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.17 per GM (median of 34 NDCs) -> about $5.10 for 1 tube (30 g)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. A90: Up to a 90-day supply is allowed. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=clobetasol>)
- **Medicare Part D (Massachusetts):** on the formulary of 94 of 96 plan segments. Plans by lowest tier for this drug: tier 1: 12, tier 2: 43, tier 3: 8, tier 4: 31. Restrictions on that tier (number of plans): quantity limit: 77.
  - Average plan cost for 1 tube (30 g): $15.44 (from 94 plans' pricing; this is the plan's drug price, not the patient's share).

## Vitamin D2 (ergocalciferol) 50,000 unit capsule

- **RxNorm:** ergocalciferol — brands: Drisdol — 2 RxCUIs, 161 NDCs. Controlled: no.
- **FDA shortage:** not found on FDA shortage list. No FDA shortage entry was found for this exact drug and strength. (checked 2026-10-24, <https://www.accessdata.fda.gov/scripts/drugshortages/default.cfm>)
- **NADAC (as of 10/21/2026):** Generic: $0.12 per EA (median of 9 NDCs) -> about $0.46 for 4 capsules (1 a week)
- **MassHealth:** yes (on the MassHealth Drug List); PA: no. M90: Mandatory 90-day supply after a first fill of up to 30 days. (<https://mhdl.pharmacy.services.conduent.com/MHDL/pubdruglistget.do?searchFor=ergocalciferol>)
- **Medicare Part D (Massachusetts):** not on any Massachusetts plan formulary in the CMS file.

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
