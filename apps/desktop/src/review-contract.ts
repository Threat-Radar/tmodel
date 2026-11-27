// #290: the shapes of #289's review operations, as engine/HUMAN_REVIEW.md and
// engine/examples/human-review/contract.json define them. The screens rely on
// these parsers: an answer that names another model, revision, threat or route,
// or whose views disagree about their revision, stays an error and is never
// shown as a saved version.

import type { AttackPathResponse } from "./graph-types";
import type { EngineGraphResponse, ModelReportInput, ModelSummary } from "./model-types";
import { parseRiskCalculation, RISK_MATRIX, type RiskCalculation } from "./risk-calculation";

/** The one matrix profile the review operations accept (HUMAN_REVIEW.md). */
export const REVIEW_MATRIX = RISK_MATRIX;
export const IMPACT_CATEGORIES = ["safety", "financial", "operational", "privacy"] as const;
export type ImpactCategory = typeof IMPACT_CATEGORIES[number];
export const FEASIBILITY_VALUES = ["high", "medium", "low", "very_low"] as const;
export type FeasibilityValue = typeof FEASIBILITY_VALUES[number];
export const SEVERITY_VALUES = ["negligible", "moderate", "major", "severe"] as const;
export type SeverityValue = typeof SEVERITY_VALUES[number];
export const VERDICTS = ["accepted", "rejected"] as const;
export type Verdict = typeof VERDICTS[number];
/** Rationale and annotation limit, in characters (HUMAN_REVIEW.md). */
export const TEXT_LIMIT = 4096;
const ID_LIMIT = 256;

export interface ContextRequest {
  model_id: string;
  revision: string;
  matrix: string;
  threat_id: string;
  route_id: string;
}

export interface RefreshRequest {
  model_id: string;
  revision: string;
  matrix: string;
}

export interface ReviewUpdate {
  assertion_id: string;
  verdict: Verdict;
  rationale: string;
  annotation?: string;
  /** Present only to correct the reviewer's own existing review. */
  review_id?: string;
}

export interface FeasibilityUpdate {
  attack_path_id: string;
  rating: FeasibilityValue | null;
}

export interface ImpactUpdate {
  risk_score_id: string;
  damage_scenario_id: string | null;
  stakeholder_id: string | null;
  values: Partial<Record<ImpactCategory, SeverityValue | null>>;
}

export interface SaveRequest {
  model_id: string;
  expected_revision: string;
  matrix: string;
  threat_id: string;
  route_id: string;
  reviews?: ReviewUpdate[];
  feasibility?: FeasibilityUpdate[];
  impacts?: ImpactUpdate[];
}

export interface ReviewAssertion {
  id: string;
  subject: string;
  predicate: string;
  object: string;
  assertion_status: string | null;
  asserted_by: string | null;
  generated_by: string | null;
  confidence: string | null;
}

export interface ReviewRecord {
  id: string;
  reviews: string;
  reviewer: string | null;
  review_status: string | null;
  /** The rationale (`Review.justification`). */
  justification: string | null;
  /** The annotation (`Review.description`). */
  description: string | null;
}

export interface ReviewHistoryEntry {
  revision: string;
  review: ReviewRecord;
}

export interface ReviewStateSummary {
  id: string;
  status: string;
  reviewed: boolean;
}

export interface ReviewRoute {
  id: string;
  steps: string[];
  authored_path: string | null;
  rating_paths: string[];
  feasibility: FeasibilityValue | null;
  problems: string[];
}

export interface ReviewAttackPath {
  id: string;
  attack_feasibility: FeasibilityValue | null;
}

export interface ReviewRiskScore {
  id: string;
  threat: string;
  /** Null when the score records none; a save must send the same null back. */
  damage_scenario: string | null;
  for_stakeholder: string | null;
  impact: Partial<Record<ImpactCategory, SeverityValue | null>>;
}

export interface PermittedActions {
  submit_review: boolean;
  save_feasibility: boolean;
  save_impacts: boolean;
  correct_own_review: boolean;
  accept_proposal: boolean;
}

