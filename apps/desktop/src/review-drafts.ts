// #290: unsaved review input for one route, and the one atomic save request it
// becomes. Drafts hold only what the reviewer changed, so a value set back to
// the recorded one is no longer a change, and an omitted impact category keeps
// its recorded value (HUMAN_REVIEW.md, Rating scope). Nothing here is lost on a
// failed save: a draft is cleared only after the engine confirms the save.

import {
  IMPACT_CATEGORIES,
  TEXT_LIMIT,
  VERDICTS,
  type FeasibilityValue,
  type ImpactCategory,
  type ImpactUpdate,
  type ReviewContext,
  type ReviewRecord,
  type ReviewUpdate,
  type SaveRequest,
  type SeverityValue,
  type Verdict,
} from "./review-contract";

export interface ReviewDraft {
  verdict?: Verdict;
  rationale?: string;
  annotation?: string;
}

/** One route's unsaved input, tied to the version it was made on. */
export class RouteDraft {
  readonly reviews = new Map<string, ReviewDraft>();
  readonly feasibility = new Map<string, FeasibilityValue | null>();
  readonly impacts = new Map<string, Map<ImpactCategory, SeverityValue | null>>();

  constructor(readonly threatId: string, readonly routeId: string, public baseRevision: string) {}

  get empty(): boolean {
    return this.reviews.size === 0 && this.feasibility.size === 0 && this.impacts.size === 0;
  }
}

export function routeKey(threatId: string, routeId: string): string {
  return `${threatId}\u0000${routeId}`;
}

/** The reviewer's own review of an assertion: the one a save corrects. */
export function ownReview(context: ReviewContext, assertionId: string): ReviewRecord | undefined {
  return context.reviews.find((review) => review.reviews === assertionId && review.reviewer === context.reviewer_id);
}

/** What the form shows for an assertion: the draft over the reviewer's own review. */
export function reviewValues(context: ReviewContext, draft: RouteDraft | undefined, assertionId: string) {
  const own = ownReview(context, assertionId);
  const entry = draft?.reviews.get(assertionId);
  const recordedVerdict = own && (VERDICTS as readonly string[]).includes(own.review_status ?? "")
    ? own.review_status as Verdict
    : undefined;
  return {
    own,
    verdict: entry?.verdict ?? recordedVerdict,
    rationale: entry?.rationale ?? own?.justification ?? "",
    annotation: entry?.annotation ?? own?.description ?? "",
  };
}

export function feasibilityValue(context: ReviewContext, draft: RouteDraft | undefined, pathId: string): FeasibilityValue | null {
  if (draft?.feasibility.has(pathId)) return draft.feasibility.get(pathId) ?? null;
  return context.attack_paths.find((path) => path.id === pathId)?.attack_feasibility ?? null;
}

export function impactValue(
  context: ReviewContext,
  draft: RouteDraft | undefined,
  scoreId: string,
  category: ImpactCategory,
): SeverityValue | null {
  const changed = draft?.impacts.get(scoreId);
  if (changed?.has(category)) return changed.get(category) ?? null;
  return context.risk_scores.find((score) => score.id === scoreId)?.impact[category] ?? null;
}

/** Records a review edit, dropping it once it matches what is recorded. */
export function setReviewField(
  context: ReviewContext,
  draft: RouteDraft,
  assertionId: string,
  field: keyof ReviewDraft,
  value: string,
): void {
  const entry = { ...draft.reviews.get(assertionId) };
  if (field === "verdict") {
    if ((VERDICTS as readonly string[]).includes(value)) entry.verdict = value as Verdict;
  } else {
    entry[field] = value;
  }
  const own = ownReview(context, assertionId);
  const recorded: ReviewDraft = {
    verdict: own?.review_status as Verdict | undefined,
    rationale: own?.justification ?? "",
    annotation: own?.description ?? "",
  };
  for (const key of ["verdict", "rationale", "annotation"] as const) {
    if (entry[key] !== undefined && entry[key] === recorded[key]) delete entry[key];
  }
  if (Object.keys(entry).length === 0) draft.reviews.delete(assertionId);
  else draft.reviews.set(assertionId, entry);
}

export function setFeasibility(context: ReviewContext, draft: RouteDraft, pathId: string, value: FeasibilityValue | null): void {
  const recorded = context.attack_paths.find((path) => path.id === pathId)?.attack_feasibility ?? null;
  if (value === recorded) draft.feasibility.delete(pathId);
  else draft.feasibility.set(pathId, value);
}

export function setImpact(
  context: ReviewContext,
  draft: RouteDraft,
  scoreId: string,
  category: ImpactCategory,
  value: SeverityValue | null,
): void {
  const recorded = context.risk_scores.find((score) => score.id === scoreId)?.impact[category] ?? null;
  const changed = new Map(draft.impacts.get(scoreId));
  if (value === recorded) changed.delete(category);
  else changed.set(category, value);
  if (changed.size === 0) draft.impacts.delete(scoreId);
  else draft.impacts.set(scoreId, changed);
}

export type DraftField = "verdict" | "rationale" | "annotation" | "feasibility" | "impact";

export interface DraftProblem {
  /** The assertion, attack path or risk score the problem is about. */
  target: string;
  field: DraftField;
  message: string;
}

export interface SavePlan {
  request: SaveRequest;
  /** What blocks the save: the request is sent only when this is empty. */
  problems: DraftProblem[];
  /** Draft entries for targets this version no longer has: kept, listed, not sent. */
  stale: string[];
  changes: number;
}

