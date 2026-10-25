"""Step 9 (part 1b) checks in a real browser (Playwright, Chromium): vaccines are searchable.

Run from the repository folder while the app is running (..\\.venv\\Scripts\\python.exe run.py):
    ..\\.venv\\Scripts\\python.exe tests\\ui_step9_vaccines.py

Check 6 sends one chat question (gpt-6-luna through Portkey); nothing else uses the AI model.
Saves pass/fail to output/ui_test_results_step9_vaccines.json and screenshots named step9_*.png. This test makes no
accounts or posts; cleanup still runs the shared safe cleanup (test accounts only, counts put back).
"""

import json
import os
import re
import sqlite3
import sys
import time
import traceback
from pathlib import Path

import httpx
from playwright.sync_api import Page, expect, sync_playwright

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))
import cleanup_util  # noqa: E402

SNAP = cleanup_util.snapshot()  # counts before this run, put back by cleanup()
BASE = os.getenv("RXL_BASE", "http://127.0.0.1:8000")
SHOTS = REPO / "output" / "screenshots"
RESULTS = REPO / "output" / "ui_test_results_step9_vaccines.json"
DESKTOP = {"width": 1280, "height": 900}
PHONE = {"width": 390, "height": 844}
results: list[dict] = []


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


def new_page(browser, viewport=DESKTOP, **s) -> Page:
    """A fresh browser with settings saved once (not re-applied on every page load)."""
    settings = {"lang": "en", "easy": False, "place": "", "insurance": "", "plan": "", "drugId": "", "vaccineId": ""} | s
    ctx = browser.new_context(viewport=viewport)
    ctx.add_init_script(f"if (!sessionStorage.getItem('rxl-init')) {{ sessionStorage.setItem('rxl-init', '1'); "
                        f"localStorage.setItem('rxlantern.settings', JSON.stringify({json.dumps(settings)})); }}")
    return ctx.new_page()


def shot(page: Page, name: str, full: bool = False) -> None:
    page.wait_for_timeout(300)
    page.screenshot(path=str(SHOTS / f"step9_{name}"), full_page=full)


def type_into(page: Page, selector: str, text: str) -> None:
    box = page.locator(selector)
    box.click()
    box.fill("")
    box.press_sequentially(text, delay=15)


def no_sideways(page: Page) -> bool:
    return page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def search_vaccine(page: Page, typed: str, want: str, place: str, insurance: str, plan_name: str | None = None,
                   button: str = "Search", find: str = "Find pharmacies") -> None:
    """Top search bar -> guided search with the vaccine filled in -> place and insurance -> vaccine results."""
    page.goto(BASE)
    type_into(page, "#top-search", typed)
    first = page.locator("#top-search-list li").first
    expect(first).to_contain_text(want)
    expect(first.locator(".vaccine-badge")).to_be_visible()
    page.locator(".top-search").get_by_role("button", name=button).click()
    expect(page.locator(".search-card .chosen")).to_contain_text(want)
    expect(page.locator("#vaccine-chosen")).to_be_visible()
    page.locator("#place").fill(place)
    page.locator(f".ins-list input[name=insurance] >> nth={['masshealth', 'medicare', 'commercial', 'uninsured', ''].index(insurance)}").check()
    if plan_name:
        page.locator(".plan-select select").select_option(label=plan_name)
    page.get_by_role("button", name=find).click()
    page.wait_for_url(re.compile(r"/vaccine-results\?vaccine="))
    expect(page.locator(".vax-card").first).to_be_visible(timeout=15000)


# ----------------------------------------------------------------------------- 1-3. top search -> vaccine results
@check(1, "Top search 'hepatitis B vaccine' near 02368 (Randolph) reaches the vaccine results page with Morrissey Blvd")
def t_hepb_full(browser):
    page = new_page(browser)
    search_vaccine(page, "hepatitis B vaccine", "Hepatitis B", "02368", "masshealth")
    assert "vaccine=hepb" in page.url
    expect(page.locator("h1")).to_contain_text("Hepatitis B")
    card = page.locator(".vax-card", has_text="Morrissey")
    expect(card).to_be_visible()
    expect(card.locator(".vax-listed")).to_contain_text("CVS's vaccine page")
    expect(card).to_contain_text("miles away")
    shot(page, "01_hepb_randolph_results.png")
    return f"{page.locator('.vax-card').count()} pharmacies listed; Morrissey Blvd shown as listed on CVS's vaccine page (call to confirm)"


