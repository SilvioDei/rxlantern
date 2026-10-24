// Turns the coverage facts from /api/results into plain sentences (English or Spanish). Always estimates, never a copay.
import type { Coverage, Plan } from "./api";
import type { Key } from "./i18n";

type T = (key: Key, vars?: Record<string, string | number>) => string;

const money = (n: number) => n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function nadacLine(c: Coverage, t: T): string {
  return c.nadac.estimate != null ? t("nadacLine", { amount: money(c.nadac.estimate), supply: c.nadac.amount }) : t("nadacNone");
}

/** Sentences for the coverage card, for the chosen insurance. */
export function coverageLines(c: Coverage, plan: Plan | null, t: T): string[] {
  const out: string[] = [];
  if (c.masshealth) {
    const m = c.masshealth;
    out.push(m.covered.startsWith("yes") ? t("mhCovered") : t("mhNotListed"));
    const pa = m.prior_authorization;
    if (pa === "yes") out.push(t("mhPA_yes"));
    else if (pa === "no") out.push(t("mhPA_no"));
    else if (pa && pa !== "not found") out.push(`${t("mhPA_some")} ${pa.replace(/^only in some cases:\s*/, "")}`);
    out.push(t("mhCopay"));
  } else if (c.medicare) {
    const m = c.medicare;
    out.push(t("mcCovering", { n: m.plans_covering, total: m.plans_in_massachusetts }));
    if (m.monthly_estimate) out.push(t("mcMonthly", { typical: money(m.monthly_estimate.typical), low: money(m.monthly_estimate.lowest), high: money(m.monthly_estimate.highest) }));
    if (m.plans_with_prior_authorization) out.push(t("mcPA", { n: m.plans_with_prior_authorization }));
    out.push(t("mcCap", { cap: m.yearly_cap }));
    if (m.insulin_cap) out.push(t("mcInsulin", { cap: m.insulin_cap }));
    if (m.negotiated_price) out.push(t("mcNegotiated"));
  } else if (c.commercial) {
    out.push(t("comNoList", { plan: plan && plan.id !== "other_commercial" ? plan.name : t("yourPlan") }));
  } else if (c.insurance === "uninsured") {
    out.push(t("uninsuredLine"));
  } else {
    out.push(t("noInsuranceChosen"));
  }
  return out;
}

/** One short line for each pharmacy card. */
export function cardCost(c: Coverage, t: T): string {
  if (c.medicare?.monthly_estimate) {
    return t("mcMonthly", { typical: money(c.medicare.monthly_estimate.typical), low: money(c.medicare.monthly_estimate.lowest), high: money(c.medicare.monthly_estimate.highest) });
  }
  const base = nadacLine(c, t);
  if (c.masshealth) return `${c.masshealth.covered.startsWith("yes") ? t("mhCovered") : t("mhNotListed")} ${base}`;
  return base;
}
