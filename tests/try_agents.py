"""Run the Step 4 test questions through the full agent team and save the results.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m tests.try_agents [question numbers...]
Calls gpt-6-luna through Portkey. Results go to output/agent_test_runs.json.
"""

import asyncio
import json
import sys
import time

from fastapi.testclient import TestClient

from backend.config import APP_NAME, MODEL_NAME, OUTPUT_DIR
from backend.main import app

QUESTIONS = [
    {"n": 1, "question": "Is there a pharmacy open right now near 02111?", "language": "en"},
    {"n": 2, "question": "Is Concerta 18 mg in shortage? Which pharmacy has it?", "language": "en"},
    {"n": 3, "question": "How much will Eliquis 5 mg cost me with Medicare?", "language": "en"},
    {"n": 4, "question": "Does MassHealth cover Ozempic?", "language": "en"},
    {"n": 5, "question": "Where can I get a flu shot in Chinatown, and does Blue Cross cover it?", "language": "en"},
    {"n": 6, "question": "My sumatriptan didn't work. Should I take two?", "language": "en"},
    {"n": 7, "question": "¿Qué farmacia en East Boston tiene entrega a domicilio?", "language": "es"},
    {"n": 8, "question": "Will my kid's amoxicillin liquid be covered? We have Blue Cross Blue Shield.", "language": "en"},
    {"n": 9, "question": "Is the CVS at South Station open on weekends?", "language": "en"},
    {"n": 10, "question": "How close is an urgent care or clinic to the hospital?", "language": "en"},
    {"n": 11, "question": "Is there a walk-in clinic near the CVS in Mattapan?", "language": "en"},
    # Step 7c: a medicine outside RxLantern's list, and a newly added Schedule II medicine.
    {"n": 12, "question": "Is methotrexate in shortage right now?", "language": "en"},
    {"n": 13, "question": "Which pharmacy near 02115 has Vyvanse 30 mg in stock?", "language": "en"},
]


def main() -> None:
    pick = {int(a) for a in sys.argv[1:]} or {q["n"] for q in QUESTIONS}
    out_path = OUTPUT_DIR / "agent_test_runs.json"
    old = {r["n"]: r for r in json.loads(out_path.read_text(encoding="utf-8"))["runs"]} if out_path.exists() else {}
    runs = dict(old)
    with TestClient(app) as client:
        for q in QUESTIONS:
            if q["n"] not in pick:
                continue
            t0 = time.time()
            r = client.post("/api/ask", json={"question": q["question"], "language": q["language"]})
            body = r.json()
            if r.status_code != 200:
                runs[q["n"]] = q | {"status_code": r.status_code, "error": body}
                print(f"Q{q['n']}: HTTP {r.status_code} {body}")
                continue
            u = body["usage"]
            runs[q["n"]] = q | {
                "run_id": body["run_id"], "stop_reason": body["stop_reason"],
                "seconds": round(time.time() - t0, 1),
                "reply": body["reply_text"], "follow_up_question": body["follow_up_question"],
                "call_script": body["call_script"], "pharmacy_cards": body["pharmacy_cards"],
                "sources": body["sources"], "agents_run": body["agents_run"], "tools_run": body["tools_run"],
                "safety": body["safety"],
                "tokens": {"input": u["input_tokens"], "cached_input": u["cached_input_tokens"],
                           "output": u["output_tokens"], "model_requests": u["requests"], "tool_calls": u["tool_calls"]},
                "cost_usd": u["cost_usd"], "usage_display": u["display"],
            }
            print(f"Q{q['n']}: {body['agents_run']} | in={u['input_tokens']} cached={u['cached_input_tokens']} "
                  f"out={u['output_tokens']} | {runs[q['n']]['seconds']}s")
    out_path.write_text(json.dumps({"app": APP_NAME, "model": MODEL_NAME,
                                    "runs": [runs[k] for k in sorted(runs)]}, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
