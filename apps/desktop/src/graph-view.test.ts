import { describe, expect, it, vi } from "vitest";
import type { AttackPathOption } from "./attack-path";
import { EngineGraphDataProvider, type EngineGraphResponse } from "./engine-graph-provider";
import { MAX_GRAPH_START_ATTEMPTS, connectGraphStartup } from "./graph-startup";
import {
  ProgressiveGraphLoader,
  type GraphLoadBatch,
  type GraphLoadResult,
} from "./graph-loader";
import type { GraphState } from "./graph-model";
import type { GraphDataProvider, GraphResponse } from "./graph-types";
import { KnowledgeGraphView } from "./graph-view";

const EMPTY_RESULT: GraphLoadResult = {
  canceled: false,
  insertedNodes: 0,
  insertedEdges: 0,
  pendingEdges: 0,
};

describe("knowledge-graph view request coordination", () => {
  it("ignores a stale neighborhood after selection changes and applies the newer expansion", async () => {
    const neighborhoods = new Map<string, Deferred<GraphResponse>>();
    const calls: string[] = [];
    const view = createView(async (nodeId) => {
      calls.push(nodeId);
      const pending = deferred<GraphResponse>();
      neighborhoods.set(nodeId, pending);
      return pending.promise;
    });

    const firstExpansion = view.expandSelection();
    view.handleSelection("component:new");
    const secondExpansion = view.expandSelection();
    neighborhoods.get("component:old")?.resolve(response("component:old"));
    await Promise.resolve();
    neighborhoods.get("component:new")?.resolve(response("component:new"));
    await Promise.all([firstExpansion, secondExpansion]);

    expect(calls).toEqual(["component:old", "component:new"]);
    expect(view.loadedFocusIds).toEqual(["component:new"]);
    expect(view.state.selectedNodeId).toBe("component:new");
  });

  it("cancels an in-flight stale expansion without aborting its replacement", async () => {
    const firstLoadStarted = deferred<void>();
    const seenSignals = new Map<string, AbortSignal>();
    const view = createView(async (nodeId) => response(nodeId));
    view.loadGraphResponse = async (graph, _runLayout, signal) => {
      if (!signal) throw new Error("Expected expansion cancellation signal");
      seenSignals.set(graph.focusId ?? "", signal);
      if (graph.focusId === "component:old") {
        firstLoadStarted.resolve();
        await new Promise<void>((resolve) => {
          signal.addEventListener("abort", () => resolve(), { once: true });
        });
        return { ...EMPTY_RESULT, canceled: true };
      }
      return EMPTY_RESULT;
    };

    const firstExpansion = view.expandSelection();
    await firstLoadStarted.promise;
    view.handleSelection("component:new");
    const secondExpansion = view.expandSelection();
    await Promise.all([firstExpansion, secondExpansion]);

    expect(seenSignals.get("component:old")?.aborted).toBe(true);
    expect(seenSignals.get("component:new")?.aborted).toBe(false);
    expect(view.state.selectedNodeId).toBe("component:new");
  });

  it("reports a current expansion failure without changing graph state", async () => {
    const view = createView(async () => {
      throw new Error("engine unavailable");
    });
    const before = structuredClone(view.state);

    await expect(view.expandSelection()).resolves.toBeUndefined();

    expect(view.state).toEqual(before);
    expect(view.element("graph-loading")).toMatchObject({
      hidden: false,
      textContent: "Unable to expand neighborhood: engine unavailable",
    });
  });

  it("lets only the latest path selection publish and clearing invalidates older work", async () => {
    const delayed = new Map<string, Deferred<GraphResponse>>();
    const calls: string[] = [];
    const view = createView(async (nodeId) => {
      calls.push(nodeId);
      if (nodeId === "attack-step:slow") {
        const pending = deferred<GraphResponse>();
        delayed.set(nodeId, pending);
        return pending.promise;
      }
      return response(nodeId);
    });
    const slow = pathOption("slow", "attack-step:slow");
    const fast = pathOption("fast", "attack-step:fast");
    view.availableAttackPaths = [slow, fast];

    const slowSelection = view.selectAttackPath(slow.id);
    const fastSelection = view.selectAttackPath(fast.id);
    await fastSelection;
    delayed.get("attack-step:slow")?.resolve(response("attack-step:slow"));
    await slowSelection;

    expect(view.activeAttackPath?.id).toBe("fast");
    expect(calls).toEqual(["attack-step:slow", "attack-step:fast"]);

    const clearingSelection = view.selectAttackPath(slow.id);
    view.clearAttackPath();
    delayed.get("attack-step:slow")?.resolve(response("attack-step:slow"));
    await clearingSelection;
    expect(view.activeAttackPath).toBeUndefined();
  });

  it("restores the active selector and highlight status when path loading fails", async () => {
    const view = createView(async () => {
      throw new Error("request failed");
    });
    const active = pathOption("active", "attack-step:fast");
    const failed = pathOption("failed", "attack-step:slow");
    view.availableAttackPaths = [active, failed];
    view.activeAttackPath = active;
    view.element("attack-path-select").value = failed.id;

    await expect(view.selectAttackPath(failed.id)).resolves.toBeUndefined();

    expect(view.activeAttackPath).toBe(active);
    expect(view.element("attack-path-select").value).toBe(active.id);
    expect(view.element("attack-path-status").textContent).toContain(
      "Unable to load selected attack path: request failed",
    );
  });

  it("does not let a stale failed path request overwrite a newer selection", async () => {
    const slow = rejectedDeferred<GraphResponse>();
    const view = createView(async (nodeId) => {
      if (nodeId === "attack-step:slow") return slow.promise;
      return response(nodeId);
    });
    const stale = pathOption("stale", "attack-step:slow");
    const current = pathOption("current", "attack-step:fast");
    view.availableAttackPaths = [stale, current];

    const staleSelection = view.selectAttackPath(stale.id);
    view.element("attack-path-select").value = current.id;
    await view.selectAttackPath(current.id);
    slow.reject(new Error("stale failure"));
    await staleSelection;

    expect(view.activeAttackPath).toBe(current);
    expect(view.element("attack-path-select").value).toBe(current.id);
    const status = view.element("attack-path-status") as {
      classList: { contains(name: string): boolean };
    };
    expect(status.classList.contains("is-error")).toBe(false);
  });

  it("keeps multi-batch expansion and path selection from canceling each other", async () => {
    const view = createView(async (nodeId) => response(nodeId));
    const loader = new TwoBatchLoader();
    const internals = view as ViewHarness & {
      loader: TwoBatchLoader;
      cy: unknown;
      appendNodeList(): void;
      setLoadingProgress(message: string): void;
    };
    Object.defineProperty(internals, "loader", { value: loader });
    internals.cy = fakeCytoscape();
    internals.appendNodeList = () => undefined;
    internals.setLoadingProgress = () => undefined;
    internals.loadGraphResponse = KnowledgeGraphView.prototype["loadGraphResponse"].bind(internals);
    const path = pathOption("path", "attack-step:fast");
    internals.availableAttackPaths = [path];
    internals.element("attack-path-select").value = path.id;

    const expansion = internals.expandSelection();
    await waitFor(() => loader.hasCall("component:old"));
    const pathSelection = internals.selectAttackPath(path.id);
    await waitFor(() => loader.hasCall("attack-step:fast"));

    expect(loader.signalFor("component:old")?.aborted).toBe(false);
    expect(loader.signalFor("attack-step:fast")?.aborted).toBe(false);
    loader.release("component:old");
    loader.release("attack-step:fast");
    await Promise.all([expansion, pathSelection]);

    expect(internals.activeAttackPath).toBe(path);
    expect(loader.completedFocusIds).toEqual(["component:old", "attack-step:fast"]);
  });

  it("refreshes expandable metadata for an already loaded selected node", async () => {
    const view = createView(async (nodeId) => ({
      source: "engine",
      focusId: nodeId,
      nodes: [{ ...node(nodeId), expandable: false }],
      edges: [],
    }));
    const internals = view as ViewHarness & {
      loader: ProgressiveGraphLoader;
      cy: unknown;
      appendNodeList(): void;
      runGraphLayout(): void;
      setLoadingProgress(message: string): void;
    };
    const loader = new ProgressiveGraphLoader({ schedule: async () => Promise.resolve() });
    Object.defineProperty(internals, "loader", { value: loader });
    internals.cy = fakeCytoscape();
    internals.appendNodeList = () => undefined;
    internals.runGraphLayout = () => undefined;
    internals.setLoadingProgress = () => undefined;
    internals.loadGraphResponse = KnowledgeGraphView.prototype["loadGraphResponse"].bind(internals);
    await loader.load({
      source: "engine",
      nodes: [{ ...node("component:old"), expandable: true }],
      edges: [],
    }, () => undefined);

    expect(view.state.nodes.find((item) => item.id === "component:old")?.expandable).toBe(true);
    await view.expandSelection();

    expect(view.state.nodes.find((item) => item.id === "component:old")?.expandable).toBe(false);
  });

  it("shows progress when a small page activates more than one batch of pending edges", async () => {
    const messages: string[] = [];
    const view = createView(async (nodeId) => response(nodeId));
    const internals = view as ViewHarness & {
      loader: ProgressiveGraphLoader;
      cy: unknown;
      appendNodeList(): void;
      setLoadingProgress(message: string): void;
    };
    const pendingEdges = Array.from({ length: 201 }, (_, index) => ({
      id: `pending:${index}`,
      source: "component:0",
      target: "component:1",
      relationshipType: "uses_component",
      properties: {},
    }));
    await internals.loader.load(
      { source: "engine", nodes: [], edges: pendingEdges },
      () => undefined,
    );
    internals.cy = { batch: (callback: () => void) => callback(), add: () => undefined };
    internals.appendNodeList = () => undefined;
    internals.setLoadingProgress = (message) => { messages.push(message); };

    await KnowledgeGraphView.prototype["loadGraphResponse"].call(
      internals,
      {
        source: "engine",
        nodes: [node("component:0"), node("component:1")],
        edges: [],
      },
      false,
    );

    expect(messages).toContain("Loading graph… 0 of 203");
    expect(messages).toContain("Loading graph… 203 of 203");
    expect(messages[messages.length - 1]).toBe("");
  });
});