export interface ReviewContext {
  model_id: string;
  revision: string;
  reviewer_id: string;
  route: ReviewRoute;
  threat: { id: string };
  attack_paths: ReviewAttackPath[];
  assertions: ReviewAssertion[];
  reviews: ReviewRecord[];
  history: ReviewHistoryEntry[];
  review_states: ReviewStateSummary[];
  risk_scores: ReviewRiskScore[];
  calculated_risk: RiskCalculation;
  permitted_actions: PermittedActions;
  problems: string[];
}

/** Everything one saved revision shows, from one save or refresh answer. */
export interface RevisionViews {
  model_id: string;
  revision: string;
  graph: EngineGraphResponse;
  attackPaths: AttackPathResponse[];
  risk: RiskCalculation;
  /** The engine's `report_data`: the existing report builder's input for this revision. */
  reportInput: ModelReportInput;
}

export interface ReviewFieldError {
  field: string;
  message: string;
}

/** What the screens do about a failure (HUMAN_REVIEW.md, Errors). */
export type ReviewFailureKind =
  | "validation"
  | "permission"
  | "not_found"
  | "conflict"
  | "save_failure"
  | "unavailable"
  | "unexpected"
  | "network"
  | "malformed";

const KINDS: Readonly<Record<string, ReviewFailureKind>> = {
  validation_error: "validation",
  permission_denied: "permission",
  not_found: "not_found",
  revision_conflict: "conflict",
  save_failure: "save_failure",
  workspace_failure: "unavailable",
  internal_error: "unexpected",
  network_error: "network",
  malformed_response: "malformed",
};

/** A structured failure. Messages are the engine's own (never a path or credential) or the app's. */
export class ReviewApiError extends Error {
  readonly kind: ReviewFailureKind;

  constructor(
    readonly code: string,
    message: string,
    readonly details: {
      status?: number;
      fields?: readonly ReviewFieldError[];
      currentRevision?: string;
    } = {},
  ) {
    super(message);
    this.name = "ReviewApiError";
    this.kind = KINDS[code] ?? "unexpected";
  }
}

/** The error an engine answer carries, or a plain one for an unreadable answer. */
export function reviewErrorFromResponse(status: number, body: unknown): ReviewApiError {
  const error = isRecord(body) && isRecord(body.error) ? body.error : undefined;
  const code = typeof error?.code === "string" ? error.code : "internal_error";
  const message = typeof error?.message === "string" && error.message.trim()
    ? error.message
    : `The engine answered HTTP ${status}.`;
  const fields = Array.isArray(error?.fields)
    ? error.fields.filter((item): item is ReviewFieldError => isRecord(item)
      && typeof item.field === "string" && typeof item.message === "string")
    : undefined;
  const currentRevision = isText(error?.current_revision) ? error.current_revision : undefined;
  return new ReviewApiError(code, message, { status, fields, currentRevision });
}

export function malformed(what: string): ReviewApiError {
  return new ReviewApiError("malformed_response", `The engine's answer could not be read: ${what}.`);
}

