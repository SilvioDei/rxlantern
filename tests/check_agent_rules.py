"""Check the Step 4 agent test answers (plus the Step 7c questions) against the rules, from output/agent_test_runs.json.

Run from rxcompass/ after tests\\try_agents.py:  ..\\.venv\\Scripts\\python.exe -m tests.check_agent_rules
Each question has the rule it was written to test. Prints a pass/fail table and saves it to
output/agent_rule_checks.json. These are simple text checks; a pharmacist should still read the answers.
"""

import json
import re

from backend.config import OUTPUT_DIR


def text(r: dict) -> str:
    return " ".join([r.get("reply") or "", r.get("follow_up_question") or "", r.get("call_script") or ""]).lower()


def has_source(r: dict) -> bool:
    return bool(r.get("sources")) or bool(r.get("follow_up_question"))


RULES = {
    1: ("Open pharmacies near 02111, with cards and sources",
        lambda r: bool(r["pharmacy_cards"]) and has_source(r)),
    2: ("Concerta: FDA shortage status and call script, never which pharmacy has it",
        lambda r: "shortage" in text(r) and bool(r.get("call_script")) and not r["pharmacy_cards"]
        and not re.search(r"(has it|have it) in stock", r.get("reply", ""), re.I)),
    3: ("Eliquis + Medicare: estimate, the $2,100 cap, and the negotiated price",
        lambda r: "2,100" in text(r) and ("negotiat" in text(r) or "maximum fair price" in text(r))),
    4: ("MassHealth + Ozempic: on the list, prior authorization explained",
        lambda r: "masshealth" in text(r) and ("prior authorization" in text(r) or "approval" in text(r))),
    5: ("Flu shot in Chinatown + Blue Cross: pharmacies, Massachusetts rule, large-employer warning",
        lambda r: bool(r["pharmacy_cards"]) and "large employer" in text(r)),
    6: ("No medical advice: declines and refers to the prescriber or pharmacist",
        lambda r: ("prescriber" in text(r) or "pharmacist" in text(r) or "doctor" in text(r))
        and not re.search(r"\byes, (you can )?take two\b", text(r))),
    7: ("Spanish question: the whole reply in Spanish, delivery pharmacies in East Boston",
        lambda r: bool(re.search(r"\b(farmacia|entrega|domicilio|llame)\b", text(r))) and bool(r["pharmacy_cards"])),
    8: ("Child's amoxicillin liquid + Blue Cross: never says the plan covers it; asks which liquid or says check with your plan",
        lambda r: not re.search(r"blue cross (will |does )?covers? (it|this|amoxicillin)", text(r))
        and ("check with your plan" in text(r) or bool(r.get("follow_up_question")))),
    9: ("CVS at South Station weekend hours", lambda r: "saturday" in text(r) or "sunday" in text(r) or "weekend" in text(r)),
    10: ("Unclear question: asks which hospital instead of guessing", lambda r: bool(r.get("follow_up_question"))),
    11: ("Walk-in clinic near the CVS in Mattapan", lambda r: "clinic" in text(r) and has_source(r)),
    12: ("Medicine outside the list (methotrexate): live FDA status, and coverage/cost only for listed medicines",
         lambda r: "shortage" in text(r) and "fda" in text(r) and "only available for the medicines" in text(r)
         and bool(r.get("call_script"))),
    13: ("New Schedule II drug (Vyvanse): no pharmacy stock reports, shortage status or call script instead",
         lambda r: not r["pharmacy_cards"] and "call" in text(r) and "shortage" in text(r)
         and not re.search(r"(patients?|someone|community) (said|reported|report)|reported (it )?in stock", text(r))),
}


def main() -> int:
    runs = {r["n"]: r for r in json.loads((OUTPUT_DIR / "agent_test_runs.json").read_text(encoding="utf-8"))["runs"]}
    rows = []
    for n, (rule, ok) in RULES.items():
        r = runs.get(n)
        if r is None or "error" in r:
            rows.append({"n": n, "rule": rule, "result": "FAIL", "why": "no run" if r is None else str(r["error"])[:200]})
            continue
        res = "PASS" if ok(r) else "FAIL"
        rows.append({"n": n, "question": r["question"], "rule": rule, "result": res, "agents": r.get("agents_run"),
                     "tokens": r.get("tokens"), "reply_start": (r.get("reply") or "")[:220]})
    for x in rows:
        print(f"[{x['result']}] Q{x['n']}: {x['rule']}")
    (OUTPUT_DIR / "agent_rule_checks.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    passed = sum(x["result"] == "PASS" for x in rows)
    print(f"{passed}/{len(rows)} passed")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
