import type { GraphProperties, GraphPropertyValue } from "./graph-types";

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
 * Presents an Assertion's `assertion_status` with its Review's `review_status`.
 *
 * Both are open strings in the schema; this only chooses how to display them.
 * A negative human verdict on either value wins, so a rejected or
 * changes-requested record is never drawn as accepted. Otherwise only an
 * accepted Assertion, with no contrary Review, is accepted: the same rule as
 * the engine's `ReviewState` (APP-0001 A-007, A-045). A Review cannot accept a
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
  return reviewStatePresentation(
    stringValue(properties.assertion_status),
    stringValue(properties.review_status),
  );
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
