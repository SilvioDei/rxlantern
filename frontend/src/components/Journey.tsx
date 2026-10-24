// Step 7c part 2 pieces shared by several pages: prior authorization helper, transfer helper, "Before you go"
// checklist, "Send it here" link, savings finder, shortage watchlist (star + highlights), languages reported by
// patients, and the time-saved line. All of them read our own API only (no AI).
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { api, type Coverage, type Impact, type Savings } from "../api";
import type { Key } from "../i18n";
import { Modal, ReadAloud, SampleBadge, SourceLink, ago, miles } from "./Bits";

export const STAFF_LANGUAGES = ["Cantonese", "Mandarin", "Haitian Creole", "Spanish", "Portuguese", "Vietnamese"];
type T = (key: Key, vars?: Record<string, string | number>) => string;
export const langName = (t: T, l: string) => t(`lang_${l}` as Key);

// ----------------------------------------------------------------------------- prior authorization
/** "yes" when coverage says PA is needed, "maybe" when only in some cases or some Medicare plans; else null. */
export function priorAuth(c: Coverage | null | undefined): "yes" | "maybe" | null {
  const pa = c?.masshealth?.prior_authorization;
  if (pa === "yes") return "yes";
  if (pa && pa.startsWith("only in some cases")) return "maybe";
  if (c?.medicare && c.medicare.plans_with_prior_authorization > 0) return "maybe";
  return null;
}

export function PriorAuthCard({ coverage }: { coverage: Coverage | null | undefined }) {
  const { t } = useApp();
  const pa = priorAuth(coverage);
  if (!pa) return null;
  const lines = [t("paWhat"), t("paWhy"), t("paAsk"), t("paAsk1"), t("paAsk2"), t("paAsk3"), t("paNote")];
  return (
    <section className="card pa-card" aria-labelledby="pa-title">
      <h2 id="pa-title" className="h3"><span aria-hidden="true">📝</span> {t("paTitle")}</h2>
      {pa === "maybe" && <p><strong>{t("paMaybe")}</strong></p>}
      <p>{t("paWhat")}</p>
      <p>{t("paWhy")}</p>
      <p className="pa-ask"><strong>{t("paAsk")}</strong></p>
      <ul className="plain-list">
        <li>{t("paAsk1")}</li><li>{t("paAsk2")}</li><li>{t("paAsk3")}</li>
      </ul>
      <p className="small muted">{t("paNote")}</p>
      <div className="card-actions"><ReadAloud text={() => lines.join(" ")} /></div>
    </section>
  );
}

// ----------------------------------------------------------------------------- transfer helper
export function TransferHelper({ pharmacyId, drugId, controlled, open }: {
  pharmacyId?: string; drugId?: string | null; controlled?: boolean; open?: boolean;
}) {
  const { t, meta } = useApp();
  const p = meta?.pharmacies.find((x) => x.id === pharmacyId);
  const d = meta?.drugs.find((x) => x.id === drugId);
  const name = p ? `${p.name}, ${p.address.split(",")[0]}` : t("transferThePharmacy");
  const phone = p?.phone ?? t("transferItsPhone");
  const drug = d ? d.name : t("transferYourMedicine");
  const script = t("transferScript", { drug, pharmacy: name, phone });
  const body = controlled || d?.controlled ? (
    <p className="transfer-controlled"><strong>{t("transferControlled")}</strong></p>
  ) : (
    <>
      <p>{t("transferIntro")}</p>
      <p className="script-text script-box">{script}</p>
      <p><strong>{t("transferHave")}</strong></p>
      <ul className="plain-list">
        <li>{t("transferHave1", { pharmacy: name, phone })}</li>
        <li>{t("transferHave2", { drug })}</li>
        <li>{t("transferHave3")}</li>
      </ul>
      <div className="card-actions"><ReadAloud text={script} /></div>
    </>
  );
  return (
    <details className="transfer-helper" open={open}>
      <summary><span aria-hidden="true">↪</span> {t("transferOpen")}</summary>
      <h3 className="h3">{t("transferTitle")}</h3>
      {body}
    </details>
  );
}

/** Shown right after a patient reports "They don't have it". */
export function TransferHost() {
  const { t, transfer, closeTransfer } = useApp();
  if (!transfer) return null;
  return (
    <Modal title={t("transferTitle")} onClose={closeTransfer}>
      <TransferHelper pharmacyId={transfer.pharmacyId} drugId={transfer.drugId} open />
    </Modal>
  );
}

// ----------------------------------------------------------------------------- before you go + send it here
export function BeforeYouGo({ drugName, hoursToday }: { drugName?: string | null; hoursToday?: string | null }) {
  const { t } = useApp();
  const items = [t("bygInsurance"), t("bygId"), drugName ? t("bygMedicine", { drug: drugName }) : t("bygMedicineAny"),
    hoursToday ? t("bygHours", { hours: hoursToday }) : t("bygHoursCards")];
  return (
    <section className="card byg-card" aria-labelledby="byg-title">
      <h2 id="byg-title" className="h3"><span aria-hidden="true">✅</span> {t("bygTitle")}</h2>
      <ul className="checklist">{items.map((x) => <li key={x}><span aria-hidden="true">☐</span> {x}</li>)}</ul>
      <div className="card-actions no-print"><ReadAloud text={() => [t("bygTitle"), ...items].join(". ")} /></div>
    </section>
  );
}

