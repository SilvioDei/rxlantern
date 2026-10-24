// Vaccines: choose one, see nearby pharmacies that list it (with booking links), and who pays by insurance type
// (Massachusetts rule, large-employer warning, travel vaccines "check with your plan", yellow fever certified sites).
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";
import { useOrigin } from "../origin";
import { SourceLink, miles, telHref } from "../components/Bits";

interface Vaccine {
  id: string; name: string; group: string; checked_date: string; certified_sites_only: boolean; clinic_finder: string | null;
  pharmacies: { id: string; name: string; address: string; neighborhood: string; phone: string; latitude: number; longitude: number; booking_url: string }[];
  medicare: { part: string; coverage: string; cost: string; source: string };
  masshealth: { coverage: string; cost: string; source: string };
  commercial: { coverage: string; cost: string; source: string;
    massachusetts: { rule: string; coverage: string; cost: string; patient_message: string; applies_to?: string; sources: string[]; verification: string } };
  notes: string[];
}

export function Vaccines() {
  const { t, lang, place, set } = useApp();
  const { origin } = useOrigin();
  const [list, setList] = useState<Vaccine[] | null>(null);
  const [error, setError] = useState("");
  const [chosen, setChosen] = useState("flu");
  useEffect(() => { api.get<{ vaccines: Vaccine[] }>("/api/vaccines").then((r) => setList(r.vaccines)).catch(() => setError(t("errorOffline"))); }, [t]);
  const v = list?.find((x) => x.id === chosen);
  const nearby = useMemo(() => (v?.pharmacies ?? [])
    .map((p) => ({ ...p, dist: origin ? Math.round(miles(origin, { lat: p.latitude, lon: p.longitude }) * 10) / 10 : null }))
    .sort((a, b) => (a.dist ?? 0) - (b.dist ?? 0)), [v, origin]);

  return (
    <>
      <h1>{t("vaccinesTitle")}</h1>
      <p className="lead">{t("vaccinesIntro")}</p>
      {error && <p className="alert" role="alert">{error}</p>}
      {!list && !error && <p className="muted" role="status">{t("loading")}</p>}
      {list && (
        <section className="card" aria-labelledby="pick-vaccine">
          <h2 id="pick-vaccine" className="h3">{t("chooseVaccine")}</h2>
          <div className="chips" role="group" aria-labelledby="pick-vaccine">
            {list.map((x) => (
              <button key={x.id} type="button" className={`chip ${chosen === x.id ? "chip-on" : ""}`} aria-pressed={chosen === x.id}
                onClick={() => setChosen(x.id)}>{x.name}{x.group === "travel" ? ` (${t("travel")})` : ""}</button>
            ))}
          </div>
          <label className="inline-label">{t("step2Label")}
            <input value={place} placeholder={t("placePlaceholder")} maxLength={40} onChange={(e) => set({ place: e.target.value })} name="place" />
          </label>
        </section>
      )}
      {v && (
        <div className="two-col">
          <section className="card" aria-labelledby="vax-where">
            <div className="card-top">
              <h2 id="vax-where">{v.name}</h2>
              <span className={`badge ${v.group === "travel" ? "badge-unknown" : "badge-ok"}`}>{v.group === "travel" ? t("travel") : t("routine")}</span>
            </div>
            {v.certified_sites_only && (
              <p className="alert"><strong>{t("yellowFever")}</strong>{" "}
                {v.clinic_finder && <a href={v.clinic_finder} target="_blank" rel="noreferrer">{t("findClinic")} ↗</a>}</p>
            )}
            <h3>{t("offeredAt")}</h3>
            {nearby.length ? (
              <ul className="feed">
                {nearby.map((p) => (
                  <li key={p.id} className="feed-item">
                    <Link to={`/pharmacies/${p.id}`}><strong>{p.name}</strong></Link> — {p.address}{p.dist != null && <span className="muted"> · {t("away", { miles: p.dist })}</span>}
                    <div className="card-actions">
                      {p.booking_url && p.booking_url !== "not found" && <a className="btn primary" href={p.booking_url} target="_blank" rel="noreferrer">{t("bookVaccine")} ↗</a>}
                      <a className="btn ghost" href={telHref(p.phone)}>{t("call")} {p.phone}</a>
                    </div>
                  </li>
                ))}
              </ul>
            ) : <p className="muted">{t("noneListed")}</p>}
            <p className="muted small">{t("vaccinesNote")}</p>
          </section>
          <section className="card" aria-labelledby="vax-pay">
            <h2 id="vax-pay">{t("coverage")}</h2>
            {v.group === "travel" && <p className="notice"><strong>{t("travelCheck")}</strong></p>}
            <dl className="coverage">
              <dt>{t("medicare")} {v.medicare.part !== "not found" && `(Part ${v.medicare.part})`}</dt>
              <dd>{v.medicare.coverage} {v.medicare.cost} <SourceLink url={v.medicare.source} /></dd>
              <dt>{t("masshealth")}</dt>
              <dd>{v.masshealth.coverage} {v.masshealth.cost} <SourceLink url={v.masshealth.source} /></dd>
              <dt>{t("commercial")}{v.group !== "travel" && ` — ${t("maRule")}`}</dt>
              <dd>{v.group === "travel" ? t("travelCheck") : <><strong>{v.commercial.massachusetts.rule}.</strong> {v.commercial.massachusetts.coverage} {v.commercial.massachusetts.cost}</>}
                {" "}{v.commercial.massachusetts.sources?.[0] && <SourceLink url={v.commercial.massachusetts.sources[0]} />} <span className="muted small">({v.commercial.massachusetts.verification})</span></dd>
              {v.group !== "travel" && (<><dt>{t("employerWarning")}</dt><dd className="warn-text">{v.commercial.massachusetts.patient_message}</dd></>)}
              <dt>{t("uninsured")}</dt>
              <dd>{t("uninsuredVaccine")}</dd>
            </dl>
            <p className="muted small">{t("checked", { date: v.checked_date })}</p>
            {lang === "es" && <p className="small">{t("dataEnglishNote")}</p>}
          </section>
        </div>
      )}
    </>
  );
}