@check(2, "Top search 'hep b' near 02122 reaches the vaccine results page with Morrissey Blvd")
def t_hepb_short(browser):
    page = new_page(browser)
    search_vaccine(page, "hep b", "Hepatitis B", "02122", "medicare")
    expect(page.locator(".vax-card").first).to_contain_text("Morrissey")
    return "Morrissey Blvd is the first (nearest) card near 02122"


@check(3, "Top search 'flu shot' near 02368 reaches the flu vaccine results with Morrissey Blvd")
def t_flu(browser):
    page = new_page(browser)
    search_vaccine(page, "flu shot", "Flu", "02368", "uninsured")
    assert "vaccine=flu" in page.url
    card = page.locator(".vax-card", has_text="Morrissey")
    expect(card.locator(".vax-listed")).to_contain_text("own page")
    shot(page, "03_flu_results.png")
    return "flu is on the Morrissey Blvd store's own page"


# ----------------------------------------------------------------------------- 4. every vaccine and its common names
CASES = [("hep B shot", "Hepatitis B"), ("hepatitis b shot", "Hepatitis B"), ("hepatits b", "Hepatitis B"),
         ("Hep B.", "Hepatitis B"), ("flu shot", "Flu"), ("flu shto", "Flu"), ("influenza", "Flu"),
         ("COVID shot", "COVID-19"), ("COVID booster", "COVID-19"), ("covid boster", "COVID-19"),
         ("shingles", "Shingles"), ("Shingrix", "Shingles"), ("shingrex", "Shingles"), ("RSV", "RSV"),
         ("pneumonia", "Pneumococcal"), ("pneumococcal", "Pneumococcal"), ("pnuemonia", "Pneumococcal"),
         ("tetanus", "Tdap"), ("Tdap", "Tdap"), ("hep A", "Hepatitis A"), ("typhoid", "Typhoid"),
         ("yellow fever", "Yellow fever"), ("yelow fever", "Yellow fever")]


@check(4, "All 10 vaccines found by the names patients use, with small spelling mistakes and spoken-style text")
def t_all_names(browser):
    page = new_page(browser)
    page.goto(BASE)
    misses = []
    for typed, want in CASES:
        type_into(page, "#top-search", typed)
        try:
            expect(page.locator("#top-search-list li").first).to_contain_text(want, timeout=3000)
        except AssertionError:
            misses.append(f"{typed} -> {page.locator('#top-search-list li').first.inner_text()[:40] if page.locator('#top-search-list li').count() else 'nothing'}")
    # The guided search finds them too.
    type_into(page, "#drug-search", "shingles shot")
    expect(page.locator("#drug-list li").first).to_contain_text("Shingles")
    # Spoken searches use the same box: the microphone writes the words it heard into it.
    expect(page.locator(".top-search .mic")).to_be_visible()
    found = {w for _, w in CASES} - {m.split(" -> ")[0] for m in misses}
    assert not misses, f"missed: {misses}"
    assert len(found) == 10
    type_into(page, "#top-search", "hep b")
    shot(page, "04_hep_b_suggestion.png")
    return f"{len(CASES)} names and misspellings, all 10 vaccines; guided search too; mic present (speech goes into the same box)"


