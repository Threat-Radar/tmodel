// Renders a ModelReport as HTML (#208). The one renderer for both outputs: the
// app puts this markup in its report view, and the static Pages build writes it
// into one page per example model. Every model value is escaped (safe-html.ts),
// and the output holds no script, no event handler and no external reference.
//
// Technical identifiers (model ids, CURIEs, CPE and purl strings, schema field
// names, raw status values) appear only inside a closed "Details" toggle.
//
// Node runs this file directly (type stripping): `.ts` value imports only.

import type {
  AssetRow,
  ComponentRow,
  DamageRow,
  ImpactRating,
  MitigationRow,
  ModelReport,
  PathRow,
  ReportDetail,
  ReportRef,
  ReportStatus,
  ReportText,
  RequirementRow,
  RiskRow,
  ThreatRow,
} from "./model-report";
import { layoutPathDiagram, pathDiagramSvg } from "./path-diagram.ts";
import { html, join, trusted, type SafeHtml } from "./safe-html.ts";

export interface ReportRenderOptions {
  /** App only: adds "Open in path view" buttons (data-open-path). */
  interactive?: boolean;
  /** Static pages: a contents list linking to each section. */
  contents?: boolean;
}

/** The report's sections, in the order #208 and a TARA read them. */
export const REPORT_SECTIONS = [
  { id: "report-components", title: "Assets and components" },
  { id: "report-damage", title: "Damage scenarios" },
  { id: "report-threats", title: "Threats" },
  { id: "report-paths", title: "Attack paths" },
  { id: "report-mitigations", title: "Mitigations" },
  { id: "report-risk", title: "Risk" },
  { id: "report-requirements", title: "Requirements" },
] as const;

// What kind of example a model is, in the words spec/vectors/README.md uses for
// each family. A proposal model (`pv-*`) is drafted by AI from the published
// write-up of a real automotive attack and names the real product; the others
// are illustrative models written to exercise the object model.
const EXAMPLE_KIND_NOTICES: Readonly<Record<string, string>> = {
  proposal: "This model was drafted by AI from the published write-up of a real automotive attack, "
    + "to exercise tmodel's object model. It is not a verified security assessment of the product it names.",
};
const DEFAULT_KIND_NOTICE = "This is an illustrative threat model written for the tmodel project to exercise "
  + "its object model. It is not a security assessment of a real product.";

/** The example-data banner for one model, without the leading "Example data." */
export function exampleNotice(report: Pick<ModelReport, "model" | "reviewers">): string {
  const kind = EXAMPLE_KIND_NOTICES[report.model.kind] ?? DEFAULT_KIND_NOTICE;
  // Read from the model's recorded Reviews, never assumed from its kind.
  const review = report.reviewers.length === 0
    ? "No human review is recorded in it, so every threat and attack path in it is a hypothesis."
    : "AI-proposed threats and paths are hypotheses until a human reviewer accepts them.";
  return `${kind} ${review}`;
}

/** The banner for a list of example models of every kind (the Pages index). */
export const MODEL_LIST_NOTICE = "These models were written to exercise tmodel's object model; none of them is a "
  + "security assessment. The proposal examples were drafted by AI from published write-ups of real automotive "
  + "attacks and name the real products. AI-proposed threats and paths are hypotheses until a human reviewer "
  + "accepts them.";

export function renderModelReport(report: ModelReport, options: ReportRenderOptions = {}): string {
  // One anchor per path, unique within the report even when two ids slug alike.
  const anchors = uniqueSlugs(report.attackPaths.map((row) => row.id));
  const sections: SafeHtml[] = [
    section(0, componentsSection(report)),
    section(1, damageSection(report)),
    section(2, threatsSection(report)),
    section(3, pathsSection(report, options, anchors)),
    section(4, mitigationsSection(report)),
    section(5, riskSection(report)),
    section(6, requirementsSection(report)),
  ];
  return html`<article class="model-report" aria-labelledby="report-title">
${header(report, options)}
${sections}
</article>`.value;
}

