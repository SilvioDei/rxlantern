// Pop-ups shown from any page: log in / create account, stock report, review, and delete account.
import { useState, type FormEvent } from "react";
import { useApp, errorText } from "../state";
import { api } from "../api";
import { MicButton, MicNote, Modal } from "./Bits";

export function AuthModal() {
  const { authOpen } = useApp();
  return authOpen ? <AuthForm /> : null;
}

function AuthForm() {
  const { t, closeAuth, refreshMe, notify } = useApp();
  const [mode, setMode] = useState<"login" | "create">("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "create") {
        await api.post("/api/auth/register", { email, display_name: name, password: pw, confirm_password: pw2 });
      }
      const r = await api.post<{ display_name: string }>("/api/auth/login", { email, password: pw });
      await refreshMe();
      notify(t("loggedIn", { name: r.display_name }));
      closeAuth(true);
    } catch (err) {
      setError(errorText(err, t));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={mode === "login" ? t("authTitleLogin") : t("authTitleCreate")} onClose={() => closeAuth(false)}>
      <p className="muted">{t("authWhy")}</p>
      <form onSubmit={submit} className="form" noValidate={false}>
        <label>{t("email")}<input name="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        {mode === "create" && (
          <label>{t("displayName")}<input name="display_name" required minLength={2} maxLength={30} value={name} onChange={(e) => setName(e.target.value)} /></label>
        )}
        <label>{mode === "create" ? t("password") : t("passwordLogin")}
          <input name="password" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} required minLength={mode === "create" ? 10 : 1} value={pw} onChange={(e) => setPw(e.target.value)} /></label>
        {mode === "create" && (
          <label>{t("confirmPassword")}<input name="confirm_password" type="password" autoComplete="new-password" required value={pw2} onChange={(e) => setPw2(e.target.value)} /></label>
        )}
        {error && <p className="alert" role="alert">{error}</p>}
        <button type="submit" className="btn primary big" disabled={busy}>{busy ? t("saving") : mode === "login" ? t("login") : t("createAccount")}</button>
      </form>
      <button type="button" className="link-button" onClick={() => { setMode(mode === "login" ? "create" : "login"); setError(""); }}>
        {mode === "login" ? t("needAccount") : t("haveAccount")}
      </button>
    </Modal>
  );
}

/** Opened when the pharmacy or the medicine is not known yet (e.g. "I called a pharmacy" on Shortage watch). */
export function ReportFormHost() {
  const { reportForm } = useApp();
  return reportForm ? <ReportForm key={JSON.stringify(reportForm)} /> : null;
}

function ReportForm() {
  const { t, meta, reportForm, closeReportForm, notify, bump } = useApp();
  const [pharmacy, setPharmacy] = useState(reportForm?.pharmacyId ?? "");
  const [drug, setDrug] = useState(reportForm?.drugId ?? "");
  const [inStock, setInStock] = useState<boolean | null>(reportForm?.inStock ?? null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (inStock === null || !pharmacy || !drug) return;
    setBusy(true);
    try {
      await api.post(`/api/pharmacies/${pharmacy}/stock-reports`, { drug_id: drug, in_stock: inStock });
      notify(t("thanksReport"));
      bump();
      closeReportForm();
    } catch (err) {
      setMsg(errorText(err, t));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("reportTitle")} onClose={closeReportForm}>
      <form onSubmit={submit} className="form">
        <label>{t("pharmacy")}
          <select name="pharmacy" value={pharmacy} onChange={(e) => setPharmacy(e.target.value)} required>
            <option value="">{t("choosePharmacy")}</option>
            {meta?.pharmacies.map((p) => <option key={p.id} value={p.id}>{p.name} — {p.address}</option>)}
          </select>
        </label>
        <label>{t("medicine")}
          <select name="drug" value={drug} onChange={(e) => setDrug(e.target.value)} required>
            <option value="">{t("pickMedicine")}</option>
            {meta?.drugs.map((d) => (
              <option key={d.id} value={d.id} disabled={d.controlled}>{d.name}{d.controlled ? ` ${t("controlledOption")}` : ""}</option>
            ))}
          </select>
        </label>
        <fieldset className="choice-row">
          <legend className="sr-only">{t("reportTitle")}</legend>
          <label className={`choice ${inStock === true ? "on" : ""}`}><input type="radio" name="stock" checked={inStock === true} onChange={() => setInStock(true)} /> {t("inStock")}</label>
          <label className={`choice ${inStock === false ? "on" : ""}`}><input type="radio" name="stock" checked={inStock === false} onChange={() => setInStock(false)} /> {t("outOfStock")}</label>
        </fieldset>
        <p className="muted small">{t("callToConfirm")}</p>
        {msg && <p className="alert" role="alert">{msg}</p>}
        <button type="submit" className="btn primary big" disabled={busy || inStock === null || !pharmacy || !drug}>{busy ? t("saving") : t("submit")}</button>
      </form>
    </Modal>
  );
}

