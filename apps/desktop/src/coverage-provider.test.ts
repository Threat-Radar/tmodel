import { describe, expect, it, vi } from "vitest";
import {
  calculateCoverageFallback,
  CompatibleCoverageProvider,
  parseCoverageResponse,
} from "./coverage-provider";
import { REQUIREMENTS_GRAPH } from "./requirements-fixture.test-support";
import type { EngineGraphEdge, EngineGraphNode } from "./model-types";

describe("PR #243-compatible coverage provider", () => {
  const fallback = calculateCoverageFallback(REQUIREMENTS_GRAPH, "product:tcu");

  it("computes conservative recorded and hypothetical coverage", () => {
    expect(fallback).toMatchObject({
      file: "mvp-02-automotive-ecu.yaml",
      product: "product:tcu",
      count: 2,
      counts: { satisfied: 1, in_progress: 0, unsatisfied: 1 },
      unaddressed_threats: ["threat:two"],
      proposed_assertions: [{
        id: "assertion:proposal",
        assertion_status: "proposed",
        effect: "individual",
        review_ids: ["review:proposal"],
      }],
      excluded_assertions: [],
    });
    expect(fallback.if_all_proposed_accepted.unaddressed_threats).toEqual([]);
    expect(fallback.interpretation).toContain("not verified compliance");
  });

  it("accepts a valid PR #243 response and rejects malformed response shapes", () => {
    expect(parseCoverageResponse(structuredClone(fallback))).toEqual(fallback);
    expect(() => parseCoverageResponse({ ...fallback, count: 99 }))
      .toThrow("malformed response");
    expect(() => parseCoverageResponse({ interpretation: "missing everything else" }))
      .toThrow("malformed response");
  });

  it("rejects totals that do not equal count", () => {
    expect(() => parseCoverageResponse({
      ...structuredClone(fallback),
      counts: { ...fallback.counts, satisfied: 999 },
    })).toThrow("status totals do not equal count");
  });

  it("rejects status counts that contradict the Requirement rows", () => {
    expect(() => parseCoverageResponse({
      ...structuredClone(fallback),
      counts: { satisfied: 0, in_progress: 1, unsatisfied: 1 },
    })).toThrow("satisfied count contradicts its Requirements");
  });

  it("validates joint and individual hypothetical answers", () => {
    const invalidJoint = structuredClone(fallback);
    invalidJoint.if_all_proposed_accepted.counts.satisfied += 1;
    expect(() => parseCoverageResponse(invalidJoint)).toThrow("joint hypothetical status totals");

    const invalidIndividual = structuredClone(fallback);
    invalidIndividual.proposed_assertions[0].if_accepted.counts.satisfied += 1;
    expect(() => parseCoverageResponse(invalidIndividual))
      .toThrow("hypothetical for assertion:proposal status totals");
  });

  it("rejects duplicate Requirement and proposal ids", () => {
    const duplicateRequirement = structuredClone(fallback);
    duplicateRequirement.requirements = [
      structuredClone(fallback.requirements[0]),
      structuredClone(fallback.requirements[0]),
    ];
    duplicateRequirement.count = 2;
    duplicateRequirement.counts = { satisfied: 2, in_progress: 0, unsatisfied: 0 };
    expect(() => parseCoverageResponse(duplicateRequirement))
      .toThrow("duplicate Requirement ids");

    const duplicateProposal = structuredClone(fallback);
    duplicateProposal.proposed_assertions.push(structuredClone(fallback.proposed_assertions[0]));
    expect(() => parseCoverageResponse(duplicateProposal)).toThrow("duplicate ids");
  });

  it("uses the endpoint when available", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => new Response(JSON.stringify(fallback), {
      status: 200, headers: { "Content-Type": "application/json" },
    }));
    const graphProvider = { getModelGraph: vi.fn(async () => REQUIREMENTS_GRAPH) };
    const provider = new CompatibleCoverageProvider(
      "mvp-02-automotive-ecu.yaml", graphProvider, "http://127.0.0.1:8765", fetchMock,
    );

    const result = await provider.getCoverage("product:tcu");
    expect(result.source).toBe("engine");
    expect(graphProvider.getModelGraph).not.toHaveBeenCalled();
    expect(String(fetchMock.mock.calls[0][0])).toContain("/coverage?");
  });

  it.each([
    ["product", { product: "product:other" }, "does not match requested"],
    ["file", { file: "other-model.yaml" }, "does not match requested"],
  ] as const)("rejects a successful response for the wrong %s without falling back", async (
    _field,
    mismatch,
    message,
  ) => {
    const fetchMock = vi.fn<typeof fetch>(async () => new Response(JSON.stringify({
      ...structuredClone(fallback),
      ...mismatch,
    }), { status: 200, headers: { "Content-Type": "application/json" } }));
    const graphProvider = { getModelGraph: vi.fn(async () => REQUIREMENTS_GRAPH) };
    const provider = new CompatibleCoverageProvider(
      "/models/mvp-02-automotive-ecu.yaml",
      graphProvider,
      "http://127.0.0.1:8765",
      fetchMock,
    );

    await expect(provider.getCoverage("product:tcu")).rejects.toThrow(message);
    expect(graphProvider.getModelGraph).not.toHaveBeenCalled();
  });

  it("falls back only for a missing endpoint", async () => {
    const graphProvider = { getModelGraph: vi.fn(async () => REQUIREMENTS_GRAPH) };
    const provider = new CompatibleCoverageProvider(
      "mvp-02-automotive-ecu.yaml",
      graphProvider,
      "https://example.test/engine",
      vi.fn<typeof fetch>(async () => new Response("not found", { status: 404 })),
    );
    const result = await provider.getCoverage("product:tcu");
    expect(result.source).toBe("frontend-fallback");
    expect(result.notice).toContain("PR #243");
    expect(graphProvider.getModelGraph).toHaveBeenCalledTimes(1);
  });

  it("keeps non-404 engine failures visible", async () => {
    const graphProvider = { getModelGraph: vi.fn(async () => REQUIREMENTS_GRAPH) };
    const provider = new CompatibleCoverageProvider(
      "mvp-02-automotive-ecu.yaml",
      graphProvider,
      "https://example.test/engine",
      vi.fn<typeof fetch>(async () => new Response(JSON.stringify({ error: "model invalid" }), {
        status: 500, headers: { "Content-Type": "application/json" },
      })),
    );
    await expect(provider.getCoverage("product:tcu")).rejects.toThrow("model invalid");
    expect(graphProvider.getModelGraph).not.toHaveBeenCalled();
  });

  it("keeps authored satisfied_by baseline coverage when a proposed Assertion shares the triple", () => {
    const graph = mutableGraph();
    const proposed = assertedEdge(graph);
    graph.edges = graph.edges.filter((edge) => edge !== proposed);
    const satisfied = graph.edges.find((edge) => edge.relationship_type === "satisfied_by");
    if (!satisfied) throw new Error("fixture lost satisfied_by");
    attachAssertion(satisfied, "assertion:proposal", "proposed");

    const result = calculateCoverageFallback(graph, "product:tcu");
    expect(result.counts).toEqual({ satisfied: 1, in_progress: 0, unsatisfied: 1 });
    expect(result.proposed_assertions).toEqual([]);
    expect(result.if_all_proposed_accepted).toEqual(expect.objectContaining({
      counts: result.counts,
    }));
  });

  it("keeps an authored addresses baseline link despite a rejected Assertion on the triple", () => {
    const graph = mutableGraph();
    const addresses = graph.edges.find((edge) => (
      edge.relationship_type === "addresses" && edge.target === "threat:one"
    ));
    if (!addresses) throw new Error("fixture lost authored addresses");
    graph.nodes.push(assertionNode("assertion:rejected", "rejected"));
    attachAssertion(addresses, "assertion:rejected", "rejected");

    const result = calculateCoverageFallback(graph, "product:tcu");
    expect(result.requirements.find((row) => row.id === "requirement:family")?.addressed_threats)
      .toEqual(["threat:one"]);
    expect(result.excluded_assertions).toContain("assertion:rejected");
  });

  it("uses an Assertion-only link only after justified unanimous human acceptance", () => {
    const graph = mutableGraph();
    setProposalVerdict(graph, "accepted", "accepted");
    const accepted = calculateCoverageFallback(graph, "product:tcu");
    expect(accepted.unaddressed_threats).toEqual([]);
    expect(accepted.proposed_assertions).toEqual([]);

    graph.nodes.push({
      id: "review:conflict",
      domain_type: "Review",
      label: "Conflicting human review",
      properties: { review_status: "rejected", justification: "The evidence is insufficient." },
    });
    graph.edges.push(
      edge("review:conflict", "reviews", "assertion:proposal"),
      edge("review:conflict", "reviewer", "party:human"),
    );
    const conflicted = calculateCoverageFallback(graph, "product:tcu");
    expect(conflicted.unaddressed_threats).toEqual(["threat:two"]);
    expect(conflicted.excluded_assertions).toContain("assertion:proposal");
  });

  it("keeps multiple proposed Assertions on one edge distinct", () => {
    const graph = mutableGraph();
    const asserted = assertedEdge(graph);
    graph.nodes.push(assertionNode("assertion:second", "proposed"));
    attachAssertion(asserted, "assertion:second", "proposed", "Second independent basis.");

    const result = calculateCoverageFallback(graph, "product:tcu");
    expect(result.proposed_assertions.map((proposal) => proposal.id)).toEqual([
      "assertion:proposal", "assertion:second",
    ]);
    expect(asserted.assertions?.map((assertion) => ({
      id: assertion.id,
      description: assertion.description,
      reviews: assertion.reviews.map((review) => review.id),
    }))).toEqual([
      {
        id: "assertion:proposal",
        description: "Analytical relationship awaiting a decision.",
        reviews: ["review:proposal"],
      },
      { id: "assertion:second", description: "Second independent basis.", reviews: [] },
    ]);
  });
});

