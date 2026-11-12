import { DEFAULT_ENGINE_URL } from "./engine";
import type {
  AttackPathGoalResponse,
  AttackPathResponse,
  GraphDataProvider,
  GraphEdge,
  GraphNode,
  GraphProperties,
  GraphProviderMetadata,
  GraphResponse,
} from "./graph-types";
import type { AttackPathResults, EngineGraphEdge, EngineGraphResponse } from "./model-types";

export type { EngineGraphResponse } from "./model-types";

/** The model a provider opens when none is named (developer default; the app passes one). */
export const DEFAULT_MODEL_FILE = "mvp-01-software-doc-service.yaml";

export interface EngineGraphProviderOptions {
  /** Node types left out of the graph pages, with every edge that touches them. */
  hiddenDomainTypes?: ReadonlySet<string>;
  /**
   * "neighborhood" (default) opens on the first Component's one-hop
   * neighbourhood. "threats" opens on every threat with its one-hop
   * neighbourhood (paths, damage, risk, mitigations), so the first view tells
   * the model's story and every node beyond it is still reached by expanding
   * (#208); a model without threats falls back to "neighborhood".
   */
  initialView?: "neighborhood" | "threats";
  /** Override the source label for an API-compatible static response set. */
  metadata?: GraphProviderMetadata;
}


/**
 * Local-engine provider for Issue #59. It fetches one storage-neutral graph DTO,
 * caches it, and derives one-hop pages until #65 supplies a storage façade.
 */
export class EngineGraphDataProvider implements GraphDataProvider {
  readonly metadata: GraphProviderMetadata;
  private graphPromise?: Promise<EngineGraphResponse>;

  constructor(
    private readonly modelFile = DEFAULT_MODEL_FILE,
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
    private readonly options: EngineGraphProviderOptions = {},
  ) {
    this.metadata = options.metadata ?? {
      source: "engine" as const,
      label: "Engine model data",
      notice: `Engine model data from ${fileName(modelFile)}`,
    };
  }

  async getInitialGraph(): Promise<GraphResponse> {
    const graph = await this.visibleGraph();
    if (this.options.initialView === "threats") {
      const threats = graph.nodes.filter((node) => node.domain_type === "ThreatInstance");
      if (threats.length > 0) {
        const ids = new Set<string>();
        for (const threat of threats) for (const id of neighborhoodIds(graph, threat.id)) ids.add(id);
        return graphResponse(graph, ids, threats[0].id, this.metadata.notice, this.metadata.source);
      }
    }
    const focusId = graph.nodes.find((node) => node.domain_type === "Component")?.id
      ?? graph.nodes[0]?.id;
    if (!focusId) return graphResponse(graph, new Set(), undefined, this.metadata.notice, this.metadata.source);
    return graphResponse(graph, neighborhoodIds(graph, focusId), focusId, this.metadata.notice, this.metadata.source);
  }

  /** Every visible node of the model, for "Show whole model". */
  async getWholeGraph(): Promise<GraphResponse> {
    const graph = await this.visibleGraph();
    return graphResponse(
      graph,
      new Set(graph.nodes.map((node) => node.id)),
      undefined,
      this.metadata.notice,
      this.metadata.source,
    );
  }

  async getNeighborhood(nodeId: string): Promise<GraphResponse> {
    const graph = await this.visibleGraph();
    return graphResponse(
      graph,
      neighborhoodIds(graph, nodeId),
      nodeId,
      this.metadata.notice,
      this.metadata.source,
    );
  }

  async getAttackPaths(): Promise<readonly AttackPathResponse[]> {
    const graph = await this.fullGraph();
    const goals = await this.request<AttackPathGoalResponse>("/attack-paths", {
      file: graph.file,
    });
    return Promise.all(
      goals.threats.map((goal) => this.request<AttackPathResponse>("/attack-paths", {
        file: graph.file,
        goal,
      })),
    );
  }

  /**
   * Like getAttackPaths, but one threat's failure does not lose the others: the
   * model report shows what the engine did compute and says what is missing.
   */
  async getAttackPathResults(): Promise<AttackPathResults> {
    const graph = await this.fullGraph();
    let goals: AttackPathGoalResponse;
    try {
      goals = await this.request<AttackPathGoalResponse>("/attack-paths", { file: graph.file });
    } catch (error) {
      return { responses: [], failures: [{ goal: null, message: errorText(error) }] };
    }
    const settled = await Promise.allSettled(goals.threats.map((goal) => (
      this.request<AttackPathResponse>("/attack-paths", { file: graph.file, goal })
    )));
    const results: AttackPathResults = { responses: [], failures: [] };
    settled.forEach((outcome, index) => {
      if (outcome.status === "fulfilled") results.responses.push(outcome.value);
      else results.failures.push({ goal: goals.threats[index], message: errorText(outcome.reason) });
    });
    return results;
  }