# ----------------------------------------------------------------------------- 5. coverage by insurance
@check(5, "Coverage shows correctly for MassHealth, Medicare, and Blue Cross (plus travel and yellow fever rules)")
def t_coverage(browser):
    notes = []
    page = new_page(browser, place="02122", insurance="masshealth")
    page.goto(f"{BASE}/vaccine-results?vaccine=hepb")
    cov = page.locator(".vax-coverage")
    expect(cov.locator(".cov-masshealth")).to_contain_text("MassHealth Drug List")
    assert cov.locator(".cov-medicare").count() == 0 and cov.locator(".cov-commercial").count() == 0
    notes.append("MassHealth: drug list, no PA")

    page = new_page(browser, place="02122", insurance="medicare")
    page.goto(f"{BASE}/vaccine-results?vaccine=hepb")
    cov = page.locator(".vax-coverage")
    expect(cov).to_contain_text("(Part B (for some people))")
    expect(cov.locator(".cov-medicare")).to_contain_text("$0")
    assert cov.locator(".cov-masshealth").count() == 0
    notes.append("Medicare: Part B for some people, $0")

    page = new_page(browser, place="02122", insurance="commercial", plan="bcbs_ma")
    page.goto(f"{BASE}/vaccine-results?vaccine=hepb")
    cov = page.locator(".vax-coverage")
    expect(cov).to_contain_text("Blue Cross Blue Shield of Massachusetts")
    expect(cov.locator(".cov-commercial")).to_contain_text("Bulletin 2025-03")
    expect(cov.locator(".employer-warning")).to_contain_text("large employer")
    shot(page, "05_hepb_blue_cross_coverage.png")
    notes.append("Blue Cross: Massachusetts rule first, then the large-employer warning")

    page.goto(f"{BASE}/vaccine-results?vaccine=typhoid")
    expect(page.locator(".vax-coverage")).to_contain_text("Check with your plan")
    page.goto(f"{BASE}/vaccine-results?vaccine=yellowfever")
    expect(page.locator(".yellow-fever-alert")).to_contain_text("certified sites")
    expect(page.locator(".yellow-fever-alert a")).to_have_attribute("href", re.compile("yellow-fever-vaccination-clinics"))
    notes.append("typhoid: check with your plan; yellow fever: certified sites + CDC finder")
    return "; ".join(notes)


# ----------------------------------------------------------------------------- 6. cards: call, rate, send it here, before you go
@check(6, "Vaccine cards: Call with a vaccine script, Rate this pharmacy, Send it here, Before you go; no stock-report buttons")
def t_cards(browser):
    page = new_page(browser, place="02122", insurance="masshealth")
    page.goto(f"{BASE}/vaccine-results?vaccine=hepb")
    card = page.locator(".vax-card", has_text="Morrissey")
    expect(card.get_by_role("button", name="Rate this pharmacy")).to_be_visible()
    send = card.locator(".send-here-btn")
    expect(send).to_have_attribute("href", re.compile(r"/send-here/cvs-2283\?vaccine=hepb"))
    expect(page.locator(".byg-card")).to_contain_text("vaccination record")
    expect(card.locator(".book-btn")).to_be_visible()
    assert page.locator(".report-buttons").count() == 0, "stock-report buttons on the vaccine page"
    assert page.get_by_role("button", name=re.compile("They have it|They don't")).count() == 0
    card.get_by_role("button", name="Call").click()
    modal = page.locator("[role=dialog]")
    expect(modal).to_contain_text("hepatitis B vaccine")
    expect(modal.get_by_role("link", name=re.compile("Dial"))).to_have_attribute("href", re.compile(r"^tel:"))
    assert modal.locator(".report-buttons").count() == 0, "stock-report buttons in the call window"
    shot(page, "06_call_script_modal.png")
    page.keyboard.press("Escape")
    send.click()
    page.wait_for_url(re.compile("/send-here/cvs-2283"))
    expect(page.locator(".sh-address")).to_contain_text("715 Morrissey")
    expect(page.locator(".byg-card")).to_contain_text("Hepatitis B")
    return "call window shows the vaccine script and a tel: link, no report buttons; Send it here page carries the vaccine into Before you go"


# ----------------------------------------------------------------------------- 7. medicine search unchanged
@check(7, "A medicine search still works as before (top search 'Ozempic' -> strength -> results)")
def t_medicine(browser):
    page = new_page(browser)
    page.goto(BASE)
    type_into(page, "#top-search", "Ozempic")
    first = page.locator("#top-search-list li").first
    expect(first).to_contain_text("Ozempic")
    assert first.locator(".vaccine-badge").count() == 0
    page.locator(".top-search").get_by_role("button", name="Search").click()
    page.locator("input[name=drug-option]").first.check()
    page.locator("#place").fill("02124")
    page.locator(".ins-list input[name=insurance] >> nth=0").check()
    page.get_by_role("button", name="Find pharmacies").click()
    page.wait_for_url(re.compile(r"/results\?drug=ozempic"))
    expect(page.locator(".result-card").first).to_be_visible(timeout=15000)
    expect(page.locator(".report-buttons").first).to_be_visible()
    type_into(page, "#top-search", "amoxicilin") if page.locator("#top-search").count() else None
    return "Ozempic -> strength -> 02124 -> results with stock-report buttons, as before"


