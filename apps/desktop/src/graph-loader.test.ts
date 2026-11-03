import { describe, expect, it } from "vitest";
import { ProgressiveGraphLoader, type GraphLoadBatch } from "./graph-loader";
import { createGraphState, mergeGraph, selectNode, toCytoscapeElements } from "./graph-model";
import type { GraphEdge, GraphNode, GraphResponse } from "./graph-types";

const immediate = async (): Promise<void> => Promise.resolve();

describe("progressive graph loading", () => {
  it("inserts bounded batches in order and completes with exact counts", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 2, schedule: immediate });
    const batches: GraphLoadBatch[] = [];
    const result = await loader.load(smallGraph(), (batch) => { batches.push(batch); });

    expect(batches.every((batch) => batch.nodes.length + batch.edges.length <= 2)).toBe(true);
    expect(batches[0].nodes.map((node) => node.id)).toEqual(["component:0", "component:1"]);
    expect(result).toMatchObject({ canceled: false, insertedNodes: 3, insertedEdges: 2 });
  });

  it("deduplicates stable node and edge IDs across repeated responses", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 2, schedule: immediate });
    const inserted: GraphLoadBatch[] = [];
    await loader.load(smallGraph(), (batch) => { inserted.push(batch); });
    const repeated = await loader.load(smallGraph(), (batch) => { inserted.push(batch); });

    expect(repeated).toMatchObject({ insertedNodes: 0, insertedEdges: 0 });
    expect(new Set(inserted.flatMap((batch) => batch.nodes.map((node) => node.id))).size).toBe(3);
    expect(new Set(inserted.flatMap((batch) => batch.edges.map((edge) => edge.id))).size).toBe(2);
  });

  it("holds an edge until endpoints arrive in a later response", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 2, schedule: immediate });
    const firstPageBatches: GraphLoadBatch[] = [];
    const secondPageBatches: GraphLoadBatch[] = [];
    const edgeOnly = response([], [edge(0, 0, 1)]);
    const pending = await loader.load(edgeOnly, (batch) => { firstPageBatches.push(batch); });
    const completed = await loader.load(
      response([node(0), node(1)], []),
      (batch) => { secondPageBatches.push(batch); },
    );

    expect(pending).toMatchObject({ insertedEdges: 0, pendingEdges: 1 });
    expect(firstPageBatches).toEqual([]);
    expect(completed).toMatchObject({ insertedNodes: 2, insertedEdges: 1, pendingEdges: 0 });
    expect(secondPageBatches.every((batch) => batch.processed <= batch.total)).toBe(true);
    const finalBatch = secondPageBatches[secondPageBatches.length - 1];
    expect(finalBatch).toMatchObject({ processed: 3, total: 3 });
    expect(finalBatch?.edges[0]).toMatchObject({
      id: "edge:0",
      source: "component:0",
      target: "component:1",
    });
  });

  it("preserves selection while progressive batches merge into state", async () => {
    const initial = response([node(0)], []);
    let state = selectNode(createGraphState(initial), "component:0");
    const loader = new ProgressiveGraphLoader({ batchSize: 1, schedule: immediate });
    await loader.load(smallGraph(), (batch) => {
      state = mergeGraph(state, response(batch.nodes, batch.edges));
    });

    expect(state.selectedNodeId).toBe("component:0");
    expect(state.nodes).toHaveLength(3);
    expect(state.edges).toHaveLength(2);
  });

  it("stops safely after cancellation without emitting later batches", async () => {
    const controller = new AbortController();
    let schedules = 0;
    const loader = new ProgressiveGraphLoader({
      batchSize: 2,
      schedule: async () => {
        schedules += 1;
        controller.abort();
      },
    });
    const batches: GraphLoadBatch[] = [];
    const result = await loader.load(
      smallGraph(),
      (batch) => { batches.push(batch); },
      controller.signal,
    );

    expect(result).toMatchObject({
      canceled: true,
      insertedNodes: 2,
      insertedEdges: 0,
      pendingEdges: 0,
    });
    expect(schedules).toBe(1);
    expect(batches).toHaveLength(1);
  });

  it("does not leak an unresolved edge from a canceled request into a later load", async () => {
    const controller = new AbortController();
    const loader = new ProgressiveGraphLoader({
      batchSize: 1,
      schedule: async () => { controller.abort(); },
    });
    const staleEdge = edge(99, 0, 2);
    const canceled = await loader.load(
      response([node(0), node(1)], [staleEdge]),
      () => undefined,
      controller.signal,
    );
    const laterBatches: GraphLoadBatch[] = [];
    const later = await loader.load(
      response([node(2)], []),
      (batch) => { laterBatches.push(batch); },
    );

    expect(canceled).toMatchObject({ canceled: true, pendingEdges: 0 });
    expect(later).toMatchObject({ canceled: false, insertedNodes: 1, insertedEdges: 0 });
    expect(laterBatches.flatMap((batch) => batch.edges)).not.toContainEqual(staleEdge);
  });

  it("preserves a pending edge adopted by an overlapping replacement load", async () => {
    const releases: Array<() => void> = [];
    const schedule = () => new Promise<void>((resolve) => { releases.push(resolve); });
    const loader = new ProgressiveGraphLoader({ batchSize: 1, schedule });
    const firstController = new AbortController();
    const firstBatches: GraphLoadBatch[] = [];
    const replacementBatches: GraphLoadBatch[] = [];

    const firstLoad = loader.load(
      response([node(0), node(1)], [edge(0, 0, 2)]),
      (batch) => { firstBatches.push(batch); },
      firstController.signal,
    );
    await waitFor(() => releases.length === 1);

    firstController.abort();
    const replacementLoad = loader.load(
      response([node(2)], []),
      (batch) => { replacementBatches.push(batch); },
    );
    releases.shift()?.();
    await waitFor(() => releases.length === 1);
    releases.shift()?.();

    const [first, replacement] = await Promise.all([firstLoad, replacementLoad]);
    expect(first).toMatchObject({ canceled: true, insertedNodes: 1, insertedEdges: 0 });
    expect(replacement).toMatchObject({ canceled: false, insertedNodes: 1, insertedEdges: 1 });
    expect(replacementBatches.flatMap((batch) => batch.edges).map((item) => item.id))
      .toEqual(["edge:0"]);
    expect(replacementBatches.every((batch) => batch.processed <= batch.total)).toBe(true);
    expect(replacementBatches[replacementBatches.length - 1])
      .toMatchObject({ processed: 2, total: 2, pendingEdges: 0 });
  });

  it("uses the authoritative plan when a small page activates many pending edges", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 200, schedule: immediate });
    const pendingEdges = Array.from({ length: 201 }, (_, index) => edge(index, 0, 1));
    await loader.load(response([], pendingEdges), () => undefined);
    const plannedTotals: number[] = [];
    const batches: GraphLoadBatch[] = [];

    const completed = await loader.load(
      response([node(0), node(1)], []),
      (batch) => { batches.push(batch); },
      undefined,
      (total) => { plannedTotals.push(total); },
    );

    expect(plannedTotals).toEqual([203]);
    expect(completed).toMatchObject({ insertedNodes: 2, insertedEdges: 201, pendingEdges: 0 });
    expect(batches.every((batch) => batch.processed <= batch.total)).toBe(true);
    expect(batches[batches.length - 1]).toMatchObject({ processed: 203, total: 203 });
  });

  it("retries every element from a batch rejected by the insertion callback", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 5, schedule: immediate });
    await expect(loader.load(smallGraph(), () => {
      throw new Error("insertion failed");
    })).rejects.toThrow("insertion failed");

    const accepted: GraphLoadBatch[] = [];
    const retried = await loader.load(smallGraph(), (batch) => { accepted.push(batch); });

    expect(retried).toMatchObject({ insertedNodes: 3, insertedEdges: 2, pendingEdges: 0 });
    expect(accepted.flatMap((batch) => batch.nodes).map((item) => item.id)).toEqual([
      "component:0",
      "component:1",
      "component:2",
    ]);
    expect(accepted.flatMap((batch) => batch.edges).map((item) => item.id)).toEqual([
      "edge:0",
      "edge:1",
    ]);
  });

  it("keeps accepted batches while retrying only a later failed batch", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 2, schedule: immediate });
    const acceptedBeforeFailure: GraphLoadBatch[] = [];
    let attempt = 0;
    await expect(loader.load(smallGraph(), (batch) => {
      attempt += 1;
      if (attempt === 2) throw new Error("second batch failed");
      acceptedBeforeFailure.push(batch);
    })).rejects.toThrow("second batch failed");

    const retryBatches: GraphLoadBatch[] = [];
    const retried = await loader.load(smallGraph(), (batch) => { retryBatches.push(batch); });
    const allAcceptedNodes = [...acceptedBeforeFailure, ...retryBatches]
      .flatMap((batch) => batch.nodes.map((item) => item.id));
    const allAcceptedEdges = [...acceptedBeforeFailure, ...retryBatches]
      .flatMap((batch) => batch.edges.map((item) => item.id));

    expect(retried).toMatchObject({ insertedNodes: 1, insertedEdges: 2, pendingEdges: 0 });
    expect(allAcceptedNodes).toEqual(["component:0", "component:1", "component:2"]);
    expect(allAcceptedEdges).toEqual(["edge:0", "edge:1"]);
  });

  it("retries a previously pending edge when its activating batch fails", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 3, schedule: immediate });
    await loader.load(response([], [edge(0, 0, 1)]), () => undefined);
    await expect(loader.load(response([node(0), node(1)], []), () => {
      throw new Error("activation failed");
    })).rejects.toThrow("activation failed");

    const accepted: GraphLoadBatch[] = [];
    const retried = await loader.load(
      response([node(0), node(1)], []),
      (batch) => { accepted.push(batch); },
    );

    expect(retried).toMatchObject({ insertedNodes: 2, insertedEdges: 1, pendingEdges: 0 });
    expect(accepted.flatMap((batch) => batch.edges).map((item) => item.id)).toEqual(["edge:0"]);
  });

  it("can retry safely after the progress-planning callback throws", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 5, schedule: immediate });
    await expect(loader.load(
      smallGraph(),
      () => undefined,
      undefined,
      () => { throw new Error("planning failed"); },
    )).rejects.toThrow("planning failed");

    const retried = await loader.load(smallGraph(), () => undefined);
    expect(retried).toMatchObject({ insertedNodes: 3, insertedEdges: 2, pendingEdges: 0 });
  });

  it("does not leak pending edges from a request whose planning callback throws", async () => {
    const loader = new ProgressiveGraphLoader({ batchSize: 5, schedule: immediate });
    await expect(loader.load(
      response([], [edge(99, 0, 1)]),
      () => undefined,
      undefined,
      () => { throw new Error("planning failed"); },
    )).rejects.toThrow("planning failed");

    const accepted: GraphLoadBatch[] = [];
    const unrelated = await loader.load(
      response([node(0), node(1)], []),
      (batch) => { accepted.push(batch); },
    );

    expect(unrelated).toMatchObject({ insertedNodes: 2, insertedEdges: 0, pendingEdges: 0 });
    expect(accepted.flatMap((batch) => batch.edges)).toEqual([]);
  });

  it("maps and batches a deterministic 3,000-node graph without loss or dangling edges", async () => {
    const graph = syntheticGraph(3_000);
    const loader = new ProgressiveGraphLoader({ batchSize: 200, schedule: immediate });
    let state = createGraphState(response([], []));
    const started = performance.now();
    const result = await loader.load(graph, (batch) => {
      state = mergeGraph(state, response(batch.nodes, batch.edges));
    });
    const elements = toCytoscapeElements(state);
    const elapsedMs = performance.now() - started;
    console.info(`progressive graph test: 3000 nodes, ${graph.edges.length} edges in ${elapsedMs.toFixed(1)} ms`);

    expect(result.canceled).toBe(false);
    expect(result.pendingEdges).toBe(0);
    expect(state.nodes).toHaveLength(3_000);
    expect(state.edges).toHaveLength(5_997);
    expect(elements).toHaveLength(8_997);
    expect(new Set(state.nodes.map((item) => item.id)).size).toBe(state.nodes.length);
    expect(new Set(state.edges.map((item) => item.id)).size).toBe(state.edges.length);
    const nodeIds = new Set(state.nodes.map((item) => item.id));
    expect(state.edges.every((item) => nodeIds.has(item.source) && nodeIds.has(item.target))).toBe(true);
  });
});

