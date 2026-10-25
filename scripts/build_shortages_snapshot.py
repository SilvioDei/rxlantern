"""Save FDA shortage status for all 150 drugs to data/shortages_snapshot.json (offline fallback).

Run from the repository folder:  ..\\.venv\\Scripts\\python.exe scripts\\build_shortages_snapshot.py
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.tools import OPENFDA_SHORTAGES, SHORTAGE_PAGE, fetch_fda_shortage  # noqa: E402

drugs = json.loads((ROOT / "data" / "drugs.json").read_text(encoding="utf-8"))["drugs"]
results = []
with httpx.Client(timeout=30) as client:
    for d in drugs:
        r = fetch_fda_shortage(d, client)
        results.append(r)
        time.sleep(0.6)  # stay well under openFDA's 240 requests per minute without a key
        print(f"{d['id']:22} {r['status']:45} entries={len(r['matching_entries'])}")

out = ROOT / "data" / "shortages_snapshot.json"
out.write_text(json.dumps({"checked_date": date.today().isoformat(), "api": OPENFDA_SHORTAGES,
                           "source": SHORTAGE_PAGE, "drugs": results}, indent=2), encoding="utf-8")
print(f"wrote {out}")
