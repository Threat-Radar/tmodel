import { describe, expect, it, vi } from "vitest";
import fixture from "./fixtures/risk-mvp-02.json";
import model from "./fixtures/report-input-mvp-02.json";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { buildModelReport } from "./model-report";
import type { ModelReportInput } from "./model-types";
import { parseRiskCalculation, renderRiskCalculation, RISK_MATRIX } from "./risk-calculation";
import { StaticPreviewApi } from "./static-api";

const file = "mvp-02-automotive-ecu.yaml";
const report = buildModelReport(model as unknown as ModelReportInput);

describe("engine risk calculation in the report (#63)", () => {
  it("requests an explicit matrix and preserves the engine's per-category results", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>(async () => new Response(JSON.stringify(fixture)));
    const provider = new EngineGraphDataProvider(file, "http://engine.test", fetch);
    const response = await provider.getRiskCalculation(RISK_MATRIX);
    expect(String(fetch.mock.calls[0][0])).toBe(
      `http://engine.test/risk?file=${file}&matrix=${RISK_MATRIX}`,
    );
    expect(response.assessments[0].derived_risk).toEqual({
      safety: 5, financial: 4, operational: 5, privacy: 1,
    });
    const rendered = renderRiskCalculation(response, report);
    expect(rendered).toContain("Safety: 5");
    expect(rendered).toContain("Financial: 4");
    expect(rendered).toContain("Privacy: 1");
    expect(rendered).toContain("Route 1");
    expect(rendered).toContain("informative profile");
    expect(rendered).toContain("does not approve a threat");
  });

  it("rejects a different model/profile, invalid vectors and inconsistent counts", () => {
    const invalid = [
      { ...fixture, file: "other.yaml" },
      { ...fixture, matrix: "unselected" },
      { ...fixture, count: 999 },
      { ...fixture, assessments: [{ ...fixture.assessments[0], derived_risk: { safety: 0 } }] },
    ];
    for (const response of invalid) {
      expect(() => parseRiskCalculation(response, file, RISK_MATRIX)).toThrow("invalid or mismatched");
    }
  });

  it("keeps missing route ratings unresolved without substituting zero or recorded risk", () => {
    const response = structuredClone(fixture);
    const assessment = response.assessments[0];
    Object.assign(assessment, {
      complete: false, feasibility: null, problems: ["route_rating_required"],
      derived_risk: { safety: null, financial: null, operational: null, privacy: null },
    });
    const rendered = renderRiskCalculation(parseRiskCalculation(response, file, RISK_MATRIX), report);
    expect(rendered).toContain("Incomplete");
    expect(rendered).toContain("Safety: Not calculated");
    expect(rendered).not.toContain("Safety: 0");
    expect(rendered).toContain("Unresolved input details");
    // Individual computed routes remain inspectable even when the aggregate is unresolved.
    expect(rendered).toContain("Route 1");
  });

  it("escapes model labels and problem text", () => {
    const altered = structuredClone(report);
    altered.threats[0].name = "<img src=x onerror=alert(1)>";
    const response = parseRiskCalculation(structuredClone(fixture), file, RISK_MATRIX);
    response.assessments[0].problems.push("<script>alert(1)</script>");
    response.assessments[0].complete = false;
    const rendered = renderRiskCalculation(parseRiskCalculation(response, file, RISK_MATRIX), altered);
    expect(rendered).not.toContain("<script>");
    expect(rendered).not.toContain("<img");
    expect(rendered).toContain("&lt;script&gt;");
  });

  it("shows both conflicting ratings and their sources without choosing a winner", () => {
    const response = parseRiskCalculation(structuredClone(fixture), file, RISK_MATRIX);
    const item = response.assessments[0];
    item.paths = [
      { id: "path:one", feasibility: "high", rating_source: "AttackPath.attack_feasibility", used_for_ratings: true, route_ids: [item.routes[0].id] },
      { id: "path:two", feasibility: "low", rating_source: "AttackPath.attack_feasibility", used_for_ratings: true, route_ids: [item.routes[0].id] },
    ];
    item.routes[0].rating_paths = ["path:one", "path:two"];
    item.routes[0].feasibility = null;
    item.routes[0].derived_risk = { safety: null, financial: null, operational: null, privacy: null };
    item.routes[0].problems = ["conflicting_route_ratings"];
    item.complete = false;
    item.feasibility = null;
    item.derived_risk = { safety: null, financial: null, operational: null, privacy: null };
    const rendered = renderRiskCalculation(response, report);
    expect(rendered).toContain("Conflicting recorded ratings");
    expect(rendered).toContain("Route feasibility: Not recorded");
    expect(rendered).toContain("Authored path: High");
    expect(rendered).toContain("Authored path: Low");
    expect(rendered).toContain("path:one · AttackPath.attack_feasibility");
    expect(rendered).toContain("path:two · AttackPath.attack_feasibility");
    expect(rendered).toContain("Safety: Not calculated");
  });

  it("distinguishes absent and incomplete assessments and retains their damage and stakeholder scope", () => {
    const response = parseRiskCalculation(structuredClone(fixture), file, RISK_MATRIX);
    const incomplete = response.assessments[0];
    incomplete.complete = false;
    incomplete.problems = ["missing_impact"];
    incomplete.for_stakeholder = "party:one";
    const absent = structuredClone(incomplete);
    absent.id = null;
    absent.damage_scenario = null;
    absent.threat_damage_scenario = incomplete.damage_scenario;
    absent.for_stakeholder = "party:two";
    response.assessments = [incomplete, absent];
    response.count = 2;
    const rendered = renderRiskCalculation(response, report);
    expect(rendered).toContain("Incomplete assessment");
    expect(rendered).toContain("Not assessed: no risk assessment recorded");
    expect(rendered).toContain("Assessment damage:");
    expect(rendered).toContain("Threat-linked damage:");
    expect(rendered).toContain("party:one");
    expect(rendered).toContain("party:two");
    expect(rendered).toContain(incomplete.id as string);
  });

  it("rejects missing rating sources rather than losing the conflict evidence", () => {
    const response = structuredClone(fixture);
    response.assessments[0].paths = [];
    expect(() => parseRiskCalculation(response, file, RISK_MATRIX)).toThrow("invalid or mismatched");
  });

  it("serves the same calculation through the static preview with no engine fallback", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>(async () => new Response(JSON.stringify(fixture)));
    const api = new StaticPreviewApi("https://example.test/data/", fetch);
    const provider = new EngineGraphDataProvider(file, api.engineBase, api.fetch);
    expect(await provider.getRiskCalculation(RISK_MATRIX)).toEqual(fixture);
    expect(String(fetch.mock.calls[0][0])).toBe(
      "https://example.test/data/models/mvp-02-automotive-ecu/risk.json",
    );
    const bad = await api.fetch(`${api.engineBase}risk?file=${file}&matrix=unknown`);
    expect(bad.status).toBe(400);
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});