describe("knowledge-graph incremental layout", () => {
  it("preserves existing positions and viewport after neighborhood expansion", async () => {
    const view = createView(async () => ({
      source: "engine",
      focusId: "component:old",
      nodes: [node("component:added")],
      edges: [{
        id: "relationship:old-added",
        source: "component:old",
        target: "component:added",
        relationshipType: "composed_of",
        properties: {},
      }],
    }));
    const { cy, positions, viewport } = installIncrementalLayoutHarness(view);
    view.loadGraphResponse = async (graph) => {
      addGraphResponseToHarness(view, cy, graph);
      return { ...EMPTY_RESULT, insertedNodes: 1, insertedEdges: 1 };
    };

    await view.expandSelection();

    expect(previousPositions(cy, view.initialNodeIds)).toEqual(positions);
    expect({ pan: cy.pan(), zoom: cy.zoom() }).toEqual(viewport);
    expect(cy.layoutOptions).toMatchObject({ name: "cose", randomize: false, fit: false });
    expect(cy.node("component:old").locked()).toBe(false);
  });

  it("preserves existing positions when an attack path introduces a node", async () => {
    const stepId = "attack-step:added";
    const view = createView(async () => ({
      source: "engine",
      focusId: stepId,
      nodes: [node(stepId)],
      edges: [{
        id: "relationship:old-step",
        source: "component:old",
        target: stepId,
        relationshipType: "steps",
        properties: {},
      }],
    }));
    const { cy, positions, viewport } = installIncrementalLayoutHarness(view);
    const option = pathOption("new-path", stepId);
    view.availableAttackPaths = [option];
    view.loadGraphResponse = async (graph) => {
      addGraphResponseToHarness(view, cy, graph);
      return { ...EMPTY_RESULT, insertedNodes: 1, insertedEdges: 1 };
    };

    await view.selectAttackPath(option.id);

    expect(previousPositions(cy, view.initialNodeIds)).toEqual(positions);
    expect({ pan: cy.pan(), zoom: cy.zoom() }).toEqual(viewport);
    expect(view.activeAttackPath).toBe(option);
  });

  it("does not recalculate layout when switching loaded paths or clearing", async () => {
    const view = createView(async (nodeId) => response(nodeId));
    const first = pathOption("first", "attack-step:slow");
    const second = pathOption("second", "attack-step:fast");
    view.availableAttackPaths = [first, second];
    let layoutCalls = 0;
    view.runIncrementalGraphLayout = () => { layoutCalls += 1; };

    await view.selectAttackPath(first.id);
    await view.selectAttackPath(second.id);
    view.clearAttackPath();

    expect(layoutCalls).toBe(0);
  });

  it("places expanded nodes clear of every loaded node and label without moving them", async () => {
    const added = ["component:a1", "component:a2", "component:a3", "component:a4"];
    const view = createView(async () => ({
      source: "engine",
      focusId: "component:old",
      nodes: added.map(node),
      edges: added.map((id) => ({
        id: `relationship:old-${id}`,
        source: "component:old",
        target: id,
        relationshipType: "composed_of",
        properties: {},
      })),
    }));
    const { cy, positions, viewport } = installIncrementalLayoutHarness(view);
    view.loadGraphResponse = async (graph) => {
      // New elements arrive stacked on the existing ones, as Cytoscape adds them.
      addGraphResponseToHarness(view, cy, graph, { x: 20, y: 40 });
      return { ...EMPTY_RESULT, insertedNodes: graph.nodes.length, insertedEdges: graph.edges.length };
    };

    await view.expandSelection();

    expect(previousPositions(cy, view.initialNodeIds)).toEqual(positions);
    expect({ pan: cy.pan(), zoom: cy.zoom() }).toEqual(viewport);
    const boxes = cy.nodes().items.map((item) => ({ id: item.id(), box: item.boundingBox() }));
    for (const id of added) {
      const own = boxes.find((entry) => entry.id === id)?.box;
      if (!own) throw new Error(`Missing ${id}`);
      const overlapping = boxes.filter((entry) => entry.id !== id && boxesOverlap(own, entry.box));
      expect(overlapping.map((entry) => entry.id)).toEqual([]);
    }
  });

  it("keeps every position fixed across repeated path switching and clearing", async () => {
    const stepId = "attack-step:added";
    const view = createView(async () => ({
      source: "engine",
      focusId: stepId,
      nodes: [node(stepId)],
      edges: [{
        id: "relationship:old-step",
        source: "component:old",
        target: stepId,
        relationshipType: "steps",
        properties: {},
      }],
    }));
    const { cy } = installIncrementalLayoutHarness(view);
    const first = pathOption("first", stepId);
    const second = pathOption("second", "attack-step:fast");
    view.availableAttackPaths = [first, second];
    view.loadGraphResponse = async (graph) => {
      const before = cy.nodes().length;
      addGraphResponseToHarness(view, cy, graph);
      return { ...EMPTY_RESULT, insertedNodes: cy.nodes().length - before };
    };

    await view.selectAttackPath(first.id);
    const settled = previousPositions(cy, new Set(view.state.nodes.map((item) => item.id)));
    const settledViewport = { pan: cy.pan(), zoom: cy.zoom() };
    for (let round = 0; round < 3; round += 1) {
      await view.selectAttackPath(second.id);
      await view.selectAttackPath(first.id);
    }
    view.clearAttackPath();

    expect(previousPositions(cy, new Set(Object.keys(settled)))).toEqual(settled);
    expect({ pan: cy.pan(), zoom: cy.zoom() }).toEqual(settledViewport);
  });

  it("restores temporary locks after completion without unlocking intentional locks", () => {
    const view = createView(async (nodeId) => response(nodeId));
    const { cy } = installIncrementalLayoutHarness(view, true);
    const intentionallyLocked = cy.node("component:new");
    intentionallyLocked.lock();
    cy.addNode("component:added", { x: 0, y: 0 });
    view.state = {
      ...view.state,
      nodes: [...view.state.nodes, node("component:added")],
      edges: [{
        id: "relationship:old-added",
        source: "component:old",
        target: "component:added",
        relationshipType: "composed_of",
        properties: {},
      }],
    };

    view.runIncrementalGraphLayout(view.initialNodeIds, "component:old");

    expect(cy.node("component:old").locked()).toBe(false);
    expect(intentionallyLocked.locked()).toBe(true);
  });

  it("releases temporary locks when an incremental layout is interrupted", () => {
    const view = createView(async (nodeId) => response(nodeId));
    const { cy, viewport } = installIncrementalLayoutHarness(view, false);
    const intentionallyLocked = cy.node("component:new");
    intentionallyLocked.lock();
    cy.addNode("component:added", { x: 0, y: 0 });
    view.state = {
      ...view.state,
      nodes: [...view.state.nodes, node("component:added")],
      edges: [{
        id: "relationship:old-added",
        source: "component:old",
        target: "component:added",
        relationshipType: "composed_of",
        properties: {},
      }],
    };

    view.runIncrementalGraphLayout(view.initialNodeIds, "component:old");
    expect(cy.node("component:old").locked()).toBe(true);
    view.stopIncrementalLayout();

    expect(cy.node("component:old").locked()).toBe(false);
    expect(intentionallyLocked.locked()).toBe(true);
    expect({ pan: cy.pan(), zoom: cy.zoom() }).toEqual(viewport);
  });
});

