// One pharmacy: counter hours and store hours side by side (counter first), lunch, weekend and holiday notes,
// delivery, services, vaccines with booking link, nearby clinics, call script, community reports, and reviews.
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useApp } from "../state";
import { BeforeYouGo, ReportedLanguages, SendHereLink, langName } from "../components/Journey";
import type { PharmacyInsights } from "../api";
import { api, type Holiday, type PharmacyBrief, type ReportCounts, type Review, type ReviewSummary, type StockSummary } from "../api";
import { CallScriptCard, NotFoundText, OpenBadge, ReadAloud, SampleBadge, Stars, ago, directionsHref, telHref } from "../components/Bits";
import { DAY_NAMES } from "../i18n";

interface Details {
  name: string; address: string; phone: string; type: string; neighborhood: string; website: string;
  counter_hours: Record<string, string> | string; store_hours: Record<string, string> | string;
  weekend: { summary_counter_first?: string } & Record<string, unknown>;
  lunch_break: Record<string, { start: string; end: string }> | string; holiday_hours: string | unknown;
  delivery: string; delivery_details: Record<string, string> | string; drive_thru: string;
  languages: string[] | string;
  vaccines_routine: string[] | string; vaccines_travel: string[] | string; clinic_on_site: string;
  specialty_pharmacy: string; vaccine_booking_url: string; sources: Record<string, string>; checked_date: string;
  nearby_clinics: { name: string; kind: string; address: string; distance_label: string; walk_in: string }[] | string;
  brief: PharmacyBrief; stock_reports: StockSummary; sample_reports: ReportCounts[];
  reviews: ReviewSummary; sample_reviews: Review[]; holidays: Holiday[];
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const DAY_KEYS: Record<string, string> = { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" };

function to12(hhmm: string) {
  const [h, m] = hhmm.split(":").map(Number);
  return `${h % 12 || 12}:${String(m).padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`;
}

function ReportList({ items, sample }: { items: ReportCounts[]; sample?: boolean }) {
  const { t, lang } = useApp();
  return (
    <ul className="feed">
      {items.map((x) => (
        <li key={x.drug_id} className={sample ? "feed-item is-sample" : "feed-item"}>
          {sample && <SampleBadge />} <strong>{x.drug ?? x.drug_id}</strong>: {t("inStockCount", { n: x.in_stock_reports })} · {t("outStockCount", { n: x.out_of_stock_reports })} · <span className="muted">{t("latest", { time: ago(x.latest_report, lang) })}</span>
          {x.conflicting && <div className="warn-text">{t("conflicting")}</div>}
        </li>
      ))}
    </ul>
  );
}

/** Best time to go: typical wait by weekday and part of the day, only with at least 3 reviews in that slot. */
function BestTime({ pharmacyId }: { pharmacyId: string }) {
  const { t, lang, version } = useApp();
  const [x, setX] = useState<PharmacyInsights | null>(null);
  useEffect(() => { api.get<PharmacyInsights>(`/api/pharmacies/${pharmacyId}/insights`).then(setX).catch(() => setX(null)); }, [pharmacyId, version]);
  if (!x) return null;
  const line = (b: PharmacyInsights["best_times"][number]) =>
    t("bestTimeLine", { day: lang === "es" ? b.day_es : b.day_en, time: t(`t_${b.time}` as never), m: b.typical_wait_minutes });
  return (
    <section className="card best-time" aria-labelledby="best-time-title">
      <h2 id="best-time-title">{t("bestTimeTitle")}</h2>
      {x.best_times.length === 0 && x.sample_best_times.length === 0 && <p className="muted best-time-none">{t("bestTimeNone")}</p>}
      {x.best_times.length > 0 && <ul className="plain-list best-time-real">{x.best_times.map((b) => <li key={b.weekday + b.time}>{line(b)} ({b.reviews})</li>)}</ul>}
      {x.sample_best_times.length > 0 && (
        <ul className="plain-list best-time-sample">{x.sample_best_times.map((b) => <li key={b.weekday + b.time}><SampleBadge /> {line(b)} ({b.reviews})</li>)}</ul>
      )}
      <p className="small muted">{t("bestTimeNote")}</p>
    </section>
  );
}

function ReviewList({ items }: { items: Review[] }) {
  const { t } = useApp();
  return (
    <ul className="feed">
      {items.map((r, i) => (
        <li key={i} className={r.sample ? "feed-item is-sample" : "feed-item"}>
          {r.sample && <SampleBadge />} <Stars n={r.rating} />
          {r.wait_minutes != null && <span className="muted"> · {r.wait_minutes} min</span>}
          <span className="muted"> · {r.visit_date}{r.visit_time ? ` (${t(`vt_${r.visit_time}` as never)})` : ""} · {r.by}</span>
          {r.languages && r.languages.length > 0 && <span className="muted"> · {t("langReportedBadge")}: {r.languages.map((l) => langName(t, l)).join(", ")}</span>}
          {r.comment && <p className="review-text">{r.comment}</p>}
        </li>
      ))}
    </ul>
  );
}

export function PharmacyPage() {
  const { id = "" } = useParams();
  const nav = useNavigate();
  const { t, lang, meta, drugId, set, version, rate } = useApp();
  const [d, setD] = useState<Details | null>(null);
  const [error, setError] = useState("");
  const [script, setScript] = useState("");
  const drug = meta?.drugs.find((x) => x.id === drugId);

  const load = useCallback(() => {
    api.get<Details>(`/api/pharmacies/${id}?lang=${lang}`).then(setD).catch((e) => setError(e?.status === 404 ? t("notFound") : t("errorGeneric")));
  }, [id, lang, t]);
  useEffect(load, [load, version]);
  useEffect(() => {
    if (!drugId) { setScript(""); return; }
    api.get<{ call_script: string }>(`/api/drugs/${drugId}/call-script?lang=${lang}`).then((r) => setScript(r.call_script)).catch(() => setScript(""));
  }, [drugId, lang]);

  if (error) return <p className="alert" role="alert">{error}</p>;
  if (!d) return <p className="muted" role="status">{t("loading")}</p>;
  const counter = typeof d.counter_hours === "object" ? d.counter_hours : null;
  const store = typeof d.store_hours === "object" ? d.store_hours : null;
  const lunch = typeof d.lunch_break === "object" ? d.lunch_break : null;
  const lunchSpans = lunch ? [...new Set(Object.values(lunch).map((b) => `${to12(b.start)}–${to12(b.end)}`))] : [];
  const vaccines = [d.vaccines_routine, d.vaccines_travel].flatMap((v) => (Array.isArray(v) ? v : []));
  const dd = typeof d.delivery_details === "object" ? d.delivery_details : null;
  const realReviews = d.reviews.recent;

  return (
    <article className="pharmacy-page">
      <button type="button" className="link-button back" onClick={() => nav(-1)}>← {t("back")}</button>
      <header className="page-head">
        <h1>{d.name}</h1>
        <OpenBadge open={d.brief.open_now} opensNext={d.brief.opens_next} status={d.brief.status} />
      </header>
      <p className="address big">{d.address} · {d.neighborhood}</p>
      {d.brief.open_now && d.brief.closes_at && <p><strong>{t("closesAt", { time: d.brief.closes_at })}</strong></p>}
      <div className="card-actions">
        <a className="btn primary" href={telHref(d.phone)}><span aria-hidden="true">📞</span> {t("call")} {d.phone}</a>
        <a className="btn ghost" href={directionsHref(d.address)} target="_blank" rel="noreferrer">{t("directions")}</a>
        <a className="btn ghost" href={d.website} target="_blank" rel="noreferrer">{new URL(d.website).hostname.replace(/^www\./, "")} ↗</a>
        <button type="button" className="btn ghost" onClick={() => rate(id)}><span aria-hidden="true">★</span> {t("ratePharmacy")}</button>
        <SendHereLink pharmacyId={id} drugId={drugId || null} />
      </div>
      <BeforeYouGo drugName={drug?.name} hoursToday={d.brief.counter_today === "closed" ? t("closed") : d.brief.counter_today} />
      {d.holidays.map((h) => <p key={h.date} className="notice" role="note">{t("holidayNotice", { name: lang === "es" ? h.name_es : h.name, date: h.date })}</p>)}

      <section className="hours-grid" aria-label={t("counterHours")}>
        <div className="card hours counter">
          <h2>{t("counterHours")}</h2>
          {counter ? (
            <table>
              <tbody>{DAYS.map((day) => <tr key={day}><th scope="row">{DAY_NAMES[lang][day]}</th><td>{counter[day] === "closed" ? t("closed") : counter[day]}</td></tr>)}</tbody>
            </table>
          ) : <p className="muted">{t("notFound")}</p>}
          <p><strong>{t("lunch")}:</strong> {lunchSpans.length ? `${lunchSpans.join(", ")} (${Object.keys(lunch!).map((k) => DAY_NAMES[lang][DAY_KEYS[k]].slice(0, 3)).join(", ")})` : t("noLunch")}</p>
        </div>
        <div className="card hours store">
          <h2>{t("storeHours")}</h2>
          {store ? (
            <table>
              <tbody>{DAYS.map((day) => <tr key={day}><th scope="row">{DAY_NAMES[lang][day]}</th><td>{store[day] === "closed" ? t("closed") : store[day]}</td></tr>)}</tbody>
            </table>
          ) : <p className="muted">{t("notFound")}</p>}
        </div>
      </section>

      <section className="card two-col">
        <div><h2>{t("weekend")}</h2><p>{d.weekend?.summary_counter_first ?? t("notFound")}</p></div>
        <div><h2>{t("holiday")}</h2><p>{d.holiday_hours && d.holiday_hours !== "not found" ? String(d.holiday_hours) : t("holidayNotFound")}</p></div>
      </section>

      <section className="card two-col">
        <div>
          <h2>{t("delivery")}</h2>
          <p><NotFoundText value={d.delivery} /></p>
          {dd && <ul className="small">{["same_day", "cost", "area", "how_to_request"].map((k) => dd[k] && <li key={k}><NotFoundText value={dd[k]} /></li>)}</ul>}
        </div>
        <div>
          <h2>{t("services")}</h2>
          <ul className="small">
            <li><strong>{t("vaccinesListed")}:</strong> {vaccines.length ? vaccines.join(", ") : <NotFoundText value={null} />}
              {d.vaccine_booking_url && d.vaccine_booking_url !== "not found" && <> · <a href={d.vaccine_booking_url} target="_blank" rel="noreferrer">{t("bookVaccine")} ↗</a></>}</li>
            <li><strong>{t("clinic")}:</strong> <NotFoundText value={d.clinic_on_site} /></li>
            <li><strong>{t("specialty")}:</strong> <NotFoundText value={d.specialty_pharmacy} /></li>
            <li><strong>{t("driveThru")}:</strong> <NotFoundText value={d.drive_thru} /></li>
            <li><strong>{t("fLanguage")} ({t("langWebsite")}):</strong> <NotFoundText value={Array.isArray(d.languages) ? d.languages.join(", ") : d.languages} /></li>
          </ul>
          <h3 className="h3">{t("langReportedTitle")}</h3>
          <ReportedLanguages real={d.brief.reported_languages} sample={d.brief.sample_reported_languages} />
          <p className="small muted"><Link to="/language-card">{t("langCardLink")}</Link></p>
        </div>
      </section>

      <section className="card">
        <h2>{t("nearbyClinics")}</h2>
        {Array.isArray(d.nearby_clinics) ? (
          <ul>
            {d.nearby_clinics.slice(0, 6).map((c) => (
              <li key={c.name + c.address}><strong>{c.name}</strong> — {c.address} · {c.distance_label}
                {c.walk_in.startsWith("not found") && <span className="muted"> ({t("callFirst")})</span>}</li>
            ))}
          </ul>
        ) : <p className="muted">{String(d.nearby_clinics)}</p>}
      </section>

      <section className="card" aria-labelledby="call-about">
        <label id="call-about" className="step-label">{t("callAbout")}
          <select value={drugId} onChange={(e) => set({ drugId: e.target.value })} name="call-drug">
            <option value="">{t("pickMedicine")}</option>
            {meta?.drugs.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        {script && <CallScriptCard text={script} drugId={drugId} pharmacyId={id} controlled={drug?.controlled} />}
        {drug?.controlled && <p className="notice small">{t("controlledExplain")}</p>}
      </section>

      <section className="card" aria-labelledby="reports-title">
        <h2 id="reports-title">{t("stockReports")}</h2>
        {d.stock_reports.drugs.length === 0 && d.sample_reports.length === 0 && <p className="muted">{t("noReportsYet")}</p>}
        {d.stock_reports.drugs.length > 0 && <ReportList items={d.stock_reports.drugs} />}
        {d.sample_reports.length > 0 && <ReportList items={d.sample_reports} sample />}
        <p className="reminder">{t("callToConfirm")}</p>
      </section>

      <BestTime pharmacyId={id} />

      <section className="card" aria-labelledby="reviews-title">
        <div className="section-head">
          <h2 id="reviews-title">{t("reviews")}</h2>
          <button type="button" className="btn" onClick={() => rate(id)}><span aria-hidden="true">★</span> {t("ratePharmacy")}</button>
        </div>
        {d.reviews.average_rating != null ? (
          <p className="big">★ {t("avgRating", { r: d.reviews.average_rating })}{d.reviews.average_wait_minutes != null && ` · ${t("avgWait", { m: d.reviews.average_wait_minutes })}`} ({d.reviews.reviews})</p>
        ) : d.reviews.reviews > 0 ? <p>{t("fewReviews", { n: d.reviews.reviews })}</p> : <p className="empty-text">{t("noReviewsYet")}</p>}
        {realReviews.length > 0 && <ReviewList items={realReviews} />}
        {d.sample_reviews.length > 0 && <><h3 className="sample-head">{t("samplePosts")}</h3><ReviewList items={d.sample_reviews} /></>}
      </section>
      <div className="card-actions"><ReadAloud label={t("readPage")} text={() => document.getElementById("main")?.innerText ?? ""} /></div>
      <p className="muted small">{t("checked", { date: d.checked_date })} · <Link to="/about">{t("navAbout")}</Link></p>
    </article>
  );
}