// ── header ──────────────────────────────────────────────────────────────────

function header(report: ModelReport, options: ReportRenderOptions): SafeHtml {
  const { model, threatSummary } = report;
  const chips = threatSummary.byStatus.map((entry) => html`<li class="summary-chip rs-${entry.kind}"><strong>${entry.count}</strong> ${entry.label}</li>`);
  const reviewers = report.reviewers.length > 0
    ? html`Human reviews recorded by ${report.reviewers.join(", ")}.`
    : html`No human review is recorded in this model.`;
  const contents = options.contents
    ? html`<nav class="report-contents" aria-label="Report sections"><ol>${REPORT_SECTIONS.map((entry) => html`<li><a href="#${entry.id}">${entry.title}</a></li>`)}</ol></nav>`
    : "";
  return html`<header class="report-header">
  <p class="eyebrow">Example threat model · ${model.kindLabel}</p>
  <h2 id="report-title">${model.title}</h2>
  ${scope(model.description)}
  <p class="example-banner" role="note"><strong>Example data.</strong> ${exampleNotice(report)}</p>
  ${attackPathWarning(report)}
  <div class="threat-summary" aria-label="Threats by review status">
    <p class="summary-total"><strong>${plural(threatSummary.total, "threat")}</strong>${threatSummary.aiProposed > 0 ? html`, ${threatSummary.aiProposed} of them AI-proposed` : ""}</p>
    ${chips.length > 0 ? html`<ul class="summary-chips">${chips}</ul>` : ""}
    <p class="summary-reviewers">${reviewers}</p>
  </div>
  ${contents}
</header>`;
}

/** The product description as reader text; a modelling note stays under Details (readableText). */
function scope(text: ReportText): SafeHtml {
  // A model with several products has one line per product.
  const shown = text.summary
    ? join(text.summary.split("\n").map((line) => html`<p class="report-scope">${line}</p>`))
    : text.full
      ? html`<p class="report-scope missing">The product description is a modelling note; see Details.</p>`
      : html`<p class="report-scope missing">No product description is recorded.</p>`;
  const full = text.full && text.trimmed
    ? html`<details class="row-details report-scope-details"><summary>Details</summary><dl><div><dt>Full description</dt><dd>${text.full}</dd></div></dl></details>`
    : "";
  return html`${shown}${full}`;
}

/** Says which attack paths the engine could not compute, so the report never looks complete when it is not. */
function attackPathWarning(report: ModelReport): SafeHtml | string {
  if (report.attackPathProblems.length === 0) return "";
  const items = report.attackPathProblems.map((problem) => problem.threat
    ? html`<li><strong>${problem.threat.label}</strong>: ${problem.message}</li>`
    : html`<li><strong>Every threat</strong> (the engine could not list them): ${problem.message}</li>`);
  return html`<div class="report-warning" role="note"><p><strong>Incomplete.</strong> The engine could not compute some attack paths. The paths below still follow the model's own steps and review records, but the engine's computed ways through them are missing for:</p><ul>${items}</ul></div>`;
}

function section(index: number, body: SafeHtml): SafeHtml {
  const entry = REPORT_SECTIONS[index];
  return html`<section class="report-section" id="${entry.id}" aria-labelledby="${entry.id}-title">
<h3 id="${entry.id}-title"><span class="section-number">${index + 1}</span> ${entry.title}</h3>
${body}
</section>`;
}

// ── sections ────────────────────────────────────────────────────────────────

function componentsSection(report: ModelReport): SafeHtml {
  const assets = report.assets.length > 0
    ? table("Assets: what is worth protecting", ["Asset", "Security properties", "Handled by", "Description"], report.assets.map(assetRow))
    : html`<p class="empty-note">No assets are recorded in this model. The components below are the parts of the system.</p>`;
  const components = table(
    "Products and components",
    ["Name", "Kind", "Structure", "Description"],
    report.components.map(componentRow),
    "No products or components are recorded.",
  );
  return html`${assets}${components}`;
}