describe("knowledge-graph startup and recovery", () => {
  it("does not recreate Cytoscape or listeners when start is retried", async () => {
    let initialCalls = 0;
    const { view, document } = createDomView({
      getInitialGraph: async () => {
        initialCalls += 1;
        if (initialCalls === 1) throw new Error("Engine request failed: HTTP 503");
        return startupGraph();
      },
    });

    await expect(view.start()).rejects.toThrow("HTTP 503");
    expect(view.renderGraphCalls).toBe(0);
    document.byId("data-source-notice").classList.add("is-error");

    await view.start();
    await view.start();

    expect(view.renderGraphCalls).toBe(1);
    expect(view.state.nodes.map((item) => item.id)).toEqual([
      "attack-path:imds-pivot",
      "threat-instance:imds-pivot",
    ]);
    expect(document.byId("data-source-notice").classList.contains("is-error")).toBe(false);
    expect(document.byId("data-source-notice").textContent).toBe("Engine model data");
  });

  it("keeps the loaded graph usable when attack-path discovery fails", async () => {
    const { view, document } = createDomView({
      getAttackPaths: async () => {
        throw new Error("Engine request failed: cannot read model");
      },
    });

    await expect(view.start()).resolves.toBeUndefined();

    expect(view.state.selectedNodeId).toBe("attack-path:imds-pivot");
    expect(document.byId("inspector-label").textContent).toBe("IMDS pivot path");
    expect(document.byId("expand-node").disabled).toBe(false);
    const status = document.byId("attack-path-status");
    expect(status.textContent).toBe("Unable to load attack paths: Engine request failed: cannot read model");
    expect(status.classList.contains("is-error")).toBe(true);
    expect(document.byId("attack-path-select").disabled).toBe(true);
    expect(document.byId("data-source-notice").classList.contains("is-error")).toBe(false);

    view.handleSelection("threat-instance:imds-pivot");
    expect(document.byId("inspector-label").textContent).toBe("IMDS pivot threat");
  });

  it("shows assertion and review status for a relationship in the inspector", async () => {
    const { view, document } = createDomView();
    await view.start();

    const item = document.byId("relationship-list").children[0];
    expect(item.classList.contains("review-changes_requested")).toBe(true);
    expect(item.textContent).toContain("→ realizes_threat");
    expect(item.textContent).toContain("Changes Requested");
    expect(item.textContent).toContain(
      "assertion_status: proposed · review_status: changes_requested",
    );
    expect(item.textContent).toContain("assertion:ai-imds-pivot-realizes · review:ai-triage");
  });

  it("leaves structural relationships in the inspector without review badges", async () => {
    const { view, document } = createDomView({
      getInitialGraph: async () => ({
        ...startupGraph(),
        edges: [{ ...startupGraph().edges[0], relationshipType: "steps", properties: {} }],
      }),
    });
    await view.start();

    const item = document.byId("relationship-list").children[0];
    expect(item.textContent).toBe("→ stepsIMDS pivot threat");
    expect(item.className).toBe("relationship-item");
  });

  it("renders an Other node-type entry and every relationship review state in the legends", async () => {
    const { view, document } = createDomView();
    view.renderLegend();

    expect(document.byId("type-legend").textContent).toContain("Other types");
    const relationshipLegend = document.byId("relationship-legend");
    expect(relationshipLegend.textContent).toBe(
      "StructuralAcceptedProposedChanges RequestedRejectedUnknown Status",
    );
    // A divider, not a heading, separates the groups; every state keeps a
    // line marker and a tooltip naming it as a relationship review status.
    const [divider, ...states] = relationshipLegend.children;
    expect(divider.className).toBe("legend-divider");
    expect(divider.attributes.get("aria-hidden")).toBe("true");
    expect(states.map((item) => item.children[0].tagName)).toEqual(Array(6).fill("svg"));
    expect(states.slice(1).map((item) => (item as unknown as { title: string }).title)).toEqual([
      "Relationship review status: Accepted",
      "Relationship review status: Proposed",
      "Relationship review status: Changes Requested",
      "Relationship review status: Rejected",
      "Relationship review status: Unknown Status",
    ]);
  });

  it("never gives a rejected or changes-requested path the reviewed banner style", async () => {
    const { view, document } = createDomView();
    const status = document.byId("attack-path-status");
    const option = (assertion: string, review: string | null, reviewed: boolean): AttackPathOption => ({
      ...pathOption("p", "attack-step:a"),
      result: {
        steps: ["attack-step:a"],
        goal_step: "attack-step:a",
        review: { reviewed, assertion_status: assertion, review_status: review },
      },
    });

    view.renderAttackPathStatus(option("accepted", "rejected", true));
    expect(status.classList.contains("is-reviewed")).toBe(false);
    expect(status.classList.contains("is-negative")).toBe(true);
    expect(status.textContent).toContain("rejected, not accepted");

    view.renderAttackPathStatus(option("proposed", "changes_requested", false));
    expect(status.classList.contains("is-negative")).toBe(true);
    expect(status.textContent).toContain("changes requested, not accepted");

    view.renderAttackPathStatus(option("accepted", "accepted", true));
    expect(status.classList.contains("is-reviewed")).toBe(true);
    expect(status.classList.contains("is-negative")).toBe(false);
  });
});

