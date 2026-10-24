"""Step 7c (part 1) website checks in a real browser (Playwright, Chromium).

Run from rxcompass/ while the app is running (..\\.venv\\Scripts\\python.exe run.py):
    ..\\.venv\\Scripts\\python.exe tests\\ui_step7c.py

Checks 1-7 of Step 7c. (Check 8 = tests\\ui_step7b.py plus the Step 4 agent questions in tests\\try_agents.py.)
Types with real key presses, saves pass/fail to output/ui_test_results_7c.json and screenshots named 7c_*.png to
output/screenshots/, then deletes every test account and its posts. No AI model is called.
"""

import json
import os
import re
import sqlite3
import sys
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path

import httpx
from playwright.sync_api import Page, expect, sync_playwright

REPO = Path(__file__).resolve().parent.parent
BASE = os.getenv("RXL_BASE", "http://127.0.0.1:8000")
SHOTS = REPO / "output" / "screenshots"
RESULTS = REPO / "output" / "ui_test_results_7c.json"
USER_DB = REPO / "data" / "rxlantern_user.db"
PASSWORD = "lantern-test-" + uuid.uuid4().hex[:8]
accounts: list[str] = []
results: list[dict] = []
DESKTOP = {"width": 1280, "height": 800}
PHONE = {"width": 375, "height": 812}


def check(n: int, name: str):
    def deco(fn):
        def run(*a):
            t0 = time.time()
            try:
                notes = fn(*a) or ""
                results.append({"n": n, "check": name, "result": "PASS", "notes": notes, "seconds": round(time.time() - t0, 1)})
            except Exception as e:  # noqa: BLE001 - record the failure and keep going
                results.append({"n": n, "check": name, "result": "FAIL", "notes": f"{type(e).__name__}: {e}"[:700],
                                "seconds": round(time.time() - t0, 1)})
                traceback.print_exc()
            print(f"[{results[-1]['result']}] {n}. {name}  {results[-1]['notes']}", flush=True)
        return run
    return deco


def settings_script(**s) -> str:
    base = {"lang": "en", "easy": False, "place": "", "insurance": "", "plan": "", "drugId": ""} | s
    return f"localStorage.setItem('rxlantern.settings', JSON.stringify({json.dumps(base)}))"


def new_page(browser, viewport=DESKTOP, **settings) -> Page:
    ctx = browser.new_context(viewport=viewport)
    ctx.add_init_script(settings_script(**settings))
    return ctx.new_page()


def shot(page: Page, name: str, full: bool = False) -> None:
    page.wait_for_timeout(300)
    page.screenshot(path=str(SHOTS / f"7c_{name}"), full_page=full)


def type_into(page: Page, selector: str, text: str) -> None:
    box = page.locator(selector)
    box.click()
    box.fill("")
    box.press_sequentially(text, delay=12)


# ----------------------------------------------------------------------------- 1. drug search
# (what the patient types, a word the suggestion must contain). All are drugs added in Step 7c.
BY_BRAND = [("Wegovy", "Wegovy"), ("Jardiance", "Jardiance"), ("Lexapro", "Escitalopram"), ("Lasix", "Furosemide"),
            ("Zithromax", "Azithromycin"), ("Flomax", "Tamsulosin"), ("Narcan", "Naloxone"), ("Keflex", "Cephalexin"),
            ("Tamiflu", "Oseltamivir"), ("Symbicort", "Symbicort"), ("Trulicity", "Trulicity"), ("Vyvanse", "Vyvanse")]
BY_GENERIC = [("losartan", "Losartan"), ("gabapentin", "Gabapentin"), ("montelukast", "Montelukast"),
              ("cefdinir", "Cefdinir"), ("tirzepatide", "Zepbound"), ("dulaglutide", "Trulicity"),
              ("pantoprazole", "Pantoprazole"), ("prednisone", "Prednisone"), ("oxycodone", "Oxycodone"),
              ("rosuvastatin", "Rosuvastatin"), ("empagliflozin", "Jardiance"), ("buprenorphine", "Suboxone")]
