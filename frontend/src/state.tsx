// Visitor settings (language, Easy view, place, insurance, plan) saved only in this browser, plus login state,
// the "post a report / rate this pharmacy" flow (log in only at that moment), and short status messages.
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { api, ApiError, type Me, type Meta } from "./api";
import { translate, type Key, type Lang } from "./i18n";

interface Settings {
  lang: Lang;
  easy: boolean;
  place: string;      // ZIP code or neighborhood (this browser only)
  insurance: string;  // masshealth | medicare | commercial | uninsured | ""
  plan: string;       // commercial plan id
  drugId: string;     // last medicine chosen in the guided search
}

/** A position from "Use my location": kept in memory only (never saved, never sent to the server). */
export interface Origin { lat: number; lon: number; label: string; fromDevice: boolean }

export interface ReportRequest { pharmacyId?: string; drugId?: string; inStock?: boolean }

interface AppState extends Settings {
  set: (patch: Partial<Settings>) => void;
  t: (key: Key, vars?: Record<string, string | number>) => string;
  meta: Meta | null;
  me: Me;
  refreshMe: () => Promise<void>;
  requireLogin: (then: () => void) => void;
  authOpen: boolean;
  closeAuth: (loggedIn: boolean) => void;
  deviceOrigin: Origin | null;
  setDeviceOrigin: (o: Origin | null) => void;
  /** Post a stock report. With pharmacy, drug, and answer known it saves right away (after login if needed);
   *  otherwise it opens the report form with what is known filled in. */
  report: (r: ReportRequest) => void;
  reportForm: ReportRequest | null;
  closeReportForm: () => void;
  rate: (pharmacyId: string) => void;
  reviewFor: string | null;
  closeReview: () => void;
  /** Bumped after every post, so pages reload and show it right away. */
  version: number;
  bump: () => void;
  toast: { text: string; ok: boolean } | null;
  notify: (text: string, ok?: boolean) => void;
  /** Step 7c part 2: the transfer helper, opened after a "They don't have it" report. */
  transfer: ReportRequest | null;
  showTransfer: (r: ReportRequest) => void;
  closeTransfer: () => void;
}

const KEY = "rxlantern.settings";
const Ctx = createContext<AppState | null>(null);

function load(): Settings {
  const fallback: Settings = { lang: navigator.language?.startsWith("es") ? "es" : "en", easy: false, place: "",
    insurance: "", plan: "", drugId: "" };
  try {
    return { ...fallback, ...JSON.parse(localStorage.getItem(KEY) || "{}") };
  } catch {
    return fallback;
  }
}

export function errorText(e: unknown, t: AppState["t"]): string {
  if (e instanceof ApiError) {
    if (e.code === "offline") return t("errorOffline");
    if (e.code === "generic") return t("errorGeneric");
    return e.message;
  }
  return t("errorGeneric");
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>(load);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [me, setMe] = useState<Me>({ logged_in: false });
  const [authOpen, setAuthOpen] = useState(false);
  const pending = useRef<(() => void) | null>(null);
  const [deviceOrigin, setDeviceOrigin] = useState<Origin | null>(null);
  const [reportForm, setReportForm] = useState<ReportRequest | null>(null);
  const [reviewFor, setReviewFor] = useState<string | null>(null);
  const [version, setVersion] = useState(0);
  const [toast, setToast] = useState<{ text: string; ok: boolean } | null>(null);
  const [transfer, setTransfer] = useState<ReportRequest | null>(null);
  const toastTimer = useRef<number>(0);

  const set = useCallback((patch: Partial<Settings>) => setSettings((s) => ({ ...s, ...patch })), []);
  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(settings));
    document.documentElement.lang = settings.lang;
    document.body.classList.toggle("easy", settings.easy);
  }, [settings]);

  const refreshMe = useCallback(async () => {
    try {
      setMe(await api.get<Me>("/api/auth/me"));
    } catch {
      setMe({ logged_in: false });
    }
  }, []);
  useEffect(() => {
    api.get<Meta>("/api/meta").then((m) => {
      setMeta(m);
      document.title = m.app_name;
    }).catch(() => undefined);
    refreshMe();
  }, [refreshMe]);

  const t = useCallback((key: Key, vars?: Record<string, string | number>) =>
    translate(settings.lang, key, { app: meta?.app_name ?? "RxLantern", ...vars }), [settings.lang, meta]);

  const notify = useCallback((text: string, ok = true) => {
    setToast({ text, ok });
    window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(null), 7000);
  }, []);

  const requireLogin = useCallback((then: () => void) => {
    if (me.logged_in) then();
    else {
      pending.current = then;
      setAuthOpen(true);
    }
  }, [me.logged_in]);

  const closeAuth = useCallback((loggedIn: boolean) => {
    setAuthOpen(false);
    const next = pending.current;
    pending.current = null;
    if (loggedIn && next) next();
  }, []);

  const bump = useCallback(() => setVersion((v) => v + 1), []);

  const report = useCallback((r: ReportRequest) => {
    requireLogin(async () => {
      if (r.pharmacyId && r.drugId && r.inStock !== undefined) {
        try {
          await api.post(`/api/pharmacies/${r.pharmacyId}/stock-reports`, { drug_id: r.drugId, in_stock: r.inStock });
          notify(t("thanksReport"));
          bump();
          if (!r.inStock) setTransfer({ pharmacyId: r.pharmacyId, drugId: r.drugId });
        } catch (e) {
          notify(errorText(e, t), false);
        }
      } else {
        setReportForm(r);
      }
    });
  }, [requireLogin, notify, t, bump]);

  const rate = useCallback((pharmacyId: string) => requireLogin(() => setReviewFor(pharmacyId)), [requireLogin]);

  return (
    <Ctx.Provider value={{
      ...settings, set, t, meta, me, refreshMe, requireLogin, authOpen, closeAuth, deviceOrigin, setDeviceOrigin,
      report, reportForm, closeReportForm: () => setReportForm(null), rate, reviewFor, closeReview: () => setReviewFor(null),
      version, bump, toast, notify, transfer, showTransfer: setTransfer, closeTransfer: () => setTransfer(null),
    }}>
      {children}
    </Ctx.Provider>
  );
}

export function useApp(): AppState {
  const v = useContext(Ctx);
  if (!v) throw new Error("useApp outside AppProvider");
  return v;
}
