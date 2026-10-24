// My medicine list (one-stop pharmacy): 2 to 5 of our medicines -> nearby pharmacies ranked by how likely they are to
// fill all of them (recent patient reports, FDA shortage status, open now, distance). The list is saved only in this
// browser, and the patient's location never leaves it (distances are measured here).
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../state";
import { api, type DrugMeta, type PharmacyBrief } from "../api";
import { useOrigin } from "../origin";
import { MedicineSearch } from "../components/MedicineSearch";
import { MicButton, MicNote, OpenBadge, ReadAloud, SampleBadge, SourceLink, miles, telHref } from "../components/Bits";
import { ReportedLanguages, SendHereLink } from "../components/Journey";
import type { Medicine } from "../search";

const KEY = "rxlantern.mylist";
interface ListDrug { id: string; name: string; controlled: boolean; shortage_status: string; checked_date: string; source: string }
interface ListPharmacy extends PharmacyBrief {
  reported_in_stock: string[]; reported_out: string[]; sample_reported_in_stock: string[]; score_base: number;
}
interface ListData { drugs: ListDrug[]; pharmacies: ListPharmacy[]; shortages: number; sample_data: boolean }

function loadIds(): string[] {
  try { return (JSON.parse(localStorage.getItem(KEY) || "[]") as string[]).slice(0, 5); } catch { return []; }
}