describe("manual graph retry after automatic attempts are used up", () => {
  const CONNECTED = {
    kind: "connected",
    health: { status: "ok", engine: "tmodel-engine", version: "0.1.0" },
  } as const;
  const ENGINE_GRAPH: EngineGraphResponse = {
    file: "/repo/spec/vectors/model.yaml",
    nodes: [
      { id: "component:a", domain_type: "Component", label: "A", properties: {} },
      { id: "component:b", domain_type: "Component", label: "B", properties: {} },
    ],
    edges: [{
      id: "relationship:component:a|uses_component|component:b",
      source: "component:a",
      target: "component:b",
      relationship_type: "uses_component",
      properties: {},
    }],
  };

  function recoveryHarness() {
    let graphResponses: Array<() => Response> = [];
    const graphRequests = vi.fn();
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      const url = new URL(String(input));
      if (url.pathname === "/attack-paths") {
        return jsonResponse({ file: ENGINE_GRAPH.file, threats: [], reviewed_threats: [], steps: 0 });
      }
      graphRequests();
      const next = graphResponses.shift();
      return next ? next() : jsonResponse(ENGINE_GRAPH);
    });
    const provider = new EngineGraphDataProvider("model.yaml", "http://engine.test", fetchMock);
    const { view, document } = createDomView({
      getInitialGraph: () => provider.getInitialGraph(),
      getNeighborhood: (id) => provider.getNeighborhood(id),
      getAttackPaths: () => provider.getAttackPaths(),
    });
    const notice = document.byId("data-source-notice");
    const retryButton = document.createElement("button");
    retryButton.hidden = true;
    const startup = connectGraphStartup(
      () => view.start(),
      true,
      {
        notice: notice as unknown as HTMLElement,
        retryButton: retryButton as unknown as HTMLButtonElement,
      },
      () => undefined,
    );
    const failGraph = (count: number) => {
      graphResponses = Array.from({ length: count }, () => () => jsonResponse(
        { error: "cannot read model" },
        400,
      ));
    };
    const click = () => (retryButton.onclick as () => void)();
    return { view, notice, retryButton, startup, graphRequests, failGraph, click };
  }

  it("recovers on Retry graph without a reload, once, and cleans up the error state", async () => {
    const { view, notice, retryButton, startup, graphRequests, failGraph, click } = recoveryHarness();
    failGraph(MAX_GRAPH_START_ATTEMPTS);

    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS + 5; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }
    expect(graphRequests).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS);
    expect(view.renderGraphCalls).toBe(0);
    expect(notice.classList.contains("is-error")).toBe(true);
    expect(notice.textContent).toBe(
      "Unable to load the knowledge graph: Engine request failed: cannot read model. Use Retry graph to try again.",
    );
    expect(retryButton).toMatchObject({ hidden: false, disabled: false });

    // The /graph problem is fixed while the engine stays healthy.
    click();
    expect(retryButton).toMatchObject({ hidden: true, disabled: true });
    click();
    await startup.retryNow();

    expect(graphRequests).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);
    expect(startup.started).toBe(true);
    expect(view.renderGraphCalls).toBe(1);
    expect(view.state.nodes.map((item) => item.id)).toEqual(["component:a", "component:b"]);
    expect(view.state.edges).toHaveLength(1);
    expect(notice.classList.contains("is-error")).toBe(false);
    expect(notice.textContent).toBe("Engine model data from model.yaml");
    expect(retryButton).toMatchObject({ hidden: true, disabled: true });

    for (let poll = 0; poll < 3; poll += 1) await startup.engineStateChanged(CONNECTED);
    await startup.retryNow();
    expect(graphRequests).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 1);
    expect(view.renderGraphCalls).toBe(1);
    expect(view.state.nodes).toHaveLength(2);
  });

  it("reports a failed manual retry and lets the user try again", async () => {
    const { view, notice, retryButton, startup, graphRequests, failGraph, click } = recoveryHarness();
    failGraph(MAX_GRAPH_START_ATTEMPTS + 1);
    for (let poll = 0; poll < MAX_GRAPH_START_ATTEMPTS; poll += 1) {
      await startup.engineStateChanged(CONNECTED);
    }

    click();
    expect(notice.textContent).toBe("Retrying the knowledge graph…");
    await startup.retryNow();
    expect(startup.started).toBe(false);
    expect(notice.classList.contains("is-error")).toBe(true);
    expect(notice.textContent).toContain("cannot read model. Use Retry graph to try again.");
    expect(retryButton).toMatchObject({ hidden: false, disabled: false });

    click();
    await startup.retryNow();
    expect(startup.started).toBe(true);
    expect(graphRequests).toHaveBeenCalledTimes(MAX_GRAPH_START_ATTEMPTS + 2);
    expect(view.renderGraphCalls).toBe(1);
    expect(retryButton.hidden).toBe(true);
  });
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

