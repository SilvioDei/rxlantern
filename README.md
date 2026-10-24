# RxLantern

RxLantern helps a Boston patient find, before leaving the doctor's office, which pharmacy can fill a prescription, whether
it is open, whether it may take their insurance, and roughly what it will cost. Patients help each other by sharing what
they found when they called, and an AI pharmacist chat (gpt-6-luna through Portkey) answers questions in plain English or
Spanish.

## Requirements

- **Python 3.11, 3.12, 3.13, or 3.14** (tested on all four on 2026-10-24). Python 3.10 or older will not work.
- About 200 MB of disk space for the virtual environment. **No Node.js** (the website is already built in
  `frontend/dist`).
- A **Portkey API key**. It is the only key RxLantern needs. `OPENAI_API_KEY` is not used.

## Setup (about 3 minutes)

The `.env` file goes **one folder above** this repository (or inside it). For example:

```
submissions/
├── .env                 <- PORTKEY_API_KEY=...   (one folder above the repo)
└── rxlantern/           <- this repository (any folder name works)
    ├── run.py
    └── README.md
```

### Windows (PowerShell or Command Prompt)

```bash
git clone <this repository's URL>
```

```bash
cd <the cloned folder>
```

```bash
python -m venv .venv
```

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```bash
.venv\Scripts\python.exe run.py
```

If `python` is not found or is older than 3.11, use the Python launcher instead, for example `py -3.12 -m venv .venv`.
You do not need to "activate" the virtual environment.

### Mac / Linux

```bash
git clone <this repository's URL>
```

```bash
cd <the cloned folder>
```

```bash
python3 -m venv .venv
```

```bash
.venv/bin/python -m pip install -r requirements.txt
```

```bash
.venv/bin/python run.py
```

### Open the app

Open **http://127.0.0.1:8000** in a browser. The first start builds the local database from the files in `data/`
(a few seconds). The terminal shows where the key was loaded from, for example
`PORTKEY_API_KEY loaded from ...\.env`. Press Ctrl+C to stop.

## Settings (`.env`)

See `.env.example`. Only the first one is needed.

| Setting | Needed? | What it does |
|---|---|---|
| `PORTKEY_API_KEY` | **Required for the chat** | Your Portkey key. Every page except the "Ask RxLantern" chat works without it. |
| `RXLANTERN_ADMIN_EMAILS` | Optional | Comma-separated emails that can approve or reject comments in the Admin moderation queue. Empty = no admins (nothing breaks). |
| `RXLANTERN_SHOW_SAMPLE_DATA` | Optional (default `1`) | Shows a few demonstration stock reports, reviews, and search counts so you can see the community features on an empty database. They always carry a **Sample** badge, are never saved, and are never counted with real posts. Set `0` to hide them. |
| `RXLANTERN_PORT` | Optional (default `8000`) | Use another port if 8000 is busy. |

`.env` is read from this folder first, then from the folder one level above. A variable already set in your system
environment wins over both.

## Troubleshooting

- **"RxLantern needs Python 3.11 or newer"**: create the virtual environment with a newer Python (see above), delete the
  old `.venv` folder first.
- **The chat says "The chat is not set up yet"**: the `PORTKEY_API_KEY` was not found or Portkey did not accept it.
  Check the `.env` file is one folder above (or inside) the repository and the key is current. All other pages work.
- **"Address already in use" / port 8000 busy**: add `RXLANTERN_PORT=8001` to `.env` and open http://127.0.0.1:8001.
- **`pip install` fails**: update pip first (`.venv\Scripts\python.exe -m pip install --upgrade pip`, or
  `.venv/bin/python -m pip install --upgrade pip`), then install again.
- **Shortage data shows yesterday's date**: FDA shortage data refreshes in the background at most once a day; the saved
  copy in `data/` is used until then. No action needed.

## What is on the site

- **Find my medicine** (home): a "What medicine do you need?" search bar, then a 3-step guided search (150 medicines by
  brand or generic name, small spelling mistakes OK; ZIP, neighborhood, or "Use my location"; insurance), and the chat.
  A medicine not in the list gets its live FDA shortage status and a call script.
- **Results**: nearby pharmacies with a map, open hours (pharmacy counter first), FDA shortage status, coverage and
  cost estimates for the chosen insurance, the plan's pharmacy finder and phone number, community stock reports
  (last 72 hours), reviews, a prior authorization helper, a savings finder (links to GoodRx, TrumpRx.gov, and the
  maker's program; never prices), a "Before you go" checklist, "Send it here" cards for the doctor, call scripts, and
  "I called: They have it / They don't" buttons (with a transfer helper).
- **My medicine list**, **Pharmacies** (with best time to go and languages reported by patients), **Shortage watch**
  (with a watchlist), **Vaccines**, **Community**, **About & Privacy**, **Language help card**, **For pharmacies**
  (anonymous search counts), and an **Admin** moderation queue.
- Voice input and read aloud, Easy view (large text, high contrast), English / Español, keyboard navigation, phone
  layout.

## Safety rules in code

No health information is stored (accounts hold only an email, a nickname, and a hashed password; "Delete my account"
removes everything). No stock reports for controlled medicines (DEA schedule from the FDA's NDC directory: 18 of the
150). No medical advice. Emergencies ("I took too many pills", "no puedo respirar") get 911 and Poison Control
(1-800-222-1222) at once, before any AI call. Requests for the system prompt or other users' data are declined in code.
Spending limits per question, per day, and per visitor. Costs are always labeled as estimates. The 16 safety tests and
their screenshots are in `output/safety_report.html` (open it by double-clicking).

## Data sources

Pharmacies' own websites; the ClinCalc DrugStats "Top 300 of 2024" list (AHRQ MEPS data) for choosing the 150 medicines;
RxNorm; the openFDA NDC directory and drug shortages; NADAC; the MassHealth Drug List (checked 2026-10-24); CMS Medicare
Part D 2026 files; CDC, CMS, and Mass.gov vaccine rules; each insurance plan's own website; Census ZIP centers; GoodRx's
sitemap, TrumpRx.gov's medication list, and each brand's own website for savings links. Every fact shows its source and
the date it was checked (see About & Privacy). Rebuild scripts are in `scripts/` (for example
`scripts/fetch_masshealth.py` refreshes the MassHealth data in one command).

## Tests (optional, for developers)

Install the test tools with `pip install -r requirements-dev.txt` and `python -m playwright install chromium`, start the
app, then run `tests/ui_step7b.py`, `tests/ui_step7c.py`, `tests/ui_step7c2.py` (website checks in a real browser),
`tests/safety_tests.py` (16 safety tests), and `tests/try_agents.py` + `tests/check_agent_rules.py` (the agent test
questions; these use the AI model). Results are saved in `output/`.
