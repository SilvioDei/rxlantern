// Home: a compact medicine search bar at the top, "How it works", the 3-step guided search (medicine, place,
// insurance), and the "Ask RxLantern" chat. The top bar starts the same guided search.
import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state";
import { api, ApiError, type DrugMeta, type FinalReply, type VaccineMeta } from "../api";
import { Answer } from "../components/Answer";
import { MicButton, MicNote } from "../components/Bits";
import { MedicineSearch } from "../components/MedicineSearch";
import { ImpactLine, WatchHighlights } from "../components/Journey";
import { STRINGS } from "../i18n";
import { medicines, optionFromQuery, vaccineItems, type Medicine } from "../search";

/** A medicine picked in the top search bar, handed to the guided search (n changes on every pick). */
interface Preset { m: Medicine; query: string; n: number }

interface Turn { question: string; reply?: FinalReply; error?: string }

function HowItWorks() {
  const { t } = useApp();
  const steps = [["how1Title", "how1", "💊"], ["how2Title", "how2", "🏥"], ["how3Title", "how3", "📞"]] as const;
  return (
    <section className="how" aria-labelledby="how-title">
      <h2 id="how-title">{t("howTitle")}</h2>
      <ol className="how-steps">
        {steps.map(([title, text, icon], i) => (
          <li key={title} className="how-step">
            <span className="how-num" aria-hidden="true">{i + 1}</span>
            <div><h3><span aria-hidden="true">{icon}</span> {t(title)}</h3><p>{t(text)}</p></div>
          </li>
        ))}
      </ol>
    </section>
  );
}

function DrugStep({ chosen, setChosen, vaccine, setVaccine, preset }: {
  chosen: DrugMeta | null; setChosen: (d: DrugMeta | null) => void;
  vaccine: VaccineMeta | null; setVaccine: (v: VaccineMeta | null) => void; preset: Preset | null;
}) {
  const { t, meta } = useApp();
  const meds = useMemo(() => medicines(meta?.drugs ?? []), [meta]);
  const [medicine, setMedicine] = useState<Medicine | null>(null);

  // Coming back to the page: show the medicine or vaccine chosen last time.
  useEffect(() => {
    if (chosen && !medicine) setMedicine(meds.find((m) => m.options.some((o) => o.id === chosen.id)) ?? null);
    else if (vaccine && !medicine) setMedicine(vaccineItems([vaccine])[0]);
  }, [chosen, vaccine, meds, medicine]);

  const pick = (m: Medicine, query: string) => {
    setMedicine(m);
    if (m.vaccine) { setChosen(null); setVaccine(m.vaccine); }
    else { setVaccine(null); setChosen(optionFromQuery(query, m)); }
  };
  // A medicine picked in the top search bar starts this same guided search.
  useEffect(() => { if (preset) pick(preset.m, preset.query); }, [preset?.n]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="step-block">
      <p className="step-num">{t("step", { n: 1 })}</p>
      {!medicine ? (
        <MedicineSearch id="drug-search" listId="drug-list" label={t("step1Label")} help={t("step1Help")}
          placeholder={t("step1Placeholder")} onPick={pick} withVaccines />
      ) : (
        <>
          <p className="step-label">{t("step1Label")}</p>
          <div className="chosen-row">
            <span className="chosen"><span aria-hidden="true">✓</span> {medicine.label}</span>
            {medicine.controlled && <span className="badge badge-warn">{t("controlledBadge")}</span>}
            {medicine.vaccine && <span className="badge badge-ok vaccine-badge"><span aria-hidden="true">💉</span> {t("vaccineBadge")}</span>}
            <button type="button" className="link-button" onClick={() => { setMedicine(null); setChosen(null); setVaccine(null); }}>{t("changeDrug")}</button>
          </div>
          {medicine.vaccine ? <p className="muted small vaccine-next" id="vaccine-chosen">{t("vaccineChosenNote")}</p> : (
          <fieldset className="option-list">
            <legend>{medicine.options.length > 1 ? t("pickStrength") : t("pickStrengthOne")}</legend>
            {medicine.options.map((o) => (
              <label key={o.id} className={`option ${chosen?.id === o.id ? "on" : ""}`}>
                <input type="radio" name="drug-option" checked={chosen?.id === o.id} onChange={() => setChosen(o)} />
                <span><strong>{o.strength}</strong> · {o.form}</span>
              </label>
            ))}
          </fieldset>)}
        </>
      )}
    </div>
  );
}

