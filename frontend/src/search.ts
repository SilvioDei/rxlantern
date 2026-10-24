// Medicine suggestions for the search box: brand and generic names, small spelling mistakes allowed.
import type { DrugMeta } from "./api";

export interface Medicine { label: string; options: DrugMeta[]; controlled: boolean }

const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9.% ]+/g, " ").trim();

// Spanish spellings patients may type for our generic names.
const SPANISH: Record<string, string> = { amoxicilina: "amoxicillin", atorvastatina: "atorvastatin", levotiroxina: "levothyroxine",
  metformina: "metformin", amlodipino: "amlodipine", omeprazol: "omeprazole", sertralina: "sertraline", salbutamol: "albuterol",
  albuterol: "albuterol", insulina: "insulin", sumatriptan: "sumatriptan", latanoprost: "latanoprost", fluticasona: "fluticasone",
  triamcinolona: "triamcinolone", epinefrina: "epinephrine", nicotina: "nicotine", parche: "patch",
  losartan: "losartan", ibuprofeno: "ibuprofen", gabapentina: "gabapentin", prednisona: "prednisone",
  cefalexina: "cephalexin", azitromicina: "azithromycin", fluoxetina: "fluoxetine",
  escitalopram: "escitalopram", pantoprazol: "pantoprazole", famotidina: "famotidine", ondansetron: "ondansetron",
  montelukast: "montelukast", oseltamivir: "oseltamivir", furosemida: "furosemide", rosuvastatina: "rosuvastatin",
  simvastatina: "simvastatin", clopidogrel: "clopidogrel", warfarina: "warfarin", naloxona: "naloxone",
  metilfenidato: "methylphenidate", trazodona: "trazodone", bupropiona: "bupropion" };

function lev(a: string, b: string): number {
  const dp = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    let prev = dp[0];
    dp[0] = i;
    for (let j = 1; j <= b.length; j++) {
      const tmp = dp[j];
      dp[j] = Math.min(dp[j] + 1, dp[j - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1));
      prev = tmp;
    }
  }
  return dp[b.length];
}

export function medicines(drugs: DrugMeta[]): Medicine[] {
  const by = new Map<string, Medicine>();
  for (const d of drugs) {
    const m = by.get(d.medicine_label) ?? { label: d.medicine_label, options: [], controlled: false };
    m.options.push(d);
    m.controlled = m.controlled || d.controlled;
    by.set(d.medicine_label, m);
  }
  return [...by.values()];
}

function words(m: Medicine): string[] {
  const all = m.options.flatMap((d) => [d.medicine_label, d.generic, d.name, ...d.brands]).map(norm).join(" ");
  return [...new Set(all.split(/\s+/).filter((w) => w.length >= 3 && !/^\d/.test(w)))];
}

/** Best matches for what the patient typed, best first. */
export function suggest(query: string, meds: Medicine[], limit = 6): Medicine[] {
  let q = norm(query);
  if (q.length < 2) return [];
  q = q.split(/\s+/).map((w) => SPANISH[w] ?? w).join(" ");
  const qWords = q.split(/\s+/).filter((w) => w.length >= 2 && !/^\d/.test(w) && !["mg", "mcg", "ml"].includes(w));
  const scored: { m: Medicine; s: number }[] = [];
  for (const m of meds) {
    let best = 0;
    for (const w of words(m)) {
      for (const qw of qWords) {
        if (w === qw) best = Math.max(best, 3);
        else if (w.startsWith(qw)) best = Math.max(best, 2 + qw.length / 100);
        else if (qw.length >= 4) {
          const d = lev(qw, w.slice(0, Math.max(qw.length, Math.min(w.length, qw.length + 1))));
          const allowed = qw.length >= 7 ? 2 : 1;
          if (d <= allowed) best = Math.max(best, 1.5 - d / 10);
        }
      }
    }
    if (best > 0) scored.push({ m, s: best });
  }
  return scored.sort((a, b) => b.s - a.s || a.m.label.localeCompare(b.m.label)).slice(0, limit).map((x) => x.m);
}

/** If the patient typed a strength ("Concerta 18 mg"), pick the matching option. */
export function optionFromQuery(query: string, m: Medicine): DrugMeta | null {
  if (m.options.length === 1) return null;
  const nums = norm(query).match(/\d+(\.\d+)?/g) ?? [];
  const hits = m.options.filter((o) => nums.some((n) => o.strength.includes(n)));
  return hits.length === 1 ? hits[0] : null;
}
