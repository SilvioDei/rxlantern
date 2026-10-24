"""Community side of RxLantern: accounts, sessions, stock reports, reviews, and moderation.

Everything is stored in data/rxlantern_user.db (git-ignored; set RXLANTERN_USER_DB to use another file,
which the tests do). Accounts hold only an email, a display name, and a scrypt password hash.
No names, birthdates, member IDs, or health information are ever asked for or stored.
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from backend import config

NF = "not found"
CALL_TO_CONFIRM = "Call to confirm before you go."
REPORT_WINDOW_HOURS = 72
SAME_REPORT_HOURS = 6
MAX_REPORTS_PER_DAY = 10
REVIEW_EVERY_DAYS = 7
MIN_REVIEWS_FOR_AVERAGE = 3
SESSION_DAYS = 7
LOGIN_MAX_FAILURES = 5
LOGIN_WINDOW_MINUTES = 15
GENERIC_LOGIN_ERROR = "That email and password don't match. Please try again."

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL, expires_at TEXT NOT NULL
);
-- Failed logins are keyed by a hash of the email and the visitor's address, never the password.
CREATE TABLE IF NOT EXISTS login_failures (email_hash TEXT NOT NULL, ip TEXT NOT NULL, at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS stock_reports (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), pharmacy_id TEXT NOT NULL,
    drug_id TEXT NOT NULL, in_stock INTEGER NOT NULL CHECK (in_stock IN (0, 1)), reported_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), pharmacy_id TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5), wait_minutes INTEGER CHECK (wait_minutes BETWEEN 0 AND 600),
    visit_date TEXT NOT NULL, comment TEXT, status TEXT NOT NULL CHECK (status IN ('published', 'pending', 'rejected')),
    moderation TEXT, created_at TEXT NOT NULL, decided_at TEXT, decided_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_reports_pd ON stock_reports(pharmacy_id, drug_id, reported_at);
CREATE INDEX IF NOT EXISTS idx_reviews_p ON reviews(pharmacy_id, status);
"""


class CommunityError(Exception):
    """A friendly, patient-facing reason a request was refused."""

    def __init__(self, message: str, status: int = 400, code: str = "refused"):
        super().__init__(message)
        self.message, self.status, self.code = message, status, code


# ----------------------------------------------------------------------------- database
def db_path() -> Path:
    return Path(os.getenv("RXLANTERN_USER_DB") or (config.DATA_DIR / "rxlantern_user.db"))


def init_db() -> Path:
    """Create the tables if missing. Old Step 4 placeholder tables are dropped only if they are empty."""
    path = db_path()
    con = sqlite3.connect(path)
    try:
        for old in ("pharmacy_ratings", "community_users"):
            exists = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (old,)).fetchone()
            if exists and con.execute(f"SELECT COUNT(*) FROM {old}").fetchone()[0] == 0:
                con.execute(f"DROP TABLE {old}")
        cols = [r[1] for r in con.execute("PRAGMA table_info(stock_reports)")]
        if cols and "reported_at" not in cols and con.execute("SELECT COUNT(*) FROM stock_reports").fetchone()[0] == 0:
            con.execute("DROP TABLE stock_reports")
        con.executescript(SCHEMA)
        con.commit()
    finally:
        con.close()
    return path


@contextmanager
def _con():
    """Open the user database and always close it (sqlite3's own 'with' only commits)."""
    init_db()
    con = sqlite3.connect(db_path())
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
    finally:
        con.close()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


# ----------------------------------------------------------------------------- accounts
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[A-Za-z]{2,}$")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    n, r, p = 2 ** 14, 8, 1
    dk = hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p, dklen=32)
    return f"scrypt${n}${r}${p}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, n, r, p, salt, dk = stored.split("$")
        test = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(test.hex(), dk)
    except (ValueError, TypeError):
        return False


_DUMMY_HASH = hash_password(secrets.token_hex(8))  # used so a wrong email takes as long as a wrong password


def create_account(email: str, display_name: str, password: str, confirm_password: str) -> dict:
    email = (email or "").strip().lower()
    display_name = (display_name or "").strip()
    if not EMAIL_RE.match(email):
        raise CommunityError("Please enter a valid email address.")
    if not 2 <= len(display_name) <= 30 or "@" in display_name:
        raise CommunityError("Please choose a display name of 2 to 30 characters (a nickname is best, not your real name).")
    if password != confirm_password:
        raise CommunityError("The two passwords don't match.")
    if len(password) < 10:
        raise CommunityError("Please use a password with at least 10 characters.")
    with _con() as con:
        if con.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            # Same wording as success would reveal nothing; but creating twice must fail. Keep it neutral.
            raise CommunityError("We couldn't create that account. If you already have one, please log in.", 409)
        cur = con.execute("INSERT INTO users (email, display_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
                          (email, display_name, hash_password(password), _iso(_now())))
        con.commit()
        return {"id": cur.lastrowid, "display_name": display_name}