function PlaceStep({ error }: { error: string }) {
  const { t, place, set, meta, deviceOrigin, setDeviceOrigin } = useApp();
  const [locating, setLocating] = useState(false);
  const [geoError, setGeoError] = useState("");
  return (
    <div className="step-block">
      <p className="step-num">{t("step", { n: 2 })}</p>
      <label htmlFor="place" className="step-label">{t("step2Label")}</label>
      <p className="muted small">{t("step2Help")}</p>
      <div className="input-row">
        <input id="place" value={deviceOrigin ? "" : place} list="neighborhoods" placeholder={t("placePlaceholder")} maxLength={40}
          disabled={!!deviceOrigin} onChange={(e) => set({ place: e.target.value })} />
        <datalist id="neighborhoods">{meta?.neighborhoods.map((n) => <option key={n} value={n} />)}</datalist>
        {!deviceOrigin && <MicButton onText={(txt) => set({ place: txt.replace(/[.!?]+$/, "").slice(0, 40) })} />}
        {deviceOrigin ? (
          <button type="button" className="btn ghost" onClick={() => setDeviceOrigin(null)}>{t("changeDrug")}</button>
        ) : (
          <button type="button" className="btn ghost" disabled={locating || !("geolocation" in navigator)} onClick={() => {
            setLocating(true);
            setGeoError("");
            navigator.geolocation.getCurrentPosition(
              (pos) => { setDeviceOrigin({ lat: pos.coords.latitude, lon: pos.coords.longitude, label: "", fromDevice: true }); setLocating(false); },
              () => { setGeoError(t("locationError")); setLocating(false); },
              { timeout: 10000, maximumAge: 300000 });
          }}><span aria-hidden="true">📍</span> {locating ? t("locating") : t("useLocation")}</button>
        )}
      </div>
      {deviceOrigin && <p className="notice small"><span aria-hidden="true">📍</span> {t("usingLocation")}</p>}
      {(geoError || error) && <p className="alert small" role="alert">{geoError || error}</p>}
    </div>
  );
}

