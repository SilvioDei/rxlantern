// Small shared pieces: read aloud, voice input, badges, report buttons, call script, call pop-up, sources, modal.
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { canSpeak, listen, recognitionSupported, speak, stopSpeaking } from "../speech";
import { shortageKey } from "../i18n";
import type { Fact } from "../api";

export function ReadAloud({ text, label }: { text: string | (() => string); label?: string }) {
  const { t, lang } = useApp();
  const [on, setOn] = useState(false);
  useEffect(() => () => stopSpeaking(), []);
  if (!canSpeak()) return null;
  return (
    <button type="button" className="btn ghost" aria-pressed={on}
      onClick={() => {
        if (on) { stopSpeaking(); setOn(false); }
        else { setOn(true); speak(typeof text === "function" ? text() : text, lang, () => setOn(false)); }
      }}>
      <span aria-hidden="true">{on ? "■" : "🔊"}</span> {on ? t("stopReading") : (label ?? t("readAloud"))}
    </button>
  );
}

/** Microphone button (browser speech recognition). Shown to everyone; in a browser without speech recognition
 *  it says so and asks the patient to type. */
export function MicButton({ onText }: { onText: (text: string) => void }) {
  const { t, lang, notify } = useApp();
  const [listening, setListening] = useState(false);
  return (
    <button type="button" className={`btn ghost mic ${listening ? "listening" : ""}`} aria-pressed={listening}
      title={t("micNote")}
      onClick={() => {
        if (!recognitionSupported()) { notify(t("micUnsupported"), false); return; }
        setListening(true);
        listen(lang, onText, () => setListening(false));
      }}>
      <span aria-hidden="true">🎤</span> {listening ? t("micListening") : t("micStart")}
    </button>
  );
}

/** The privacy note shown by the microphone. */
export function MicNote() {
  const { t } = useApp();
  return <p className="mic-note"><span aria-hidden="true">ⓘ</span> {t("micNote")}</p>;
}

export function SampleBadge() {
  const { t } = useApp();
  return <span className="badge badge-sample" title={t("sampleExplain")}>{t("sample")}</span>;
}

export function OpenBadge({ open, opensNext, status }: { open: boolean | null; opensNext?: string | null; status?: string }) {
  const { t } = useApp();
  if (open === true) return <span className="badge badge-open"><span aria-hidden="true">●</span> {t("openNow")}</span>;
  if (open === false) {
    if (!opensNext || opensNext === "not found") return <span className="badge badge-closed">{t("closed")}</span>;
    return <span className="badge badge-closed">{t(status === "closed for lunch" ? "closedLunch" : "closedOpens", { when: opensNext })}</span>;
  }
  return <span className="badge badge-unknown">{t("hoursUnknown")}</span>;
}

export function ShortageBadge({ status }: { status: string }) {
  const { t } = useApp();
  const k = shortageKey(status);
  const cls = k === "st_in_shortage" ? "badge-warn" : k === "st_not_listed" || k === "st_resolved" ? "badge-ok" : "badge-unknown";
  return <span className={`badge ${cls}`}>{k === "st_in_shortage" ? "⚠ " : ""}{t(k)}</span>;
}

export function Stars({ n }: { n: number }) {
  const { t } = useApp();
  return <span className="stars-inline" role="img" aria-label={t("stars", { n })}>{"★".repeat(n)}{"☆".repeat(5 - n)}</span>;
}

export function telHref(phone: string) {
  return `tel:+1${phone.replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "")}`;
}