function assetRow(row: AssetRow): SafeHtml {
  return html`<tr>
<th scope="row">${row.name}</th>
<td>${list(row.securityProperties)}</td>
<td>${refs(row.processedBy)}</td>
<td>${description(row.description)}${detailsToggle(row.details, row.description)}</td>
</tr>`;
}

function componentRow(row: ComponentRow): SafeHtml {
  const structure = [
    row.partOf.length > 0 ? html`<div>Part of ${refs(row.partOf)}</div>` : "",
    row.contains.length > 0 ? html`<div>Contains ${refs(row.contains)}</div>` : "",
    row.uses.length > 0 ? html`<div>Uses ${refs(row.uses)}</div>` : "",
  ].filter(Boolean);
  return html`<tr>
<th scope="row">${row.name}</th>
<td>${row.kind}</td>
<td>${structure.length > 0 ? structure : missing("No structure recorded")}</td>
<td>${description(row.description)}${detailsToggle(row.details, row.description)}</td>
</tr>`;
}

function damageSection(report: ModelReport): SafeHtml {
  return table(
    "Damage scenarios: what could go wrong for the stakeholder",
    ["Damage scenario", "Assets damaged", "Threats leading to it", "Impact", "Description"],
    report.damageScenarios.map(damageRow),
    "No damage scenarios are recorded.",
  );
}

function damageRow(row: DamageRow): SafeHtml {
  const compromised = row.compromisedProperties.length > 0
    ? html`<div class="cell-note">Compromised: ${row.compromisedProperties.join(", ")}</div>`
    : "";
  const impactSource = row.impactSource === "risk assessment"
    ? html`<div class="cell-note">As rated in the risk assessment</div>`
    : "";
  return html`<tr>
<th scope="row">${row.name}</th>
<td>${row.assets.length > 0 ? refs(row.assets) : missing("Not recorded")}${compromised}</td>
<td>${refs(row.threats)}</td>
<td>${impact(row.impact, "Not rated")}${impactSource}</td>
<td>${description(row.description)}${detailsToggle(row.details, row.description)}</td>
</tr>`;
}

function threatsSection(report: ModelReport): SafeHtml {
  return table(
    "Threats and their review status",
    ["Threat", "Source", "Review status", "Damage", "Attack paths", "Mitigations"],
    report.threats.map(threatRow),
    "No threats are recorded.",
  );
}

function threatRow(row: ThreatRow): SafeHtml {
  const violated = row.violatedProperty
    ? html`<div class="cell-note">Violates: ${row.violatedProperty}</div>`
    : "";
  return html`<tr class="${rowClass(row.status)}">
<th scope="row">${row.name}${violated}${row.description.summary ? html`<div class="cell-note">${row.description.summary}</div>` : ""}</th>
<td>${row.source.kind === "unrecorded" ? missing("Not recorded") : row.source.label}</td>
<td>${statusBlock(row.status, row.source.kind === "ai")}</td>
<td>${refs(row.damages)}</td>
<td>${refs(row.paths)}</td>
<td>${row.mitigations.length > 0 ? refs(row.mitigations) : missing("None recorded")}${detailsToggle(row.details, row.description, row.status)}</td>
</tr>`;
}

function pathsSection(
  report: ModelReport,
  options: ReportRenderOptions,
  anchors: ReadonlyMap<string, string>,
): SafeHtml {
  if (report.attackPaths.length === 0) return html`<p class="empty-note">No attack paths are recorded.</p>`;
  // The section's table (#208), then each path in detail: its story and diagram.
  const summary = table(
    "Attack paths: how each threat could be carried out",
    ["Attack path", "Threat", "Steps, in order", "Feasibility", "Review status"],
    report.attackPaths.map((row) => pathTableRow(row, anchors.get(row.id) ?? slug(row.id))),
  );
  return html`${summary}
<p class="section-help">Each path in detail, below: its steps in order, and where two branches join, whether the step needs all of them (AND) or any one (OR).</p>
${report.attackPaths.map((row) => pathCard(row, options, anchors.get(row.id) ?? slug(row.id)))}`;
}

