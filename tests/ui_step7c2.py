"""Step 7c (part 2) feature checks in a real browser (Playwright, Chromium).

Run from rxcompass/ while the app is running (..\\.venv\\Scripts\\python.exe run.py):
    ..\\.venv\\Scripts\\python.exe tests\\ui_step7c2.py

Checks 1-12 of Step 7c part 2. (Check 13 = tests\\ui_step7b.py, tests\\ui_step7c.py, and the Step 4 agent questions.)
Check 11 sends two chat questions (gpt-6-luna through Portkey); nothing else uses the AI model.
"Real visitor" calls are simulated with a normal browser user agent and undone at the end. Saves pass/fail to
output/ui_test_results_7c2.json and screenshots named 7c2_*.png, then deletes every test account, its posts, the test
search counts, and the test question count, so the user database has no real-user rows again.
"""

import json
import os
import re
import sqlite3
import sys
import time
import traceback
import uuid
from datetime import date, datetime
from pathlib import Path

import httpx
from playwright.sync_api import Page, expect, sync_playwright

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))
import cleanup_util  # noqa: E402

SNAP = cleanup_util.snapshot()  # counts before this run, put back by cleanup()
BASE = os.getenv("RXL_BASE", "http://127.0.0.1:8000")
SHOTS = REPO / "output" / "screenshots"
RESULTS = REPO / "output" / "ui_test_results_7c2.json"
USER_DB = REPO / "data" / "rxlantern_user.db"
PASSWORD = "lantern-test-" + uuid.uuid4().hex[:8]
REAL_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
accounts: list[str] = []
results: list[dict] = []
DESKTOP = {"width": 1280, "height": 900}
PHONE = {"width": 390, "height": 844}
STATE: dict = {}


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


def settings(**s) -> dict:
    return {"lang": "en", "easy": False, "place": "", "insurance": "", "plan": "", "drugId": ""} | s


def new_ctx(browser, viewport=DESKTOP, mylist=None, **s):
    ctx = browser.new_context(viewport=viewport)
    init = f"localStorage.setItem('rxlantern.settings', JSON.stringify({json.dumps(settings(**s))}));"
    if mylist is not None:
        init += f"if (localStorage.getItem('rxlantern.mylist') === null) localStorage.setItem('rxlantern.mylist', JSON.stringify({json.dumps(mylist)}));"
    ctx.add_init_script(init)
    return ctx


def shot(page: Page, name: str, full: bool = False) -> None:
    page.wait_for_timeout(300)
    page.screenshot(path=str(SHOTS / f"7c2_{name}"), full_page=full)


def type_into(page: Page, selector: str, text: str) -> None:
    box = page.locator(selector)
    box.click()
    box.fill("")
    box.press_sequentially(text, delay=12)


def login(request, name="Tester 7c2") -> str:
    """Create a test account and log in through a Playwright (browser context) or httpx client."""
    email = f"rxl-test-{uuid.uuid4().hex[:8]}@example.com"
    accounts.append(email)
    body = {"email": email, "display_name": name, "password": PASSWORD, "confirm_password": PASSWORD}
    if isinstance(request, httpx.Client):
        assert request.post("/api/auth/register", json=body).status_code in (200, 201)
        assert request.post("/api/auth/login", json={"email": email, "password": PASSWORD}).status_code == 200
    else:
        assert request.post(f"{BASE}/api/auth/register", data=body).ok
        assert request.post(f"{BASE}/api/auth/login", data={"email": email, "password": PASSWORD}).ok
    return email


def no_sideways(page: Page) -> bool:
    return page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


