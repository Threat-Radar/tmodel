import { describe, expect, it, vi } from "vitest";
import {
  EngineGraphDataProvider,
  mapEngineGraphResponse,
  type EngineGraphResponse,
} from "./engine-graph-provider";

const ENGINE_GRAPH: EngineGraphResponse = {
  file: "/repo/spec/vectors/model.yaml",
  nodes: [
    { id: "component:a", domain_type: "Component", label: "A", properties: { description: "A" } },
    { id: "component:b", domain_type: "Component", label: "B", properties: {} },
    { id: "attack-step:one", domain_type: "AttackStep", label: "One", properties: {} },
    { id: "attack-step:two", domain_type: "AttackStep", label: "Two", properties: {} },
  ],
  edges: [
    {
      id: "relationship:component:a|uses_component|component:b",
      source: "component:a",
      target: "component:b",
      relationship_type: "uses_component",
      properties: {},
    },
    {
      id: "relationship:attack-step:one|precedes|attack-step:two",
      source: "attack-step:one",
      target: "attack-step:two",
      relationship_type: "precedes",
      properties: {},
    },
  ],
};

describe("engine graph provider", () => {
  it("maps engine snake-case DTOs without changing stable IDs or edge direction", () => {
    const original = structuredClone(ENGINE_GRAPH);
    const mapped = mapEngineGraphResponse(ENGINE_GRAPH);

    expect(mapped.nodes[0]).toMatchObject({
      id: "component:a",
      domainType: "Component",
      label: "A",
    });
    expect(mapped.edges[0]).toMatchObject({
      id: "relationship:component:a|uses_component|component:b",
      source: "component:a",
      target: "component:b",
      relationshipType: "uses_component",
    });
    expect(ENGINE_GRAPH).toEqual(original);
  });

  it("uses an engine graph response for initial focus and one-hop neighborhoods", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(ENGINE_GRAPH));
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock);

    const initial = await provider.getInitialGraph();
    const neighborhood = await provider.getNeighborhood("attack-step:one");

    expect(initial.focusId).toBe("component:a");
    expect(initial.nodes.map((node) => node.id)).toEqual(["component:a", "component:b"]);
    expect(initial.edges).toHaveLength(1);
    expect(neighborhood.nodes.map((node) => node.id)).toEqual([
      "attack-step:one",
      "attack-step:two",
    ]);
    expect(neighborhood.nodes.find((node) => node.id === "attack-step:one")?.expandable)
      .toBe(false);
    expect(neighborhood.edges[0]).toMatchObject({
      source: "attack-step:one",
      target: "attack-step:two",
      relationshipType: "precedes",
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0][0])).toBe("http://engine.test/graph?file=model.yaml");
  });

  it("calls the browser fetch function with its required global binding", async () => {
    const originalFetch = globalThis.fetch;
    const browserLikeFetch = vi.fn(function (this: typeof globalThis) {
      if (this !== globalThis) throw new TypeError("Illegal invocation");
      return Promise.resolve(jsonResponse(ENGINE_GRAPH));
    }) as unknown as typeof fetch;
    globalThis.fetch = browserLikeFetch;
    try {
      const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test");
      await expect(provider.getInitialGraph()).resolves.toMatchObject({ source: "engine" });
    } finally {
      globalThis.fetch = originalFetch;
    }
  });

  it("requests attack paths for every goal using the canonical file from the graph", async () => {
    const calls: URL[] = [];
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      const url = new URL(String(input));
      calls.push(url);
      if (url.pathname === "/graph") return jsonResponse(ENGINE_GRAPH);
      if (!url.searchParams.has("goal")) {
        return jsonResponse({
          file: ENGINE_GRAPH.file,
          threats: ["threat-instance:one", "threat-instance:two"],
          reviewed_threats: ["threat-instance:one"],
          steps: 2,
        });
      }
      const goal = url.searchParams.get("goal") ?? "";
      return jsonResponse({ file: ENGINE_GRAPH.file, goal, paths: [] });
    });
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock);

    const paths = await provider.getAttackPaths();

    expect(paths.map((response) => response.goal)).toEqual([
      "threat-instance:one",
      "threat-instance:two",
    ]);
    expect(calls.slice(1).every((url) => url.searchParams.get("file") === ENGINE_GRAPH.file)).toBe(true);
  });

  it("reports an engine client error instead of mixing in fixture data", async () => {
    const provider = new EngineGraphDataProvider(
      "../outside.yaml",
      "http://engine.test",
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(
        { error: "outside approved model directory" },
        400,
      )),
    );

    await expect(provider.getInitialGraph()).rejects.toThrow(
      "Engine request failed: outside approved model directory",
    );
  });

  it("evicts a failed /graph request so a later call can recover", async () => {
    const fetchMock = vi.fn<typeof fetch>()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce(jsonResponse({ error: "engine starting" }, 503))
      .mockResolvedValue(jsonResponse(ENGINE_GRAPH));
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock);

    await expect(provider.getInitialGraph()).rejects.toThrow("Failed to fetch");
    await expect(provider.getNeighborhood("component:a")).rejects.toThrow(
      "Engine request failed: engine starting",
    );
    await expect(provider.getInitialGraph()).resolves.toMatchObject({ focusId: "component:a" });
    await expect(provider.getNeighborhood("attack-step:one")).resolves.toMatchObject({
      focusId: "attack-step:one",
    });

    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("shares one in-flight /graph request between concurrent callers", async () => {
    let respond!: (response: Response) => void;
    const fetchMock = vi.fn<typeof fetch>(() => new Promise<Response>((resolve) => {
      respond = resolve;
    }));
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock);

    const initial = provider.getInitialGraph();
    const neighborhood = provider.getNeighborhood("component:b");
    respond(jsonResponse(ENGINE_GRAPH));
    await Promise.all([initial, neighborhood]);

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("shares one failed in-flight request without caching the failure", async () => {
    let fail!: (error: Error) => void;
    const fetchMock = vi.fn<typeof fetch>()
      .mockImplementationOnce(() => new Promise<Response>((_resolve, reject) => { fail = reject; }))
      .mockResolvedValue(jsonResponse(ENGINE_GRAPH));
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock);

    const first = provider.getInitialGraph();
    const second = provider.getInitialGraph();
    fail(new TypeError("Failed to fetch"));
    await expect(first).rejects.toThrow("Failed to fetch");
    await expect(second).rejects.toThrow("Failed to fetch");
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await expect(provider.getInitialGraph()).resolves.toMatchObject({ source: "engine" });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("passes Assertion and Review metadata through to frontend edges unchanged", () => {
    const graph: EngineGraphResponse = {
      ...ENGINE_GRAPH,
      edges: [{
        id: "relationship:attack-path:imds-pivot|realizes_threat|threat-instance:imds-pivot",
        source: "component:a",
        target: "component:b",
        relationship_type: "realizes_threat",
        properties: {
          assertion_ids: ["assertion:ai-imds-pivot-realizes"],
          assertion_status: "proposed",
          confidence: "low",
          review_ids: ["review:ai-triage"],
          review_status: "changes_requested",
        },
      }],
    };

    expect(mapEngineGraphResponse(graph).edges[0].properties).toEqual(graph.edges[0].properties);
  });
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
