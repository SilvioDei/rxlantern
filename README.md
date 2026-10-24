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

- **Find my medicine** (home): "How it works", then a 3-step guided search: medicine (suggestions as you type,
  small spelling mistakes OK, then strength/form), place (ZIP, neighborhood, or "Use my location"), and insurance
  (MassHealth, Medicare, a work/private plan from a list, or none). Below it: "Or ask RxLantern anything" (the chat).
- **Results**: nearby pharmacies with a map; sort by distance, open now, open latest, rating, or shortest wait;
  filter by open now, delivery, language, wheelchair access. FDA shortage status (and FDA's estimate, if given),
  coverage and cost estimates for the chosen insurance, the plan's official pharmacy finder and member services
  number, holiday notices, community stock reports (last 72 hours), reviews, and buttons to call (with a script),
  get directions, report "They have it / They don't", and rate the pharmacy. "Print / share for my doctor" makes a
  printable summary with no personal information.
- **Pharmacies**, **Shortage watch**, **Vaccines**, **Community**, **About & Privacy**, and an **Admin** moderation
  queue (admins only).
- Easy view (large text, high contrast, read aloud, voice input), English / Español, keyboard navigation, phone layout.

## Safety rules in code

No health information is stored (accounts hold only an email, a nickname, and a hashed password; "Delete my account"
removes the account and all its posts). No stock reports for controlled medicines. No medical advice. Emergencies
("I took too many pills", "no puedo respirar", ...) get 911 and Poison Control (1-800-222-1222) at once, before any AI
call, and are logged in `output/audit_trail.json`. Costs are always labeled as estimates, never as a copay.

## Sample data

Graders start with an empty user database, so a few sample stock reports and reviews are shown when
`SHOW_SAMPLE_DATA = True` in `backend/config.py` (the default; `RXLANTERN_SHOW_SAMPLE_DATA=0` turns it off). They are
never saved to the database, never counted with real posts, always carry a "Sample" badge, and are dated relative to
today.

## Data sources

Pharmacies' own websites, RxNorm, openFDA drug shortages (refreshed in the background at most once a day), NADAC,
the MassHealth Drug List, CMS Medicare Part D files, CDC / CMS / Mass.gov vaccine rules, each insurance plan's own
website (`data/insurance_plans.json`), and Census ZIP centers. Every fact shows its source and the date it was checked;
see the About & Privacy page.

## Tests

`tests/ui_step7b.py` checks the whole site in a real browser (Playwright) while the app runs. Results are in
`output/ui_test_results.json` and screenshots in `output/screenshots/`.
