import { describe, expect, it, vi } from "vitest";
import { CompatibleCoverageProvider } from "./coverage-provider";
import { REQUIREMENTS_GRAPH } from "./requirements-fixture.test-support";
import { EngineSdlDataProvider } from "./engine-sdl-provider";
import sdlFixture from "./fixtures/sdl-01-view.json";
import { StaticPreviewApi } from "./static-api";

describe("static preview API", () => {
  it("maps the existing read-only engine routes to Pages JSON without localhost", async () => {
    const seen: string[] = [];
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const url = new URL(String(input));
      seen.push(`${init?.method ?? "GET"} ${url.href}`);
      if (url.pathname.endsWith("/goals.json")) {
        return json({ goals: [{ goal: "threat:one", file: "goal-001.json" }] });
      }
      return json({ path: url.pathname });
    });
    const api = new StaticPreviewApi("https://threat-radar.github.io/tmodel/app/data/", fetchMock);

    await api.fetch(`${api.engineBase}models`);
    await api.fetch(`${api.engineBase}graph?file=mvp-01-software-doc-service.yaml`);
    await api.fetch(`${api.engineBase}attack-paths?file=mvp-01-software-doc-service.yaml`);
    await api.fetch(`${api.engineBase}attack-paths?file=mvp-01-software-doc-service.yaml&goal=threat%3Aone`);

    expect(seen).toEqual([
      "GET https://threat-radar.github.io/tmodel/app/data/models.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/graph.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/attack-paths/index.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/attack-paths/goals.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/attack-paths/goal-001.json",
    ]);
    expect(seen.join(" ")).not.toContain("127.0.0.1");
    expect(seen.join(" ")).not.toContain("localhost");
  });

  it("serves SDL from published data, with support for multiple programs", async () => {
    const file = "sdl-example.yaml";
    const listing = { models: [{ file, programs: [{ id: "program:one", name: "One" }] }] };
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      const path = new URL(String(input)).pathname;
      if (path.endsWith("/sdl/models.json")) return json(listing);
      if (path.endsWith("/sdl/sdl-example.json")) return json({ views: { "program:one": sdlFixture } });
      return json({ views: { "program:one": sdlFixture, "program:two": sdlFixture } });
    });
    const api = new StaticPreviewApi("https://example.test/tmodel/app/data/", fetchMock);
    const provider = new EngineSdlDataProvider(api.engineBase, api.fetch);
    await expect(provider.listModels()).resolves.toEqual(listing.models);
    await expect(provider.getView(file)).resolves.toEqual(sdlFixture);
    await expect(provider.getView("sdl-other.yaml", "program:two")).resolves.toEqual(sdlFixture);
    await expect(provider.getView("sdl-other.yaml")).rejects.toThrow("select an SDL program");
    await expect(provider.getView(file, "__proto__")).rejects.toThrow("unknown SDL program");
    expect(fetchMock.mock.calls.every(([url]) => String(url).startsWith("https://example.test/tmodel/app/data/sdl/")))
      .toBe(true);
  });

  it("rejects mutations and unsafe model paths without making a network request", async () => {
    const fetchMock = vi.fn<typeof fetch>();
    const api = new StaticPreviewApi("https://example.test/tmodel/app/data/", fetchMock);
    const mutation = await api.fetch(`${api.engineBase}models`, { method: "POST" });
    const escape = await api.fetch(`${api.engineBase}graph?file=..%2Fsecret.yaml`);

    expect(mutation.status).toBe(405);
    expect(await mutation.json()).toEqual({ error: "browser preview data is read-only" });
    expect(escape.status).toBe(400);
    const sdlEscape = await api.fetch(`${api.engineBase}sdl?file=..%2Fsecret.yaml`);
    expect(sdlEscape.status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("supports the Requirements coverage fallback without contacting localhost", async () => {
    const fetchMock = vi.fn<typeof fetch>();
    const api = new StaticPreviewApi("https://threat-radar.github.io/tmodel/app/data/", fetchMock);
    const provider = new CompatibleCoverageProvider(
      "mvp-02-automotive-ecu.yaml",
      { getModelGraph: vi.fn(async () => REQUIREMENTS_GRAPH) },
      api.engineBase,
      api.fetch,
    );

    const result = await provider.getCoverage("product:tcu");
    expect(result.source).toBe("frontend-fallback");
    expect(result.response.counts).toEqual({ satisfied: 1, in_progress: 0, unsatisfied: 1 });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

function json(value: unknown): Response {
  return new Response(JSON.stringify(value), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
