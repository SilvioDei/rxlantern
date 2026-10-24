"""Token and cost log, append-only audit trail, daily budget, and per-visitor rate limit.

Files (both in output/, both committed to a public repo, so nothing secret or personal goes in):
  token_log.jsonl   one line per question: run ID, time, language, agents, tokens per agent and total, cost
  audit_trail.json  one entry per question: redacted question, agent steps, hand-offs, tool calls (short),
                    tokens, stop reason, and code safety rules that fired. Entries are only ever appended.
"""

import json
import re
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from backend import config

BOSTON = ZoneInfo("America/New_York")
TOKEN_LOG = config.OUTPUT_DIR / "token_log.jsonl"
AUDIT_TRAIL = config.OUTPUT_DIR / "audit_trail.json"
_lock = threading.Lock()

# Last line of defense before anything is written: no keys, no passwords, no personal health information.
_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{10,}"),
    re.compile(r"(?i)(api[_-]?key|password|passwd|secret|token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{10,}"),
]


def scrub(value, max_len: int = 300):
    """Shorten and clean any value before it goes into a log file."""
    from backend.agents import redact_phi  # local import to avoid a cycle

    if isinstance(value, dict):
        return {k: scrub(v, max_len) for k, v in value.items() if k.lower() not in {"password", "api_key", "authorization"}}
    if isinstance(value, (list, tuple)):
        return [scrub(v, max_len) for v in list(value)[:8]]
    if isinstance(value, str):
        out = value
        key = config.os.getenv("PORTKEY_API_KEY", "")
        if key:
            out = out.replace(key, "[key removed]")
        for pat in _SECRET_PATTERNS:
            out = pat.sub("[secret removed]", out)
        out, _ = redact_phi(out)
        return out if len(out) <= max_len else out[: max_len - 3] + "..."
    return value


def cost_usd(input_tokens: int, cached_input_tokens: int, output_tokens: int, web_searches: int = 0) -> float | None:
    """Dollar cost of a run. None if prices are not set."""
    p = config.PRICES_USD_PER_MILLION
    if any(p.get(k) is None for k in ("input", "cached_input", "output")):
        return None
    uncached = max(input_tokens - cached_input_tokens, 0)
    dollars = (uncached * p["input"] + cached_input_tokens * p["cached_input"] + output_tokens * p["output"]) / 1_000_000
    return round(dollars + web_searches * config.WEB_SEARCH_USD_PER_CALL, 6)


def boston_now() -> datetime:
    return datetime.now(BOSTON)


def _read_token_log() -> list[dict]:
    if not TOKEN_LOG.exists():
        return []
    return [json.loads(line) for line in TOKEN_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]


def tokens_used_today() -> int:
    today = boston_now().date().isoformat()
    return sum(r["total"]["total_tokens"] for r in _read_token_log() if r["timestamp"][:10] == today)


def daily_budget_left() -> int:
    return config.DAILY_TOKEN_BUDGET - tokens_used_today()


def usage_today() -> dict:
    today = boston_now().date().isoformat()
    rows = [r for r in _read_token_log() if r["timestamp"][:10] == today]
    total = sum(r["total"]["total_tokens"] for r in rows)
    costs = [r["total"]["cost_usd"] for r in rows if r["total"]["cost_usd"] is not None]
    return {
        "date": today, "questions": len(rows),
        "questions_answered_with_zero_tokens": sum(1 for r in rows if r["total"]["total_tokens"] == 0),
        "total_tokens": total,
        "input_tokens": sum(r["total"]["input_tokens"] for r in rows),
        "cached_input_tokens": sum(r["total"]["cached_input_tokens"] for r in rows),
        "output_tokens": sum(r["total"]["output_tokens"] for r in rows),
        "average_tokens_per_question": round(total / len(rows)) if rows else 0,
        "total_cost_usd": round(sum(costs), 6) if len(costs) == len(rows) else None,
        "daily_token_budget": config.DAILY_TOKEN_BUDGET, "budget_left": config.DAILY_TOKEN_BUDGET - total,
        "prices_usd_per_million": config.PRICES_USD_PER_MILLION, "price_source": config.PRICE_SOURCE,
    }


def write_run(token_entry: dict, audit_entry: dict) -> None:
    """Append one question to the token log and the audit trail. Never removes anything."""
    token_entry = scrub(token_entry, 500)
    audit_entry = scrub(audit_entry, 300)
    with _lock:
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(token_entry, ensure_ascii=False) + "\n")
        trail = json.loads(AUDIT_TRAIL.read_text(encoding="utf-8")) if AUDIT_TRAIL.exists() else {
            "about": f"{config.APP_NAME} audit trail. Append-only. Personal information and secrets are removed.",
            "entries": []}
        trail["entries"].append(audit_entry)
        tmp = AUDIT_TRAIL.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(trail, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(AUDIT_TRAIL)


class RateLimiter:
    """At most N questions per visitor in any rolling hour (kept in memory)."""

    def __init__(self, per_hour: int | None = None):
        self.per_hour = per_hour
        self.hits: dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, visitor: str) -> bool:
        limit = self.per_hour if self.per_hour is not None else config.MAX_QUESTIONS_PER_VISITOR_PER_HOUR
        now = time.time()
        with self.lock:
            q = self.hits[visitor]
            while q and now - q[0] > 3600:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True


def read_audit(last: int = 20) -> list[dict]:
    if not AUDIT_TRAIL.exists():
        return []
    return json.loads(AUDIT_TRAIL.read_text(encoding="utf-8"))["entries"][-last:]


__all__ = ["cost_usd", "usage_today", "write_run", "daily_budget_left", "RateLimiter", "scrub", "Path"]
