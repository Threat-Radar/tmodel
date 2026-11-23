import { DEFAULT_ENGINE_URL } from "./engine";
import type { EngineGraphDataProvider } from "./engine-graph-provider";
import type { EngineGraphEdge, EngineGraphNode, EngineGraphResponse } from "./model-types";

export type CoverageStatus = "satisfied" | "in_progress" | "unsatisfied";

export interface CoverageMitigation {
  id: string;
  status: string | null;
}

export interface CoverageRequirement {
  id: string;
  name: string;
  status: CoverageStatus;
  scope: { applies_to: string[]; families: string[] };
  mitigations: CoverageMitigation[];
  addressed_threats: string[];
}

export interface CoverageAnswer {
  requirements: CoverageRequirement[];
  count: number;
  counts: Record<CoverageStatus, number>;
  scope: string[];
  unaddressed_threats: string[];
}

export interface CoverageProposal {
  id: string;
  subject: string;
  predicate: string;
  object: string;
  assertion_status: "proposed";
  review_ids: string[];
  effect: "individual" | "with_other_proposals";
  if_accepted: CoverageAnswer;
}

export interface CoverageResponse extends CoverageAnswer {
  file: string;
  product: string;
  proposed_assertions: CoverageProposal[];
  if_all_proposed_accepted: CoverageAnswer;
  excluded_assertions: string[];
  interpretation: string;
}

export interface CoverageLoadResult {
  response: CoverageResponse;
  source: "engine" | "frontend-fallback";
  notice: string;
}

const COVERAGE_LINKS = new Set(["applies_to", "satisfied_by", "addresses"]);
const SCOPE_LINKS = new Set(["composed_of", "uses_component", "build_composed_of"]);

/**
 * PR #243-compatible coverage client. Until `/coverage` lands, a 404 uses a
 * conservative, read-only projection of the already-loaded graph. Other API
 * failures stay visible instead of silently changing semantics.
 */
