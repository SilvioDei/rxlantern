// One answer from the agents: reply, pharmacy cards, call script, warnings, follow-up, sources, tokens/cost.
import { useState } from "react";
import { useApp } from "../state";
import type { FinalReply } from "../api";
import { CallScriptCard, PharmacyCardView, ReadAloud, Sources } from "./Bits";

export function Answer({ reply, onFollowUp }: { reply: FinalReply; onFollowUp: (answer: string) => void }) {
  const { t, easy, lang, meta } = useApp();
  const [text, setText] = useState("");
  const q = reply.follow_up_question ?? "";
  const placeLike = /zip|neighbo|hospital|barrio|c[oó]digo|area|zona/i.test(q);
  const insLike = /insurance|seguro|plan/i.test(q);
  const formLike = /form|capsule|liquid|forma|c[aá]psula|l[ií]quido/i.test(q);
  const chips: string[] = placeLike ? (meta?.neighborhoods ?? []).slice(0, 8)
    : insLike ? ["MassHealth", "Medicare", lang === "es" ? "Plan comercial" : "Commercial plan", lang === "es" ? "Sin seguro" : "No insurance"]
    : formLike ? (lang === "es" ? ["Cápsulas", "Líquido para niños"] : ["Capsules", "Liquid for children"]) : [];
  const cost = reply.usage.cost_usd;
  const tokens = reply.usage.total_tokens;

  return (
    <section className="answer" aria-live="polite" aria-labelledby="answer-title">
      <div className="answer-head">
        <h2 id="answer-title">{t("answerTitle")}</h2>
        {easy && <ReadAloud text={[reply.reply_text, reply.follow_up_question].filter(Boolean).join(" ")} />}
      </div>
      <div className="card reply-card">
        <p className="reply-text">{reply.reply_text}</p>
      </div>

      {reply.follow_up_question && (
        <div className="card followup-card">
          <h3>{t("followUpTitle")}</h3>
          <p>{reply.follow_up_question}</p>
          {chips.length > 0 && (
            <div className="chips">
              {chips.map((c) => <button key={c} type="button" className="chip" onClick={() => onFollowUp(c)}>{c}</button>)}
            </div>
          )}
          <form className="inline-form" onSubmit={(e) => { e.preventDefault(); if (text.trim()) { onFollowUp(text.trim()); setText(""); } }}>
            <label className="sr-only" htmlFor="followup-input">{t("followUpPlaceholder")}</label>
            <input id="followup-input" value={text} onChange={(e) => setText(e.target.value)} placeholder={t("followUpPlaceholder")} />
            <button type="submit" className="btn primary">{t("send")}</button>
          </form>
        </div>
      )}

      {reply.pharmacy_cards.length > 0 && (
        <div className="cards-grid">
          {reply.pharmacy_cards.map((c) => <PharmacyCardView key={c.id} {...c} />)}
        </div>
      )}

      {reply.call_script && <CallScriptCard text={reply.call_script} />}

      {lang === "en" && reply.warnings?.length > 0 && (
        <div className="card warn-card" role="note">
          <h3>{t("warningsTitle")}</h3>
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