def _email_hash(email: str) -> str:
    return hashlib.sha256((email or "").strip().lower().encode()).hexdigest()


def _too_many_failures(con, email: str, ip: str) -> bool:
    since = time.time() - LOGIN_WINDOW_MINUTES * 60
    n_email = con.execute("SELECT COUNT(*) FROM login_failures WHERE email_hash = ? AND at > ?",
                          (_email_hash(email), since)).fetchone()[0]
    n_ip = con.execute("SELECT COUNT(*) FROM login_failures WHERE ip = ? AND at > ?", (ip, since)).fetchone()[0]
    return n_email >= LOGIN_MAX_FAILURES or n_ip >= LOGIN_MAX_FAILURES * 4


def login(email: str, password: str, ip: str = "unknown") -> tuple[str, dict]:
    """Return (session token, user). Same error for unknown email and wrong password."""
    email = (email or "").strip().lower()
    with _con() as con:
        if _too_many_failures(con, email, ip):
            raise CommunityError(f"Too many tries. Please wait {LOGIN_WINDOW_MINUTES} minutes and try again.", 429,
                                 "too_many_attempts")
        row = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        ok = verify_password(password or "", row["password_hash"] if row else _DUMMY_HASH) and row is not None
        if not ok:
            con.execute("INSERT INTO login_failures VALUES (?, ?, ?)", (_email_hash(email), ip, time.time()))
            con.commit()
            raise CommunityError(GENERIC_LOGIN_ERROR, 401, "bad_login")
        token = secrets.token_urlsafe(32)
        con.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",
                    (hashlib.sha256(token.encode()).hexdigest(), row["id"], _iso(_now()),
                     _iso(_now() + timedelta(days=SESSION_DAYS))))
        con.execute("DELETE FROM login_failures WHERE email_hash = ?", (_email_hash(email),))
        con.commit()
        return token, {"id": row["id"], "display_name": row["display_name"]}


def logout(token: str | None) -> None:
    if token:
        with _con() as con:
            con.execute("DELETE FROM sessions WHERE token_hash = ?", (hashlib.sha256(token.encode()).hexdigest(),))
            con.commit()


