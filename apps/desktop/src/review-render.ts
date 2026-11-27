// #290: the markup of the Review & Edit panel. Pure functions from a review
// context and its draft to escaped HTML (safe-html.ts): every model value is
// text, never markup. Controls appear only for actions the engine's
// permitted_actions allow on the current version; everything else is shown
// read-only.

import type { ModelReport } from "./model-report";
import type { EngineGraphResponse } from "./model-types";
import { categoryLabel, findVersion, versionLabel, type ProjectVersions } from "./project-workspace";
import {
  FEASIBILITY_VALUES,
  IMPACT_CATEGORIES,
  SEVERITY_VALUES,
  TEXT_LIMIT,
  type ReviewContext,
  type ReviewRecord,
} from "./review-contract";
import {
  feasibilityValue,
  impactValue,
  ownReview,
  reviewValues,
  type DraftProblem,
  type RouteDraft,
} from "./review-drafts";
import type { RiskCalculation } from "./risk-calculation";
import { html, type SafeHtml } from "./safe-html";

/** Display names for the ids a context names: report names first, then graph labels. */
export class ReviewNames {
  private readonly names = new Map<string, string>();

  constructor(report: ModelReport | undefined, graph: EngineGraphResponse | undefined) {
    for (const node of graph?.nodes ?? []) if (node.label) this.names.set(node.id, node.label);
    if (!report) return;
    for (const item of [...report.threats, ...report.damageScenarios, ...report.attackPaths]) this.names.set(item.id, item.name);
    for (const risk of report.risks) {
      if (risk.id) this.names.set(risk.id, risk.name);
      if (risk.stakeholder) this.names.set(risk.stakeholder.id, risk.stakeholder.label);
    }
    for (const path of report.attackPaths) for (const step of path.story.steps) this.names.set(step.id, step.name);
  }

  of(id: string | null | undefined, fallback = "Not recorded"): string {
    if (!id) return fallback;
    return this.names.get(id) ?? id;
  }
}

export interface ReviewRenderInput {
  context: ReviewContext;
  draft: RouteDraft | undefined;
  names: ReviewNames;
  versions: ProjectVersions | undefined;
  /** True only on the project's current version, with the panel not saving. */
  editable: boolean;
  saving: boolean;
  problems: readonly DraftProblem[];
}

const FEASIBILITY_LABELS: Readonly<Record<string, string>> = {
  high: "High", medium: "Medium", low: "Low", very_low: "Very low",
};
const SEVERITY_LABELS: Readonly<Record<string, string>> = {
  negligible: "Negligible", moderate: "Moderate", major: "Major", severe: "Severe",
};
const STATE_LABELS: Readonly<Record<string, string>> = {
  accepted: "Accepted",
  proposed: "Proposed, not accepted",
  rejected: "Rejected",
  changes_requested: "Changes requested",
  unreviewed: "Not reviewed",
};
const VERDICT_LABELS: Readonly<Record<string, string>> = {
  accepted: "Accepted",
  rejected: "Rejected",
  changes_requested: "Changes requested",
};
const PROBLEM_TEXT: Readonly<Record<string, string>> = {
  route_specific_path_required: "No authored attack path matches exactly this route, so it has no route-specific record to review or rate. A model author must add a separate attack path for this route first.",
  feasibility_missing: "Feasibility is not rated for this route.",
  conflicting_route_ratings: "The authored paths that own this route give different feasibility ratings, so the route stays unresolved until they agree. Saving one value does not change the others.",
  route_rating_required: "No authored attack path owns this route, so its feasibility cannot be rated here.",
  damage_scenario_scope_mismatch: "The assessment's damage scenario differs from the threat's, so its risk is withheld.",
  attack_path_scope_mismatch: "The assessment's attack paths differ from the threat's, so its risk is withheld.",
};

export function feasibilityLabel(value: string | null | undefined): string {
  return value ? FEASIBILITY_LABELS[value] ?? value : "Not rated";
}