interface ViewHarness {
  state: GraphState;
  availableAttackPaths: AttackPathOption[];
  activeAttackPath?: AttackPathOption;
  initialNodeIds: ReadonlySet<string>;
  loadedFocusIds: string[];
  handleSelection(nodeId: string): void;
  expandSelection(): Promise<void>;
  selectAttackPath(optionId: string): Promise<void>;
  clearAttackPath(): void;
  runIncrementalGraphLayout(previousNodeIds: ReadonlySet<string>, anchorId?: string): void;
  stopIncrementalLayout(): void;
  element(id: string): Record<string, unknown>;
  loadGraphResponse(
    graph: GraphResponse,
    runLayout?: boolean,
    signal?: AbortSignal,
  ): Promise<GraphLoadResult | undefined>;
}

function createView(
  getNeighborhood: (nodeId: string) => Promise<GraphResponse>,
): ViewHarness {
  const elements = new Map<string, Record<string, unknown>>([
    ["attack-path-select", { value: "" }],
    ["clear-attack-path", { disabled: false }],
    ["attack-path-status", fakeElement()],
    ["graph-loading", { hidden: true, textContent: "" }],
    ["node-count", { textContent: "0" }],
  ]);
  const fakeDocument = {
    getElementById: (id: string) => elements.get(id) ?? null,
  } as unknown as Document;
  const provider: GraphDataProvider = {
    metadata: { source: "engine", label: "Test", notice: "Test data" },
    getInitialGraph: async () => response("component:old"),
    getNeighborhood,
    getAttackPaths: async () => [],
  };
  const instance = new KnowledgeGraphView(provider, fakeDocument) as unknown as ViewHarness & {
    cy: unknown;
    renderInspector(): void;
    renderAttackPathStatus(): void;
    applyAttackPathHighlight(): void;
  };
  instance.state = {
    nodes: [
      { ...node("component:old"), expandable: true },
      node("component:new"),
      node("attack-step:slow"),
      node("attack-step:fast"),
    ],
    edges: [],
    selectedNodeId: "component:old",
  };
  instance.cy = {
    getElementById: () => ({ select: () => undefined, unselect: () => undefined }),
  };
  instance.renderInspector = () => undefined;
  instance.renderAttackPathStatus = () => undefined;
  instance.applyAttackPathHighlight = () => undefined;
  instance.element = (id: string) => {
    const element = elements.get(id);
    if (!element) throw new Error(`Missing test element ${id}`);
    return element;
  };
  instance.loadedFocusIds = [];
  instance.initialNodeIds = new Set(instance.state.nodes.map((item) => item.id));
  instance.loadGraphResponse = async (graph) => {
    instance.loadedFocusIds.push(graph.focusId ?? "");
    return EMPTY_RESULT;
  };
  return instance;
}

