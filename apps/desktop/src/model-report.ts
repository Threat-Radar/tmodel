// The model report (#208): a TARA-ordered, human-readable view of one example
// model, built from the engine's `/graph` and `/attack-paths` responses.
//
// Shared by the app and the static Pages renderer, so both always show the same
// thing. It only arranges what the model records: a missing value stays missing
// ("Not recorded", "Not assessed"), and review state comes only from recorded
// Assertions and Reviews, never from a threat's own claim about itself
// (CLAUDE.md: AI output is a hypothesis until a human accepts it).
//
// Node runs this file directly (type stripping), so value imports carry `.ts`
// and only `import type` is used for types.

import type { AttackPathResponse, GraphProperties, GraphPropertyValue } from "./graph-types";
import type { AttackPathFailure, EngineGraphEdge, EngineGraphNode, ModelReportInput } from "./model-types";
import { reviewStatePresentation } from "./review-status.ts";

/** Records about the model rather than the system; never drawn as nodes in the default views. */
export const BOOKKEEPING_TYPES: ReadonlySet<string> = new Set([
  "Assertion",
  "Review",
  "Party",
  "LifecyclePhase",
  "View",
]);

export type ReportStatusKind =
  | "accepted"
  | "changes_requested"
  | "rejected"
  | "proposed"
  | "not_reviewed"
  | "unknown"
  | "mixed";

export interface ReportStatus {
  kind: ReportStatusKind;
  /** Badge text, e.g. "Accepted", "Rejected", "AI-proposed, not reviewed". */
  label: string;
  /** True only for an accepted record: the one state shown as reviewed. */
  reviewed: boolean;
  reviewers: string[];
  /** The reviewer's recorded reason, in full (details only). */
  justification: string | null;
  /** The same reason as reader text, for the default view (readableText). */
  reason: ReportText;
  /** The model's own values, kept for the details toggle. */
  assertionStatus: string | null;
  reviewStatus: string | null;
  assertionIds: string[];
  reviewIds: string[];
}

export interface ReportText {
  /** Readable sentences for the default view; null when every sentence is a modelling note. */
  summary: string | null;
  /** The model's full text, unchanged except for whitespace; shown under details. */
  full: string | null;
  /** True when the summary leaves something out of the full text. */
  trimmed: boolean;
}

export interface ReportRef {
  id: string;
  label: string;
  /** The model points at an id it does not define. */
  missing?: boolean;
}

export interface ReportDetail {
  label: string;
  value: string;
}

interface ReportItem {
  id: string;
  name: string;
  description: ReportText;
  details: ReportDetail[];
}

export interface AssetRow extends ReportItem {
  securityProperties: string[];
  processedBy: ReportRef[];
}

export interface ComponentRow extends ReportItem {
  kind: string;
  partOf: ReportRef[];
  contains: ReportRef[];
  uses: ReportRef[];
}

export interface ImpactRating {
  category: string;
  rating: string;
}

export interface DamageRow extends ReportItem {
  assets: ReportRef[];
  compromisedProperties: string[];
  threats: ReportRef[];
  impact: ImpactRating[];
  impactSource: "damage scenario" | "risk assessment" | null;
}

export interface ThreatSource {
  kind: "ai" | "human" | "unrecorded";
  label: string;
}

export interface ThreatRow extends ReportItem {
  source: ThreatSource;
  status: ReportStatus;
  violatedProperty: string | null;
  damages: ReportRef[];
  paths: ReportRef[];
  mitigations: ReportRef[];
}

export interface VulnerabilityRow extends ReportItem {
  catalogRef: string | null;
  affects: ReportRef[];
  weaknesses: ReportRef[];
  propagatesTo: ReportRef[];
}

export interface WeaknessRow extends ReportItem {
  catalogRef: string | null;
  vulnerabilities: ReportRef[];
  attackPatterns: ReportRef[];
}

export interface AttackPatternRow extends ReportItem {
  catalogRef: string | null;
  weaknesses: ReportRef[];
}

export type StepGate = "and" | "or" | "unspecified";

export interface StoryStep {
  id: string;
  number: number;
  name: string;
  description: ReportText;
  phase: string | null;
  /** How this step combines the path steps before it; null with fewer than two. */
  gate: StepGate | null;
  /** Numbers of the path steps that directly precede this one. */
  after: number[];
  /** Column for drawing: 0 for a starting step, else one more than its latest predecessor. */
  stage: number;
}

export interface PathStory {
  pathId: string;
  pathName: string;
  steps: StoryStep[];
  /** Engine-computed alternatives (`/attack-paths`), as step numbers in order. */
  alternatives: number[][];
  threat: ReportRef | null;
  damages: ReportRef[];
  mitigations: ReportRef[];
  targets: ReportRef[];
  /** The threat's own provenance state, kept apart from the path assertion's review. */
  threatStatus: ReportStatus;
  status: ReportStatus;
  /** The engine failed, or a computed step is unavailable, so `alternatives` may be incomplete. */
  alternativesMissing: boolean;
}

