// One chat answer: emergency card, reply, pharmacy cards, call script (with report buttons), warnings, sources, tokens.
import { useState } from "react";
import { useApp } from "../state";
import type { FinalReply } from "../api";
import { CallScriptCard, MicButton, MicNote, PharmacyCardView, ReadAloud, Sources } from "./Bits";

function Emergency({ reply }: { reply: FinalReply }) {
  const { t } = useApp();
  const crisis = /988/.test(reply.reply_text);
  return (
    <section className="emergency" role="alert" aria-labelledby={`em-${reply.run_id}`}>
      <h2 id={`em-${reply.run_id}`}><span aria-hidden="true">⚠</span> {t("emergencyTitle")}</h2>
      <p className="emergency-text">{reply.reply_text}</p>
      <div className="card-actions">
        <a className="btn emergency-btn" href="tel:911">{t("call911")}</a>
        <a className="btn emergency-btn" href="tel:+18002221222">{t("callPoison")}</a>
        {crisis && <a className="btn emergency-btn" href="tel:988">{t("call988")}</a>}
      </div>
    </section>
  );
}

export function Answer({ reply, onFollowUp }: { reply: FinalReply; onFollowUp: (answer: string) => void }) {
  const { t, lang, meta } = useApp();
  const [text, setText] = useState("");
  if (reply.emergency) return <Emergency reply={reply} />;
  const q = reply.follow_up_question ?? "";
  const placeLike = /zip|neighbo|hospital|barrio|c[oó]digo|area|zona/i.test(q);
  const insLike = /insurance|seguro|plan/i.test(q);
  const formLike = /form|capsule|liquid|forma|c[aá]psula|l[ií]quido/i.test(q);
  const chips: string[] = placeLike ? (meta?.neighborhoods ?? []).slice(0, 8)
    : insLike ? ["MassHealth", "Medicare", lang === "es" ? "Plan comercial" : "Commercial plan", lang === "es" ? "Sin seguro" : "No insurance"]
    : formLike ? (lang === "es" ? ["Cápsulas", "Líquido para niños"] : ["Capsules", "Liquid for children"]) : [];
  const cost = reply.usage.cost_usd;
  const tokens = reply.usage.total_tokens;
  const drug = meta?.drugs.find((d) => d.id === reply.drug_id);
  const controlled = !!drug?.controlled || !!reply.controlled;
  const onlyPharmacy = reply.pharmacy_cards.length === 1 ? reply.pharmacy_cards[0].id : undefined;

  return (
    <section className="answer" aria-live="polite">
      <div className="answer-head">
        <h3>{t("answerTitle")}</h3>
        <ReadAloud text={[reply.reply_text, reply.follow_up_question].filter(Boolean).join(" ")} />
      </div>
      <div className="reply-card">
        <p className="reply-text">{reply.reply_text}</p>
      </div>

      {reply.follow_up_question && (
        <div className="followup-card">
          <h4>{t("followUpTitle")}</h4>
          <p>{reply.follow_up_question}</p>
          {chips.length > 0 && (
            <div className="chips">
              {chips.map((c) => <button key={c} type="button" className="chip" onClick={() => onFollowUp(c)}>{c}</button>)}
            </div>
          )}
          <form className="inline-form" onSubmit={(e) => { e.preventDefault(); if (text.trim()) { onFollowUp(text.trim()); setText(""); } }}>
            <label className="sr-only" htmlFor={`followup-${reply.run_id}`}>{t("followUpPlaceholder")}</label>
            <input id={`followup-${reply.run_id}`} value={text} onChange={(e) => setText(e.target.value)} placeholder={t("followUpPlaceholder")} />
            <MicButton onText={(txt) => setText((x) => (x ? `${x} ${txt}` : txt))} />
            <button type="submit" className="btn primary">{t("send")}</button>
          </form>
          <MicNote />
        </div>
      )}

      {reply.pharmacy_cards.length > 0 && (
        <div className="cards-grid">
          {reply.pharmacy_cards.map((c) => <PharmacyCardView key={c.id} {...c} drugId={reply.drug_id} controlled={controlled} />)}
        </div>
      )}

      {reply.call_script && (
        <CallScriptCard text={reply.call_script} drugId={reply.drug_id} pharmacyId={onlyPharmacy} controlled={controlled} />
      )}
      {controlled && reply.call_script && <p className="notice small">{t("controlledExplain")}</p>}

      {lang === "en" && reply.warnings?.length > 0 && (
        <div className="warn-card" role="note">
          <h4>{t("warningsTitle")}</h4>
          <ul>{reply.warnings.map((w) => <li key={w}>{w}</li>)}</ul>
        </div>
      )}

      <Sources facts={reply.sources} />
      <p className="tokens-line">
        {tokens > 0 ? t("usedTokens", { tokens: tokens.toLocaleString(), cost: cost != null ? cost.toFixed(4) : "?" }) : t("usedTokensFree")}
      </p>
    </section>
  );
}
