"""Click through the website with Playwright and save screenshots to output/screenshots/.

Start the app first (python run.py), then run from the repository folder:
    ..\\.venv\\Scripts\\python.exe -m tests.ui_test
Asks a few questions (model calls), posts a stock report and a review with a throwaway test account,
then deletes that account and its posts so data/rxlantern_user.db is empty again.
"""

import json
import os
import secrets
import sqlite3
import time
from contextlib import closing

import httpx
from playwright.sync_api import Page, expect, sync_playwright

from backend import config

BASE = "http://127.0.0.1:8000"
SHOTS = config.OUTPUT_DIR / "screenshots"
DESKTOP = {"width": 1280, "height": 900}
PHONE = {"width": 390, "height": 844}
ANSWER_TIMEOUT = 120_000
results: list[dict] = []


def step(name: str, ok: bool, **info) -> None:
    results.append({"step": name, "passed": bool(ok), **info})
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  {info}" if info and not ok else ""))


def no_secrets(page: Page, name: str) -> None:
    """Fail if the page shows an API key or the owner's email."""
    text = page.content().lower()
    key = os.getenv("PORTKEY_API_KEY", "")
    owner = config.admin_emails()  # read from .env, never written in this file
    bad = [f"admin email #{i + 1}" for i, e in enumerate(sorted(owner)) if e in text or e.split("@")[0] in text] \
        + (["api key"] if key and key.lower() in text else [])
    step(f"no key or owner email visible: {name}", not bad)


def shot(page: Page, name: str, full: bool = True) -> None:
    no_secrets(page, name)
    page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=full)


def ask(page: Page, question: str) -> None:
    before = page.locator(".answer, .turn .alert").count()
    page.fill("#ask-box", question)
    page.click("button[type=submit]:has-text('Ask'), button[type=submit]:has-text('Preguntar')")
    page.locator(".working").first.wait_for(state="visible", timeout=10_000)
    page.wait_for_function(f"document.querySelectorAll('.answer, .turn .alert').length > {before}", timeout=ANSWER_TIMEOUT)


def wait_ready() -> None:
    for _ in range(60):
        try:
            if httpx.get(f"{BASE}/api/health", timeout=2).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(1)
    raise SystemExit("The app is not running at http://127.0.0.1:8000 (start it with: python run.py)")