export interface PathRow extends ReportItem {
  threat: ReportRef | null;
  /**
   * Other threats this path is linked to, each with its own review state. The
   * schema gives a path one `realizes_threat`; an Assertion can name another.
   */
  otherThreats: ProposedLink[];
  /** Where the realised threat came from; an AI-proposed path is a hypothesis. */
  source: ThreatSource;
  feasibility: string | null;
  status: ReportStatus;
  story: PathStory;
}

export interface MitigationRow extends ReportItem {
  threats: ReportRef[];
  status: string | null;
  owner: ReportRef | null;
  phases: string[];
  statedAs: ReportRef[];
}

export interface RiskRow {
  id: string | null;
  name: string;
  assessed: boolean;
  threat: ReportRef | null;
  damage: ReportRef | null;
  stakeholder: ReportRef | null;
  feasibility: string | null;
  impact: ImpactRating[];
  risk: string | null;
  mitigationStatus: string | null;
  description: ReportText;
  details: ReportDetail[];
}

export interface ProposedLink {
  target: ReportRef;
  status: ReportStatus;
}

export interface RequirementRow extends ReportItem {
  text: string | null;
  kind: string | null;
  normativity: string | null;
  origin: string | null;
  clause: string | null;
  addresses: ReportRef[];
  satisfiedBy: ReportRef[];
  derivedFrom: ReportRef[];
  proposedLinks: ProposedLink[];
}

export interface StatusCount {
  kind: ReportStatusKind;
  label: string;
  count: number;
}

/** A threat whose attack paths the engine could not compute when the report was built. */
export interface AttackPathProblem {
  /** Null when the engine could not even list the threats. */
  threat: ReportRef | null;
  message: string;
}

export interface ModelReport {
  model: {
    id: string;
    file: string;
    title: string;
    description: ReportText;
    kindLabel: string;
    kind: string;
  };
  threatSummary: {
    total: number;
    aiProposed: number;
    byStatus: StatusCount[];
  };
  reviewers: string[];
  assets: AssetRow[];
  components: ComponentRow[];
  damageScenarios: DamageRow[];
  threats: ThreatRow[];
  vulnerabilities: VulnerabilityRow[];
  weaknesses: WeaknessRow[];
  attackPatterns: AttackPatternRow[];
  attackPaths: PathRow[];
  mitigations: MitigationRow[];
  risks: RiskRow[];
  requirements: RequirementRow[];
  /** Empty unless some `/attack-paths` answers failed (app only). */
  attackPathProblems: AttackPathProblem[];
}

// Order of the status counts in the report header.
const SUMMARY_ORDER: readonly ReportStatusKind[] = [
  "accepted",
  "changes_requested",
  "rejected",
  "proposed",
  "not_reviewed",
  "unknown",
  "mixed",
];

const COUNT_LABELS: Readonly<Record<ReportStatusKind, string>> = {
  accepted: "accepted",
  changes_requested: "changes requested",
  rejected: "rejected",
  proposed: "proposed, not reviewed",
  not_reviewed: "not reviewed",
  unknown: "unrecognised status",
  mixed: "mixed review states",
};

const IMPACT_ORDER = ["safety", "financial", "operational", "privacy"];

const OBJECT_TYPE_LABELS: Readonly<Record<string, string>> = {
  Product: "Product",
  ProductInstance: "Product instance",
  Component: "Component",
  ThreatInstance: "Threat",
  AttackPath: "Attack path",
  AttackStep: "Attack step",
  Party: "Party",
  LifecyclePhase: "Lifecycle phase",
  DamageScenario: "Damage scenario",
  RiskScore: "Risk score",
  Mitigation: "Mitigation",
  Requirement: "Requirement",
  Asset: "Asset",
  Vulnerability: "Vulnerability",
  Weakness: "Weakness",
  AttackPattern: "Attack pattern",
};