/** One row of the attack-path table; the path's name links to its detailed card below. */
function pathTableRow(row: PathRow, anchor: string): SafeHtml {
  const steps = row.story.steps.length > 0
    ? html`<ol class="table-steps">${row.story.steps.map((step) => html`<li value="${step.number}">${step.name}</li>`)}</ol>`
    : missing("No steps recorded");
  return html`<tr class="${rowClass(row.status)}">
<th scope="row"><a class="path-link" href="#path-${anchor}">${row.name}</a></th>
<td>${row.threat ? row.threat.label : missing("No threat recorded")}</td>
<td>${steps}</td>
<td>${row.feasibility ?? missing("Not rated")}</td>
<td>${statusBlock(row.status, row.source.kind === "ai")}</td>
</tr>`;
}

function pathCard(row: PathRow, options: ReportRenderOptions, anchor: string): SafeHtml {
  const diagram = layoutPathDiagram(row.story);
  const open = options.interactive
    ? html`<button type="button" class="open-path-button" data-open-path="${row.id}">Open in path view</button>`
    : "";
  return html`<article class="path-card ${rowClass(row.status)}" id="path-${anchor}" aria-labelledby="path-${anchor}-title">
<header class="path-card-header">
  <div>
    <h4 id="path-${anchor}-title">${row.name}</h4>
    ${pathFacts(row)}
  </div>
  <div class="path-card-status">${statusBlock(row.status, row.source.kind === "ai")}${open}</div>
</header>
${pathStoryBody(row)}
<figure class="path-figure">
  <div class="path-figure-scroll">${trusted(pathDiagramSvg(diagram, `Attack path diagram: ${row.name}, ${row.status.label}`, anchor))}</div>
  <figcaption>Steps run left to right. AND/OR marks where branches join; the threat, its damage and its mitigations follow.</figcaption>
</figure>
${detailsToggle(row.details, row.description, row.status)}
</article>`;
}

/**
 * The text story of one path, without the diagram: the app's path view shows
 * it beside its Cytoscape drawing, so both outputs tell a path the same way.
 */
export function renderPathSummary(row: PathRow): string {
  return html`<div class="model-report path-summary">
<h2>${row.name}</h2>
${pathFacts(row)}
<div class="path-summary-status">${statusBlock(row.status, row.source.kind === "ai")}</div>
${pathStoryBody(row, true)}
${detailsToggle(row.details, row.description, row.status)}
</div>`.value;
}

function pathFacts(row: PathRow): SafeHtml {
  const others = row.otherThreats.map((link) => html`<p class="cell-note">Also linked to the threat ${link.target.label} (${link.status.label})</p>`);
  return html`<p class="cell-note">Realizes ${row.threat ? row.threat.label : missing("no recorded threat")} · Feasibility: ${row.feasibility ?? missing("Not rated")}</p>${others}`;
}

/**
 * The ordered steps, AND/OR joins, outcome and mitigations of a path. With
 * `stepButtons` (the app's path view) each step's name is a button that shows
 * the step in the drawing: a native button, so Tab, Enter and Space reach it as
 * well as a click. The static report has nothing to highlight, so its steps
 * stay plain text.
 */