# ----------------------------------------------------------------------------- 1. my medicine list
@check(1, "My medicine list with Ozempic 0.5 mg, lisinopril 10 mg, and albuterol: ranked pharmacies with 'X of 3'")
def t_mylist(browser):
    ctx = new_ctx(browser, place="02124", mylist=[])
    page = ctx.new_page()
    page.goto(f"{BASE}/my-list")
    for typed, label in (("Ozempic", "Ozempic"), ("lisinopril", "Lisinopril"), ("albuterol", "Albuterol inhaler")):
        type_into(page, "#mylist-search", typed)
        page.locator("#mylist-search-list li", has_text=label).first.click()
        if page.locator(".option-list button.option").count():
            page.locator(".option-list button.option").first.click()
    expect(page.locator(".mylist-item")).to_have_count(3)
    expect(page.locator(".mylist-card").first).to_be_visible(timeout=15000)
    first = page.locator(".mylist-card").first.inner_text()
    assert re.search(r"Reported in stock for \d of 3 of your medicines", first), first
    assert "Call to confirm" in first
    # A real "in stock" report for 2 of the 3 medicines lifts a farther pharmacy to the top.
    with httpx.Client(base_url=BASE, timeout=30) as c:
        login(c)
        for d in ("ozempic_05", "lisinopril_10"):
            assert c.post("/api/pharmacies/bmc-yawkey/stock-reports", json={"drug_id": d, "in_stock": True}).status_code == 200
    page.reload()
    top = page.locator(".mylist-card").first
    expect(top).to_contain_text("BMC", timeout=15000)
    expect(top).to_contain_text("Reported in stock for 2 of 3 of your medicines")
    assert page.evaluate("JSON.parse(localStorage.getItem('rxlantern.mylist')).length") == 3
    shot(page, "01_my_medicine_list.png")
    ctx.close()
    return "3 medicines added by typing; each card says 'Reported in stock for X of 3'; 2 real reports moved BMC Yawkey to #1 (2 of 3); list saved only in localStorage"


# ----------------------------------------------------------------------------- 2. prior authorization helper
@check(2, "A drug with prior authorization shows the prior authorization helper")
def t_pa(browser):
    ctx = new_ctx(browser, place="02124", insurance="masshealth")
    page = ctx.new_page()
    page.goto(f"{BASE}/results?drug=ozempic_05")
    card = page.locator(".pa-card")
    expect(card).to_be_visible(timeout=15000)
    for txt in ("Prior authorization", "must approve", "can't fill it under your insurance", "What to ask your doctor's office"):
        expect(card).to_contain_text(txt)
    card.scroll_into_view_if_needed()
    shot(page, "02_prior_authorization_helper.png")
    page.goto(f"{BASE}/results?drug=lisinopril_10")
    expect(page.locator(".summary-grid")).to_be_visible()
    page.wait_for_timeout(400)
    assert page.locator(".pa-card").count() == 0, "PA helper shown for a drug without PA"
    ctx.close()
    return "Ozempic + MassHealth (PA yes): helper explains PA, why the pharmacy can't fill it, and what to ask; lisinopril (no PA): no helper"


# ----------------------------------------------------------------------------- 3. transfer helper
@check(3, "'They don't have it' offers the transfer helper; Concerta shows only the prescriber/pharmacist line")
def t_transfer(browser):
    ctx = new_ctx(browser, place="02124")
    login(ctx.request)
    page = ctx.new_page()
    page.goto(f"{BASE}/results?drug=amoxicillin_500")
    card = page.locator(".result-card").first
    expect(card).to_be_visible(timeout=15000)
    name = card.locator("h3").inner_text()
    card.get_by_role("button", name="I called: They don't have it").click()
    modal = page.locator(".modal")
    expect(modal).to_contain_text("Ask another pharmacy to transfer your prescription", timeout=10000)
    expect(modal.locator(".script-box")).to_contain_text("Amoxicillin 500 mg capsule")
    expect(modal.locator(".script-box")).to_contain_text(name)
    expect(modal).to_contain_text("Have this ready")
    shot(page, "03_transfer_helper.png")
    page.keyboard.press("Escape")
    page.goto(f"{BASE}/results?drug=concerta_18")
    helper = page.locator(".script-card .transfer-helper")
    expect(helper).to_be_visible(timeout=15000)
    helper.locator("summary").click()
    expect(helper).to_contain_text("Ask your prescriber or pharmacist what to do for this medicine.")
    assert helper.locator(".script-box").count() == 0, "transfer script shown for a controlled medicine"
    shot(page, "03b_transfer_controlled.png")
    ctx.close()
    return f"after 'They don't have it' at {name}: transfer script with that pharmacy and the medicine; Concerta: only 'Ask your prescriber or pharmacist'"