/** Builds the report for one model. Pure: the same input always gives the same report. */
export function buildModelReport(input: ModelReportInput): ModelReport {
  const index = new GraphIndex(input.graph.nodes, input.graph.edges);
  const threats = index.ofType("ThreatInstance").map((node) => threatRow(index, node));
  const threatById = new Map(threats.map((threat) => [threat.id, threat]));
  const failures: readonly AttackPathFailure[] = input.attackPathFailures ?? [];
  const failedGoals = new Set(failures.map((failure) => failure.goal));
  const attackPaths = index.ofType("AttackPath").map((node) => pathRow(
    index,
    node,
    threatById,
    input.attackPaths,
    failedGoals,
  ));
  const riskScores = index.ofType("RiskScore").map((node) => riskRow(index, node));
  const assessed = new Set(riskScores.map((risk) => risk.threat?.id).filter(isString));
  const notAssessed: RiskRow[] = threats
    .filter((threat) => !assessed.has(threat.id))
    .map((threat) => ({
      id: null,
      name: `Not assessed: ${threat.name}`,
      assessed: false,
      threat: { id: threat.id, label: threat.name },
      damage: threat.damages[0] ?? null,
      stakeholder: null,
      feasibility: null,
      impact: [],
      risk: null,
      mitigationStatus: null,
      description: emptyText(),
      details: [],
    }));
  const reviewers = unique(index.ofType("Review").flatMap((review) => (
    index.linked(review.id, "reviewer").map(displayName)
  )));

  return {
    model: {
      id: input.model.id,
      file: input.model.file,
      title: input.model.title,
      description: readableDescription(input.model.description),
      kindLabel: input.model.kind_label,
      kind: input.model.kind,
    },
    threatSummary: {
      total: threats.length,
      aiProposed: threats.filter((threat) => threat.source.kind === "ai").length,
      byStatus: SUMMARY_ORDER
        .map((kind) => ({
          kind,
          label: COUNT_LABELS[kind],
          count: threats.filter((threat) => threat.status.kind === kind).length,
        }))
        .filter((entry) => entry.count > 0),
    },
    reviewers,
    assets: index.ofType("Asset").map((node) => assetRow(index, node)),
    components: [
      ...index.ofType("Product"),
      ...index.ofType("ProductInstance"),
      ...index.ofType("Component"),
    ].map((node) => componentRow(index, node)),
    damageScenarios: index.ofType("DamageScenario").map((node) => damageRow(index, node, riskScores)),
    threats,
    vulnerabilities: index.ofType("Vulnerability").map((node) => vulnerabilityRow(index, node)),
    weaknesses: index.ofType("Weakness").map((node) => weaknessRow(index, node)),
    attackPatterns: index.ofType("AttackPattern").map((node) => attackPatternRow(index, node)),
    attackPaths,
    mitigations: index.ofType("Mitigation").map((node) => mitigationRow(index, node)),
    risks: [...riskScores, ...notAssessed],
    requirements: index.ofType("Requirement").map((node) => requirementRow(index, node, threatById)),
    attackPathProblems: failures.map((failure) => ({
      threat: failure.goal ? index.ref(failure.goal) : null,
      message: failure.message,
    })),
  };
}

// ── rows ────────────────────────────────────────────────────────────────────

function assetRow(index: GraphIndex, node: EngineGraphNode): AssetRow {
  return {
    ...item(node, ["security_properties", "processed_by"]),
    securityProperties: strings(node.properties.security_properties).map(humanize),
    processedBy: index.refs(node.id, "processed_by"),
  };
}

function componentRow(index: GraphIndex, node: EngineGraphNode): ComponentRow {
  return {
    ...item(node, []),
    kind: OBJECT_TYPE_LABELS[node.domain_type] ?? humanize(node.domain_type),
    partOf: index.sources(node.id, "composed_of").map((source) => index.ref(source.id)),
    contains: index.refs(node.id, "composed_of"),
    uses: index.refs(node.id, "uses_component"),
  };
}

function damageRow(index: GraphIndex, node: EngineGraphNode, risks: readonly RiskRow[]): DamageRow {
  const own = impactRatings(node.properties.impact);
  const fromRisk = risks.filter((risk) => risk.damage?.id === node.id && risk.impact.length > 0);
  const impact = own.length > 0 ? own : fromRisk.length === 1 ? fromRisk[0].impact : [];
  return {
    ...item(node, ["impact", "damages_asset", "compromised_property"]),
    assets: index.refs(node.id, "damages_asset"),
    compromisedProperties: strings(node.properties.compromised_property).map(humanize),
    threats: uniqueRefs(index.incoming(node.id)
      .filter((edge) => index.node(edge.source)?.domain_type === "ThreatInstance")
      .map((edge) => index.ref(edge.source))),
    impact,
    impactSource: own.length > 0 ? "damage scenario" : impact.length > 0 ? "risk assessment" : null,
  };
}

function threatRow(index: GraphIndex, node: EngineGraphNode): ThreatRow {
  const source = threatSource(text(node.properties.source_method));
  const paths = index.sources(node.id, "realizes_threat")
    .filter((path) => path.domain_type === "AttackPath");
  const statuses = paths.map((path) => linkStatus(index, path.id, "realizes_threat", node.id, source));
  return {
    ...item(node, ["source_method", "violates_property", "method_facet"]),
    source,
    status: combinedStatus(statuses, source),
    violatedProperty: text(node.properties.violates_property),
    damages: index.refs(node.id, "realizes_damage"),
    paths: paths.map((path) => index.ref(path.id)),
    mitigations: index.sources(node.id, "mitigates").map((mitigation) => index.ref(mitigation.id)),
  };
}

function vulnerabilityRow(index: GraphIndex, node: EngineGraphNode): VulnerabilityRow {
  return {
    ...item(node, ["catalog_ref"]),
    catalogRef: text(node.properties.catalog_ref),
    affects: index.refs(node.id, "affects"),
    weaknesses: index.refs(node.id, "instance_of"),
    propagatesTo: index.refs(node.id, "propagates_to"),
  };
}

