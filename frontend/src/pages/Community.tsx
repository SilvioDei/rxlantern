// Community: the latest stock reports and reviews across all pharmacies. Real and sample posts are kept apart.
// Patients can search by medicine (same suggestions as the guided search), pharmacy, and neighborhood, and sort by
// newest or by rating. Reviews are about a pharmacy, so the medicine search filters stock reports only.
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { api, type Review } from "../api";
import { SampleBadge, Stars, ago } from "../components/Bits";
import { MedicineSearch } from "../components/MedicineSearch";
import type { Medicine } from "../search";

interface Report {
  pharmacy_id: string; pharmacy: string; address: string; neighborhood: string; drug_id: string; drug: string;
  in_stock: boolean; reported_at: string; sample: boolean; pharmacy_rating: number | null;
}
interface FeedReview extends Review { neighborhood: string; created_at?: string; pharmacy_rating: number | null }
interface Feed { reports: Report[]; reviews: FeedReview[]; sample_reports: Report[]; sample_reviews: FeedReview[]; sample_data: boolean }
type Sort = "newest" | "rating";

function ReportItem({ r }: { r: Report }) {
  const { t, lang } = useApp();
  return (
    <li className={`feed-item ${r.sample ? "is-sample" : ""}`}>
      {r.sample && <SampleBadge />}
      <span className={`badge ${r.in_stock ? "badge-ok" : "badge-warn"}`}>{r.in_stock ? `✓ ${t("inStockWord")}` : `✕ ${t("outStockWord")}`}</span>{" "}
      <strong>{r.drug}</strong> · <Link to={`/pharmacies/${r.pharmacy_id}`}>{r.pharmacy}</Link>, {r.address.split(",")[0]}
      <span className="muted"> · {r.neighborhood} · {ago(r.reported_at, lang)}</span>
    </li>
  );
}

function ReviewItem({ r }: { r: FeedReview }) {
  const { t } = useApp();
  return (
    <li className={`feed-item ${r.sample ? "is-sample" : ""}`}>
      {r.sample && <SampleBadge />}
      <Stars n={r.rating} /> · <Link to={`/pharmacies/${r.pharmacy_id}`}>{r.pharmacy}</Link>
      <span className="muted"> · {r.neighborhood}</span>
      {r.wait_minutes != null && <span className="muted"> · {t("waitMinutes")}: {r.wait_minutes}</span>}
      <span className="muted"> · {r.visit_date} · {r.by}</span>
      {r.comment && <p className="review-text">{r.comment}</p>}
    </li>
  );
}

const newestReport = (a: Report, b: Report) => b.reported_at.localeCompare(a.reported_at);
const newestReview = (a: FeedReview, b: FeedReview) =>
  (b.created_at ?? b.visit_date).localeCompare(a.created_at ?? a.visit_date) || b.visit_date.localeCompare(a.visit_date);
// "By rating": reviews by their stars; stock reports by their pharmacy's average rating (pharmacies without
// 3 real reviews yet come last). Ties: newest first.
const byRatingReport = (a: Report, b: Report) => (b.pharmacy_rating ?? -1) - (a.pharmacy_rating ?? -1) || newestReport(a, b);
const byRatingReview = (a: FeedReview, b: FeedReview) => b.rating - a.rating || newestReview(a, b);

