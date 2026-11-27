// #290 contract tests: the screens' parsing and requests against #289's real
// examples (engine/examples/human-review/contract.json) and the review
// service's own r1 refresh and r2 context (fixtures/human-review-revisions.json).
import { describe, expect, it } from "vitest";
import contract from "../../../engine/examples/human-review/contract.json";
import revisions from "./fixtures/human-review-revisions.json";
import { buildModelReport } from "./model-report";
import {
  parseReviewContext,
  parseRevisionViews,
  REVIEW_MATRIX,
  ReviewApiError,
  reviewErrorFromResponse,
  type ContextRequest,
} from "./review-contract";
import { planSave, RouteDraft, setFeasibility, setImpact, setReviewField } from "./review-drafts";

const contextRequest = contract.context.request as ContextRequest;

describe("review contract (#289 examples)", () => {
  it("reads the context example for exactly the requested model, revision, threat and route", () => {
    const context = parseReviewContext(contract.context.response, contextRequest);
    expect(context.revision).toBe("r1");
    expect(context.reviewer_id).toBe("party:reviewer");
    expect(context.route.id).toBe(contextRequest.route_id);
    expect(context.route.rating_paths).toEqual(["path:a"]);
    expect(context.assertions.map((assertion) => [assertion.subject, assertion.predicate, assertion.object]))
      .toEqual([["path:a", "realizes_threat", "threat:t"]]);
    expect(context.permitted_actions).toEqual(contract.context.response.permitted_actions);
    expect(context.risk_scores[0].impact.privacy).toBe("negligible");
    expect(context.calculated_risk.assessments[0].derived_risk).toEqual({ safety: 3, financial: 2, operational: 2, privacy: 1 });
    expect(REVIEW_MATRIX).toBe(contextRequest.matrix);
  });

  it("refuses a context for another revision, route or threat, or without permitted actions", () => {
    const response = contract.context.response;
    expect(() => parseReviewContext(response, { ...contextRequest, revision: "r2" })).toThrow(/another model or revision/);
    expect(() => parseReviewContext(response, { ...contextRequest, route_id: "route:other" })).toThrow(/another route/);
    expect(() => parseReviewContext(response, { ...contextRequest, threat_id: "threat:other" })).toThrow(/another threat/);
    const { permitted_actions: _actions, ...withoutActions } = response;
    expect(() => parseReviewContext(withoutActions, contextRequest)).toThrow(/permitted actions/);
  });

  it("reads the r2 context the engine gives after the contract's save, with the reviewer's own review", () => {
    const request = revisions.context_r2.request as ContextRequest;
    const context = parseReviewContext(revisions.context_r2.response, request);
    expect(context.reviews).toEqual([expect.objectContaining({ id: "review:fixture-review", reviewer: "party:reviewer", review_status: "accepted" })]);
    expect(context.history.map((entry) => entry.revision)).toEqual(["r2"]);
    expect(context.permitted_actions.correct_own_review).toBe(true);
    expect(context.permitted_actions.accept_proposal).toBe(false);
  });

  it("reads the save response as one revision's views, all tagged r2", () => {
    const views = parseRevisionViews(contract.save.response, { model_id: "local:one", notRevision: "r1" });
    expect(views.revision).toBe("r2");
    expect(views.graph.nodes).toHaveLength(10);
    expect(views.attackPaths.map((response) => response.goal)).toEqual(["threat:t"]);
    expect(views.risk.assessments[0].derived_risk).toEqual({ safety: 5, financial: 4, operational: 3, privacy: 4 });
    expect(views.reportInput.model.kind_label).toBe("Editable local model");
    // The existing report builder reads report_data as it is.
    const report = buildModelReport(views.reportInput);
    expect(report.attackPaths.map((row) => row.id)).toEqual(["path:a"]);
  });

  it("refuses views that disagree about their revision, or a save that names its own starting revision", () => {
    const response = contract.save.response;
    expect(() => parseRevisionViews({ ...response, risk: { ...response.risk, revision: "r1" } }, { model_id: "local:one" }))
      .toThrow(/risk view belongs to another revision/);
    expect(() => parseRevisionViews(response, { model_id: "local:one", notRevision: "r2" })).toThrow(/started from/);
    expect(() => parseRevisionViews(response, { model_id: "local:two" })).toThrow(/another model/);
    expect(() => parseRevisionViews({ ...response, report_data: { ...response.report_data, attackPaths: [] } }, { model_id: "local:one" }))
      .toThrow(/different models/);
  });

  it("reads the engine's r1 refresh: the same model before the save", () => {
    const request = revisions.refresh_r1.request;
    expect(request).toEqual({ ...contract.refresh_request, revision: "r1" });
    const views = parseRevisionViews(revisions.refresh_r1.response, { model_id: request.model_id, revision: request.revision });
    expect(views.risk.assessments[0].derived_risk).toEqual({ safety: 3, financial: 2, operational: 2, privacy: 1 });
  });

  it("builds exactly the contract's save request from the same review and ratings", () => {
    const context = parseReviewContext(contract.context.response, contextRequest);
    const draft = new RouteDraft(context.threat.id, context.route.id, context.revision);
    const review = contract.save.request.reviews[0];
    setReviewField(context, draft, review.assertion_id, "verdict", review.verdict);
    setReviewField(context, draft, review.assertion_id, "rationale", review.rationale);
    setReviewField(context, draft, review.assertion_id, "annotation", review.annotation);
    setFeasibility(context, draft, "path:a", "high");
    setImpact(context, draft, "risk:r", "privacy", "major");
    const plan = planSave(context, draft, REVIEW_MATRIX);
    expect(plan.problems).toEqual([]);
    expect(plan.request).toEqual(contract.save.request);
  });

  it("classifies every error example and keeps its fields and current revision", () => {
    const statuses: Record<string, number> = { validation_error: 422, permission_denied: 403, revision_conflict: 409, save_failure: 503 };
    const errors = contract.errors.map((example) => reviewErrorFromResponse(statuses[example.error.code], example));
    expect(errors.map((error) => error.kind)).toEqual(["validation", "permission", "conflict", "save_failure"]);
    expect(errors[0].details.fields).toEqual([{ field: "rationale", message: "Explain the review decision." }]);
    expect(errors[2].details.currentRevision).toBe("r2");
    expect(errors.every((error) => error instanceof ReviewApiError && error.message.length > 0)).toBe(true);
    expect(reviewErrorFromResponse(503, { error: { code: "workspace_failure", message: "Editable review sessions are not configured." } }).kind)
      .toBe("unavailable");
    expect(reviewErrorFromResponse(500, undefined)).toMatchObject({ kind: "unexpected", message: "The engine answered HTTP 500." });
  });
});
