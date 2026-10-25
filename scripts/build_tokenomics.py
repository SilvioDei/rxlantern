"""Write output/tokenomics.md from the real runs in output/cost_experiment.json.

Run from the repository folder:  ..\\.venv\\Scripts\\python.exe scripts\\build_tokenomics.py
"""

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend import config  # noqa: E402

QUESTIONS_PER_PATIENT_PER_MONTH = 4  # chosen by the project owner
USERS = (1, 100, 10_000)


def money(x: float, digits: int = 4) -> str:
    return f"${x:,.{digits}f}"


def main() -> None:
    exp = json.loads((ROOT / "output" / "cost_experiment.json").read_text(encoding="utf-8"))
    p = config.PRICES_USD_PER_MILLION
    normal, everyone = exp["runs"]["normal"], exp["runs"]["ask_everyone"]
    n = len(normal)
    model_rows = [r for r in normal if r["tokens"]["total"] > 0]
    zero_rows = [r for r in normal if r["tokens"]["total"] == 0]

    avg = {k: statistics.mean(r["tokens"][k] for r in normal) for k in ("input", "cached_input", "output", "total")}
    avg_m = {k: statistics.mean(r["tokens"][k] for r in model_rows) for k in ("input", "cached_input", "output", "total")}
    avg_cost = statistics.mean(r["cost_usd"] for r in normal)
    avg_cost_m = statistics.mean(r["cost_usd"] for r in model_rows)

    tot_in = sum(r["tokens"]["input"] for r in normal)
    tot_cached = sum(r["tokens"]["cached_input"] for r in normal)
    saved_cache = tot_cached * (p["input"] - p["cached_input"]) / 1_000_000
    cost_no_cache = sum(r["cost_usd"] for r in normal) + saved_cache
    cost_with = sum(r["cost_usd"] for r in normal)

    saved_rules_tokens = len(zero_rows) * avg_m["total"]
    saved_rules_cost = len(zero_rows) * avg_cost_m

    s_n, s_e = exp["summary"]["normal"], exp["summary"]["ask_everyone"]
    per_user = QUESTIONS_PER_PATIENT_PER_MONTH * avg_cost
    per_user_e = QUESTIONS_PER_PATIENT_PER_MONTH * s_e["avg_cost_usd"]

    L = []
    w = L.append
    w(f"# {config.APP_NAME} tokenomics\n")
    w(f"Model: **{config.MODEL_NAME}** through Portkey. Prices (US dollars per 1 million tokens): input "
      f"**${p['input']:.2f}**, cached input **${p['cached_input']:.2f}**, output **${p['output']:.2f}**; web search "
      f"**${config.WEB_SEARCH_USD_PER_CALL:.2f} per search**. Source: {config.PRICE_SOURCE} (Portkey lists cents per "
      "token; converted to dollars per 1M and confirmed with the project owner).\n")
    w(f"Data: the {n} Step 4 test questions run once in normal mode and once in \"ask everyone\" mode "
      "(`tests/cost_experiment.py`, raw results in `output/cost_experiment.json`). Cost per question = "
      "(input - cached input) x input price + cached input x cached price + output x output price.\n")

    w("## 1. Average tokens and cost per question (normal mode)\n")
    w("| | Input | Cached input | Output | Total (input + output) | Cost |")
    w("|---|---:|---:|---:|---:|---:|")
    w(f"| All {n} questions | {avg['input']:,.0f} | {avg['cached_input']:,.0f} | {avg['output']:,.0f} | "
      f"{avg['total']:,.0f} | {money(avg_cost, 6)} |")
    w(f"| {len(model_rows)} questions the model answered | {avg_m['input']:,.0f} | {avg_m['cached_input']:,.0f} | "
      f"{avg_m['output']:,.0f} | {avg_m['total']:,.0f} | {money(avg_cost_m, 6)} |\n")
    w("Cached input tokens are part of the input count (OpenAI counts them inside input). Output tokens cost 5x input, "
      f"so output is {sum(r['tokens']['output'] for r in normal) * p['output'] / 1e6 / cost_with:.0%} of the cost "
      f"while being {sum(r['tokens']['output'] for r in normal) / sum(r['tokens']['total'] for r in normal):.0%} of the tokens.\n")

    w("## 2. What prompt caching saved\n")
    w(f"- Input tokens: {tot_in:,}. Of these, {tot_cached:,} ({tot_cached / tot_in:.0%}) were read from OpenAI's prompt cache.")
    w(f"- Cached tokens cost ${p['cached_input']:.2f} per 1M instead of ${p['input']:.2f}: a 90% discount.")
    w(f"- Saved: {tot_cached:,} x (${p['input']:.2f} - ${p['cached_input']:.2f}) / 1,000,000 = **{money(saved_cache, 6)}** "
      f"on these {n} questions.")
    w(f"- Cost with caching {money(cost_with, 6)} vs. {money(cost_no_cache, 6)} without: "
      f"**{saved_cache / cost_no_cache:.0%} cheaper**.")
    w("- Why it works: each prompt file puts the long fixed instructions first and today's date/time last, and each "
      "agent sends a stable `prompt_cache_key`, so repeat calls reuse the same prefix. Caching only starts once a prefix "
      "is long enough and has been seen recently, so the first question of the day caches less.\n")

    w("## 3. What the code-level rules saved\n")
    w(f"- {len(zero_rows)} of {n} questions ({len(zero_rows) / n:.0%}) were answered by code with **0 tokens**: "
      + "; ".join(f"Q{r['n']} ({r['stop_reason']})" for r in zero_rows) + ".")
    w(f"- If the model had handled them like a normal question: {len(zero_rows)} x {avg_m['total']:,.0f} tokens = "
      f"**{saved_rules_tokens:,.0f} tokens** and {len(zero_rows)} x {money(avg_cost_m, 6)} = **{money(saved_rules_cost, 6)}** saved.")
    w("- These rules are also safer: the model never sees a medical-advice question, and never guesses a hospital.")
    w("- Other code rules that cost nothing: the daily token budget and the per-visitor rate limit refuse before any "
      "model call (see `output/limit_tests.json`).\n")

    w("## 4. Cost per user per month\n")
    w(f"Assumption: **{QUESTIONS_PER_PATIENT_PER_MONTH} questions per patient per month**, with the same mix as the "
      f"{n} test questions (average {money(avg_cost, 6)} per question, normal mode).\n")
    w("| Users | Math | Monthly cost (normal mode) | Monthly cost if every question asked all three specialists |")
    w("|---:|---|---:|---:|")
    for u in USERS:
        w(f"| {u:,} | {u:,} x {QUESTIONS_PER_PATIENT_PER_MONTH} x {money(avg_cost, 6)} | **{money(u * per_user, 2 if u > 1 else 4)}** | "
          f"{money(u * per_user_e, 2 if u > 1 else 4)} |")
    w("")
    w(f"- One patient: {QUESTIONS_PER_PATIENT_PER_MONTH} x {money(avg_cost, 6)} = {money(per_user, 6)} per month.")
    w(f"- 100 users: 100 x {money(per_user, 6)} = {money(100 * per_user, 4)} per month "
      f"({100 * QUESTIONS_PER_PATIENT_PER_MONTH:,} questions).")
    w(f"- 10,000 users: 10,000 x {money(per_user, 6)} = {money(10_000 * per_user, 2)} per month "
      f"({10_000 * QUESTIONS_PER_PATIENT_PER_MONTH:,} questions, about "
      f"{10_000 * QUESTIONS_PER_PATIENT_PER_MONTH * avg['total'] / 30:,.0f} tokens a day).")
    w(f"- Daily budget check: the app's daily budget is {config.DAILY_TOKEN_BUDGET:,} tokens, enough for about "
      f"{config.DAILY_TOKEN_BUDGET / avg['total']:,.0f} questions a day at today's average. 10,000 users would need "
      "the budget raised.")
    w(f"- Not included: web searches for holiday hours cost ${config.WEB_SEARCH_USD_PER_CALL:.2f} each, about "
      f"{config.WEB_SEARCH_USD_PER_CALL / avg_cost_m:.0f}x a normal answer, which is why holiday results are cached for "
      "24 hours and saved holiday hours are used first. Hosting, Portkey fees, and staff time are also not included.\n")

    w("## 5. Did cost-cutting hurt quality? (cost experiment)\n")
    w("Same 11 questions, two modes. \"Passed\" = the answer followed the rules and gave the key fact for that "
      "question (automatic checks in `tests/cost_experiment.py`, spot-checked by hand). The code safety rules stay on in "
      "both modes, so Q6 and Q10 use 0 tokens in both.\n")
    w("| # | Question | Normal: specialists | Normal: tokens | Normal: cost | Ask everyone: specialists | Ask everyone: tokens | Ask everyone: cost | Passed (normal / everyone) |")
    w("|---:|---|---:|---:|---:|---:|---:|---:|---|")
    for a, b in zip(normal, everyone):
        q = a["question"] if len(a["question"]) <= 60 else a["question"][:57] + "..."
        w(f"| {a['n']} | {q} | {len(a['specialists_called'])} | {a['tokens']['total']:,} | {money(a['cost_usd'], 6)} | "
          f"{len(b['specialists_called'])} | {b['tokens']['total']:,} | {money(b['cost_usd'], 6)} | "
          f"{'yes' if a['passed'] else 'NO'} / {'yes' if b['passed'] else 'NO'} |")
    w(f"| | **Total** | {sum(len(r['specialists_called']) for r in normal)} | **{s_n['total_tokens']:,}** | "
      f"**{money(s_n['total_cost_usd'], 6)}** | {sum(len(r['specialists_called']) for r in everyone)} | "
      f"**{s_e['total_tokens']:,}** | **{money(s_e['total_cost_usd'], 6)}** | {s_n['passed']}/{n} / {s_e['passed']}/{n} |\n")
    w(f"**Result:** normal mode used **{1 - s_n['total_tokens'] / s_e['total_tokens']:.0%} fewer tokens** and cost "
      f"**{1 - s_n['total_cost_usd'] / s_e['total_cost_usd']:.0%} less** than asking all three specialists, with the "
      f"same quality ({s_n['passed']}/{n} vs {s_e['passed']}/{n} passed). Calling the extra specialists added tokens "
      "without making any answer pass that failed before.\n")
    w("Limits of this evidence: 11 questions, one run per mode, and automatic checks look for key facts and rules, "
      "not writing quality. Model answers vary a little from run to run.\n")

    (ROOT / "output" / "tokenomics.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
