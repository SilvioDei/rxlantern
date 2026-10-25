"""Safe cleanup for the browser tests: remove only what a test run created, never what real people posted or asked.

- Accounts: only test addresses (@example.com). Their stock reports, reviews, and sessions go with them.
- Answered questions: only the rows for the chat answers a test itself sent as a "real visitor" (note_question).
- Search counts: only the searches a test itself made as a "real visitor" are taken off again (note_search).
- Nothing is ever reset or overwritten, so a real question or search made while tests run is kept.
Before deleting, restore() prints what it will remove and refuses to touch any account that is not a test address.
"""

import sqlite3
from pathlib import Path

USER_DB = Path(__file__).resolve().parent.parent / "data" / "rxlantern_user.db"
TEST_DOMAIN = "@example.com"
_questions: list[str] = []                       # run ids of test questions that were counted as real
_searches: dict[tuple[str, str], int] = {}       # (drug_id, neighborhood) -> searches a test added this week


def _con() -> sqlite3.Connection:
    return sqlite3.connect(USER_DB)


def snapshot() -> dict:
    """Kept for the test scripts' start-up line; cleanup no longer restores from it."""
    return {}


def note_question(run_id: str) -> None:
    """A test sent a chat question as a real visitor and it was counted: remove that one row at cleanup."""
    _questions.append(run_id)


def note_search(drug_id: str, neighborhood: str, n: int) -> None:
    """A test made n searches as a real visitor: take n off that count at cleanup."""
    _searches[(drug_id, neighborhood)] = _searches.get((drug_id, neighborhood), 0) + n


def plan() -> dict:
    """Everything cleanup would delete: test accounts and their posts, and the test's own counted rows."""
    with _con() as con:
        users = con.execute("SELECT id, email, display_name, created_at FROM users WHERE lower(email) LIKE ?",
                            (f"%{TEST_DOMAIN}",)).fetchall()
        ids = [u[0] for u in users]
        q = ",".join("?" * len(ids)) or "NULL"
        return {"accounts": [{"id": u[0], "email": u[1], "name": u[2], "created_at": u[3]} for u in users],
                "stock_reports": con.execute(f"SELECT id, user_id, pharmacy_id, drug_id FROM stock_reports WHERE user_id IN ({q})", ids).fetchall(),
                "reviews": con.execute(f"SELECT id, user_id, pharmacy_id FROM reviews WHERE user_id IN ({q})", ids).fetchall(),
                "test_questions": list(_questions), "test_searches": dict(_searches)}


def restore(_snap: dict | None = None) -> dict:
    """Delete test accounts and their posts and the test's own counted rows; return the table counts after."""
    p = plan()
    for a in p["accounts"]:
        assert a["email"].lower().endswith(TEST_DOMAIN), f"refusing to delete a non-test account: {a['email']}"
    print(f"cleanup: deleting {len(p['accounts'])} test accounts ({', '.join(a['email'] for a in p['accounts']) or 'none'}), "
          f"{len(p['stock_reports'])} of their stock reports, {len(p['reviews'])} of their reviews, "
          f"{len(p['test_questions'])} test chat answers counted as real, test searches {p['test_searches'] or 'none'}; "
          "nothing else", flush=True)
    with _con() as con:
        for a in p["accounts"]:
            for table in ("stock_reports", "reviews", "sessions"):
                con.execute(f"DELETE FROM {table} WHERE user_id = ?", (a["id"],))
            con.execute("DELETE FROM users WHERE id = ?", (a["id"],))
        for run_id in p["test_questions"]:
            con.execute("DELETE FROM answered_questions WHERE run_id = ?", (run_id,))
        for (drug, hood), n in p["test_searches"].items():
            row = con.execute("SELECT week, count FROM search_counts WHERE drug_id = ? AND neighborhood = ? "
                              "ORDER BY week DESC LIMIT 1", (drug, hood)).fetchone()
            if row:
                left = row[1] - n
                if left > 0:
                    con.execute("UPDATE search_counts SET count = ? WHERE drug_id = ? AND neighborhood = ? AND week = ?",
                                (left, drug, hood, row[0]))
                else:
                    con.execute("DELETE FROM search_counts WHERE drug_id = ? AND neighborhood = ? AND week = ?",
                                (drug, hood, row[0]))
        con.commit()
        _questions.clear()
        _searches.clear()
        return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("users", "sessions", "stock_reports", "reviews", "search_counts", "answered_questions")}
