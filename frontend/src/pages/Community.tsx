// Community: the latest stock reports and reviews across all pharmacies. Real and sample posts are kept apart.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { api, type Review } from "../api";
import { SampleBadge, Stars, ago } from "../components/Bits";

interface Report { pharmacy_id: string; pharmacy: string; address: string; drug_id: string; drug: string; in_stock: boolean; reported_at: string; sample: boolean }
interface Feed { reports: Report[]; reviews: Review[]; sample_reports: Report[]; sample_reviews: Review[]; sample_data: boolean }

function ReportItem({ r }: { r: Report }) {
  const { t, lang } = useApp();
  return (
    <li className={`feed-item ${r.sample ? "is-sample" : ""}`}>
      {r.sample && <SampleBadge />}
      <span className={`badge ${r.in_stock ? "badge-ok" : "badge-warn"}`}>{r.in_stock ? `✓ ${t("inStockWord")}` : `✕ ${t("outStockWord")}`}</span>{" "}
      <strong>{r.drug}</strong> · <Link to={`/pharmacies/${r.pharmacy_id}`}>{r.pharmacy}</Link>, {r.address.split(",")[0]}
      <span className="muted"> · {ago(r.reported_at, lang)}</span>
    </li>
  );
}

function ReviewItem({ r }: { r: Review }) {
  const { t } = useApp();
  return (
    <li className={`feed-item ${r.sample ? "is-sample" : ""}`}>
      {r.sample && <SampleBadge />}
      <Stars n={r.rating} /> · <Link to={`/pharmacies/${r.pharmacy_id}`}>{r.pharmacy}</Link>
      {r.wait_minutes != null && <span className="muted"> · {t("waitMinutes")}: {r.wait_minutes}</span>}
      <span className="muted"> · {r.visit_date} · {r.by}</span>
      {r.comment && <p className="review-text">{r.comment}</p>}
    </li>
  );
}

export function Community() {
  const { t, version } = useApp();
  const [feed, setFeed] = useState<Feed | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { api.get<Feed>("/api/community").then(setFeed).catch(() => setError(t("errorGeneric"))); }, [version, t]);

  return (
    <>
      <h1>{t("communityTitle")}</h1>
      <p className="lead">{t("communityIntro")}</p>
      {feed?.sample_data && <p className="notice" role="note"><SampleBadge /> <strong>{t("sampleNote")}</strong> {t("sampleExplain")}</p>}
      <p className="small muted">{t("howChecked")} <Link to="/about">{t("navAbout")}</Link></p>
      {error && <p className="alert" role="alert">{error}</p>}
      {!feed && !error && <p className="muted" role="status">{t("loading")}</p>}
      {feed && (
        <div className="two-col">
          <section className="card" aria-labelledby="c-reports">
            <h2 id="c-reports">{t("latestReports")}</h2>
            {feed.reports.length ? <ul className="feed">{feed.reports.map((r, i) => <ReportItem key={i} r={r} />)}</ul> : <p className="muted">{t("noReportsYet")}</p>}
            {feed.sample_reports.length > 0 && (
              <>
                <h3 className="sample-head">{t("samplePosts")}</h3>
                <ul className="feed">{feed.sample_reports.map((r, i) => <ReportItem key={i} r={r} />)}</ul>
              </>
            )}
            <p className="reminder">{t("callToConfirm")}</p>
          </section>
          <section className="card" aria-labelledby="c-reviews">
            <h2 id="c-reviews">{t("latestReviews")}</h2>
            {feed.reviews.length ? <ul className="feed">{feed.reviews.map((r, i) => <ReviewItem key={i} r={r} />)}</ul> : <p className="muted">{t("noReviewsYet").split(".")[0]}.</p>}
            {feed.sample_reviews.length > 0 && (
              <>
                <h3 className="sample-head">{t("samplePosts")}</h3>
                <ul className="feed">{feed.sample_reviews.map((r, i) => <ReviewItem key={i} r={r} />)}</ul>
              </>
            )}
          </section>
        </div>
      )}
    </>
  );
}