# ----------------------------------------------------------------------------- 8. chat
@check(8, "Chat answers 'Does the CVS on Morrissey Blvd have the hepatitis B vaccine, and is it covered?'")
def t_chat(browser):
    page = new_page(browser, insurance="masshealth")
    page.goto(BASE)
    page.locator("#ask-box").fill("Does the CVS on Morrissey Blvd have the hepatitis B vaccine, and is it covered?")
    with page.expect_response(lambda r: "/api/ask" in r.url, timeout=180000) as info:
        page.locator("form:has(#ask-box) button[type=submit]").click()
    body = info.value.json()
    assert info.value.status == 200, f"status {info.value.status}: {str(body)[:200]}"
    text = body.get("reply_text", "")
    low = text.lower()
    assert "morrissey" in low or any("Morrissey" in (c.get("address") or "") for c in body.get("pharmacy_cards") or []), text[:300]
    assert "hepatitis b" in low, text[:300]
    assert re.search(r"cover|masshealth|\$0|no cost|copay|pay", low), f"no coverage part: {text[:300]}"
    assert not re.search(r"\bin stock\b(?! report)", low) or "not" in low, f"claims stock: {text[:300]}"
    page.wait_for_timeout(800)
    shot(page, "08_chat_morrissey_hepb.png", full=False)
    page.locator(".conversation .turn").last.scroll_into_view_if_needed()
    shot(page, "08_chat_morrissey_hepb_answer.png")
    return f"stop={body.get('stop_reason')}; reply: {text[:650]}"


# ----------------------------------------------------------------------------- 9. Spanish, Easy view, phone
@check(9, "Works in Spanish, in Easy view, and at phone width (no sideways scroll)")
def t_es_easy_phone(browser):
    views = 0
    for viewport, easy, lang in ((DESKTOP, False, "es"), (DESKTOP, True, "en"), (PHONE, False, "en"), (PHONE, True, "es")):
        page = new_page(browser, viewport=viewport, lang=lang, easy=easy, place="02122", insurance="masshealth")
        page.goto(BASE)
        type_into(page, "#top-search", "vacuna de la gripe" if lang == "es" else "hep b")
        expect(page.locator("#top-search-list li").first).to_contain_text("Flu" if lang == "es" else "Hepatitis B")
        expect(page.locator("#top-search-list li").first.locator(".vaccine-badge")).to_contain_text("Vacuna" if lang == "es" else "Vaccine")
        page.goto(f"{BASE}/vaccine-results?vaccine=hepb")
        expect(page.locator(".vax-card").first).to_be_visible(timeout=15000)
        if lang == "es":
            expect(page.locator("h1")).to_contain_text("Dónde vacunarse")
            expect(page.locator(".vax-coverage")).to_contain_text("Quién paga")
        if easy:
            assert "easy" in (page.locator("body").get_attribute("class") or "")
        assert no_sideways(page), f"sideways scroll at {viewport['width']}px (easy={easy}, {lang})"
        if viewport is PHONE and easy:
            shot(page, "09_phone_easy_spanish.png", full=True)
        elif viewport is PHONE:
            shot(page, "09_phone.png")
        views += 1
    return f"{views} views (Spanish desktop, Easy view, phone, phone + Easy view + Spanish); no sideways scroll"