function weaknessRow(index: GraphIndex, node: EngineGraphNode): WeaknessRow {
  return {
    ...item(node, ["catalog_ref"]),
    catalogRef: text(node.properties.catalog_ref),
    vulnerabilities: index.sources(node.id, "instance_of").map((source) => index.ref(source.id)),
    attackPatterns: index.refs(node.id, "exploited_by"),
  };
}

function attackPatternRow(index: GraphIndex, node: EngineGraphNode): AttackPatternRow {
  return {
    ...item(node, ["catalog_ref"]),
    catalogRef: text(node.properties.catalog_ref),
    weaknesses: index.sources(node.id, "exploited_by").map((source) => index.ref(source.id)),
  };
}

function pathRow(
  index: GraphIndex,
  node: EngineGraphNode,
  threats: ReadonlyMap<string, ThreatRow>,
  responses: readonly AttackPathResponse[],
  failedGoals: ReadonlySet<string | null>,
): PathRow {
  // The authored `realizes_threat` first; any other linked threat is listed with its own review state.
  const linkedThreats = index.linked(node.id, "realizes_threat");
  const threatNode = index.linked(node.id, "realizes_threat", { authoredOnly: true })[0] ?? linkedThreats[0];
  const threat = threatNode ? threats.get(threatNode.id) : undefined;
  const source = threat?.source ?? UNRECORDED_SOURCE;
  const status = threatNode
    ? linkStatus(index, node.id, "realizes_threat", threatNode.id, source)
    : statusFrom(undefined, source, index);
  const alternativesMissing = failedGoals.has(null)
    || linkedThreats.some((linked) => failedGoals.has(linked.id));
  const story = pathStory(index, node, threat, status, responses, alternativesMissing);
  return {
    ...item(node, ["attack_feasibility"]),
    threat: threatNode ? index.ref(threatNode.id) : null,
    otherThreats: linkedThreats
      .filter((linked) => linked.id !== threatNode?.id)
      .map((linked) => ({
        target: index.ref(linked.id),
        status: linkStatus(
          index,
          node.id,
          "realizes_threat",
          linked.id,
          threats.get(linked.id)?.source ?? UNRECORDED_SOURCE,
        ),
      })),
    source,
    feasibility: optionalHumanized(node.properties.attack_feasibility),
    status,
    story,
  };
}

function pathStory(
  index: GraphIndex,
  path: EngineGraphNode,
  threat: ThreatRow | undefined,
  status: ReportStatus,
  responses: readonly AttackPathResponse[],
  alternativesMissing: boolean,
): PathStory {
  const authored = index.linked(path.id, "steps");
  const computed = responses
    .flatMap((response) => response.paths)
    .filter((candidate) => candidate.authored_path === path.id);
  const computedStepIds = unique(computed.flatMap((candidate) => candidate.steps));
  const computedSteps = computedStepIds
    .map((id) => index.node(id))
    .filter((node): node is EngineGraphNode => node?.domain_type === "AttackStep");
  // A computed route can enter this authored path through a prerequisite step
  // owned by another path. Keep that step in the story: it is part of the
  // engine's route even though it is not repeated in this path's `steps` slot.
  const storySteps = uniqueNodes([...authored, ...computedSteps]);
  const inPath = new Set(storySteps.map((step) => step.id));
  const storyOrder = new Map(storySteps.map((step, position) => [step.id, position]));
  const predecessors = new Map(storySteps.map((step) => [
    step.id,
    index.sources(step.id, "precedes")
      .filter((before) => inPath.has(before.id))
      .map((before) => before.id),
  ]));

  // Topological order under `precedes`, with authored order followed by first
  // computed appearance as the stable tie-breaker. This matches the engine's
  // `_ordered` rule while retaining prerequisites that another path authored.
  const remaining = new Map(storySteps.map((step) => [step.id, predecessors.get(step.id)?.length ?? 0]));
  const ordered: string[] = [];
  const byStoryOrder = (a: string, b: string) => (storyOrder.get(a) ?? 0) - (storyOrder.get(b) ?? 0);
  const ready = storySteps.filter((step) => remaining.get(step.id) === 0).map((step) => step.id);
  while (ready.length > 0) {
    ready.sort(byStoryOrder);
    const next = ready.shift() as string;
    ordered.push(next);
    for (const after of index.linked(next, "precedes")) {
      if (!remaining.has(after.id)) continue;
      const left = (remaining.get(after.id) ?? 0) - 1;
      remaining.set(after.id, left);
      if (left === 0) ready.push(after.id);
    }
  }
  // A cycle (the engine rejects one) leaves steps unordered; keep them in the
  // stable authored/computed order so the report still names every known step.
  for (const step of storySteps) if (!ordered.includes(step.id)) ordered.push(step.id);

  const number = new Map(ordered.map((id, position) => [id, position + 1]));
  const stage = new Map<string, number>();
  for (const id of ordered) {
    const before = predecessors.get(id) ?? [];
    stage.set(id, before.length === 0 ? 0 : Math.max(...before.map((p) => stage.get(p) ?? 0)) + 1);
  }

  const steps: StoryStep[] = ordered.map((id) => {
    const node = index.node(id) as EngineGraphNode;
    const before = predecessors.get(id) ?? [];
    const gate = text(node.properties.gate);
    return {
      id,
      number: number.get(id) ?? 0,
      name: displayName(node),
      description: readableText(text(node.properties.description)),
      phase: optionalHumanized(node.properties.kill_chain_phase),
      gate: before.length < 2 ? null : gate === "and_gate" ? "and" : gate === "or_gate" ? "or" : "unspecified",
      after: before.map((p) => number.get(p) ?? 0).sort((a, b) => a - b),
      stage: stage.get(id) ?? 0,
    };
  });

  const alternatives = computed
    .map((candidate) => candidate.steps.map((id) => number.get(id)).filter(isNumber));
  const computedStepsIncomplete = computedStepIds.some((id) => !number.has(id));
  const targets = uniqueRefs([
    ...(threat ? index.refs(threat.id, "targets_element") : []),
    ...ordered.flatMap((id) => index.refs(id, "targets_element")),
  ]);

  return {
    pathId: path.id,
    pathName: displayName(path),
    steps,
    alternatives: uniqueLists(alternatives),
    threat: threat ? { id: threat.id, label: threat.name } : null,
    damages: threat?.damages ?? [],
    mitigations: threat?.mitigations ?? [],
    targets,
    threatStatus: threat ? statusFrom(undefined, threat.source, index) : emptyStatus(),
    status,
    alternativesMissing: alternativesMissing || computedStepsIncomplete,
  };
}