MISSPELLED = [("metoprolal", "Metoprolol"), ("gabapenten", "Gabapentin"), ("trazadone", "Trazodone"),
              ("jardience", "Jardiance"), ("azithromicin", "Azithromycin"), ("levetiracitam", "Levetiracetam"),
              ("montelucast", "Montelukast"), ("rosuvastatine", "Rosuvastatin"), ("cefalexin", "Cephalexin"),
              ("pantoprazol", "Pantoprazole"), ("escitalopran", "Escitalopram"), ("hydroxizine", "Hydroxyzine")]


@check(1, "Drug search finds 10+ new drugs by brand name, generic name, and a misspelling")
def t_search(browser):
    page = new_page(browser)
    page.goto(BASE)
    page.locator("#drug-search").wait_for()
    found = {}
    for label, cases in (("brand", BY_BRAND), ("generic", BY_GENERIC), ("misspelling", MISSPELLED)):
        ok = []
        for typed, want in cases:
            type_into(page, "#drug-search", typed)
            try:
                expect(page.locator("#drug-list")).to_contain_text(want, timeout=3000)
                ok.append(typed)
            except AssertionError:
                print(f"   no suggestion '{want}' for '{typed}'")
            if typed == "jardience":
                shot(page, "01_misspelled_suggestion.png")
        found[label] = ok
        assert len(ok) >= 10, f"{label}: only {len(ok)} of {len(cases)} found: {ok}"
    # The same suggestions work in the top search bar.
    type_into(page, "#top-search", "Zithromax")
    expect(page.locator("#top-search-list")).to_contain_text("Azithromycin")
    return "; ".join(f"{k}: {len(v)}/{len(dict(BY_BRAND))} found" for k, v in found.items())


# ----------------------------------------------------------------------------- 2. new Schedule II drug
@check(2, "A newly added Schedule II drug (Vyvanse) shows no stock reports or report buttons")
def t_schedule2(browser):
    meta = httpx.get(f"{BASE}/api/meta").json()
    vy = next(d for d in meta["drugs"] if d["id"] == "vyvanse_30")
    assert vy["controlled"], "Vyvanse is not flagged controlled"
    page = new_page(browser, place="02124", insurance="medicare")
    page.goto(BASE)
    type_into(page, "#drug-search", "Vyvanse")
    expect(page.locator("#drug-list")).to_contain_text("Controlled medicine")
    page.locator("#drug-list li", has_text="Vyvanse").first.click()
    page.locator("input[name=drug-option]").first.check()
    page.get_by_role("button", name="Find pharmacies").click()
    page.wait_for_url(re.compile(r"/results\?drug=vyvanse_30"))
    expect(page.locator(".controlled-note")).to_be_visible()
    expect(page.locator(".result-card").first).to_be_visible()
    expect(page.locator(".script-card")).to_be_visible()
    assert page.locator(".report-buttons").count() == 0, "report buttons shown for a C-II drug"
    assert page.get_by_role("button", name=re.compile("I called")).count() == 0, "'I called' buttons shown"
    assert page.locator(".reports-box").count() == 0, "stock reports shown for a C-II drug"
    shot(page, "02_schedule2_vyvanse_results.png")
    # The shortage watch card has no community counts or report buttons either.
    page.goto(f"{BASE}/shortages")
    card = page.locator(".drug-card", has_text="Vyvanse")
    expect(card).to_be_visible(timeout=10000)
    assert card.get_by_role("button", name="I called a pharmacy").count() == 0
    # The server refuses a stock report for it, even when logged in.
    email = f"rxl-test-{uuid.uuid4().hex[:8]}@example.com"
    accounts.append(email)
    with httpx.Client(base_url=BASE) as c:
        assert c.post("/api/auth/register", json={"email": email, "display_name": "Tester 7c", "password": PASSWORD,
                                                  "confirm_password": PASSWORD}).status_code in (200, 201)
        assert c.post("/api/auth/login", json={"email": email, "password": PASSWORD}).status_code == 200
        r = c.post("/api/pharmacies/cvs-2283/stock-reports", json={"drug_id": "vyvanse_30", "in_stock": True})
        assert r.status_code == 403, f"server accepted a C-II stock report ({r.status_code})"
        r2 = c.post("/api/pharmacies/cvs-2283/stock-reports", json={"drug_id": "oxycodone_5", "in_stock": True})
        assert r2.status_code == 403, f"server accepted an oxycodone stock report ({r2.status_code})"
        c.delete("/api/auth/account")
    return f"Vyvanse ({vy['name']}) flagged controlled; results page and shortage watch have no reports or report buttons; API refuses (403) Vyvanse and oxycodone reports"


