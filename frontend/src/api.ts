// Small fetch helpers for the RxLantern API. Errors become friendly codes the pages translate.

export type ApiErrorCode = "offline" | "rate" | "busy" | "generic" | "http";

export class ApiError extends Error {
  code: ApiErrorCode;
  status: number;
  constructor(code: ApiErrorCode, message: string, status = 0) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, { credentials: "same-origin", headers: { "Content-Type": "application/json" }, ...init });
  } catch {
    throw new ApiError("offline", "offline");
  }
  let body: any = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  if (!res.ok) {
    if (res.status === 429 && body?.stop_reason?.startsWith("rate limit")) throw new ApiError("rate", body.reply_text, 429);
    const msg = body?.error || body?.detail || "error";
    throw new ApiError(res.status >= 500 ? "generic" : "http", msg, res.status);
  }
  return body as T;
}

export const api = {
  get: <T>(path: string) => call<T>(path),
  post: <T>(path: string, data?: unknown) => call<T>(path, { method: "POST", body: JSON.stringify(data ?? {}) }),
  del: <T>(path: string) => call<T>(path, { method: "DELETE" }),
};

// ---- shapes returned by the backend (only the fields the site uses)
export interface Fact { text: string; source: string; checked_date: string }
export interface PharmacyCard {
  id: string; name: string; address: string; phone: string; open_now: boolean | null; status: string;
  closes_at: string | null; opens_next: string | null; distance_miles: number | null;
}
export interface FinalReply {
  run_id: string; language: "en" | "es"; reply_text: string; stop_reason: string;
  pharmacy_cards: PharmacyCard[]; call_script: string | null; sources: Fact[]; follow_up_question: string | null;
  warnings: string[]; agents_run: string[];
  usage: { total_tokens: number; cost_usd: number | null };
}
export interface Meta {
  app_name: string; neighborhoods: string[]; insurance_types: string[];
  pharmacies: { id: string; name: string; address: string; neighborhood: string }[];
  drugs: { id: string; name: string; controlled: boolean }[];
  vaccines: { id: string; name: string }[];
}
export interface PharmacyBrief {
  id: string; name: string; type: string; address: string; phone: string; neighborhood: string;
  latitude: number; longitude: number; open_now: boolean | null; status: string; closes_at: string | null;
  opens_next: string | null; delivery: string; drive_thru: string; wheelchair_accessible: string;
  languages: string[] | string; vaccines: string[]; website: string; checked_date: string;
}
export interface Me { logged_in: boolean; display_name?: string; is_admin?: boolean }
export interface StockSummary {
  drugs: { drug_id: string; drug?: string; in_stock_reports: number; out_of_stock_reports: number; latest_report: string; conflicting: boolean }[];
  message: string | null; reminder: string;
}
export interface ReviewSummary {
  reviews: number; average_rating: number | null; average_wait_minutes: number | null; message: string | null;
  recent: { rating: number; wait_minutes: number | null; visit_date: string; comment: string | null; by: string }[];
}
