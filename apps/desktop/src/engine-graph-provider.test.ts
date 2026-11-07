import { describe, expect, it, vi } from "vitest";
import {
  EngineGraphDataProvider,
  mapEngineGraphResponse,
  type EngineGraphResponse,
} from "./engine-graph-provider";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import { BOOKKEEPING_TYPES } from "./model-report";

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

describe("engine graph provider for the model views (#208)", () => {
  const withBookkeeping: EngineGraphResponse = {
    ...ENGINE_GRAPH,
    nodes: [
      ...ENGINE_GRAPH.nodes,
      { id: "assertion:x", domain_type: "Assertion", label: "Claim", properties: {} },
      { id: "party:reviewer", domain_type: "Party", label: "@reviewer", properties: {} },
    ],
    edges: [
      ...ENGINE_GRAPH.edges,
      {
        id: "relationship:assertion:x|subject|component:a",
        source: "assertion:x",
        target: "component:a",
        relationship_type: "subject",
        properties: {},
      },
    ],
  };
  const hidden = new Set(["Assertion", "Party"]);

  it("leaves hidden types, and every edge touching them, out of the graph pages", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(withBookkeeping));
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock, {
      hiddenDomainTypes: hidden,
    });
    const initial = await provider.getInitialGraph();
    const neighborhood = await provider.getNeighborhood("component:a");
    for (const page of [initial, neighborhood]) {
      expect(page.nodes.map((node) => node.domainType)).not.toContain("Assertion");
      expect(page.nodes.map((node) => node.domainType)).not.toContain("Party");
      expect(page.edges.map((edge) => edge.relationshipType)).not.toContain("subject");
    }
    // A node whose only other neighbour is hidden is not offered as expandable.
    expect(neighborhood.nodes.find((node) => node.id === "component:a")?.expandable).toBe(false);
  });

  // The Explore graph's start view on real model data (mvp-02, as the engine returns it).
  const mvp02Graph = (mvp02 as unknown as { graph: EngineGraphResponse }).graph;
  const exploreProvider = () => new EngineGraphDataProvider(
    "mvp-02-automotive-ecu.yaml",
    "http://engine.test",
    vi.fn<typeof fetch>().mockImplementation(async () => jsonResponse(mvp02Graph)),
    { hiddenDomainTypes: BOOKKEEPING_TYPES, initialView: "threats" },
  );

  it("opens on the threats and their neighbours, and leaves the rest of the model to expansion", async () => {
    const provider = exploreProvider();
    const initial = await provider.getInitialGraph();
    const whole = await provider.getWholeGraph();
    const types = new Set(initial.nodes.map((node) => node.domainType));
    // The story of the model, not a parts list: both threats, their paths, damage, risk and mitigations.
    expect(initial.nodes.filter((node) => node.domainType === "ThreatInstance")).toHaveLength(2);
    for (const type of ["AttackPath", "DamageScenario", "RiskScore", "Mitigation"]) expect(types).toContain(type);
    expect(initial.focusId).toMatch(/^threat-instance:/);
    expect(initial.nodes.length).toBeLessThan(whole.nodes.length);
    // Expansion is meaningful again: some loaded nodes have neighbours not yet shown,
    // and expanding one of them brings in objects the start view left out.
    const expandable = initial.nodes.filter((node) => node.expandable);
    expect(expandable.length).toBeGreaterThan(0);
    const shown = new Set(initial.nodes.map((node) => node.id));
    const path = expandable.find((node) => node.domainType === "AttackPath");
    expect(path).toBeDefined();
    const neighborhood = await provider.getNeighborhood(path?.id ?? "");
    expect(neighborhood.nodes.some((node) => !shown.has(node.id) && node.domainType === "AttackStep")).toBe(true);
    for (const page of [initial, neighborhood]) {
      expect(page.nodes.some((node) => BOOKKEEPING_TYPES.has(node.domainType))).toBe(false);
    }
  });

  it("falls back to a component's neighbourhood for a model without threats", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(withBookkeeping));
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock, {
      hiddenDomainTypes: hidden,
      initialView: "threats",
    });
    const initial = await provider.getInitialGraph();
    expect(initial.focusId).toBe("component:a");
    expect(initial.nodes.map((node) => node.id)).toEqual(["component:a", "component:b"]);
  });

  it("lists every visible node for Show whole model, with nothing left to expand", async () => {
    const whole = await exploreProvider().getWholeGraph();
    const visible = mvp02Graph.nodes.filter((node) => !BOOKKEEPING_TYPES.has(node.domain_type));
    expect(whole.nodes.map((node) => node.id).sort()).toEqual(visible.map((node) => node.id).sort());
    expect(whole.nodes.every((node) => !node.expandable)).toBe(true);
  });

  it("keeps the attack paths that did compute when one threat's request fails", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockImplementation(async (input) => {
      const url = new URL(String(input));
      if (url.pathname === "/graph") return jsonResponse(ENGINE_GRAPH);
      const goal = url.searchParams.get("goal");
      if (!goal) return jsonResponse({ file: ENGINE_GRAPH.file, threats: ["threat:ok", "threat:bad"], reviewed_threats: [], steps: 2 });
      if (goal === "threat:bad") return jsonResponse({ error: "cycle in precedes" }, 400);
      return jsonResponse({ file: ENGINE_GRAPH.file, goal, paths: [] });
    });
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock);
    const results = await provider.getAttackPathResults();
    expect(results.responses.map((response) => response.goal)).toEqual(["threat:ok"]);
    expect(results.failures).toEqual([{ goal: "threat:bad", message: "Engine request failed: cycle in precedes" }]);
  });

  it("reports one failure for every threat when the threat list itself fails", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockImplementation(async (input) => (
      new URL(String(input)).pathname === "/graph" ? jsonResponse(ENGINE_GRAPH) : jsonResponse({ error: "no such file" }, 400)
    ));
    const results = await new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock).getAttackPathResults();
    expect(results).toEqual({ responses: [], failures: [{ goal: null, message: "Engine request failed: no such file" }] });
  });

  it("hands the report the whole model, with nothing hidden, from one request", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(withBookkeeping));
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock, {
      hiddenDomainTypes: hidden,
    });
    const graph = await provider.getModelGraph();
    await provider.getInitialGraph();
    expect(graph.nodes).toHaveLength(6);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0][0])).toBe("http://engine.test/graph?file=model.yaml");
  });
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