function mitigationRow(index: GraphIndex, node: EngineGraphNode): MitigationRow {
  const owner = index.linked(node.id, "implementation_owner")[0];
  return {
    ...item(node, ["mitigation_status", "stated_as"]),
    threats: index.refs(node.id, "mitigates"),
    status: optionalHumanized(node.properties.mitigation_status),
    owner: owner ? index.ref(owner.id) : null,
    phases: index.linked(node.id, "applies_in_phase").map(displayName),
    statedAs: index.refs(node.id, "stated_as"),
  };
}

function riskRow(index: GraphIndex, node: EngineGraphNode): RiskRow {
  const threat = index.linked(node.id, "threat")[0];
  const damage = index.linked(node.id, "damage_scenario")[0];
  const stakeholder = index.linked(node.id, "for_stakeholder")[0];
  return {
    id: node.id,
    name: displayName(node),
    assessed: true,
    threat: threat ? index.ref(threat.id) : null,
    damage: damage ? index.ref(damage.id) : null,
    stakeholder: stakeholder ? index.ref(stakeholder.id) : null,
    feasibility: optionalHumanized(node.properties.feasibility),
    impact: impactRatings(node.properties.impact),
    risk: text(node.properties.risk),
    mitigationStatus: optionalHumanized(node.properties.mitigation_status),
    description: readableText(text(node.properties.description)),
    details: details(node, ["feasibility", "impact", "risk", "mitigation_status"]),
  };
}

function requirementRow(
  index: GraphIndex,
  node: EngineGraphNode,
  threats: ReadonlyMap<string, ThreatRow>,
): RequirementRow {
  const proposedLinks = index.outgoing(node.id)
    .filter((edge) => hasAssertion(edge.properties))
    .map((edge) => {
      const threat = threats.get(edge.target);
      return {
        target: index.ref(edge.target),
        status: statusFrom(edge.properties, threat?.source ?? UNRECORDED_SOURCE, index),
      };
    });
  return {
    ...item(node, [
      "text",
      "requirement_kind",
      "normativity",
      "text_origin",
      "source_locator",
      "addresses",
      "derived_from",
    ]),
    text: text(node.properties.text),
    kind: optionalHumanized(node.properties.requirement_kind),
    normativity: optionalHumanized(node.properties.normativity),
    origin: optionalHumanized(node.properties.text_origin),
    clause: text(node.properties.source_locator),
    // Authored links only; an asserted link with its own review state is listed apart.
    addresses: index.refs(node.id, "addresses", { authoredOnly: true }),
    satisfiedBy: index.refs(node.id, "satisfied_by", { authoredOnly: true }),
    derivedFrom: uniqueRefs([
      ...index.refs(node.id, "derived_from"),
      ...index.refs(node.id, "refines"),
    ]),
    proposedLinks,
  };
}

function item(node: EngineGraphNode, shown: readonly string[]): ReportItem {
  return {
    id: node.id,
    name: displayName(node),
    description: readableText(text(node.properties.description)),
    details: details(node, shown),
  };
}

/**
 * The technical record behind a row, for the details toggle: the model id, the
 * object type and every recorded value that no column already shows.
 */
function details(node: EngineGraphNode, shown: readonly string[]): ReportDetail[] {
  const out: ReportDetail[] = [
    { label: "Model id", value: node.id },
    { label: "Object type", value: node.domain_type },
  ];
  for (const [key, value] of Object.entries(node.properties)) {
    if (key === "description" || shown.includes(key) || value === null) continue;
    out.push({ label: humanize(key), value: displayValue(value) });
  }
  return out;
}

