import { describe, expect, it } from "vitest";
import { relationshipReviewState, reviewStatePresentation } from "./review-status";

describe("review-state presentation", () => {
  it.each([
    ["accepted", "accepted", "accepted", "Accepted"],
    ["accepted", null, "accepted", "Accepted"],
    ["proposed", null, "proposed", "Proposed"],
    ["proposed", "changes_requested", "changes_requested", "Changes Requested"],
    ["proposed", "rejected", "rejected", "Rejected"],
    ["rejected", null, "rejected", "Rejected"],
  ] as const)("presents assertion %s with review %s as %s", (assertion, review, kind, label) => {
    const presentation = reviewStatePresentation(assertion, review);
    expect(presentation.kind).toBe(kind);
    expect(presentation.label).toBe(label);
    expect(presentation.assertionStatus).toBe(assertion);
    expect(presentation.reviewStatus).toBe(review);
  });

  it("lets a negative human verdict win over an accepted Assertion", () => {
    expect(reviewStatePresentation("accepted", "rejected").kind).toBe("rejected");
    expect(reviewStatePresentation("accepted", "changes_requested").kind).toBe("changes_requested");
    expect(reviewStatePresentation("changes_requested", "accepted").kind).toBe("changes_requested");
    expect(reviewStatePresentation("rejected", "changes_requested").kind).toBe("rejected");
  });

  it("does not let a Review accept a proposed Assertion on its own", () => {
    expect(reviewStatePresentation("proposed", "accepted").kind).toBe("proposed");
  });

  it("treats unrecognized or contradictory values as unknown, never accepted", () => {
    expect(reviewStatePresentation("needs_triage", null)).toMatchObject({
      kind: "unknown",
      label: "Unknown Status",
      assertionStatus: "needs_triage",
    });
    expect(reviewStatePresentation("accepted", "pending").kind).toBe("unknown");
    expect(reviewStatePresentation(null, "accepted").kind).toBe("unknown");
  });

  it("labels a record with no status as not reviewed", () => {
    expect(reviewStatePresentation(null, undefined)).toMatchObject({
      kind: "unknown",
      label: "Not Reviewed",
      description: "not reviewed, no status recorded",
      assertionStatus: null,
      reviewStatus: null,
    });
  });

  it("normalizes case and separators but returns the raw values unchanged", () => {
    const presentation = reviewStatePresentation(" Proposed ", "Changes-Requested");
    expect(presentation.kind).toBe("changes_requested");
    expect(presentation.assertionStatus).toBe(" Proposed ");
    expect(presentation.reviewStatus).toBe("Changes-Requested");
  });

  it("keeps structural relationships without Assertion metadata neutral", () => {
    expect(relationshipReviewState({})).toBeUndefined();
    expect(relationshipReviewState({ description: "composed of" })).toBeUndefined();
  });

  it("presents an Assertion-backed relationship even when no status was recorded", () => {
    expect(relationshipReviewState({ assertion_ids: ["assertion:a"] })).toMatchObject({
      kind: "unknown",
      label: "Not Reviewed",
    });
    expect(relationshipReviewState({
      assertion_ids: ["assertion:ai-imds-pivot-realizes"],
      assertion_status: "proposed",
      review_ids: ["review:ai-triage"],
      review_status: "changes_requested",
    })).toMatchObject({ kind: "changes_requested", label: "Changes Requested" });
  });
});
