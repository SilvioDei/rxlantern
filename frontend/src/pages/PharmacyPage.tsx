// One pharmacy: counter hours and store hours side by side (counter first), services, clinics, reports, reviews.
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useApp } from "../state";
import { api, type PharmacyBrief, type ReviewSummary, type StockSummary } from "../api";
import { NotFoundText, OpenBadge, directionsHref, telHref } from "../components/Bits";
import { ReportForm, ReviewForm } from "../components/Forms";
import { DAY_NAMES } from "../i18n";

interface Details {
  name: string; address: string; phone: string; type: string; neighborhood: string; website: string;
  counter_hours: Record<string, string> | string; store_hours: Record<string, string> | string;
  weekend: { summary_counter_first?: string } & Record<string, unknown>;
  lunch_break: Record<string, { start: string; end: string }> | string; holiday_hours: string | unknown;
  delivery: string; delivery_details: Record<string, string> | string; drive_thru: string;
  wheelchair_accessible: string; languages: string[] | string;
  vaccines_routine: string[] | string; vaccines_travel: string[] | string; clinic_on_site: string;
  specialty_pharmacy: string; vaccine_booking_url: string; sources: Record<string, string>; checked_date: string;
  nearby_clinics: { name: string; kind: string; address: string; distance_label: string; walk_in: string }[] | string;
  brief: PharmacyBrief; stock_reports: StockSummary; reviews: ReviewSummary;
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const DAY_KEYS: Record<string, string> = { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" };

function to12(hhmm: string) {
  const [h, m] = hhmm.split(":").map(Number);
  return `${h % 12 || 12}:${String(m).padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`;
}

function fmtTime(iso: string, lang: string) {
  try { return new Date(iso).toLocaleString(lang === "es" ? "es-US" : "en-US", { dateStyle: "medium", timeStyle: "short" }); }
  catch { return iso; }
}

export function PharmacyPage() {
  const { id = "" } = useParams();
  const { t, lang, requireLogin } = useApp();
  const [d, setD] = useState<Details | null>(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState<"report" | "review" | null>(null);

  const load = useCallback(() => {
    api.get<Details>(`/api/pharmacies/${id}?lang=${lang}`).then(setD).catch(() => setError(t("errorGeneric")));
  }, [id, lang, t]);
  useEffect(load, [load]);

  if (error) return <p className="alert">{error}</p>;
  if (!d) return <p className="muted">{t("loading")}</p>;
  const counter = typeof d.counter_hours === "object" ? d.counter_hours : null;
  const store = typeof d.store_hours === "object" ? d.store_hours : null;
  const lunch = typeof d.lunch_break === "object" ? d.lunch_break : null;
  const lunchSpans = lunch ? [...new Set(Object.values(lunch).map((b) => `${to12(b.start)}–${to12(b.end)}`))] : [];
  const vaccines = [d.vaccines_routine, d.vaccines_travel].flatMap((v) => (Array.isArray(v) ? v : []));
  const dd = typeof d.delivery_details === "object" ? d.delivery_details : null;

  return (
    <article className="pharmacy-page">
      <Link to="/pharmacies" className="back">← {t("back")}</Link>
      <header className="page-head">
        <h1>{d.name}</h1>
        <OpenBadge open={d.brief.open_now} opensNext={d.brief.opens_next} />
      </header>
      <p className="address big">{d.address} · {d.neighborhood}</p>
      <div className="card-actions">
        <a className="btn primary" href={telHref(d.phone)}><span aria-hidden="true">📞</span> {t("call")} {d.phone}</a>
        <a className="btn ghost" href={directionsHref(d.address)} target="_blank" rel="noreferrer">{t("directions")}</a>
        <a className="btn ghost" href={d.website} target="_blank" rel="noreferrer">{new URL(d.website).hostname.replace(/^www\./, "")}</a>
      </div>

      <section className="hours-grid" aria-label={t("counterHours")}>
        <div className="card hours counter">
          <h2>{t("counterHours")}</h2>
          {counter ? (
            <table>
              <tbody>{DAYS.map((day) => <tr key={day}><th scope="row">{DAY_NAMES[lang][day]}</th><td>{counter[day]}</td></tr>)}</tbody>
            </table>
          ) : <p className="muted">{t("notFound")}</p>}
          <p><strong>{t("lunch")}:</strong> {lunchSpans.length ? `${lunchSpans.join(", ")} (${Object.keys(lunch!).map((k) => DAY_NAMES[lang][DAY_KEYS[k]].slice(0, 3)).join(", ")})` : t("noLunch")}</p>
        </div>
        <div className="card hours store">
          <h2>{t("storeHours")}</h2>
          {store ? (
            <table>
              <tbody>{DAYS.map((day) => <tr key={day}><th scope="row">{DAY_NAMES[lang][day]}</th><td>{store[day]}</td></tr>)}</tbody>
            </table>
          ) : <p className="muted">{t("notFound")}</p>}
        </div>
      </section>

      <section className="card">
        <h2>{t("weekend")}</h2>
        <p>{d.weekend?.summary_counter_first ?? t("notFound")}</p>
        <h2>{t("holiday")}</h2>
        <p>{d.holiday_hours && d.holiday_hours !== "not found" ? String(d.holiday_hours) : t("holidayNotFound")}</p>
      </section>

      <section className="card two-col">
        <div>
          <h2>{t("delivery")}</h2>
          <p><NotFoundText value={d.delivery} /></p>
          {dd && (
            <ul className="small">
              {["same_day", "cost", "area", "how_to_request"].map((k) => dd[k] && <li key={k}><NotFoundText value={dd[k]} /></li>)}
            </ul>
          )}
        </div>
        <div>
          <h2>{t("services")}</h2>
          <ul className="small">
            <li><strong>{t("vaccinesListed")}:</strong> {vaccines.length ? vaccines.join(", ") : <NotFoundText value={null} />}</li>
            <li><strong>{t("clinic")}:</strong> <NotFoundText value={d.clinic_on_site} /></li>
            <li><strong>{t("specialty")}:</strong> <NotFoundText value={d.specialty_pharmacy} /></li>
            <li><strong>{t("fLanguage")}:</strong> <NotFoundText value={Array.isArray(d.languages) ? d.languages.join(", ") : d.languages} /></li>
            <li><strong>{t("fWheelchair")}:</strong> <NotFoundText value={d.wheelchair_accessible} /></li>
          </ul>
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

      <section className="card">
        <div className="section-head">
          <h2>{t("stockReports")}</h2>
          <button type="button" className="btn" onClick={() => requireLogin(() => setForm("report"))}>{t("postReport")}</button>
        </div>
        {d.stock_reports.drugs.length === 0 ? <p className="muted">{t("noReports")}</p> : (
          <ul>
            {d.stock_reports.drugs.map((x) => (
              <li key={x.drug_id}><strong>{x.drug ?? x.drug_id}</strong>: {t("inStockCount", { n: x.in_stock_reports })} · {t("outStockCount", { n: x.out_of_stock_reports })} · <span className="muted">{t("latest", { time: fmtTime(x.latest_report, lang) })}</span>
                {x.conflicting && <div className="warn-text">{t("conflicting")}</div>}</li>
            ))}
          </ul>
        )}
        <p className="reminder">{t("callToConfirm")}</p>
      </section>

      <section className="card">
        <div className="section-head">
          <h2>{t("reviews")}</h2>
          <button type="button" className="btn" onClick={() => requireLogin(() => setForm("review"))}>{t("writeReview")}</button>
        </div>
        <p className="muted">{t("reviewCount", { n: d.reviews.reviews })}</p>
        {d.reviews.average_rating != null ? (
          <p className="big">★ {t("avgRating", { r: d.reviews.average_rating })}{d.reviews.average_wait_minutes != null && ` · ${t("avgWait", { m: d.reviews.average_wait_minutes })}`}</p>
        ) : <p>{t("notEnoughReviews")}</p>}
        <ul className="reviews">
          {d.reviews.recent.map((r, i) => (
            <li key={i}><span aria-label={t("stars", { n: r.rating })}>{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
              {r.wait_minutes != null && <span className="muted"> · {r.wait_minutes} min</span>}
              <span className="muted"> · {r.visit_date} · {r.by}</span>
              {r.comment && <p className="review-text">{r.comment}</p>}</li>
          ))}
        </ul>
      </section>
      <p className="muted small">{t("checked", { date: d.checked_date })}</p>

      {form === "report" && <ReportForm pharmacyId={id} onDone={load} onClose={() => setForm(null)} />}
      {form === "review" && <ReviewForm pharmacyId={id} onDone={load} onClose={() => setForm(null)} />}
    </article>
  );
}
