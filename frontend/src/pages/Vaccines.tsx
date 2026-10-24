// Vaccines: which pharmacies list each one, and coverage by insurance (Massachusetts rule + large-employer warning).
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";

interface Vaccine {
  id: string; name: string; group: string; checked_date: string; certified_sites_only: boolean; clinic_finder: string | null;
  pharmacies: { id: string; name: string; address: string; neighborhood: string }[];
  medicare: { part: string; coverage: string; cost: string; source: string };
  masshealth: { coverage: string; cost: string; source: string };
  commercial: { coverage: string; cost: string; source: string;
    massachusetts: { rule: string; coverage: string; cost: string; patient_message: string; applies_to?: string; sources: string[]; verification: string } };
  notes: string[];
}

function Src({ url }: { url: string }) {
  if (!/^https?:/.test(url)) return null;
  return <a className="src" href={url} target="_blank" rel="noreferrer">{new URL(url).hostname.replace(/^www\./, "")}</a>;
}

export function Vaccines() {
  const { t } = useApp();
  const [list, setList] = useState<Vaccine[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { api.get<{ vaccines: Vaccine[] }>("/api/vaccines").then((r) => setList(r.vaccines)).catch(() => setError(t("errorOffline"))); }, [t]);

  return (
    <>
      <h1>{t("vaccinesTitle")}</h1>
      <p className="lead">{t("vaccinesIntro")}</p>
      {error && <p className="alert">{error}</p>}
      {!list && !error && <p className="muted">{t("loading")}</p>}
      <div className="vaccine-list">
        {list?.map((v) => {
          const ma = v.commercial.massachusetts;
          return (
            <article key={v.id} className="card vaccine-card">
              <div className="card-top">
                <h2 className="h3">{v.name}</h2>
                <span className={`badge ${v.group === "travel" ? "badge-warn" : "badge-ok"}`}>{v.group === "travel" ? t("travel") : t("routine")}</span>
              </div>
              {v.certified_sites_only && (
                <p className="notice"><strong>{t("yellowFever")}</strong>{" "}
                  {v.clinic_finder && <a href={v.clinic_finder} target="_blank" rel="noreferrer">{t("findClinic")}</a>}</p>
              )}
              <h3>{t("offeredAt")}</h3>
              {v.pharmacies.length ? (
                <ul className="small">{v.pharmacies.map((p) => <li key={p.id}><Link to={`/pharmacies/${p.id}`}>{p.name}</Link> — {p.address}</li>)}</ul>
              ) : <p className="muted small">{t("noneListed")}</p>}
              <h3>{t("coverage")}</h3>
              <dl className="coverage">
                <dt>{t("medicare")} {v.medicare.part !== "not found" && `(Part ${v.medicare.part})`}</dt>
                <dd>{v.medicare.coverage} {v.medicare.cost} <Src url={v.medicare.source} /></dd>
                <dt>{t("masshealth")}</dt>
                <dd>{v.masshealth.coverage} {v.masshealth.cost} <Src url={v.masshealth.source} /></dd>
                <dt>{t("commercial")} — {t("maRule")}</dt>
                <dd><strong>{ma.rule}.</strong> {ma.coverage} {ma.cost} {ma.sources?.[0] && <Src url={ma.sources[0]} />} <span className="muted small">({ma.verification})</span></dd>
                {v.group !== "travel" && (<><dt>{t("employerWarning")}</dt><dd className="warn-text">{ma.patient_message}</dd></>)}
              </dl>
              <p className="muted small">{t("checked", { date: v.checked_date })}</p>
            </article>
          );
        })}
      </div>
    </>
  );
}