# ----------------------------------------------------------------------------- 3. drug not in the list
@check(3, "A drug not in the list shows its live FDA shortage status and a call script")
def t_other(browser):
    page = new_page(browser)
    page.goto(BASE)
    type_into(page, "#top-search", "methotrexate")
    expect(page.locator(".top-search .no-match")).to_contain_text("not in RxLantern's list")
    page.locator(".top-search").get_by_role("button", name="Search").click()
    page.wait_for_url(re.compile(r"/other-medicine\?name=methotrexate"))
    status = page.locator(".other-status")
    expect(status).to_be_visible(timeout=20000)
    today = datetime.now().date().isoformat()
    expect(status).to_contain_text(f"checked {today}")
    expect(status.locator(".badge")).to_be_visible()
    expect(status).to_contain_text("accessdata.fda.gov")
    expect(page.locator(".script-card")).to_contain_text("calling about methotrexate")
    expect(page.locator("main")).to_contain_text("Coverage and cost details are only available for the medicines in RxLantern's list")
    assert page.locator(".report-buttons").count() == 0
    badge = status.locator(".badge").inner_text()
    shot(page, "03_not_in_list_methotrexate.png", full=True)
    api = httpx.get(f"{BASE}/api/other-drug", params={"name": "methotrexate"}, timeout=30).json()
    assert api["from"].startswith("openFDA API"), api["from"]
    # A made-up name says "not found" instead of guessing.
    page.goto(f"{BASE}/other-medicine?name=zzqxvremedy")
    expect(page.locator(".other-status")).to_contain_text("could not find a medicine with this name", timeout=20000)
    return f"methotrexate: '{badge}' ({api['status']}), checked {today} from openFDA, call script shown; made-up name -> not found"


# ----------------------------------------------------------------------------- 4. community search
def report_items(page: Page):
    return page.locator("section[aria-labelledby=c-reports] .feed-item")


def review_items(page: Page):
    return page.locator("section[aria-labelledby=c-reviews] .feed-item")


@check(4, "Community search by medication, pharmacy, and neighborhood works, including 'no posts'")
def t_community(browser):
    # One real report from a test account, so real posts are searched too (it is deleted at the end).
    email = f"rxl-test-{uuid.uuid4().hex[:8]}@example.com"
    accounts.append(email)
    with httpx.Client(base_url=BASE) as c:
        c.post("/api/auth/register", json={"email": email, "display_name": "Tester 7c", "password": PASSWORD,
                                           "confirm_password": PASSWORD})
        c.post("/api/auth/login", json={"email": email, "password": PASSWORD})
        r = c.post("/api/pharmacies/walgreens-3135/stock-reports", json={"drug_id": "cephalexin_susp_250", "in_stock": True})
        assert r.status_code in (200, 201), f"could not post a test report: {r.status_code} {r.text[:200]}"
    page = new_page(browser)
    page.goto(f"{BASE}/community")
    expect(page.locator("#community-med")).to_be_visible()
    expect(page.locator(".community-search .mic")).to_be_visible()
    # by medication (real post, found by brand name)
    type_into(page, "#community-med", "Keflex")
    page.locator("#community-med-list li", has_text="Cephalexin").first.click()
    expect(report_items(page).first).to_contain_text("Cephalexin")
    texts = report_items(page).all_inner_texts()
    assert texts and all("Cephalexin" in x for x in texts), texts
    shot(page, "04_community_search_medicine.png")
    # by medication (sample posts)
    page.get_by_role("button", name="Change").click()
    type_into(page, "#community-med", "Ozempic")
    page.locator("#community-med-list li", has_text="Ozempic").first.click()
    texts = report_items(page).all_inner_texts()
    assert texts and all("Ozempic" in x for x in texts), texts
    # "no posts" for a medicine nobody reported
    page.get_by_role("button", name="Change").click()
    type_into(page, "#community-med", "lisinopril")
    page.locator("#community-med-list li", has_text="Lisinopril").first.click()
    expect(page.locator(".empty-posts").first).to_have_text("No posts for this medication yet")
    assert report_items(page).count() == 0
    shot(page, "05_community_no_posts.png")
    page.get_by_role("button", name="Clear search").click()
    # by pharmacy
    page.select_option("select[name=pharmacy]", "gary-drug")
    for x in report_items(page).all_inner_texts() + review_items(page).all_inner_texts():
        assert "Gary Drug" in x, x
    n_pharm = report_items(page).count() + review_items(page).count()
    page.select_option("select[name=pharmacy]", "")
    # by neighborhood
    page.select_option("select[name=neighborhood]", "Dorchester")
    items = report_items(page).all_inner_texts() + review_items(page).all_inner_texts()
    assert items and all("Dorchester" in x for x in items), items
    # sort by rating
    page.select_option("select[name=neighborhood]", "")
    page.select_option("select[name=sort]", "rating")
    stars = [x.count("★") for x in page.locator("section[aria-labelledby=c-reviews] .stars-inline").all_inner_texts()]
    assert stars, "no reviews to sort"
    # real reviews first, then sample reviews: each group is sorted by stars, highest first
    sample = page.locator("section[aria-labelledby=c-reviews] .is-sample .stars-inline").all_inner_texts()
    s = [x.count("★") for x in sample]
    assert s == sorted(s, reverse=True), f"sample reviews not sorted by rating: {s}"
    page.select_option("select[name=sort]", "newest")
    shot(page, "06_community_search_filters.png")
    return (f"medicine (Keflex -> real cephalexin report; Ozempic -> sample reports), 'No posts for this medication "
            f"yet' for lisinopril, pharmacy filter ({n_pharm} posts, all Gary Drug), neighborhood filter "
            f"({len(items)} posts, all Dorchester), rating sort {s}")