/**
 * The one saveModelChanges request for a route's draft, against the version the
 * context was read from. A review of an assertion the reviewer already reviewed
 * is always sent as a correction of that review, never as a second review.
 */
export function planSave(context: ReviewContext, draft: RouteDraft, matrix: string): SavePlan {
  const problems: DraftProblem[] = [];
  const stale: string[] = [];
  const actions = context.permitted_actions;
  const reviews: ReviewUpdate[] = [];
  for (const [assertionId, entry] of draft.reviews) {
    if (!context.assertions.some((assertion) => assertion.id === assertionId)) {
      stale.push(assertionId);
      continue;
    }
    const values = reviewValues(context, draft, assertionId);
    const allowed = values.own ? actions.correct_own_review : actions.submit_review;
    if (!allowed) {
      problems.push({ target: assertionId, field: "verdict", message: "This session cannot record this review." });
      continue;
    }
    if (!values.verdict) problems.push({ target: assertionId, field: "verdict", message: "Choose accept or reject." });
    if (!values.rationale.trim()) {
      problems.push({ target: assertionId, field: "rationale", message: "Explain the decision: a rationale is required." });
    } else if (values.rationale.length > TEXT_LIMIT) {
      problems.push({ target: assertionId, field: "rationale", message: `Shorten the rationale to ${TEXT_LIMIT} characters or fewer.` });
    }
    if (values.annotation.length > TEXT_LIMIT) {
      problems.push({ target: assertionId, field: "annotation", message: `Shorten the annotation to ${TEXT_LIMIT} characters or fewer.` });
    }
    if (!values.verdict) continue;
    const update: ReviewUpdate = { assertion_id: assertionId, verdict: values.verdict, rationale: values.rationale };
    // Omitting the annotation keeps a recorded note; an empty one clears it.
    if (entry.annotation !== undefined && (values.own || entry.annotation.trim())) update.annotation = entry.annotation;
    if (values.own) update.review_id = values.own.id;
    reviews.push(update);
  }
  const feasibility = [...draft.feasibility].flatMap(([pathId, rating]) => {
    if (!context.route.rating_paths.includes(pathId) || !context.attack_paths.some((path) => path.id === pathId)) {
      stale.push(pathId);
      return [];
    }
    if (!actions.save_feasibility) {
      problems.push({ target: pathId, field: "feasibility", message: "This session cannot change feasibility ratings." });
      return [];
    }
    return [{ attack_path_id: pathId, rating }];
  });
  const impacts: ImpactUpdate[] = [];
  for (const [scoreId, changed] of draft.impacts) {
    const score = context.risk_scores.find((candidate) => candidate.id === scoreId);
    if (!score) {
      stale.push(scoreId);
      continue;
    }
    if (!actions.save_impacts) {
      problems.push({ target: scoreId, field: "impact", message: "This session cannot change impact ratings." });
      continue;
    }
    const values: ImpactUpdate["values"] = {};
    for (const category of IMPACT_CATEGORIES) if (changed.has(category)) values[category] = changed.get(category) ?? null;
    impacts.push({
      risk_score_id: scoreId,
      damage_scenario_id: score.damage_scenario,
      stakeholder_id: score.for_stakeholder,
      values,
    });
  }
  const request: SaveRequest = {
    model_id: context.model_id,
    expected_revision: context.revision,
    matrix,
    threat_id: context.threat.id,
    route_id: context.route.id,
  };
  if (reviews.length) request.reviews = reviews;
  if (feasibility.length) request.feasibility = feasibility;
  if (impacts.length) request.impacts = impacts;
  const changes = reviews.length + feasibility.length
    + impacts.reduce((total, update) => total + Object.keys(update.values).length, 0);
  return { request, problems, stale, changes };
}

/** Counts a draft's changes the way the unsaved-changes summary lists them. */
export function draftChangeCount(draft: RouteDraft | undefined): number {
  if (!draft) return 0;
  let count = draft.reviews.size + draft.feasibility.size;
  for (const changed of draft.impacts.values()) count += changed.size;
  return count;
}

/** Removes what a save stored, keeping anything typed after the save began. */
export function clearSaved(draft: RouteDraft, saved: RouteDraft): void {
  for (const [id, entry] of saved.reviews) {
    const now = draft.reviews.get(id);
    if (now && now.verdict === entry.verdict && now.rationale === entry.rationale && now.annotation === entry.annotation) {
      draft.reviews.delete(id);
    }
  }
  for (const [id, rating] of saved.feasibility) if (draft.feasibility.get(id) === rating) draft.feasibility.delete(id);
  for (const [id, changed] of saved.impacts) {
    const now = draft.impacts.get(id);
    if (!now) continue;
    for (const [category, value] of changed) if (now.get(category) === value) now.delete(category);
    if (now.size === 0) draft.impacts.delete(id);
  }
}

export function snapshot(draft: RouteDraft): RouteDraft {
  const copy = new RouteDraft(draft.threatId, draft.routeId, draft.baseRevision);
  for (const [id, entry] of draft.reviews) copy.reviews.set(id, { ...entry });
  for (const [id, rating] of draft.feasibility) copy.feasibility.set(id, rating);
  for (const [id, changed] of draft.impacts) copy.impacts.set(id, new Map(changed));
  return copy;
}