# ----------------------------------------------------------------------------- 10. time-saved baseline
@check(10, "Time-saved estimate: about 12 patient minutes 'based on three measured calls', staff 4 (English and Spanish)")
def t_impact(browser):
    imp = httpx.get(f"{BASE}/api/impact").json()
    b = imp["baselines"]
    assert b["patient_minutes_per_question"] == 12 and b["staff_minutes_per_question"] == 4, b
    assert len(b["measured_calls"]) == 3
    out = []
    for lang, words in (("en", ["about 12 minutes", "based on three measured calls to Boston-area pharmacies",
                                 "about 4 minutes", "15 minutes", "13 minutes", "9 minutes"]),
                        ("es", ["unos 12 minutos", "según tres llamadas medidas a farmacias del área de Boston", "unos 4 minutos"])):
        page = new_page(browser, lang=lang)
        page.goto(f"{BASE}/about")
        main = page.locator("main")
        for w in words:
            expect(main).to_contain_text(w)
        text = main.inner_text()
        with sqlite3.connect(cleanup_util.USER_DB) as con:  # no account holder's name on the page (read at run time)
            names = [r[0] for r in con.execute("SELECT display_name FROM users") if r[0] and len(r[0]) >= 3]
        assert not [n for n in names if n in text], "a person's name is on the About page"
        out.append(lang)
        if lang == "en":
            main.get_by_text("based on three measured calls").first.scroll_into_view_if_needed()
            shot(page, "10_about_time_saved.png")
    return "API baselines 12/4 with three measured calls; About page in " + " and ".join(out) + "; no names"


# ----------------------------------------------------------------------------- 11. "about 1 mile away"
@check(11, "Distances say 'about 1 mile away' (singular) when they round to 1, and 'miles' otherwise (English and Spanish)")
def t_one_mile(browser):
    sys.path.insert(0, str(REPO))
    from backend import tools  # same distance formula as the browser
    best = None
    for z in tools._rows("SELECT zip, latitude, longitude FROM zip_centroids"):
        for ph in tools._pharmacies():
            d = tools.miles(z["latitude"], z["longitude"], ph["latitude"], ph["longitude"])
            if 0.97 <= d <= 1.03 and (best is None or abs(d - 1) < abs(best[2] - 1)):
                best = (z["zip"], ph, d)
    assert best, "no ZIP about 1 mile from a pharmacy"
    zip_code, ph, d = best
    notes = []
    for lang, one, many in (("en", "about 1 mile away", re.compile(r"about \d+(\.\d)? miles away")),
                            ("es", "a aproximadamente 1 milla", re.compile(r"a unas \d+(\.\d)? millas"))):
        page = new_page(browser, lang=lang, place=zip_code, insurance="masshealth")
        page.goto(f"{BASE}/results?drug=lisinopril_10")
        card = page.locator(f"#ph-{ph['id']}")
        page.get_by_role("button", name=re.compile("Show all|Mostrar")).click() if page.get_by_role("button", name=re.compile("Show all|Mostrar")).count() else None
        expect(card.locator(".address")).to_contain_text(one, timeout=15000)
        text = page.locator("main").inner_text()
        bad = re.findall(r"(?<![\d.])1(\.0)? (miles|millas)", text)
        assert not bad, f"plural used for 1: {bad}"
        assert many.search(text), "other distances should still say miles"
        if lang == "en":
            card.scroll_into_view_if_needed()
            shot(page, "11_about_1_mile_away.png")
        notes.append(f"{lang}: '{one}'")
    assert tools.miles_label(1.0) == "about 1 mile away" and tools.miles_label(2.34) == "about 2.3 miles away"
    return f"ZIP {zip_code} to {ph['name']} {ph['address'][:24]} ({d:.2f} mi): " + "; ".join(notes) + "; chat labels too"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SHOTS.mkdir(parents=True, exist_ok=True)
    only = {int(x) for x in sys.argv[1:]}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for n, fn in enumerate((t_hepb_full, t_hepb_short, t_flu, t_all_names, t_coverage, t_cards, t_medicine,
                                t_chat, t_es_easy_phone, t_impact, t_one_mile), 1):
            if not only or n in only:
                fn(browser)
        browser.close()
    after = cleanup_util.restore(SNAP)
    RESULTS.write_text(json.dumps({"results": results, "user_db_after": after}, indent=1, ensure_ascii=False), encoding="utf-8")
    passed = sum(r["result"] == "PASS" for r in results)
    print(f"\n{passed}/{len(results)} passed. User database after cleanup: {after}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
