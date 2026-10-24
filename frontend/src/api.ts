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
    const msg = body?.error || (typeof body?.detail === "string" ? body.detail : "") || "error";
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
  warnings: string[]; agents_run: string[]; emergency?: boolean; drug_id?: string | null;
  usage: { total_tokens: number; cost_usd: number | null };
}
export interface DrugMeta {
  id: string; name: string; controlled: boolean; generic: string; brands: string[]; strength: string; form: string;
  medicine: string; medicine_label: string;
}
export interface Meta {
  app_name: string; neighborhoods: string[]; insurance_types: string[];
  plans: { id: string; name: string; type: string }[];
  pharmacies: { id: string; name: string; address: string; neighborhood: string }[];
  drugs: DrugMeta[];
  vaccines: { id: string; name: string }[];
  sample_data: boolean;
}
export interface PharmacyBrief {
  id: string; name: string; type: string; address: string; phone: string; neighborhood: string;
  latitude: number; longitude: number; open_now: boolean | null; status: string; closes_at: string | null;
  closes_for?: string | null; opens_next: string | null; counter_today: string; closes_latest_minutes: number | null;
  store_today: string; delivery: string; delivery_summary: string | null; drive_thru: string;
  wheelchair_accessible: string; languages: string[] | string; vaccines: string[]; website: string;
  vaccine_booking_url: string; checked_date: string; hours_source: string;
}
export interface ReportCounts {
  drug_id?: string; in_stock_reports: number; out_of_stock_reports: number; latest_report: string; conflicting: boolean;
  sample?: boolean; drug?: string;
}
export interface ResultPharmacy extends PharmacyBrief {
  reviews: { reviews: number; average_rating: number | null; average_wait_minutes: number | null };
  sample_reviews: number;
  reports?: ReportCounts | null;
  sample_report?: ReportCounts | null;
}
export interface Plan {
  id: string; type: string; name: string; pharmacy_finder_url: string; member_services_phone: string;
  phone_note: string; finder_note: string; source_url: string; checked_date: string; verified: string;
}
export interface Shortage {
  status: string; summary: string; source: string; checked_date: string; fda_estimate: string | null;
  fda_updated: string | null;
}
export interface Coverage {
  insurance: string;
  nadac: { estimate: number | null; kind: string; amount: string; label: string; as_of: string; source: string; checked_date: string };
  masshealth?: { covered: string; prior_authorization: string; notes: string[] | string; list_last_updated: string; source: string; checked_date: string };
  medicare?: {
    plans_in_massachusetts: number; plans_covering: number; monthly_estimate: { lowest: number; typical: number; highest: number } | null;
    plans_with_prior_authorization: number; yearly_cap: string; insulin_cap: string | null; negotiated_price: boolean;
    amount: string; note: string; source: string; rules_source: string; checked_date: string;
  };
  commercial?: { coverage: string; answer: string; checked_date: string };
}
export interface Holiday { date: string; name: string; name_es: string }
export interface Results {
  drug: { id: string; name: string; strength: string; form: string; controlled: boolean; amount: string | null };
  shortage: Shortage; coverage: Coverage; plan: Plan | null; call_script: string; controlled_message: string | null;
  holidays: Holiday[]; checked_at: string; pharmacies: ResultPharmacy[]; reminder: string; sample_data: boolean;
}
export interface Me { logged_in: boolean; display_name?: string; is_admin?: boolean }
export interface StockSummary { drugs: ReportCounts[]; message: string | null; reminder: string }
export interface Review {
  rating: number; wait_minutes: number | null; visit_date: string; comment: string | null; by: string; sample?: boolean;
  pharmacy_id?: string; pharmacy?: string;
}
export interface ReviewSummary {
  reviews: number; average_rating: number | null; average_wait_minutes: number | null; message: string | null;
  recent: Review[];
}
