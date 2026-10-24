// For pharmacies: anonymous demand signals. Counts of RxLantern searches by medicine, Boston neighborhood, and week,
// only counts of 5 or more. Nothing about the person searching is stored. Sample counts are shown apart.
import { useEffect, useState } from "react";
import { useApp } from "../state";
import { api } from "../api";
import { ReadAloud, SampleBadge } from "../components/Bits";

interface Row { drug_id: string; drug: string; neighborhood: string; week: string; count: number; sample?: boolean }
interface Demand { rows: Row[]; sample_rows: Row[]; weeks: string[]; min_count: number; sample_data: boolean }

export function ForPharmacies() {
  const { t } = useApp();
  const [d, setD] = useState<Demand | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { api.get<Demand>("/api/demand").then(setD).catch(() => setError(t("errorGeneric"))); }, [t]);
  const line = (r: Row) => t("fpLine", { n: r.count, drug: r.drug, hood: r.neighborhood });
  const byWeek = (rows: Row[]) => [...new Set(rows.map((r) => r.week))].map((w) => [w, rows.filter((r) => r.week === w)] as const);
  return (
    <div className="for-pharmacies-page">
      <h1>{t("fpTitle")}</h1>
      <p className="lead">{t("fpIntro")}</p>
      <p className="notice small" role="note"><span aria-hidden="true">🔒</span> {t("fpPrivacy")}</p>
      {error && <p className="alert" role="alert">{error}</p>}
      {!d && !error && <p className="muted" role="status">{t("loading")}</p>}
      {d && (
        <>
          <section className="card" aria-labelledby="fp-real">
            <div className="section-head">
              <h2 id="fp-real" className="h3">{t("fpTitle")}</h2>
              <ReadAloud text={() => [...d.rows, ...d.sample_rows].map(line).join(". ") || t("fpNone")} />
            </div>
            {d.rows.length === 0 ? <p className="empty-posts">{t("fpNone")}</p> : byWeek(d.rows).map(([w, rows]) => (
              <div key={w}>
                <h3 className="h3">{t("fpWeek", { date: w })}</h3>
                <ul className="feed demand-list">{rows.map((r, i) => <li key={i} className="feed-item">{line(r)}</li>)}</ul>
              </div>
            ))}
          </section>
          {d.sample_rows.length > 0 && (
            <section className="card" aria-labelledby="fp-sample">
              <h2 id="fp-sample" className="h3 sample-head">{t("fpSampleHead")}</h2>
              <p className="small muted">{t("sampleExplain")}</p>
              <ul className="feed demand-list">
                {d.sample_rows.map((r, i) => <li key={i} className="feed-item is-sample"><SampleBadge /> {line(r)} · {t("fpWeek", { date: r.week })}</li>)}
              </ul>
            </section>
          )}
        </>
      )}
    </div>
  );
}