function installIncrementalLayoutHarness(view: ViewHarness, finishOnRun = true) {
  const cy = new FakeLayoutCore(finishOnRun);
  let offset = 0;
  for (const item of view.state.nodes) {
    cy.addNode(item.id, { x: 20 + offset, y: 40 + offset });
    offset += 25;
  }
  const positions = previousPositions(cy, view.initialNodeIds);
  const viewport = { pan: cy.pan(), zoom: cy.zoom() };
  (view as ViewHarness & { cy: unknown }).cy = cy;
  return { cy, positions, viewport };
}

function addGraphResponseToHarness(
  view: ViewHarness,
  cy: FakeLayoutCore,
  graph: GraphResponse,
  at = { x: 0, y: 0 },
): void {
  for (const item of graph.nodes) {
    if (!view.state.nodes.some((existing) => existing.id === item.id)) {
      view.state = { ...view.state, nodes: [...view.state.nodes, item] };
      cy.addNode(item.id, at);
    }
  }
  view.state = { ...view.state, edges: [...view.state.edges, ...graph.edges] };
  cy.edgeCount = view.state.edges.length;
}

function previousPositions(
  cy: FakeLayoutCore,
  ids: ReadonlySet<string>,
): Record<string, { x: number; y: number }> {
  return Object.fromEntries([...ids].map((id) => [id, cy.node(id).position()]));
}

class FakeLayoutNode {
  readonly length = 1;

  constructor(
    private readonly nodeId: string,
    private coordinates: { x: number; y: number },
    private isLocked = false,
  ) {}

  id(): string { return this.nodeId; }
  position(next?: { x: number; y: number }): { x: number; y: number } {
    if (next) this.coordinates = { ...next };
    return { ...this.coordinates };
  }
  locked(): boolean { return this.isLocked; }
  lock(): this { this.isLocked = true; return this; }
  unlock(): this { this.isLocked = false; return this; }
  width(): number { return 28; }
  // A 28px node with a wrapped label below it, as drawn by the real style.
  boundingBox(): { x1: number; y1: number; x2: number; y2: number; w: number; h: number } {
    const { x, y } = this.coordinates;
    return { x1: x - 38, y1: y - 15, x2: x + 38, y2: y + 45, w: 76, h: 60 };
  }
}

function boxesOverlap(
  a: { x1: number; y1: number; x2: number; y2: number },
  b: { x1: number; y1: number; x2: number; y2: number },
): boolean {
  return Math.min(a.x2, b.x2) > Math.max(a.x1, b.x1) && Math.min(a.y2, b.y2) > Math.max(a.y1, b.y1);
}

class FakeLayoutNodeCollection {
  constructor(readonly items: FakeLayoutNode[]) {}

  get length(): number { return this.items.length; }
  filter(predicate: (node: FakeLayoutNode) => boolean): FakeLayoutNodeCollection {
    return new FakeLayoutNodeCollection(this.items.filter(predicate));
  }
  forEach(callback: (node: FakeLayoutNode, index: number) => void): void {
    this.items.forEach(callback);
  }
  lock(): this { this.items.forEach((item) => item.lock()); return this; }
  unlock(): this { this.items.forEach((item) => item.unlock()); return this; }
  boundingBox(): { x1: number; y1: number; x2: number; y2: number } {
    const positions = this.items.map((item) => item.position());
    return {
      x1: Math.min(...positions.map((position) => position.x)),
      y1: Math.min(...positions.map((position) => position.y)),
      x2: Math.max(...positions.map((position) => position.x)),
      y2: Math.max(...positions.map((position) => position.y)),
    };
  }
  shift(delta: { x: number; y: number }): this {
    this.items.forEach((item) => {
      const position = item.position();
      item.position({ x: position.x + delta.x, y: position.y + delta.y });
    });
    return this;
  }
}

