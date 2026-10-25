"""Safe cleanup for the browser tests: remove only what a test run created, never what real people posted.

- Accounts: only test addresses (@example.com). Their stock reports, reviews, and sessions go with them.
- Search counts and the time-saved counter: put back exactly as they were before the run (snapshot()).
- Login failures: only rows added during the run.
Before deleting, plan() lists every row it would remove, and cleanup refuses to touch any account that is not a
test address.
"""

import sqlite3
import time
from pathlib import Path

USER_DB = Path(__file__).resolve().parent.parent / "data" / "rxlantern_user.db"
TEST_DOMAIN = "@example.com"


def _con() -> sqlite3.Connection:
    return sqlite3.connect(USER_DB)


def snapshot() -> dict:
    """Call once at the start of a test run."""
    with _con() as con:
        return {"started": time.time(),
                "search_counts": con.execute("SELECT drug_id, neighborhood, week, count FROM search_counts").fetchall(),
                "impact_counter": con.execute("SELECT key, value FROM impact_counter").fetchall()}


def plan() -> dict:
    """Everything cleanup would delete: test accounts and their posts only."""
    with _con() as con:
        users = con.execute("SELECT id, email, display_name, created_at FROM users WHERE lower(email) LIKE ?",
                            (f"%{TEST_DOMAIN}",)).fetchall()
        ids = [u[0] for u in users]
        q = ",".join("?" * len(ids)) or "NULL"
        return {"accounts": [{"id": u[0], "email": u[1], "name": u[2], "created_at": u[3]} for u in users],
                "stock_reports": con.execute(f"SELECT id, user_id, pharmacy_id, drug_id FROM stock_reports WHERE user_id IN ({q})", ids).fetchall(),
                "reviews": con.execute(f"SELECT id, user_id, pharmacy_id FROM reviews WHERE user_id IN ({q})", ids).fetchall()}


def restore(snap: dict) -> dict:
    """Delete test accounts and their posts; put counts back as they were; return the table counts after."""
    p = plan()
    for a in p["accounts"]:
        assert a["email"].lower().endswith(TEST_DOMAIN), f"refusing to delete a non-test account: {a['email']}"
    print(f"cleanup: deleting {len(p['accounts'])} test accounts ({', '.join(a['email'] for a in p['accounts']) or 'none'}), "
          f"{len(p['stock_reports'])} of their stock reports, {len(p['reviews'])} of their reviews; "
          "restoring search counts and the time-saved counter to their values before the run", flush=True)
    with _con() as con:
        for a in p["accounts"]:
            for table in ("stock_reports", "reviews", "sessions"):
                con.execute(f"DELETE FROM {table} WHERE user_id = ?", (a["id"],))
            con.execute("DELETE FROM users WHERE id = ?", (a["id"],))
        con.execute("DELETE FROM login_failures WHERE at >= ?", (snap["started"],))
        con.execute("DELETE FROM search_counts")
        con.executemany("INSERT INTO search_counts (drug_id, neighborhood, week, count) VALUES (?, ?, ?, ?)",
                        snap["search_counts"])
        con.execute("DELETE FROM impact_counter")
        con.executemany("INSERT INTO impact_counter (key, value) VALUES (?, ?)", snap["impact_counter"])
        con.commit()
        return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("users", "sessions", "stock_reports", "reviews", "login_failures", "search_counts",
                          "impact_counter")}
