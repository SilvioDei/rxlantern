// About & Privacy: what RxLantern does, where every piece of data comes from (with dates), privacy, checks, limits.
import { useEffect, useState } from "react";
import { useApp } from "../state";
import { api, type Plan } from "../api";
import { SourceLink } from "../components/Bits";
import { ImpactLine } from "../components/Journey";
import type { Key } from "../i18n";

interface About { sources: { key: string; source: string; url: string | null; checked_date: string | null }[]; plans: Plan[] }

const LABELS: Record<string, Record<"en" | "es", string>> = {
  pharmacies: { en: "Pharmacies, hours, and services", es: "Farmacias, horarios y servicios" },
  drugs: { en: "Medicine names", es: "Nombres de medicinas" },
  shortages: { en: "Drug shortages", es: "Escasez de medicinas" },
  nadac: { en: "Cost estimates", es: "Costos estimados" },
  masshealth: { en: "MassHealth coverage", es: "Cobertura de MassHealth" },
  medicare: { en: "Medicare Part D coverage", es: "Cobertura de Medicare Parte D" },
  vaccines: { en: "Vaccine coverage", es: "Cobertura de vacunas" },
  insurance: { en: "Insurance pharmacy finders and phone numbers", es: "Buscadores de farmacias y teléfonos de seguros" },
  zips: { en: "ZIP code locations", es: "Ubicación de códigos postales" },
  holidays: { en: "Holidays", es: "Días festivos" },
  savings: { en: "Savings links (GoodRx, TrumpRx.gov, manufacturers)", es: "Enlaces de ahorro (GoodRx, TrumpRx.gov, fabricantes)" },
};

export function AboutPage() {
  const { t, lang } = useApp();
  const [about, setAbout] = useState<About | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { api.get<About>("/api/about").then(setAbout).catch(() => setError(t("errorGeneric"))); }, [t]);
  const sections: [Key, Key][] = [["aboutPrivacy", "aboutPrivacyText"], ["aboutChecks", "aboutChecksText"],
    ["aboutAdvice", "aboutAdviceText"], ["aboutWrong", "aboutWrongText"], ["aboutAI", "aboutAIText"], ["aboutVoice", "aboutVoiceText"]];

  return (
    <>
      <h1>{t("aboutTitle")}</h1>
      <p className="about-disclaimer muted">{t("aboutDisclaimer")}</p>
      <section className="card"><h2>{t("aboutWhat")}</h2><p>{t("aboutWhatText")}</p></section>
      <ImpactLine full />
      <div className="two-col">
        {sections.map(([h, p]) => (
          <section key={h} className="card" id={h === "aboutVoice" ? "voice" : undefined}>
            <h2>{t(h)}</h2><p>{t(p)}</p>
            {h === "aboutVoice" && <p className="mic-note-about"><span aria-hidden="true">ⓘ</span> {t("micNote")}</p>}
          </section>
        ))}
      </div>
      <section className="card" aria-labelledby="data-title">
        <h2 id="data-title">{t("aboutData")}</h2>
        {error && <p className="alert" role="alert">{error}</p>}
        {!about && !error && <p className="muted" role="status">{t("loading")}</p>}
        {about && (
          <div className="table-wrap">
            <table className="data-table">
              <thead><tr><th scope="col">{t("aboutDataCol1")}</th><th scope="col">{t("aboutDataCol2")}</th><th scope="col">{t("aboutDataCol3")}</th></tr></thead>
              <tbody>
                {about.sources.map((s) => (
                  <tr key={s.key}>
                    <th scope="row">{LABELS[s.key]?.[lang] ?? s.key}</th>
                    <td>{s.source}{s.url && <> · <SourceLink url={s.url} /></>}</td>
                    <td>{s.checked_date ?? t("notFound")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {about && (
        <section className="card" aria-labelledby="plans-title">
          <h2 id="plans-title">{t("aboutPlans")}</h2>
          <div className="table-wrap">
            <table className="data-table">
              <tbody>
                {about.plans.filter((p) => p.id !== "other_commercial").map((p) => (
                  <tr key={p.id}>
                    <th scope="row">{p.name}</th>
                    <td>{p.pharmacy_finder_url !== "not found" ? <SourceLink url={p.pharmacy_finder_url} /> : <span className="muted">{t("planFinderNotFound")}</span>}</td>
                    <td>{p.member_services_phone === "not found" ? t("notFound") : p.member_services_phone}</td>
                    <td className="small">{t("checked", { date: p.checked_date })}{p.source_url !== "not found" && <> · <SourceLink url={p.source_url.split(" ; ")[0]} /></>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
      {lang === "es" && <p className="small">{t("dataEnglishNote")}</p>}
    </>
  );
}
