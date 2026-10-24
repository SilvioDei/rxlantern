// Home: "Ask RxLantern" box, quick starts, optional details (saved in this browser only), and answers.
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state";
import { api, ApiError, type FinalReply } from "../api";
import { Answer } from "../components/Answer";
import { ReportForm } from "../components/Forms";
import { Logo } from "../components/Logo";
import { STRINGS } from "../i18n";
import { listen, recognitionSupported } from "../speech";

interface Turn { question: string; reply?: FinalReply; error?: string }

export function Home() {
  const { t, lang, easy, place, insurance, set, meta, requireLogin } = useApp();
  const nav = useNavigate();
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(0);
  const [listening, setListening] = useState(false);
  const [reportOpen, setReportOpen] = useState(false);
  const box = useRef<HTMLTextAreaElement>(null);
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
        ? (e.code === "rate" ? t("errorRate") : e.code === "offline" ? t("errorOffline") : e.status === 429 ? t("errorBusy") : t("errorGeneric"))
        : t("errorGeneric");
      setTurns((ts) => ts.map((x, i) => (i === ts.length - 1 ? { ...x, error: msg } : x)));
    } finally {
      setBusy(false);
      setTimeout(() => answers.current?.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    }
  };

  const submit = (e: FormEvent) => { e.preventDefault(); ask(question); };
  const prefill = (text: string) => { setQuestion(text); setTimeout(() => { box.current?.focus(); box.current?.setSelectionRange(text.length, text.length); }, 0); };
  const micOk = easy && recognitionSupported();

  return (
    <>
      <section className="hero">
        <div className="hero-logo"><Logo size={easy ? 76 : 96} /></div>
        <h1>{t("heroTitle")}</h1>
        <p className="lead">{t("heroText")}</p>
      </section>

      <section className="ask-panel card" aria-labelledby="ask-label">
        <form onSubmit={submit}>
          <label id="ask-label" htmlFor="ask-box" className="ask-label">{t("askLabel")}</label>
          <div className="ask-row">
            <textarea id="ask-box" ref={box} rows={easy ? 3 : 2} value={question} maxLength={1000}
              placeholder={t("askPlaceholder")} onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(question); } }} />
            <div className="ask-buttons">
              {micOk && (
                <button type="button" className={`btn mic ${listening ? "listening" : ""}`} aria-pressed={listening}
                  onClick={() => {
                    setListening(true);
                    listen(lang, (txt) => setQuestion((q) => (q ? `${q} ${txt}` : txt)), () => setListening(false));
                  }}>
                  <span aria-hidden="true">🎤</span> {listening ? t("micListening") : t("micStart")}
                </button>
              )}
              <button type="submit" className="btn primary big" disabled={busy || !question.trim()}>{t("askButton")}</button>
            </div>
          </div>
        </form>

        <div className="quick" role="group" aria-label={t("quickTitle")}>
          <button type="button" className="quick-btn" onClick={() => ask(place.trim() ? t("qOpenText", { place: place.trim() }) : t("qOpenNoPlace"))}>
            <span aria-hidden="true">🕯️</span> {t("qOpen")}</button>
          <button type="button" className="quick-btn" onClick={() => prefill(t("qShortageText"))}><span aria-hidden="true">📋</span> {t("qShortage")}</button>
          <button type="button" className="quick-btn" onClick={() => prefill(t("qCostText"))}><span aria-hidden="true">💲</span> {t("qCost")}</button>
          <button type="button" className="quick-btn" onClick={() => nav("/vaccines")}><span aria-hidden="true">💉</span> {t("qVaccines")}</button>
          <button type="button" className="quick-btn" onClick={() => requireLogin(() => setReportOpen(true))}><span aria-hidden="true">☎️</span> {t("qCalled")}</button>
        </div>

        <details className="details-box" open={!!(place || insurance)}>
          <summary>{t("detailsTitle")}</summary>
          <div className="details-grid">
            <label>{t("placeLabel")}
              <input value={place} list="neighborhoods" placeholder={t("placePlaceholder")} maxLength={40}
                onChange={(e) => set({ place: e.target.value })} />
              <datalist id="neighborhoods">{meta?.neighborhoods.map((n) => <option key={n} value={n} />)}</datalist>
            </label>
            <label>{t("insuranceLabel")}
              <select value={insurance} onChange={(e) => set({ insurance: e.target.value })}>
                <option value="">{t("insNone")}</option>
                {(meta?.insurance_types ?? []).map((i) => <option key={i} value={i}>{t(`ins_${i}` as never)}</option>)}
              </select>
            </label>
          </div>
          <p className="privacy"><span aria-hidden="true">🔒</span> {t("privacyNote")}</p>
        </details>
      </section>

      <div className="conversation" ref={answers}>
        {turns.map((turn, i) => (
          <div key={i} className="turn">
            <p className="you-asked"><span className="muted">›</span> {turn.question}</p>
            {turn.reply && <Answer reply={turn.reply} onFollowUp={(a) => ask(`${turn.question} — ${a}`)} />}
            {turn.error && <p className="alert" role="alert">{turn.error}</p>}
            {!turn.reply && !turn.error && busy && i === turns.length - 1 && (
              <div className="working card" role="status" aria-live="polite">
                <span className="lantern-dot" aria-hidden="true" />
                {(STRINGS[lang].working as string[])[step]}
              </div>
            )}
          </div>
        ))}
      </div>
      {reportOpen && <ReportForm onClose={() => setReportOpen(false)} />}
    </>
  );
}