  /** The whole model as the engine returned it, with nothing hidden (the model report reads this). */
  getModelGraph(): Promise<EngineGraphResponse> {
    return this.fullGraph();
  }

  private async visibleGraph(): Promise<EngineGraphResponse> {
    const graph = await this.fullGraph();
    const hidden = this.options.hiddenDomainTypes;
    if (!hidden || hidden.size === 0) return graph;
    const nodes = graph.nodes.filter((node) => !hidden.has(node.domain_type));
    const kept = new Set(nodes.map((node) => node.id));
    return {
      file: graph.file,
      nodes,
      edges: graph.edges.filter((edge) => kept.has(edge.source) && kept.has(edge.target)),
    };
  }

  private fullGraph(): Promise<EngineGraphResponse> {
    // Concurrent callers share one in-flight request. Only a successful
    // response stays cached: a failed one is evicted so a later call can
    // retry once the engine is reachable.
    if (!this.graphPromise) {
      const pending = this.request<EngineGraphResponse>("/graph", { file: this.modelFile });
      this.graphPromise = pending;
      pending.catch(() => {
        if (this.graphPromise === pending) this.graphPromise = undefined;
      });
    }
    return this.graphPromise;
  }

  private request<T>(path: string, query: Readonly<Record<string, string>>): Promise<T> {
    return requestEngineJson<T>(this.baseUrl, path, query, this.fetchImpl);
  }
}

/** GET a JSON route of the local engine; a non-2xx answer throws with the engine's own message. */
export async function requestEngineJson<T>(
  baseUrl: string,
  path: string,
  query: Readonly<Record<string, string>>,
  fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
): Promise<T> {
  const url = new URL(path, `${baseUrl.replace(/\/$/, "")}/`);
  for (const [name, value] of Object.entries(query)) url.searchParams.set(name, value);
  const response = await fetchImpl(url);
  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json() as { error?: unknown };
      if (typeof body.error === "string") detail = body.error;
    } catch {
      // Preserve the HTTP status when the engine did not return JSON.
    }
    throw new Error(`Engine request failed: ${detail}`);
  }
  return await response.json() as T;
}

export function mapEngineGraphResponse(response: EngineGraphResponse): GraphResponse {
  return graphResponse(
    response,
    new Set(response.nodes.map((node) => node.id)),
    undefined,
    `Engine model data from ${fileName(response.file)}`,
    "engine",
  );
}

function neighborhoodIds(graph: EngineGraphResponse, nodeId: string): Set<string> {
  if (!graph.nodes.some((node) => node.id === nodeId)) return new Set();
  const ids = new Set([nodeId]);
  for (const edge of graph.edges) {
    if (edge.source === nodeId) ids.add(edge.target);
    if (edge.target === nodeId) ids.add(edge.source);
  }
  return ids;
}

function graphResponse(
  graph: EngineGraphResponse,
  ids: ReadonlySet<string>,
  focusId: string | undefined,
  notice: string,
  source: GraphResponse["source"],
): GraphResponse {
  const adjacency = adjacencyByNode(graph.edges);
  const nodes: GraphNode[] = graph.nodes
    .filter((node) => ids.has(node.id))
    .map((node) => ({
      id: node.id,
      domainType: node.domain_type,
      label: node.label,
      properties: cloneProperties(node.properties),
      expandable: [...(adjacency.get(node.id) ?? [])].some((neighbor) => !ids.has(neighbor)),
    }));
  const edges: GraphEdge[] = graph.edges
    .filter((edge) => ids.has(edge.source) && ids.has(edge.target))
    .map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      relationshipType: edge.relationship_type,
      properties: cloneProperties(edge.properties),
    }));
  return { source, notice, focusId, nodes, edges };
}

function adjacencyByNode(edges: readonly EngineGraphEdge[]): Map<string, Set<string>> {
  const adjacency = new Map<string, Set<string>>();
  for (const edge of edges) {
    addNeighbor(adjacency, edge.source, edge.target);
    addNeighbor(adjacency, edge.target, edge.source);
  }
  return adjacency;
}

function addNeighbor(adjacency: Map<string, Set<string>>, source: string, target: string): void {
  const neighbors = adjacency.get(source) ?? new Set<string>();
  neighbors.add(target);
  adjacency.set(source, neighbors);
}

function cloneProperties(properties: GraphProperties): GraphProperties {
  return Object.fromEntries(
    Object.entries(properties).map(([key, value]) => [
      key,
      Array.isArray(value) ? [...value] : value,
    ]),
  );
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function fileName(path: string): string {
  return path.split(/[\\/]/).pop() ?? path;
}
