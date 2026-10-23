import { describe, expect, it } from "vitest";
import type { AttackPathOption } from "./attack-path";
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
): void {
  for (const item of graph.nodes) {
    if (!view.state.nodes.some((existing) => existing.id === item.id)) {
      view.state = { ...view.state, nodes: [...view.state.nodes, item] };
      cy.addNode(item.id, { x: 0, y: 0 });
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
}

class FakeLayoutNodeCollection {
  constructor(private readonly items: FakeLayoutNode[]) {}

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
  getElementById(id: string): FakeLayoutNode { return this.node(id); }
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
