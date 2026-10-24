// Log in / create account pop-up, stock report form, and review form.
import { useState, type FormEvent } from "react";
import { useApp } from "../state";
import { api, ApiError } from "../api";
import { Modal } from "./Bits";

function errText(e: unknown, t: ReturnType<typeof useApp>["t"]) {
  if (e instanceof ApiError) {
    if (e.code === "offline") return t("errorOffline");
    if (e.code === "generic") return t("errorGeneric");
    return e.message;
  }
  return t("errorGeneric");
}

export function AuthModal() {
  const { t, authOpen, closeAuth, refreshMe } = useApp();
  const [mode, setMode] = useState<"login" | "create">("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  if (!authOpen) return null;

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "create") {
        await api.post("/api/auth/register", { email, display_name: name, password: pw, confirm_password: pw2 });
      }
      await api.post("/api/auth/login", { email, password: pw });
      await refreshMe();
      setPw(""); setPw2("");
      closeAuth(true);
    } catch (err) {
      setError(errText(err, t));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={mode === "login" ? t("authTitleLogin") : t("authTitleCreate")} onClose={() => closeAuth(false)}>
      <p className="muted">{t("authWhy")}</p>
      <form onSubmit={submit} className="form">
        <label>{t("email")}<input type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        {mode === "create" && (
          <label>{t("displayName")}<input required minLength={2} maxLength={30} value={name} onChange={(e) => setName(e.target.value)} /></label>
        )}
        <label>{t("password")}<input type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} required minLength={mode === "create" ? 10 : 1} value={pw} onChange={(e) => setPw(e.target.value)} /></label>
        {mode === "create" && (
          <label>{t("confirmPassword")}<input type="password" autoComplete="new-password" required value={pw2} onChange={(e) => setPw2(e.target.value)} /></label>
        )}
        {error && <p className="alert" role="alert">{error}</p>}
        <button type="submit" className="btn primary" disabled={busy}>{mode === "login" ? t("login") : t("createAccount")}</button>
      </form>
      <button type="button" className="link-button" onClick={() => { setMode(mode === "login" ? "create" : "login"); setError(""); }}>
        {mode === "login" ? t("needAccount") : t("haveAccount")}
      </button>
    </Modal>
  );
}

export function ReportForm({ pharmacyId, onDone, onClose }: { pharmacyId?: string; onDone?: () => void; onClose: () => void }) {
  const { t, meta } = useApp();
  const [pharmacy, setPharmacy] = useState(pharmacyId ?? meta?.pharmacies[0]?.id ?? "");
  const [drug, setDrug] = useState(meta?.drugs.find((d) => !d.controlled)?.id ?? "");
  const [inStock, setInStock] = useState<boolean | null>(null);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (inStock === null) return;
    setBusy(true);
    try {
      await api.post(`/api/pharmacies/${pharmacy}/stock-reports`, { drug_id: drug, in_stock: inStock });
      setMsg({ ok: true, text: t("thanksReport") });
      onDone?.();
    } catch (err) {
      setMsg({ ok: false, text: errText(err, t) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("reportTitle")} onClose={onClose}>
      <form onSubmit={submit} className="form">
        <label>{t("pharmacy")}
          <select value={pharmacy} onChange={(e) => setPharmacy(e.target.value)} required>
            {meta?.pharmacies.map((p) => <option key={p.id} value={p.id}>{p.name} — {p.address}</option>)}
          </select>
        </label>
        <label>{t("medicine")}
          <select value={drug} onChange={(e) => setDrug(e.target.value)} required>
            {meta?.drugs.map((d) => (
              <option key={d.id} value={d.id} disabled={d.controlled}>{d.name}{d.controlled ? ` ${t("controlledOption")}` : ""}</option>
            ))}
          </select>
        </label>
        <fieldset className="choice-row">
          <legend className="sr-only">{t("medicine")}</legend>
          <label className={`choice ${inStock === true ? "on" : ""}`}><input type="radio" name="stock" checked={inStock === true} onChange={() => setInStock(true)} /> {t("inStock")}</label>
          <label className={`choice ${inStock === false ? "on" : ""}`}><input type="radio" name="stock" checked={inStock === false} onChange={() => setInStock(false)} /> {t("outOfStock")}</label>
        </fieldset>
        {msg && <p className={msg.ok ? "notice" : "alert"} role="status">{msg.text}</p>}
        <button type="submit" className="btn primary" disabled={busy || inStock === null}>{t("submit")}</button>
      </form>
    </Modal>
  );
}

export function ReviewForm({ pharmacyId, onDone, onClose }: { pharmacyId: string; onDone?: () => void; onClose: () => void }) {
  const { t } = useApp();
  const today = new Date().toLocaleDateString("en-CA");
  const [rating, setRating] = useState(0);
  const [wait, setWait] = useState("");
  const [visit, setVisit] = useState(today);
  const [comment, setComment] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!rating) return;
    setBusy(true);
    try {
      const r = await api.post<{ status: string; message: string }>(`/api/pharmacies/${pharmacyId}/reviews`, {
        rating, wait_minutes: wait === "" ? null : Number(wait), visit_date: visit, comment: comment || null,
      });
      const text = r.status === "published" ? t("modPublished") : r.status === "pending" ? t("modPending") : `${t("modRejected")} ${r.message.replace(/^We couldn't publish this comment\.\s*/, "")}`;
      setMsg({ ok: r.status !== "rejected", text });
      onDone?.();
    } catch (err) {
      setMsg({ ok: false, text: errText(err, t) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("reviewTitle")} onClose={onClose}>
      <form onSubmit={submit} className="form">
        <fieldset className="stars">
          <legend>{t("rating")}</legend>
          {[1, 2, 3, 4, 5].map((n) => (
            <label key={n} className={`star ${rating >= n ? "on" : ""}`} title={t("stars", { n })}>
              <input type="radio" name="rating" value={n} checked={rating === n} onChange={() => setRating(n)} aria-label={t("stars", { n })} />
              <span aria-hidden="true">★</span>
            </label>
          ))}
        </fieldset>
        <label>{t("waitMinutes")}<input type="number" min={0} max={600} inputMode="numeric" value={wait} onChange={(e) => setWait(e.target.value)} /></label>
        <label>{t("visitDate")}<input type="date" max={today} required value={visit} onChange={(e) => setVisit(e.target.value)} /></label>
        <label>{t("comment")}
          <textarea maxLength={300} rows={3} value={comment} onChange={(e) => setComment(e.target.value)} aria-describedby="comment-help" />
        </label>
        <p id="comment-help" className="muted small">{t("commentHelp")} · {t("chars", { n: comment.length })}</p>
        {msg && <p className={msg.ok ? "notice" : "alert"} role="status">{msg.text}</p>}
        <button type="submit" className="btn primary" disabled={busy || !rating}>{t("submit")}</button>
      </form>
    </Modal>
  );
}