def main() -> None:
    wait_ready()
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ---------------------------------------------------------------- normal desktop
        ctx = browser.new_context(viewport=DESKTOP, locale="en-US")
        page = ctx.new_page()
        page.goto(BASE)
        expect(page.locator("h1")).to_contain_text("Find your medicine")
        step("home loads with app name from the backend", page.title() == config.APP_NAME, title=page.title())
        step("Easy view button on the first screen", page.get_by_role("button", name="Easy view").is_visible())
        step("footer shows the safety lines", "not medical advice" in page.locator("footer").inner_text())
        shot(page, "01_home_normal")

        for q in ["Is there a pharmacy open right now near 02111?",
                  "Is Concerta 18 mg in shortage? Which pharmacy has it?",
                  "Is the CVS at South Station open on weekends?"]:
            ask(page, q)
            last = page.locator(".turn").last
            step(f"asked through the website: {q}", last.locator(".answer").count() == 1,
                 reply=last.locator(".reply-text").first.inner_text()[:160] if last.locator(".reply-text").count() else None,
                 tokens_line=last.locator(".tokens-line").inner_text() if last.locator(".tokens-line").count() else None)

        page.goto(BASE)
        ask(page, "Where can I fill Eliquis 5 mg near 02111, and what should I say when I call the pharmacy?")
        turn = page.locator(".turn").last
        has_cards, has_script = turn.locator(".pharmacy-card").count() > 0, turn.locator(".script-card").count() > 0
        step("answer shows pharmacy cards and a call script", has_cards and has_script,
             cards=turn.locator(".pharmacy-card").count(), script=has_script)
        step("pharmacy card has tap-to-call and directions links",
             turn.locator(".pharmacy-card a[href^='tel:']").count() > 0 and turn.locator(".pharmacy-card a:has-text('Directions')").count() > 0)
        step("tokens and cost line shown", "tokens" in turn.locator(".tokens-line").inner_text())
        turn.scroll_into_view_if_needed()
        no_secrets(page, "answer")
        page.screenshot(path=str(SHOTS / "04_answer_cards_and_call_script.png"), full_page=True)

        # ---------------------------------------------------------------- every page
        page.goto(f"{BASE}/pharmacies")
        page.locator(".pharmacy-card").first.wait_for()
        n_all = page.locator(".pharmacy-card").count()
        page.get_by_label("Delivery").check()
        n_delivery = page.locator(".pharmacy-card").count()
        page.get_by_label("Delivery").uncheck()
        step("pharmacies list with filters and map", n_all == 20 and 0 < n_delivery < 20
             and page.locator(".leaflet-container").count() == 1, all=n_all, delivery=n_delivery)
        page.wait_for_timeout(1500)  # map tiles
        shot(page, "09_pharmacies_list_and_map", full=False)

        page.goto(f"{BASE}/pharmacies/cvs-10174")
        page.locator(".hours.counter").wait_for()
        boxes = page.locator(".hours-grid .card")
        step("pharmacy page: counter hours first, store hours beside it",
             "counter" in boxes.nth(0).inner_text().lower() and "store hours" in boxes.nth(1).inner_text().lower())
        shot(page, "05_pharmacy_page")

        page.goto(f"{BASE}/shortages")
        page.locator(".drug-card").first.wait_for()
        concerta = page.locator(".drug-card", has_text="Concerta")
        step("shortage watch: 25 drugs, controlled show call script only",
             page.locator(".drug-card").count() == 25 and concerta.locator(".script-card").count() == 1
             and concerta.locator("text=Community reports").count() == 0)
        shot(page, "06_shortage_watch")

        page.goto(f"{BASE}/vaccines")
        page.locator(".vaccine-card").first.wait_for()
        flu = page.locator(".vaccine-card", has_text="Flu (influenza)")
        step("vaccines: pharmacies, Massachusetts rule, large-employer warning",
             page.locator(".vaccine-card").count() == 10 and "large employer" in flu.inner_text().lower()
             and "Bulletin 2025-03" in flu.inner_text())
        shot(page, "07_vaccines")

        page.goto(f"{BASE}/admin")
        step("admin page hidden from visitors", "only for admins" in page.locator("main").inner_text())

        # ---------------------------------------------------------------- posting with a throwaway account
        email = f"ui-test-{secrets.token_hex(4)}@example.com"
        page.goto(f"{BASE}/pharmacies/cvs-2283")
        page.get_by_role("button", name="Post a stock report").click()
        page.get_by_role("button", name="New here? Create an account").click()
        page.get_by_label("Email").fill(email)
        page.get_by_label("Display name").fill("UI Tester")
        page.get_by_label("Password (at least 10 characters)").fill("ui-test-password-123")
        page.get_by_label("Confirm password").fill("ui-test-password-123")
        page.get_by_role("button", name="Create account").click()
        page.get_by_role("dialog").get_by_text("I just called or visited a pharmacy").wait_for()
        step("account pop-up appears only when posting, then the report form opens", True)
        page.get_by_label("Medicine and strength").select_option("ozempic_05")
        page.get_by_role("dialog").get_by_text("In stock", exact=True).click()
        page.get_by_role("dialog").get_by_role("button", name="Submit").click()
        expect(page.get_by_role("dialog")).to_contain_text("Thank you")
        page.get_by_role("button", name="Close").click()
        page.wait_for_timeout(500)
        step("stock report posted and shown", "said in stock" in page.locator("main").inner_text())

        page.get_by_role("button", name="Write a review").click()
        page.get_by_role("dialog").get_by_label("4 stars").check(force=True)
        page.get_by_label("Wait time (minutes)").fill("12")
        page.get_by_label("Comment (optional, up to 300 characters)").fill("Quick service and the staff were friendly.")
        page.get_by_role("dialog").get_by_role("button", name="Submit").click()
        page.get_by_role("dialog").locator(".notice, .alert").wait_for(timeout=60_000)
        review_msg = page.get_by_role("dialog").locator(".notice, .alert").inner_text()
        step("review posted with a friendly moderation message", "Thank you" in review_msg, message=review_msg)
        page.get_by_role("button", name="Close").click()

        deleted = page.evaluate("fetch('/api/auth/account', {method: 'DELETE'}).then(r => r.json())")
        with closing(sqlite3.connect(config.DATA_DIR / "rxlantern_user.db")) as con:
            counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                      for t in ("users", "sessions", "stock_reports", "reviews")}
        step("test account and its posts deleted; real database empty again",
             deleted.get("deleted") and not any(counts.values()), deleted=deleted, counts=counts)
        ctx.close()

        # ---------------------------------------------------------------- Easy view
        ctx = browser.new_context(viewport=DESKTOP, locale="en-US")
        page = ctx.new_page()
        page.goto(BASE)
        page.get_by_role("button", name="Easy view").click()
        body_size = page.evaluate("parseFloat(getComputedStyle(document.body).fontSize)")
        step("Easy view: larger text and remembered in the browser", body_size >= 22
             and "easy" in page.evaluate("localStorage.getItem('rxlantern.settings')"), font_px=body_size)
        mic_supported = page.evaluate("'webkitSpeechRecognition' in window || 'SpeechRecognition' in window")
        step("microphone button shown only when the browser supports it",
             (page.locator("button.mic").count() == 1) == bool(mic_supported), supported=mic_supported)
        page.keyboard.press("Tab")
        focus_outline = page.evaluate("getComputedStyle(document.activeElement).outlineStyle")
        step("keyboard focus is visible", focus_outline not in ("none", ""), outline=focus_outline)
        shot(page, "02_home_easy_view")
        ask(page, "Does MassHealth cover Ozempic?")
        step("Easy view: read-aloud button on the answer", page.locator(".answer button:has-text('Read aloud')").count() >= 1)
        ctx.close()

        # ---------------------------------------------------------------- Spanish
        ctx = browser.new_context(viewport=DESKTOP, locale="en-US")
        page = ctx.new_page()
        page.goto(BASE)
        page.get_by_role("button", name="Cambiar a español").click()
        step("Spanish switch changes the site text", "Encuentre su medicina" in page.locator("h1").inner_text())
        shot(page, "03_home_spanish")
        ask(page, "¿Qué farmacia en East Boston tiene entrega a domicilio?")
        reply = page.locator(".reply-text").last.inner_text()
        step("agent reply is in Spanish", any(w in reply.lower() for w in ("farmacia", "entrega", " en ")), reply=reply[:160])
        ctx.close()

        # ---------------------------------------------------------------- phone width
        ctx = browser.new_context(viewport=PHONE, locale="en-US", is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.goto(BASE)
        overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
        step("phone width: no sideways scrolling", not overflow)
        shot(page, "08_home_phone")
        ctx.close()
        browser.close()

    out = config.OUTPUT_DIR / "ui_test_results.json"
    out.write_text(json.dumps({"passed": sum(r["passed"] for r in results), "total": len(results), "results": results},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{sum(r['passed'] for r in results)}/{len(results)} passed -> {out}")


if __name__ == "__main__":
    main()