export function severityLabel(value: string | null | undefined): string {
  return value ? SEVERITY_LABELS[value] ?? value : "Not rated";
}

export function problemText(code: string): string {
  return PROBLEM_TEXT[code] ?? `Unresolved input: ${code}`;
}

export function revisionName(versions: ProjectVersions | undefined, revision: string): string {
  const version = findVersion(versions, revision);
  return version ? versionLabel(version) : `Version ${revision}`;
}

function fieldError(problems: readonly DraftProblem[], target: string, field: DraftProblem["field"]): DraftProblem | undefined {
  return problems.find((problem) => problem.target === target && problem.field === field);
}

function predicateText(predicate: string): string {
  return predicate === "realizes_threat" ? "realizes the threat" : predicate.replace(/_/g, " ");
}

export function assertionTitle(names: ReviewNames, assertion: ReviewContext["assertions"][number]): string {
  return `${names.of(assertion.subject)} ${predicateText(assertion.predicate)} ${names.of(assertion.object)}`;
}

function reviewLine(names: ReviewNames, context: ReviewContext, review: ReviewRecord): SafeHtml {
  const you = review.reviewer === context.reviewer_id ? " (you)" : "";
  return html`<strong>${names.of(review.reviewer, "Unknown reviewer")}${you}</strong>: ${VERDICT_LABELS[review.review_status ?? ""] ?? review.review_status ?? "No verdict"}.
 Rationale: ${review.justification?.trim() ? review.justification : "none recorded"}.${review.description?.trim() ? html` Annotation: ${review.description}` : ""}`;
}

function assertionBlock(input: ReviewRenderInput, index: number): SafeHtml {
  const { context, names, editable, saving, problems } = input;
  const assertion = context.assertions[index];
  const prefix = `review-a${index}`;
  const state = context.review_states.find((item) => item.id === assertion.id);
  const records = context.reviews.filter((review) => review.reviews === assertion.id);
  const own = ownReview(context, assertion.id);
  const allowed = own ? context.permitted_actions.correct_own_review : context.permitted_actions.submit_review;
  const meta = html`<p id="${prefix}-meta" class="review-meta">${assertion.asserted_by ? html`Proposed by ${names.of(assertion.asserted_by)}` : "Proposer not recorded"}${assertion.generated_by ? html` · generated by ${assertion.generated_by}` : ""}${assertion.confidence ? html` · confidence ${assertion.confidence}` : ""} · recorded status ${assertion.assertion_status ?? "not recorded"} · review state: ${STATE_LABELS[state?.status ?? ""] ?? state?.status ?? "not recorded"}</p>`;
  const existing = records.length
    ? html`<ul class="review-records">${records.map((review) => html`<li>${reviewLine(names, context, review)}</li>`)}</ul>`
    : html`<p class="review-empty">No human review is recorded yet.</p>`;
  if (!(editable && allowed)) {
    return html`<div class="review-assertion" role="group" aria-labelledby="${prefix}-title" aria-describedby="${prefix}-meta">
<h4 id="${prefix}-title">${assertionTitle(names, assertion)}</h4>${meta}${existing}</div>`;
  }
  const values = reviewValues(context, input.draft, assertion.id);
  const verdictError = fieldError(problems, assertion.id, "verdict");
  const rationaleError = fieldError(problems, assertion.id, "rationale");
  const annotationError = fieldError(problems, assertion.id, "annotation");
  const disabled = saving ? html` disabled` : "";
  const radio = (value: "accepted" | "rejected", text: string) => html`<label class="review-choice"><input type="radio" name="${prefix}-verdict" id="${prefix}-verdict-${value}" value="${value}" data-review-field="verdict" data-target="${assertion.id}"${values.verdict === value ? html` checked` : ""}${disabled}${verdictError ? html` aria-describedby="${prefix}-verdict-error"` : ""}> ${text}</label>`;
  return html`<fieldset class="review-assertion" aria-describedby="${prefix}-meta">
<legend id="${prefix}-title">${assertionTitle(names, assertion)}</legend>${meta}${existing}
<fieldset class="review-verdict"${verdictError ? html` aria-invalid="true"` : ""}><legend>${own ? "Correct your review" : "Your decision"}</legend>${radio("accepted", "Accept")}${radio("rejected", "Reject")}</fieldset>
${verdictError ? html`<p id="${prefix}-verdict-error" class="field-error">${verdictError.message}</p>` : ""}
<label class="review-label" for="${prefix}-rationale">Rationale (required)</label>
<textarea id="${prefix}-rationale" rows="3" maxlength="${TEXT_LIMIT}" data-review-field="rationale" data-target="${assertion.id}" aria-describedby="${prefix}-rationale-help${rationaleError ? html` ${prefix}-rationale-error` : ""}"${rationaleError ? html` aria-invalid="true"` : ""}${disabled}>${values.rationale}</textarea>
<p id="${prefix}-rationale-help" class="review-help">Why you accept or reject this proposal. It is saved as the review's justification.</p>
${rationaleError ? html`<p id="${prefix}-rationale-error" class="field-error">${rationaleError.message}</p>` : ""}
<label class="review-label" for="${prefix}-annotation">Annotation (optional)</label>
<textarea id="${prefix}-annotation" rows="2" maxlength="${TEXT_LIMIT}" data-review-field="annotation" data-target="${assertion.id}"${annotationError ? html` aria-describedby="${prefix}-annotation-error" aria-invalid="true"` : ""}${disabled}>${values.annotation}</textarea>
${annotationError ? html`<p id="${prefix}-annotation-error" class="field-error">${annotationError.message}</p>` : ""}
${own ? html`<p class="review-help">Saving changes your own review in a new version; earlier versions keep it as it was.</p>` : ""}
</fieldset>`;
}

