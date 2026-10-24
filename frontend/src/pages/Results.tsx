// The results page: one medicine, nearby pharmacies, shortage status, coverage, insurance contacts, community posts.
// Built from the database and our own tools only (no AI). Distances are measured in the browser.
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useApp } from "../state";
import { api, type Results as ResultsData, type ResultPharmacy } from "../api";
import { useOrigin } from "../origin";
import { MapView } from "../components/MapView";
import {
  CallModal, CallScriptCard, OpenBadge, ReadAloud, ReportButtons, SampleBadge, ShortageBadge, SourceLink,
  ago, directionsHref, miles, telHref,
} from "../components/Bits";
import { cardCost, coverageLines, nadacLine } from "../coverage";
import { shortageKey } from "../i18n";
import { BeforeYouGo, PriorAuthCard, ReportedLanguages, SavingsFinder, SendHereLink, StarButton, speaks } from "../components/Journey";

type Sort = "distance" | "open" | "latest" | "rating" | "wait";
interface Row extends ResultPharmacy { dist: number | null }

const LANGUAGES = ["Spanish", "Chinese (Cantonese)", "Chinese (Mandarin)", "Haitian Creole", "Vietnamese", "Portuguese", "Cape Verdean Creole"];

export function useResults() {
  const { lang, insurance, plan, version } = useApp();
  const [params] = useSearchParams();
  const drug = params.get("drug") ?? "";
  const at = params.get("at");
  const [data, setData] = useState<ResultsData | null>(null);
  const [error, setError] = useState("");
  const load = useCallback(() => {
    if (!drug) return;
    setError("");
    const q = new URLSearchParams({ drug_id: drug, insurance, plan, lang });
    if (at) q.set("at", at);
    api.get<ResultsData>(`/api/results?${q}`).then(setData).catch((e) => setError(e?.message || "error"));
  }, [drug, insurance, plan, lang, at]);
  useEffect(load, [load, version]);
  return { drug, data, error, reload: load };
}

/** Demand signals: count this search once per browser session (drug + typed ZIP or neighborhood + week).
 *  Never sent for "Use my location". The server ignores automated tests. */
function useSearchCount(drugId: string | undefined) {
  const { place, deviceOrigin } = useApp();
  useEffect(() => {
    const where = place.trim();
    if (!drugId || !where || deviceOrigin) return;
    const key = `rxlantern.counted.${drugId}.${where.toLowerCase()}`;
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, "1");
    api.post("/api/search-count", { drug_id: drugId, place: where }).catch(() => undefined);
  }, [drugId, place, deviceOrigin]);
}

export function withDistance(data: ResultsData | null, origin: { lat: number; lon: number } | null): Row[] {
  return (data?.pharmacies ?? []).map((p) => ({
    ...p, dist: origin ? Math.round(miles(origin, { lat: p.latitude, lon: p.longitude }) * 10) / 10 : null,
  }));
}

function sortRows(rows: Row[], sort: Sort): Row[] {
  const byDist = (a: Row, b: Row) => (a.dist ?? 99) - (b.dist ?? 99);
  const cmp: Record<Sort, (a: Row, b: Row) => number> = {
    distance: byDist,
    open: (a, b) => Number(b.open_now === true) - Number(a.open_now === true) || byDist(a, b),
    latest: (a, b) => (b.closes_latest_minutes ?? -2) - (a.closes_latest_minutes ?? -2) || byDist(a, b),
    rating: (a, b) => (b.reviews.average_rating ?? -1) - (a.reviews.average_rating ?? -1) || byDist(a, b),
    wait: (a, b) => (a.reviews.average_wait_minutes ?? 9999) - (b.reviews.average_wait_minutes ?? 9999) || byDist(a, b),
  };
  return [...rows].sort(cmp[sort]);
}

