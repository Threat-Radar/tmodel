import type { GraphEdge, GraphNode, GraphResponse } from "./graph-types";

export const DEFAULT_GRAPH_BATCH_SIZE = 200;

export interface GraphLoadBatch {
  nodes: GraphNode[];
  edges: GraphEdge[];
  processed: number;
  total: number;
  pendingEdges: number;
}

export interface GraphLoadResult {
  canceled: boolean;
  insertedNodes: number;
  insertedEdges: number;
  pendingEdges: number;
}

export type GraphBatchScheduler = () => Promise<void>;

export interface ProgressiveGraphLoaderOptions {
  batchSize?: number;
  schedule?: GraphBatchScheduler;
}

type GraphLoadPlanHandler = (total: number) => void;

interface PendingEdge {
  edge: GraphEdge;
  owners: Set<symbol>;
}

export class ProgressiveGraphLoader {
  private readonly loadedNodeIds = new Set<string>();
  private readonly loadedEdgeIds = new Set<string>();
  private readonly pendingEdges = new Map<string, PendingEdge>();
  private readonly batchSize: number;
  private readonly schedule: GraphBatchScheduler;
  private loadQueue: Promise<void> = Promise.resolve();

  constructor(options: ProgressiveGraphLoaderOptions = {}) {
    this.batchSize = Math.max(1, Math.floor(options.batchSize ?? DEFAULT_GRAPH_BATCH_SIZE));
    this.schedule = options.schedule ?? scheduleBrowserFrame;
  }

  load(
    response: GraphResponse,
    onBatch: (batch: GraphLoadBatch) => void | Promise<void>,
    signal?: AbortSignal,
    onPlan?: GraphLoadPlanHandler,
  ): Promise<GraphLoadResult> {
    const requestId = Symbol("graph-load");
    const ownedEdgeIds = new Set<string>();
    this.registerResponseEdges(response.edges, requestId, ownedEdgeIds);
    this.adoptProcessableEdges(response.nodes, requestId, ownedEdgeIds);

    const previousLoad = this.loadQueue;
    let releaseQueue!: () => void;
    this.loadQueue = new Promise((resolve) => { releaseQueue = resolve; });

    return this.runLoad(
      previousLoad,
      requestId,
      ownedEdgeIds,
      response,
      onBatch,
      signal,
      onPlan,
    ).finally(releaseQueue);
  }

  private async runLoad(
    previousLoad: Promise<void>,
    requestId: symbol,
    ownedEdgeIds: Set<string>,
    response: GraphResponse,
    onBatch: (batch: GraphLoadBatch) => void | Promise<void>,
    signal?: AbortSignal,
    onPlan?: GraphLoadPlanHandler,
  ): Promise<GraphLoadResult> {
    await previousLoad;
    if (signal?.aborted) {
      this.releasePendingEdges(requestId, ownedEdgeIds);
      return { canceled: true, insertedNodes: 0, insertedEdges: 0, pendingEdges: this.pendingEdges.size };
    }

    const nodes = deduplicate(response.nodes, this.loadedNodeIds);
    this.adoptProcessableEdges(nodes, requestId, ownedEdgeIds);

    const availableNodeIds = new Set(this.loadedNodeIds);
    for (const node of nodes) availableNodeIds.add(node.id);
    const processableEdgeIds = new Set<string>();
    for (const [id, pending] of this.pendingEdges) {
      const { edge } = pending;
      if (availableNodeIds.has(edge.source) && availableNodeIds.has(edge.target)) {
        processableEdgeIds.add(id);
      }
    }

    let nodeIndex = 0;
    let insertedNodes = 0;
    let insertedEdges = 0;

    try {
      // The total describes everything this response can actually insert. That
      // includes edges held from an earlier page whose endpoints arrive now, and
      // excludes newly queued edges that still have a missing endpoint.
      const total = nodes.length + processableEdgeIds.size;
      onPlan?.(total);

      while (nodeIndex < nodes.length || this.hasReadyEdge(processableEdgeIds)) {
        if (signal?.aborted) break;

        const batchNodes = nodes.slice(nodeIndex, nodeIndex + this.batchSize);
        const remainingCapacity = this.batchSize - batchNodes.length;
        const edgeCapacity = batchNodes.length === 0 ? this.batchSize : remainingCapacity;
        const availableBatchNodeIds = new Set(this.loadedNodeIds);
        for (const node of batchNodes) availableBatchNodeIds.add(node.id);
        const batchEdges = this.findReadyEdges(
          edgeCapacity,
          processableEdgeIds,
          availableBatchNodeIds,
        );

        await onBatch({
          nodes: batchNodes,
          edges: batchEdges,
          processed: insertedNodes + insertedEdges + batchNodes.length + batchEdges.length,
          total,
          pendingEdges: this.pendingEdges.size - batchEdges.length,
        });

        // Commit IDs only after the consumer has accepted the complete batch.
        // A rejected callback therefore leaves every proposed element retryable.
        nodeIndex += batchNodes.length;
        for (const node of batchNodes) this.loadedNodeIds.add(node.id);
        for (const edge of batchEdges) {
          this.pendingEdges.delete(edge.id);
          this.loadedEdgeIds.add(edge.id);
        }
        insertedNodes += batchNodes.length;
        insertedEdges += batchEdges.length;

        if (nodeIndex < nodes.length || this.hasReadyEdge(processableEdgeIds)) {
          await this.schedule();
        }
      }
    } catch (error) {
      // A failed plan, insertion, or scheduler owns no unaccepted edges. Prior
      // owners remain, while response-owned edges can be registered by a retry.
      this.releasePendingEdges(requestId, ownedEdgeIds);
      throw error;
    } finally {
      // A canceled request must not leave unresolved edges behind for an
      // unrelated later response. Edges already pending before this request
      // remain valid and are deliberately preserved.
      if (signal?.aborted) {
        this.releasePendingEdges(requestId, ownedEdgeIds);
      }
    }

    return {
      canceled: signal?.aborted ?? false,
      insertedNodes,
      insertedEdges,
      pendingEdges: this.pendingEdges.size,
    };
  }