# ----------------------------------------------------------------------------- 4. send it here + before you go
@check(4, "'Send it here' card and 'Before you go' checklist appear and print cleanly")
def t_send_here(browser):
    ctx = new_ctx(browser, place="02124")
    page = ctx.new_page()
    page.goto(f"{BASE}/results?drug=ozempic_05")
    expect(page.locator(".byg-card")).to_contain_text("Your insurance card", timeout=15000)
    expect(page.locator(".byg-card")).to_contain_text("photo ID")
    page.goto(f"{BASE}/pharmacies/cvs-2283")
    expect(page.locator(".byg-card")).to_contain_text("Pharmacy counter hours today")
    page.goto(f"{BASE}/results?drug=ozempic_05")
    card = page.locator(".result-card").first
    expect(card).to_be_visible(timeout=15000)
    name = card.locator("h3").inner_text()
    card.get_by_role("link", name=re.compile("Send it here")).click()
    page.wait_for_url(re.compile(r"/send-here/"))
    sh = page.locator(".send-here-card")
    expect(sh.locator(".sh-name")).to_have_text(name)
    expect(sh.locator(".sh-phone")).to_contain_text(re.compile(r"\(\d{3}\) \d{3}-\d{4}"))
    expect(page.locator(".byg-card")).to_contain_text("Ozempic (semaglutide) 0.5 mg pen")
    shot(page, "04_send_it_here.png")
    page.emulate_media(media="print")
    assert not page.locator(".site-header").is_visible() and not page.locator(".site-footer").is_visible()
    assert sh.is_visible() and page.locator(".byg-card").is_visible()
    text = page.locator("main").inner_text()
    assert "@" not in text and "ZIP" not in text and "02124" not in text, "personal information on the card"
    page.pdf(path=str(REPO / "output" / "send_here_sample.pdf"), format="Letter")
    page.emulate_media(media="screen")
    ctx.close()
    return "checklist on results and pharmacy pages; 'Send it here' card with exact name, address, phone; print view hides site chrome; no personal info; PDF saved to output/send_here_sample.pdf"


# ----------------------------------------------------------------------------- 5. crowdsourced languages
@check(5, "A review with 'Staff spoke Cantonese' shows as 'Reported by patients', and the language filter finds it")
def t_languages(browser):
    pid = "bmc-yawkey"
    ctx = new_ctx(browser, place="02118")
    login(ctx.request)
    page = ctx.new_page()
    page.goto(f"{BASE}/pharmacies/{pid}")
    page.get_by_role("button", name="Rate this pharmacy").first.click()
    modal = page.locator(".modal")
    modal.locator("label.star").nth(3).click()
    modal.locator("input[name=wait]").fill("15")
    modal.locator("select[name=visit_time]").select_option("morning")
    modal.locator("label.check", has_text="Cantonese").click()
    modal.locator("button[type=submit]").click()
    expect(page.locator(".toast")).to_contain_text("published", timeout=15000)
    page.reload()
    langs = page.locator(".reported-langs").first
    expect(langs).to_contain_text("Reported by patients")
    expect(langs).to_contain_text("Cantonese (1)")
    assert "Sample" not in langs.inner_text(), "real report shown as sample"
    langs.scroll_into_view_if_needed()
    shot(page, "05_languages_reported_by_patients.png")
    page.goto(f"{BASE}/pharmacies")
    page.locator("select").nth(1).select_option("Cantonese")
    expect(page.locator(".pharmacy-card", has_text="BMC Yawkey").first).to_be_visible()
    page.goto(f"{BASE}/results?drug=amoxicillin_500")
    page.select_option("select[name=language]", "Chinese (Cantonese)")
    expect(page.locator(f"#ph-{pid}")).to_be_visible()
    expect(page.locator(f"#ph-{pid} .reported-langs")).to_contain_text("Cantonese")
    ctx.close()
    return "review ticked Cantonese -> pharmacy page 'Reported by patients: Cantonese (1)' (not sample); Pharmacies and Results language filters include BMC Yawkey"


