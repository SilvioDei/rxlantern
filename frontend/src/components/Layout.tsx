// Header (logo, navigation, Easy view, language, login) and footer, shown on every page.
import { NavLink, Link } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";
import { Logo } from "./Logo";

export function Header() {
  const { t, lang, set, easy, me, meta, refreshMe, requireLogin } = useApp();
  const app = meta?.app_name ?? "RxLantern";
  return (
    <header className="site-header">
      <a className="skip" href="#main">{t("skip")}</a>
      <div className="header-row">
        <Link to="/" className="brand" aria-label={app}>
          <Logo size={42} />
          <span className="brand-name">{app}</span>
        </Link>
        <div className="header-actions">
          <button type="button" className={`pill ${easy ? "pill-on" : ""}`} aria-pressed={easy}
            title={t("easyHelp")} onClick={() => set({ easy: !easy })}>
            <span aria-hidden="true">Aa</span> {easy ? t("easyOn") : t("easyOff")}
          </button>
          <button type="button" className="pill" lang={lang === "en" ? "es" : "en"} aria-label={t("langSwitchLabel")}
            onClick={() => set({ lang: lang === "en" ? "es" : "en" })}>
            {t("langSwitch")}
          </button>
          {me.logged_in ? (
            <button type="button" className="pill subtle" onClick={async () => { await api.post("/api/auth/logout"); refreshMe(); }}>
              {t("logout")}
            </button>
          ) : (
            <button type="button" className="pill subtle" onClick={() => requireLogin(() => undefined)}>{t("login")}</button>
          )}
        </div>
      </div>
      <nav className="main-nav" aria-label="Main">
        <NavLink to="/" end>{t("navHome")}</NavLink>
        <NavLink to="/pharmacies">{t("navPharmacies")}</NavLink>
        <NavLink to="/shortages">{t("navShortages")}</NavLink>
        <NavLink to="/vaccines">{t("navVaccines")}</NavLink>
        {me.is_admin && <NavLink to="/admin">{t("navAdmin")}</NavLink>}
      </nav>
    </header>
  );
}

export function Footer() {
  const { t, lang } = useApp();
  return (
    <footer className="site-footer">
      <p><strong>{t("footer1")}</strong></p>
      <p>{t("footer2")}</p>
      {lang === "es" && <p className="muted small">{t("dataEnglishNote")}</p>}
    </footer>
  );
}
