// Pharmacies list with filters and an OpenStreetMap map.
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state";
import { api, type PharmacyBrief } from "../api";
import { PharmacyCardView, miles } from "../components/Bits";
import { useOrigin } from "../origin";
import { MapView } from "../components/MapView";

export function Pharmacies() {
  const { t, lang, meta, version } = useApp();
  const { origin } = useOrigin();
  const nav = useNavigate();
  const [all, setAll] = useState<PharmacyBrief[] | null>(null);
  const [error, setError] = useState("");
  const [openNow, setOpenNow] = useState(false);
  const [delivery, setDelivery] = useState(false);
  const [vaccine, setVaccine] = useState("");
  const [language, setLanguage] = useState("");
  const [wheelchair, setWheelchair] = useState(false);
  const [hood, setHood] = useState("");

  useEffect(() => {
    api.get<{ pharmacies: PharmacyBrief[] }>(`/api/pharmacies?lang=${lang}`).then((r) => setAll(r.pharmacies))
      .catch(() => setError(t("errorOffline")));
  }, [lang, t, version]);

  const vaccineOptions = useMemo(() => [...new Set((all ?? []).flatMap((p) => p.vaccines))].sort(), [all]);
  const list = useMemo(() => (all ?? []).filter((p) =>
    (!openNow || p.open_now === true) &&
    (!delivery || p.delivery === "yes") &&
    (!vaccine || p.vaccines.includes(vaccine)) &&
    (!language || (Array.isArray(p.languages) && p.languages.some((l) => l.toLowerCase().includes(language.toLowerCase())))) &&
    (!wheelchair || p.wheelchair_accessible === "yes") &&
    (!hood || p.neighborhood === hood))
    .map((p) => ({ ...p, distance_miles: origin ? Math.round(miles(origin, { lat: p.latitude, lon: p.longitude }) * 10) / 10 : null }))
    .sort((a, b) => (a.distance_miles ?? 0) - (b.distance_miles ?? 0)), [all, openNow, delivery, vaccine, language, wheelchair, hood, origin]);
  const select = useCallback((id: string) => nav(`/pharmacies/${id}`), [nav]);

  return (
    <>
      <h1>{t("pharmaciesTitle")}</h1>
      <p className="lead">{t("pharmaciesIntro")}</p>
      <section className="card filters" aria-label={t("filters")}>
        <label className="check"><input type="checkbox" name="open" checked={openNow} onChange={(e) => setOpenNow(e.target.checked)} /> {t("fOpenNow")}</label>
        <label className="check"><input type="checkbox" checked={delivery} onChange={(e) => setDelivery(e.target.checked)} /> {t("fDelivery")}</label>
        <label className="check"><input type="checkbox" checked={wheelchair} onChange={(e) => setWheelchair(e.target.checked)} /> {t("fWheelchair")}</label>
        <label>{t("fVaccine")}
          <select value={vaccine} onChange={(e) => setVaccine(e.target.value)}>
            <option value="">{t("fAnyVaccine")}</option>
            {vaccineOptions.map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </label>
        <label>{t("fLanguage")}
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="">{t("fAnyLanguage")}</option>
            {["Spanish", "Haitian Creole", "Cantonese", "Mandarin", "Vietnamese", "Portuguese"].map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </label>
        <label>{t("fNeighborhood")}
          <select value={hood} onChange={(e) => setHood(e.target.value)}>
            <option value="">{t("fAllNeighborhoods")}</option>
            {meta?.neighborhoods.map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </label>
      </section>
      {(language || wheelchair) && <p className="notice">{t("notListedNote")}</p>}
      {error && <p className="alert" role="alert">{error}</p>}
      {!all && !error && <p className="muted">{t("loading")}</p>}
      {all && (
        <div className="split">
          <div>
            <p className="muted" aria-live="polite">{t("results", { n: list.length })}</p>
            {list.length === 0 && <div className="card empty"><p>{t("noResults")}</p></div>}
            <div className="cards-grid one-col">
              {list.map((p) => <PharmacyCardView key={p.id} {...p} />)}
            </div>
          </div>
          <div className="map-wrap"><MapView points={list} label={t("mapLabel")} onSelect={select} origin={origin} originLabel={t("youAreHere")} /></div>
        </div>
      )}
    </>
  );
}