function historyBlock(input: ReviewRenderInput): SafeHtml | string {
  const { context, names, versions } = input;
  if (context.history.length === 0) return html`<p class="review-empty">No review history through this version.</p>`;
  return html`<details class="review-history"><summary>Review history (${context.history.length})</summary>
<ol>${context.history.map((entry) => html`<li><span class="review-history-version">${revisionName(versions, entry.revision)}</span> ${reviewLine(names, context, entry.review)}</li>`)}</ol></details>`;
}

function feasibilityBlock(input: ReviewRenderInput): SafeHtml {
  const { context, names, editable, saving } = input;
  const owners = context.route.rating_paths.filter((id) => context.attack_paths.some((path) => path.id === id));
  const canRate = editable && context.permitted_actions.save_feasibility;
  const rows = owners.map((pathId, index) => {
    const id = `review-p${index}-feasibility`;
    const recorded = context.attack_paths.find((path) => path.id === pathId)?.attack_feasibility ?? null;
    const value = feasibilityValue(context, input.draft, pathId);
    const error = fieldError(input.problems, pathId, "feasibility");
    if (!canRate) {
      return html`<p class="review-value"><span>Feasibility of ${names.of(pathId)}</span> <strong>${feasibilityLabel(recorded)}</strong></p>`;
    }
    return html`<div class="review-field"><label class="review-label" for="${id}">Feasibility of ${names.of(pathId)}</label>
<select id="${id}" data-review-field="feasibility" data-target="${pathId}"${saving ? html` disabled` : ""}${error ? html` aria-invalid="true" aria-describedby="${id}-error"` : ""}>
<option value=""${value === null ? html` selected` : ""}>Not rated</option>${FEASIBILITY_VALUES.map((option) => html`<option value="${option}"${value === option ? html` selected` : ""}>${feasibilityLabel(option)}</option>`)}
</select>${value !== recorded ? html`<span class="review-was">Recorded: ${feasibilityLabel(recorded)}</span>` : ""}
${error ? html`<p id="${id}-error" class="field-error">${error.message}</p>` : ""}</div>`;
  });
  const problems = [...context.route.problems, ...context.problems].filter((code, index, all) => all.indexOf(code) === index);
  return html`<section class="review-block" aria-labelledby="review-feasibility-heading">
<h3 id="review-feasibility-heading">Route feasibility</h3>
<p class="review-help">How hard this route is for an attacker. It is stored on the authored attack path that owns exactly this route, and applies to this route only.</p>
${rows.length ? rows : html`<p class="review-empty">No authored path rates this route.</p>`}
${problems.length ? html`<ul class="review-flags">${problems.map((code) => html`<li>${problemText(code)}</li>`)}</ul>` : ""}
</section>`;
}

