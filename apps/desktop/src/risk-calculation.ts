// Display engine results without deriving scores or changing recorded ratings (#63).
import type { ModelReport } from "./model-report";
import { html, type SafeHtml } from "./safe-html.ts";

export const RISK_MATRIX = "annex-h-table-h8";
const CATEGORIES = ["safety", "financial", "operational", "privacy"] as const;
type Category = typeof CATEGORIES[number];
type Vector<T> = Record<Category, T>;
interface Route {
  id: string;
  steps: string[];
  feasibility: string | null;
  derived_risk: Vector<number | null>;
  problems: string[];
}
interface Assessment {
  id: string | null;
  threat: string;
  damage_scenario: string | null;
  for_stakeholder: string | null;
  feasibility: string | null;
  impact: Vector<string | null>;
  derived_risk: Vector<number | null>;
  mitigation_status: string | null;
  routes: Route[];
  complete: boolean;
  problems: string[];
}
export interface RiskCalculation {
  file: string;
  matrix: string;
  count: number;
  assessments: Assessment[];
}

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function strings(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}
function nullableString(value: unknown): boolean {
  return value === null || typeof value === "string";
}
function feasibility(value: unknown): boolean {
  return value === null || (typeof value === "string"
    && ["very_low", "low", "medium", "high"].includes(value));
}
function vector(value: unknown, check: (item: unknown) => boolean): boolean {
  return record(value) && CATEGORIES.every((key) => check(value[key]));
}
function risk(value: unknown): boolean {
  return value === null || (Number.isInteger(value) && Number(value) >= 1 && Number(value) <= 5);
}

/** A failed or mismatched answer stays an error, never an apparently complete assessment. */
export function parseRiskCalculation(value: unknown, file: string, matrix: string): RiskCalculation {
  const bad = () => { throw new Error("The engine returned an invalid or mismatched risk calculation."); };
  if (!record(value) || value.file !== file.split(/[\\/]/).pop() || value.matrix !== matrix
    || matrix !== RISK_MATRIX || !Array.isArray(value.assessments)
    || value.count !== value.assessments.length) return bad();
  for (const item of value.assessments) {
    if (!record(item) || !nullableString(item.id) || typeof item.threat !== "string"
      || !nullableString(item.damage_scenario) || !nullableString(item.for_stakeholder)
      || !feasibility(item.feasibility) || typeof item.complete !== "boolean"
      || !strings(item.problems) || !Array.isArray(item.routes)
      || !vector(item.derived_risk, risk)
      || !vector(item.impact, (rating) => rating === null
        || (typeof rating === "string" && ["negligible", "moderate", "major", "severe"].includes(rating)))
      || !(item.mitigation_status === null
        || (typeof item.mitigation_status === "string"
          && ["planned", "in_progress", "complete", "accepted_risk", "not_applicable"].includes(item.mitigation_status)))) return bad();
    if (item.complete && (item.problems.length > 0 || item.feasibility === null
      || !vector(item.derived_risk, (value) => value !== null && risk(value)))) return bad();
    for (const route of item.routes) {
      if (!record(route) || typeof route.id !== "string" || !strings(route.steps)
        || !feasibility(route.feasibility) || !vector(route.derived_risk, risk)
        || !strings(route.problems)) return bad();
    }
  }
  return value as unknown as RiskCalculation;
}

function label(value: string | null): string {
  if (value === null) return "Not recorded";
  const words = value.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}
function values(value: Vector<string | number | null>, missing = "Not calculated"): SafeHtml {
  return html`<ul>${CATEGORIES.map((category) => html`<li>${label(category)}: ${
    value[category] === null ? missing : label(String(value[category]))
  }</li>`)}</ul>`;
}
function problems(items: string[]): SafeHtml | string {
  return items.length ? html`<details><summary>Unresolved input details</summary><ul>${
    items.map((item) => html`<li>${item}</li>`)
  }</ul></details>` : "";
}

export function renderRiskCalculation(result: RiskCalculation, report: ModelReport): string {
  const names = new Map<string, string>();
  for (const item of [...report.threats, ...report.damageScenarios]) names.set(item.id, item.name);
  for (const risk of report.risks) {
    if (risk.stakeholder) names.set(risk.stakeholder.id, risk.stakeholder.label);
  }
  for (const path of report.attackPaths) for (const step of path.story.steps) names.set(step.id, step.name);
  const name = (id: string | null, fallback: string) => id === null ? fallback : names.get(id) ?? fallback;
  return html`<div class="calculated-risk">
<h4>Calculated risk vector</h4>
<p>Matrix: Annex H, Table H.8 example. This informative profile is not a universal ISO/SAE 21434 formula.</p>
<p>Safety, financial, operational and privacy results remain separate. The scenario shows the highest risk across its routes. Mitigation status does not lower the score.</p>
${result.assessments.length === 0 ? html`<p>No threats are recorded in this model.</p>` : html`
<div class="report-table-scroll"><table class="report-table"><caption>Calculated assessments and recorded inputs</caption>
<thead><tr><th scope="col">Threat and damage</th><th scope="col">Feasibility</th><th scope="col">Impact</th><th scope="col">Derived risk</th><th scope="col">Mitigation</th><th scope="col">Input status</th></tr></thead>
<tbody>${result.assessments.map((item) => html`<tr>
<th scope="row">${name(item.threat, "Threat")}<div class="cell-note">${name(item.damage_scenario, "Damage not recorded")}</div><div class="cell-note">For ${name(item.for_stakeholder, "stakeholder not recorded")}</div><div class="cell-note">Path review: ${report.threats.find((threat) => threat.id === item.threat)?.status.label ?? "Not reviewed"}</div></th>
<td>${label(item.feasibility)}</td><td>${values(item.impact, "Not rated")}</td><td>${values(item.derived_risk)}</td>
<td>${label(item.mitigation_status)}</td><td>${item.complete ? "Inputs available" : "Incomplete"}${problems(item.problems)}</td>
</tr>`)}</tbody></table></div>`}
${result.assessments.map((item) => html`<details><summary>Routes for ${name(item.threat, "threat")}</summary>
${item.routes.length === 0 ? html`<p>No attack routes are available.</p>` : html`<ol>${item.routes.map((route, index) => html`<li>
<strong>Route ${index + 1}</strong>: ${route.steps.map((id) => name(id, "Attack step")).join(" → ")}
<p>Recorded feasibility: ${label(route.feasibility)}</p>${values(route.derived_risk)}${problems(route.problems)}
</li>`)}</ol>`}</details>`)}
<p class="cell-note">Recorded ratings require human verification. Calculation does not approve a threat or change a review. Missing or conflicting inputs remain unresolved.</p>
</div>`.value;
}
