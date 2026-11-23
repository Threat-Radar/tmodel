import type { EngineGraphEdge, EngineGraphNode, EngineGraphResponse } from "./model-types";
import { relationshipReviewState, type ReviewStateKind } from "./review-status";

export const REQUIREMENT_SORTS = [
  "id", "name", "kind", "normativity", "source", "satisfaction",
] as const;
export type RequirementSort = typeof REQUIREMENT_SORTS[number];
export type RequirementSortOrder = "asc" | "desc";
export type RequirementSatisfaction = "satisfied" | "in_progress" | "unsatisfied" | "not_recorded";

export interface RequirementQuery {
  search?: string;
  kind?: string;
  product?: string;
  sort: RequirementSort;
  order: RequirementSortOrder;
  limit: number;
  offset: number;
}

export const DEFAULT_REQUIREMENT_QUERY: RequirementQuery = {
  sort: "id",
  order: "asc",
  limit: 25,
  offset: 0,
};

export interface RequirementProduct {
  id: string;
  name: string;
}

export interface RequirementMitigation {
  id: string;
  name: string;
  status: string | null;
}

export interface RequirementReviewEvidence {
  id: string;
  status: string | null;
  reviewer: string | null;
  justification: string | null;
}

export interface RequirementAssertionEvidence {
  id: string;
  status: string | null;
  confidence: string | null;
  reviewState: ReviewStateKind;
  description: string | null;
  evidence: string[];
  reviews: RequirementReviewEvidence[];
}

export interface RequirementRelationship {
  edgeId: string;
  established: boolean;
  authored: boolean;
  direction: "incoming" | "outgoing";
  predicate: string;
  targetId: string;
  targetName: string;
  targetType: string;
  assertionIds: string[];
  assertionStatus: string | null;
  confidence: string | null;
  reviewState: ReviewStateKind | "structural";
  descriptions: string[];
  evidence: string[];
  reviews: RequirementReviewEvidence[];
  assertions: RequirementAssertionEvidence[];
}

export interface RequirementRow {
  id: string;
  name: string;
  text: string | null;
  description: string | null;
  kind: string | null;
  normativity: string | null;
  textOrigin: string | null;
  sourceRef: string | null;
  sourceLocator: string | null;
  appliesTo: string[];
  appliesToFamilies: string[];
  applicableProducts: RequirementProduct[];
  satisfaction: RequirementSatisfaction;
  mitigations: RequirementMitigation[];
  relationships: RequirementRelationship[];
}

export interface RequirementCatalog {
  file: string;
  requirements: RequirementRow[];
  products: RequirementProduct[];
  kinds: Record<string, number>;
}

export interface RequirementTableResponse {
  rows: RequirementRow[];
  total: number;
  count: number;
  all: number;
  query: RequirementQuery;
  kinds: Record<string, number>;
}

const REQUIREMENT_RELATIONSHIPS = new Set([
  "addresses",
  "stated_as",
  "satisfied_by",
  "refines",
  "derived_from",
  "conflicts_with",
  "maps_to",
  "applies_to",
]);

export function buildRequirementCatalog(graph: EngineGraphResponse): RequirementCatalog {
  const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
  const products = graph.nodes.filter((node) => node.domain_type === "Product")
    .map((node) => ({ id: node.id, name: node.label }))
    .sort((left, right) => left.name.localeCompare(right.name) || left.id.localeCompare(right.id));
  const established = graph.edges.filter((edge) => (
    isEstablishedRelationship(edge, graph.edges, nodes)
  ));
  const scopes = new Map(products.map((product) => [
    product.id,
    productScope(product.id, established),
  ]));
  const requirements = graph.nodes.filter((node) => node.domain_type === "Requirement")
    .map((node) => requirementRow(node, graph.edges, nodes, products, scopes))
    .sort((left, right) => left.id.localeCompare(right.id));
  const kinds: Record<string, number> = {};
  for (const requirement of requirements) {
    if (requirement.kind) kinds[requirement.kind] = (kinds[requirement.kind] ?? 0) + 1;
  }
  return {
    file: graph.file.split(/[\\/]/).pop() ?? graph.file,
    requirements,
    products,
    kinds,
  };
}

