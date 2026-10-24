// Small shared pieces: read-aloud button, open/closed badge, pharmacy card, call-script card, sources, modal.
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { canSpeak, speak, stopSpeaking } from "../speech";
import type { Fact } from "../api";

export function ReadAloud({ text }: { text: string }) {
  const { t, lang } = useApp();
  const [on, setOn] = useState(false);
  useEffect(() => () => stopSpeaking(), []);
  if (!canSpeak()) return null;
  return (
    <button type="button" className="btn ghost" aria-pressed={on}
      onClick={() => {
        if (on) { stopSpeaking(); setOn(false); }
        else { setOn(true); speak(text, lang, () => setOn(false)); }
      }}>
      <span aria-hidden="true">{on ? "■" : "🔊"}</span> {on ? t("stopReading") : t("readAloud")}
    </button>
  );
}

export function OpenBadge({ open, opensNext }: { open: boolean | null; opensNext?: string | null }) {
  const { t } = useApp();
  if (open === true) return <span className="badge badge-open">● {t("openNow")}</span>;
  if (open === false) return <span className="badge badge-closed">{opensNext ? t("closedOpens", { when: opensNext }) : t("closed")}</span>;
  return <span className="badge badge-unknown">{t("hoursUnknown")}</span>;
}

export function telHref(phone: string) {
  return `tel:+1${phone.replace(/\D/g, "")}`;
}

export function directionsHref(address: string) {
  return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(address)}`;
}

export function PharmacyCardView(p: {
  id: string; name: string; address: string; phone: string; open_now: boolean | null;
  closes_at: string | null; opens_next: string | null; distance_miles?: number | null;
}) {
  const { t } = useApp();
  return (
    <article className="card pharmacy-card">
      <div className="card-top">
        <h3><Link to={`/pharmacies/${p.id}`}>{p.name}</Link></h3>
        <OpenBadge open={p.open_now} opensNext={p.opens_next} />
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
    </article>
  );
}

export function CallScriptCard({ text }: { text: string }) {
  const { t } = useApp();
  const [copied, setCopied] = useState(false);
  return (
    <section className="card script-card" aria-labelledby="script-title">
      <h3 id="script-title">{t("callScriptTitle")}</h3>
      <p className="script-text">{text}</p>
      <div className="card-actions">
        <button type="button" className="btn" onClick={async () => {
          try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { /* ignore */ }
        }}>{copied ? t("copied") : t("copy")}</button>
        <ReadAloud text={text} />
      </div>
    </section>
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
            {/^https?:/.test(f.source)
              ? <a href={f.source} target="_blank" rel="noreferrer">{new URL(f.source).hostname.replace(/^www\./, "")}</a>
              : <span>{f.source}</span>}
            {f.checked_date && <span className="muted"> · {t("checked", { date: f.checked_date })}</span>}
          </li>
        ))}
      </ul>
    </details>
  );
}

export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  const { t } = useApp();
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const prev = document.activeElement as HTMLElement | null;
    ref.current?.querySelector<HTMLElement>("input, select, textarea, button")?.focus();
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("keydown", onKey); prev?.focus(); };
  }, [onClose]);
  return (
    <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" ref={ref}>
        <div className="modal-head">
          <h2 id="modal-title">{title}</h2>
          <button type="button" className="btn ghost" onClick={onClose} aria-label={t("close")}>✕</button>
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