# ----------------------------------------------------------------------------- 6. language help card
@check(6, "The language help card prints in all four languages")
def t_language_card(browser):
    ctx = new_ctx(browser)
    page = ctx.new_page()
    page.goto(f"{BASE}/language-card")
    page.emulate_media(media="print")
    card = page.locator(".language-card")
    for lang, bit in (("zh-Hant", "語言"), ("zh-Hans", "语言"), ("ht", "Mwen bezwen èd"), ("es", "Necesito ayuda en mi idioma")):
        expect(card.locator(f".lc-text[lang={lang}]")).to_contain_text(bit)
    assert card.locator(".lc-english").count() == 4
    expect(card).to_contain_text("I need help in my language, please. Can someone help me or call an interpreter?")
    expect(card).to_contain_text("Translation not yet reviewed by a native speaker.")
    assert not page.locator(".site-header").is_visible()
    page.pdf(path=str(REPO / "output" / "language_card_sample.pdf"), format="Letter")
    page.emulate_media(media="screen")
    shot(page, "06_language_help_card.png", full=True)
    ctx.close()
    return "Chinese (Traditional and Simplified), Haitian Creole, Spanish, each with the English; warning label; print view; PDF saved to output/language_card_sample.pdf"


# ----------------------------------------------------------------------------- 7. best time to go
@check(7, "Best time to go appears only with at least 3 reviews in a time slot")
def t_best_time(browser):
    pid = "gary-drug"
    ctx = new_ctx(browser)
    page = ctx.new_page()
    waits = [10, 12, 14]
    for i, w in enumerate(waits, 1):
        with httpx.Client(base_url=BASE, timeout=30) as c:
            login(c, f"Tester {i}")
            r = c.post(f"/api/pharmacies/{pid}/reviews", json={"rating": 4, "wait_minutes": w, "visit_date": date.today().isoformat(),
                                                              "visit_time": "afternoon"})
            assert r.status_code == 200 and r.json()["status"] == "published", r.text
        page.goto(f"{BASE}/pharmacies/{pid}")
        box = page.locator(".best-time")
        expect(box).to_be_visible(timeout=15000)
        if i < 3:
            assert box.locator(".best-time-real").count() == 0, f"best time shown with only {i} reviews"
            expect(box).to_contain_text("Not enough reviews yet")
    day = datetime.now().strftime("%A")
    expect(page.locator(".best-time-real")).to_contain_text(f"{day}s, afternoons: about 12 minutes (3)")
    page.locator(".best-time").scroll_into_view_if_needed()
    shot(page, "07_best_time_to_go.png")
    page.goto(f"{BASE}/pharmacies/cvs-5874")
    expect(page.locator(".best-time-sample")).to_contain_text("mornings")
    ctx.close()
    return f"1 and 2 reviews: 'Not enough reviews yet'; 3rd review -> '{day}s, afternoons: about 12 minutes (3)'; sample slot shown with a Sample badge at CVS Chinatown"