export function queryRequirements(
  catalog: RequirementCatalog,
  query: RequirementQuery,
): RequirementTableResponse {
  const needle = query.search?.trim().toLocaleLowerCase("und");
  const filtered = catalog.requirements.filter((row) => (
    (!needle || [row.id, row.name, row.text, row.sourceRef, row.sourceLocator]
      .filter((value): value is string => typeof value === "string")
      .some((value) => value.toLocaleLowerCase("und").includes(needle)))
    && (!query.kind || row.kind === query.kind)
    && (!query.product || row.applicableProducts.some((product) => product.id === query.product))
  ));
  const rows = [...filtered].sort((left, right) => compareRows(left, right, query));
  const contextualKinds: Record<string, number> = {};
  for (const row of catalog.requirements.filter((candidate) => (
    (!needle || [candidate.id, candidate.name, candidate.text, candidate.sourceRef, candidate.sourceLocator]
      .filter((value): value is string => typeof value === "string")
      .some((value) => value.toLocaleLowerCase("und").includes(needle)))
    && (!query.product || candidate.applicableProducts.some((product) => product.id === query.product))
  ))) {
    if (row.kind) contextualKinds[row.kind] = (contextualKinds[row.kind] ?? 0) + 1;
  }
  const page = rows.slice(query.offset, query.offset + query.limit);
  return {
    rows: page,
    total: rows.length,
    count: page.length,
    all: catalog.requirements.length,
    query: { ...query },
    kinds: contextualKinds,
  };
}

export function isRequirementSort(value: string): value is RequirementSort {
  return (REQUIREMENT_SORTS as readonly string[]).includes(value);
}

function requirementRow(
  node: EngineGraphNode,
  edges: readonly EngineGraphEdge[],
  nodes: ReadonlyMap<string, EngineGraphNode>,
  products: readonly RequirementProduct[],
  scopes: ReadonlyMap<string, ReadonlySet<string>>,
): RequirementRow {
  const establishedIds = new Set(edges.filter((edge) => (
    isEstablishedRelationship(edge, edges, nodes)
  )).map((edge) => edge.id));
  const relationships = edges.flatMap((edge) => {
    if (!REQUIREMENT_RELATIONSHIPS.has(edge.relationship_type)) return [];
    const direction = edge.source === node.id ? "outgoing" : edge.target === node.id ? "incoming" : null;
    if (!direction) return [];
    const targetId = direction === "outgoing" ? edge.target : edge.source;
    const target = nodes.get(targetId);
    const reviewIds = stringValues(edge, "review_ids");
    const statuses = stringValues(edge, "review_statuses");
    const justifications = stringValues(edge, "review_justifications");
    const presentation = relationshipReviewState(edge.properties);
    const assertions: RequirementAssertionEvidence[] = edge.assertions?.map((assertion) => ({
      id: assertion.id,
      status: assertion.assertion_status,
      confidence: assertion.confidence,
      reviewState: relationshipReviewState({
        assertion_status: assertion.assertion_status,
        review_status: combinedReviewStatus(assertion.reviews.map((review) => review.review_status)),
      })?.kind ?? "unknown",
      description: assertion.description,
      evidence: [...assertion.evidence],
      reviews: assertion.reviews.map((review) => ({
        id: review.id,
        status: review.review_status,
        reviewer: review.reviewer,
        justification: review.justification,
      })),
    })) ?? [];
    return [{
      edgeId: edge.id,
      established: establishedIds.has(edge.id),
      authored: edge.authored === true || (
        edge.authored === undefined && !stringValues(edge, "assertion_ids").length
      ),
      direction,
      predicate: edge.relationship_type,
      targetId,
      targetName: target?.label ?? targetId,
      targetType: target?.domain_type ?? "Unknown",
      assertionIds: stringValues(edge, "assertion_ids"),
      assertionStatus: stringValue(edge, "assertion_status"),
      confidence: stringValue(edge, "confidence"),
      reviewState: presentation?.kind ?? "structural",
      descriptions: stringValues(edge, "assertion_descriptions"),
      evidence: stringValues(edge, "assertion_evidence"),
      reviews: reviewIds.map((id, index) => ({
        id,
        status: statuses[index] ?? stringValue(edge, "review_status"),
        reviewer: null,
        justification: justifications[index] ?? null,
      })),
      assertions,
    } satisfies RequirementRelationship];
  }).sort((left, right) => (
    left.predicate.localeCompare(right.predicate) || left.targetId.localeCompare(right.targetId)
  ));
  const authoredOrAccepted = relationships.filter((relationship) => (
    relationship.established
  ));
  const appliesTo = authoredOrAccepted.filter((relationship) => (
    relationship.direction === "outgoing" && relationship.predicate === "applies_to"
  )).map((relationship) => relationship.targetId);
  const families = propertyStrings(node, "applies_to_family");
  const applicableProducts = products.filter((product) => (
    appliesTo.some((target) => scopes.get(product.id)?.has(target))
    || families.some((family) => propertyStrings(nodes.get(product.id), "classifications").includes(family))
  ));
  const mitigations = authoredOrAccepted.filter((relationship) => (
    relationship.direction === "outgoing" && relationship.predicate === "satisfied_by"
  )).map((relationship) => {
    const mitigation = nodes.get(relationship.targetId);
    return {
      id: relationship.targetId,
      name: mitigation?.label ?? relationship.targetId,
      status: propertyString(mitigation, "mitigation_status"),
    };
  });
  return {
    id: node.id,
    name: node.label,
    text: propertyString(node, "text"),
    description: propertyString(node, "description"),
    kind: propertyString(node, "requirement_kind"),
    normativity: propertyString(node, "normativity"),
    textOrigin: propertyString(node, "text_origin"),
    sourceRef: propertyString(node, "source_ref"),
    sourceLocator: propertyString(node, "source_locator"),
    appliesTo,
    appliesToFamilies: families,
    applicableProducts,
    satisfaction: satisfaction(mitigations),
    mitigations,
    relationships,
  };
}