function InsuranceStep() {
  const { t, insurance, plan, set, meta } = useApp();
  const options = ["masshealth", "medicare", "commercial", "uninsured", ""] as const;
  return (
    <div className="step-block">
      <p className="step-num">{t("step", { n: 3 })}</p>
      <fieldset className="option-list ins-list">
        <legend className="step-label">{t("step3Label")}</legend>
        <p className="muted small">{t("step3Help")}</p>
        {options.map((o) => (
          <label key={o || "unsure"} className={`option ${insurance === o ? "on" : ""}`}>
            <input type="radio" name="insurance" checked={insurance === o} onChange={() => set({ insurance: o })} />
            <span>{o ? t(`ins_${o}` as never) : t("insUnsure")}</span>
          </label>
        ))}
      </fieldset>
      {insurance === "commercial" && (
        <label className="plan-select">{t("planLabel")}
          <select value={plan} onChange={(e) => set({ plan: e.target.value })}>
            <option value="">{t("planPick")}</option>
            {meta?.plans.filter((p) => p.type === "commercial").map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
      )}
    </div>
  );
}

function GuidedSearch({ preset }: { preset: Preset | null }) {
  const { t, meta, drugId, vaccineId, set, place, deviceOrigin } = useApp();
  const nav = useNavigate();
  const [chosen, setChosenState] = useState<DrugMeta | null>(null);
  const [vaccine, setVaccineState] = useState<VaccineMeta | null>(null);
  useEffect(() => { if (meta && vaccineId && !vaccine) setVaccineState(meta.vaccines.find((v) => v.id === vaccineId) ?? null); }, [meta, vaccineId, vaccine]);
  const setVaccine = (v: VaccineMeta | null) => { setVaccineState(v); set({ vaccineId: v?.id ?? "" }); };
  const [error, setError] = useState<{ drug?: string; place?: string }>({});
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (meta && drugId && !chosen) setChosenState(meta.drugs.find((d) => d.id === drugId) ?? null); }, [meta, drugId, chosen]);
  const setChosen = (d: DrugMeta | null) => { setChosenState(d); set({ drugId: d?.id ?? "" }); };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const errs: { drug?: string; place?: string } = {};
    if (!chosen && !vaccine) errs.drug = t("needDrug");
    if (!deviceOrigin && !place.trim()) errs.place = t("needPlace");
    if (!errs.place && !deviceOrigin) {
      setBusy(true);
      try {
        const loc = await api.get<{ found: boolean }>(`/api/location?place=${encodeURIComponent(place.trim())}`);
        if (!loc.found) errs.place = t("placeNotFound");
      } catch {
        errs.place = t("errorOffline");
      }
      setBusy(false);
    }
    setError(errs);
    if (!errs.drug && !errs.place && vaccine) nav(`/vaccine-results?vaccine=${vaccine.id}`);
    else if (!errs.drug && !errs.place && chosen) nav(`/results?drug=${chosen.id}`);
  };

  return (
    <section className="card search-card" id="guided-search" aria-labelledby="search-title">
      <h2 id="search-title">{t("searchTitle")}</h2>
      <form onSubmit={submit} noValidate>
        <div className="steps-grid">
          <DrugStep chosen={chosen} setChosen={setChosen} vaccine={vaccine} setVaccine={setVaccine} preset={preset} />
          <PlaceStep error={error.place ?? ""} />
          <InsuranceStep />
        </div>
        {error.drug && <p className="alert" role="alert">{error.drug}</p>}
        <div className="search-submit">
          <button type="submit" className="btn primary big" disabled={busy}><span aria-hidden="true">🔎</span> {t("findButton")}</button>
          <p className="privacy"><span aria-hidden="true">🔒</span> {t("privacyNote")}</p>
        </div>
      </form>
    </section>
  );
}