# ----------------------------------------------------------------------------- 8. shortage watchlist
@check(8, "Starring a drug, then a new report, highlights it on the next visit")
def t_watchlist(browser):
    ctx = new_ctx(browser, place="02124")
    page = ctx.new_page()
    page.goto(f"{BASE}/shortages")
    card = page.locator(".drug-card", has_text="Amoxicillin 500 mg capsule")
    try:
        expect(card).to_be_visible(timeout=15000)
    except AssertionError:
        shot(page, "debug_watch.png", full=False)
        raise
    card.get_by_role("button", name=re.compile("^Watch")).click()
    expect(card.locator(".star-btn")).to_have_attribute("aria-pressed", "true")
    assert page.locator(".watch-card").count() == 0
    page.wait_for_timeout(1200)
    with httpx.Client(base_url=BASE, timeout=30) as c:
        login(c)
        assert c.post("/api/pharmacies/cvs-2283/stock-reports", json={"drug_id": "amoxicillin_500", "in_stock": True}).status_code == 200
    page.close()
    page = ctx.new_page()  # next visit: a new browser session (same browser, same saved star)
    page.goto(f"{BASE}/shortages")
    watch = page.locator(".watch-card")
    expect(watch).to_contain_text("Amoxicillin 500 mg capsule: reported in stock at CVS Pharmacy", timeout=15000)
    shot(page, "08_shortage_watchlist.png")
    page.goto(BASE)
    expect(page.locator(".watch-card")).to_be_visible()
    stored = page.evaluate("JSON.parse(localStorage.getItem('rxlantern.watch'))")
    assert stored["ids"] == ["amoxicillin_500"], stored
    page.close()
    page = ctx.new_page()  # the visit after that: nothing new
    page.goto(f"{BASE}/shortages")
    expect(page.locator(".drug-card").first).to_be_visible(timeout=15000)
    page.wait_for_timeout(800)
    assert page.locator(".watch-card").count() == 0, "old report highlighted again"
    ctx.close()
    return "star saved in localStorage only; new real 'in stock' report near 02124 highlighted on the next visit (a new browser session: shortage watch and home), not on the visit after"


# ----------------------------------------------------------------------------- 9. demand signals
def db_count(drug_id: str) -> int:
    con = sqlite3.connect(USER_DB)
    n = con.execute("SELECT COALESCE(SUM(count), 0) FROM search_counts WHERE drug_id = ?", (drug_id,)).fetchone()[0]
    con.close()
    return n


@check(9, "For pharmacies: counts of 5 or more shown, smaller hidden; test searches not counted")
def t_demand(browser):
    drug = "lisinopril_10"
    before = db_count(drug)
    with httpx.Client(base_url=BASE, timeout=30, headers=REAL_UA) as c:
        for _ in range(4):
            assert c.post("/api/search-count", json={"drug_id": drug, "place": "Dorchester"}).json()["counted"]
        rows = c.get("/api/demand").json()["rows"]
        assert not any(r["drug_id"] == drug for r in rows), "a count under 5 was shown"
        c.post("/api/search-count", json={"drug_id": drug, "place": "Dorchester"})
    ctx = new_ctx(browser, place="Dorchester")
    page = ctx.new_page()
    page.goto(f"{BASE}/results?drug={drug}")  # a test search in the browser
    expect(page.locator(".result-card").first).to_be_visible(timeout=15000)
    page.wait_for_timeout(800)
    assert db_count(drug) == before + 5, f"test search was counted ({db_count(drug)})"
    marked = httpx.post(f"{BASE}/api/search-count", json={"drug_id": drug, "place": "Dorchester"}, headers=REAL_UA | {"X-RxLantern-Test": "1"}).json()
    assert marked["counted"] is False
    page.goto(f"{BASE}/for-pharmacies")
    expect(page.locator("main")).to_contain_text(f"{before + 5} searches for Lisinopril 10 mg tablet near Dorchester")
    expect(page.locator("main")).to_contain_text("15 searches for Ozempic (semaglutide) 0.5 mg pen near Dorchester")
    assert "Cefdinir" not in page.locator("main").inner_text(), "a sample count under 5 was shown"
    shot(page, "09_for_pharmacies_demand.png", full=True)
    ctx.close()
    return "4 searches: hidden; 5th: '5 searches for Lisinopril 10 mg tablet near Dorchester'; headless-browser and marked test searches not counted; sample 3-count hidden"