function productScope(product: string, edges: readonly EngineGraphEdge[]): Set<string> {
  const scope = new Set([product]);
  for (const edge of edges) {
    if (edge.relationship_type === "of_product" && edge.target === product) scope.add(edge.source);
  }
  const todo = [...scope];
  while (todo.length) {
    const current = todo.pop()!;
    for (const edge of edges) {
      if (edge.source !== current
        || !["composed_of", "uses_component", "build_composed_of"].includes(edge.relationship_type)
        || scope.has(edge.target)) continue;
      scope.add(edge.target);
      todo.push(edge.target);
    }
  }
  return scope;
}

function satisfaction(mitigations: readonly RequirementMitigation[]): RequirementSatisfaction {
  if (!mitigations.length) return "not_recorded";
  const statuses = new Set(mitigations.map((mitigation) => mitigation.status));
  if (statuses.has("complete")) return "satisfied";
  if (statuses.has("in_progress")) return "in_progress";
  return "unsatisfied";
}

function isEstablishedRelationship(
  edge: EngineGraphEdge,
  edges: readonly EngineGraphEdge[],
  nodes: ReadonlyMap<string, EngineGraphNode>,
): boolean {
  if (edge.authored === true) return true;
  if (edge.assertions?.length) {
    return edge.assertions.some((assertion) => assertionAccepted(assertion.id, edges, nodes));
  }
  const assertionIds = stringValues(edge, "assertion_ids");
  if (!assertionIds.length) return edge.authored !== false;
  return normalized(stringValue(edge, "assertion_status")) === "accepted"
    && assertionIds.some((id) => assertionAccepted(id, edges, nodes));
}

function assertionAccepted(
  assertionId: string,
  edges: readonly EngineGraphEdge[],
  nodes: ReadonlyMap<string, EngineGraphNode>,
): boolean {
  if (normalized(propertyString(nodes.get(assertionId), "assertion_status")) !== "accepted") {
    return false;
  }
  const humanReviews = edges.filter((edge) => (
    edge.relationship_type === "reviews" && edge.target === assertionId
  )).map((edge) => nodes.get(edge.source))
    .filter((review): review is EngineGraphNode => (
      review?.domain_type === "Review" && edges.some((candidate) => (
        candidate.source === review.id
        && candidate.relationship_type === "reviewer"
        && nodes.get(candidate.target)?.domain_type === "Party"
        && normalized(propertyString(nodes.get(candidate.target), "party_kind")) === "person"
      ))
    ));
  return humanReviews.length > 0 && humanReviews.every((review) => (
    normalized(propertyString(review, "review_status")) === "accepted"
    && Boolean(propertyString(review, "justification")?.trim())
  ));
}

function combinedReviewStatus(statuses: readonly (string | null)[]): string | null {
  const values = statuses.map(normalized).filter((status): status is string => Boolean(status));
  if (values.includes("rejected")) return "rejected";
  if (values.includes("changes_requested")) return "changes_requested";
  if (values.length > 0 && values.every((status) => status === "accepted")) return "accepted";
  return new Set(values).size === 1 ? values[0] : values.length ? "mixed" : null;
}

function compareRows(left: RequirementRow, right: RequirementRow, query: RequirementQuery): number {
  const value = (row: RequirementRow): string => {
    switch (query.sort) {
      case "id": return row.id;
      case "name": return row.name;
      case "kind": return row.kind ?? "";
      case "normativity": return row.normativity ?? "";
      case "source": return `${row.sourceRef ?? ""} ${row.sourceLocator ?? ""}`;
      case "satisfaction": return row.satisfaction;
    }
  };
  const compared = value(left).localeCompare(value(right), undefined, { numeric: true });
  return (query.order === "asc" ? compared : -compared) || left.id.localeCompare(right.id);
}

function stringValue(edge: EngineGraphEdge, key: string): string | null {
  const value = edge.properties[key];
  return typeof value === "string" ? value : null;
}

function stringValues(edge: EngineGraphEdge, key: string): string[] {
  const value = edge.properties[key];
  if (typeof value === "string") return [value];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function propertyString(node: EngineGraphNode | undefined, key: string): string | null {
  const value = node?.properties[key];
  return typeof value === "string" ? value : null;
}

function propertyStrings(node: EngineGraphNode | undefined, key: string): string[] {
  const value = node?.properties[key];
  if (typeof value === "string") return [value];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function normalized(value: string | null): string | undefined {
  const result = value?.trim().toLowerCase().replace(/[\s-]+/g, "_");
  return result || undefined;
}
