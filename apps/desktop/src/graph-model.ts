import type {
  GraphAssertionProvenance,
  GraphEdge,
  GraphNode,
  GraphRelationship,
  GraphResponse,
} from "./graph-types";
import {
  relationshipReviewState,
  reviewStatePresentation,
  type ReviewStateKind,
  type ReviewStatePresentation,
} from "./review-status";

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
    /** Direct model relationship; its primary canvas style always stays established. */
    authored?: boolean;
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
        authored: edge.authored,
        assertions: edge.assertions,
        properties: edge.properties,
      });
    } else if (edge.target === nodeId) {
      relationships.push({
        edgeId: edge.id,
        direction: "incoming",
        relationshipType: edge.relationshipType,
        connectedNodeId: edge.source,
        connectedNode: nodes.get(edge.source),
        authored: edge.authored,
        assertions: edge.assertions,
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
  if (edge.authored !== undefined) data.authored = edge.authored;
  // The primary line represents the relationship itself. Directly authored
  // provenance remains established even when Assertions about the same triple
  // are proposed, rejected, or disputed; those verdicts remain in the inspector.
  if (edge.authored === true) return { group: "edges", data };

  const review = edge.assertions?.length
    ? structuredAssertionPresentation(edge.assertions)
    : relationshipReviewState(edge.properties);
  if (review) {
    data.reviewState = review.kind;
    data.assertionStatus = review.assertionStatus;
    data.reviewStatus = review.reviewStatus;
    // The label carries the state as text too, so it never rests on color.
    if (review.kind !== "accepted") data.label = `${edge.relationshipType} · ${review.label.toLowerCase()}`;
  }
  return { group: "edges", data };
}

function structuredAssertionPresentation(
  assertions: readonly GraphAssertionProvenance[],
): ReviewStatePresentation {
  const presentations = assertions.map((assertion) => reviewStatePresentation(
    assertion.assertion_status,
    combinedReviewStatus(assertion.reviews.map((review) => review.review_status)),
  ));
  const kinds = new Set(presentations.map((presentation) => presentation.kind));
  if (assertions.length === 1) return presentations[0];
  if (kinds.size === 1) {
    const presentation = presentations[0];
    return {
      ...presentation,
      label: `${assertions.length} ${presentation.label} Assertions`,
      description: `${assertions.length} Assertions independently record ${presentation.description}`,
      assertionStatus: null,
      reviewStatus: null,
    };
  }
  return {
    kind: "unknown",
    label: "Mixed Assertion States",
    description: "multiple Assertions record different states; inspect each Assertion",
    assertionStatus: null,
    reviewStatus: null,
  };
}

function combinedReviewStatus(statuses: readonly (string | null)[]): string | null {
  const values = statuses.map(normalized).filter((status): status is string => Boolean(status));
  if (values.includes("rejected")) return "rejected";
  if (values.includes("changes_requested")) return "changes_requested";
  if (values.length > 0 && values.every((status) => status === "accepted")) return "accepted";
  return new Set(values).size === 1 ? values[0] : values.length ? "mixed" : null;
}

function normalized(value: string | null): string | undefined {
  const result = value?.trim().toLowerCase().replace(/[\s-]+/g, "_");
  return result || undefined;
}

function cloneNode(node: GraphNode): GraphNode {
  return { ...node, properties: cloneProperties(node.properties) };
}

function cloneEdge(edge: GraphEdge): GraphEdge {
  return {
    ...edge,
    assertions: edge.assertions?.map((assertion) => ({
      ...assertion,
      evidence: [...assertion.evidence],
      reviews: assertion.reviews.map((review) => ({ ...review })),
    })),
    properties: cloneProperties(edge.properties),
  };
}

function cloneProperties(properties: GraphNode["properties"]): GraphNode["properties"] {
  return Object.fromEntries(
    Object.entries(properties).map(([key, value]) => [key, Array.isArray(value) ? [...value] : value]),
  );
}