// ── review state ────────────────────────────────────────────────────────────

const UNRECORDED_SOURCE: ThreatSource = { kind: "unrecorded", label: "Not recorded" };

function linkStatus(
  index: GraphIndex,
  source: string,
  relationship: string,
  target: string,
  threatSourceValue: ThreatSource,
): ReportStatus {
  const edge = index.outgoing(source).find((candidate) => (
    candidate.relationship_type === relationship && candidate.target === target
  ));
  return statusFrom(edge?.properties, threatSourceValue, index);
}

function statusFrom(
  properties: GraphProperties | undefined,
  source: ThreatSource,
  index: GraphIndex,
): ReportStatus {
  const assertionStatus = properties ? text(properties.assertion_status) : null;
  const reviewStatus = properties ? text(properties.review_status) : null;
  const assertionIds = properties ? strings(properties.assertion_ids) : [];
  const reviewIds = properties ? strings(properties.review_ids) : [];
  const reviews = reviewIds.map((id) => index.node(id)).filter(isDefined);
  const reviewers = unique(reviews.flatMap((review) => (
    index.linked(review.id, "reviewer").map(displayName)
  )));
  const justification = reviews.map((review) => text(review.properties.justification))
    .filter(isString)
    .map(collapse)
    .join(" ") || null;

  let kind: ReportStatusKind;
  if (assertionStatus === null && reviewStatus === null) kind = "not_reviewed";
  else {
    const presented = reviewStatePresentation(assertionStatus, reviewStatus).kind;
    kind = presented;
  }
  return {
    kind,
    label: statusLabel(kind, source),
    reviewed: kind === "accepted",
    reviewers,
    justification,
    reason: readableText(justification),
    assertionStatus,
    reviewStatus,
    assertionIds,
    reviewIds,
  };
}

function combinedStatus(statuses: readonly ReportStatus[], source: ThreatSource): ReportStatus {
  if (statuses.length === 0) return { ...emptyStatus(), label: statusLabel("not_reviewed", source) };
  const kinds = unique(statuses.map((status) => status.kind));
  const kind: ReportStatusKind = kinds.length === 1 ? kinds[0] : "mixed";
  const justification = statuses.map((status) => status.justification).filter(isString).join(" ") || null;
  return {
    kind,
    label: statusLabel(kind, source),
    reviewed: kind === "accepted",
    reviewers: unique(statuses.flatMap((status) => status.reviewers)),
    justification,
    reason: readableText(justification),
    assertionStatus: statuses.length === 1 ? statuses[0].assertionStatus : null,
    reviewStatus: statuses.length === 1 ? statuses[0].reviewStatus : null,
    assertionIds: unique(statuses.flatMap((status) => status.assertionIds)),
    reviewIds: unique(statuses.flatMap((status) => status.reviewIds)),
  };
}

function emptyStatus(): ReportStatus {
  return {
    kind: "not_reviewed",
    label: "Not reviewed",
    reviewed: false,
    reviewers: [],
    justification: null,
    reason: emptyText(),
    assertionStatus: null,
    reviewStatus: null,
    assertionIds: [],
    reviewIds: [],
  };
}

export function statusLabel(kind: ReportStatusKind, source: ThreatSource): string {
  const ai = source.kind === "ai";
  switch (kind) {
    case "accepted":
      return "Accepted";
    case "changes_requested":
      return "Changes requested";
    case "rejected":
      return "Rejected";
    case "proposed":
      return ai ? "AI-proposed, not reviewed" : "Proposed, not reviewed";
    case "not_reviewed":
      return ai ? "AI-proposed, not reviewed" : "Not reviewed";
    case "mixed":
      return "Mixed review states";
    case "unknown":
      return "Unrecognised status, not reviewed";
  }
}

/** Where a threat came from, read from its recorded `source_method`. */
export function threatSource(sourceMethod: string | null): ThreatSource {
  if (!sourceMethod) return UNRECORDED_SOURCE;
  if (/^\s*ai:/i.test(sourceMethod) || /\bAI[- ]proposed\b/i.test(sourceMethod)) {
    return { kind: "ai", label: "AI-proposed" };
  }
  if (/\bAI[- ](drafted|generated)\b/i.test(sourceMethod)) return { kind: "ai", label: "AI-drafted" };
  if (/\bhuman\b/i.test(sourceMethod)) return { kind: "human", label: "Human-elicited" };
  return UNRECORDED_SOURCE;
}

function hasAssertion(properties: GraphProperties): boolean {
  return ["assertion_ids", "review_ids", "assertion_status", "review_status"].some((key) => key in properties);
}

// ── readable text ───────────────────────────────────────────────────────────

// A sentence with any of these is a modelling note, not reader text: ids (CURIEs,
// CPE, purl), schema field and class names, spec cross-references and code marks.
const SPEC_REFERENCE = /§|\b(?:ADR|DEC|DL|RPT|PLAN|ARCH|APP|MAP|PROC|BACKLOG|R)-\d+/;

