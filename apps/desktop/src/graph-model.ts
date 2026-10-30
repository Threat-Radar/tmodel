import type {
  GraphEdge,
  GraphNode,
  GraphRelationship,
  GraphResponse,
} from "./graph-types";
import { relationshipReviewState, type ReviewStateKind } from "./review-status";

export interface GraphState {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId?: string;
}

export interface CytoscapeNodeElement {
  group: "nodes";
  data: { id: string; label: string; domainType: string };
}

export interface CytoscapeEdgeElement {
  group: "edges";
  data: {
    id: string;
    source: string;
    target: string;
    relationshipType: string;
    label: string;
    // Present only for relationships backed by an Assertion. The raw values
    // are kept as recorded; `reviewState` only selects the edge style.
    reviewState?: ReviewStateKind;
    assertionStatus?: string | null;
    reviewStatus?: string | null;
  };
}

export type CytoscapeElement = CytoscapeNodeElement | CytoscapeEdgeElement;

export function createGraphState(response: GraphResponse): GraphState {
  return mergeGraph({ nodes: [], edges: [] }, response);
}

export function mergeGraph(state: GraphState, response: GraphResponse): GraphState {
  const nodes = new Map(state.nodes.map((node) => [node.id, node]));
  const edges = new Map(state.edges.map((edge) => [edge.id, edge]));

  for (const node of response.nodes) nodes.set(node.id, cloneNode(node));
  for (const edge of response.edges) edges.set(edge.id, cloneEdge(edge));

  return {
    nodes: [...nodes.values()],
    edges: [...edges.values()],
    selectedNodeId: state.selectedNodeId,
  };
}

export function selectNode(state: GraphState, nodeId: string): GraphState {
  if (!state.nodes.some((node) => node.id === nodeId)) return state;
  return { ...state, selectedNodeId: nodeId };
}

export function relationshipsForNode(
  state: GraphState,
  nodeId: string,
): GraphRelationship[] {
  const nodes = new Map(state.nodes.map((node) => [node.id, node]));
  const relationships: GraphRelationship[] = [];

  for (const edge of state.edges) {
    if (edge.source === nodeId) {
      relationships.push({
        edgeId: edge.id,
        direction: "outgoing",
        relationshipType: edge.relationshipType,
        connectedNodeId: edge.target,
        connectedNode: nodes.get(edge.target),
        properties: edge.properties,
      });
    } else if (edge.target === nodeId) {
      relationships.push({
        edgeId: edge.id,
        direction: "incoming",
        relationshipType: edge.relationshipType,
        connectedNodeId: edge.source,
        connectedNode: nodes.get(edge.source),
        properties: edge.properties,
      });
    }
  }

  return relationships;
}

export function toCytoscapeElements(state: GraphState): CytoscapeElement[] {
  const knownNodes = new Set(state.nodes.map((node) => node.id));
  const nodeElements = state.nodes.map(toCytoscapeNodeElement);
  const edgeElements: CytoscapeEdgeElement[] = state.edges
    .filter((edge) => knownNodes.has(edge.source) && knownNodes.has(edge.target))
    .map(toCytoscapeEdgeElement);

  return [...nodeElements, ...edgeElements];
}

export function toCytoscapeNodeElement(node: GraphNode): CytoscapeNodeElement {
  return {
    group: "nodes",
    data: { id: node.id, label: node.label, domainType: node.domainType },
  };
}

export function toCytoscapeEdgeElement(edge: GraphEdge): CytoscapeEdgeElement {
  const data: CytoscapeEdgeElement["data"] = {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    relationshipType: edge.relationshipType,
    label: edge.relationshipType,
  };
  const review = relationshipReviewState(edge.properties);
  if (review) {
    data.reviewState = review.kind;
    data.assertionStatus = review.assertionStatus;
    data.reviewStatus = review.reviewStatus;
    // The label carries the state as text too, so it never rests on color.
    if (review.kind !== "accepted") data.label = `${edge.relationshipType} · ${review.label.toLowerCase()}`;
  }
  return { group: "edges", data };
}

function cloneNode(node: GraphNode): GraphNode {
  return { ...node, properties: cloneProperties(node.properties) };
}

function cloneEdge(edge: GraphEdge): GraphEdge {
  return { ...edge, properties: cloneProperties(edge.properties) };
}

function cloneProperties(properties: GraphNode["properties"]): GraphNode["properties"] {
  return Object.fromEntries(
    Object.entries(properties).map(([key, value]) => [key, Array.isArray(value) ? [...value] : value]),
  );
}