function pathStoryBody(row: PathRow, stepButtons = false): SafeHtml {
  const story = row.story;
  const steps = story.steps.map((step) => {
    const joins = step.gate === "and"
      ? html` <span class="gate gate-and">AND</span> <span class="cell-note">needs all of steps ${step.after.join(" and ")}</span>`
      : step.gate === "or"
        ? html` <span class="gate gate-or">OR</span> <span class="cell-note">needs any one of steps ${step.after.join(" or ")}</span>`
        : step.gate === "unspecified"
          ? html` <span class="gate">?</span> <span class="cell-note">follows steps ${step.after.join(", ")}; the model records no AND/OR gate</span>`
          : step.after.length === 1
            ? html` <span class="cell-note">after step ${step.after[0]}</span>`
            : "";
    const name = stepButtons
      ? html`<button type="button" class="step-name step-button" aria-pressed="false" title="Show step ${step.number} in the drawing">${step.name}</button>`
      : html`<span class="step-name">${step.name}</span>`;
    return html`<li value="${step.number}" data-step="${step.id}">${name}${step.phase ? html` <span class="phase-chip">${step.phase}</span>` : ""}${joins}</li>`;
  });
  const alternatives = story.alternativesMissing
    ? html`<p class="cell-note warning-note">The engine could not compute the ways through this path, so its list of alternatives is missing.</p>`
    : story.alternatives.length > 1
      ? html`<p class="cell-note">The engine finds ${story.alternatives.length} ways through this path: ${join(story.alternatives.map((alternative) => `steps ${alternative.join(" → ")}`), "; ")}.</p>`
      : "";
  const negative = row.status.kind === "rejected" || row.status.kind === "changes_requested";
  const reason = row.status.reason.summary
    ? html` Reviewer’s reason: ${row.status.reason.summary}`
    : row.status.reason.full ? " The reviewer’s reason is under Details." : "";
  return html`${negative ? html`<p class="status-callout rs-${row.status.kind}" role="note"><strong>${row.status.kind === "rejected" ? "Rejected" : "Changes requested"}:</strong> this path is not an accepted part of the model.${reason}</p>` : ""}
<div class="path-story">
  <ol class="path-steps">${steps}</ol>
  ${alternatives}
  <p class="path-outcome">${story.threat ? html`<span>Realizes the threat <strong>${story.threat.label}</strong></span>` : missing("No threat recorded")}${story.damages.length > 0 ? html`<span>, which leads to <strong>${refs(story.damages)}</strong></span>` : ""}.</p>
  <p class="path-outcome">${story.mitigations.length > 0 ? html`Mitigated by ${refs(story.mitigations)}.` : missing("No mitigation is recorded for this threat.")}</p>
  ${story.targets.length > 0 ? html`<p class="path-outcome">Targets ${refs(story.targets)}.</p>` : ""}
</div>`;
}

function mitigationsSection(report: ModelReport): SafeHtml {
  return table(
    "Mitigations: what is done about the threats",
    ["Mitigation", "Against threats", "Status", "Owner", "Lifecycle phases", "Description"],
    report.mitigations.map(mitigationRow),
    "No mitigations are recorded.",
  );
}

function mitigationRow(row: MitigationRow): SafeHtml {
  const stated = row.statedAs.length > 0
    ? html`<div class="cell-note">Stated as the requirement ${refs(row.statedAs)}</div>`
    : "";
  return html`<tr>
<th scope="row">${row.name}</th>
<td>${row.threats.length > 0 ? refs(row.threats) : missing("No threat of its own")}</td>
<td>${row.status ?? missing("Not recorded")}</td>
<td>${row.owner ? row.owner.label : missing("Not recorded")}</td>
<td>${row.phases.length > 0 ? row.phases.join(", ") : missing("Not recorded")}</td>
<td>${description(row.description)}${stated}${detailsToggle(row.details, row.description)}</td>
</tr>`;
}

function riskSection(report: ModelReport): SafeHtml {
  return table(
    "Risk: how likely and how bad, per threat",
    ["Threat", "Damage", "Feasibility", "Impact", "Risk", "Mitigation status"],
    report.risks.map(riskRow),
    "No threats, so no risk to assess.",
  );
}

