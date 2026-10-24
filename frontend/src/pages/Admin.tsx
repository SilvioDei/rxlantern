// Admin: the moderation queue. Only admin accounts can see it (checked again by the server).
import { useCallback, useEffect, useState } from "react";
import { useApp } from "../state";
import { api } from "../api";

interface Pending { id: number; pharmacy_id: string; rating: number; wait_minutes: number | null; visit_date: string; comment: string; moderation: { reason?: string } }

export function Admin() {
  const { t, me } = useApp();
  const [items, setItems] = useState<Pending[] | null>(null);
  const load = useCallback(() => { api.get<{ pending: Pending[] }>("/api/admin/pending").then((r) => setItems(r.pending)).catch(() => setItems([])); }, []);
  useEffect(() => { if (me.is_admin) load(); }, [me.is_admin, load]);

  if (!me.is_admin) return <p className="notice">{t("notAdmin")}</p>;
  return (
    <>
      <h1>{t("adminTitle")}</h1>
      {items && items.length === 0 && <p className="muted">{t("adminEmpty")}</p>}
      {items?.map((r) => (
        <article key={r.id} className="card">
          <p><strong>{r.pharmacy_id}</strong> · {"★".repeat(r.rating)} · {r.visit_date}{r.wait_minutes != null && ` · ${r.wait_minutes} min`}</p>
          <p className="review-text">{r.comment}</p>
          <p className="muted small">{r.moderation?.reason}</p>
          <div className="card-actions">
            <button type="button" className="btn primary" onClick={async () => { await api.post(`/api/admin/reviews/${r.id}/approve`); load(); }}>{t("approve")}</button>
            <button type="button" className="btn ghost" onClick={async () => { await api.post(`/api/admin/reviews/${r.id}/reject`); load(); }}>{t("reject")}</button>
          </div>
        </article>
      ))}
    </>
  );
}