const MODELLING_MARKUP: readonly RegExp[] = [
  /`/,
  SPEC_REFERENCE,
  /\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/,
  /\b[a-z][a-z0-9-]*:[a-z0-9][\w.@/-]*/i,
  /\b(?:Assertion|RiskScore|DamageScenario|ThreatInstance|AttackPath|AttackStep|AttackPattern|ProductInstance|LifecyclePhase|TrustBoundary|DataFlow|ThreatModel|SecurityProgram|GovernedView|RedundancyGroup|ExampleModel\w*)\b/,
  /\b[\w-]+\.(?:md|ya?ml|json)\b/,
];

/**
 * Splits a model description into what a reader sees and the full text. Spec
 * cross-references in parentheses, such as "(§3 structural node)" or
 * "(ADR-0002)", are left out.
 * The summary is the leading sentences up to the first one that holds a
 * modelling note, so a kept sentence never loses the context before it. Nothing
 * is reworded, and the full text stays available under details.
 */
export function readableText(raw: string | null): ReportText {
  if (!raw || !raw.trim()) return emptyText();
  const full = collapse(raw);
  const withoutRefs = full.replace(/\s*\(([^()]*)\)/g, (match, inner: string) => (
    SPEC_REFERENCE.test(inner) ? "" : match
  ));
  const kept: string[] = [];
  for (const sentence of sentences(withoutRefs)) {
    if (MODELLING_MARKUP.some((pattern) => pattern.test(sentence))) break;
    kept.push(sentence);
  }
  const summary = kept.join(" ").trim() || null;
  return { summary, full, trimmed: summary !== full };
}

/**
 * A model's product description as reader text. For a model with several
 * products the engine gives one line per product ("Name: description"); each
 * line is read on its own, so a modelling note in one product's text never
 * hides another product. The summary keeps one line per product.
 */
export function readableDescription(raw: string | null): ReportText {
  if (!raw || !raw.trim()) return emptyText();
  const parts = raw.split("\n").map(readableText).filter((part) => part.full !== null);
  if (parts.length <= 1) return parts[0] ?? emptyText();
  const summaries = parts.map((part) => part.summary).filter(isString);
  return {
    summary: summaries.join("\n") || null,
    full: parts.map((part) => part.full).join(" "),
    trimmed: parts.some((part) => part.trimmed) || summaries.length < parts.length,
  };
}

function sentences(value: string): string[] {
  const out: string[] = [];
  const boundary = /[.!?]+["')\]]*(?:\s+|$)/g;
  let start = 0;
  let match: RegExpExecArray | null;
  while ((match = boundary.exec(value)) !== null) {
    const end = match.index + match[0].length;
    const next = value.charAt(end);
    // Split only before a capital, a digit or an opening mark, so "e.g. the" stays whole.
    if (end < value.length && !/[A-Z0-9"'(@]/.test(next)) continue;
    out.push(value.slice(start, end).trim());
    start = end;
    if (end >= value.length) break;
  }
  if (start < value.length) out.push(value.slice(start).trim());
  return out.filter((sentence) => sentence.length > 0);
}

function emptyText(): ReportText {
  return { summary: null, full: null, trimmed: false };
}

// ── values ──────────────────────────────────────────────────────────────────

/** "very_low" → "Very low"; "lateral_movement" → "Lateral movement". */
export function humanize(value: string): string {
  const spaced = value
    .replace(/[_]+/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .trim();
  return spaced.charAt(0).toUpperCase() + spaced.slice(1).toLowerCase();
}

function optionalHumanized(value: GraphPropertyValue | undefined): string | null {
  const raw = text(value);
  return raw ? humanize(raw) : null;
}

function impactRatings(value: GraphPropertyValue | undefined): ImpactRating[] {
  const parsed = parseMapping(value);
  if (!parsed) return [];
  const keys = Object.keys(parsed).sort((a, b) => {
    const ai = IMPACT_ORDER.indexOf(a);
    const bi = IMPACT_ORDER.indexOf(b);
    return (ai < 0 ? IMPACT_ORDER.length : ai) - (bi < 0 ? IMPACT_ORDER.length : bi) || a.localeCompare(b);
  });
  return keys
    .filter((key) => typeof parsed[key] === "string" || typeof parsed[key] === "number")
    .map((key) => ({ category: humanize(key), rating: humanize(String(parsed[key])) }));
}

function parseMapping(value: GraphPropertyValue | undefined): Record<string, unknown> | null {
  if (typeof value !== "string" || !value.trim().startsWith("{")) return null;
  try {
    const parsed: unknown = JSON.parse(value);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? parsed as Record<string, unknown>
      : null;
  } catch {
    return null;
  }
}

function displayValue(value: GraphPropertyValue): string {
  if (Array.isArray(value)) return value.join(", ");
  if (value === null) return "—";
  return String(value);
}

function text(value: GraphPropertyValue | undefined): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function strings(value: GraphPropertyValue | undefined): string[] {
  if (typeof value === "string") return value.trim() ? [value] : [];
  if (Array.isArray(value)) return value.filter((entry) => typeof entry === "string" && entry.trim());
  return [];
}

function collapse(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function unique<T>(values: readonly T[]): T[] {
  return [...new Set(values)];
}

function uniqueRefs(refs: readonly ReportRef[]): ReportRef[] {
  const seen = new Set<string>();
  return refs.filter((ref) => (seen.has(ref.id) ? false : (seen.add(ref.id), true)));
}

function uniqueNodes(nodes: readonly EngineGraphNode[]): EngineGraphNode[] {
  const seen = new Set<string>();
  return nodes.filter((node) => (seen.has(node.id) ? false : (seen.add(node.id), true)));
}

function uniqueLists(lists: readonly number[][]): number[][] {
  const seen = new Set<string>();
  return lists.filter((list) => {
    const key = list.join(",");
    return seen.has(key) ? false : (seen.add(key), true);
  });
}

function isString(value: string | null | undefined): value is string {
  return typeof value === "string" && value.length > 0;
}

function isNumber(value: number | undefined): value is number {
  return typeof value === "number";
}

function isDefined<T>(value: T | undefined): value is T {
  return value !== undefined;
}

// ── graph index ─────────────────────────────────────────────────────────────

class GraphIndex {
  private readonly nodes: Map<string, EngineGraphNode>;
  private readonly types = new Map<string, EngineGraphNode[]>();
  private readonly out = new Map<string, EngineGraphEdge[]>();
  private readonly into = new Map<string, EngineGraphEdge[]>();

  constructor(nodes: readonly EngineGraphNode[], edges: readonly EngineGraphEdge[]) {
    this.nodes = new Map(nodes.map((node) => [node.id, node]));
    for (const node of nodes) push(this.types, node.domain_type, node);
    for (const edge of edges) {
      push(this.out, edge.source, edge);
      push(this.into, edge.target, edge);
    }
  }

  node(id: string): EngineGraphNode | undefined {
    return this.nodes.get(id);
  }

  ofType(type: string): EngineGraphNode[] {
    return this.types.get(type) ?? [];
  }

  outgoing(id: string): EngineGraphEdge[] {
    return this.out.get(id) ?? [];
  }

  incoming(id: string): EngineGraphEdge[] {
    return this.into.get(id) ?? [];
  }

  /** Objects this node points at through `slot`: projected edges, else id properties. */
  linked(id: string, slot: string, options: { authoredOnly?: boolean } = {}): EngineGraphNode[] {
    return this.targetIds(id, slot, options)
      .map((target) => this.nodes.get(target))
      .filter(isDefined);
  }

  refs(id: string, slot: string, options: { authoredOnly?: boolean } = {}): ReportRef[] {
    return uniqueRefs(this.targetIds(id, slot, options).map((target) => this.ref(target)));
  }

  sources(id: string, slot: string): EngineGraphNode[] {
    return this.incoming(id)
      .filter((edge) => edge.relationship_type === slot)
      .map((edge) => this.nodes.get(edge.source))
      .filter(isDefined);
  }

  ref(id: string): ReportRef {
    const node = this.nodes.get(id);
    if (!node) return { id, label: "An object this model does not define", missing: true };
    const name = displayName(node);
    const catalog = text(node.properties.catalog_ref);
    const showCatalog = catalog && ["Weakness", "AttackPattern", "Vulnerability"].includes(node.domain_type)
      && !name.includes(catalog);
    return { id, label: showCatalog ? `${name} (${catalog})` : name };
  }

  private targetIds(id: string, slot: string, options: { authoredOnly?: boolean }): string[] {
    const edges = this.outgoing(id).filter((edge) => (
      edge.relationship_type === slot && !(options.authoredOnly && isAssertedOnly(edge))
    ));
    const fromEdges = edges.map((edge) => edge.target);
    const node = this.nodes.get(id);
    const fromProperty = node ? strings(node.properties[slot]) : [];
    return unique([...fromEdges, ...fromProperty]);
  }
}

/**
 * The object's own name. The engine labels an unnamed object with its id, which
 * the default view never shows (#208), so it reads "Unnamed <type>" instead; the
 * id stays under Details.
 */
export function displayName(node: EngineGraphNode): string {
  if (node.label && node.label.trim() && node.label !== node.id) return node.label;
  const type = OBJECT_TYPE_LABELS[node.domain_type] ?? humanize(node.domain_type);
  return `Unnamed ${type.toLowerCase()}`;
}

// An edge that exists only because an Assertion names it, with no authored slot
// behind it, carries its review metadata and no authored value in the source node.
function isAssertedOnly(edge: EngineGraphEdge): boolean {
  return hasAssertion(edge.properties) && edge.properties.assertion_status !== "accepted";
}

function push<T>(map: Map<string, T[]>, key: string, value: T): void {
  const list = map.get(key);
  if (list) list.push(value);
  else map.set(key, [value]);
}