export function SendHereLink({ pharmacyId, drugId }: { pharmacyId: string; drugId?: string | null }) {
  const { t } = useApp();
  return (
    <Link className="btn ghost send-here-btn" to={`/send-here/${pharmacyId}${drugId ? `?drug=${drugId}` : ""}`}>
      <span aria-hidden="true">🩺</span> {t("sendHereButton")}</Link>
  );
}

// ----------------------------------------------------------------------------- savings finder
export function SavingsFinder({ drugId }: { drugId: string }) {
  const { t, insurance } = useApp();
  const [s, setS] = useState<Savings | null>(null);
  useEffect(() => {
    api.get<Savings>(`/api/savings/${drugId}?insurance=${insurance}`).then(setS).catch(() => setS(null));
  }, [drugId, insurance]);
  if (!s) return null;
  const note = <p className="small savings-note"><span aria-hidden="true">ⓘ</span> {t("savNote")}</p>;
  if (!s.show_links) return <section className="card savings-card note-only" aria-label={t("savTitle")}>{note}</section>;
  const m = s.manufacturer;
  return (
    <section className="card savings-card" aria-labelledby="sav-title">
      <h2 id="sav-title" className="h3"><span aria-hidden="true">💲</span> {t("savTitle")}</h2>
      <p className="small muted">{t("savWho")}</p>
      <ul className="savings-links">
        <li>{s.goodrx?.url ? <a href={s.goodrx.url} target="_blank" rel="noreferrer" className="goodrx-link">{t("savGoodrx")} ↗</a>
          : t("savNotListed", { site: "GoodRx" })}</li>
        <li>{s.trumprx?.url ? <a href={s.trumprx.url} target="_blank" rel="noreferrer" className="trumprx-link">{t("savTrumprx")} ↗</a>
          : s.trumprx_controlled ? t("savTrumpControlled") : t("savNotListed", { site: "TrumpRx.gov" })}</li>
        {m && (
          <li>{m.url !== "not found"
            ? <><a href={m.url} target="_blank" rel="noreferrer" className="maker-link">{t("savMaker")}{m.link_text ? `: ${m.link_text}` : ""} ↗</a>
              <span className="src muted"> · {t("checked", { date: m.checked_date })} · <SourceLink url={m.source} /></span></>
            : <>{t("savMakerNF")} <span className="src muted">· {t("checked", { date: m.checked_date })} · <SourceLink url={m.brand_site} /></span></>}</li>
        )}
      </ul>
      <p className="small muted">{t("savLinksOnly")} {t("checked", { date: s.checked_date })}</p>
      {note}
    </section>
  );
}

// ----------------------------------------------------------------------------- shortage watchlist
const WATCH_KEY = "rxlantern.watch";
interface Watch { ids: string[]; lastVisit: string | null }
function readWatch(): Watch {
  try { return { ids: [], lastVisit: null, ...JSON.parse(localStorage.getItem(WATCH_KEY) || "{}") }; }
  catch { return { ids: [], lastVisit: null }; }
}
// A visit = one browser session (this tab). At the start of a visit we read when the last visit started and save
// this one, so every page in this visit compares against the same moment ("new since your last visit").
const VISIT_SINCE: string | null = (() => {
  if (typeof window === "undefined") return null;
  const SESSION_KEY = "rxlantern.visitSince";
  const kept = sessionStorage.getItem(SESSION_KEY);
  if (kept !== null) return kept || null;
  const w = readWatch();
  sessionStorage.setItem(SESSION_KEY, w.lastVisit ?? "");
  localStorage.setItem(WATCH_KEY, JSON.stringify({ ...w, lastVisit: new Date().toISOString() }));
  return w.lastVisit;
})();

export function useWatchlist() {
  const [ids, setIds] = useState<string[]>(() => readWatch().ids);
  const toggle = (id: string) => {
    const w = readWatch();
    const next = w.ids.includes(id) ? w.ids.filter((x) => x !== id) : [...w.ids, id];
    localStorage.setItem(WATCH_KEY, JSON.stringify({ ...w, ids: next }));
    setIds(next);
  };
  return { ids, toggle };
}

export function StarButton({ drugId, name }: { drugId: string; name: string }) {
  const { t } = useApp();
  const { ids, toggle } = useWatchlist();
  const on = ids.includes(drugId);
  return (
    <button type="button" className={`btn ghost star-btn ${on ? "on" : ""}`} aria-pressed={on} title={t("starHelp")}
      aria-label={`${on ? t("starOn") : t("starAdd")}: ${name}`} onClick={() => toggle(drugId)}>
      <span aria-hidden="true">{on ? "★" : "☆"}</span> {on ? t("starOn") : t("starAdd")}
    </button>
  );
}

