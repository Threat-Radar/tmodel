import { describe, expect, it } from "vitest";
import evidence from "./fixtures/review-evidence.json";
import { buildModelReport } from "./model-report";
import type { ModelReportInput } from "./model-types";
import { pathBannerText } from "./path-view";
import { relationshipReviewState } from "./review-status";
import { attackPathReviewState } from "./attack-path";
import { toCytoscapeEdgeElement } from "./graph-model";

const cases = evidence.cases as unknown as {
  name: string;
  human_reviewed: boolean;
  input: ModelReportInput;
  risk: { assessments: { path_reviewed: boolean }[] };
}[];

describe("engine human review evidence across app views", () => {
  it.each(cases)("keeps report, graph, path banner and risk aligned for $name", (fixture) => {
    const report = buildModelReport(fixture.input);
    const path = report.attackPaths[0];
    const edge = fixture.input.graph.edges.find((item) => item.source === "path:a"
      && item.relationship_type === "realizes_threat");
    if (!edge) throw new Error("Fixture relationship missing");
    const expected = fixture.human_reviewed;
    expect(report.threats[0].status.reviewed).toBe(expected);
    expect(path.status.reviewed).toBe(expected);
    expect(path.status.kind === "accepted").toBe(expected);
    expect(relationshipReviewState(edge.properties)?.kind === "accepted").toBe(expected);
    expect(pathBannerText(path).includes("a human reviewed this path and accepted it")).toBe(expected);
    expect(fixture.risk.assessments[0].path_reviewed).toBe(expected);
    expect(attackPathReviewState(fixture.input.attackPaths[0].paths[0].review).kind === "accepted")
      .toBe(expected);
    const styled = toCytoscapeEdgeElement({ ...edge, authored: false,
      relationshipType: edge.relationship_type });
    expect(styled.data.reviewState === "accepted").toBe(expected);
    expect(path.status.reviewers).not.toContain("agent");
    // Recorded verdicts remain available, including an agent's contrary opinion.
    expect(path.status.reviewStatus).toBe(edge.properties.review_status ?? null);
  });

  it("does not turn accepted status strings from an old snapshot into human acceptance", () => {
    const input = structuredClone(cases.find((item) => item.name === "agent_only")!.input);
    input.graph = { ...input.graph, edges: input.graph.edges.map((edge) => {
      const { human_reviewed: _reviewed, effective_assertion_status: _assertion,
        effective_review_status: _review, ...recorded } = edge.properties;
      return { ...edge, properties: recorded };
    }) };
    const report = buildModelReport(input);
    expect(report.attackPaths[0].status).toMatchObject({
      kind: "not_reviewed", reviewed: false, reviewStatus: "accepted",
    });
    expect(pathBannerText(report.attackPaths[0])).not.toContain("a human reviewed");
  });

  it("guards a stale accepted label when its effective reviewed flag is false", () => {
    const path = buildModelReport(cases.find((item) => item.human_reviewed)!.input).attackPaths[0];
    const stale = { ...path, status: { ...path.status, reviewed: false } };
    expect(pathBannerText(stale)).toContain("not shown as reviewed");
    expect(pathBannerText(stale)).not.toContain("a human reviewed");
  });
});
