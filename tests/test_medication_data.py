"""Check the Step 3 medication tables and the FDA shortage tool (cache + offline fallback).

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m tests.test_medication_data
Calls the public openFDA API once; no AI model is called.
"""

import sqlite3
from unittest import mock

import httpx

from backend import tools
from backend.build_db import DB_PATH, build_db


def main() -> None:
    build_db()
    con = sqlite3.connect(DB_PATH)
    try:
        counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                  for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
        controlled = [r[0] for r in con.execute("SELECT id FROM drugs WHERE controlled = 1 ORDER BY id")]
    finally:
        con.close()
    print("Tables:", counts)
    assert counts["drugs"] == 25 and counts["masshealth"] == 25 and counts["shortages"] == 25
    assert counts["vaccines"] == 10 and counts["nadac_prices"] > 0
    assert controlled == ["adderall_xr_30", "concerta_18"], controlled

    first = tools.check_fda_shortage("Concerta")
    second = tools.check_fda_shortage("concerta_18")
    print("Concerta:", first["status"], "| from:", first["from"], "->", second["from"])
    assert second["from"] == "cache"

    with mock.patch.object(tools.httpx, "Client", side_effect=httpx.ConnectError("offline")):
        con = sqlite3.connect(DB_PATH)
        con.execute("DELETE FROM shortage_cache")
        con.commit()
        con.close()
        offline = tools.check_fda_shortage("atorvastatin")
    print("Atorvastatin offline:", offline["status"], "| from:", offline["from"])
    assert offline["from"].startswith("snapshot")

    print("Unknown drug:", tools.check_fda_shortage("not-a-drug")["status"])
    print("OK")


if __name__ == "__main__":
    main()
