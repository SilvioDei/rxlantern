// "Send it here": a one-screen card with the pharmacy's exact name, address, and phone, big and clear, to show the
// doctor's office before they send the prescription. Printable. No personal information. Includes "Before you go".
import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useApp } from "../state";
import { api, type PharmacyBrief } from "../api";
import { ReadAloud } from "../components/Bits";
import { BeforeYouGo } from "../components/Journey";

export function SendHere() {
  const { id = "" } = useParams();
  const [params] = useSearchParams();
  const nav = useNavigate();
  const { t, lang, meta } = useApp();
  const [p, setP] = useState<PharmacyBrief | null>(null);
  const [error, setError] = useState("");
  const drug = meta?.drugs.find((d) => d.id === params.get("drug"));
  useEffect(() => {
    api.get<{ brief: PharmacyBrief }>(`/api/pharmacies/${id}?lang=${lang}`).then((r) => setP(r.brief))
      .catch(() => setError(t("notFound")));
  }, [id, lang, t]);
  if (error) return <p className="alert" role="alert">{error}</p>;
  if (!p) return <p className="muted" role="status">{t("loading")}</p>;
  const hours = p.counter_today === "closed" ? t("closed") : p.counter_today;
  return (
    <div className="send-here-page print-page">
      <div className="no-print card-actions">
        <button type="button" className="link-button back" onClick={() => nav(-1)}>← {t("sendHereBack")}</button>
      </div>
      <section className="send-here-card" aria-labelledby="sh-title">
        <p className="sh-label" id="sh-title">{t("sendHereTitle")}</p>
        {lang === "es" && <p className="sh-label-en" lang="en">{t("sendHereEnglish")}</p>}
        <p className="sh-name">{p.name}</p>
        <p className="sh-address">{p.address}</p>
        <p className="sh-phone"><span aria-hidden="true">📞</span> {p.phone}</p>
        <p className="small">{t("sendHereNoPersonal")}</p>
      </section>
      <p className="no-print">{t("sendHereNote")}</p>
      <BeforeYouGo drugName={drug ? drug.name : null} hoursToday={hours} />
      <div className="card-actions no-print">
        <button type="button" className="btn primary big" onClick={() => window.print()}><span aria-hidden="true">🖨</span> {t("sendHerePrint")}</button>
        <ReadAloud text={() => `${t("sendHereTitle")} ${p.name}. ${p.address}. ${p.phone}.`} />
      </div>
    </div>
  );
}
