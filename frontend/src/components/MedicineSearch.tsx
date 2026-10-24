// The medicine search box with suggestions (brand or generic names, small spelling mistakes OK) and the microphone.
// Used by the guided search, the search bar at the top of the home page, and the Community page search.
import { useMemo, useState, type FormEvent, type KeyboardEvent } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { medicines, suggest, type Medicine } from "../search";
import { MicButton, MicNote } from "./Bits";

export function MedicineSearch({ id, listId, label, help, placeholder, onPick, submitLabel, onNoMatch, otherLink = true,
  labelClass = "step-label", className = "" }: {
  id: string; listId: string; label: string; help?: string; placeholder?: string;
  onPick: (m: Medicine, query: string) => void;
  /** With a submit button, Enter or the button picks the best suggestion, or calls onNoMatch when there is none. */
  submitLabel?: string; onNoMatch?: (query: string) => void;
  /** Offer the live FDA shortage check when the medicine is not in RxLantern's list. */
  otherLink?: boolean; labelClass?: string; className?: string;
}) {
  const { t, meta } = useApp();
  const meds = useMemo(() => medicines(meta?.drugs ?? []), [meta]);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const [open, setOpen] = useState(false);
  const list = useMemo(() => suggest(query, meds), [query, meds]);
  const q = query.trim();

  const pick = (m: Medicine) => { setOpen(false); onPick(m, query); };
  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") { setOpen(false); return; }
    if (!list.length) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setOpen(true); setActive((a) => (a + 1) % list.length); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => (a - 1 + list.length) % list.length); }
    else if (e.key === "Enter" && open && !submitLabel) { e.preventDefault(); pick(list[active]); }
  };
  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (list.length) pick(list[Math.min(active, list.length - 1)]);
    else if (q.length >= 2) onNoMatch?.(q);
  };

  const box = (
    <div className={`combo ${className}`}>
      <div className="input-row">
        <input id={id} role="combobox" aria-expanded={open && list.length > 0} aria-controls={listId}
          aria-autocomplete="list" aria-describedby={help ? `${id}-help` : undefined} autoComplete="off" value={query}
          aria-activedescendant={open && list.length ? `${id}-opt-${active}` : undefined}
          placeholder={placeholder} onKeyDown={onKey} maxLength={60}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); setActive(0); }} />
        <MicButton onText={(txt) => { setQuery(txt); setOpen(true); setActive(0); }} />
        {submitLabel && <button type="submit" className="btn primary"><span aria-hidden="true">🔎</span> {submitLabel}</button>}
      </div>
      {open && list.length > 0 && (
        <ul id={listId} role="listbox" className="suggestions" aria-label={t("suggestions")}>
          {list.map((m, i) => (
            <li key={m.label} id={`${id}-opt-${i}`} role="option" aria-selected={i === active}
              className={i === active ? "active" : ""} onMouseDown={(e) => { e.preventDefault(); pick(m); }}>
              <strong>{m.label}</strong>
              <span className="muted small"> · {m.options.map((o) => o.strength).join(" / ")}</span>
              {m.controlled && <span className="badge badge-warn small-badge">{t("controlledBadge")}</span>}
            </li>
          ))}
        </ul>
      )}
      {q.length >= 3 && list.length === 0 && (
        <div className="notice small no-match" role="status">
          <p>{t("noDrugMatch")}</p>
          {otherLink && <Link className="btn ghost" to={`/other-medicine?name=${encodeURIComponent(q)}`}>{t("otherCheckButton", { name: q })}</Link>}
        </div>
      )}
      <MicNote />
    </div>
  );

  return (
    <>
      <label htmlFor={id} className={labelClass}>{label}</label>
      {help && <p className="muted small" id={`${id}-help`}>{help}</p>}
      {submitLabel ? <form onSubmit={submit} role="search" noValidate>{box}</form> : box}
    </>
  );
}
