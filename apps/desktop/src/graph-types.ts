export type GraphPropertyValue = string | number | boolean | string[] | null;

export type GraphProperties = Readonly<Record<string, GraphPropertyValue>>;

export interface GraphNode {
  id: string;
  domainType: string;
  label: string;
  properties: GraphProperties;
  expandable?: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationshipType: string;
  properties: GraphProperties;
}

export interface GraphRelationship {
  edgeId: string;
  direction: "incoming" | "outgoing";
  relationshipType: string;
  connectedNodeId: string;
  connectedNode?: GraphNode;
}

export interface GraphResponse {
  source: "development-fixture" | "engine";
  notice?: string;
  focusId?: string;
  nodes: readonly GraphNode[];
  edges: readonly GraphEdge[];
}

export interface GraphProviderMetadata {
  source: GraphResponse["source"];
  label: string;
  notice: string;
}

export interface GraphDataProvider {
  readonly metadata: GraphProviderMetadata;
  getInitialGraph(): Promise<GraphResponse>;
  getNeighborhood(nodeId: string): Promise<GraphResponse>;
  // Each item remains one unmodified PR #132 response for one goal. Providers
  // may aggregate several goal requests for presentation in a single selector.
  getAttackPaths(): Promise<readonly AttackPathResponse[]>;
}

// Transport types for the engine response merged in PR #132. Path computation
// remains engine-owned; the frontend only presents the returned stable IDs.
export interface AttackPathReview {
  reviewed: boolean;
  assertion_status: string | null;
  review_status: string | null;
}

export interface AttackPathResult {
  steps: string[];
  goal_step: string;
  authored_path?: string;
  review: AttackPathReview;
}

export interface AttackPathResponse {
  file: string;
  goal: string;
  paths: readonly AttackPathResult[];
}

export interface AttackPathGoalResponse {
  file: string;
  threats: readonly string[];
  reviewed_threats: readonly string[];
  steps: number;
}
