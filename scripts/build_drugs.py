"""Build data/drugs.json: RxLantern's 150 drugs matched to RxNorm (NLM) names, RxCUIs, and NDCs, with each
drug's DEA schedule taken from the FDA's public NDC directory (openFDA), never typed in by hand.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe scripts\\build_drugs.py
Uses the free RxNav REST API (https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html) and the openFDA NDC
directory bulk file (https://open.fda.gov/apis/drug/ndc/download/, saved to data/raw/, git-ignored). No keys.

Which drugs: the 25 drugs from Step 3, plus 125 more taken from the ClinCalc DrugStats "Top 300 of 2024"
(AHRQ Medical Expenditure Panel Survey 2024 data; see LIST_SOURCE), favoring shortage-prone and high-cost
medicines patients often struggle to get (GLP-1s, inhalers, insulins, children's antibiotic liquids, ADHD
medicines). Strength and form = the one most often prescribed. The 30-day amount is for cost estimates only.
"""

import io
import json
import re
import sys
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

import httpx

RXNAV = "https://rxnav.nlm.nih.gov/REST"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "drugs.json"
RAW = ROOT / "data" / "raw"
NDC_DIRECTORY = "https://download.open.fda.gov/drug/ndc/drug-ndc-0001-of-0001.json.zip"
NDC_DIRECTORY_PAGE = "https://open.fda.gov/apis/drug/ndc/"
LIST_SOURCE = {
    "name": "ClinCalc DrugStats Database, The Top 300 of 2024 (version 2026.08, updated August 9, 2026)",
    "url": "https://clincalc.com/DrugStats/Top300Drugs.aspx",
    "underlying_data": "Medical Expenditure Panel Survey (MEPS) 2024, Agency for Healthcare Research and Quality (AHRQ)",
    "checked_date": "2026-10-24",
}


def S(units, unit, basis):
    return {"units": units, "nadac_unit": unit, "basis": basis}


def tab(n, what="tablets", how=None):
    return S(n, "EA", f"{n} {what}" + (f" ({how})" if how else ""))


DAY1, DAY2, DAY3 = "1 a day", "1 twice a day", "1 three times a day"

