// Visitor settings (language, Easy view, place, insurance) saved only in this browser, plus login state.
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Me, type Meta } from "./api";
import { translate, type Key, type Lang } from "./i18n";

interface Settings {
  lang: Lang;
  easy: boolean;
  place: string;
  insurance: string;
}

interface AppState extends Settings {
  set: (patch: Partial<Settings>) => void;
  t: (key: Key, vars?: Record<string, string | number>) => string;
  meta: Meta | null;
  me: Me;
  refreshMe: () => Promise<void>;
  requireLogin: (then: () => void) => void;
  authOpen: boolean;
  closeAuth: (loggedIn: boolean) => void;
}

const KEY = "rxlantern.settings";
const Ctx = createContext<AppState | null>(null);

function load(): Settings {
  const fallback: Settings = { lang: navigator.language?.startsWith("es") ? "es" : "en", easy: false, place: "", insurance: "" };
  try {
    return { ...fallback, ...JSON.parse(localStorage.getItem(KEY) || "{}") };
  } catch {
    return fallback;
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>(load);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [me, setMe] = useState<Me>({ logged_in: false });
  const [authOpen, setAuthOpen] = useState(false);
  const [pending, setPending] = useState<(() => void) | null>(null);

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

  const requireLogin = useCallback((then: () => void) => {
    if (me.logged_in) then();
    else {
      setPending(() => then);
      setAuthOpen(true);
    }
  }, [me.logged_in]);

  const closeAuth = useCallback((loggedIn: boolean) => {
    setAuthOpen(false);
    if (loggedIn && pending) pending();
    setPending(null);
  }, [pending]);

  return (
    <Ctx.Provider value={{ ...settings, set, t, meta, me, refreshMe, requireLogin, authOpen, closeAuth }}>
      {children}
    </Ctx.Provider>
  );
}

export function useApp(): AppState {
  const v = useContext(Ctx);
  if (!v) throw new Error("useApp outside AppProvider");
  return v;
}
