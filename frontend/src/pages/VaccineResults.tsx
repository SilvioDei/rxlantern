// Vaccine results: one vaccine near the patient's place, like the medicine results page. Pharmacies that list it
// (on their own page, or on their chain's vaccine page: call to confirm), open now, booking link, a Call button with a
// short vaccine call script, and who pays for the chosen insurance. No stock-report buttons for vaccines.
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";
import { useOrigin } from "../origin";
import { MapView } from "../components/MapView";
import { CallModal, OpenBadge, ReadAloud, SampleBadge, SourceLink, directionsHref, miles, telHref } from "../components/Bits";
import { BeforeYouGo, ReportedLanguages, SendHereLink } from "../components/Journey";

interface Detail { coverage: string; cost: string; source: string; part?: string }
interface VaxPharmacy {
  id: string; name: string; address: string; phone: string; latitude: number; longitude: number; neighborhood: string;
  open_now: boolean | null; status: string; closes_at: string | null; closes_for: string | null; opens_next: string | null;
  counter_today: string; offer: "store" | "chain" | "not_listed"; offer_source: string; offer_checked_date: string;
  offer_chain: string | null; booking_url: string; sample_reviews: number;
  reviews: { reviews: number; average_rating: number | null; average_wait_minutes: number | null };
  reported_languages?: Record<string, number>; sample_reported_languages?: Record<string, number>;
}
interface VaxData {
  vaccine: { id: string; name: string; group: string; notes: string[]; certified_sites_only: boolean; clinic_finder: string | null; checked_date: string };
  details: { medicare: Detail; masshealth: Detail & { dph_rule?: { says: string; source: string } };
    commercial: Detail & { massachusetts: { rule: string; coverage: string; cost: string; patient_message: string;
      applies_to?: string; sources: string[]; verification: string } } };
  insurance: string;
  plan: { name: string; pharmacy_finder_url: string; member_services_phone: string; checked_date: string } | null;
  call_script: string;
  chain_note: { chain: string; says: string; source: string; checked_date: string } | null;
  holidays: { date: string; name: string; name_es: string }[];
  pharmacies: VaxPharmacy[];
}
interface Row extends VaxPharmacy { dist: number | null }

function Coverage({ data }: { data: VaxData }) {
  const { t, lang, insurance } = useApp();
  const v = data.vaccine, d = data.details, ma = d.commercial.massachusetts;
  const travel = v.group === "travel";
  const show = (k: string) => !insurance || insurance === k;
  const plan = data.plan;
  return (
    <section className="card vax-coverage" aria-labelledby="vax-pay">
      <h2 id="vax-pay" className="h3">{t("vaxWhoPays")} <span className="estimate-tag">{t("estimateLabel")}</span></h2>
      {!insurance && <p className="small muted">{t("vaxAllIns")}</p>}
      {travel && <p className="notice"><strong>{t("travelCheck")}</strong></p>}
      <dl className="coverage">
        {show("medicare") && (<>
          <dt>{t("medicare")} {d.medicare.part && d.medicare.part !== "not found" && `(Part ${d.medicare.part})`}</dt>
          <dd className="cov-medicare">{d.medicare.coverage} {d.medicare.cost} <SourceLink url={d.medicare.source} /></dd>
        </>)}
        {show("masshealth") && (<>
          <dt>{t("masshealth")}</dt>
          <dd className="cov-masshealth">{d.masshealth.coverage} {d.masshealth.cost} <SourceLink url={d.masshealth.source} />
            {d.masshealth.dph_rule && <> {d.masshealth.dph_rule.says} <SourceLink url={d.masshealth.dph_rule.source} /></>}</dd>
        </>)}
        {show("commercial") && (<>
          <dt>{plan && insurance === "commercial" ? plan.name : t("commercial")}{!travel && ` — ${t("maRule")}`}</dt>
          <dd className="cov-commercial">{travel ? <>{t("travelCheck")} {ma.coverage}</>
            : <><strong>{ma.rule}.</strong> {ma.coverage} {ma.cost}</>}
            {" "}{ma.sources?.[0] && <SourceLink url={ma.sources[0]} />} <span className="muted small">({ma.verification})</span></dd>
          {!travel && (<><dt>{t("employerWarning")}</dt><dd className="warn-text employer-warning">{ma.patient_message}</dd></>)}
        </>)}
        {show("uninsured") && (<><dt>{t("uninsured")}</dt><dd className="cov-uninsured">{t("uninsuredVaccine")}</dd></>)}
      </dl>
      {plan && insurance === "commercial" && (
        <p className="small">
          {plan.pharmacy_finder_url !== "not found" && <><a href={plan.pharmacy_finder_url} target="_blank" rel="noreferrer">{t("planFinder")} ↗</a> · </>}
          {plan.member_services_phone !== "not found" && <a href={telHref(plan.member_services_phone)}>{t("callInsurance", { phone: plan.member_services_phone })}</a>}
        </p>
      )}
      <p className="small">{t("vaxRulesWarning")}</p>
      <p className="src muted">{t("checked", { date: v.checked_date })}</p>
      {lang === "es" && <p className="small muted">{t("dataEnglishNote")}</p>}
    </section>
  );
}

