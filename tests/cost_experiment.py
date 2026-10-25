"""Did cost-cutting hurt quality? Run the 11 Step 4 questions in two modes and compare.

  A. normal: the Front Desk calls only the specialist(s) it needs (what RxLantern does).
  B. ask_everyone: the Front Desk is told to call all three specialists on every question.

The code-level safety rules (medical advice, unclear hospital) stay on in both modes: safety is never turned off.
Each answer is checked automatically for the rule and the key fact that question needs.
Run from the repository folder:  ..\\.venv\\Scripts\\python.exe -m tests.cost_experiment
Results: output/cost_experiment.json
"""

import asyncio
import json
import re
import statistics

from backend import config
from backend.agents import ask
from tests.try_agents import QUESTIONS

SPECIALISTS = {"Pharmacy Finder", "Medication Access", "Community"}


def first_sentence(text: str) -> str:
    return re.split(r"(?<=[.!?])\s+", text.strip())[0].lower()


# What a correct, rule-following answer must contain, per question.
CHECKS = {
    1: ("a pharmacy counter that is open now is shown, or (when none is open) the next opening time and nearest option",
        lambda r: any(c.open_now for c in r.pharmacy_cards) or (
            (bool(r.pharmacy_cards) or re.search(r"\b\d+ [A-Z][\w. ]*?\b(St|Ave|Blvd|Street|Avenue|Boulevard)\b", r.reply_text))
            and re.search(r"\bopens?\b", r.reply_text, re.I) is not None
            and re.search(r"\d{1,2}(:\d{2})?\s*(AM|PM)", r.reply_text, re.I) is not None)),
    2: ("says Concerta is in shortage, names no pharmacy (controlled), gives a call script",
        lambda r: "shortage" in r.reply_text.lower() and not r.pharmacy_cards and bool(r.call_script)),
    3: ("gives a Medicare estimate, the $2,100 cap, and Eliquis's negotiated price",
        lambda r: "$" in r.reply_text and "2,100" in r.reply_text and "negotiated" in r.reply_text.lower()),
    4: ("says MassHealth covers it with prior authorization",
        lambda r: re.search(r"prior authori|approv", r.reply_text, re.I) is not None),
    5: ("shows the Chinatown CVS that lists flu shots and the large-employer warning",
        lambda r: any("631 Washington" in c.address for c in r.pharmacy_cards) and "employer" in r.reply_text.lower()),
    6: ("declines medical advice", lambda r: r.stop_reason == "medical advice declined"),
    7: ("answers in Spanish with the East Boston CVS that delivers",
        lambda r: re.search(r"\b(farmacia|entrega|domicilio|llame)\b", r.reply_text, re.I) is not None
        and any("210 Border" in c.address for c in r.pharmacy_cards)),
    8: ("no coverage claim for Blue Cross; NADAC label and 'check with your plan'",
        lambda r: "check with your plan" in r.reply_text.lower() and "not your copay" in r.reply_text.lower()
        and not re.search(r"\b(is|will be|are) covered\b", r.reply_text.lower())),
    9: ("pharmacy counter first (closed on weekends), store hours after",
        lambda r: "counter" in first_sentence(r.reply_text) and "closed" in first_sentence(r.reply_text)),
    10: ("asks which hospital instead of guessing", lambda r: bool(r.follow_up_question) and not r.tools_run),
    11: ("names Mattapan Community Health Center near the CVS",
         lambda r: "mattapan community health center" in r.reply_text.lower()),
}
NEVER = [(re.compile(r"definitely (in stock|has it|have it)", re.I), "said a drug is definitely in stock")]


def grade(n: int, r) -> dict:
    desc, fn = CHECKS[n]
    broken = [msg for pat, msg in NEVER if pat.search(r.reply_text)]
    passed = bool(fn(r)) and not broken and r.stop_reason in ("completed", "medical advice declined",
                                                               "follow-up asked (unclear question)")
    return {"check": desc, "passed": passed, "rules_broken": broken}


async def run_mode(ask_everyone: bool) -> list[dict]:
    rows = []
    for q in [q for q in QUESTIONS if q["n"] in CHECKS]:  # the 11 Step 4 questions (try_agents now has 13)
        r = await ask(q["question"], q["language"], ask_everyone=ask_everyone)
        g = grade(q["n"], r)
        called = sorted(SPECIALISTS & set(r.agents_run))
        rows.append({"n": q["n"], "question": q["question"], "mode": "ask_everyone" if ask_everyone else "normal",
                     "run_id": r.run_id, "specialists_called": called, "tools_run": len(r.tools_run),
                     "tokens": {"input": r.usage.input_tokens, "cached_input": r.usage.cached_input_tokens,
                                "output": r.usage.output_tokens, "total": r.usage.total_tokens},
                     "model_requests": r.usage.requests, "cost_usd": r.usage.cost_usd,
                     "stop_reason": r.stop_reason, **g, "reply": r.reply_text})
        print(f"{rows[-1]['mode']:12} Q{q['n']:<2} specialists={len(called)} tokens={r.usage.total_tokens:6} "
              f"cost={r.usage.cost_usd} passed={g['passed']}")
    return rows


async def main_async() -> dict:
    normal = await run_mode(False)
    everyone = await run_mode(True)
    return {"normal": normal, "ask_everyone": everyone}


def summary(rows: list[dict]) -> dict:
    model_rows = [r for r in rows if r["tokens"]["total"] > 0]
    costs = [r["cost_usd"] for r in rows if r["cost_usd"] is not None]
    return {"questions": len(rows), "passed": sum(r["passed"] for r in rows),
            "total_tokens": sum(r["tokens"]["total"] for r in rows),
            "avg_tokens_per_question": round(statistics.mean(r["tokens"]["total"] for r in rows)),
            "avg_tokens_per_model_answered_question": round(statistics.mean(r["tokens"]["total"] for r in model_rows)),
            "total_cost_usd": round(sum(costs), 6), "avg_cost_usd": round(statistics.mean(costs), 6),
            "avg_specialists_called": round(statistics.mean(len(r["specialists_called"]) for r in rows), 2)}


def main() -> None:
    data = asyncio.run(main_async())
    result = {"model": config.MODEL_NAME, "prices_usd_per_million": config.PRICES_USD_PER_MILLION,
              "price_source": config.PRICE_SOURCE,
              "note": "Code-level safety rules (Q6 medical advice, Q10 unclear hospital) stay on in both modes.",
              "summary": {"normal": summary(data["normal"]), "ask_everyone": summary(data["ask_everyone"])},
              "runs": data}
    out = config.OUTPUT_DIR / "cost_experiment.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
