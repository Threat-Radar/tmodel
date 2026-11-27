import { describe, expect, it } from "vitest";
import contract from "../../../engine/examples/human-review/contract.json";
import { CompatibleCoverageProvider } from "./coverage-provider";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { parseRevisionViews } from "./review-contract";
import { CLOSED_VERSION_API, isProjectVersionLabel, projectVersionLabel, RevisionApi } from "./revision-api";

const views = parseRevisionViews(contract.save.response, { model_id: "local:one", revision: "r2" });

describe("project version views in memory", () => {
  it("labels a project version without a path separator and apart from example files", () => {
    const label = projectVersionLabel("local/one", "v002");
    expect(label).toBe("project:local%2Fone@v002");
    expect(isProjectVersionLabel(label)).toBe(true);
    expect(isProjectVersionLabel("mvp-01-software-doc-service.yaml")).toBe(false);
  });

  it("serves the version's graph, attack paths and risk to the existing providers", async () => {
    const label = projectVersionLabel("local:one", "r2");
    const api = new RevisionApi(label, views);
    const provider = new EngineGraphDataProvider(label, api.engineBase, api.fetch);
    expect((await provider.getModelGraph()).nodes).toHaveLength(10);
    const paths = await provider.getAttackPathResults();
    expect(paths.failures).toEqual([]);
    expect(paths.responses.map((response) => [response.goal, response.file])).toEqual([["threat:t", label]]);
    const risk = await provider.getRiskCalculation("annex-h-table-h8");
    expect(risk.assessments[0].derived_risk.safety).toBe(5);
    await expect(provider.getRiskCalculation("another-matrix")).rejects.toThrow();
  });

  it("answers nothing for another label, another route or a write, and never calls the engine", async () => {
    const api = new RevisionApi(projectVersionLabel("local:one", "r2"), views);
    const ask = (path: string, init?: RequestInit) => api.fetch(new URL(path, api.engineBase), init);
    expect((await ask("/graph?file=mvp-01-software-doc-service.yaml")).status).toBe(404);
    expect((await ask(`/tara?file=${encodeURIComponent(api.label)}`)).status).toBe(404);
    expect((await ask(`/graph?file=${encodeURIComponent(api.label)}`, { method: "POST" })).status).toBe(405);
    expect((await CLOSED_VERSION_API.fetch(new URL("/graph?file=x", CLOSED_VERSION_API.engineBase))).status).toBe(404);
  });

  it("lets requirements coverage fall back to the version's own graph", async () => {
    const label = projectVersionLabel("local:one", "r2");
    const api = new RevisionApi(label, views);
    const graph = new EngineGraphDataProvider(label, api.engineBase, api.fetch);
    // The example model has no Product: only the fallback, reading this version's graph, says so.
    await expect(new CompatibleCoverageProvider(label, graph, api.engineBase, api.fetch).getCoverage("product:none"))
      .rejects.toThrow("unknown product: product:none");
  });
});