function Reports({ p, reminder }: { p: Row; reminder: string }) {
  const { t, lang } = useApp();
  const r = p.reports, s = p.sample_report;
  return (
    <div className="card-section reports-box">
      <p className="section-label">{t("reportsTitle")}</p>
      {!r && !s && <p className="muted">{t("noReportsYet")}</p>}
      {r && (
        <p className="report-line">
          <span className="stock-in">{t("inStockCount", { n: r.in_stock_reports })}</span> · <span className="stock-out">{t("outStockCount", { n: r.out_of_stock_reports })}</span>
          <span className="muted"> · {t("latest", { time: ago(r.latest_report, lang) })}</span>
          {r.conflicting && <span className="warn-text"> {t("conflicting")}</span>}
        </p>
      )}
      {s && (
        <p className="report-line sample-line">
          <SampleBadge /> {t("inStockCount", { n: s.in_stock_reports })} · {t("outStockCount", { n: s.out_of_stock_reports })}
          <span className="muted"> · {t("latest", { time: ago(s.latest_report, lang) })}</span>
        </p>
      )}
      <p className="reminder">{reminder === "Call to confirm before you go." ? t("callToConfirm") : reminder}</p>
    </div>
  );
}

function ReviewLine({ p }: { p: Row }) {
  const { t } = useApp();
  const r = p.reviews;
  return (
    <p className="small">
      {r.average_rating != null
        ? <><span aria-hidden="true">★</span> {t("avgRating", { r: r.average_rating })}{r.average_wait_minutes != null && ` · ${t("avgWait", { m: r.average_wait_minutes })}`} ({r.reviews})</>
        : r.reviews > 0 ? t("fewReviews", { n: r.reviews }) : t("noReviewsYet")}
      {p.sample_reviews > 0 && <> · <SampleBadge /> <Link to={`/pharmacies/${p.id}`}>{t("sampleReviews", { n: p.sample_reviews })}</Link></>}
    </p>
  );
}

