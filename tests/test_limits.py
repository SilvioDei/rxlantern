"""Show each spending limit stopping a run. Results go to output/limit_tests.json.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m tests.test_limits
Limits are lowered on purpose for each check, then put back. A few small model calls are made.
"""

import asyncio
import json

from fastapi.testclient import TestClient

from backend import config, usage_log
from backend.agents import ask
from backend.main import app, rate_limiter

QUESTION = "Is there a pharmacy open right now near 02111?"
KEYS = ("MAX_MODEL_REQUESTS_PER_QUESTION", "MAX_TOOL_CALLS_PER_QUESTION", "MAX_TOKENS_PER_QUESTION",
        "DAILY_TOKEN_BUDGET", "MAX_QUESTIONS_PER_VISITOR_PER_HOUR")


def summarize(name: str, reply, expect: str, setting: str) -> dict:
    ok = expect.lower() in reply.stop_reason.lower()
    print(f"{name:32} stopped={ok}  tokens={reply.usage.total_tokens:6}  {reply.stop_reason[:90]}")
    return {"limit": name, "test_setting": setting, "stopped": ok, "stop_reason": reply.stop_reason,
            "reply": reply.reply_text, "tokens_used": reply.usage.total_tokens,
            "model_requests": reply.usage.requests, "run_id": reply.run_id}


async def model_checks(saved: dict) -> list[dict]:
    """All checks that may call the model run in ONE event loop (the AI client is tied to it)."""
    out = []
    config.MAX_MODEL_REQUESTS_PER_QUESTION = 1  # Front Desk + one specialist needs more than 1 request
    out.append(summarize("model requests per question", await ask(QUESTION), "limit", "1 request"))
    config.MAX_MODEL_REQUESTS_PER_QUESTION = saved["MAX_MODEL_REQUESTS_PER_QUESTION"]

    config.MAX_TOOL_CALLS_PER_QUESTION = 1  # asking a specialist plus its tool = 2+ tool calls
    out.append(summarize("tool calls per question", await ask(QUESTION), "limit", "1 tool call"))
    config.MAX_TOOL_CALLS_PER_QUESTION = saved["MAX_TOOL_CALLS_PER_QUESTION"]

    config.MAX_TOKENS_PER_QUESTION = 1500  # a normal answer uses about 6,000-17,000 tokens
    out.append(summarize("total tokens per question", await ask(QUESTION), "limit", "1,500 tokens"))
    config.MAX_TOKENS_PER_QUESTION = saved["MAX_TOKENS_PER_QUESTION"]

    config.DAILY_TOKEN_BUDGET = usage_log.tokens_used_today()  # budget already used up
    out.append(summarize("daily token budget (app)", await ask(QUESTION), "budget", "budget = tokens already used today"))
    config.DAILY_TOKEN_BUDGET = saved["DAILY_TOKEN_BUDGET"]
    return out


def rate_check() -> dict:
    """2 questions per visitor per hour; the 3rd is refused before any model call.
    Uses a question the code answers itself (0 tokens), so this check costs nothing."""
    rate_limiter.per_hour = 2
    rate_limiter.hits.clear()
    with TestClient(app) as client:
        resp = [client.post("/api/ask", json={"question": "Should I take two of my pills?"}) for _ in range(3)]
    codes = [r.status_code for r in resp]
    ok = codes == [200, 200, 429]
    print(f"{'questions per visitor per hour':32} stopped={ok}  codes={codes}")
    third = resp[2].json()
    return {"limit": "questions per visitor per hour", "test_setting": "2 per hour", "stopped": ok,
            "http_status_codes": codes, "stop_reason": third["stop_reason"], "reply": third["reply_text"],
            "tokens_used": 0, "run_id": third["run_id"]}


def main() -> None:
    saved = {k: getattr(config, k) for k in KEYS}
    try:
        results = asyncio.run(model_checks(saved))
        results.append(rate_check())
    finally:
        for k, v in saved.items():
            setattr(config, k, v)
        rate_limiter.per_hour = None
        rate_limiter.hits.clear()
    out = config.OUTPUT_DIR / "limit_tests.json"
    out.write_text(json.dumps({"settings_in_config": saved, "results": results}, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    assert all(r["stopped"] for r in results), "a limit did not stop its run"
    print(f"OK - all {len(results)} limits stopped their runs -> {out}")


if __name__ == "__main__":
    main()
