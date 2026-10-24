# RxLantern

Before leaving the doctor's office, a Boston patient finds which pharmacy can fill their prescription, whether it is
open, whether it may take their insurance, and roughly what it will cost. Patients help each other by reporting what
they found when they called.

## Start the app (Python only)

From the `rxcompass/` folder, with the `.venv` one level above:

```
..\.venv\Scripts\python.exe run.py
```

Open http://127.0.0.1:8000. The website is already built in `frontend/dist`, so Node.js is not needed.
Put `PORTKEY_API_KEY=...` in a `.env` file in `rxcompass/` or one folder above it. Only the chat uses the AI model
(gpt-6-luna through Portkey); every other page loads from the database.

## What is on the site

- **Find my medicine** (home): a compact "What medicine do you need?" search bar at the top, "How it works", then a
  3-step guided search: medicine (150 medicines; brand or generic names, suggestions as you type, small spelling
  mistakes OK, then strength/form), place (ZIP, neighborhood, or "Use my location"), and insurance (MassHealth,
  Medicare, a work/private plan from a list, or none). Below it: "Or ask RxLantern anything" (the chat).
- **A medicine not in the list**: its FDA shortage status is checked live (openFDA) with a call script; coverage and
  cost details are only available for the medicines in RxLantern's list.
- **Results**: nearby pharmacies with a map; sort by distance, open now, open latest, rating, or shortest wait;
  filter by open now, delivery, and language. FDA shortage status (and FDA's estimate, if given),
  coverage and cost estimates for the chosen insurance, the plan's official pharmacy finder and member services
  number, holiday notices, community stock reports (last 72 hours), reviews, and buttons to call (with a script),
  get directions, report "They have it / They don't", and rate the pharmacy. "Print / share for my doctor" makes a
  printable summary with no personal information.
- **My medicine list**: add 2 to 5 medicines and see nearby pharmacies ranked by how likely they are to fill all of
  them ("Reported in stock for 2 of 3 of your medicines"; always call to confirm). Saved only in your browser.
- On the results page: a **prior authorization helper** when coverage needs PA, a **savings finder** (links to GoodRx,
  TrumpRx.gov, and the maker's savings program; never prices; note only for Medicare and MassHealth), a **Before you
  go** checklist, a star to **watch** a medicine, and **Send it here** cards to show your doctor. After "They don't
  have it", a **transfer helper** script.
- Pharmacy pages: **Best time to go** (typical wait by day and time, from 3+ reviews) and **languages reported by
  patients** ("Staff spoke my language" in reviews), also used by the language filter.
- **Language help card** (Chinese, Haitian Creole, Spanish, English) and a **For pharmacies** page with anonymous
  search counts (5 or more only). A **time-saved** estimate is on the home and About pages.
- **Pharmacies**, **Shortage watch** (all 150 medicines), **Vaccines**, **Community** (search by medicine, pharmacy,
  or neighborhood; sort by newest or rating), **About & Privacy**, and an **Admin** moderation queue (admins only).
- Voice input (🎤 Speak) and Read aloud for everyone, Easy view (large text, high contrast, big buttons),
  English / Español, keyboard navigation, phone layout.

## Safety rules in code

No health information is stored (accounts hold only an email, a nickname, and a hashed password; "Delete my account"
removes the account and all its posts). No stock reports for controlled medicines (any DEA schedule, from the FDA's
NDC directory: 18 of the 150). No medical advice. Emergencies
("I took too many pills", "no puedo respirar", ...) get 911 and Poison Control (1-800-222-1222) at once, before any AI
call, and are logged in `output/audit_trail.json`. Costs are always labeled as estimates, never as a copay.

## Sample data

Graders start with an empty user database, so a few sample stock reports and reviews are shown when
`SHOW_SAMPLE_DATA = True` in `backend/config.py` (the default; `RXLANTERN_SHOW_SAMPLE_DATA=0` turns it off). They are
never saved to the database, never counted with real posts, always carry a "Sample" badge, and are dated relative to
today.

## Data sources

Pharmacies' own websites, the ClinCalc DrugStats "Top 300 of 2024" list (AHRQ MEPS data) for choosing the 150
medicines, RxNorm, the openFDA NDC directory (DEA schedules), openFDA drug shortages (refreshed in the background at
most once a day), NADAC, the MassHealth Drug List, CMS Medicare Part D files, CDC / CMS / Mass.gov vaccine rules, each insurance plan's own
website (`data/insurance_plans.json`), Census ZIP centers, and for savings links: GoodRx's sitemap, TrumpRx.gov's
medication list, and each brand's own website (`data/savings.json`, rebuilt by `scripts/build_savings.py`). Every fact shows its source and the date it was checked;
see the About & Privacy page.

## MassHealth data

MassHealth coverage for all 150 medicines comes from the MassHealth Drug List website (checked 2026-10-24; the
site was down overnight, so this step ran late) (cross-checked with the October 2026 MassHealth Drug List PDF). If the
site is ever down again, new medicines show "MassHealth coverage not checked yet. Call the pharmacy or MassHealth to
confirm." To refresh MassHealth data, from `rxcompass/` run:

```
..\.venv\Scripts\python.exe scripts\fetch_masshealth.py
```

then restart the app.

## Tests

`tests/ui_step7b.py`, `tests/ui_step7c.py`, and `tests/ui_step7c2.py` check the whole site in a real browser (Playwright) while the app
runs. Results are in `output/ui_test_results.json`, `output/ui_test_results_7c.json`, and
`output/ui_test_results_7c2.json`, screenshots in
`output/screenshots/`. `tests/try_agents.py` runs the agent test questions (uses the AI model) and
`tests/check_agent_rules.py` checks the answers against the rules. The medication data check for pharmacists is
`output/medication_check.md`.