function riskRow(row: RiskRow): SafeHtml {
  if (!row.assessed) {
    return html`<tr class="row-not-assessed">
<th scope="row">${row.threat?.label ?? row.name}</th>
<td>${row.damage ? row.damage.label : missing("Not recorded")}</td>
<td colspan="4">${missing("Not assessed: the model records no risk score for this threat.")}</td>
</tr>`;
  }
  const stakeholder = row.stakeholder
    ? html`<div class="cell-note">For ${row.stakeholder.label}</div>`
    : "";
  return html`<tr>
<th scope="row">${row.threat ? row.threat.label : missing("No threat recorded")}<div class="cell-note">${row.name}</div></th>
<td>${row.damage ? row.damage.label : missing("Not recorded")}${stakeholder}</td>
<td>${row.feasibility ?? missing("Not rated")}</td>
<td>${impact(row.impact, "Not rated")}</td>
<td>${row.risk ?? missing("Not recorded")}</td>
<td>${row.mitigationStatus ?? missing("Not recorded")}${detailsToggle(row.details, row.description)}</td>
</tr>`;
}

function requirementsSection(report: ModelReport): SafeHtml {
  if (report.requirements.length === 0) {
    return html`<p class="empty-note">No requirements are recorded in this model.</p>`;
  }
  return table(
    "Requirements that apply",
    ["Requirement", "Text", "Kind", "Addresses", "Satisfied by"],
    report.requirements.map(requirementRow),
  );
}

function requirementRow(row: RequirementRow): SafeHtml {
  const proposed = row.proposedLinks.map((link) => html`<div class="cell-note">${link.status.label}: also addresses ${link.target.label}</div>`);
  const origin = row.origin ? html`<div class="cell-note">${row.origin}${row.clause ? html`, ${row.clause}` : ""}</div>` : "";
  const derived = row.derivedFrom.length > 0
    ? html`<div class="cell-note">Derived from ${refs(row.derivedFrom)}</div>`
    : "";
  return html`<tr>
<th scope="row">${row.name}${derived}</th>
<td>${row.text ?? missing("No text recorded")}${origin}</td>
<td>${row.kind ?? missing("Not recorded")}${row.normativity ? html`<div class="cell-note">${row.normativity}</div>` : ""}</td>
<td>${row.addresses.length > 0 ? refs(row.addresses) : missing("None recorded")}${proposed}</td>
<td>${row.satisfiedBy.length > 0 ? refs(row.satisfiedBy) : missing("None recorded")}${detailsToggle(row.details, row.description)}</td>
</tr>`;
}

// ── pieces ──────────────────────────────────────────────────────────────────

function table(caption: string, headers: readonly string[], rows: readonly SafeHtml[], empty?: string): SafeHtml {
  if (rows.length === 0) return html`<p class="empty-note">${empty ?? "Nothing recorded."}</p>`;
  return html`<div class="report-table-scroll" role="region" aria-label="${caption}" tabindex="0">
<table class="report-table">
<caption>${caption}</caption>
<thead><tr>${headers.map((name) => html`<th scope="col">${name}</th>`)}</tr></thead>
<tbody>${rows}</tbody>
</table>
</div>`;
}

function statusBlock(status: ReportStatus, aiSource: boolean): SafeHtml {
  const reviewers = status.reviewers.length > 0
    ? html`<div class="cell-note">Reviewer: ${join(status.reviewers.map((handle) => html`<span class="handle">${handle}</span>`), ", ")}</div>`
    : status.kind === "accepted" || status.kind === "rejected" || status.kind === "changes_requested"
      ? html`<div class="cell-note">Reviewer not recorded</div>`
      : "";
  const hypothesis = aiSource && status.kind === "rejected"
    ? html`<div class="cell-note">Rejected AI hypothesis</div>`
    : "";
  return html`<span class="status-badge rs-${status.kind}">${status.label}</span>${reviewers}${hypothesis}`;
}

function rowClass(status: ReportStatus): string {
  return `row-status-${status.kind}`;
}

function description(text: ReportText): SafeHtml | string {
  if (text.summary) return text.summary;
  if (text.full) return missing("Modelling note only; see details");
  return missing("No description");
}