/** A getReviewContext answer for exactly the requested model, revision, threat and route. */
export function parseReviewContext(value: unknown, request: ContextRequest): ReviewContext {
  if (!isRecord(value)) throw malformed("not an object");
  if (value.model_id !== request.model_id || value.revision !== request.revision) {
    throw malformed("it names another model or revision");
  }
  if (!isText(value.reviewer_id)) throw malformed("no verified reviewer");
  const route = parseRoute(value.route);
  if (route.id !== request.route_id) throw malformed("it names another route");
  if (!isRecord(value.threat) || value.threat.id !== request.threat_id) throw malformed("it names another threat");
  const assertions = list(value.assertions, "assertions").map(parseAssertion);
  const reviews = list(value.reviews, "reviews").map(parseReview);
  const history = list(value.history, "history").map((item) => {
    if (!isRecord(item) || !isText(item.revision)) throw malformed("a history entry has no revision");
    return { revision: item.revision, review: parseReview(item.review) };
  });
  const states = list(value.review_states, "review_states").map((item) => {
    if (!isRecord(item) || !isText(item.id) || typeof item.status !== "string" || typeof item.reviewed !== "boolean") {
      throw malformed("a review state is incomplete");
    }
    return { id: item.id, status: item.status, reviewed: item.reviewed };
  });
  const actions = value.permitted_actions;
  const names = ["submit_review", "save_feasibility", "save_impacts", "correct_own_review", "accept_proposal"] as const;
  if (!isRecord(actions) || !names.every((name) => typeof actions[name] === "boolean")) {
    throw malformed("the permitted actions are incomplete");
  }
  if (!Array.isArray(value.problems) || !value.problems.every((item) => typeof item === "string")) {
    throw malformed("the problems are not a list of codes");
  }
  return {
    model_id: request.model_id,
    revision: request.revision,
    reviewer_id: value.reviewer_id,
    route,
    threat: { id: request.threat_id },
    attack_paths: list(value.attack_paths, "attack_paths").map((item) => {
      if (!isRecord(item) || !isText(item.id) || !optionalFeasibility(item.attack_feasibility)) {
        throw malformed("an attack path record is incomplete");
      }
      return { id: item.id, attack_feasibility: (item.attack_feasibility ?? null) as FeasibilityValue | null };
    }),
    assertions,
    reviews,
    history,
    review_states: states,
    risk_scores: list(value.risk_scores, "risk_scores").map(parseRiskScore),
    calculated_risk: parseRisk(value.calculated_risk, request.model_id),
    permitted_actions: Object.fromEntries(names.map((name) => [name, actions[name] === true])) as unknown as PermittedActions,
    problems: [...value.problems] as string[],
  };
}

/**
 * A save or refresh answer: all four views tagged with one model and revision.
 * `revision` is the revision a refresh asked for; `notRevision` is the revision
 * a save started from, which a new saved revision can never equal.
 */
export function parseRevisionViews(
  value: unknown,
  expected: { model_id: string; revision?: string; notRevision?: string },
): RevisionViews {
  if (!isRecord(value) || value.model_id !== expected.model_id || !isText(value.revision)) {
    throw malformed("it names another model or no revision");
  }
  const revision = value.revision;
  if (expected.revision !== undefined && revision !== expected.revision) throw malformed("it names another revision");
  if (expected.notRevision !== undefined && revision === expected.notRevision) {
    throw malformed("the saved revision is the one the save started from");
  }
  const tagged = (name: string): Record<string, unknown> => {
    const view = value[name];
    if (!isRecord(view) || view.model_id !== expected.model_id || view.revision !== revision) {
      throw malformed(`its ${name} view belongs to another revision`);
    }
    return view;
  };
  const graph = parseGraph(tagged("graph"), "graph");
  const paths = tagged("attack_paths");
  const attackPaths = list(paths.responses, "attack path responses").map(parseAttackPathResponse);
  const risk = parseRisk(tagged("risk"), expected.model_id);
  const report = tagged("report_data");
  const reportGraph = parseGraph(report.graph, "report graph");
  const reportPaths = list(report.attackPaths, "report attack paths").map(parseAttackPathResponse);
  if (reportGraph.nodes.length !== graph.nodes.length || reportGraph.edges.length !== graph.edges.length
    || reportPaths.length !== attackPaths.length) {
    throw malformed("its report and its graph describe different models");
  }
  return {
    model_id: expected.model_id,
    revision,
    graph,
    attackPaths,
    risk,
    reportInput: { model: parseModelSummary(report.model), graph: reportGraph, attackPaths: reportPaths },
  };
}

/** The file label a risk answer gets, so #63's parser (which matches a file name) accepts it. */
export function riskLabel(modelId: string): string {
  return modelId.split(/[\\/]/).pop() || "model";
}

function parseRisk(value: unknown, modelId: string): RiskCalculation {
  if (!isRecord(value) || value.matrix !== REVIEW_MATRIX) throw malformed("its risk uses another matrix");
  const label = riskLabel(modelId);
  try {
    return parseRiskCalculation({ ...value, file: label }, label, REVIEW_MATRIX);
  } catch {
    throw malformed("its calculated risk is incomplete");
  }
}

