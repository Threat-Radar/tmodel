import { describe, expect, it } from "vitest";
import contract from "../../../engine/examples/human-review/contract.json";
import revisions from "./fixtures/human-review-revisions.json";
import { parseReviewContext, REVIEW_MATRIX, TEXT_LIMIT, type ContextRequest, type ReviewContext } from "./review-contract";
import {
  clearSaved,
  draftChangeCount,
  planSave,
  reviewValues,
  RouteDraft,
  setFeasibility,
  setImpact,
  setReviewField,
  snapshot,
} from "./review-drafts";

const r1 = () => parseReviewContext(contract.context.response, contract.context.request as ContextRequest);
const r2 = () => parseReviewContext(revisions.context_r2.response, revisions.context_r2.request as ContextRequest);
const draftFor = (context: ReviewContext) => new RouteDraft(context.threat.id, context.route.id, context.revision);

describe("review drafts", () => {
  it("keeps only what differs from the recorded values", () => {
    const context = r1();
    const draft = draftFor(context);
    setFeasibility(context, draft, "path:a", "high");
    setImpact(context, draft, "risk:r", "privacy", "major");
    expect(draftChangeCount(draft)).toBe(2);
    setFeasibility(context, draft, "path:a", "low");
    setImpact(context, draft, "risk:r", "privacy", "negligible");
    expect(draft.empty).toBe(true);
  });

  it("sends only the changed impact categories, with the score's own damage and stakeholder", () => {
    const context = r1();
    const draft = draftFor(context);
    setImpact(context, draft, "risk:r", "safety", null);
    const plan = planSave(context, draft, REVIEW_MATRIX);
    expect(plan.request.impacts).toEqual([{ risk_score_id: "risk:r", damage_scenario_id: "damage:d", stakeholder_id: "party:reviewer", values: { safety: null } }]);
    expect(plan.request.reviews).toBeUndefined();
    expect(plan.request.feasibility).toBeUndefined();
  });

  it("refuses a decision without a verdict or rationale, or a text over the limit, and sends nothing", () => {
    const context = r1();
    const draft = draftFor(context);
    setReviewField(context, draft, "assertion:path", "rationale", "   ");
    setReviewField(context, draft, "assertion:path", "annotation", "a".repeat(TEXT_LIMIT + 1));
    const plan = planSave(context, draft, REVIEW_MATRIX);
    expect(plan.problems.map((problem) => problem.field)).toEqual(["verdict", "rationale", "annotation"]);
    expect(plan.request.reviews).toBeUndefined();
  });

  it("corrects the reviewer's own review by its id, keeping or clearing the annotation as asked", () => {
    const context = r2();
    expect(reviewValues(context, undefined, "assertion:path")).toMatchObject({
      verdict: "accepted",
      rationale: "Test-only human input supplied by the test client.",
      annotation: "Synthetic contract example",
    });
    const draft = draftFor(context);
    setReviewField(context, draft, "assertion:path", "verdict", "rejected");
    let plan = planSave(context, draft, REVIEW_MATRIX);
    // Omitting the annotation keeps the recorded note.
    expect(plan.request.reviews).toEqual([{
      assertion_id: "assertion:path",
      verdict: "rejected",
      rationale: "Test-only human input supplied by the test client.",
      review_id: "review:fixture-review",
    }]);
    setReviewField(context, draft, "assertion:path", "annotation", "");
    plan = planSave(context, draft, REVIEW_MATRIX);
    expect(plan.request.reviews?.[0].annotation).toBe("");
  });

  it("does not offer what the session may not do", () => {
    const context = { ...r1(), permitted_actions: { ...r1().permitted_actions, submit_review: false, save_feasibility: false } };
    const draft = draftFor(context);
    setReviewField(context, draft, "assertion:path", "verdict", "accepted");
    setFeasibility(context, draft, "path:a", "high");
    const plan = planSave(context, draft, REVIEW_MATRIX);
    expect(plan.problems.map((problem) => problem.message)).toEqual([
      "This session cannot record this review.",
      "This session cannot change feasibility ratings.",
    ]);
  });

  it("keeps but does not send changes for targets the version no longer has", () => {
    const context = r1();
    const draft = draftFor(context);
    draft.feasibility.set("path:gone", "high");
    draft.impacts.set("risk:gone", new Map([["safety", "major"]]));
    const plan = planSave(context, draft, REVIEW_MATRIX);
    expect(plan.stale).toEqual(["path:gone", "risk:gone"]);
    expect(plan.changes).toBe(0);
    expect(draftChangeCount(draft)).toBe(2);
  });

  it("clears only what a save stored, keeping anything changed after the save began", () => {
    const context = r1();
    const draft = draftFor(context);
    setFeasibility(context, draft, "path:a", "high");
    setImpact(context, draft, "risk:r", "privacy", "major");
    const saved = snapshot(draft);
    setImpact(context, draft, "risk:r", "privacy", "severe");
    clearSaved(draft, saved);
    expect(draft.feasibility.size).toBe(0);
    expect(draft.impacts.get("risk:r")?.get("privacy")).toBe("severe");
  });
});
