import { staticDataBase } from "./app-mode";
import type { GraphPropertyValue } from "./graph-types";
import type { EngineGraphEdge, EngineGraphNode, EngineGraphResponse } from "./model-types";
import {
  buildRequirementCatalog,
  combineRequirementCatalogs,
  type RequirementCatalog,
  type RequirementCatalogSource,
} from "./requirements-model";

const EXPECTED_SOURCES: Readonly<Record<string, number>> = {
  "owasp-asvs-5": 34,
  "eu-cra-2024-2847": 23,
  "iec-62443-4-1-2018": 52,
};
const EXPECTED_TOTAL = 109;

export interface RequirementStandardsSource {
  readonly notice: string;
  getCatalog(signal?: AbortSignal): Promise<RequirementCatalog>;
}

/** The same generated Vite public asset serves desktop and GitHub Pages. */
export class StaticRequirementStandardsSource implements RequirementStandardsSource {
  readonly notice = "Extracted standards catalog · 109 entries · not assigned to the selected model";

  constructor(
    private readonly url = new URL("requirements/catalog.json", staticDataBase()).href,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async getCatalog(signal?: AbortSignal): Promise<RequirementCatalog> {
    const response = await this.fetchImpl(this.url, { signal });
    if (!response.ok) throw new Error(`Standards catalog request failed: HTTP ${response.status}`);
    return parseRequirementStandardsCatalog(await response.json());
  }
}

export function parseRequirementStandardsCatalog(value: unknown): RequirementCatalog {
  if (!isObject(value) || value.schema_version !== 1
    || value.name !== "Extracted Standards Catalog"
    || value.count !== EXPECTED_TOTAL || !Array.isArray(value.sources)) {
    throw malformed("expected the version 1, 109-entry catalog envelope");
  }
  const sources = value.sources.map(parseSource);
  const sourceIds = sources.map((source) => source.metadata.id);
  if (new Set(sourceIds).size !== sourceIds.length) throw malformed("duplicate source ids");
  for (const [id, expected] of Object.entries(EXPECTED_SOURCES)) {
    const source = sources.find((candidate) => candidate.metadata.id === id);
    if (!source || source.metadata.count !== expected) {
      throw malformed(`${id} must contain ${expected} Requirements`);
    }
  }
  if (sources.length !== Object.keys(EXPECTED_SOURCES).length) {
    throw malformed("unexpected standards source");
  }

  const catalogs = sources.map(({ metadata, graph }) => buildRequirementCatalog(graph, {
    id: metadata.id,
    name: metadata.name,
    version: metadata.version,
  }));
  const result = combineRequirementCatalogs("extracted-standards-catalog.json", catalogs);
  if (result.requirements.length !== EXPECTED_TOTAL) {
    throw malformed(`expected ${EXPECTED_TOTAL} unique Requirements`);
  }
  return result;
}

function parseSource(value: unknown): {
  metadata: RequirementCatalogSource;
  graph: EngineGraphResponse;
} {
  if (!isObject(value) || typeof value.id !== "string" || typeof value.name !== "string"
    || typeof value.version !== "string" || !nonnegativeInteger(value.count)
    || !isGraph(value.graph)) {
    throw malformed("invalid source entry");
  }
  const requirementCount = value.graph.nodes.filter((node) => node.domain_type === "Requirement").length;
  if (requirementCount !== value.count) {
    throw malformed(`${value.id} count contradicts its graph`);
  }
  return {
    metadata: {
      id: value.id,
      name: value.name,
      version: value.version,
      count: value.count,
    },
    graph: value.graph,
  };
}

function isGraph(value: unknown): value is EngineGraphResponse {
  return isObject(value) && typeof value.file === "string"
    && Array.isArray(value.nodes) && value.nodes.every(isNode)
    && Array.isArray(value.edges) && value.edges.every(isEdge);
}

function isNode(value: unknown): value is EngineGraphNode {
  return isObject(value) && typeof value.id === "string"
    && typeof value.domain_type === "string" && typeof value.label === "string"
    && isProperties(value.properties);
}

function isEdge(value: unknown): value is EngineGraphEdge {
  return isObject(value) && ["id", "source", "target", "relationship_type"]
    .every((key) => typeof value[key] === "string")
    && (value.authored === undefined || typeof value.authored === "boolean")
    && isProperties(value.properties) && Array.isArray(value.assertions)
    && value.assertions.every((assertion) => isObject(assertion)
      && typeof assertion.id === "string"
      && (assertion.assertion_status === null || typeof assertion.assertion_status === "string")
      && (assertion.confidence === null || typeof assertion.confidence === "string")
      && (assertion.description === null || typeof assertion.description === "string")
      && stringArray(assertion.evidence) && Array.isArray(assertion.reviews)
      && assertion.reviews.every((review) => isObject(review)
        && typeof review.id === "string"
        && (review.review_status === null || typeof review.review_status === "string")
        && (review.reviewer === null || typeof review.reviewer === "string")
        && (review.justification === null || typeof review.justification === "string")));
}

function isProperties(value: unknown): value is Readonly<Record<string, GraphPropertyValue>> {
  return isObject(value) && Object.values(value).every((item) => (
    item === null || typeof item === "string" || typeof item === "number"
    || typeof item === "boolean" || stringArray(item)
  ));
}

function stringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function nonnegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function malformed(detail: string): Error {
  return new Error(`Extracted standards catalog is malformed: ${detail}`);
}