export function MyList() {
  const { t, meta, lang, place, set } = useApp();
  const { origin } = useOrigin();
  const [ids, setIds] = useState<string[]>(loadIds);
  const [choosing, setChoosing] = useState<Medicine | null>(null);
  const [data, setData] = useState<ListData | null>(null);
  const [error, setError] = useState("");
  const [showAll, setShowAll] = useState(false);
  const [placeText, setPlaceText] = useState(place);

  useEffect(() => { localStorage.setItem(KEY, JSON.stringify(ids)); }, [ids]);
  useEffect(() => {
    setData(null);
    setError("");
    if (ids.length < 2) return;
    api.get<ListData>(`/api/my-list?drug_ids=${ids.join(",")}&lang=${lang}`).then(setData).catch(() => setError(t("errorGeneric")));
  }, [ids, lang, t]);

  const drugs = useMemo(() => ids.map((id) => meta?.drugs.find((d) => d.id === id)).filter(Boolean) as DrugMeta[], [ids, meta]);
  const add = (id: string) => { setChoosing(null); setIds((xs) => (xs.includes(id) || xs.length >= 5 ? xs : [...xs, id])); };
  const pick = (m: Medicine) => (m.options.length === 1 ? add(m.options[0].id) : setChoosing(m));

  const ranked = useMemo(() => (data?.pharmacies ?? []).map((p) => {
    const dist = origin ? Math.round(miles(origin, { lat: p.latitude, lon: p.longitude }) * 10) / 10 : null;
    return { ...p, dist, score: p.score_base - (dist ?? 0) * 0.3 };
  }).sort((a, b) => b.score - a.score || (a.dist ?? 0) - (b.dist ?? 0)), [data, origin]);
  const names = (list: string[]) => list.map((id) => data?.drugs.find((d) => d.id === id)?.name ?? id).join(", ");
  const total = data?.drugs.length ?? 0;
  const shortageNames = (data?.drugs ?? []).filter((d) => d.shortage_status === "in shortage").map((d) => d.name);
  const controlled = (data?.drugs ?? []).filter((d) => d.controlled);
  const shown = showAll ? ranked : ranked.slice(0, 8);

  return (
    <div className="mylist-page">
      <h1>{t("myListTitle")}</h1>
      <p className="lead">{t("myListIntro")}</p>

      <section className="card mylist-edit" aria-labelledby="ml-list">
        <h2 id="ml-list" className="h3">{t("myListCount", { n: ids.length })}</h2>
        {drugs.length === 0 ? <p className="muted">{t("myListEmpty")}</p> : (
          <ul className="mylist-items">
            {drugs.map((d) => (
              <li key={d.id} className="mylist-item">
                <span><strong>{d.name}</strong>{d.controlled && <span className="badge badge-warn small-badge">{t("controlledBadge")}</span>}</span>
                <button type="button" className="link-button" aria-label={`${t("myListRemove")}: ${d.name}`}
                  onClick={() => setIds((xs) => xs.filter((x) => x !== d.id))}>{t("myListRemove")}</button>
              </li>
            ))}
          </ul>
        )}
        {ids.length < 5 ? (
          choosing ? (
            <fieldset className="option-list">
              <legend>{t("myListWhich")} — {choosing.label}</legend>
              {choosing.options.map((o) => (
                <button key={o.id} type="button" className="option" onClick={() => add(o.id)}>
                  <strong>{o.strength}</strong> · {o.form}</button>
              ))}
              <button type="button" className="link-button" onClick={() => setChoosing(null)}>{t("cancel")}</button>
            </fieldset>
          ) : (
            <MedicineSearch key={ids.join(",")} id="mylist-search" listId="mylist-search-list" label={t("myListAddLabel")}
              labelClass="field-label" placeholder={t("myListPlaceholder")} onPick={pick} />
          )
        ) : <p className="notice small">{t("myListMax")}</p>}
        <form className="mylist-place" onSubmit={(e) => { e.preventDefault(); set({ place: placeText.trim() }); }}>
          <label htmlFor="mylist-place" className="field-label">{t("myListPlace")}</label>
          <div className="input-row">
            <input id="mylist-place" value={placeText} maxLength={40} list="neighborhoods-ml" placeholder={t("placePlaceholder")}
              onChange={(e) => setPlaceText(e.target.value)} onBlur={() => set({ place: placeText.trim() })} />
            <datalist id="neighborhoods-ml">{meta?.neighborhoods.map((n) => <option key={n} value={n} />)}</datalist>
            <MicButton onText={(txt) => { const v = txt.replace(/[.!?]+$/, "").slice(0, 40); setPlaceText(v); set({ place: v }); }} />
            <button type="submit" className="btn">{t("send")}</button>
          </div>
          <MicNote />
        </form>
        {ids.length > 0 && <button type="button" className="btn ghost" onClick={() => setIds([])}>{t("myListClear")}</button>}
      </section>

      {ids.length < 2 && <p className="notice" role="status">{t("myListNeedTwo")}</p>}
      {error && <p className="alert" role="alert">{error}</p>}
      {ids.length >= 2 && !data && !error && <p className="muted" role="status">{t("loading")}</p>}
      {data && (
        <section aria-labelledby="ml-ranked">
          <div className="section-head">
            <h2 id="ml-ranked">{t("myListRanked")}</h2>
            <ReadAloud text={() => [t("myListRanked"), ...shown.slice(0, 3).map((p) =>
              `${p.name}, ${p.address}. ${t("myListInStock", { n: p.reported_in_stock.length, total })}.`), t("myListNever")].join(" ")} />
          </div>
          <p className="small muted">{t("myListHow")}</p>
          <p className="notice" role="note">{t("myListNever")}</p>
          {shortageNames.length > 0 && <p className="alert small">{t("myListShortage", { names: shortageNames.join(", ") })}</p>}
          {controlled.map((d) => <p key={d.id} className="notice small">{t("myListControlled", { name: d.name })}</p>)}
          <p className="src muted">FDA · {t("checked", { date: data.drugs[0]?.checked_date ?? "" })} · <SourceLink url={data.drugs[0]?.source} /></p>
          <div className="mylist-results">
            {shown.map((p, i) => (
              <article key={p.id} className="card mylist-card" aria-labelledby={`ml-${p.id}`}>
                <div className="card-top">
                  <h3 id={`ml-${p.id}`}><span className="rank">{i + 1}.</span> <Link to={`/pharmacies/${p.id}`}>{p.name}</Link></h3>
                  <OpenBadge open={p.open_now} opensNext={p.opens_next} status={p.status} />
                </div>
                <p className="address">{p.address}{p.dist != null && <span className="muted"> · {t("away", { miles: p.dist })}</span>}</p>
                <p className="small">{t("counterToday", { hours: p.counter_today === "closed" ? t("closed") : p.counter_today })}</p>
                <p className="fill-line"><strong>{t("myListInStock", { n: p.reported_in_stock.length, total })}</strong></p>
                {p.reported_out.length > 0 && <p className="small warn-text">{t("myListOut", { names: names(p.reported_out) })}</p>}
                {p.reported_in_stock.length + p.reported_out.length === 0 && <p className="small muted">{t("myListNoReports")}</p>}
                {p.sample_reported_in_stock.length > 0 && (
                  <p className="small sample-line"><SampleBadge /> {t("myListSampleLine", { n: p.sample_reported_in_stock.length, total })}</p>
                )}
                <ReportedLanguages real={p.reported_languages} sample={p.sample_reported_languages} compact />
                <p className="reminder small">{t("callToConfirm")}</p>
                <div className="card-actions">
                  <a className="btn primary" href={telHref(p.phone)}><span aria-hidden="true">📞</span> {t("call")} {p.phone}</a>
                  <SendHereLink pharmacyId={p.id} />
                </div>
              </article>
            ))}
          </div>
          {ranked.length > 8 && !showAll && <button type="button" className="btn ghost" onClick={() => setShowAll(true)}>{t("showAll", { n: ranked.length })}</button>}
        </section>
      )}
    </div>
  );
}