# id, display name, group, RxNorm search term, regex for the generic RxNorm concept(s) (SCD or GPCK; matched
# ignoring case because RxNorm uses Tall Man letters like "predniSONE"), strength, dosage form, and the amount
# used for 30-day cost estimates (NADAC pricing units: EA = each, ML, GM).
# The DEA schedule is NOT typed here: it comes from the openFDA NDC directory (dea_schedules below).
DRUGS = [
    # ---- the 25 drugs from Step 3 (same strengths and forms)
    ("adderall_xr_30", "Adderall XR 30 mg ER capsule", "adhd", "amphetamine",
     r"^24 HR amphetamine aspartate 7\.5 MG / amphetamine sulfate 7\.5 MG / dextroamphetamine saccharate 7\.5 MG / dextroamphetamine sulfate 7\.5 MG Extended Release Oral Capsule$",
     "30 mg (mixed amphetamine salts)", "extended-release capsule", tab(30, "capsules", DAY1)),
    ("concerta_18", "Concerta 18 mg ER tablet", "adhd", "methylphenidate",
     r"^24 HR methylphenidate hydrochloride 18 MG Extended Release Oral Tablet$",
     "18 mg", "extended-release tablet", tab(30, how=DAY1)),
    ("atorvastatin_20", "Atorvastatin 20 mg tablet", "common", "atorvastatin", r"^atorvastatin 20 MG Oral Tablet$",
     "20 mg", "tablet", tab(30, how=DAY1)),
    ("lisinopril_10", "Lisinopril 10 mg tablet", "common", "lisinopril", r"^lisinopril 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30, how=DAY1)),
    ("levothyroxine_50", "Levothyroxine 50 mcg tablet", "common", "levothyroxine", r"^levothyroxine sodium 0\.05 MG Oral Tablet$",
     "50 mcg", "tablet", tab(30, how=DAY1)),
    ("metformin_500", "Metformin 500 mg tablet", "common", "metformin", r"^metformin hydrochloride 500 MG Oral Tablet$",
     "500 mg", "tablet", tab(60, how=DAY2)),
    ("amlodipine_5", "Amlodipine 5 mg tablet", "common", "amlodipine", r"^amlodipine 5 MG Oral Tablet$",
     "5 mg", "tablet", tab(30, how=DAY1)),
    ("omeprazole_20", "Omeprazole 20 mg DR capsule", "common", "omeprazole", r"^omeprazole 20 MG Delayed Release Oral Capsule$",
     "20 mg", "delayed-release capsule", tab(30, "capsules", DAY1)),
    ("sertraline_50", "Sertraline 50 mg tablet", "common", "sertraline", r"^sertraline 50 MG Oral Tablet$",
     "50 mg", "tablet", tab(30, how=DAY1)),
    ("amoxicillin_500", "Amoxicillin 500 mg capsule", "antibiotic", "amoxicillin", r"^amoxicillin 500 MG Oral Capsule$",
     "500 mg", "capsule", tab(30, "capsules", "a typical 10-day course, 3 a day")),
    ("ozempic_05", "Ozempic (semaglutide) 0.5 mg pen", "expensive", "semaglutide",
     r"^0\.25 MG, 0\.5 MG Dose 3 ML semaglutide 0\.68 MG/ML Pen Injector$",
     "0.5 mg per weekly dose (2 mg/3 mL pen)", "pen injector", S(3, "ML", "1 pen (3 mL), about 1 month at 0.5 mg weekly")),
    ("mounjaro_5", "Mounjaro (tirzepatide) 5 mg pen", "expensive", "tirzepatide", r"^0\.5 ML tirzepatide 10 MG/ML Auto-Injector$",
     "5 mg/0.5 mL", "single-dose pen (auto-injector)", S(2, "ML", "4 single-dose pens (0.5 mL each), 1 a week")),
    ("eliquis_5", "Eliquis (apixaban) 5 mg tablet", "expensive", "apixaban", r"^apixaban 5 MG Oral Tablet$",
     "5 mg", "tablet", tab(60, how=DAY2)),
    ("humira_40", "Humira (adalimumab) 40 mg pen", "expensive", "adalimumab", r"^0\.4 ML adalimumab 100 MG/ML Auto-Injector$",
     "40 mg/0.4 mL", "pen (auto-injector)", S(2, "EA", "2 pens (every other week)")),
    ("dupixent_300", "Dupixent (dupilumab) 300 mg pen", "expensive", "dupilumab", r"^2 ML dupilumab 150 MG/ML Auto-Injector$",
     "300 mg/2 mL", "pen (auto-injector)", S(4, "ML", "2 pens (2 mL each), every other week")),
    ("albuterol_hfa", "Albuterol HFA 90 mcg inhaler", "inhaler", "albuterol",
     r"^NDA0\d+ 200 ACTUAT albuterol 0\.09 MG/ACTUAT Metered Dose Inhaler$",
     "90 mcg per puff (200 puffs)", "metered-dose inhaler", S(18, "GM", "1 inhaler (18 g size; some brands are 6.7 g or 8.5 g)")),
    ("lantus_solostar", "Insulin glargine (Lantus SoloStar) pen", "insulin", "insulin glargine", r"^3 ML insulin glargine 100 UNT/ML Pen Injector$",
     "100 units/mL, 3 mL pen", "pen injector", S(15, "ML", "1 box of 5 pens (3 mL each)")),
    ("amoxicillin_susp_400", "Amoxicillin 400 mg/5 mL oral suspension", "antibiotic", "amoxicillin", r"^amoxicillin 80 MG/ML Oral Suspension$",
     "400 mg/5 mL", "oral suspension", S(100, "ML", "1 bottle (100 mL)")),
    ("sumatriptan_50", "Sumatriptan 50 mg tablet", "common", "sumatriptan", r"^sumatriptan 50 MG Oral Tablet$",
     "50 mg", "tablet", tab(9)),
    ("latanoprost_0005", "Latanoprost 0.005% eye drops", "other", "latanoprost", r"^latanoprost 0\.05 MG/ML Ophthalmic Solution$",
     "0.005% (50 mcg/mL)", "eye drops (solution)", S(2.5, "ML", "1 bottle (2.5 mL)")),
    ("fluticasone_nasal_50", "Fluticasone 50 mcg nasal spray", "other", "fluticasone",
     r"^(\d+ ACTUAT )?fluticasone propionate 0\.05 MG/ACTUAT (Metered Dose )?Nasal Spray$",
     "50 mcg per spray", "nasal spray", S(16, "GM", "1 bottle (16 g, about 120 sprays)")),
    ("triamcinolone_cream_01", "Triamcinolone 0.1% cream", "other", "triamcinolone", r"^triamcinolone acetonide 1 MG/ML Topical Cream$",
     "0.1%", "cream", S(30, "GM", "1 tube (30 g)")),
    ("epinephrine_03", "Epinephrine 0.3 mg auto-injector", "other", "epinephrine", r"^(A?NDA\d+ )?0\.3 ML epinephrine 1 MG/ML Auto-Injector$",
     "0.3 mg/0.3 mL", "auto-injector", S(2, "EA", "1 two-pack of auto-injectors")),
    ("nicotine_patch_21", "Nicotine 21 mg patch", "other", "nicotine", r"^24 HR nicotine 0\.875 MG/HR Transdermal System$",
     "21 mg/24 hours", "transdermal patch", S(28, "EA", "28 patches")),
    ("paxlovid", "Paxlovid dose pack", "antiviral", "nirmatrelvir",
     r"^\{20 \(nirmatrelvir 150 MG Oral Tablet\) / 10 \(ritonavir 100 MG Oral Tablet\) \} Pack$",
     "nirmatrelvir 300 mg + ritonavir 100 mg twice daily", "dose pack (5 days)", S(30, "EA", "1 five-day dose pack (30 tablets)")),

    # ---- GLP-1 and other diabetes medicines
    ("wegovy_24", "Wegovy (semaglutide) 2.4 mg pen", "expensive", "semaglutide", r"^0\.75 ML semaglutide 3\.2 MG/ML Auto-Injector$",
     "2.4 mg/0.75 mL", "single-dose pen (auto-injector)", S(3, "ML", "4 single-dose pens (0.75 mL each), 1 a week")),
    ("rybelsus_7", "Rybelsus (semaglutide) 7 mg tablet", "expensive", "semaglutide", r"^semaglutide 7 MG Oral Tablet$",
     "7 mg", "tablet", tab(30, how=DAY1)),
    ("zepbound_25", "Zepbound (tirzepatide) 2.5 mg pen", "expensive", "tirzepatide", r"^0\.5 ML tirzepatide 5 MG/ML Auto-Injector$",
     "2.5 mg/0.5 mL", "single-dose pen (auto-injector)", S(2, "ML", "4 single-dose pens (0.5 mL each), 1 a week")),
    ("trulicity_15", "Trulicity (dulaglutide) 1.5 mg pen", "expensive", "dulaglutide", r"^0\.5 ML dulaglutide 3 MG/ML Auto-Injector$",
     "1.5 mg/0.5 mL", "single-dose pen (auto-injector)", S(2, "ML", "4 single-dose pens (0.5 mL each), 1 a week")),
    ("victoza_18", "Victoza (liraglutide) pen", "expensive", "liraglutide", r"^3 ML liraglutide 6 MG/ML Pen Injector$",
     "18 mg/3 mL pen (0.6, 1.2, or 1.8 mg doses)", "pen injector", S(6, "ML", "2 pens (3 mL each), about 1 month at 1.2 mg a day")),
    ("jardiance_10", "Jardiance (empagliflozin) 10 mg tablet", "expensive", "empagliflozin", r"^empagliflozin 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30, how=DAY1)),
    ("farxiga_10", "Farxiga (dapagliflozin) 10 mg tablet", "expensive", "dapagliflozin", r"^dapagliflozin 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30, how=DAY1)),
    ("januvia_100", "Januvia (sitagliptin) 100 mg tablet", "expensive", "sitagliptin", r"^sitagliptin( phosphate)? 100 MG Oral Tablet$",
     "100 mg", "tablet", tab(30, how=DAY1)),
    ("glipizide_5", "Glipizide 5 mg tablet", "common", "glipizide", r"^glipizide 5 MG Oral Tablet$",
     "5 mg", "tablet", tab(60, how=DAY2)),
    ("pioglitazone_30", "Pioglitazone 30 mg tablet", "common", "pioglitazone", r"^pioglitazone 30 MG Oral Tablet$",
     "30 mg", "tablet", tab(30, how=DAY1)),
    ("metformin_er_500", "Metformin ER 500 mg tablet", "common", "metformin",
     r"^24 HR metformin hydrochloride 500 MG Extended Release Oral Tablet$",
     "500 mg", "extended-release tablet", tab(60, how="2 a day")),

    # ---- insulins
    ("humalog_kwikpen", "Insulin lispro (Humalog KwikPen) pen", "insulin", "insulin lispro", r"^3 ML insulin lispro 100 UNT/ML Pen Injector$",
     "100 units/mL, 3 mL pen", "pen injector", S(15, "ML", "1 box of 5 pens (3 mL each)")),
    ("novolog_flexpen", "Insulin aspart (NovoLog FlexPen) pen", "insulin", "insulin aspart", r"^3 ML insulin aspart,? human 100 UNT/ML Pen Injector$",
     "100 units/mL, 3 mL pen", "pen injector", S(15, "ML", "1 box of 5 pens (3 mL each)")),
    ("tresiba_flextouch", "Insulin degludec (Tresiba FlexTouch) pen", "insulin", "insulin degludec", r"^3 ML insulin degludec 100 UNT/ML Pen Injector$",
     "100 units/mL, 3 mL pen", "pen injector", S(15, "ML", "1 box of 5 pens (3 mL each)")),
    ("toujeo_solostar", "Toujeo SoloStar (insulin glargine 300 units/mL) pen", "insulin", "insulin glargine",
     r"^1\.5 ML insulin glargine 300 UNT/ML Pen Injector$",
     "300 units/mL, 1.5 mL pen", "pen injector", S(4.5, "ML", "1 box of 3 pens (1.5 mL each)")),
    ("insulin_nph_pen", "Insulin NPH (Humulin N / Novolin N) pen", "insulin", "insulin isophane",
     r"^3 ML insulin isophane,? human 100 UNT/ML Pen Injector$",
     "100 units/mL, 3 mL pen", "pen injector", S(15, "ML", "1 box of 5 pens (3 mL each)")),

    # ---- inhalers and breathing
    ("advair_diskus_250", "Fluticasone/salmeterol (Advair Diskus) 250/50 inhaler", "inhaler", "salmeterol",
     r"^60 ACTUAT fluticasone propionate 0\.25 MG/ACTUAT / salmeterol 0\.05 MG/ACTUAT Dry Powder Inhaler$",
     "250 mcg/50 mcg per puff (60 puffs)", "dry powder inhaler", S(60, "EA", "1 inhaler (60 puffs)")),
    ("symbicort_160", "Budesonide/formoterol (Symbicort) 160/4.5 inhaler", "inhaler", "formoterol",
     r"^120 ACTUAT budesonide 0\.16 MG/ACTUAT / formoterol fumarate 0\.0045 MG/ACTUAT Metered Dose Inhaler$",
     "160 mcg/4.5 mcg per puff (120 puffs)", "metered-dose inhaler", S(10.2, "GM", "1 inhaler (120 puffs, 10.2 g)")),
    ("trelegy_100", "Trelegy Ellipta 100/62.5/25 inhaler", "inhaler", "umeclidinium",
     r"^30 ACTUAT fluticasone furoate 0\.1 MG/ACTUAT / umeclidinium 0\.0625 MG/ACTUAT / vilanterol 0\.025 MG/ACTUAT Dry Powder Inhaler$",
     "100/62.5/25 mcg per puff (30 puffs)", "dry powder inhaler", S(30, "EA", "1 inhaler (30 puffs)")),
    ("spiriva_handihaler", "Tiotropium (Spiriva HandiHaler) 18 mcg capsules", "inhaler", "tiotropium",
     r"^tiotropium 0\.018 MG Inhal\w+ Powder$|^tiotropium bromide 0\.018 MG",
     "18 mcg per capsule", "inhalation powder capsules", S(30, "EA", "30 capsules (1 a day)")),
    ("flovent_hfa_110", "Fluticasone (Flovent HFA) 110 mcg inhaler", "inhaler", "fluticasone",
     r"^120 ACTUAT fluticasone propionate 0\.11 MG/ACTUAT Metered Dose Inhaler$",
     "110 mcg per puff (120 puffs)", "metered-dose inhaler", S(12, "GM", "1 inhaler (12 g)")),
    ("albuterol_neb_25", "Albuterol 2.5 mg/3 mL nebulizer solution", "inhaler", "albuterol",
     r"^(3 ML )?albuterol 0\.83 MG/ML Inhalation Solution$",
     "2.5 mg/3 mL", "nebulizer solution (vials)", S(75, "ML", "1 box (25 vials of 3 mL)")),
    ("duoneb", "Ipratropium/albuterol (DuoNeb) nebulizer solution", "inhaler", "ipratropium",
     r"^(3 ML )?albuterol 0\.833 MG/ML / ipratropium bromide 0\.167 MG/ML Inhalation Solution$",
     "0.5 mg/2.5 mg per 3 mL", "nebulizer solution (vials)", S(90, "ML", "30 vials (3 mL each)")),
    ("budesonide_neb_05", "Budesonide 0.5 mg/2 mL nebulizer suspension (Pulmicort Respules)", "inhaler", "budesonide",
     r"^(2 ML )?budesonide 0\.25 MG/ML Inhalation Suspension$",
     "0.5 mg/2 mL", "nebulizer suspension (vials)", S(60, "ML", "30 vials (2 mL each)")),
    ("montelukast_10", "Montelukast 10 mg tablet", "common", "montelukast", r"^montelukast 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30, how=DAY1)),
    ("montelukast_chew_5", "Montelukast 5 mg chewable tablet (children)", "common", "montelukast", r"^montelukast 5 MG Chewable Tablet$",
     "5 mg", "chewable tablet", tab(30, "chewable tablets", DAY1)),
    ("benzonatate_100", "Benzonatate 100 mg capsule", "common", "benzonatate", r"^benzonatate 100 MG Oral Capsule$",
     "100 mg", "capsule", tab(30, "capsules")),
    ("naloxone_nasal_4", "Naloxone 4 mg nasal spray (Narcan)", "other", "naloxone",
     r"^(0\.1 ML )?naloxone hydrochloride 40 MG/ML Nasal Spray$",
     "4 mg per spray", "nasal spray", S(2, "EA", "1 two-pack")),
    ("oseltamivir_75", "Oseltamivir (Tamiflu) 75 mg capsule", "antiviral", "oseltamivir", r"^oseltamivir 75 MG Oral Capsule$",
     "75 mg", "capsule", tab(10, "capsules", "one 5-day course")),
    ("oseltamivir_susp", "Oseltamivir (Tamiflu) 6 mg/mL oral suspension", "antiviral", "oseltamivir", r"^oseltamivir 6 MG/ML Oral Suspension$",
     "6 mg/mL", "oral suspension", S(60, "ML", "1 bottle (60 mL)")),

    # ---- antibiotics, antivirals, antifungals (with children's liquids)
    ("amoxicillin_susp_250", "Amoxicillin 250 mg/5 mL oral suspension", "antibiotic", "amoxicillin", r"^amoxicillin 50 MG/ML Oral Suspension$",
     "250 mg/5 mL", "oral suspension", S(100, "ML", "1 bottle (100 mL)")),
    ("amox_clav_875", "Amoxicillin/clavulanate (Augmentin) 875/125 mg tablet", "antibiotic", "clavulanate",
     r"^amoxicillin 875 MG / clavulanate 125 MG Oral Tablet$",
     "875 mg/125 mg", "tablet", tab(20, how="a 10-day course, 2 a day")),
    ("amox_clav_susp_400", "Amoxicillin/clavulanate 400/57 mg per 5 mL oral suspension", "antibiotic", "clavulanate",
     r"^amoxicillin 80 MG/ML / clavulanate 11\.4 MG/ML Oral Suspension$",
     "400 mg/57 mg per 5 mL", "oral suspension", S(100, "ML", "1 bottle (100 mL)")),
    ("azithromycin_250", "Azithromycin (Z-Pak) 250 mg tablet", "antibiotic", "azithromycin",
     r"^azithromycin 250 MG Oral Tablet$|^\{6 \(azithromycin 250 MG Oral Tablet\) \} Pack$",
     "250 mg", "tablet", tab(6, how="a 5-day pack")),
    ("azithromycin_susp_200", "Azithromycin 200 mg/5 mL oral suspension", "antibiotic", "azithromycin",
     r"^azithromycin 40 MG/ML Oral Suspension$",
     "200 mg/5 mL", "oral suspension", S(15, "ML", "1 bottle (15 mL)")),
    ("cephalexin_500", "Cephalexin 500 mg capsule", "antibiotic", "cephalexin", r"^cephalexin 500 MG Oral Capsule$",
     "500 mg", "capsule", tab(28, "capsules", "a 7-day course, 4 a day")),
    ("cephalexin_susp_250", "Cephalexin 250 mg/5 mL oral suspension", "antibiotic", "cephalexin", r"^cephalexin 50 MG/ML Oral Suspension$",
     "250 mg/5 mL", "oral suspension", S(100, "ML", "1 bottle (100 mL)")),
    ("cefdinir_susp_250", "Cefdinir 250 mg/5 mL oral suspension", "antibiotic", "cefdinir", r"^cefdinir 50 MG/ML Oral Suspension$",
     "250 mg/5 mL", "oral suspension", S(60, "ML", "1 bottle (60 mL)")),
    ("doxycycline_100", "Doxycycline hyclate 100 mg capsule", "antibiotic", "doxycycline", r"^doxycycline hyclate 100 MG Oral Capsule$",
     "100 mg", "capsule", tab(20, "capsules", "a 10-day course, 2 a day")),
    ("smx_tmp_ds", "Sulfamethoxazole/trimethoprim DS 800/160 mg tablet (Bactrim DS)", "antibiotic", "sulfamethoxazole",
     r"^sulfamethoxazole 800 MG / trimethoprim 160 MG Oral Tablet$",
     "800 mg/160 mg", "tablet", tab(20, how="a 10-day course, 2 a day")),
    ("smx_tmp_susp", "Sulfamethoxazole/trimethoprim 200/40 mg per 5 mL oral suspension", "antibiotic", "sulfamethoxazole",
     r"^sulfamethoxazole 40 MG/ML / trimethoprim 8 MG/ML Oral Suspension$",
     "200 mg/40 mg per 5 mL", "oral suspension", S(100, "ML", "1 bottle (100 mL)")),
    ("nitrofurantoin_100", "Nitrofurantoin (Macrobid) 100 mg capsule", "antibiotic", "nitrofurantoin",
     r"^nitrofurantoin,? macrocrystals 25 MG / nitrofurantoin,? monohydrate 75 MG Oral Capsule$",
     "100 mg", "capsule", tab(10, "capsules", "a 5-day course, 2 a day")),
    ("ciprofloxacin_500", "Ciprofloxacin 500 mg tablet", "antibiotic", "ciprofloxacin", r"^ciprofloxacin 500 MG Oral Tablet$",
     "500 mg", "tablet", tab(14, how="a 7-day course, 2 a day")),
    ("metronidazole_500", "Metronidazole 500 mg tablet", "antibiotic", "metronidazole", r"^metronidazole 500 MG Oral Tablet$",
     "500 mg", "tablet", tab(14, how="a 7-day course, 2 a day")),
    ("penicillin_vk_500", "Penicillin VK 500 mg tablet", "antibiotic", "penicillin V", r"^penicillin V potassium 500 MG Oral Tablet$",
     "500 mg", "tablet", tab(40, how="a 10-day course, 4 a day")),
    ("fluconazole_150", "Fluconazole 150 mg tablet", "antiviral", "fluconazole", r"^fluconazole 150 MG Oral Tablet$",
     "150 mg", "tablet", tab(1, "tablet")),
    ("valacyclovir_1g", "Valacyclovir 1 g tablet", "antiviral", "valacyclovir", r"^valacyclovir 1000 MG Oral Tablet$",
     "1 g (1,000 mg)", "tablet", tab(30)),
    ("mupirocin_2", "Mupirocin 2% ointment", "antibiotic", "mupirocin", r"^mupirocin 20 MG/GM Topical Ointment$|^mupirocin 0\.02 MG/MG Topical Ointment$",
     "2%", "ointment", S(22, "GM", "1 tube (22 g)")),

    # ---- heart, blood pressure, cholesterol, blood thinners
    ("losartan_50", "Losartan 50 mg tablet", "common", "losartan", r"^losartan potassium 50 MG Oral Tablet$",
     "50 mg", "tablet", tab(30, how=DAY1)),
    ("metoprolol_succ_er_50", "Metoprolol succinate ER 50 mg tablet", "common", "metoprolol",
     r"^24 HR metoprolol succinate 50 MG Extended Release Oral Tablet$",
     "50 mg", "extended-release tablet", tab(30, how=DAY1)),
    ("metoprolol_tart_25", "Metoprolol tartrate 25 mg tablet", "common", "metoprolol", r"^metoprolol tartrate 25 MG Oral Tablet$",
     "25 mg", "tablet", tab(60, how=DAY2)),
    ("rosuvastatin_10", "Rosuvastatin 10 mg tablet", "common", "rosuvastatin", r"^rosuvastatin calcium 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30, how=DAY1)),
    ("hydrochlorothiazide_25", "Hydrochlorothiazide 25 mg tablet", "common", "hydrochlorothiazide", r"^hydrochlorothiazide 25 MG Oral Tablet$",
     "25 mg", "tablet", tab(30, how=DAY1)),
    ("simvastatin_20", "Simvastatin 20 mg tablet", "common", "simvastatin", r"^simvastatin 20 MG Oral Tablet$",
     "20 mg", "tablet", tab(30, how=DAY1)),
    ("pravastatin_40", "Pravastatin 40 mg tablet", "common", "pravastatin", r"^pravastatin sodium 40 MG Oral Tablet$",
     "40 mg", "tablet", tab(30, how=DAY1)),
    ("furosemide_20", "Furosemide 20 mg tablet", "common", "furosemide", r"^furosemide 20 MG Oral Tablet$",
     "20 mg", "tablet", tab(30, how=DAY1)),
    ("carvedilol_125", "Carvedilol 12.5 mg tablet", "common", "carvedilol", r"^carvedilol 12\.5 MG Oral Tablet$",
     "12.5 mg", "tablet", tab(60, how=DAY2)),
    ("spironolactone_25", "Spironolactone 25 mg tablet", "common", "spironolactone", r"^spironolactone 25 MG Oral Tablet$",
     "25 mg", "tablet", tab(30, how=DAY1)),
    ("clopidogrel_75", "Clopidogrel 75 mg tablet", "common", "clopidogrel", r"^clopidogrel 75 MG Oral Tablet$",
     "75 mg", "tablet", tab(30, how=DAY1)),
    ("valsartan_160", "Valsartan 160 mg tablet", "common", "valsartan", r"^valsartan 160 MG Oral Tablet$",
     "160 mg", "tablet", tab(30, how=DAY1)),
    ("ezetimibe_10", "Ezetimibe 10 mg tablet", "common", "ezetimibe", r"^ezetimibe 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30, how=DAY1)),
    ("propranolol_10", "Propranolol 10 mg tablet", "common", "propranolol", r"^propranolol hydrochloride 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(60, how=DAY2)),
    ("xarelto_20", "Xarelto (rivaroxaban) 20 mg tablet", "expensive", "rivaroxaban", r"^rivaroxaban 20 MG Oral Tablet$",
     "20 mg", "tablet", tab(30, how=DAY1)),
    ("warfarin_5", "Warfarin 5 mg tablet", "common", "warfarin", r"^warfarin sodium 5 MG Oral Tablet$",
     "5 mg", "tablet", tab(30, how=DAY1)),
    ("entresto_49_51", "Entresto (sacubitril/valsartan) 49/51 mg tablet", "expensive", "sacubitril",
     r"^sacubitril 49 MG / valsartan 51 MG Oral Tablet$",
     "49 mg/51 mg", "tablet", tab(60, how=DAY2)),
    ("repatha_140", "Repatha (evolocumab) 140 mg pen", "expensive", "evolocumab", r"^1 ML evolocumab 140 MG/ML Auto-Injector$",
     "140 mg/mL", "pen (auto-injector)", S(2, "ML", "2 pens (every other week)")),
    ("brilinta_90", "Brilinta (ticagrelor) 90 mg tablet", "expensive", "ticagrelor", r"^ticagrelor 90 MG Oral Tablet$",
     "90 mg", "tablet", tab(60, how=DAY2)),
    ("nitroglycerin_sl_04", "Nitroglycerin 0.4 mg sublingual tablet", "common", "nitroglycerin", r"^nitroglycerin 0\.4 MG Sublingual Tablet$",
     "0.4 mg", "sublingual tablet", tab(25, how="1 bottle")),

    # ---- mental health and sleep
    ("escitalopram_10", "Escitalopram 10 mg tablet", "common", "escitalopram", r"^escitalopram 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30, how=DAY1)),
    ("bupropion_xl_150", "Bupropion XL 150 mg tablet", "common", "bupropion",
     r"^24 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet$",
     "150 mg", "extended-release tablet", tab(30, how=DAY1)),
    ("fluoxetine_20", "Fluoxetine 20 mg capsule", "common", "fluoxetine", r"^fluoxetine 20 MG Oral Capsule$",
     "20 mg", "capsule", tab(30, "capsules", DAY1)),
    ("trazodone_50", "Trazodone 50 mg tablet", "common", "trazodone", r"^trazodone hydrochloride 50 MG Oral Tablet$",
     "50 mg", "tablet", tab(30, how=DAY1)),
    ("duloxetine_60", "Duloxetine 60 mg DR capsule", "common", "duloxetine", r"^duloxetine 60 MG Delayed Release Oral Capsule$",
     "60 mg", "delayed-release capsule", tab(30, "capsules", DAY1)),
    ("buspirone_10", "Buspirone 10 mg tablet", "common", "buspirone", r"^buspirone hydrochloride 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(60, how=DAY2)),
    ("venlafaxine_er_75", "Venlafaxine ER 75 mg capsule", "common", "venlafaxine", r"^24 HR venlafaxine 75 MG Extended Release Oral Capsule$",
     "75 mg", "extended-release capsule", tab(30, "capsules", DAY1)),
    ("hydroxyzine_25", "Hydroxyzine HCl 25 mg tablet", "common", "hydroxyzine", r"^hydroxyzine hydrochloride 25 MG Oral Tablet$",
     "25 mg", "tablet", tab(30)),
    ("quetiapine_25", "Quetiapine 25 mg tablet", "common", "quetiapine", r"^quetiapine 25 MG Oral Tablet$",
     "25 mg", "tablet", tab(30, how=DAY1)),
    ("aripiprazole_5", "Aripiprazole 5 mg tablet", "common", "aripiprazole", r"^aripiprazole 5 MG Oral Tablet$",
     "5 mg", "tablet", tab(30, how=DAY1)),
    ("lamotrigine_100", "Lamotrigine 100 mg tablet", "common", "lamotrigine", r"^lamotrigine 100 MG Oral Tablet$",
     "100 mg", "tablet", tab(30, how=DAY1)),
    ("alprazolam_05", "Alprazolam 0.5 mg tablet", "common", "alprazolam", r"^alprazolam 0\.5 MG Oral Tablet$",
     "0.5 mg", "tablet", tab(30)),
    ("clonazepam_05", "Clonazepam 0.5 mg tablet", "common", "clonazepam", r"^clonazepam 0\.5 MG Oral Tablet$",
     "0.5 mg", "tablet", tab(30)),
    ("lorazepam_05", "Lorazepam 0.5 mg tablet", "common", "lorazepam", r"^lorazepam 0\.5 MG Oral Tablet$",
     "0.5 mg", "tablet", tab(30)),
    ("zolpidem_10", "Zolpidem 10 mg tablet", "common", "zolpidem", r"^zolpidem tartrate 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30)),

    # ---- ADHD
    ("adderall_ir_10", "Amphetamine salts (Adderall) 10 mg tablet", "adhd", "amphetamine",
     r"^amphetamine aspartate 2\.5 MG / amphetamine sulfate 2\.5 MG / dextroamphetamine saccharate 2\.5 MG / dextroamphetamine sulfate 2\.5 MG Oral Tablet$",
     "10 mg (mixed amphetamine salts)", "tablet", tab(60, how=DAY2)),
    ("vyvanse_30", "Lisdexamfetamine (Vyvanse) 30 mg capsule", "adhd", "lisdexamfetamine", r"^lisdexamfetamine dimesylate 30 MG Oral Capsule$",
     "30 mg", "capsule", tab(30, "capsules", DAY1)),
    ("methylphenidate_10", "Methylphenidate (Ritalin) 10 mg tablet", "adhd", "methylphenidate",
     r"^methylphenidate hydrochloride 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(60, how=DAY2)),
    ("focalin_xr_10", "Dexmethylphenidate ER (Focalin XR) 10 mg capsule", "adhd", "dexmethylphenidate",
     r"^24 HR dexmethylphenidate hydrochloride 10 MG Extended Release Oral Capsule$",
     "10 mg", "extended-release capsule", tab(30, "capsules", DAY1)),
    ("atomoxetine_40", "Atomoxetine (Strattera) 40 mg capsule", "adhd", "atomoxetine", r"^atomoxetine 40 MG Oral Capsule$",
     "40 mg", "capsule", tab(30, "capsules", DAY1)),
    ("guanfacine_er_1", "Guanfacine ER (Intuniv) 1 mg tablet", "adhd", "guanfacine", r"^24 HR guanfacine 1 MG Extended Release Oral Tablet$",
     "1 mg", "extended-release tablet", tab(30, how=DAY1)),

    # ---- pain, nerve pain, muscle, addiction treatment
    ("hydrocodone_apap_5_325", "Hydrocodone/acetaminophen 5/325 mg tablet", "pain", "hydrocodone",
     r"^acetaminophen 325 MG / hydrocodone bitartrate 5 MG Oral Tablet$",
     "5 mg/325 mg", "tablet", tab(20)),
    ("oxycodone_5", "Oxycodone 5 mg tablet", "pain", "oxycodone", r"^oxycodone hydrochloride 5 MG Oral Tablet$",
     "5 mg", "tablet", tab(20)),
    ("oxycodone_apap_5_325", "Oxycodone/acetaminophen (Percocet) 5/325 mg tablet", "pain", "oxycodone",
     r"^acetaminophen 325 MG / oxycodone hydrochloride 5 MG Oral Tablet$",
     "5 mg/325 mg", "tablet", tab(20)),
    ("tramadol_50", "Tramadol 50 mg tablet", "pain", "tramadol", r"^tramadol hydrochloride 50 MG Oral Tablet$",
     "50 mg", "tablet", tab(30)),
    ("gabapentin_300", "Gabapentin 300 mg capsule", "common", "gabapentin", r"^gabapentin 300 MG Oral Capsule$",
     "300 mg", "capsule", tab(90, "capsules", DAY3)),
    ("pregabalin_75", "Pregabalin (Lyrica) 75 mg capsule", "pain", "pregabalin", r"^pregabalin 75 MG Oral Capsule$",
     "75 mg", "capsule", tab(60, "capsules", DAY2)),
    ("buprenorphine_naloxone_8_2", "Buprenorphine/naloxone (Suboxone) 8/2 mg film", "pain", "buprenorphine",
     r"^buprenorphine 8 MG / naloxone 2 MG Sublingual Film$",
     "8 mg/2 mg", "sublingual film", S(30, "EA", "30 films (1 a day)")),
    ("meloxicam_15", "Meloxicam 15 mg tablet", "common", "meloxicam", r"^meloxicam 15 MG Oral Tablet$",
     "15 mg", "tablet", tab(30, how=DAY1)),
    ("ibuprofen_800", "Ibuprofen 800 mg tablet", "common", "ibuprofen", r"^ibuprofen 800 MG Oral Tablet$",
     "800 mg", "tablet", tab(90, how="up to 3 a day")),
    ("cyclobenzaprine_10", "Cyclobenzaprine 10 mg tablet", "common", "cyclobenzaprine", r"^cyclobenzaprine hydrochloride 10 MG Oral Tablet$",
     "10 mg", "tablet", tab(30)),
    ("diclofenac_gel_1", "Diclofenac 1% gel", "other", "diclofenac", r"^diclofenac sodium (10 MG/GM|10 MG/ML|0\.01 MG/MG) Topical Gel$",
     "1%", "gel", S(100, "GM", "1 tube (100 g)")),
    ("phentermine_375", "Phentermine 37.5 mg tablet", "other", "phentermine", r"^phentermine hydrochloride 37\.5 MG Oral Tablet$",
     "37.5 mg", "tablet", tab(30, how=DAY1)),
    ("testosterone_cyp_200", "Testosterone cypionate 200 mg/mL injection", "other", "testosterone",
     r"^(1|10) ML testosterone cypionate 200 MG/ML Injection$|^testosterone cypionate 200 MG/ML Injectable Solution$",
     "200 mg/mL", "injection (vial)", S(1, "ML", "1 mL")),

    # ---- stomach
    ("pantoprazole_40", "Pantoprazole 40 mg DR tablet", "common", "pantoprazole", r"^pantoprazole 40 MG Delayed Release Oral Tablet$",
     "40 mg", "delayed-release tablet", tab(30, how=DAY1)),
    ("famotidine_20", "Famotidine 20 mg tablet", "common", "famotidine", r"^famotidine 20 MG Oral Tablet$",
     "20 mg", "tablet", tab(60, how=DAY2)),
    ("ondansetron_odt_4", "Ondansetron 4 mg orally disintegrating tablet", "common", "ondansetron",
     r"^ondansetron 4 MG Disintegrating Oral Tablet$",
     "4 mg", "orally disintegrating tablet", tab(20)),
    ("linzess_145", "Linzess (linaclotide) 145 mcg capsule", "expensive", "linaclotide", r"^linaclotide 0\.145 MG Oral Capsule$",
     "145 mcg", "capsule", tab(30, "capsules", DAY1)),

    # ---- other common and specialty medicines
    ("prednisone_20", "Prednisone 20 mg tablet", "common", "prednisone", r"^prednisone 20 MG Oral Tablet$",
     "20 mg", "tablet", tab(10)),
    ("prednisolone_soln_15", "Prednisolone 15 mg/5 mL oral solution", "common", "prednisolone",
     r"^prednisolone 3 MG/ML Oral Solution$",
     "15 mg/5 mL", "oral solution", S(100, "ML", "100 mL")),
    ("methylprednisolone_4_pack", "Methylprednisolone 4 mg dose pack (Medrol)", "common", "methylprednisolone",
     r"^\{21 \(methylprednisolone 4 MG Oral Tablet\) \} Pack$",
     "4 mg (21 tablets, 6 days)", "dose pack", S(21, "EA", "1 dose pack (21 tablets)")),
    ("allopurinol_100", "Allopurinol 100 mg tablet", "common", "allopurinol", r"^allopurinol 100 MG Oral Tablet$",
     "100 mg", "tablet", tab(30, how=DAY1)),
    ("colchicine_06", "Colchicine 0.6 mg tablet", "common", "colchicine", r"^colchicine 0\.6 MG Oral Tablet$",
     "0.6 mg", "tablet", tab(60)),
    ("estradiol_1", "Estradiol 1 mg tablet", "common", "estradiol", r"^estradiol 1 MG Oral Tablet$",
     "1 mg", "tablet", tab(30, how=DAY1)),
    ("norgestimate_ee", "Norgestimate/ethinyl estradiol (Sprintec) birth control pack", "common", "norgestimate",
     r"^\{21 \(ethinyl estradiol 0\.035 MG / norgestimate 0\.25 MG Oral Tablet\) / 7 \(inert ingredients 1 MG Oral Tablet\) \} Pack$",
     "0.25 mg/0.035 mg", "tablet pack (28 days)", S(28, "EA", "1 pack (28 tablets)")),
    ("medroxyprogesterone_inj_150", "Medroxyprogesterone (Depo-Provera) 150 mg/mL injection", "other", "medroxyprogesterone",
     r"^1 ML medroxyprogesterone acetate 150 MG/ML (Prefilled Syringe|Injection)$",
     "150 mg/mL", "injection (every 3 months)", S(1, "ML", "1 shot (1 mL, every 3 months)")),
    ("finasteride_5", "Finasteride 5 mg tablet", "common", "finasteride", r"^finasteride 5 MG Oral Tablet$",
     "5 mg", "tablet", tab(30, how=DAY1)),
    ("tamsulosin_04", "Tamsulosin 0.4 mg capsule", "common", "tamsulosin", r"^tamsulosin hydrochloride 0\.4 MG Oral Capsule$",
     "0.4 mg", "capsule", tab(30, "capsules", DAY1)),
    ("alendronate_70", "Alendronate 70 mg tablet (weekly)", "common", "alendronate",
     r"^alendronic acid 70 MG Oral Tablet$|^alendronate sodium 70 MG Oral Tablet$",
     "70 mg", "tablet", tab(4, how="1 a week")),
    ("levetiracetam_500", "Levetiracetam 500 mg tablet", "common", "levetiracetam", r"^levetiracetam 500 MG Oral Tablet$",
     "500 mg", "tablet", tab(60, how=DAY2)),
    ("truvada_prep", "Emtricitabine/tenofovir DF (Truvada) 200/300 mg tablet", "expensive", "emtricitabine",
     r"^emtricitabine 200 MG / tenofovir disoproxil fumarate 300 MG Oral Tablet$",
     "200 mg/300 mg", "tablet", tab(30, how=DAY1)),
    ("biktarvy", "Biktarvy (bictegravir/emtricitabine/tenofovir alafenamide) tablet", "expensive", "bictegravir",
     r"^bictegravir 50 MG / emtricitabine 200 MG / tenofovir alafenamide 25 MG Oral Tablet$",
     "50 mg/200 mg/25 mg", "tablet", tab(30, how=DAY1)),
    ("enbrel_50", "Enbrel (etanercept) 50 mg pen", "expensive", "etanercept", r"^1 ML etanercept 50 MG/ML Auto-Injector$",
     "50 mg/mL", "pen (auto-injector)", S(4, "ML", "4 pens (1 a week)")),
    ("nurtec_75", "Nurtec ODT (rimegepant) 75 mg", "expensive", "rimegepant", r"^rimegepant 75 MG Disintegrating Oral Tablet$",
     "75 mg", "orally disintegrating tablet", tab(8)),
    ("timolol_eye_05", "Timolol 0.5% eye drops", "other", "timolol", r"^12 HR timolol 5 MG/ML Ophthalmic Solution$",
     "0.5%", "eye drops (solution)", S(5, "ML", "1 bottle (5 mL)")),
    ("clobetasol_cream_005", "Clobetasol 0.05% cream", "other", "clobetasol", r"^clobetasol propionate 0\.5 MG/(GM|ML) Topical Cream$",
     "0.05%", "cream", S(30, "GM", "1 tube (30 g)")),
    ("ergocalciferol_50000", "Vitamin D2 (ergocalciferol) 50,000 unit capsule", "other", "ergocalciferol",
     r"^ergocalciferol 1\.25 MG Oral Capsule$",
     "50,000 units (1.25 mg)", "capsule", tab(4, "capsules", "1 a week")),
]

# For brand-name items, keep only that brand's products (e.g. Mounjaro, not Zepbound, which shares
# the same RxNorm generic concept). Others keep every single-drug brand (SBD).
BRAND_ONLY = {"adderall_xr_30": "Adderall", "concerta_18": "Concerta", "ozempic_05": "Ozempic",
              "mounjaro_5": "Mounjaro", "eliquis_5": "Eliquis", "humira_40": "Humira", "dupixent_300": "Dupixent",
              "lantus_solostar": "Lantus", "paxlovid": "Paxlovid 5-Day",
              "wegovy_24": "Wegovy", "rybelsus_7": "Rybelsus", "zepbound_25": "Zepbound", "trulicity_15": "Trulicity",
              "victoza_18": "Victoza", "toujeo_solostar": "Toujeo", "repatha_140": "Repatha", "enbrel_50": "Enbrel",
              "trelegy_100": "Trelegy", "biktarvy": "Biktarvy", "nurtec_75": "Nurtec", "linzess_145": "Linzess"}

# The FDA shortage search uses the ingredient that names the product on FDA's list (default: the RxNorm term).
SHORTAGE_TERM = {"amox_clav_875": "amoxicillin", "amox_clav_susp_400": "amoxicillin", "advair_diskus_250": "fluticasone",
                 "symbicort_160": "budesonide", "trelegy_100": "fluticasone", "duoneb": "albuterol",
                 "insulin_nph_pen": "insulin", "truvada_prep": "emtricitabine"}

SCHEDULE_ORDER = ["CI", "CII", "CIII", "CIV", "CV"]


def get(client, path, **params):
    r = client.get(f"{RXNAV}{path}", params=params)
    r.raise_for_status()
    return r.json()


def concepts(client, term):
    d = get(client, "/drugs.json", name=term)
    out = []
    for g in (d.get("drugGroup", {}).get("conceptGroup") or []):
        for p in g.get("conceptProperties") or []:
            out.append({"rxcui": p["rxcui"], "name": p["name"], "tty": g["tty"]})
    return out


def related(client, rxcui, ttys):
    d = get(client, f"/rxcui/{rxcui}/related.json", tty=" ".join(ttys))
    out = []
    for g in d.get("relatedGroup", {}).get("conceptGroup") or []:
        for p in g.get("conceptProperties") or []:
            out.append({"rxcui": p["rxcui"], "name": p["name"], "tty": g["tty"]})
    return out


def ndcs(client, rxcui):
    d = get(client, f"/rxcui/{rxcui}/ndcs.json")
    return sorted(set((d.get("ndcGroup", {}).get("ndcList") or {}).get("ndc") or []))


def ndc11(ndc: str) -> str:
    a, b, c = ndc.split("-")
    return a.zfill(5) + b.zfill(4) + c.zfill(2)


def ndc_directory() -> tuple[dict, dict, str]:
    """openFDA NDC directory: DEA schedules indexed by RxCUI and by 11-digit package NDC."""
    raw = RAW / Path(NDC_DIRECTORY).name
    if "--download" in sys.argv or not raw.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        print(f"downloading {NDC_DIRECTORY}")
        with httpx.stream("GET", NDC_DIRECTORY, timeout=600, follow_redirects=True) as r, open(raw, "wb") as f:
            r.raise_for_status()
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
    z = zipfile.ZipFile(raw)
    data = json.loads(z.read(z.namelist()[0]))
    by_rxcui, by_ndc = defaultdict(list), {}
    for p in data["results"]:
        item = {"product_ndc": p.get("product_ndc"), "brand_name": p.get("brand_name"),
                "dea_schedule": p.get("dea_schedule") or "none"}
        for rx in (p.get("openfda") or {}).get("rxcui", []):
            by_rxcui[rx].append(item)
        for pk in p.get("packaging") or []:
            try:
                by_ndc[ndc11(pk["package_ndc"])] = item
            except (KeyError, ValueError):
                pass
    return by_rxcui, by_ndc, data["meta"].get("last_updated", "not found")


def dea_schedule(rxcuis, drug_ndcs, by_rxcui, by_ndc) -> dict:
    """Schedule from every NDC-directory product that matches the drug's RxCUIs or NDCs (strictest wins)."""
    products = {}
    for rx in rxcuis:
        for p in by_rxcui.get(rx, []):
            products[p["product_ndc"]] = p
    for n in drug_ndcs:
        if n in by_ndc:
            products[by_ndc[n]["product_ndc"]] = by_ndc[n]
    if not products:
        return {"schedule": "not found", "controlled": "not found", "products_matched": 0, "schedules_seen": {}}
    seen = defaultdict(int)
    for p in products.values():
        seen[p["dea_schedule"]] += 1
    scheduled = [s for s in SCHEDULE_ORDER if s in seen]
    sched = scheduled[0] if scheduled else None
    return {"schedule": f"C-{sched[1:]}" if sched else "not controlled", "controlled": bool(sched),
            "products_matched": len(products), "schedules_seen": dict(seen)}


def main():
    today = date.today().isoformat()
    by_rxcui, by_ndc, ndc_updated = ndc_directory()
    print(f"openFDA NDC directory last updated {ndc_updated}: {len(by_ndc)} packages")
    drugs, problems = [], []
    assert len({d[0] for d in DRUGS}) == len(DRUGS), "duplicate drug id"
    with httpx.Client(timeout=60) as c:
        cache = {}
        for did, display, group, term, pattern, strength, form, supply in DRUGS:
            if term not in cache:
                cache[term] = concepts(c, term)
            all_c = cache[term]
            generic = [dict(x) for x in all_c if x["tty"] in ("SCD", "GPCK") and re.search(pattern, x["name"], re.I)]
            if not generic:
                print(f"!! no RxNorm match for {did}", file=sys.stderr)
                problems.append(did)
                continue
            brands, brand_names, products = [], set(), []
            for g in generic:
                g["ndcs"] = ndcs(c, g["rxcui"])
                want_tty = "BPCK" if g["tty"] == "GPCK" else "SBD"
                for b in related(c, g["rxcui"], [want_tty]):
                    if b["tty"] != want_tty or b["rxcui"] in {x["rxcui"] for x in brands}:
                        continue
                    if did in BRAND_ONLY and not b["name"].endswith(f"[{BRAND_ONLY[did]}]"):
                        continue
                    b["ndcs"] = ndcs(c, b["rxcui"])
                    brands.append(b)
                    m = re.search(r"\[([^\]]+)\]\s*$", b["name"])
                    if m:
                        brand_names.add(m.group(1))
                ing = related(c, g["rxcui"], ["IN", "MIN"])
                products.extend(i["name"] for i in ing)
            all_ndcs = sorted({n for x in generic + brands for n in x["ndcs"]})
            rxcuis = [x["rxcui"] for x in generic + brands]
            dea = dea_schedule(rxcuis, all_ndcs, by_rxcui, by_ndc)
            drugs.append({
                "id": did,
                "display_name": display,
                "category": group,
                "generic_name": " / ".join(sorted(set(products))) or "not found",
                "brand_names": sorted(brand_names) or "not found",
                "strength": strength,
                "dosage_form": form,
                # A drug whose schedule could not be found is treated as controlled (the safer choice) and listed
                # in medication_check.md for pharmacist review.
                "controlled": dea["controlled"] is not False,
                "dea_schedule": dea["schedule"],
                "dea_schedule_check": {"products_matched": dea["products_matched"], "schedules_seen": dea["schedules_seen"]},
                "rxnorm_generic": [{k: g[k] for k in ("rxcui", "tty", "name")} | {"ndc_count": len(g["ndcs"])} for g in generic],
                "rxnorm_brand": [{k: b[k] for k in ("rxcui", "tty", "name")} | {"ndc_count": len(b["ndcs"])} for b in brands],
                "rxcuis": rxcuis,
                "ndcs": all_ndcs,
                "typical_30_day_supply": supply,
                "shortage_search": SHORTAGE_TERM.get(did, term),
                "sources": {
                    "rxnorm": f"{RXNAV}/drugs.json?name={term.replace(' ', '+')}",
                    "ndcs": f"{RXNAV}/rxcui/<rxcui>/ndcs.json (one call per RxCUI listed)",
                    "brand_names": f"{RXNAV}/rxcui/<generic rxcui>/related.json?tty=SBD+BPCK",
                    "dea_schedule": f"openFDA NDC directory ({NDC_DIRECTORY_PAGE}), last updated {ndc_updated}; "
                                    "matched by RxCUI and package NDC",
                    "typical_30_day_supply": "RxLantern assumption for cost estimates only (not a dosing instruction)",
                },
                "checked_date": today,
            })
            print(f"{did:28} rx={len(rxcuis):2} ndcs={len(all_ndcs):4} dea={dea['schedule']:15} brands={sorted(brand_names)[:4]}")
    if problems:
        print("NOT MATCHED:", problems)
    OUT.write_text(json.dumps({"checked_date": today, "source": "RxNorm / RxNav API, U.S. National Library of Medicine",
                               "list_source": LIST_SOURCE,
                               "dea_schedule_source": {"name": "openFDA NDC directory", "url": NDC_DIRECTORY_PAGE,
                                                       "file": NDC_DIRECTORY, "last_updated": ndc_updated},
                               "count": len(drugs), "drugs": drugs}, indent=1), encoding="utf-8")
    print(f"wrote {OUT} ({len(drugs)} drugs)")


if __name__ == "__main__":
    main()
