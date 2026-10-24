// Shortage watch: FDA status for the 150 drugs (from our database, refreshed daily in the background),
// FDA's estimate if given, community report counts (non-controlled only), and three buttons per drug.
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";
import { CallScriptCard, SampleBadge, ShortageBadge, SourceLink } from "../components/Bits";
import { StarButton, WatchHighlights } from "../components/Journey";

interface Counts { in_stock_reports: number; out_of_stock_reports: number }
interface DrugRow {
  id: string; name: string; controlled: boolean; shortage_status: string; shortage_summary: string;
  fda_estimate: string | null; fda_updated: string | null; checked_date: string; source: string; call_script: string;
  community: { refused?: boolean; message?: string; real?: Counts | null; sample?: Counts | null };
}

function DrugCard({ d }: { d: DrugRow }) {
  const { t, set, report } = useApp();
  const nav = useNavigate();
  const [script, setScript] = useState(false);
  return (
    <article className={`card drug-card ${d.controlled ? "controlled" : ""}`} aria-labelledby={`drug-${d.id}`}>
      <div className="card-top">
        <h2 className="h3" id={`drug-${d.id}`}>{d.name}</h2>
        <ShortageBadge status={d.shortage_status} />
        <StarButton drugId={d.id} name={d.name} />
      </div>
      <p className="small">{d.fda_estimate ? t("fdaEstimate", { text: d.fda_estimate }) : t("fdaNoEstimate")}</p>
      <p className="src muted">FDA · {t("checked", { date: d.checked_date })}{d.fda_updated && ` · ${t("fdaUpdated", { date: d.fda_updated })}`} · <SourceLink url={d.source} /></p>
      {d.controlled ? (
        <p className="notice small"><strong>{t("controlledTitle")}.</strong> {t("controlledExplain")}</p>
      ) : (
        <div className="small">
          <strong>{t("communityReports")}:</strong>{" "}
          {d.community.real ? t("reportCounts", { in: d.community.real.in_stock_reports, out: d.community.real.out_of_stock_reports })
            : <span className="muted">{t("noReportsYet")}</span>}
          {d.community.sample && <div><SampleBadge /> {t("reportCounts", { in: d.community.sample.in_stock_reports, out: d.community.sample.out_of_stock_reports })}</div>}
        </div>
      )}
      <div className="card-actions">
        <button type="button" className="btn primary" onClick={() => { set({ drugId: d.id }); nav(`/results?drug=${d.id}`); }}>{t("findNear")}</button>
        <button type="button" className="btn ghost" aria-expanded={script} onClick={() => setScript(!script)}>{script ? t("hideScript") : t("getScript")}</button>
        {!d.controlled && <button type="button" className="btn ghost" onClick={() => report({ drugId: d.id })}>{t("iCalled")}</button>}
      </div>
      {script && <CallScriptCard text={d.call_script} drugId={d.id} controlled={d.controlled} />}
    </article>
  );
}

export function Shortages() {
  const { t, lang } = useApp();
  const { version } = useApp();
  const [rows, setRows] = useState<DrugRow[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    setError("");
    api.get<{ drugs: DrugRow[] }>(`/api/drugs?lang=${lang}`).then((r) => setRows(r.drugs)).catch(() => setError(t("errorOffline")));
  }, [lang, t, version]);

  return (
    <>
      <h1>{t("shortTitle")}</h1>
      <p className="lead">{t("shortIntro")}</p>
      <WatchHighlights />
      {error && <p className="alert" role="alert">{error}</p>}
      {!rows && !error && <p className="muted" role="status">{t("loading")}</p>}
      <div className="drug-list">{rows?.map((d) => <DrugCard key={d.id} d={d} />)}</div>
      {lang === "es" && <p className="small">{t("dataEnglishNote")}</p>}
    </>
  );
}