export class CompatibleCoverageProvider {
  constructor(
    private readonly file: string,
    private readonly graphProvider: Pick<EngineGraphDataProvider, "getModelGraph">,
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async getCoverage(product: string, signal?: AbortSignal): Promise<CoverageLoadResult> {
    const url = new URL("/coverage", `${this.baseUrl.replace(/\/$/, "")}/`);
    url.searchParams.set("file", this.file);
    url.searchParams.set("product", product);
    const response = await this.fetchImpl(url, { signal });
    if (response.ok) {
      const parsed = parseCoverageResponse(await response.json());
      validateCoverageIdentity(parsed, this.file, product);
      return {
        response: parsed,
        source: "engine",
        notice: "Recorded coverage from the local engine `/coverage` query.",
      };
    }
    if (response.status !== 404) {
      let detail = `HTTP ${response.status}`;
      try {
        const body = await response.json() as { error?: unknown };
        if (typeof body.error === "string") detail = body.error;
      } catch {
        // Retain the HTTP status when the engine did not return JSON.
      }
      throw new Error(`Coverage request failed: ${detail}`);
    }
    const graph = await this.graphProvider.getModelGraph();
    return {
      response: calculateCoverageFallback(graph, product),
      source: "frontend-fallback",
      notice: "Frontend fallback computed from this example model because `/coverage` is not available yet; response shape follows PR #243.",
    };
  }
}

/** PR #243's exact response shape, guarded before it reaches the UI. */
export function parseCoverageResponse(value: unknown): CoverageResponse {
  if (!isObject(value) || typeof value.file !== "string" || typeof value.product !== "string"
    || typeof value.interpretation !== "string" || !isCoverageAnswer(value)
    || !Array.isArray(value.proposed_assertions)
    || !value.proposed_assertions.every(isCoverageProposal)
    || !isCoverageAnswer(value.if_all_proposed_accepted)
    || !isStringArray(value.excluded_assertions)) {
    throw new Error("Coverage endpoint returned a malformed response");
  }
  const response = value as unknown as CoverageResponse;
  validateCoverageAnswer(response, "baseline");
  validateCoverageAnswer(response.if_all_proposed_accepted, "joint hypothetical");
  const proposalIds = response.proposed_assertions.map((proposal) => proposal.id);
  if (new Set(proposalIds).size !== proposalIds.length) {
    throw malformed("proposed_assertions contains duplicate ids");
  }
  for (const proposal of response.proposed_assertions) {
    validateCoverageAnswer(proposal.if_accepted, `hypothetical for ${proposal.id}`);
  }
  return response;
}

/**
 * Temporary mvp-02/browser-preview fallback. It mirrors PR #243's documented
 * collector without promoting proposed Assertions or claiming compliance.
 */
export function calculateCoverageFallback(
  graph: EngineGraphResponse,
  product: string,
): CoverageResponse {
  const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
  if (nodes.get(product)?.domain_type !== "Product") throw new Error(`unknown product: ${product}`);

  const assertions = new Map(
    graph.nodes.filter((node) => node.domain_type === "Assertion").map((node) => [node.id, node]),
  );
  const reviewEdges = graph.edges.filter((edge) => edge.relationship_type === "reviews");
  const reviewerEdges = graph.edges.filter((edge) => edge.relationship_type === "reviewer");
  const reviewsFor = (assertion: string) => reviewEdges
    .filter((edge) => edge.target === assertion)
    .map((edge) => nodes.get(edge.source))
    .filter((node): node is EngineGraphNode => node?.domain_type === "Review");
  const humanAccepted = (assertion: string): boolean => {
    const human = reviewsFor(assertion).filter((review) => reviewerEdges
      .filter((edge) => edge.source === review.id)
      .map((edge) => nodes.get(edge.target))
      .some((party) => party?.domain_type === "Party"
        && normalized(propertyString(party, "party_kind")) === "person"));
    return human.length > 0 && human.every((review) => (
      normalized(propertyString(review, "review_status")) === "accepted"
      && Boolean(propertyString(review, "justification")?.trim())
    ));
  };
  const assertionAccepted = (id: string): boolean => (
    normalized(propertyString(assertions.get(id), "assertion_status")) === "accepted"
    && humanAccepted(id)
  );

  const semantic = graph.edges.filter((edge) => (
    COVERAGE_LINKS.has(edge.relationship_type)
    || SCOPE_LINKS.has(edge.relationship_type)
    || edge.relationship_type === "of_product"
  ));
  const established = new Set<string>();
  const pending: Array<{ assertion: string; edge: EngineGraphEdge }> = [];
  const excluded = new Set<string>();
  for (const edge of semantic) {
    const provenance = new Map(edge.assertions?.map((assertion) => [assertion.id, assertion]) ?? []);
    const ids = edge.assertions?.map((assertion) => assertion.id)
      ?? propertyStrings(edge, "assertion_ids");
    const authored = edge.authored === true || (edge.authored === undefined && !ids.length);
    if (authored) established.add(edgeKey(edge));
    for (const id of ids) {
      const status = normalized(propertyString(assertions.get(id), "assertion_status")
        ?? provenance.get(id)?.assertion_status
        ?? (ids.length === 1 ? propertyStringFromEdge(edge, "assertion_status") : undefined));
      if (assertionAccepted(id)) established.add(edgeKey(edge));
      else if (status === "proposed" && COVERAGE_LINKS.has(edge.relationship_type)) {
        pending.push({ assertion: id, edge });
      } else if (COVERAGE_LINKS.has(edge.relationship_type)) excluded.add(id);
    }
  }

  const answer = (relations: ReadonlySet<string>): CoverageAnswer => {
    const targets = (subject: string, predicate: string): Set<string> => new Set(
      semantic.filter((edge) => relations.has(edgeKey(edge))
        && edge.source === subject && edge.relationship_type === predicate)
        .map((edge) => edge.target),
    );
    const scope = new Set([product]);
    for (const edge of semantic) {
      if (relations.has(edgeKey(edge)) && edge.relationship_type === "of_product"
        && edge.target === product) scope.add(edge.source);
    }
    const todo = [...scope];
    while (todo.length) {
      const current = todo.pop()!;
      for (const predicate of SCOPE_LINKS) {
        for (const child of targets(current, predicate)) {
          if (!scope.has(child)) {
            scope.add(child);
            todo.push(child);
          }
        }
      }
    }
    const families = new Set(propertyStringsFromNode(nodes.get(product), "classifications"));
    const rows: CoverageRequirement[] = [];
    const addressed = new Set<string>();
    for (const requirement of [...nodes.values()]
      .filter((node) => node.domain_type === "Requirement")
      .sort((left, right) => left.id.localeCompare(right.id))) {
      const concrete = [...targets(requirement.id, "applies_to")]
        .filter((id) => scope.has(id)).sort();
      const matchedFamilies = propertyStringsFromNode(requirement, "applies_to_family")
        .filter((family) => families.has(family)).sort();
      if (!concrete.length && !matchedFamilies.length) continue;
      const mitigations = [...targets(requirement.id, "satisfied_by")].sort().map((id) => ({
        id,
        status: propertyString(nodes.get(id), "mitigation_status") ?? null,
      }));
      const statuses = new Set(mitigations.map((mitigation) => mitigation.status));
      const status: CoverageStatus = statuses.has("complete")
        ? "satisfied"
        : statuses.has("in_progress") ? "in_progress" : "unsatisfied";
      const threats = [...targets(requirement.id, "addresses")]
        .filter((id) => nodes.get(id)?.domain_type === "ThreatInstance").sort();
      threats.forEach((id) => addressed.add(id));
      rows.push({
        id: requirement.id,
        name: requirement.label,
        status,
        scope: { applies_to: concrete, families: matchedFamilies },
        mitigations,
        addressed_threats: threats,
      });
    }
    const threats = [...nodes.values()]
      .filter((node) => node.domain_type === "ThreatInstance").map((node) => node.id).sort();
    return {
      requirements: rows,
      count: rows.length,
      counts: {
        satisfied: rows.filter((row) => row.status === "satisfied").length,
        in_progress: rows.filter((row) => row.status === "in_progress").length,
        unsatisfied: rows.filter((row) => row.status === "unsatisfied").length,
      },
      scope: [...scope].sort(),
      unaddressed_threats: threats.filter((id) => !addressed.has(id)),
    };
  };

  const baseline = answer(established);
  const allPending = new Set([...established, ...pending.map(({ edge }) => edgeKey(edge))]);
  const joint = answer(allPending);
  const proposals: CoverageProposal[] = [];
  for (const { assertion, edge } of pending.sort((a, b) => a.assertion.localeCompare(b.assertion))) {
    const individual = answer(new Set([...established, edgeKey(edge)]));
    const others = new Set([...established, ...pending
      .filter((candidate) => candidate.assertion !== assertion)
      .map((candidate) => edgeKey(candidate.edge))]);
    if (sameAnswer(individual, baseline) && sameAnswer(answer(others), joint)) continue;
    proposals.push({
      id: assertion,
      subject: edge.source,
      predicate: edge.relationship_type,
      object: edge.target,
      assertion_status: "proposed",
      review_ids: reviewsFor(assertion).map((review) => review.id).sort(),
      effect: sameAnswer(individual, baseline) ? "with_other_proposals" : "individual",
      if_accepted: individual,
    });
  }
  return {
    file: graph.file.split(/[\\/]/).pop() ?? graph.file,
    product,
    ...baseline,
    proposed_assertions: proposals,
    if_all_proposed_accepted: joint,
    excluded_assertions: [...excluded].sort(),
    interpretation: "Recorded requirement coverage; not verified compliance. Threat gaps include every ThreatInstance in this model, including hypotheses.",
  };
}

function isCoverageAnswer(value: unknown): value is CoverageAnswer {
  return isObject(value) && Array.isArray(value.requirements)
    && value.requirements.every(isCoverageRequirement)
    && isNonnegativeInteger(value.count)
    && isCoverageCounts(value.counts) && isStringArray(value.scope)
    && isStringArray(value.unaddressed_threats);
}

function validateCoverageAnswer(answer: CoverageAnswer, context: string): void {
  if (answer.count !== answer.requirements.length) {
    throw malformed(`${context} count does not match its Requirements`);
  }
  const ids = answer.requirements.map((requirement) => requirement.id);
  if (new Set(ids).size !== ids.length) {
    throw malformed(`${context} contains duplicate Requirement ids`);
  }
  const total = answer.counts.satisfied + answer.counts.in_progress + answer.counts.unsatisfied;
  if (total !== answer.count) {
    throw malformed(`${context} status totals do not equal count`);
  }
  for (const status of ["satisfied", "in_progress", "unsatisfied"] as const) {
    const observed = answer.requirements.filter((requirement) => requirement.status === status).length;
    if (answer.counts[status] !== observed) {
      throw malformed(`${context} ${status} count contradicts its Requirements`);
    }
  }
}

function validateCoverageIdentity(response: CoverageResponse, requestedFile: string, product: string): void {
  if (response.product !== product) {
    throw malformed(`product ${JSON.stringify(response.product)} does not match requested ${JSON.stringify(product)}`);
  }
  const returnedFile = fileName(response.file);
  const expectedFile = fileName(requestedFile);
  if (returnedFile !== expectedFile) {
    throw malformed(`file ${JSON.stringify(returnedFile)} does not match requested ${JSON.stringify(expectedFile)}`);
  }
}

function fileName(value: string): string {
  return value.split(/[\\/]/).pop() ?? value;
}

function malformed(detail: string): Error {
  return new Error(`Coverage endpoint returned a malformed response: ${detail}`);
}

function isCoverageRequirement(value: unknown): value is CoverageRequirement {
  return isObject(value) && typeof value.id === "string" && typeof value.name === "string"
    && ["satisfied", "in_progress", "unsatisfied"].includes(String(value.status))
    && isObject(value.scope) && isStringArray(value.scope.applies_to)
    && isStringArray(value.scope.families) && Array.isArray(value.mitigations)
    && value.mitigations.every((item) => isObject(item) && typeof item.id === "string"
      && (item.status === null || typeof item.status === "string"))
    && isStringArray(value.addressed_threats);
}

function isCoverageProposal(value: unknown): value is CoverageProposal {
  return isObject(value) && ["id", "subject", "predicate", "object"]
    .every((key) => typeof value[key] === "string")
    && value.assertion_status === "proposed" && isStringArray(value.review_ids)
    && (value.effect === "individual" || value.effect === "with_other_proposals")
    && isCoverageAnswer(value.if_accepted);
}

function isCoverageCounts(value: unknown): value is Record<CoverageStatus, number> {
  return isObject(value) && ["satisfied", "in_progress", "unsatisfied"]
    .every((key) => isNonnegativeInteger(value[key]));
}

function edgeKey(edge: Pick<EngineGraphEdge, "source" | "relationship_type" | "target">): string {
  return `${edge.source}\u0000${edge.relationship_type}\u0000${edge.target}`;
}

function propertyString(node: EngineGraphNode | undefined, key: string): string | undefined {
  const value = node?.properties[key];
  return typeof value === "string" ? value : undefined;
}

function propertyStringFromEdge(edge: EngineGraphEdge, key: string): string | undefined {
  const value = edge.properties[key];
  return typeof value === "string" ? value : undefined;
}

function propertyStrings(edge: EngineGraphEdge, key: string): string[] {
  const value = edge.properties[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function propertyStringsFromNode(node: EngineGraphNode | undefined, key: string): string[] {
  const value = node?.properties[key];
  if (typeof value === "string") return [value];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function normalized(value: string | undefined): string | undefined {
  const result = value?.trim().toLowerCase().replace(/[\s-]+/g, "_");
  return result || undefined;
}

function sameAnswer(left: CoverageAnswer, right: CoverageAnswer): boolean {
  return JSON.stringify(left) === JSON.stringify(right);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isNonnegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}
