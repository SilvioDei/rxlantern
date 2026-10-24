"""Check that the app builds data/rxlantern.db on startup from data/pharmacies.json.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m tests.test_build_db
"""

import json
import sqlite3

from fastapi.testclient import TestClient

from backend.build_db import DB_PATH, JSON_PATH
from backend.config import APP_NAME


def main() -> None:
    DB_PATH.unlink(missing_ok=True)
    from backend.main import app

    with TestClient(app) as client:
        assert client.get("/api/health").json() == {"status": "ok", "app": APP_NAME}
    assert DB_PATH.exists(), "startup did not build the database"

    expected = len(json.loads(JSON_PATH.read_text(encoding="utf-8"))["pharmacies"])
    con = sqlite3.connect(DB_PATH)
    try:
        count = con.execute("SELECT COUNT(*) FROM pharmacies").fetchone()[0]
        assert count == expected, f"{count} rows, expected {expected}"
        by_area = con.execute(
            "SELECT neighborhood, COUNT(*) FROM pharmacies GROUP BY neighborhood ORDER BY 2 DESC"
        ).fetchall()
        name, hours, lunch = con.execute(
            "SELECT address, pharmacy_hours, lunch_break FROM pharmacies WHERE id = 'cvs-10174'"
        ).fetchone()
    finally:
        con.close()
    print(f"OK: {count} pharmacies in {DB_PATH.name}")
    print("By neighborhood:", by_area)
    print("CVS 700 Atlantic:", name, "| Mon:", json.loads(hours)["mon"], "| lunch Mon:", json.loads(lunch)["mon"])


if __name__ == "__main__":
    main()
