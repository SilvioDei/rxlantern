// "Print / share for my doctor": a plain, printable summary. No personal information (no place, no location).
import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { useOrigin } from "../origin";
import { useResults, withDistance } from "./Results";
import { coverageLines, nadacLine } from "../coverage";
import { shortageKey } from "../i18n";

export function PrintSummary() {
  const { t, lang, notify } = useApp();
  const { data, error } = useResults();
  const { origin } = useOrigin();
  const rows = useMemo(() => withDistance(data, origin).sort((a, b) => (a.dist ?? 99) - (b.dist ?? 99)).slice(0, 10), [data, origin]);
  if (error) return <p className="alert" role="alert">{t("errorGeneric")}</p>;
  if (!data) return <p role="status">{t("loading")}</p>;
  const today = new Date().toLocaleDateString(lang === "es" ? "es-US" : "en-US", { dateStyle: "long" });

  return (
    <article className="print-page">
      <div className="no-print print-actions">
        <Link to={`/results?drug=${data.drug.id}`} className="back">← {t("back")}</Link>
        <button type="button" className="btn primary" onClick={() => window.print()}><span aria-hidden="true">🖨</span> {t("printButton")}</button>
        <button type="button" className="btn ghost" onClick={async () => {
          const url = `${location.origin}/print?drug=${data.drug.id}`;
          try {
            if (navigator.share) await navigator.share({ title: t("printTitle", { drug: data.drug.name }), url });
            else { await navigator.clipboard.writeText(url); notify(t("linkCopied")); }
          } catch { /* the patient closed the share sheet */ }
        }}>{t("shareButton")}</button>
      </div>
      <h1>{t("printTitle", { drug: data.drug.name })}</h1>
      <p>{t("printIntro", { date: today })}</p>

      <h2>{t("shortageTitle")}</h2>
      <p><strong>{t(shortageKey(data.shortage.status))}</strong>. {data.shortage.fda_estimate ? t("fdaEstimate", { text: data.shortage.fda_estimate }) : t("fdaNoEstimate")} (FDA, {t("checked", { date: data.shortage.checked_date })})</p>

      <h2>{t("coverageTitle")}</h2>
      <p className="small">{t("estimateLabel")}</p>
      <ul>{coverageLines(data.coverage, data.plan, t).map((l) => <li key={l}>{l}</li>)}<li>{nadacLine(data.coverage, t)}</li></ul>
      {data.plan && data.plan.member_services_phone !== "not found" && <p>{t("callInsurance", { phone: data.plan.member_services_phone })} ({data.plan.name})</p>}

      <h2>{t("navPharmacies")}</h2>
      <table className="print-table">
        <thead><tr><th scope="col">{t("colPharmacy")}</th><th scope="col">{t("colHours")}</th><th scope="col">{t("colStatus")}</th></tr></thead>
        <tbody>
          {rows.map((p) => (
            <tr key={p.id}>
              <td><strong>{p.name}</strong><br />{p.address}<br />{p.phone}{p.dist != null && <><br />{t("away", { miles: p.dist })}</>}</td>
              <td>{p.counter_today === "closed" ? t("closed") : p.counter_today}</td>
              <td>{p.open_now ? t("openNow") : p.open_now === false ? (p.opens_next && p.opens_next !== "not found" ? t("closedOpens", { when: p.opens_next }) : t("closed")) : t("hoursUnknown")}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.drug.controlled && <p>{t("controlledExplain")}</p>}
      <p className="small">{t("callToConfirm")} {t("footer1")}</p>
      <p className="small muted">{t("printNoPersonal")}</p>
    </article>
  );
}