function VaxCard({ p, data, onCall }: { p: Row; data: VaxData; onCall: (p: Row) => void }) {
  const { t, rate } = useApp();
  const r = p.reviews;
  return (
    <article className="card result-card vax-card" id={`ph-${p.id}`} tabIndex={-1} aria-labelledby={`ph-name-${p.id}`}>
      <div className="card-top">
        <h3 id={`ph-name-${p.id}`}><Link to={`/pharmacies/${p.id}`}>{p.name}</Link></h3>
        <OpenBadge open={p.open_now} opensNext={p.opens_next} status={p.status} />
      </div>
      <p className="address">{p.address}{p.dist != null && <span className="muted"> · {t("away", { miles: p.dist })}</span>}</p>
      <p className="hours-line">
        {p.open_now && p.closes_at && <strong>{t(p.closes_for === "lunch break" ? "closesLunch" : "closesAt", { time: p.closes_at })}. </strong>}
        <span>{t("counterToday", { hours: p.counter_today === "closed" ? t("closed") : p.counter_today })}</span>
      </p>
      <p className={`small vax-listed vax-${p.offer}`}>
        <span aria-hidden="true">💉</span>{" "}
        {p.offer === "store" ? t("vaxListedStore") : p.offer === "chain" ? t("vaxListedChain", { chain: p.offer_chain ?? "" }) : t("vaxNotListed")}
        {" "}<SourceLink url={p.offer_source} /> <span className="muted">· {t("checked", { date: p.offer_checked_date })}</span>
      </p>
      <p className="small">
        {r.average_rating != null
          ? <><span aria-hidden="true">★</span> {t("avgRating", { r: r.average_rating })}{r.average_wait_minutes != null && ` · ${t("avgWait", { m: r.average_wait_minutes })}`} ({r.reviews})</>
          : r.reviews > 0 ? t("fewReviews", { n: r.reviews }) : t("noReviewsYet")}
        {p.sample_reviews > 0 && <> · <SampleBadge /> <Link to={`/pharmacies/${p.id}`}>{t("sampleReviews", { n: p.sample_reviews })}</Link></>}
      </p>
      <div className="card-actions">
        <button type="button" className="btn primary" onClick={() => onCall(p)}><span aria-hidden="true">📞</span> {t("call")}</button>
        {p.booking_url && p.booking_url !== "not found" && p.offer !== "not_listed" &&
          <a className="btn ghost book-btn" href={p.booking_url} target="_blank" rel="noreferrer">{t("bookVaccine")} ↗</a>}
        <a className="btn ghost" href={directionsHref(p.address)} target="_blank" rel="noreferrer">{t("directions")}</a>
        <SendHereLink pharmacyId={p.id} vaccineId={data.vaccine.id} />
      </div>
      <ReportedLanguages real={p.reported_languages} sample={p.sample_reported_languages} compact />
      <button type="button" className="btn ghost rate-btn" onClick={() => rate(p.id)}><span aria-hidden="true">★</span> {t("ratePharmacy")}</button>
    </article>
  );
}

