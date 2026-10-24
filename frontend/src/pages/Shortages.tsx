// Shortage watch: FDA status for the 25 drugs. Controlled: status + call script only. Others: fresh community reports.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";
import { CallScriptCard } from "../components/Bits";

interface DrugRow {
  id: string; name: string; controlled: boolean; shortage_status: string; shortage_summary: string;
  checked_date: string; source: string; call_script?: string;
  community: { refused?: boolean; message?: string; reminder?: string;
    reports?: { pharmacy_id: string; pharmacy: string; in_stock_reports: number; out_of_stock_reports: number; conflicting: boolean }[] };
}

const statusClass = (s: string) => (s === "in shortage" ? "badge-warn" : s.startsWith("not found") ? "badge-ok" : "badge-unknown");

export function Shortages() {
  const { t, lang } = useApp();
  const [rows, setRows] = useState<DrugRow[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api.get<{ drugs: DrugRow[] }>(`/api/drugs?lang=${lang}`).then((r) => setRows(r.drugs)).catch(() => setError(t("errorOffline")));
  }, [lang, t]);

  return (
    <>
      <h1>{t("shortTitle")}</h1>
      <p className="lead">{t("shortIntro")}</p>
      {error && <p className="alert">{error}</p>}
      {!rows && !error && <p className="muted">{t("loading")}</p>}
      <div className="drug-list">
        {rows?.map((d) => (
          <article key={d.id} className={`card drug-card ${d.controlled ? "controlled" : ""}`}>
            <div className="card-top">
              <h2 className="h3">{d.name}</h2>
              <span className={`badge ${statusClass(d.shortage_status)}`}>{d.shortage_status}</span>
            </div>
            <p className="small">{d.shortage_summary}</p>
            <p className="muted small">FDA · {t("checked", { date: d.checked_date })} · <a href={d.source} target="_blank" rel="noreferrer">accessdata.fda.gov</a></p>
            {d.controlled ? (
              <>
                <p className="notice small"><strong>{t("controlled")}.</strong> {t("controlledExplain")}</p>
                {d.call_script && <CallScriptCard text={d.call_script} />}
              </>
            ) : (
              <div className="small">
                <strong>{t("communityReports")}:</strong>{" "}
                {d.community.reports?.length ? (
                  <ul>
                    {d.community.reports.map((r) => (
                      <li key={r.pharmacy_id}><Link to={`/pharmacies/${r.pharmacy_id}`}>{r.pharmacy}</Link>: {t("inStockCount", { n: r.in_stock_reports })} · {t("outStockCount", { n: r.out_of_stock_reports })}</li>
                    ))}
                  </ul>
                ) : <span className="muted">{t("noReports")}</span>}
                <div className="reminder">{t("callToConfirm")}</div>
              </div>
            )}
          </article>
        ))}
      </div>
    </>
  );
}
