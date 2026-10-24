// A medicine that is not in RxLantern's list: live FDA shortage status (openFDA) and a call script.
// Coverage and cost are not shown: those exist only for the medicines in the list.
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";
import { CallScriptCard, ReadAloud, ShortageBadge, SourceLink } from "../components/Bits";

interface Other {
  found: boolean | null; query: string; generic_names?: string[]; brand_names?: string[]; dea_schedule?: string;
  controlled?: boolean; status: string; summary: string; packages_by_availability?: Record<string, number>;
  fda_estimate?: string | null; source: string; checked_date: string; call_script?: string; coverage_note?: string;
}

export function OtherMedicine() {
  const { t, lang } = useApp();
  const [params] = useSearchParams();
  const name = (params.get("name") ?? "").trim().slice(0, 60);
  const [data, setData] = useState<Other | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null);
    setError("");
    if (!name) return;
    api.get<Other>(`/api/other-drug?name=${encodeURIComponent(name)}&lang=${lang}`).then(setData).catch(() => setError(t("errorGeneric")));
  }, [name, lang, t]);

  if (!name) return <div className="card"><p>{t("needDrug")}</p><Link className="btn primary" to="/">{t("otherBack")}</Link></div>;

  const names = [...(data?.generic_names ?? []), ...(data?.brand_names ?? [])];
  const pk = Object.entries(data?.packages_by_availability ?? {}).map(([k, n]) => `${k}: ${n}`).join(", ");
  return (
    <div className="other-page">
      <Link to="/" className="back">← {t("otherBack")}</Link>
      <h1>{t("otherTitle", { name })}</h1>
      <p className="lead">{t("otherIntro")}</p>
      {error && <p className="alert" role="alert">{error}</p>}
      {!data && !error && <div className="card loading-card" role="status"><span className="lantern-dot" aria-hidden="true" /> {t("loading")}</div>}
      {data && (
        <>
          <section className="card other-status" aria-labelledby="other-fda">
            <div className="card-top">
              <h2 id="other-fda" className="h3">{t("shortageTitle")}</h2>
              {data.found === false ? <span className="badge badge-unknown">{t("notFound")}</span> : <ShortageBadge status={data.status} />}
            </div>
            <p>{data.found === false ? t("otherNotFound") : data.found === null ? t("otherUnavailable") : data.summary}</p>
            {data.found && <p className="small">{data.fda_estimate ? t("fdaEstimate", { text: data.fda_estimate }) : t("fdaNoEstimate")}</p>}
            {pk && <p className="small">{t("otherPackages", { list: pk })}</p>}
            {names.length > 0 && <p className="small muted">{t("otherAlsoKnown", { names: names.slice(0, 8).join(", ") })}</p>}
            {data.controlled && <p className="notice small">{t("otherControlled", { schedule: data.dea_schedule ?? "" })}</p>}
            <p className="source-line small">FDA · <SourceLink url={data.source} /> · {t("checked", { date: data.checked_date })}</p>
            <div className="card-actions">
              <ReadAloud text={() => [t("otherTitle", { name }), data.found === false ? t("otherNotFound") : data.summary,
                t("otherCoverageNote")].join(". ")} />
            </div>
          </section>
          <p className="notice" role="note"><span aria-hidden="true">ⓘ</span> {t("otherCoverageNote")}</p>
          {data.call_script && <CallScriptCard text={data.call_script} controlled />}
          <div className="card-actions">
            <Link className="btn primary" to="/pharmacies">{t("otherFindPharmacies")}</Link>
            <Link className="btn ghost" to="/">{t("otherBack")}</Link>
          </div>
        </>
      )}
    </div>
  );
}