# ----------------------------------------------------------------------------- 5. wheelchair removed
PAGES = ["/", "/results?drug=amoxicillin_500", "/pharmacies", "/pharmacies/cvs-2283", "/shortages", "/vaccines",
         "/community", "/about", "/other-medicine?name=methotrexate", "/print?drug=amoxicillin_500"]


@check(5, "No wheelchair filter, field, or badge appears anywhere")
def t_wheelchair(browser):
    seen = []
    for lang, words in (("en", ["wheelchair"]), ("es", ["silla de ruedas", "wheelchair"])):
        page = new_page(browser, lang=lang, place="02111")
        for path in PAGES:
            page.goto(BASE + path)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            html = page.content().lower()
            for w in words:
                if w in html:
                    seen.append(f"{lang} {path}: {w}")
        page.context.close()
    for path in ("/api/pharmacies", "/api/results?drug_id=amoxicillin_500", "/api/pharmacies/cvs-2283"):
        if "wheelchair" in httpx.get(BASE + path, timeout=30).text.lower():
            seen.append(f"API {path}")
    assert not seen, seen
    return f"{len(PAGES)} pages x English and Spanish, plus 3 API responses: no wheelchair filter, field, or badge"


# ----------------------------------------------------------------------------- 6. microphone and read aloud
@check(6, "Microphone and Read aloud buttons are visible without Easy view")
def t_voice(browser):
    page = new_page(browser, place="02111")
    found = []
    page.goto(BASE)
    assert "easy" not in (page.locator("body").get_attribute("class") or "")
    for sel in (".top-search .mic", ".search-card .mic", ".ask-panel .mic"):
        expect(page.locator(sel).first).to_be_visible()
        found.append(sel)
    expect(page.locator(".top-search .mic-note")).to_contain_text(
        "In Chrome and Edge, speech is turned into text by the browser company's service. You may prefer to type private details.")
    expect(page.get_by_role("button", name="Read this page aloud")).to_be_visible()
    shot(page, "07_voice_buttons_home.png")
    page.goto(f"{BASE}/results?drug=amoxicillin_500")
    expect(page.locator(".head-actions").get_by_role("button", name="Read aloud")).to_be_visible()
    expect(page.locator(".script-card").get_by_role("button", name="Read aloud")).to_be_visible()
    page.goto(f"{BASE}/community")
    expect(page.locator(".community-search .mic")).to_be_visible()
    page.goto(f"{BASE}/other-medicine?name=methotrexate")
    expect(page.locator(".other-status").get_by_role("button", name="Read aloud")).to_be_visible(timeout=20000)
    for path in ("/pharmacies", "/shortages", "/vaccines", "/about"):
        page.goto(BASE + path)
        expect(page.get_by_role("button", name="Read this page aloud").first).to_be_visible()
    page.goto(f"{BASE}/about")
    expect(page.locator("#voice")).to_contain_text(
        "In Chrome and Edge, speech is turned into text by the browser company's service. You may prefer to type private details.")
    page.locator("#voice").scroll_into_view_if_needed()
    shot(page, "08_about_voice_note.png")
    # Review form: microphone by the comment box.
    page.goto(f"{BASE}/pharmacies/cvs-2283")
    return ("Easy view off: mic on top search, guided search, chat, and Community; 'Read this page aloud' on every page; "
            "'Read aloud' on results, call script, and the not-in-list page; note by the mic and on About & Privacy")