export function Community() {
  const { t, version, meta } = useApp();
  const [feed, setFeed] = useState<Feed | null>(null);
  const [error, setError] = useState("");
  const [med, setMed] = useState<Medicine | null>(null);
  const [pharmacy, setPharmacy] = useState("");
  const [hood, setHood] = useState("");
  const [sort, setSort] = useState<Sort>("newest");
  useEffect(() => { api.get<Feed>("/api/community").then(setFeed).catch(() => setError(t("errorGeneric"))); }, [version, t]);

  const ids = useMemo(() => new Set(med?.options.map((o) => o.id) ?? []), [med]);
  const view = useMemo(() => {
    if (!feed) return null;
    const keepPlace = (x: { pharmacy_id?: string; neighborhood: string }) =>
      (!pharmacy || x.pharmacy_id === pharmacy) && (!hood || x.neighborhood === hood);
    const reports = (list: Report[]) => list.filter((r) => keepPlace(r) && (!med || ids.has(r.drug_id)))
      .sort(sort === "rating" ? byRatingReport : newestReport);
    const reviews = (list: FeedReview[]) => list.filter(keepPlace).sort(sort === "rating" ? byRatingReview : newestReview);
    return { reports: reports(feed.reports), sampleReports: reports(feed.sample_reports),
             reviews: reviews(feed.reviews), sampleReviews: reviews(feed.sample_reviews) };
  }, [feed, med, ids, pharmacy, hood, sort]);

  const filtering = !!(med || pharmacy || hood);
  const clear = () => { setMed(null); setPharmacy(""); setHood(""); };
  const noReports = view && view.reports.length + view.sampleReports.length === 0;
  const noReviews = view && view.reviews.length + view.sampleReviews.length === 0;
  const pharmacies = (meta?.pharmacies ?? []).filter((p) => !hood || p.neighborhood === hood);

  return (
    <>
      <h1>{t("communityTitle")}</h1>
      <p className="lead">{t("communityIntro")}</p>
      {feed?.sample_data && <p className="notice" role="note"><SampleBadge /> <strong>{t("sampleNote")}</strong> {t("sampleExplain")}</p>}
      <p className="small muted">{t("howChecked")} <Link to="/about">{t("navAbout")}</Link></p>

      <section className="card community-search" aria-labelledby="cs-title">
        <h2 id="cs-title" className="h3">{t("communitySearchTitle")}</h2>
        <div className="cs-grid">
          <div className="cs-med">
            {med ? (
              <>
                <p className="field-label">{t("communityMedLabel")}</p>
                <div className="chosen-row">
                  <span className="chosen"><span aria-hidden="true">✓</span> {med.label}</span>
                  <button type="button" className="link-button" onClick={() => setMed(null)}>{t("changeDrug")}</button>
                </div>
              </>
            ) : (
              <MedicineSearch id="community-med" listId="community-med-list" label={t("communityMedLabel")} labelClass="field-label"
                placeholder={t("communityMedPlaceholder")} onPick={(m) => setMed(m)} />
            )}
          </div>
          <label className="field">{t("fPharmacy")}
            <select name="pharmacy" value={pharmacy} onChange={(e) => setPharmacy(e.target.value)}>
              <option value="">{t("fAllPharmacies")}</option>
              {pharmacies.map((p) => <option key={p.id} value={p.id}>{p.name} — {p.address.split(",")[0]}</option>)}
            </select>
          </label>
          <label className="field">{t("fNeighborhood")}
            <select name="neighborhood" value={hood} onChange={(e) => { setHood(e.target.value); setPharmacy(""); }}>
              <option value="">{t("fAllNeighborhoods")}</option>
              {meta?.neighborhoods.map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </label>
          <label className="field">{t("sortBy")}
            <select name="sort" value={sort} onChange={(e) => setSort(e.target.value as Sort)}>
              <option value="newest">{t("sortNewest")}</option>
              <option value="rating">{t("sortRatingHigh")}</option>
            </select>
          </label>
        </div>
        {filtering && <button type="button" className="btn ghost" onClick={clear}>{t("clearSearch")}</button>}
      </section>

      {error && <p className="alert" role="alert">{error}</p>}
      {!feed && !error && <p className="muted" role="status">{t("loading")}</p>}
      {view && (
        <div className="two-col">
          <section className="card" aria-labelledby="c-reports">
            <h2 id="c-reports">{t("latestReports")}</h2>
            {noReports ? (
              <p className="empty-posts" role="status">{med ? t("noPostsMed") : filtering ? t("noPostsFilter") : t("noReportsYet")}</p>
            ) : view.reports.length ? (
              <ul className="feed">{view.reports.map((r, i) => <ReportItem key={i} r={r} />)}</ul>
            ) : <p className="muted">{t("noReportsYet")}</p>}
            {view.sampleReports.length > 0 && (
              <>
                <h3 className="sample-head">{t("samplePosts")}</h3>
                <ul className="feed">{view.sampleReports.map((r, i) => <ReportItem key={i} r={r} />)}</ul>
              </>
            )}
            <p className="reminder">{t("callToConfirm")}</p>
          </section>
          <section className="card" aria-labelledby="c-reviews">
            <h2 id="c-reviews">{t("latestReviews")}</h2>
            {med && <p className="muted small">{t("reviewsNotPerMed")}</p>}
            {noReviews ? (
              <p className="empty-posts" role="status">{filtering ? t("noPostsFilter") : `${t("noReviewsYet").split(".")[0]}.`}</p>
            ) : view.reviews.length ? (
              <ul className="feed">{view.reviews.map((r, i) => <ReviewItem key={i} r={r} />)}</ul>
            ) : <p className="muted">{t("noReviewsYet").split(".")[0]}.</p>}
            {view.sampleReviews.length > 0 && (
              <>
                <h3 className="sample-head">{t("samplePosts")}</h3>
                <ul className="feed">{view.sampleReviews.map((r, i) => <ReviewItem key={i} r={r} />)}</ul>
              </>
            )}
          </section>
        </div>
      )}
    </>
  );
}