# ----------------------------------------------------------------------------- 10. savings finder
@check(10, "Savings finder: links for no insurance and Blue Cross; only the note for Medicare and MassHealth; no TrumpRx for controlled")
def t_savings(browser):
    notes = []
    for ins, plan in (("uninsured", ""), ("commercial", "bcbs_ma")):
        ctx = new_ctx(browser, place="02124", insurance=ins, plan=plan)
        page = ctx.new_page()
        page.goto(f"{BASE}/results?drug=ozempic_05")
        card = page.locator(".savings-card")
        expect(card.locator("a.goodrx-link")).to_have_attribute("href", "https://www.goodrx.com/ozempic", timeout=15000)
        expect(card.locator("a.trumprx-link")).to_have_attribute("href", "https://trumprx.gov/p/ozempic")
        expect(card.locator("a.maker-link")).to_have_attribute("href", re.compile(r"^https://www\.ozempic\.com/"))
        expect(card).to_contain_text("Manufacturer copay cards generally can't be used with Medicare or MassHealth.")
        assert not re.search(r"\$\d", card.inner_text()), "a price was shown"
        if ins == "uninsured":
            card.scroll_into_view_if_needed()
            shot(page, "10_savings_finder.png")
        notes.append(ins)
        ctx.close()
    for ins in ("medicare", "masshealth"):
        ctx = new_ctx(browser, place="02124", insurance=ins)
        page = ctx.new_page()
        page.goto(f"{BASE}/results?drug=ozempic_05")
        card = page.locator(".savings-card")
        expect(card).to_contain_text("Discount cards and coupons usually mean paying cash", timeout=15000)
        assert card.locator("a").count() == 0, f"links shown for {ins}"
        notes.append(f"{ins}: note only")
        ctx.close()
    ctx = new_ctx(browser, place="02124", insurance="uninsured")
    page = ctx.new_page()
    page.goto(f"{BASE}/results?drug=vyvanse_30")
    card = page.locator(".savings-card")
    expect(card).to_contain_text("TrumpRx.gov does not list controlled medicines.", timeout=15000)
    assert card.locator("a.trumprx-link").count() == 0
    ctx.close()
    data = json.loads((REPO / "data" / "savings.json").read_text(encoding="utf-8"))
    controlled = {d["id"] for d in httpx.get(f"{BASE}/api/meta").json()["drugs"] if d["controlled"]}
    bad = [r["drug_id"] for r in data["drugs"] if r["drug_id"] in controlled and r["trumprx"]["listed"]]
    assert not bad, bad
    return "Ozempic, no insurance and Blue Cross: GoodRx, TrumpRx, and Novo Nordisk savings links (no prices); Medicare and MassHealth: note only; Vyvanse: no TrumpRx link; no controlled drug linked to TrumpRx"


# ----------------------------------------------------------------------------- 11. time saved
@check(11, "Time-saved counter goes up after a real chat question, not after tests or sample data")
def t_impact(browser):
    start = httpx.get(f"{BASE}/api/impact").json()["questions"]
    STATE["impact_start"] = start
    q = {"question": "Is there a pharmacy open right now near 02111?", "language": "en"}
    r = httpx.post(f"{BASE}/api/ask", json=q, headers=REAL_UA, timeout=180)
    assert r.status_code == 200 and r.json()["stop_reason"] == "completed", r.text[:200]
    after_real = httpx.get(f"{BASE}/api/impact").json()
    assert after_real["questions"] == start + 1, after_real
    assert after_real["patient_minutes"] == (start + 1) * 14 and after_real["staff_minutes"] == (start + 1) * 4
    ctx = new_ctx(browser)
    page = ctx.new_page()
    resp = page.request.post(f"{BASE}/api/ask", data=q, timeout=180000)  # headless browser = automated test
    assert resp.ok
    httpx.post(f"{BASE}/api/ask", json=q | {"question": "I took too many pills"}, headers=REAL_UA, timeout=60)  # emergency: no answer counted
    assert httpx.get(f"{BASE}/api/impact").json()["questions"] == start + 1, "a test question was counted"
    page.goto(BASE)
    expect(page.locator(".impact-line").first).to_contain_text(f"RxLantern has answered {start + 1} question")
    expect(page.locator(".impact-line .estimate-tag").first).to_have_text("Estimate")
    page.goto(f"{BASE}/about")
    expect(page.locator(".impact-card")).to_contain_text(f"saving patients an estimated {(start + 1) * 14} minutes")
    expect(page.locator(".impact-card")).to_contain_text("based on two measured calls")
    expect(page.locator(".impact-card")).to_contain_text(f"pharmacy staff an estimated {(start + 1) * 4} minutes")
    shot(page, "11_time_saved_about.png")
    ctx.close()
    return f"real question: {start} -> {start + 1} (14 patient min, 4 staff min each); headless-browser question and emergency message: not counted; home line and About card labeled 'Estimate'"