interface WatchReport { pharmacy_id: string; drug_id: string; drug: string; pharmacy: string; address: string;
  neighborhood: string; latitude: number; longitude: number; reported_at: string }

/** New "in stock" reports for starred medicines since the last visit, near the saved place (3 miles). */
export function WatchHighlights() {
  const { t, lang, place } = useApp();
  const [items, setItems] = useState<(WatchReport & { dist: number | null })[]>([]);
  useEffect(() => {
    const ids = readWatch().ids;
    if (!ids.length || !VISIT_SINCE) return;
    (async () => {
      try {
        const r = await api.get<{ reports: WatchReport[] }>(`/api/watch-updates?drug_ids=${ids.join(",")}&since=${encodeURIComponent(VISIT_SINCE)}`);
        let origin: { lat: number; lon: number } | null = null;
        if (place.trim()) {
          const loc = await api.get<{ found: boolean; latitude: number; longitude: number }>(`/api/location?place=${encodeURIComponent(place.trim())}`);
          if (loc.found) origin = { lat: loc.latitude, lon: loc.longitude };
        }
        setItems(r.reports.map((x) => ({ ...x, dist: origin ? Math.round(miles(origin, { lat: x.latitude, lon: x.longitude }) * 10) / 10 : null }))
          .filter((x) => x.dist === null || x.dist <= 3).sort((a, b) => (a.dist ?? 0) - (b.dist ?? 0)));
      } catch { setItems([]); }
    })();
  }, [place]);
  if (!items.length) return null;
  return (
    <section className="card watch-card" aria-labelledby="watch-title" role="status">
      <h2 id="watch-title" className="h3"><span aria-hidden="true">★</span> {t("watchTitle")}</h2>
      <ul className="feed">
        {items.map((x, i) => (
          <li key={i} className="feed-item watch-item">
            <span className="badge badge-ok">✓ {t("inStockWord")}</span>{" "}
            {t("watchLine", { drug: x.drug, pharmacy: `${x.pharmacy}, ${x.address.split(",")[0]}` })}
            <span className="muted"> · {x.dist != null ? `${t("away", { miles: x.dist })} · ` : ""}{ago(x.reported_at, lang)}</span>
            {" "}<Link to={`/pharmacies/${x.pharmacy_id}`}>{t("details")}</Link>
          </li>
        ))}
      </ul>
      <p className="small muted">{t("watchNote")}</p>
    </section>
  );
}

// ----------------------------------------------------------------------------- languages reported by patients
export function ReportedLanguages({ real, sample, compact }: { real?: Record<string, number>; sample?: Record<string, number>; compact?: boolean }) {
  const { t } = useApp();
  const r = Object.entries(real ?? {}), s = Object.entries(sample ?? {});
  if (!r.length && !s.length) return compact ? null : <p className="muted small">{t("langNone")}</p>;
  return (
    <p className="small reported-langs">
      <span className="badge badge-info">{t("langReportedBadge")}</span>{" "}
      {r.map(([l, n]) => `${langName(t, l)} (${n})`).join(", ")}
      {s.length > 0 && <>{r.length ? " · " : ""}<SampleBadge /> {s.map(([l, n]) => `${langName(t, l)} (${n})`).join(", ")}</>}
    </p>
  );
}

/** Does a pharmacy match a language filter (pharmacy's own website or patient reports)? */
export function speaks(p: { languages: string[] | string; reported_languages?: Record<string, number>; sample_reported_languages?: Record<string, number> }, language: string) {
  const want = language.toLowerCase().replace(/^chinese \((.*)\)$/, "$1");
  const site = Array.isArray(p.languages) ? p.languages : [];
  const reported = [...Object.keys(p.reported_languages ?? {}), ...Object.keys(p.sample_reported_languages ?? {})];
  return [...site, ...reported].some((l) => l.toLowerCase().includes(want) || want.includes(l.toLowerCase()));
}

// ----------------------------------------------------------------------------- time saved
export function ImpactLine({ full }: { full?: boolean }) {
  const { t } = useApp();
  const [x, setX] = useState<Impact | null>(null);
  useEffect(() => { api.get<Impact>("/api/impact").then(setX).catch(() => setX(null)); }, []);
  if (!x) return null;
  const line = t("impactLine", { x: x.questions.toLocaleString(), y: x.patient_minutes.toLocaleString(), z: x.staff_minutes.toLocaleString() });
  if (!full) return <p className="impact-line small"><span className="estimate-tag">{t("impactEstimate")}</span> {line}</p>;
  return (
    <section className="card impact-card" aria-labelledby="impact-title">
      <h2 id="impact-title">{t("impactTitle")} <span className="estimate-tag">{t("impactEstimate")}</span></h2>
      <p className="impact-line">{line}</p>
      <p className="small muted">{t("impactHow")}</p>
    </section>
  );
}