function detailsToggle(details: readonly ReportDetail[], text: ReportText, status?: ReportStatus): SafeHtml {
  const rows: ReportDetail[] = [...details];
  if (text.full && text.trimmed) rows.splice(2, 0, { label: "Full description", value: text.full });
  if (status) {
    if (status.assertionStatus) rows.push({ label: "Assertion status", value: status.assertionStatus });
    if (status.reviewStatus) rows.push({ label: "Review status", value: status.reviewStatus });
    if (status.assertionIds.length > 0) rows.push({ label: "Assertions", value: status.assertionIds.join(", ") });
    if (status.reviewIds.length > 0) rows.push({ label: "Reviews", value: status.reviewIds.join(", ") });
    if (status.justification) rows.push({ label: "Review justification", value: status.justification });
  }
  return html`<details class="row-details"><summary>Details</summary><dl>${rows.map((row) => html`<div><dt>${row.label}</dt><dd>${row.value}</dd></div>`)}</dl></details>`;
}

function refs(values: readonly ReportRef[]): SafeHtml {
  if (values.length === 0) return missing("None");
  return join(values.map((ref) => ref.missing ? missing("an object the model does not define") : html`<span class="ref">${ref.label}</span>`), ", ");
}

function list(values: readonly string[]): SafeHtml {
  return values.length > 0 ? html`${values.join(", ")}` : missing("Not recorded");
}

function impact(values: readonly ImpactRating[], empty: string): SafeHtml {
  if (values.length === 0) return missing(empty);
  return html`<ul class="impact-list">${values.map((value) => html`<li><span>${value.category}</span> ${value.rating}</li>`)}</ul>`;
}

function missing(text: string): SafeHtml {
  return html`<span class="missing">${text}</span>`;
}

function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}

/** An id made safe for an HTML id attribute. */
export function slug(id: string): string {
  return id.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

/** A slug per id, with "-2", "-3" … added where two ids slug alike, so no HTML id repeats. */
export function uniqueSlugs(ids: readonly string[]): Map<string, string> {
  const used = new Set<string>();
  const out = new Map<string, string>();
  for (const id of ids) {
    if (out.has(id)) continue;
    const base = slug(id) || "item";
    let candidate = base;
    for (let suffix = 2; used.has(candidate); suffix += 1) candidate = `${base}-${suffix}`;
    used.add(candidate);
    out.set(id, candidate);
  }
  return out;
}

// ── default-view check ──────────────────────────────────────────────────────

/**
 * The text a reader sees with every Details toggle closed: page styles, closed
 * details and tags removed, entities decoded. Tooltips (`<title>`) stay in.
 */
export function defaultViewText(markup: string): string {
  return markup
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<details[\s\S]*?<\/details>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

// What #208 keeps out of the default view: ids (CURIEs, CPE and purl strings
// share the `prefix:value` shape), schema field names and schema class names.
const DEFAULT_VIEW_LEAKS: readonly { kind: string; pattern: RegExp }[] = [
  { kind: "id (CURIE, CPE or purl)", pattern: /\b(?!https?:)[a-z][a-z0-9-]*:[a-z0-9][\w.@/-]*/gi },
  { kind: "schema field name", pattern: /\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g },
  {
    kind: "schema class name",
    pattern: /\b(?:ThreatInstance|AttackPath|AttackStep|DamageScenario|RiskScore|ProductInstance|LifecyclePhase|GovernedView|TrustBoundary|DataFlow|AttackPattern)\b/g,
  },
];

/** Every technical identifier visible with the Details toggles closed, as "kind: text"; empty when clean. */
export function defaultViewLeaks(markup: string): string[] {
  const visible = defaultViewText(markup);
  const found = new Set<string>();
  for (const { kind, pattern } of DEFAULT_VIEW_LEAKS) {
    for (const match of visible.match(pattern) ?? []) found.add(`${kind}: ${match}`);
  }
  return [...found];
}