type MutableGraph = {
  file: string;
  nodes: EngineGraphNode[];
  edges: EngineGraphEdge[];
};

function mutableGraph(): MutableGraph {
  return structuredClone(REQUIREMENTS_GRAPH) as MutableGraph;
}

function assertedEdge(graph: MutableGraph): EngineGraphEdge {
  const result = graph.edges.find((candidate) => candidate.assertions?.length);
  if (!result) throw new Error("fixture lost asserted edge");
  return result;
}

function assertionNode(id: string, status: string): EngineGraphNode {
  return {
    id,
    domain_type: "Assertion",
    label: id,
    properties: { assertion_status: status, confidence: "medium" },
  };
}

function attachAssertion(
  target: EngineGraphEdge,
  id: string,
  status: string,
  description = "Additional analytical basis.",
): void {
  target.assertions = [
    ...(target.assertions ?? []),
    {
      id,
      assertion_status: status,
      confidence: "medium",
      description,
      evidence: [`Evidence for ${id}`],
      reviews: [],
    },
  ];
  target.properties = {
    ...target.properties,
    assertion_ids: target.assertions.map((assertion) => assertion.id),
    ...(target.assertions.length === 1 ? { assertion_status: status } : {}),
  };
}

function setProposalVerdict(
  graph: MutableGraph,
  assertionStatus: string,
  reviewStatus: string,
): void {
  const assertion = graph.nodes.find((node) => node.id === "assertion:proposal");
  const review = graph.nodes.find((node) => node.id === "review:proposal");
  const asserted = assertedEdge(graph);
  if (!assertion || !review || !asserted.assertions) throw new Error("fixture lost proposal");
  assertion.properties = { ...assertion.properties, assertion_status: assertionStatus };
  review.properties = { ...review.properties, review_status: reviewStatus };
  asserted.assertions = asserted.assertions.map((item) => ({
    ...item,
    assertion_status: assertionStatus,
    reviews: item.reviews.map((itemReview) => ({
      ...itemReview,
      review_status: reviewStatus,
    })),
  }));
  asserted.properties = {
    ...asserted.properties,
    assertion_status: assertionStatus,
    review_status: reviewStatus,
  };
}

function edge(source: string, relationship_type: string, target: string): EngineGraphEdge {
  return {
    id: `relationship:${source}|${relationship_type}|${target}`,
    source,
    relationship_type,
    target,
    authored: true,
    assertions: [],
    properties: {},
  };
}
