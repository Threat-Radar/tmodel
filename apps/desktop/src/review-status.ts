import type { GraphAssertionProvenance, GraphProperties, GraphPropertyValue } from "./graph-types";

export type ReviewStateKind =
  | "accepted"
  | "proposed"
  | "changes_requested"
  | "rejected"
  | "unknown";

export interface ReviewStatePresentation {
  kind: ReviewStateKind;
  /** Short title-case label for selectors, badges and the legend. */
  label: string;
  /** Sentence used in status banners; never implies review unless accepted. */
  description: string;
  /** The model's own values, unchanged, for display beside the label. */
  assertionStatus: string | null;
  reviewStatus: string | null;
}

// Order of the relationship-status legend and of the style rules in the graph.
export const REVIEW_STATE_KINDS: readonly ReviewStateKind[] = [
  "accepted",
  "proposed",
  "changes_requested",
  "rejected",
  "unknown",
];

export const REVIEW_STATE_LABELS: Readonly<Record<ReviewStateKind, string>> = {
  accepted: "Accepted",
  proposed: "Proposed",
  changes_requested: "Changes Requested",
  rejected: "Rejected",
  unknown: "Unknown Status",
};

const DESCRIPTIONS: Readonly<Record<ReviewStateKind, string>> = {
  accepted: "reviewed and accepted",
  proposed: "proposed, not accepted",
  changes_requested: "changes requested, not accepted",
  rejected: "rejected, not accepted",
  unknown: "unrecognized status, not treated as reviewed",
};

/**
 * Presents recorded Assertion/Review status strings without verifying a person.
 *
 * Both are open strings in the schema; this only chooses how to display them.
 * A negative human verdict on either value wins, so a rejected or
 * changes-requested record is never drawn as accepted. Otherwise only an
 * accepted Assertion, with no contrary Review, has an accepted recorded status.
 * Actual model relationships use relationshipReviewState and the engine's human
 * evidence result before describing a relationship as reviewed. A Review cannot accept a
 * `proposed` Assertion on its own; it stays proposed until the Assertion is.
 */
export function reviewStatePresentation(
  assertionStatus: string | null | undefined,
  reviewStatus: string | null | undefined,
): ReviewStatePresentation {
  const assertion = normalize(assertionStatus);
  const review = normalize(reviewStatus);
  const kind = reviewStateKind(assertion, review);
  const unrecorded = assertion === undefined && review === undefined;
  return {
    kind,
    label: unrecorded ? "Not Reviewed" : REVIEW_STATE_LABELS[kind],
    description: unrecorded ? "not reviewed, no status recorded" : DESCRIPTIONS[kind],
    assertionStatus: assertionStatus ?? null,
    reviewStatus: reviewStatus ?? null,
  };
}

/**
 * The review presentation of a graph relationship, or `undefined` for a
 * structural relationship that carries no Assertion or Review metadata.
 */
export function relationshipReviewState(
  properties: GraphProperties,
): ReviewStatePresentation | undefined {
  const hasMetadata = ["assertion_ids", "review_ids", "assertion_status", "review_status"]
    .some((key) => key in properties);
  if (!hasMetadata) return undefined;
  const recorded = reviewStatePresentation(
    stringValue(properties.assertion_status),
    stringValue(properties.review_status),
  );
  const effective = typeof properties.human_reviewed === "boolean"
    ? reviewStatePresentation(
      stringValue(properties.effective_assertion_status),
      stringValue(properties.effective_review_status),
    )
    : recorded;
  // Status strings alone cannot establish human acceptance, including old
  // snapshots without evidence. A contradictory effective verdict also wins
  // over a stale reviewed flag. Recorded agent opinions stay separate.
  if (effective.kind === "accepted" && properties.human_reviewed !== true) {
    return { ...recorded, kind: "unknown", label: "Not Reviewed",
      description: "human acceptance is not established" };
  }
  return { ...recorded, kind: effective.kind, label: effective.label,
    description: effective.description };
}

/** A single Assertion's effective evidence, retaining its recorded values. */
export function assertionReviewState(
  assertion: GraphAssertionProvenance, recordedReviewStatus: string | null,
): ReviewStatePresentation {
  return relationshipReviewState({
    assertion_status: assertion.assertion_status,
    review_status: recordedReviewStatus,
    ...(typeof assertion.human_reviewed === "boolean" ? {
      human_reviewed: assertion.human_reviewed,
      effective_assertion_status: assertion.assertion_status,
      effective_review_status: assertion.effective_status === "unreviewed"
        ? null : assertion.effective_status ?? null,
    } : {}),
  })!;
}

function reviewStateKind(
  assertion: string | undefined,
  review: string | undefined,
): ReviewStateKind {
  if (assertion === "rejected" || review === "rejected") return "rejected";
  if (assertion === "changes_requested" || review === "changes_requested") {
    return "changes_requested";
  }
  if (assertion === "accepted") {
    return review === undefined || review === "accepted" ? "accepted" : "unknown";
  }
  if (assertion === "proposed") return "proposed";
  return "unknown";
}

function normalize(value: string | null | undefined): string | undefined {
  const normalized = value?.trim().toLowerCase().replace(/[\s-]+/g, "_");
  return normalized ? normalized : undefined;
}

function stringValue(value: GraphPropertyValue | undefined): string | null {
  return typeof value === "string" ? value : null;
}