function parseRoute(value: unknown): ReviewRoute {
  if (!isRecord(value) || !isText(value.id) || !strings(value.steps) || !strings(value.rating_paths)
    || !strings(value.problems) || !optionalFeasibility(value.feasibility)
    || !(value.authored_path === undefined || value.authored_path === null || isText(value.authored_path))) {
    throw malformed("the route is incomplete");
  }
  return {
    id: value.id,
    steps: [...value.steps],
    authored_path: (value.authored_path ?? null) as string | null,
    rating_paths: [...value.rating_paths],
    feasibility: (value.feasibility ?? null) as FeasibilityValue | null,
    problems: [...value.problems],
  };
}

function parseAssertion(value: unknown): ReviewAssertion {
  if (!isRecord(value) || !isText(value.id) || !isText(value.subject) || !isText(value.predicate) || !isText(value.object)) {
    throw malformed("an assertion is incomplete");
  }
  return {
    id: value.id,
    subject: value.subject,
    predicate: value.predicate,
    object: value.object,
    assertion_status: optionalText(value.assertion_status),
    asserted_by: optionalText(value.asserted_by),
    generated_by: optionalText(value.generated_by),
    confidence: optionalText(value.confidence),
  };
}

function parseReview(value: unknown): ReviewRecord {
  if (!isRecord(value) || !isText(value.id) || !isText(value.reviews)) throw malformed("a review is incomplete");
  return {
    id: value.id,
    reviews: value.reviews,
    reviewer: optionalText(value.reviewer),
    review_status: optionalText(value.review_status),
    justification: optionalText(value.justification),
    description: optionalText(value.description),
  };
}

function parseRiskScore(value: unknown): ReviewRiskScore {
  if (!isRecord(value) || !isText(value.id) || !isText(value.threat)) throw malformed("a risk score is incomplete");
  const impact = value.impact ?? {};
  if (!isRecord(impact) || Object.entries(impact).some(([category, rating]) => !(IMPACT_CATEGORIES as readonly string[]).includes(category)
    || !(rating === null || (SEVERITY_VALUES as readonly unknown[]).includes(rating)))) {
    throw malformed("a risk score's impact is not a permitted rating");
  }
  return {
    id: value.id,
    threat: value.threat,
    damage_scenario: optionalText(value.damage_scenario),
    for_stakeholder: optionalText(value.for_stakeholder),
    impact: { ...impact } as ReviewRiskScore["impact"],
  };
}

function parseGraph(value: unknown, what: string): EngineGraphResponse {
  if (!isRecord(value) || typeof value.file !== "string" || !Array.isArray(value.nodes) || !Array.isArray(value.edges)
    || !value.nodes.every((node) => isRecord(node) && isText(node.id) && typeof node.domain_type === "string")
    || !value.edges.every((edge) => isRecord(edge) && isText(edge.id) && isText(edge.source) && isText(edge.target))) {
    throw malformed(`its ${what} is incomplete`);
  }
  return value as unknown as EngineGraphResponse;
}

function parseAttackPathResponse(value: unknown): AttackPathResponse {
  if (!isRecord(value) || !isText(value.goal) || !Array.isArray(value.paths)
    || !value.paths.every((path) => isRecord(path) && strings(path.steps))) {
    throw malformed("an attack path answer is incomplete");
  }
  return value as unknown as AttackPathResponse;
}

function parseModelSummary(value: unknown): ModelSummary {
  if (!isRecord(value) || !isText(value.id) || typeof value.title !== "string" || typeof value.kind_label !== "string"
    || !isRecord(value.counts) || typeof value.reviewed_threats !== "number") {
    throw malformed("its report header is incomplete");
  }
  return value as unknown as ModelSummary;
}

function list(value: unknown, what: string): unknown[] {
  if (!Array.isArray(value)) throw malformed(`${what} is not a list`);
  return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isText(value: unknown): value is string {
  return typeof value === "string" && value.length > 0 && value.length <= ID_LIMIT;
}

function optionalText(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function strings(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function optionalFeasibility(value: unknown): boolean {
  return value === undefined || value === null || (FEASIBILITY_VALUES as readonly unknown[]).includes(value);
}