export function VaccineResults() {
  const { t, lang, insurance, plan, version, easy } = useApp();
  const [params] = useSearchParams();
  const id = params.get("vaccine") ?? "";
  const at = params.get("at");
  const { origin } = useOrigin();
  const [data, setData] = useState<VaxData | null>(null);
  const [error, setError] = useState("");
  const [openOnly, setOpenOnly] = useState(false);
  const [calling, setCalling] = useState<Row | null>(null);
  const load = useCallback(() => {
    if (!id) return;
    setError("");
    const q = new URLSearchParams({ vaccine_id: id, insurance, plan, lang });
    if (at) q.set("at", at);
    api.get<VaxData>(`/api/vaccine-results?${q}`).then(setData).catch((e) => setError(e?.message || "error"));
  }, [id, insurance, plan, lang, at]);
  useEffect(load, [load, version]);

  const rows: Row[] = useMemo(() => (data?.pharmacies ?? []).map((p) => ({
    ...p, dist: origin ? Math.round(miles(origin, { lat: p.latitude, lon: p.longitude }) * 10) / 10 : null,
  })).sort((a, b) => (a.dist ?? 99) - (b.dist ?? 99)), [data, origin]);
  const offered = rows.filter((p) => p.offer !== "not_listed" && (!openOnly || p.open_now === true));
  const others = rows.filter((p) => p.offer === "not_listed");

  if (!id) return <div className="card"><p>{t("needDrug")}</p><Link className="btn primary" to="/">{t("newSearch")}</Link></div>;
  if (error) return <div className="card"><p className="alert" role="alert">{error === "error" ? t("errorGeneric") : error}</p><button type="button" className="btn" onClick={load}>{t("tryAgain")}</button> <Link className="btn ghost" to="/">{t("newSearch")}</Link></div>;
  if (!data) return <div className="card loading-card" role="status"><span className="lantern-dot" aria-hidden="true" /> {t("loading")}</div>;

  const v = data.vaccine;
  const placeLabel = origin ? (origin.fromDevice ? t("yourLocation") : origin.label) : null;
  const insLabel = insurance ? (insurance === "commercial" ? data.plan?.name ?? t("ins_commercial") : t(`ins_${insurance}` as never)) : t("insUnsure");

  return (
    <div className="results-page vaccine-results">
      <Link to="/" className="back">← {t("newSearch")}</Link>
      <header className="results-head">
        <div>
          <h1>{t("vaxResultsTitle", { vaccine: v.name })}</h1>
          <p className="lead">
            {placeLabel ? t("resultsNear", { place: placeLabel }) : t("noPlaceYet")}
            {" · "}{t("changeInsurance")} <strong>{insLabel}</strong> <Link to="/">({t("changeDrug")})</Link>
          </p>
        </div>
        <div className="head-actions">
          <ReadAloud text={() => [t("vaxResultsTitle", { vaccine: v.name }),
            ...offered.slice(0, 3).map((p) => `${p.name}, ${p.address}. ${p.open_now ? t("openNow") : p.opens_next ? t("closedOpens", { when: p.opens_next }) : t("closed")}`)].join(". ")} />
        </div>
      </header>

      {v.certified_sites_only && (
        <p className="alert yellow-fever-alert"><strong>{t("yellowFever")}</strong>{" "}
          {v.clinic_finder && <a href={v.clinic_finder} target="_blank" rel="noreferrer">{t("findClinic")} ↗</a>}</p>
      )}

      <div className="summary-grid vax-summary">
        <Coverage data={data} />
        <section className="card script-card" aria-labelledby="vax-script">
          <h2 id="vax-script" className="h3">{t("callScriptTitle")}</h2>
          <p className="script-text">{data.call_script}</p>
          <div className="card-actions"><ReadAloud text={data.call_script} /></div>
          <p className="small muted">{t("vaxNoReports")}</p>
        </section>
      </div>
      <BeforeYouGo vaccineName={v.name} />

      {data.holidays.map((h) => (
        <p key={h.date} className="notice" role="note"><span aria-hidden="true">📅</span> {t("holidayNotice", { name: lang === "es" ? h.name_es : h.name, date: h.date })}</p>
      ))}

      <section className="card toolbar" aria-label={t("filters")}>
        <label className="check"><input type="checkbox" name="open" checked={openOnly} onChange={(e) => setOpenOnly(e.target.checked)} /> {t("fOpenNow")}</label>
        <p className="count" role="status" aria-live="polite">{t("vaxOfferCount", { n: offered.length })}</p>
        {data.chain_note && <p className="small muted span-all">{t("vaxChainNote", { chain: data.chain_note.chain })} “{data.chain_note.says}” <SourceLink url={data.chain_note.source} /> · {t("checked", { date: data.chain_note.checked_date })}</p>}
      </section>

      <div className={`split ${easy ? "one" : ""}`}>
        <div className="result-list">
          {offered.length === 0 && <div className="card empty"><p>{t("noneListed")}</p></div>}
          {offered.map((p) => <VaxCard key={p.id} p={p} data={data} onCall={setCalling} />)}
          {others.length > 0 && (
            <details className="card vax-others">
              <summary>{t("vaxNotListedTitle", { n: others.length })}</summary>
              <ul className="feed">
                {others.map((p) => (
                  <li key={p.id} className="feed-item">
                    <Link to={`/pharmacies/${p.id}`}><strong>{p.name}</strong></Link> — {p.address}
                    {p.dist != null && <span className="muted"> · {t("away", { miles: p.dist })}</span>}
                    <div className="card-actions">
                      <button type="button" className="btn ghost" onClick={() => setCalling(p)}><span aria-hidden="true">📞</span> {t("call")}</button>
                    </div>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
        <div className="map-wrap">
          <MapView points={offered} label={t("mapLabel")} onSelect={(pid) => document.getElementById(`ph-${pid}`)?.scrollIntoView({ behavior: "smooth", block: "center" })}
            origin={origin} originLabel={t("youAreHere")} />
        </div>
      </div>

      {calling && (
        <CallModal name={calling.name} phone={calling.phone} script={data.call_script} pharmacyId={calling.id}
          drugId={null} controlled onClose={() => setCalling(null)} />
      )}
    </div>
  );
}