class FakeLayoutCore {
  private readonly nodeMap = new Map<string, FakeLayoutNode>();
  private panValue = { x: 37, y: 53 };
  private zoomValue = 1.6;
  edgeCount = 0;
  layoutOptions?: Record<string, unknown>;

  constructor(private readonly finishOnRun: boolean) {}

  addNode(id: string, position: { x: number; y: number }): void {
    this.nodeMap.set(id, new FakeLayoutNode(id, position));
  }
  node(id: string): FakeLayoutNode {
    const item = this.nodeMap.get(id);
    if (!item) throw new Error(`Missing fake node ${id}`);
    return item;
  }
  nodes(): FakeLayoutNodeCollection { return new FakeLayoutNodeCollection([...this.nodeMap.values()]); }
  edges(): { length: number } { return { length: this.edgeCount }; }
  extent(): { x1: number; y1: number; x2: number; y2: number } {
    return { x1: -500, y1: -500, x2: 500, y2: 500 };
  }
  getElementById(id: string): FakeLayoutNode | { length: 0 } {
    return this.nodeMap.get(id) ?? { length: 0 };
  }
  pan(next?: { x: number; y: number }): { x: number; y: number } {
    if (next) this.panValue = { ...next };
    return { ...this.panValue };
  }
  zoom(next?: number): number {
    if (next !== undefined) this.zoomValue = next;
    return this.zoomValue;
  }
  layout(options: Record<string, unknown>): FakeLayout {
    this.layoutOptions = options;
    return new FakeLayout(this, this.finishOnRun);
  }
  disturbViewport(): void {
    this.panValue = { x: -100, y: -200 };
    this.zoomValue = 0.4;
  }
  moveUnlockedNodes(): void {
    this.nodes().forEach((item) => {
      if (!item.locked()) {
        const position = item.position();
        item.position({ x: position.x + 10, y: position.y + 10 });
      }
    });
  }
}

class FakeLayout {
  private stopHandler?: () => void;

  constructor(
    private readonly cy: FakeLayoutCore,
    private readonly finishOnRun: boolean,
  ) {}

  one(_event: string, handler: () => void): this {
    this.stopHandler = handler;
    return this;
  }
  run(): this {
    this.cy.moveUnlockedNodes();
    this.cy.disturbViewport();
    if (this.finishOnRun) this.stopHandler?.();
    return this;
  }
  stop(): this { return this; }
}

function fakeElement(): Record<string, unknown> {
  const classes = new Set<string>();
  return {
    textContent: "",
    className: "path-status",
    classList: {
      add: (...names: string[]) => names.forEach((name) => classes.add(name)),
      contains: (name: string) => classes.has(name),
    },
  };
}

function fakeCytoscape() {
  return {
    batch: (callback: () => void) => callback(),
    add: () => undefined,
    getElementById: () => ({
      position: () => ({ x: 0, y: 0 }),
      select: () => undefined,
      unselect: () => undefined,
    }),
    nodes: () => ({
      filter: () => ({
        length: 0,
        forEach: () => undefined,
      }),
    }),
  };
}

class TwoBatchLoader {
  private readonly calls = new Map<string, { gate: Deferred<void>; signal?: AbortSignal }>();
  readonly completedFocusIds: string[] = [];

  async load(
    graph: GraphResponse,
    onBatch: (batch: GraphLoadBatch) => void | Promise<void>,
    signal?: AbortSignal,
    onPlan?: (total: number) => void,
  ): Promise<GraphLoadResult> {
    const focusId = graph.focusId ?? "";
    const gate = deferred<void>();
    this.calls.set(focusId, { gate, signal });
    onPlan?.(2);
    await onBatch({ nodes: [], edges: [], processed: 1, total: 2, pendingEdges: 0 });
    await gate.promise;
    if (signal?.aborted) return { ...EMPTY_RESULT, canceled: true };
    await onBatch({ nodes: [], edges: [], processed: 2, total: 2, pendingEdges: 0 });
    this.completedFocusIds.push(focusId);
    return EMPTY_RESULT;
  }

  hasCall(focusId: string): boolean {
    return this.calls.has(focusId);
  }

  signalFor(focusId: string): AbortSignal | undefined {
    return this.calls.get(focusId)?.signal;
  }

  release(focusId: string): void {
    this.calls.get(focusId)?.gate.resolve();
  }
}

function node(id: string) {
  return { id, domainType: "Component", label: id, properties: {} };
}

function response(focusId: string): GraphResponse {
  return { source: "engine", focusId, nodes: [], edges: [] };
}

function pathOption(id: string, stepId: string): AttackPathOption {
  return {
    id,
    label: id,
    sourceFile: "test.yaml",
    goalId: `threat-instance:${id}`,
    result: {
      steps: [stepId],
      goal_step: stepId,
      review: { reviewed: false, assertion_status: "proposed", review_status: null },
    },
  };
}

interface Deferred<T> {
  promise: Promise<T>;
  resolve(value: T): void;
}

interface RejectedDeferred<T> extends Deferred<T> {
  reject(error: unknown): void;
}

function deferred<T>(): Deferred<T> {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((resolvePromise) => { resolve = resolvePromise; });
  return { promise, resolve };
}

