"""Step 7b website checks in a real browser (Playwright, Chromium).

Run from rxcompass/ while the app is running (..\\.venv\\Scripts\\python.exe run.py):
    ..\\.venv\\Scripts\\python.exe tests\\ui_step7b.py

It starts a second copy of the app on port 8001 with SHOW_SAMPLE_DATA off (check 13), types into forms with real
key presses (the Step 7 account bug only showed up that way), saves pass/fail to output/ui_test_results.json and
screenshots to output/screenshots/, then deletes every test account and its posts.
Check 9 asks the chat one real question (uses gpt-6-luna through Portkey); every other page uses no AI.
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path

import httpx
from playwright.sync_api import Page, expect, sync_playwright

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))
import cleanup_util  # noqa: E402

SNAP = cleanup_util.snapshot()  # counts before this run, put back by cleanup()
BASE = os.getenv("RXL_BASE", "http://127.0.0.1:8000")
NO_SAMPLE_PORT = 8001
SHOTS = REPO / "output" / "screenshots"
RESULTS = REPO / "output" / "ui_test_results.json"
USER_DB = REPO / "data" / "rxlantern_user.db"
PASSWORD = "lantern-test-" + uuid.uuid4().hex[:8]
accounts: list[str] = []
results: list[dict] = []


def new_email() -> str:
    e = f"rxl-test-{uuid.uuid4().hex[:8]}@example.com"
    accounts.append(e)
    return e


def shot(page: Page, name: str, full: bool = False) -> None:
    page.wait_for_timeout(300)
    page.screenshot(path=str(SHOTS / name), full_page=full)


def check(n: int, name: str):
    def deco(fn):
        def run(*a):
            t0 = time.time()
            try:
                notes = fn(*a) or ""
                results.append({"n": n, "check": name, "result": "PASS", "notes": notes, "seconds": round(time.time() - t0, 1)})
            except Exception as e:  # noqa: BLE001 - record the failure and keep going
                results.append({"n": n, "check": name, "result": "FAIL", "notes": f"{type(e).__name__}: {e}"[:600],
                                "seconds": round(time.time() - t0, 1)})
                traceback.print_exc()
            print(f"[{results[-1]['result']}] {n}. {name}  {results[-1]['notes']}", flush=True)
        return run
    return deco


def settings_script(**s) -> str:
    base = {"lang": "en", "easy": False, "place": "", "insurance": "", "plan": "", "drugId": ""} | s
    return f"localStorage.setItem('rxlantern.settings', JSON.stringify({json.dumps(base)}))"


def type_into(page: Page, selector: str, text: str) -> None:
    box = page.locator(selector)
    box.click()
    box.press_sequentially(text, delay=15)


def create_account_in_modal(page: Page, email: str, name: str) -> None:
    modal = page.locator(".modal")
    expect(modal).to_be_visible()
    if modal.get_by_text("New here? Create an account").count():
        modal.get_by_text("New here? Create an account").click()
    type_into(page, ".modal input[name=email]", email)
    type_into(page, ".modal input[name=display_name]", name)
    type_into(page, ".modal input[name=password]", PASSWORD)
    type_into(page, ".modal input[name=confirm_password]", PASSWORD)
    vals = [page.locator(f".modal input[name={n}]").input_value() for n in ("email", "display_name", "password", "confirm_password")]
    assert vals == [email, name, PASSWORD, PASSWORD], f"typed values were not kept: {[len(v) for v in vals]}"
    modal.locator("button[type=submit]").click()
    expect(page.locator(".modal")).to_have_count(0, timeout=10000)


# ----------------------------------------------------------------------------- checks
@check(1, "Create account, log in, log out, delete account")
def t_accounts(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE)
    email = new_email()
    page.get_by_role("button", name="Log in or create account").click()
    create_account_in_modal(page, email, "Tester One")
    expect(page.locator(".toast")).to_contain_text("logged in as Tester One")
    page.get_by_role("button", name=re.compile("Account")).click()
    expect(page.locator(".account-menu")).to_contain_text("Signed in as Tester One")
    shot(page, "21_account_menu.png")
    page.get_by_role("button", name="Log out").click()
    expect(page.locator(".toast")).to_contain_text("logged out")
    page.get_by_role("button", name="Log in or create account").click()
    type_into(page, ".modal input[name=email]", email)
    type_into(page, ".modal input[name=password]", PASSWORD)
    page.locator(".modal button[type=submit]").click()
    expect(page.locator(".toast")).to_contain_text("logged in as Tester One")
    page.get_by_role("button", name=re.compile("Account")).click()
    page.get_by_role("button", name="Delete my account").click()
    page.get_by_role("button", name="Yes, delete my account").click()
    expect(page.locator(".toast")).to_contain_text("deleted")
    expect(page.get_by_role("button", name="Log in or create account")).to_be_visible()
    r = httpx.post(f"{BASE}/api/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 401, f"deleted account could still log in ({r.status_code})"
    ctx.close()
    return "typed with real key presses; deleted account can no longer log in"


JOURNEY: dict = {}


@check(2, "Full journey: Ozempic 0.5 mg, 02124, MassHealth, results, sort/filter, report, review, Community")
def t_journey(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 1000})
    page = ctx.new_page()
    JOURNEY["ctx"], JOURNEY["page"] = ctx, page
    page.goto(BASE)
    shot(page, "01_home.png", full=True)
    type_into(page, "#drug-search", "Ozempic")
    expect(page.locator("#drug-list")).to_contain_text("Ozempic (semaglutide)")
    shot(page, "04_drug_suggestions.png")
    page.locator("#drug-list li", has_text="Ozempic").first.click()
    page.locator(".option", has_text="0.5 mg").click()
    type_into(page, "#place", "02124")
    page.locator(".option", has_text="MassHealth").click()
    page.get_by_role("button", name="Find pharmacies").click()
    expect(page).to_have_url(re.compile(r"/results\?drug=ozempic_05"))
    expect(page.locator(".result-card").first).to_be_visible()
    expect(page.locator(".leaflet-container")).to_be_visible()
    assert page.locator(".leaflet-interactive").count() >= 8, "map markers missing"
    expect(page.locator(".summary-grid")).to_contain_text("MassHealth covers this medicine")
    expect(page.locator(".lead")).to_contain_text("Near ZIP 02124")
    shot(page, "05_results_page.png")
    names = lambda: page.locator(".result-card h3").all_inner_texts()  # noqa: E731
    by_distance = page.locator(".result-card .address").all_inner_texts()
    dists = [float(re.search(r"about ([\d.]+) miles", a).group(1)) for a in by_distance]
    assert dists == sorted(dists), "not sorted by distance"
    page.select_option("select[name=sort]", "latest")
    page.wait_for_timeout(200)
    after = page.locator(".result-card .address").all_inner_texts()
    assert after != by_distance, "sorting by 'open latest' did not change the order"
    for s in ("open", "rating", "wait", "distance"):
        page.select_option("select[name=sort]", s)
    count_all = int(re.search(r"\d+", page.locator(".count").inner_text()).group())
    page.check("input[name=delivery]")
    page.wait_for_timeout(200)
    count_del = int(re.search(r"\d+", page.locator(".count").inner_text()).group())
    assert 0 < count_del < count_all, f"delivery filter: {count_del} of {count_all}"
    for txt in page.locator(".result-card").all_inner_texts():
        assert "Delivery: yes" in txt
    page.uncheck("input[name=delivery]")
    # Step 7c: the wheelchair filter was removed, and the language filter now includes languages patients reported
    # (a sample review reports Spanish), so use a language nobody reported.
    page.select_option("select[name=language]", "Vietnamese")
    expect(page.locator(".empty")).to_contain_text("don't list languages spoken")
    page.get_by_role("button", name="Clear filters").click()
    page.check("input[name=open]")
    page.wait_for_timeout(200)
    for card in page.locator(".result-card").all():
        expect(card.locator(".badge-open")).to_be_visible()
    page.uncheck("input[name=open]")

    first = page.locator(".result-card").first
    pharmacy = first.locator("h3").inner_text()
    pid = first.get_attribute("id").removeprefix("ph-")
    JOURNEY["pid"], JOURNEY["pharmacy"] = pid, pharmacy
    first.get_by_role("button", name="I called: They have it").click()
    email = new_email()
    JOURNEY["email"] = email
    create_account_in_modal(page, email, "Journey Tester")  # asked to log in only now
    expect(page.locator(".toast")).to_contain_text("Your report is posted")
    card = page.locator(f"#ph-{pid}")
    expect(card.locator(".reports-box")).to_contain_text("1 said in stock")
    card.scroll_into_view_if_needed()
    shot(page, "06_report_posted_on_card.png")
    card.get_by_role("button", name="Rate this pharmacy").click()
    page.locator(".modal .star").nth(3).click()
    page.fill(".modal input[name=wait]", "10")
    type_into(page, ".modal textarea[name=comment]", "Friendly staff and a short line.")
    page.locator(".modal button[type=submit]").click()
    expect(page.locator(".toast")).to_contain_text("Your review is published", timeout=90000)
    expect(card).to_contain_text("1 review(s)")
    card.scroll_into_view_if_needed()
    shot(page, "07_review_on_results_card.png")
    page.locator(".main-nav").get_by_role("link", name="Community").click()
    feed = page.locator("#c-reports").locator("..")
    expect(feed.locator(".feed").first).to_contain_text("Ozempic")
    expect(feed.locator(".feed").first).to_contain_text(pharmacy)
    expect(page.locator("#c-reviews").locator("..").locator(".feed").first).to_contain_text("Friendly staff and a short line.")
    shot(page, "08_community.png", full=True)
    real_first = feed.locator(".feed").first.locator(".feed-item").first
    assert real_first.locator(".badge-sample").count() == 0, "real report shows a Sample badge"
    return f"report + review for {pharmacy} ({pid}) shown on results and Community"


@check(3, "Concerta 18 mg: no stock reports or report buttons, with the explanation")
def t_concerta(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 1000})
    ctx.add_init_script(settings_script(place="02124", insurance="masshealth"))
    page = ctx.new_page()
    page.goto(BASE)
    type_into(page, "#drug-search", "Concerta 18 mg")
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    page.locator(".option", has_text="18 mg").click()
    page.get_by_role("button", name="Find pharmacies").click()
    expect(page.locator(".result-card").first).to_be_visible()
    expect(page.locator(".controlled-note")).to_contain_text("does not collect or show stock reports for controlled medicines")
    expect(page.locator(".script-card")).to_contain_text("Concerta")
    assert page.locator(".report-buttons").count() == 0, "report buttons shown for a controlled drug"
    assert page.locator(".reports-box").count() == 0, "stock reports shown for a controlled drug"
    expect(page.locator(".summary-grid")).to_contain_text("In shortage")
    expect(page.locator(".result-card").first).to_contain_text("Pharmacy counter today")
    page.locator(".result-card").first.get_by_role("button", name="Call").click()
    expect(page.locator(".modal")).to_contain_text("Concerta")
    assert page.locator(".modal .report-buttons").count() == 0
    page.keyboard.press("Escape")
    shot(page, "16_results_concerta_controlled.png")
    ctx.close()
    return "shortage status, hours, and call script shown; no reports, no report buttons"


@check(4, "Medicare, then Blue Cross: coverage, plan finder link, and member services number change")
def t_insurance(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 1000})
    ctx.add_init_script("if (!sessionStorage.getItem('seeded')) {" + settings_script(place="02124", insurance="medicare", drugId="ozempic_05") + "; sessionStorage.setItem('seeded','1') }")
    page = ctx.new_page()
    page.goto(f"{BASE}/results?drug=ozempic_05")
    grid = page.locator(".summary-grid")
    expect(grid).to_contain_text("Medicare drug plans in Massachusetts cover it")
    expect(grid).to_contain_text("1-800-MEDICARE (1-800-633-4227)")
    assert page.locator(".summary-grid a[href*='medicare.gov/plan-compare']").count() == 1
    med_text = grid.inner_text()
    page.goto(BASE)
    page.locator(".chosen-row, #drug-search").first.wait_for()
    page.locator(".option", has_text="A plan through work or private").click()
    page.select_option(".plan-select select", "bcbs_ma")
    page.get_by_role("button", name="Find pharmacies").click()
    expect(grid).to_contain_text("Blue Cross Blue Shield of Massachusetts")
    expect(grid).to_contain_text("does not have commercial plans' drug lists")
    expect(grid).to_contain_text("1-800-262-2583")
    assert page.locator(".summary-grid a[href*='member.bluecrossma.com/pharmacy-locator']").count() == 1
    assert page.locator(".result-card a[href*='member.bluecrossma.com']").count() >= 1, "card lacks plan finder link"
    expect(page.locator(".result-card").first).to_contain_text("Call to confirm they take your insurance.")
    assert grid.inner_text() != med_text
    shot(page, "05b_results_blue_cross.png")
    ctx.close()
    return "Medicare: Plan Finder + 1-800-MEDICARE; Blue Cross: BCBS locator + 1-800-262-2583"


@check(5, "A closed pharmacy shows 'Closed, opens at…' and an open alternative")
def t_closed(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 1000})
    ctx.add_init_script(settings_script(place="02124", insurance="masshealth"))
    page = ctx.new_page()
    page.goto(f"{BASE}/results?drug=ozempic_05&at=2026-10-24T13:45")
    expect(page.locator(".result-card").first).to_be_visible()
    page.get_by_role("button", name=re.compile("Show all")).click()
    closed = page.locator(".result-card", has=page.locator(".badge-closed", has_text="Closed, opens")).first
    expect(closed).to_be_visible()
    expect(closed.locator(".alt-line")).to_contain_text("Open now nearby:")
    closed.scroll_into_view_if_needed()
    shot(page, "05c_closed_with_alternative.png")
    text = closed.locator(".badge-closed").inner_text()
    ctx.close()
    return f"'{text}' + open alternative (checked at Sat 1:45 PM)"


@check(6, "Shortage watch loads in under 2 seconds, and its buttons work")
def t_shortages(browser):
    page = JOURNEY["page"]
    t0 = time.time()
    page.goto(f"{BASE}/shortages")
    n_drugs = len(httpx.get(f"{BASE}/api/meta").json()["drugs"])  # 150 since Step 7c
    expect(page.locator(".drug-card")).to_have_count(n_drugs)
    secs = time.time() - t0
    assert secs < 2, f"took {secs:.2f} s"
    shot(page, "12_shortage_watch.png")
    card = page.locator(".drug-card", has_text="Amoxicillin 500 mg capsule")
    card.get_by_role("button", name="Get a call script").click()
    expect(card.locator(".script-card")).to_contain_text("Amoxicillin")
    expect(card.locator(".script-card .report-buttons")).to_be_visible()
    card.get_by_role("button", name="I called a pharmacy").click()
    expect(page.locator(".modal select[name=drug]")).to_have_value("amoxicillin_500")
    page.keyboard.press("Escape")
    concerta = page.locator(".drug-card", has_text="Concerta 18 mg")
    assert concerta.get_by_role("button", name="I called a pharmacy").count() == 0
    concerta.get_by_role("button", name="Find pharmacies near me").click()
    expect(page).to_have_url(re.compile(r"/results\?drug=concerta_18"))
    expect(page.locator(".result-card").first).to_be_visible()
    return f"{n_drugs} drugs loaded in {secs:.2f} s; call script, report form (pre-filled), and results link work"


@check(7, "Pharmacy, Vaccines, Community, and About & Privacy pages show the right content")
def t_pages(browser):
    page = JOURNEY["page"]
    page.goto(f"{BASE}/pharmacies/cvs-2283")
    body = page.locator("main")
    expect(body).to_contain_text("Pharmacy counter hours")
    txt = body.inner_text()
    assert txt.index("Pharmacy counter hours") < txt.index("Store hours"), "counter hours not first"
    for s in ("Lunch break", "Weekend", "Holidays", "Delivery", "Walk-in clinics nearby", "Book a vaccine", "Reviews",
              "Community stock reports"):
        expect(body).to_contain_text(s)
    page.select_option("select[name=call-drug]", "albuterol_hfa")
    expect(page.locator(".script-card .report-buttons")).to_be_visible()
    expect(page.get_by_role("button", name="Rate this pharmacy").first).to_be_visible()
    shot(page, "11_pharmacy_page.png", full=True)
    page.goto(f"{BASE}/pharmacies/gary-drug")
    expect(page.locator("main")).to_contain_text("No reviews yet. Be the first to rate this pharmacy.")
    page.goto(f"{BASE}/vaccines")
    page.get_by_role("button", name=re.compile("^Flu")).click()
    expect(page.locator("main")).to_contain_text("If your plan is through a large employer")
    assert page.get_by_role("link", name=re.compile("Book a vaccine")).count() >= 1
    shot(page, "13_vaccines.png", full=True)
    page.get_by_role("button", name=re.compile("Yellow fever")).click()
    expect(page.locator("main")).to_contain_text("given only at certified sites")
    expect(page.locator("main")).to_contain_text("Travel vaccines are often not covered. Check with your plan.")
    page.goto(f"{BASE}/community")
    expect(page.locator("main h1")).to_have_text("Community")
    page.goto(f"{BASE}/about")
    expect(page.locator("main")).to_contain_text("never stores health information")
    expect(page.locator("main")).to_contain_text("Answers can be wrong")
    expect(page.locator(".data-table").first.locator("tbody tr")).to_have_count(11)  # Step 7c part 2: + savings sources
    shot(page, "14_about_privacy.png", full=True)
    return "all four pages load with their key sections"


@check(8, "'Print / share for my doctor' makes a clean printable page")
def t_print(browser):
    page = JOURNEY["page"]
    page.goto(f"{BASE}/results?drug=ozempic_05")
    page.get_by_role("button", name="Print / share for my doctor").click()
    expect(page).to_have_url(re.compile(r"/print\?drug=ozempic_05"))
    expect(page.locator(".print-table tbody tr")).to_have_count(10)
    page.emulate_media(media="print")
    assert not page.locator(".site-header").is_visible() and not page.locator(".print-actions").is_visible()
    text = page.locator("main").inner_text()
    assert "02124" not in text and "@" not in text, "personal details on the print page"
    for s in ("FDA shortage status", "Coverage and cost", "Estimate only", "Counter hours today"):
        assert s in text, s
    shot(page, "15_print_summary.png", full=True)
    page.pdf(path=str(REPO / "output" / "print_summary_sample.pdf"))
    page.emulate_media(media="screen")
    return "print view hides site chrome; no ZIP or email; PDF saved to output/print_summary_sample.pdf"


@check(9, "The chat still answers, and its call script shows the report buttons")
def t_chat(browser):
    page = JOURNEY["page"]
    page.goto(BASE)
    page.fill("#ask-box", "Can you give me a call script to ask a pharmacy if they have amoxicillin 500 mg capsules?")
    page.get_by_role("button", name="Ask", exact=True).click()
    expect(page.locator(".answer .reply-text")).to_be_visible(timeout=150000)
    expect(page.locator(".answer .script-card")).to_be_visible()
    expect(page.locator(".answer .script-card .report-buttons")).to_be_visible()
    page.locator(".answer").scroll_into_view_if_needed()
    shot(page, "20_chat_answer_with_report_buttons.png")
    return page.locator(".tokens-line").inner_text()


def _ask_emergency(page: Page, q: str) -> dict:
    with page.expect_response(lambda r: r.url.endswith("/api/ask")) as resp:
        page.fill("#ask-box", q)
        page.locator("#ask-box").press("Enter")
    t0 = time.time()
    body = resp.value.json()
    expect(page.locator(".emergency").last).to_be_visible(timeout=3000)
    return body | {"_secs": time.time() - t0}


@check(10, "Emergency message in English and Spanish, before any AI call")
def t_emergency(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script("if (!sessionStorage.getItem('seeded')) {" + settings_script() + "; sessionStorage.setItem('seeded','1') }")
    page = ctx.new_page()
    page.goto(BASE)
    en = _ask_emergency(page, "I took too many pills")
    expect(page.locator(".emergency").last).to_contain_text("If this is an emergency, call 911. For a possible poisoning or overdose, call Poison Control at 1-800-222-1222.")
    page.locator(".emergency").last.scroll_into_view_if_needed()
    shot(page, "09_emergency_english.png")
    page.get_by_role("button", name="Español").click()
    es = _ask_emergency(page, "Tomé demasiadas pastillas y no puedo respirar")
    expect(page.locator(".emergency").last).to_contain_text("llame al 911")
    expect(page.locator(".emergency").last).to_contain_text("1-800-222-1222")
    page.locator(".emergency").last.scroll_into_view_if_needed()
    shot(page, "10_emergency_spanish.png")
    trail = json.loads((REPO / "output" / "audit_trail.json").read_text(encoding="utf-8"))["entries"]
    for r in (en, es):
        assert r["emergency"] and r["usage"]["total_tokens"] == 0 and r["usage"]["requests"] == 0
        entry = next(e for e in trail if e["run_id"] == r["run_id"])
        assert any("emergency message shown" in s for s in entry["safety_rules_fired"])
    ctx.close()
    return "0 model requests, 0 tokens; audit trail logs 'emergency message shown' for both"


@check(11, "English and Español both selectable, and the whole site switches")
def t_language(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script("if (!sessionStorage.getItem('seeded')) {" + settings_script(place="02124", insurance="masshealth") + "; sessionStorage.setItem('seeded','1') }")
    page = ctx.new_page()
    page.goto(BASE)
    expect(page.get_by_role("button", name="English")).to_have_attribute("aria-pressed", "true")
    page.get_by_role("button", name="Español").click()
    expect(page.get_by_role("button", name="Español")).to_have_attribute("aria-pressed", "true")
    expect(page.get_by_role("button", name="English")).to_have_attribute("aria-pressed", "false")
    expect(page.locator("html")).to_have_attribute("lang", "es")
    expect(page.locator(".main-nav")).to_contain_text("Buscar mi medicina")
    expect(page.locator("main")).to_contain_text("Cómo funciona")
    shot(page, "03_home_spanish.png", full=True)
    checks = {"/results?drug=ozempic_05": "Farmacias para", "/shortages": "Escasez de medicinas",
              "/vaccines": "Vacunas", "/community": "Comunidad", "/about": "Acerca de y privacidad",
              "/pharmacies": "Farmacias", "/pharmacies/cvs-2283": "Horario del mostrador"}
    for path, want in checks.items():
        page.goto(BASE + path)
        expect(page.locator("main")).to_contain_text(want)
        expect(page.locator(".site-footer")).to_contain_text("no consejo médico")
    page.get_by_role("button", name="English").click()
    expect(page.locator(".main-nav")).to_contain_text("Find my medicine")
    expect(page.locator("main")).to_contain_text("Pharmacy counter hours")
    ctx.close()
    return f"{len(checks)} pages checked in Spanish, then back to English"


@check(12, "Easy view on the results page, and every page at phone width")
def t_easy_phone(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 1000})
    ctx.add_init_script("if (!sessionStorage.getItem('seeded')) {" + settings_script(place="02124", insurance="masshealth") + "; sessionStorage.setItem('seeded','1') }")
    page = ctx.new_page()
    page.goto(BASE)
    page.get_by_role("button", name="Easy view").click()
    shot(page, "02_home_easy_view.png")
    page.goto(f"{BASE}/results?drug=ozempic_05")
    expect(page.locator("body")).to_have_class(re.compile("easy"))
    size = page.evaluate("parseFloat(getComputedStyle(document.body).fontSize)")
    assert size >= 22, size
    expect(page.get_by_role("button", name="Read this page aloud")).to_be_visible()
    btn_h = page.locator(".result-card .btn").first.bounding_box()["height"]
    assert btn_h >= 56, btn_h
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    focused = page.evaluate("document.activeElement && document.activeElement.tagName")
    assert focused in ("A", "BUTTON"), focused
    shot(page, "17_results_easy_view.png")
    ctx.close()

    phone = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    phone.add_init_script("if (!sessionStorage.getItem('seeded')) {" + settings_script(place="02124", insurance="medicare") + "; sessionStorage.setItem('seeded','1') }")
    p = phone.new_page()
    wide = []
    paths = ["/", "/results?drug=ozempic_05", "/results?drug=concerta_18", "/print?drug=ozempic_05", "/pharmacies",
             "/pharmacies/cvs-2283", "/shortages", "/vaccines", "/community", "/about", "/admin"]
    for path in paths:
        p.goto(BASE + path)
        p.wait_for_timeout(700)
        sw = p.evaluate("document.documentElement.scrollWidth")
        if sw > 391:
            wide.append(f"{path}={sw}px")
    p.goto(BASE)
    shot(p, "18_phone_home.png", full=True)
    p.goto(f"{BASE}/results?drug=ozempic_05")
    p.wait_for_timeout(700)
    shot(p, "19_phone_results.png")
    p.get_by_role("button", name="Easy view").click()
    for path in paths:
        p.goto(BASE + path)
        p.wait_for_timeout(500)
        sw = p.evaluate("document.documentElement.scrollWidth")
        if sw > 391:
            wide.append(f"easy {path}={sw}px")
    phone.close()
    assert not wide, "sideways scrolling: " + ", ".join(wide)
    return f"Easy view: {size:.0f}px text, {btn_h:.0f}px buttons; {len(paths)} pages x 2 views at 390px, no sideways scroll"


@check(13, "Sample data: 'Sample' badges and Community note; SHOW_SAMPLE_DATA off hides it")
def t_samples(browser):
    page = JOURNEY["page"]
    page.goto(f"{BASE}/community")
    expect(page.locator("main")).to_contain_text("Includes sample posts for demonstration")
    items = page.locator(".feed-item.is-sample")
    n = items.count()
    assert n >= 10, n
    for i in range(n):
        expect(items.nth(i).locator(".badge-sample")).to_have_text("Sample")
        expect(items.nth(i)).to_contain_text("RxLantern sample") if items.nth(i).locator(".stars-inline").count() else None
    page.goto(f"{BASE}/results?drug=ozempic_05")
    sample_card = page.locator("#ph-cvs-2283")
    if not sample_card.count():
        page.get_by_role("button", name=re.compile("Show all")).click()
    expect(page.locator("#ph-cvs-2283 .sample-line .badge-sample")).to_be_visible()
    api = httpx.get(f"{BASE}/api/results", params={"drug_id": "ozempic_05"}).json()
    row = next(p for p in api["pharmacies"] if p["id"] == JOURNEY["pid"])
    assert row["reports"]["in_stock_reports"] == 1, row["reports"]  # the one real report, never mixed with samples
    assert row["reviews"]["reviews"] == 1, row["reviews"]
    env = os.environ | {"RXLANTERN_SHOW_SAMPLE_DATA": "0", "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--port", str(NO_SAMPLE_PORT), "--log-level", "warning"],
                            cwd=REPO, env=env)
    try:
        for _ in range(60):
            try:
                if httpx.get(f"http://127.0.0.1:{NO_SAMPLE_PORT}/api/health").status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.5)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        p2 = ctx.new_page()
        p2.goto(f"http://127.0.0.1:{NO_SAMPLE_PORT}/community")
        expect(p2.locator("main h2").first).to_be_visible()
        p2.wait_for_timeout(500)
        assert "Includes sample posts" not in p2.locator("main").inner_text()
        assert p2.locator(".badge-sample").count() == 0
        p2.goto(f"http://127.0.0.1:{NO_SAMPLE_PORT}/results?drug=ozempic_05")
        expect(p2.locator(".result-card").first).to_be_visible()
        assert p2.locator(".badge-sample").count() == 0
        assert httpx.get(f"http://127.0.0.1:{NO_SAMPLE_PORT}/api/meta").json()["sample_data"] is False
        ctx.close()
    finally:
        proc.terminate()
        proc.wait(timeout=20)
    return f"{n} sample items, each badged; real counts kept apart; with SHOW_SAMPLE_DATA off: no samples, no note"


def cleanup(browser) -> dict:
    """Delete every test account (and its posts) and confirm the real database has no user rows left."""
    page = JOURNEY.get("page")
    if page is not None and JOURNEY.get("email"):
        page.goto(BASE)
        page.get_by_role("button", name=re.compile("Account")).click()
        page.get_by_role("button", name="Delete my account").click()
        page.get_by_role("button", name="Yes, delete my account").click()
        expect(page.locator(".toast")).to_contain_text("deleted")
        JOURNEY["ctx"].close()
    with httpx.Client(base_url=BASE) as c:
        for e in accounts:
            if c.post("/api/auth/login", json={"email": e, "password": PASSWORD}).status_code == 200:
                c.delete("/api/auth/account")
    # Only test accounts (@example.com) and their posts; counts go back to how they were before the run.
    return cleanup_util.restore(SNAP)


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    for old in SHOTS.glob("[0-9][0-9]*.png"):  # only this test's own numbered screenshots (01_home.png ...)
        old.unlink()
    assert httpx.get(f"{BASE}/api/health").status_code == 200, "start the app first: ..\\.venv\\Scripts\\python.exe run.py"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for fn in (t_accounts, t_journey, t_concerta, t_insurance, t_closed, t_shortages, t_pages, t_print, t_chat,
                   t_emergency, t_language, t_easy_phone, t_samples):
            fn(browser)
        counts = cleanup(browser)
        browser.close()
    passed = sum(r["result"] == "PASS" for r in results)
    out = {"run_at": datetime.now().isoformat(timespec="seconds"), "base_url": BASE, "browser": "Chromium (Playwright)",
           "passed": passed, "failed": len(results) - passed, "checks": results,
           "cleanup": {"test_accounts_created": len(accounts), "rows_left_in_user_db": counts},
           "screenshots": sorted(p.name for p in SHOTS.glob("[0-9][0-9]*.png"))}
    RESULTS.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n{passed}/{len(results)} passed. Rows left in user DB: {counts}")
    return 0 if passed == len(results) and not any(counts.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