  private hasReadyEdge(eligibleIds: ReadonlySet<string>): boolean {
    for (const [id, pending] of this.pendingEdges) {
      if (!eligibleIds.has(id)) continue;
      const { edge } = pending;
      if (this.loadedNodeIds.has(edge.source) && this.loadedNodeIds.has(edge.target)) return true;
    }
    return false;
  }

  private findReadyEdges(
    limit: number,
    eligibleIds: ReadonlySet<string>,
    availableNodeIds: ReadonlySet<string>,
  ): GraphEdge[] {
    const edges: GraphEdge[] = [];
    for (const [id, pending] of this.pendingEdges) {
      if (edges.length >= limit) break;
      if (!eligibleIds.has(id)) continue;
      const { edge } = pending;
      if (!availableNodeIds.has(edge.source) || !availableNodeIds.has(edge.target)) continue;
      edges.push(edge);
    }
    return edges;
  }

  private registerResponseEdges(
    edges: readonly GraphEdge[],
    requestId: symbol,
    ownedEdgeIds: Set<string>,
  ): void {
    for (const edge of edges) {
      if (this.loadedEdgeIds.has(edge.id)) continue;
      let pending = this.pendingEdges.get(edge.id);
      if (!pending) {
        pending = { edge, owners: new Set() };
        this.pendingEdges.set(edge.id, pending);
      }
      pending.owners.add(requestId);
      ownedEdgeIds.add(edge.id);
    }
  }

  private adoptProcessableEdges(
    nodes: readonly GraphNode[],
    requestId: symbol,
    ownedEdgeIds: Set<string>,
  ): void {
    const availableNodeIds = new Set(this.loadedNodeIds);
    for (const node of nodes) availableNodeIds.add(node.id);
    for (const [id, pending] of this.pendingEdges) {
      if (
        availableNodeIds.has(pending.edge.source)
        && availableNodeIds.has(pending.edge.target)
      ) {
        pending.owners.add(requestId);
        ownedEdgeIds.add(id);
      }
    }
  }

  private releasePendingEdges(requestId: symbol, ownedEdgeIds: ReadonlySet<string>): void {
    for (const id of ownedEdgeIds) {
      const pending = this.pendingEdges.get(id);
      if (!pending) continue;
      pending.owners.delete(requestId);
      if (pending.owners.size === 0) this.pendingEdges.delete(id);
    }
  }
}

function deduplicate<T extends { id: string }>(
  values: readonly T[],
  loadedIds: ReadonlySet<string>,
): T[] {
  const queuedIds = new Set<string>();
  return values.filter((value) => {
    if (loadedIds.has(value.id) || queuedIds.has(value.id)) return false;
    queuedIds.add(value.id);
    return true;
  });
}

function scheduleBrowserFrame(): Promise<void> {
  return new Promise((resolve) => {
    if (typeof requestAnimationFrame === "function") requestAnimationFrame(() => resolve());
    else setTimeout(resolve, 0);
  });
}
