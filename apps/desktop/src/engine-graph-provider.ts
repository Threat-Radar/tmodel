import { DEFAULT_ENGINE_URL } from "./engine";
import type {
  AttackPathGoalResponse,
  AttackPathResponse,
  GraphDataProvider,
  GraphEdge,
  GraphNode,
  GraphProperties,
  GraphResponse,
} from "./graph-types";

export const DEFAULT_MODEL_FILE = "mvp-01-software-doc-service.yaml";

interface EngineGraphNode {
  id: string;
  domain_type: string;
  label: string;
  properties: GraphProperties;
}

interface EngineGraphEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  properties: GraphProperties;
}

export interface EngineGraphResponse {
  file: string;
  nodes: readonly EngineGraphNode[];
  edges: readonly EngineGraphEdge[];
}

/**
 * Local-engine provider for Issue #59. It fetches one storage-neutral graph DTO,
 * caches it, and derives one-hop pages until #65 supplies a storage façade.
 */
export class EngineGraphDataProvider implements GraphDataProvider {
  readonly metadata;
  private graphPromise?: Promise<EngineGraphResponse>;

  constructor(
    private readonly modelFile = DEFAULT_MODEL_FILE,
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {
    this.metadata = {
      source: "engine" as const,
      label: "Engine model data",
      notice: `Engine model data from ${fileName(modelFile)}`,
    };
  }

  async getInitialGraph(): Promise<GraphResponse> {
    const graph = await this.fullGraph();
    const focusId = graph.nodes.find((node) => node.domain_type === "Component")?.id
      ?? graph.nodes[0]?.id;
    if (!focusId) return graphResponse(graph, new Set(), undefined, this.metadata.notice);
    return graphResponse(graph, neighborhoodIds(graph, focusId), focusId, this.metadata.notice);
  }

  async getNeighborhood(nodeId: string): Promise<GraphResponse> {
    const graph = await this.fullGraph();
    return graphResponse(
      graph,
      neighborhoodIds(graph, nodeId),
      nodeId,
      `Engine model data from ${fileName(graph.file)}`,
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

  private fullGraph(): Promise<EngineGraphResponse> {
    this.graphPromise ??= this.request<EngineGraphResponse>("/graph", { file: this.modelFile });
    return this.graphPromise;
  }

  private async request<T>(path: string, query: Readonly<Record<string, string>>): Promise<T> {
    const url = new URL(path, `${this.baseUrl.replace(/\/$/, "")}/`);
    for (const [name, value] of Object.entries(query)) url.searchParams.set(name, value);
    const response = await this.fetchImpl(url);
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
}

export function mapEngineGraphResponse(response: EngineGraphResponse): GraphResponse {
  return graphResponse(
    response,
    new Set(response.nodes.map((node) => node.id)),
    undefined,
    `Engine model data from ${fileName(response.file)}`,
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
  return { source: "engine", notice, focusId, nodes, edges };
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

function fileName(path: string): string {
  return path.split(/[\\/]/).pop() ?? path;
}