# ----------------------------------------------------------------------------- 12. Spanish, Easy view, phone
PAGES = [("/my-list", "Mi lista de medicinas", ".mylist-card"), ("/send-here/cvs-2283", "Por favor envíe mi receta a:", ".send-here-card"),
         ("/language-card", "Tarjeta de ayuda con el idioma", ".language-card"), ("/for-pharmacies", "Para farmacias", ".demand-list"),
         ("/results?drug=ozempic_05", "Autorización previa", ".pa-card"), ("/pharmacies/cvs-5874", "Mejor hora para ir", ".best-time")]


@check(12, "All new pages work in Spanish, in Easy view, and at phone width")
def t_spanish_easy_phone(browser):
    count = 0
    for viewport, easy, lang in ((DESKTOP, False, "es"), (DESKTOP, True, "en"), (PHONE, False, "en"), (PHONE, True, "es")):
        ctx = new_ctx(browser, viewport=viewport, lang=lang, easy=easy, place="02124", insurance="masshealth",
                      mylist=["ozempic_05", "lisinopril_10", "albuterol_hfa"])
        page = ctx.new_page()
        for path, es_text, sel in PAGES:
            page.goto(BASE + path)
            expect(page.locator(sel).first).to_be_visible(timeout=15000)
            if lang == "es":
                expect(page.locator("main")).to_contain_text(es_text)
            if easy:
                assert "easy" in (page.locator("body").get_attribute("class") or "")
            assert no_sideways(page), f"sideways scroll on {path} at {viewport['width']}px (easy={easy}, {lang})"
            expect(page.get_by_role("button", name=re.compile("Read this page aloud|Leer esta página")).first).to_be_visible()
            count += 1
        page.goto(f"{BASE}/my-list")
        expect(page.locator(".mylist-edit .mic").first).to_be_visible()
        if viewport is PHONE and easy:
            shot(page, "12_my_list_phone_easy_spanish.png")
        ctx.close()
    return f"{count} page views: 6 new pages x (Spanish desktop, Easy view, phone, phone + Easy view + Spanish); no sideways scroll; mic and read aloud present"


# ----------------------------------------------------------------------------- cleanup
def cleanup() -> dict:
    with httpx.Client(base_url=BASE) as c:
        for e in accounts:
            if c.post("/api/auth/login", json={"email": e, "password": PASSWORD}).status_code == 200:
                c.delete("/api/auth/account")
    # Only test accounts (@example.com) and their posts; counts go back to how they were before the run.
    return cleanup_util.restore(SNAP)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SHOTS.mkdir(parents=True, exist_ok=True)
    for old in SHOTS.glob("7c2_*.png"):
        old.unlink()
    assert httpx.get(f"{BASE}/api/health").status_code == 200, "start the app first: ..\\.venv\\Scripts\\python.exe run.py"
    pick = {int(a) for a in sys.argv[1:]}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for n, fn in enumerate((t_mylist, t_pa, t_transfer, t_send_here, t_languages, t_language_card, t_best_time,
                                t_watchlist, t_demand, t_savings, t_impact, t_spanish_easy_phone), 1):
            if not pick or n in pick:
                fn(browser)
        browser.close()
    counts = cleanup()
    passed = sum(r["result"] == "PASS" for r in results)
    out = {"run_at": datetime.now().isoformat(timespec="seconds"), "base_url": BASE, "browser": "Chromium (Playwright)",
           "passed": passed, "failed": len(results) - passed, "checks": results,
           "cleanup": {"test_accounts_created": len(accounts), "rows_left_in_user_db": counts},
           "screenshots": sorted(p.name for p in SHOTS.glob("7c2_*.png"))}
    RESULTS.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n{passed}/{len(results)} passed. Rows left in user DB: {counts}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