function rejectedDeferred<T>(): RejectedDeferred<T> {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

async function waitFor(predicate: () => boolean): Promise<void> {
  for (let attempt = 0; attempt < 100 && !predicate(); attempt += 1) {
    await Promise.resolve();
  }
  if (!predicate()) throw new Error("Timed out waiting for graph-view test state");
}

interface DomViewHarness {
  state: GraphState;
  renderGraphCalls: number;
  start(): Promise<void>;
  handleSelection(nodeId: string): void;
  renderLegend(): void;
  renderAttackPathStatus(option?: AttackPathOption): void;
}

function startupGraph(): GraphResponse {
  return {
    source: "engine",
    notice: "Engine model data",
    focusId: "attack-path:imds-pivot",
    nodes: [
      { id: "attack-path:imds-pivot", domainType: "AttackPath", label: "IMDS pivot path", properties: {}, expandable: true },
      { id: "threat-instance:imds-pivot", domainType: "ThreatInstance", label: "IMDS pivot threat", properties: {} },
    ],
    edges: [{
      id: "relationship:attack-path:imds-pivot|realizes_threat|threat-instance:imds-pivot",
      source: "attack-path:imds-pivot",
      target: "threat-instance:imds-pivot",
      relationshipType: "realizes_threat",
      properties: {
        assertion_ids: ["assertion:ai-imds-pivot-realizes"],
        assertion_status: "proposed",
        confidence: "low",
        review_ids: ["review:ai-triage"],
        review_status: "changes_requested",
      },
    }],
  };
}

function createDomView(overrides: Partial<GraphDataProvider> = {}) {
  const document = new FakeDocument([
    "data-source-notice", "type-legend", "relationship-legend", "graph-canvas", "node-list",
    "node-count", "graph-loading", "attack-path-select", "clear-attack-path", "attack-path-status",
    "inspector-label", "inspector-type", "inspector-id", "expand-node", "property-list",
    "relationship-list",
  ]);
  const provider: GraphDataProvider = {
    metadata: { source: "engine", label: "Engine model data", notice: "Engine model data" },
    getInitialGraph: async () => startupGraph(),
    getNeighborhood: async (nodeId) => response(nodeId),
    getAttackPaths: async () => [],
    ...overrides,
  };
  const view = new KnowledgeGraphView(provider, document as unknown as Document) as unknown as
    DomViewHarness & {
      cy?: unknown;
      renderGraph(): void;
      loadGraphResponse(graph: GraphResponse): Promise<GraphLoadResult>;
    };
  view.renderGraphCalls = 0;
  view.renderGraph = () => {
    view.renderGraphCalls += 1;
    view.cy = {
      getElementById: () => ({ select: () => undefined, unselect: () => undefined }),
      elements: () => ({ removeClass: () => undefined }),
    };
  };
  view.loadGraphResponse = async (graph) => {
    const known = new Set(view.state.nodes.map((item) => item.id));
    const knownEdges = new Set(view.state.edges.map((item) => item.id));
    view.state = {
      ...view.state,
      nodes: [...view.state.nodes, ...graph.nodes.filter((item) => !known.has(item.id))],
      edges: [...view.state.edges, ...graph.edges.filter((item) => !knownEdges.has(item.id))],
    };
    return EMPTY_RESULT;
  };
  return { view, document };
}

class FakeClassList {
  constructor(private readonly owner: FakeDomElement) {}

  private get names(): Set<string> {
    return new Set(this.owner.className.split(/\s+/).filter(Boolean));
  }
  private set names(next: Set<string>) {
    this.owner.className = [...next].join(" ");
  }
  add(...names: string[]): void { this.names = new Set([...this.names, ...names]); }
  remove(...names: string[]): void {
    const next = this.names;
    names.forEach((name) => next.delete(name));
    this.names = next;
  }
  toggle(name: string, force?: boolean): void {
    if (force ?? !this.contains(name)) this.add(name);
    else this.remove(name);
  }
  contains(name: string): boolean { return this.names.has(name); }
}

class FakeDomElement {
  className = "";
  children: FakeDomElement[] = [];
  readonly classList = new FakeClassList(this);
  readonly style: Record<string, string> = {};
  readonly dataset: Record<string, string> = {};
  readonly attributes = new Map<string, string>();
  disabled = false;
  hidden = false;
  value = "";
  type = "";
  onclick: unknown = null;
  onchange: unknown = null;
  private text = "";

  constructor(readonly tagName: string) {}

  get textContent(): string {
    return this.text + this.children.map((child) => child.textContent).join("");
  }
  set textContent(value: string) {
    this.text = value;
    this.children = [];
  }
  append(...nodes: FakeDomElement[]): void { this.children.push(...nodes); }
  prepend(...nodes: FakeDomElement[]): void { this.children.unshift(...nodes); }
  replaceChildren(...nodes: FakeDomElement[]): void {
    this.text = "";
    this.children = [...nodes];
  }
  setAttribute(name: string, value: string): void { this.attributes.set(name, value); }
  addEventListener(): void {}
}

class FakeDocument {
  private readonly elements = new Map<string, FakeDomElement>();

  constructor(ids: readonly string[]) {
    for (const id of ids) this.elements.set(id, new FakeDomElement("div"));
  }
  getElementById(id: string): FakeDomElement | null { return this.elements.get(id) ?? null; }
  byId(id: string): FakeDomElement {
    const element = this.elements.get(id);
    if (!element) throw new Error(`Missing fake element ${id}`);
    return element;
  }
  createElement(tag: string): FakeDomElement { return new FakeDomElement(tag); }
  createElementNS(_namespace: string, tag: string): FakeDomElement { return new FakeDomElement(tag); }
  createTextNode(text: string): FakeDomElement {
    const node = new FakeDomElement("#text");
    node.textContent = text;
    return node;
  }
}