export function ReviewFormHost() {
  const { reviewFor } = useApp();
  return reviewFor ? <ReviewForm key={reviewFor} pharmacyId={reviewFor} /> : null;
}

function ReviewForm({ pharmacyId }: { pharmacyId: string }) {
  const { t, meta, closeReview, notify, bump } = useApp();
  const today = new Date().toLocaleDateString("en-CA");
  const [rating, setRating] = useState(0);
  const [wait, setWait] = useState("");
  const [visit, setVisit] = useState(today);
  const [comment, setComment] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const name = meta?.pharmacies.find((p) => p.id === pharmacyId);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!rating) return;
    setBusy(true);
    try {
      const r = await api.post<{ status: string; message: string }>(`/api/pharmacies/${pharmacyId}/reviews`, {
        rating, wait_minutes: wait === "" ? null : Number(wait), visit_date: visit, comment: comment || null,
      });
      if (r.status === "rejected") {
        setMsg(`${t("modRejected")} ${r.message.replace(/^We couldn't publish this comment\.\s*/, "")}`);
      } else {
        notify(r.status === "published" ? t("modPublished") : t("modPending"));
        bump();
        closeReview();
      }
    } catch (err) {
      setMsg(errorText(err, t));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={t("reviewTitle")} onClose={closeReview}>
      {name && <p className="muted">{name.name} — {name.address}</p>}
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
        <label>{t("waitMinutes")}<input name="wait" type="number" min={0} max={600} inputMode="numeric" value={wait} onChange={(e) => setWait(e.target.value)} /></label>
        <label>{t("visitDate")}<input name="visit" type="date" max={today} required value={visit} onChange={(e) => setVisit(e.target.value)} /></label>
        <label>{t("comment")}
          <textarea name="comment" maxLength={300} rows={3} value={comment} onChange={(e) => setComment(e.target.value)} aria-describedby="comment-help" />
        </label>
        <div className="mic-line">
          <MicButton onText={(txt) => setComment((c) => (c ? `${c} ${txt}` : txt).slice(0, 300))} />
          <MicNote />
        </div>
        <p id="comment-help" className="muted small">{t("commentHelp")} · {t("chars", { n: comment.length })}</p>
        {msg && <p className="alert" role="alert">{msg}</p>}
        <button type="submit" className="btn primary big" disabled={busy || !rating}>{busy ? t("saving") : t("submit")}</button>
      </form>
    </Modal>
  );
}

export function DeleteAccountModal({ onClose }: { onClose: () => void }) {
  const { t, refreshMe, notify, bump } = useApp();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  return (
    <Modal title={t("deleteTitle")} onClose={onClose}>
      <p>{t("deleteText")}</p>
      {error && <p className="alert" role="alert">{error}</p>}
      <div className="card-actions">
        <button type="button" className="btn danger" disabled={busy} onClick={async () => {
          setBusy(true);
          try {
            await api.del("/api/auth/account");
            await refreshMe();
            notify(t("deleted"));
            bump();
            onClose();
          } catch (e) {
            setError(errorText(e, t));
            setBusy(false);
          }
        }}>{t("deleteConfirm")}</button>
        <button type="button" className="btn ghost" onClick={onClose}>{t("cancel")}</button>
      </div>
    </Modal>
  );
}