function impactBlock(input: ReviewRenderInput): SafeHtml {
  const { context, names, editable, saving } = input;
  const canRate = editable && context.permitted_actions.save_impacts;
  const scores = context.risk_scores.map((score, index) => {
    const missing = IMPACT_CATEGORIES.filter((category) => (score.impact[category] ?? null) === null);
    const title = html`${names.of(score.damage_scenario, "Damage scenario not recorded")} for ${names.of(score.for_stakeholder, "stakeholder not recorded")}`;
    const cells = IMPACT_CATEGORIES.map((category) => {
      const id = `review-s${index}-${category}`;
      const recorded = score.impact[category] ?? null;
      const value = impactValue(context, input.draft, score.id, category);
      if (!canRate) return html`<p class="review-value"><span>${categoryLabel(category)}</span> <strong>${severityLabel(recorded)}</strong></p>`;
      return html`<div class="review-field"><label class="review-label" for="${id}">${categoryLabel(category)}</label>
<select id="${id}" data-review-field="impact" data-target="${score.id}" data-category="${category}"${saving ? html` disabled` : ""}>
<option value=""${value === null ? html` selected` : ""}>Not rated</option>${SEVERITY_VALUES.map((option) => html`<option value="${option}"${value === option ? html` selected` : ""}>${severityLabel(option)}</option>`)}
</select>${value !== recorded ? html`<span class="review-was">Recorded: ${severityLabel(recorded)}</span>` : ""}</div>`;
    });
    const error = fieldError(input.problems, score.id, "impact");
    return html`<fieldset class="review-impact"><legend>${title}</legend><div class="review-impact-grid">${cells}</div>
${missing.length ? html`<p class="review-flag">Not rated: ${missing.map(categoryLabel).join(", ")}.</p>` : ""}
${error ? html`<p class="field-error">${error.message}</p>` : ""}</fieldset>`;
  });
  return html`<section class="review-block" aria-labelledby="review-impact-heading">
<h3 id="review-impact-heading">Scenario impact</h3>
<p class="review-help">How bad the damage is, per damage scenario and stakeholder. It is recorded on the threat's risk assessment, so it applies to every route of this threat.</p>
${scores.length ? scores : html`<p class="review-flag">No risk assessment is recorded for this threat, so there is no impact to rate.</p>`}
</section>`;
}

/** The engine's derived risk for one route, per assessment of its threat. */
export function routeRisk(risk: RiskCalculation, threatId: string, routeId: string) {
  return risk.assessments
    .filter((assessment) => assessment.threat === threatId)
    .map((assessment) => ({
      assessment,
      route: assessment.routes.find((route) => route.id === routeId),
      withheld: assessment.damage_scenario === null || assessment.problems.some((problem) => problem.endsWith("_scope_mismatch")),
    }));
}

export function riskValues(values: Readonly<Record<string, number | null>> | undefined, before?: Readonly<Record<string, number | null>>): string {
  if (!values) return "Not calculated";
  return IMPACT_CATEGORIES.map((category) => {
    const value = values[category] ?? null;
    const was = before?.[category] ?? null;
    const text = value === null ? "not calculated" : String(value);
    return `${categoryLabel(category)} ${text}${before && was !== value ? ` (was ${was ?? "not calculated"})` : ""}`;
  }).join(" · ");
}