function ResultCard({ p, data, alternative, onCall, highlight }: {
  p: Row; data: ResultsData; alternative: Row | null; onCall: (p: Row) => void; highlight: boolean;
}) {
  const { t, rate } = useApp();
  const controlled = data.drug.controlled;
  const plan = data.plan;
  return (
    <article className={`card result-card ${highlight ? "highlight" : ""}`} id={`ph-${p.id}`} tabIndex={-1} aria-labelledby={`ph-name-${p.id}`}>
      <div className="card-top">
        <h3 id={`ph-name-${p.id}`}><Link to={`/pharmacies/${p.id}`}>{p.name}</Link></h3>
        <OpenBadge open={p.open_now} opensNext={p.opens_next} status={p.status} />
      </div>
      <p className="address">{p.address}{p.dist != null && <span className="muted"> · {t("away", { miles: p.dist })}</span>}</p>
      <p className="hours-line">
        {p.open_now && p.closes_at && <strong>{t(p.closes_for === "lunch break" ? "closesLunch" : "closesAt", { time: p.closes_at })}. </strong>}
        <span>{t("counterToday", { hours: p.counter_today === "closed" ? t("closed") : p.counter_today })}</span>
      </p>
      {p.open_now === false && alternative && (
        <p className="alt-line"><span aria-hidden="true">➜</span> {t("openAlternative")}{" "}
          <a href={`#ph-${alternative.id}`} onClick={(e) => { e.preventDefault(); document.getElementById(`ph-${alternative.id}`)?.focus(); document.getElementById(`ph-${alternative.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" }); }}>
            {alternative.name}, {alternative.address.split(",")[0]}</a>
          {alternative.dist != null && ` (${t("away", { miles: alternative.dist })})`}</p>
      )}
      <details className="store-hours">
        <summary>{t("storeHours")}</summary>
        <p className="small">{t("storeToday", { hours: p.store_today })}</p>
      </details>

      {!controlled && <Reports p={p} reminder={data.reminder} />}

      <div className="card-section">
        <p className="section-label">{t("costOnCard")} <span className="estimate-tag">{t("estimateLabel")}</span></p>
        <p className="small">{cardCost(data.coverage, t)}</p>
      </div>
      {plan && (
        <div className="card-section">
          <p className="small">
            {plan.pharmacy_finder_url !== "not found"
              ? <a href={plan.pharmacy_finder_url} target="_blank" rel="noreferrer">{t("planFinder")} ({plan.name})</a>
              : <span className="muted">{t("planFinderNotFound")}</span>}
            {" · "}<strong>{t("confirmInsurance")}</strong>
          </p>
        </div>
      )}
      <p className="small">{p.delivery === "yes" ? `${t("deliveryYes")}${p.delivery_summary ? ` — ${p.delivery_summary}` : ""}` : t("deliveryNotFound")}</p>
      <ReviewLine p={p} />

      <div className="card-actions">
        <button type="button" className="btn primary" onClick={() => onCall(p)}><span aria-hidden="true">📞</span> {t("call")}</button>
        <a className="btn ghost" href={directionsHref(p.address)} target="_blank" rel="noreferrer">{t("directions")}</a>
        <Link className="btn ghost" to={`/pharmacies/${p.id}`}>{t("details")}</Link>
        <SendHereLink pharmacyId={p.id} drugId={data.drug.id} />
      </div>
      <ReportedLanguages real={p.reported_languages} sample={p.sample_reported_languages} compact />
      <ReportButtons pharmacyId={p.id} drugId={data.drug.id} controlled={controlled} compact />
      <button type="button" className="btn ghost rate-btn" onClick={() => rate(p.id)}><span aria-hidden="true">★</span> {t("ratePharmacy")}</button>
    </article>
  );
}

function Summary({ data }: { data: ResultsData }) {
  const { t, lang } = useApp();
  const sh = data.shortage, plan = data.plan;
  const lines = coverageLines(data.coverage, plan, t);
  return (
    <div className="summary-grid">
      <section className="card summary-card" aria-labelledby="sum-short">
        <h2 id="sum-short" className="h3">{t("shortageTitle")}</h2>
        <ShortageBadge status={sh.status} />
        <p className="small">{sh.fda_estimate ? t("fdaEstimate", { text: sh.fda_estimate }) : t("fdaNoEstimate")}</p>
        {sh.fda_updated && <p className="small muted">{t("fdaUpdated", { date: sh.fda_updated })}</p>}
        <p className="src muted">FDA · {t("checked", { date: sh.checked_date })} · <SourceLink url={sh.source} /></p>
      </section>
      <section className="card summary-card" aria-labelledby="sum-cov">
        <h2 id="sum-cov" className="h3">{t("coverageTitle")} <span className="estimate-tag">{t("estimateLabel")}</span></h2>
        <ul className="plain-list">{lines.map((l) => <li key={l}>{l}</li>)}</ul>
        <p className="small">{nadacLine(data.coverage, t)}</p>
        <p className="src muted">
          {data.coverage.masshealth && <>MassHealth · {t("checked", { date: data.coverage.masshealth.checked_date })} · <SourceLink url={data.coverage.masshealth.source} /> · </>}
          {data.coverage.medicare && <>CMS · {t("checked", { date: data.coverage.medicare.checked_date })} · <SourceLink url={data.coverage.medicare.rules_source} /> · </>}
          NADAC {data.coverage.nadac.as_of} · <SourceLink url={data.coverage.nadac.source} />
        </p>
      </section>
      <section className="card summary-card" aria-labelledby="sum-ins">
        <h2 id="sum-ins" className="h3">{t("insuranceTitle")}</h2>
        {plan ? (
          <>
            <p><strong>{plan.name}</strong></p>
            {plan.pharmacy_finder_url !== "not found"
              ? <p><a className="btn ghost" href={plan.pharmacy_finder_url} target="_blank" rel="noreferrer">{t("planFinder")} ↗</a></p>
              : <p className="small">{t("planFinderNotFound")} {plan.finder_note}</p>}
            {plan.member_services_phone !== "not found"
              ? <p><a className="btn" href={telHref(plan.member_services_phone)}><span aria-hidden="true">📞</span> {t("callInsurance", { phone: plan.member_services_phone })}</a></p>
              : <p className="small">{t("callInsuranceNotFound")}</p>}
            {plan.phone_note && <p className="small muted">{plan.phone_note}</p>}
            <p className="src muted">{t("checked", { date: plan.checked_date })}{plan.source_url !== "not found" && <> · <SourceLink url={plan.source_url.split(" ; ")[0]} /></>}</p>
          </>
        ) : <p className="small">{t("noInsuranceChosen")} <Link to="/">{t("newSearch")}</Link></p>}
      </section>
      {lang === "es" && <p className="small muted span-all">{t("dataEnglishNote")}</p>}
    </div>
  );
}

export function Results() {
  const { t, lang, insurance, easy } = useApp();
  const nav = useNavigate();
  const { drug, data, error, reload } = useResults();
  const { origin } = useOrigin();
  const [sort, setSort] = useState<Sort>("distance");
  const [openOnly, setOpenOnly] = useState(false);
  const [delivery, setDelivery] = useState(false);
  const [language, setLanguage] = useState("");
  const [calling, setCalling] = useState<Row | null>(null);
  const [highlight, setHighlight] = useState("");
  const [showAll, setShowAll] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  const rows = useMemo(() => withDistance(data, origin), [data, origin]);
  useSearchCount(data?.drug.id);
  const shown = useMemo(() => sortRows(rows.filter((p) =>
    (!openOnly || p.open_now === true) && (!delivery || p.delivery === "yes") &&
    (!language || speaks(p, language))), sort),
  [rows, openOnly, delivery, language, sort]);
  const openRows = useMemo(() => sortRows(rows.filter((p) => p.open_now === true), "distance"), [rows]);
  const select = useCallback((id: string) => {
    setHighlight(id);
    setShowAll(true);
    setTimeout(() => {
      const card = document.getElementById(`ph-${id}`);
      card?.scrollIntoView({ behavior: "smooth", block: "center" });
      card?.focus({ preventScroll: true });
    }, 50);
  }, []);

  if (!drug) return <div className="card"><p>{t("needDrug")}</p><Link className="btn primary" to="/">{t("newSearch")}</Link></div>;
  if (error) return <div className="card"><p className="alert" role="alert">{error === "error" ? t("errorGeneric") : error}</p><button type="button" className="btn" onClick={reload}>{t("tryAgain")}</button> <Link className="btn ghost" to="/">{t("newSearch")}</Link></div>;
  if (!data) return <div className="card loading-card" role="status"><span className="lantern-dot" aria-hidden="true" /> {t("loading")}</div>;

  const placeLabel = origin ? (origin.fromDevice ? t("yourLocation") : origin.label) : null;
  const unlisted = !!language && shown.length === 0;
  const insLabel = insurance ? (insurance === "commercial" ? data.plan?.name ?? t("ins_commercial") : t(`ins_${insurance}` as never)) : t("insUnsure");
  const clear = () => { setOpenOnly(false); setDelivery(false); setLanguage(""); };

  return (
    <div className="results-page">
      <Link to="/" className="back">← {t("newSearch")}</Link>
      <header className="results-head">
        <div>
          <h1>{t("resultsTitle", { drug: data.drug.name })}</h1>
          <p className="lead">
            {placeLabel ? t("resultsNear", { place: placeLabel }) : t("noPlaceYet")}
            {" · "}{t("changeInsurance")} <strong>{insLabel}</strong> <Link to="/">({t("changeDrug")})</Link>
          </p>
        </div>
        <div className="head-actions">
          <ReadAloud text={() => [data.drug.name, t(shortageKey(data.shortage.status)), ...coverageLines(data.coverage, data.plan, t),
            ...shown.slice(0, 3).map((p) => `${p.name}, ${p.address}. ${p.open_now ? t("openNow") : p.opens_next ? t("closedOpens", { when: p.opens_next }) : t("closed")}`)].join(". ")} />
          <button type="button" className="btn ghost" onClick={() => nav(`/print?drug=${data.drug.id}`)}><span aria-hidden="true">🖨</span> {t("printShare")}</button>
          <StarButton drugId={data.drug.id} name={data.drug.name} />
        </div>
      </header>

      <Summary data={data} />
      <PriorAuthCard coverage={data.coverage} />
      <SavingsFinder drugId={data.drug.id} />
      <BeforeYouGo drugName={data.drug.name} />

      {data.holidays.map((h) => (
        <p key={h.date} className="notice" role="note"><span aria-hidden="true">📅</span> {t("holidayNotice", { name: lang === "es" ? h.name_es : h.name, date: h.date })}</p>
      ))}

      {data.drug.controlled && (
        <div className="notice controlled-note" role="note">
          <h2 className="h3">{t("controlledTitle")}</h2>
          <p>{t("controlledExplain")}</p>
        </div>
      )}

      <CallScriptCard text={data.call_script} drugId={data.drug.id} controlled={data.drug.controlled} />

      <section className="card toolbar" aria-label={t("filters")}>
        <label className="sort">{t("sortBy")}
          <select value={sort} onChange={(e) => setSort(e.target.value as Sort)} name="sort">
            <option value="distance">{t("sortDistance")}</option>
            <option value="open">{t("sortOpen")}</option>
            <option value="latest">{t("sortLatest")}</option>
            <option value="rating">{t("sortRating")}</option>
            <option value="wait">{t("sortWait")}</option>
          </select>
        </label>
        <fieldset className="filter-set">
          <legend>{t("filters")}</legend>
          <label className="check"><input type="checkbox" name="open" checked={openOnly} onChange={(e) => setOpenOnly(e.target.checked)} /> {t("fOpenNow")}</label>
          <label className="check"><input type="checkbox" name="delivery" checked={delivery} onChange={(e) => setDelivery(e.target.checked)} /> {t("fDelivery")}</label>
          <label className="lang-filter">{t("fLanguage")}
            <select value={language} onChange={(e) => setLanguage(e.target.value)} name="language">
              <option value="">{t("fAnyLanguage")}</option>
              {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </label>
        </fieldset>
        <p className="count" role="status" aria-live="polite">{t("countShown", { n: shown.length })}</p>
      </section>

      <div className={`split ${easy ? "one" : ""}`}>
        <div className="result-list" ref={listRef}>
          {shown.length === 0 && (
            <div className="card empty">
              <p>{unlisted ? t("notListedNote") : t("noResults")}</p>
              <button type="button" className="btn" onClick={clear}>{t("clearFilters")}</button>
            </div>
          )}
          {(showAll ? shown : shown.slice(0, 8)).map((p) => (
            <ResultCard key={p.id} p={p} data={data} highlight={highlight === p.id} onCall={setCalling}
              alternative={p.open_now === false ? openRows.find((o) => o.id !== p.id) ?? null : null} />
          ))}
          {!showAll && shown.length > 8 && (
            <button type="button" className="btn ghost big show-all" onClick={() => setShowAll(true)}>{t("showAll", { n: shown.length })}</button>
          )}
        </div>
        <div className="map-wrap">
          <MapView points={shown} label={t("mapLabel")} onSelect={select} origin={origin} originLabel={t("youAreHere")} />
        </div>
      </div>

      {calling && (
        <CallModal name={calling.name} phone={calling.phone} script={data.call_script} pharmacyId={calling.id}
          drugId={data.drug.id} controlled={data.drug.controlled} onClose={() => setCalling(null)} />
      )}
    </div>
  );
}