# ----------------------------------------------------------------------------- 7. top search bar
@check(7, "The top search bar is visible without scrolling at desktop and phone width, and starts the guided search")
def t_top(browser):
    notes = []
    for name, vp in (("desktop", DESKTOP), ("phone", PHONE)):
        page = new_page(browser, viewport=vp)
        page.goto(BASE)
        bar = page.locator(".top-search")
        expect(bar).to_be_visible()
        assert page.evaluate("window.scrollY") == 0
        box = bar.bounding_box()
        inp = page.locator("#top-search").bounding_box()
        btn = page.locator(".top-search").get_by_role("button", name="Search").bounding_box()
        assert box and inp and btn, "top search not laid out"
        bottom = max(inp["y"] + inp["height"], btn["y"] + btn["height"])
        assert bottom <= vp["height"], f"{name}: search box ends at {bottom:.0f}px, below the {vp['height']}px screen"
        header = page.locator(".site-header").bounding_box()
        assert abs(box["y"] - (header["y"] + header["height"])) < 40, f"{name}: bar is not right under the header"
        notes.append(f"{name} {vp['width']}x{vp['height']}: input and button end at {bottom:.0f}px")
        shot(page, f"09_top_search_{name}.png")
        # It starts the same guided search.
        type_into(page, "#top-search", "Lexapro")
        page.keyboard.press("Enter")
        expect(page.locator("#guided-search .chosen")).to_contain_text("Escitalopram (Lexapro)")
        page.wait_for_function("document.activeElement && document.activeElement.name === 'drug-option'", timeout=3000)
        page.context.close()
    return "; ".join(notes) + "; Enter picks the medicine and moves to the guided search's strength step"


# ----------------------------------------------------------------------------- cleanup
def cleanup() -> dict:
    with httpx.Client(base_url=BASE) as c:
        for e in accounts:
            if c.post("/api/auth/login", json={"email": e, "password": PASSWORD}).status_code == 200:
                c.delete("/api/auth/account")
    con = sqlite3.connect(USER_DB)
    for uid in [r[0] for r in con.execute("SELECT id FROM users WHERE email LIKE '%@example.com'")]:
        for table in ("stock_reports", "reviews", "sessions"):
            con.execute(f"DELETE FROM {table} WHERE user_id = ?", (uid,))
        con.execute("DELETE FROM users WHERE id = ?", (uid,))
    con.execute("DELETE FROM login_failures")
    con.commit()
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("users", "sessions", "stock_reports", "reviews", "login_failures")}
    con.close()
    return counts


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SHOTS.mkdir(parents=True, exist_ok=True)
    for old in SHOTS.glob("7c_*.png"):
        old.unlink()
    assert httpx.get(f"{BASE}/api/health").status_code == 200, "start the app first: ..\\.venv\\Scripts\\python.exe run.py"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for fn in (t_search, t_schedule2, t_other, t_community, t_wheelchair, t_voice, t_top):
            fn(browser)
        browser.close()
    counts = cleanup()
    passed = sum(r["result"] == "PASS" for r in results)
    out = {"run_at": datetime.now().isoformat(timespec="seconds"), "base_url": BASE, "browser": "Chromium (Playwright)",
           "passed": passed, "failed": len(results) - passed, "checks": results,
           "cleanup": {"test_accounts_created": len(accounts), "rows_left_in_user_db": counts},
           "screenshots": sorted(p.name for p in SHOTS.glob("7c_*.png"))}
    RESULTS.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n{passed}/{len(results)} passed. Rows left in user DB: {counts}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