function riskBlock(input: ReviewRenderInput): SafeHtml {
  const { context, names, versions } = input;
  const entries = routeRisk(context.calculated_risk, context.threat.id, context.route.id);
  return html`<section class="review-block" aria-labelledby="review-risk-heading">
<h3 id="review-risk-heading">Calculated risk for this route</h3>
<p class="review-help">Calculated by the engine for ${revisionName(versions, context.revision)} with the Annex H, Table H.8 example profile. Each impact category stays separate, and mitigation status does not lower the score.</p>
${entries.length ? html`<ul class="review-risk">${entries.map(({ assessment, route, withheld }) => html`<li>
<strong>${assessment.id ? names.of(assessment.id) : "No risk assessment recorded"}</strong>${assessment.for_stakeholder ? html` for ${names.of(assessment.for_stakeholder)}` : ""}:
 ${withheld ? "risk withheld until the assessment's damage and attack-path scope are valid" : riskValues(route?.derived_risk)}.
 ${assessment.complete ? "Inputs complete." : html`<span class="review-flag">Incomplete assessment.</span>`}
${assessment.problems.length ? html`<ul class="review-flags">${assessment.problems.map((code) => html`<li>${problemText(code)}</li>`)}</ul>` : ""}</li>`)}</ul>`
    : html`<p class="review-empty">The engine calculated no assessment for this threat.</p>`}
</section>`;
}

/** The whole context: proposals and reviews, then the two kinds of rating, then risk. */
export function renderReviewContext(input: ReviewRenderInput): string {
  const { context, names } = input;
  return html`<section class="review-block" aria-labelledby="review-assertions-heading">
<h3 id="review-assertions-heading">Proposals and reviews</h3>
${input.editable
    ? html`<p class="review-help">Reviewing as ${names.of(context.reviewer_id)}, the reviewer the app's verified session names. Accepting or rejecting records your review in a new version; a proposal stays proposed until the sponsor accepts it, so the app never marks AI output as accepted on its own.</p>`
    : html`<p class="review-help">The proposals and human reviews this version records. A proposal stays proposed until the sponsor accepts it.</p>`}
${context.assertions.length ? context.assertions.map((_, index) => assertionBlock(input, index)) : html`<p class="review-empty">This route has no proposal to review.</p>`}
${historyBlock(input)}
</section>
${feasibilityBlock(input)}
${impactBlock(input)}
${riskBlock(input)}`.value;
}

/** The unsaved-changes summary: what Save New Version will send. */
export function changeLines(context: ReviewContext, draft: RouteDraft | undefined, names: ReviewNames): string[] {
  if (!draft) return [];
  const lines: string[] = [];
  for (const [assertionId, entry] of draft.reviews) {
    const assertion = context.assertions.find((item) => item.id === assertionId);
    const what = assertion ? assertionTitle(names, assertion) : names.of(assertionId);
    const values = reviewValues(context, draft, assertionId);
    const verdict = entry.verdict ? (entry.verdict === "accepted" ? "accept" : "reject") : values.own ? "edit your review of" : "review";
    lines.push(`${verdict.charAt(0).toUpperCase()}${verdict.slice(1)}: ${what}`);
  }
  for (const [pathId, rating] of draft.feasibility) {
    const recorded = context.attack_paths.find((path) => path.id === pathId)?.attack_feasibility ?? null;
    lines.push(`Feasibility of ${names.of(pathId)}: ${feasibilityLabel(recorded)} to ${feasibilityLabel(rating)}`);
  }
  for (const [scoreId, changed] of draft.impacts) {
    const score = context.risk_scores.find((item) => item.id === scoreId);
    for (const [category, value] of changed) {
      lines.push(`${categoryLabel(category)} impact for ${names.of(score?.damage_scenario ?? scoreId)}: ${severityLabel(score?.impact[category] ?? null)} to ${severityLabel(value)}`);
    }
  }
  return lines;
}