def user_from_token(token: str | None) -> dict | None:
    if not token:
        return None
    with _con() as con:
        row = con.execute("SELECT u.id, u.email, u.display_name, s.expires_at FROM sessions s JOIN users u "
                          "ON u.id = s.user_id WHERE s.token_hash = ?",
                          (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
    if row is None or datetime.fromisoformat(row["expires_at"]) < _now():
        return None
    return {"id": row["id"], "email": row["email"], "display_name": row["display_name"],
            "is_admin": row["email"] in config.admin_emails()}


# ----------------------------------------------------------------------------- shared lookups
def _drug(drug: str) -> dict:
    from backend import tools
    rows = tools._rows("SELECT * FROM drugs WHERE id = ?", (drug,))
    d = rows[0] if rows else tools.find_drug(drug)
    if d is None:
        raise CommunityError("Please pick one of the medicines in RxLantern.")
    return d


def _pharmacy(pharmacy_id: str) -> dict:
    from backend import tools
    p = tools._pharmacy(pharmacy_id)
    if p is None:
        raise CommunityError("Please pick one of the pharmacies in RxLantern.", 404)
    return p


CONTROLLED_MESSAGE = ("RxLantern does not accept or show stock reports for controlled medicines like Adderall XR "
                      "and Concerta. This protects patients and pharmacies. Please call the pharmacy directly.")


# ----------------------------------------------------------------------------- stock reports
def post_stock_report(user: dict, pharmacy_id: str, drug: str, in_stock: bool, now: datetime | None = None) -> dict:
    now = now or _now()
    _pharmacy(pharmacy_id)
    d = _drug(drug)
    if d["controlled"]:
        raise CommunityError(CONTROLLED_MESSAGE, 403, "controlled")
    with _con() as con:
        day_start = now - timedelta(hours=24)
        n_today = con.execute("SELECT COUNT(*) FROM stock_reports WHERE user_id = ? AND reported_at > ?",
                              (user["id"], _iso(day_start))).fetchone()[0]
        if n_today >= MAX_REPORTS_PER_DAY:
            raise CommunityError(f"You can post up to {MAX_REPORTS_PER_DAY} reports a day. Thank you for helping!",
                                 429, "daily_limit")
        recent = con.execute("SELECT reported_at FROM stock_reports WHERE user_id = ? AND pharmacy_id = ? AND drug_id = ? "
                             "AND reported_at > ?", (user["id"], pharmacy_id, d["id"],
                                                     _iso(now - timedelta(hours=SAME_REPORT_HOURS)))).fetchone()
        if recent:
            raise CommunityError(f"You already reported this medicine at this pharmacy in the last {SAME_REPORT_HOURS} "
                                 "hours.", 429, "same_report_limit")
        cur = con.execute("INSERT INTO stock_reports (user_id, pharmacy_id, drug_id, in_stock, reported_at) "
                          "VALUES (?, ?, ?, ?, ?)", (user["id"], pharmacy_id, d["id"], int(bool(in_stock)), _iso(now)))
        con.commit()
    return {"id": cur.lastrowid, "pharmacy_id": pharmacy_id, "drug_id": d["id"], "drug": d["display_name"],
            "in_stock": bool(in_stock), "reported_at": _iso(now), "note": CALL_TO_CONFIRM}


def stock_summary(pharmacy_id: str, drug: str | None = None, now: datetime | None = None) -> dict:
    """Reports from the last 72 hours only (older ones stay in the database, hidden)."""
    now = now or _now()
    d = _drug(drug) if drug else None
    if d is not None and d["controlled"]:
        return {"refused": True, "message": CONTROLLED_MESSAGE}
    sql = ("SELECT drug_id, in_stock, COUNT(DISTINCT user_id) AS people, MAX(reported_at) AS latest "
           "FROM stock_reports WHERE pharmacy_id = ? AND reported_at > ?")
    args = [pharmacy_id, _iso(now - timedelta(hours=REPORT_WINDOW_HOURS))]
    if d is not None:
        sql += " AND drug_id = ?"
        args.append(d["id"])
    with _con() as con:
        rows = con.execute(sql + " GROUP BY drug_id, in_stock", args).fetchall()
    by_drug: dict[str, dict] = {}
    for r in rows:
        x = by_drug.setdefault(r["drug_id"], {"drug_id": r["drug_id"], "in_stock_reports": 0,
                                              "out_of_stock_reports": 0, "latest_report": None})
        x["in_stock_reports" if r["in_stock"] else "out_of_stock_reports"] += r["people"]
        x["latest_report"] = max(filter(None, [x["latest_report"], r["latest"]]))
    for x in by_drug.values():
        x["conflicting"] = x["in_stock_reports"] > 0 and x["out_of_stock_reports"] > 0
        if x["conflicting"]:
            x["note"] = "People reported both in stock and out of stock. Stock can change quickly."
    return {"pharmacy_id": pharmacy_id, "window_hours": REPORT_WINDOW_HOURS, "drugs": list(by_drug.values()),
            "message": "No reports in the last 72 hours." if not by_drug else None, "reminder": CALL_TO_CONFIRM,
            "source": "RxLantern community reports", "checked_at": _iso(now)}


# ----------------------------------------------------------------------------- reviews
def _published_stats(con, pharmacy_id: str) -> dict:
    rows = con.execute("SELECT rating, wait_minutes FROM reviews WHERE pharmacy_id = ? AND status = 'published'",
                       (pharmacy_id,)).fetchall()
    n = len(rows)
    if n < MIN_REVIEWS_FOR_AVERAGE:
        return {"reviews": n, "average_rating": None, "average_wait_minutes": None,
                "message": f"Not enough reviews yet (needs at least {MIN_REVIEWS_FOR_AVERAGE})."}
    waits = [r["wait_minutes"] for r in rows if r["wait_minutes"] is not None]
    return {"reviews": n, "average_rating": round(sum(r["rating"] for r in rows) / n, 1),
            "average_wait_minutes": round(sum(waits) / len(waits)) if waits else None, "message": None}


def review_summary(pharmacy_id: str, limit: int = 5) -> dict:
    with _con() as con:
        stats = _published_stats(con, pharmacy_id)
        recent = con.execute("SELECT r.rating, r.wait_minutes, r.visit_date, r.comment, u.display_name "
                             "FROM reviews r JOIN users u ON u.id = r.user_id WHERE r.pharmacy_id = ? AND "
                             "r.status = 'published' ORDER BY r.created_at DESC LIMIT ?", (pharmacy_id, limit)).fetchall()
    return {"pharmacy_id": pharmacy_id, **stats,
            "recent": [{"rating": r["rating"], "wait_minutes": r["wait_minutes"], "visit_date": r["visit_date"],
                        "comment": r["comment"], "by": r["display_name"]} for r in recent],
            "source": "RxLantern community reviews"}


async def post_review(user: dict, pharmacy_id: str, rating: int, wait_minutes: int | None, visit_date: str,
                      comment: str | None, now: datetime | None = None) -> dict:
    now = now or _now()
    _pharmacy(pharmacy_id)
    if not isinstance(rating, int) or not 1 <= rating <= 5:
        raise CommunityError("Please choose a rating from 1 to 5.")
    if wait_minutes is not None and not 0 <= wait_minutes <= 600:
        raise CommunityError("Please enter a wait time from 0 to 600 minutes.")
    try:
        vd = date.fromisoformat(visit_date)
    except (TypeError, ValueError) as e:
        raise CommunityError("Please enter the visit date as YYYY-MM-DD.") from e
    if vd > now.date() or vd < now.date() - timedelta(days=365):
        raise CommunityError("The visit date must be within the last year, and not in the future.")
    comment = (comment or "").strip() or None
    if comment and len(comment) > 300:
        raise CommunityError("Please keep your comment to 300 characters or less.")
    with _con() as con:
        if con.execute("SELECT 1 FROM reviews WHERE user_id = ? AND pharmacy_id = ? AND created_at > ? "
                       "AND status != 'rejected'", (user["id"], pharmacy_id,
                                                    _iso(now - timedelta(days=REVIEW_EVERY_DAYS)))).fetchone():
            raise CommunityError("You can review the same pharmacy once a week.", 429, "weekly_limit")

    from backend.moderation import moderate  # model call only if there is a comment
    decision = await moderate(comment, pharmacy_id) if comment else {
        "decision": "publish", "stage": "no comment", "category": "none", "reason": "Rating only, no comment.",
        "cleaned_text": None, "tokens": None}
    status = {"publish": "published", "pending": "pending", "reject": "rejected"}[decision["decision"]]
    text = decision.get("cleaned_text") or comment
    with _con() as con:
        cur = con.execute(
            "INSERT INTO reviews (user_id, pharmacy_id, rating, wait_minutes, visit_date, comment, status, moderation, "
            "created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user["id"], pharmacy_id, rating, wait_minutes, vd.isoformat(), None if status == "rejected" else text,
             status, json.dumps({k: decision[k] for k in ("stage", "category", "reason")}), _iso(now)))
        con.commit()
        review_id = cur.lastrowid
    from backend.moderation import log_decision
    log_decision(review_id, pharmacy_id, decision, status)
    messages = {"published": "Thank you! Your review is published.",
                "pending": "Thank you! A person will check your comment before it is shown.",
                "rejected": "We couldn't publish this comment. " + decision["patient_reason"]
                if decision.get("patient_reason") else "We couldn't publish this comment."}
    return {"id": review_id, "status": status, "message": messages[status], "cleaned": bool(decision.get("cleaned_text")),
            "moderation": {k: decision[k] for k in ("stage", "category", "reason")}}


def pending_queue() -> list[dict]:
    with _con() as con:
        rows = con.execute("SELECT id, pharmacy_id, rating, wait_minutes, visit_date, comment, moderation, created_at "
                           "FROM reviews WHERE status = 'pending' ORDER BY created_at").fetchall()
    return [dict(r) | {"moderation": json.loads(r["moderation"] or "{}")} for r in rows]


def decide(review_id: int, approve: bool, admin: dict) -> dict:
    if not admin.get("is_admin"):
        raise CommunityError("Only admins can review the queue.", 403, "not_admin")
    with _con() as con:
        row = con.execute("SELECT * FROM reviews WHERE id = ? AND status = 'pending'", (review_id,)).fetchone()
        if row is None:
            raise CommunityError("That review is not in the pending queue.", 404)
        status = "published" if approve else "rejected"
        con.execute("UPDATE reviews SET status = ?, decided_at = ?, decided_by = ?, comment = ? WHERE id = ?",
                    (status, _iso(_now()), "admin", row["comment"] if approve else None, review_id))
        con.commit()
    from backend.moderation import log_decision
    log_decision(review_id, row["pharmacy_id"], {"stage": "human admin", "category": "admin decision",
                                                 "reason": "approved by admin" if approve else "rejected by admin",
                                                 "tokens": None}, status)
    return {"id": review_id, "status": status}


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]