function smallGraph(): GraphResponse {
  return response([node(0), node(1), node(2)], [edge(0, 0, 1), edge(1, 1, 2)]);
}

function syntheticGraph(count: number): GraphResponse {
  const nodes = Array.from({ length: count }, (_, index) => node(index));
  const edges: GraphEdge[] = [];
  for (let index = 0; index < count - 1; index += 1) {
    edges.push(edge(index, index, index + 1));
  }
  for (let index = 0; index < count - 2; index += 1) {
    edges.push(edge(count + index, index, index + 2));
  }
  return response(nodes, edges);
}

function node(index: number): GraphNode {
  return {
    id: `component:${index}`,
    domainType: "Component",
    label: `Component ${index}`,
    properties: { derived_test_index: index },
  };
}

function edge(index: number, source: number, target: number): GraphEdge {
  return {
    id: `edge:${index}`,
    source: `component:${source}`,
    target: `component:${target}`,
    relationshipType: "uses_component",
    properties: {},
  };
}

function response(nodes: readonly GraphNode[], edges: readonly GraphEdge[]): GraphResponse {
  return { source: "engine", nodes, edges };
}

async function waitFor(predicate: () => boolean): Promise<void> {
  for (let attempt = 0; attempt < 100 && !predicate(); attempt += 1) {
    await Promise.resolve();
  }
  if (!predicate()) throw new Error("Timed out waiting for asynchronous graph-loader state");
}
