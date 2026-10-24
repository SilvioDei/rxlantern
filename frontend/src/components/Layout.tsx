// Header (logo, Easy view, English/Español, account menu, navigation), footer, and the status message area.
import { useEffect, useRef, useState } from "react";
import { NavLink, Link, useLocation } from "react-router-dom";
import { useApp } from "../state";
import { api } from "../api";
import { Logo } from "./Logo";
import { ReadAloud } from "./Bits";
import { DeleteAccountModal } from "./Forms";

function LanguageSwitch() {
  const { t, lang, set } = useApp();
  return (
    <div className="lang-switch" role="group" aria-label={`${t("langLabel")} / Language`}>
      {(["en", "es"] as const).map((l) => (
        <button key={l} type="button" lang={l} aria-pressed={lang === l} className={lang === l ? "on" : ""}
          onClick={() => set({ lang: l })}>{l === "en" ? "English" : "Español"}</button>
      ))}
    </div>
  );
}

function AccountMenu() {
  const { t, me, refreshMe, requireLogin, notify, bump } = useApp();
  const [open, setOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  const { pathname } = useLocation();
  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => { if (!box.current?.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", esc); };
  }, [open]);

  if (!me.logged_in) {
    return <button type="button" className="pill" onClick={() => requireLogin(() => undefined)}>{t("loginOrCreate")}</button>;
  }
  return (
    <div className="account" ref={box}>
      <button type="button" className="pill" aria-expanded={open} aria-haspopup="true" onClick={() => setOpen(!open)}>
        <span aria-hidden="true">👤</span> {t("account")} <span aria-hidden="true">▾</span>
      </button>
      {open && (
        <div className="account-menu">
          <p className="muted small">{t("signedInAs", { name: me.display_name ?? "" })}</p>
          <button type="button" className="menu-item" onClick={async () => {
            await api.post("/api/auth/logout");
            await refreshMe();
            setOpen(false);
            notify(t("loggedOut"));
            bump();
          }}>{t("logout")}</button>
          <button type="button" className="menu-item danger-text" onClick={() => { setOpen(false); setConfirmDelete(true); }}>{t("deleteAccount")}</button>
        </div>
      )}
      {confirmDelete && <DeleteAccountModal onClose={() => setConfirmDelete(false)} />}
    </div>
  );
}

export function Header() {
  const { t, set, easy, me, meta } = useApp();
  const app = meta?.app_name ?? "RxLantern";
  return (
    <header className="site-header">
      <a className="skip" href="#main">{t("skip")}</a>
      <div className="header-row">
        <Link to="/" className="brand" aria-label={app}>
          <Logo size={44} />
          <span className="brand-name">{app}</span>
        </Link>
        <div className="header-actions">
          <button type="button" className={`pill ${easy ? "pill-on" : ""}`} aria-pressed={easy}
            title={t("easyHelp")} onClick={() => set({ easy: !easy })}>
            <span aria-hidden="true">Aa</span> {easy ? t("easyOn") : t("easyOff")}
          </button>
          <LanguageSwitch />
          <AccountMenu />
        </div>
      </div>
      <div className="easy-bar">
        <ReadAloud label={t("readPage")} text={() => document.getElementById("main")?.innerText ?? ""} />
      </div>
      <nav className="main-nav" aria-label={t("mainNav")}>
        <NavLink to="/" end>{t("navHome")}</NavLink>
        <NavLink to="/pharmacies">{t("navPharmacies")}</NavLink>
        <NavLink to="/shortages">{t("navShortages")}</NavLink>
        <NavLink to="/vaccines">{t("navVaccines")}</NavLink>
        <NavLink to="/community">{t("navCommunity")}</NavLink>
        <NavLink to="/about">{t("navAbout")}</NavLink>
        {me.is_admin && <NavLink to="/admin">{t("navAdmin")}</NavLink>}
      </nav>
    </header>
  );
}

export function Toast() {
  const { toast } = useApp();
  return (
    <div className="toast-area" role="status" aria-live="polite">
      {toast && <div className={`toast ${toast.ok ? "" : "toast-bad"}`}>{toast.text}</div>}
    </div>
  );
}

export function Footer() {
  const { t, lang } = useApp();
  return (
    <footer className="site-footer">
      <p><strong>{t("footer1")}</strong></p>
      <p>{t("footer2")}</p>
      <p>{t("footerPrivacy")} <Link to="/about">{t("navAbout")}</Link></p>
      {lang === "es" && <p className="small">{t("dataEnglishNote")}</p>}
    </footer>
  );
}