function Chat() {
  const { t, lang, place, insurance } = useApp();
  const nav = useNavigate();
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(0);
  const answers = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!busy) return;
    const id = setInterval(() => setStep((s) => (s + 1) % STRINGS[lang].working.length), 2600);
    return () => clearInterval(id);
  }, [busy, lang]);

  const ask = async (q: string) => {
    const text = q.trim();
    if (!text || busy) return;
    const zip = /^\d{5}$/.test(place.trim()) ? place.trim() : undefined;
    const withPlace = !zip && place.trim() && !text.toLowerCase().includes(place.trim().toLowerCase())
      ? `${text} (${lang === "es" ? "Estoy cerca de" : "I'm near"} ${place.trim()})` : text;
    setBusy(true);
    setStep(0);
    setTurns((ts) => [...ts, { question: text }]);
    setQuestion("");
    try {
      const reply = await api.post<FinalReply>("/api/ask", {
        question: withPlace, language: lang, zip_code: zip, insurance_type: insurance || undefined,
      });
      setTurns((ts) => ts.map((x, i) => (i === ts.length - 1 ? { ...x, reply } : x)));
    } catch (e) {
      const msg = e instanceof ApiError
        ? (e.code === "rate" ? t("errorRate") : e.code === "offline" ? t("errorOffline") : e.code === "bad_key" ? t("errorKey")
          : e.status === 429 ? t("errorBusy") : t("errorGeneric"))
        : t("errorGeneric");
      setTurns((ts) => ts.map((x, i) => (i === ts.length - 1 ? { ...x, error: msg } : x)));
    } finally {
      setBusy(false);
      setTimeout(() => answers.current?.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    }
  };

  return (
    <section className="card ask-panel" aria-labelledby="ask-title">
      <h2 id="ask-title">{t("orAsk")}</h2>
      <form onSubmit={(e) => { e.preventDefault(); ask(question); }}>
        <label htmlFor="ask-box" className="sr-only">{t("askLabel")}</label>
        <div className="ask-row">
          <textarea id="ask-box" rows={2} value={question} maxLength={1000} placeholder={t("askPlaceholder")}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(question); } }} />
          <div className="ask-buttons">
            <MicButton onText={(txt) => setQuestion((q) => (q ? `${q} ${txt}` : txt))} />
            <button type="submit" className="btn primary big" disabled={busy || !question.trim()}>{t("askButton")}</button>
          </div>
        </div>
        <MicNote />
      </form>
      <div className="quick" role="group" aria-label={t("quickTitle")}>
        <button type="button" className="quick-btn" onClick={() => ask(place.trim() ? t("qOpenText", { place: place.trim() }) : t("qOpenNoPlace"))}>
          <span aria-hidden="true">🕯️</span> {t("qOpen")}</button>
        <button type="button" className="quick-btn" onClick={() => nav("/vaccines")}><span aria-hidden="true">💉</span> {t("qVaccines")}</button>
        <button type="button" className="quick-btn" onClick={() => nav("/shortages")}><span aria-hidden="true">📋</span> {t("qShortages")}</button>
      </div>
      <div className="conversation" ref={answers}>
        {turns.map((turn, i) => (
          <div key={i} className="turn">
            <p className="you-asked"><span className="muted" aria-hidden="true">›</span> {turn.question}</p>
            {turn.reply && <Answer reply={turn.reply} onFollowUp={(a) => ask(`${turn.question} — ${a}`)} />}
            {turn.error && <p className="alert" role="alert">{turn.error}</p>}
            {!turn.reply && !turn.error && busy && i === turns.length - 1 && (
              <div className="working" role="status" aria-live="polite">
                <span className="lantern-dot" aria-hidden="true" />
                {(STRINGS[lang].working as string[])[step]}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function TopSearch({ onPick }: { onPick: (m: Medicine, query: string) => void }) {
  const { t } = useApp();
  const nav = useNavigate();
  return (
    <section className="top-search" aria-label={t("topSearchLabel")}>
      <MedicineSearch id="top-search" listId="top-search-list" label={t("topSearchLabel")} labelClass="top-search-label"
        placeholder={t("step1Placeholder")} submitLabel={t("topSearchButton")} onPick={onPick} withVaccines
        onNoMatch={(q) => nav(`/other-medicine?name=${encodeURIComponent(q)}`)} />
    </section>
  );
}

export function Home() {
  const { t } = useApp();
  const [preset, setPreset] = useState<Preset | null>(null);
  const startGuided = (m: Medicine, query: string) => {
    setPreset((p) => ({ m, query, n: (p?.n ?? 0) + 1 }));
    // Show the guided search with the medicine filled in; the patient confirms the strength, then the place.
    setTimeout(() => {
      const card = document.getElementById("guided-search");
      card?.scrollIntoView({ behavior: "smooth", block: "start" });
      card?.querySelector<HTMLElement>("input[name=drug-option]:checked, input[name=drug-option], #place")?.focus({ preventScroll: true });
    }, 60);
  };
  return (
    <>
      <TopSearch onPick={startGuided} />
      <WatchHighlights />
      <section className="hero">
        <h1>{t("heroTitle")}</h1>
        <p className="lead">{t("heroText")}</p>
        <ImpactLine />
      </section>
      <HowItWorks />
      <GuidedSearch preset={preset} />
      <Chat />
    </>
  );
}