export function directionsHref(address: string) {
  return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(address)}`;
}

export function fmtTime(iso: string, lang: string) {
  try { return new Date(iso).toLocaleString(lang === "es" ? "es-US" : "en-US", { dateStyle: "medium", timeStyle: "short" }); }
  catch { return iso; }
}

export function ago(iso: string, lang: string) {
  const mins = Math.max(1, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  const rtf = new Intl.RelativeTimeFormat(lang === "es" ? "es" : "en", { numeric: "auto" });
  return mins < 60 ? rtf.format(-mins, "minute") : mins < 48 * 60 ? rtf.format(-Math.round(mins / 60), "hour") : rtf.format(-Math.round(mins / 1440), "day");
}

/** "I called: They have it / They don't" (pre-filled). Never shown for controlled medicines. */
export function ReportButtons({ pharmacyId, drugId, controlled, compact }: { pharmacyId?: string; drugId?: string | null; controlled?: boolean; compact?: boolean }) {
  const { t, report } = useApp();
  if (controlled) return null;
  return (
    <div className={`report-buttons ${compact ? "compact" : ""}`} role="group" aria-label={t("afterCall")}>
      <button type="button" className="btn report-yes" onClick={() => report({ pharmacyId, drugId: drugId ?? undefined, inStock: true })}>
        <span aria-hidden="true">✓</span> {t("iHaveIt")}</button>
      <button type="button" className="btn report-no" onClick={() => report({ pharmacyId, drugId: drugId ?? undefined, inStock: false })}>
        <span aria-hidden="true">✕</span> {t("iDontHaveIt")}</button>
    </div>
  );
}

export function CallScriptCard({ text, drugId, pharmacyId, controlled, title }: { text: string; drugId?: string | null; pharmacyId?: string; controlled?: boolean; title?: string }) {
  const { t } = useApp();
  const [copied, setCopied] = useState(false);
  return (
    <section className="card script-card">
      <h3>{title ?? t("callScriptTitle")}</h3>
      <p className="script-text">{text}</p>
      <div className="card-actions">
        <button type="button" className="btn ghost" onClick={async () => {
          try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { /* ignore */ }
        }}>{copied ? t("copied") : t("copy")}</button>
        <ReadAloud text={text} />
      </div>
      {!controlled && (
        <>
          <p className="after-call">{t("afterCall")}</p>
          <ReportButtons pharmacyId={pharmacyId} drugId={drugId} />
        </>
      )}
    </section>
  );
}

/** "Call" opens this: the script first, then the dial button, then the report buttons. */
export function CallModal({ name, phone, script, pharmacyId, drugId, controlled, onClose }: {
  name: string; phone: string; script: string; pharmacyId: string; drugId?: string | null; controlled?: boolean; onClose: () => void;
}) {
  const { t } = useApp();
  return (
    <Modal title={t("callModalTitle", { name })} onClose={onClose}>
      <p className="muted">{t("callModalHelp")}</p>
      <p className="script-text script-box">{script}</p>
      <div className="card-actions">
        <a className="btn primary big" href={telHref(phone)}><span aria-hidden="true">📞</span> {t("dialNow", { phone })}</a>
        <ReadAloud text={script} />
      </div>
      {!controlled && (
        <>
          <p className="after-call">{t("afterCall")}</p>
          <ReportButtons pharmacyId={pharmacyId} drugId={drugId} />
        </>
      )}
    </Modal>
  );
}

export function Sources({ facts }: { facts: Fact[] }) {
  const { t } = useApp();
  if (!facts.length) return null;
  const seen = new Map<string, Fact>();
  facts.forEach((f) => seen.set(f.source + f.text, f));
  return (
    <details className="sources">
      <summary>{t("sourcesTitle")} ({seen.size})</summary>
      <ul>
        {[...seen.values()].map((f, i) => (
          <li key={i}>
            {f.text}{" "}
            <SourceLink url={f.source} />
            {f.checked_date && <span className="muted"> · {t("checked", { date: f.checked_date })}</span>}
          </li>
        ))}
      </ul>
    </details>
  );
}

export function SourceLink({ url }: { url: string | null | undefined }) {
  if (!url || !/^https?:/.test(url)) return url ? <span>{url}</span> : null;
  let host = url;
  try { host = new URL(url).hostname.replace(/^www\./, ""); } catch { /* keep the raw text */ }
  return <a href={url} target="_blank" rel="noreferrer">{host}</a>;
}

export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  const { t } = useApp();
  const ref = useRef<HTMLDivElement>(null);
  // Keep the latest onClose in a ref so the effect below runs only once per opening. (Running it on every render
  // moved the focus back to the first field after each key press: that is why creating an account failed.)
  const close = useRef(onClose);
  close.current = onClose;
  useEffect(() => {
    const prev = document.activeElement as HTMLElement | null;
    ref.current?.querySelector<HTMLElement>("input, select, textarea, button:not(.modal-x)")?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close.current();
      if (e.key === "Tab" && ref.current) { // keep keyboard focus inside the pop-up
        const items = [...ref.current.querySelectorAll<HTMLElement>("a[href], button:not(:disabled), input, select, textarea")];
        if (!items.length) return;
        const first = items[0], last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("keydown", onKey); prev?.focus(); };
  }, []);
  return (
    <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) close.current(); }}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" ref={ref}>
        <div className="modal-head">
          <h2 id="modal-title">{title}</h2>
          <button type="button" className="btn ghost modal-x" onClick={() => close.current()} aria-label={t("close")}>✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function NotFoundText({ value }: { value: unknown }) {
  const { t } = useApp();
  if (value === null || value === undefined || value === "" || value === "not found") return <span className="muted">{t("notFound")}</span>;
  if (value === "yes") return <span>{t("yes")}</span>;
  if (value === "no") return <span>{t("no")}</span>;
  return <span>{String(value)}</span>;
}

/** A simple pharmacy card for chat answers (with the report and rate buttons). */
export function PharmacyCardView(p: {
  id: string; name: string; address: string; phone: string; open_now: boolean | null; status?: string;
  closes_at: string | null; opens_next: string | null; distance_miles?: number | null; drugId?: string | null;
  controlled?: boolean;
}) {
  const { t, rate } = useApp();
  return (
    <article className="card pharmacy-card">
      <div className="card-top">
        <h3><Link to={`/pharmacies/${p.id}`}>{p.name}</Link></h3>
        <OpenBadge open={p.open_now} opensNext={p.opens_next} status={p.status} />
      </div>
      <p className="address">{p.address}</p>
      <p className="meta-line">
        {p.open_now && p.closes_at && <span>{t("closesAt", { time: p.closes_at })}</span>}
        {p.distance_miles != null && <span>{t("away", { miles: p.distance_miles })}</span>}
      </p>
      <div className="card-actions">
        <a className="btn" href={telHref(p.phone)}><span aria-hidden="true">📞</span> {t("call")} {p.phone}</a>
        <a className="btn ghost" href={directionsHref(p.address)} target="_blank" rel="noreferrer">{t("directions")}</a>
        <Link className="btn ghost" to={`/pharmacies/${p.id}`}>{t("details")}</Link>
      </div>
      <ReportButtons pharmacyId={p.id} drugId={p.drugId} controlled={p.controlled} compact />
      <button type="button" className="btn ghost rate-btn" onClick={() => rate(p.id)}><span aria-hidden="true">★</span> {t("ratePharmacy")}</button>
    </article>
  );
}

/** Straight-line miles between two points. */
export function miles(a: { lat: number; lon: number }, b: { lat: number; lon: number }) {
  const r = 3958.8, rad = Math.PI / 180;
  const dLat = (b.lat - a.lat) * rad, dLon = (b.lon - a.lon) * rad;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * r * Math.asin(Math.sqrt(h));
}
