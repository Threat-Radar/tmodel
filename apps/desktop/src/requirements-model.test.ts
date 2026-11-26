import { describe, expect, it } from "vitest";
import { buildRequirementCatalog, queryRequirements } from "./requirements-model";
import {
  REQUIREMENTS_GRAPH,
  requirementsGraphWithEverySatisfactionState,
} from "./requirements-fixture.test-support";

describe("requirements table model", () => {
  const catalog = buildRequirementCatalog(REQUIREMENTS_GRAPH);

  it("preserves source attribution, scope, satisfaction, Assertions, and Reviews", () => {
    const family = catalog.requirements.find((row) => row.id === "requirement:family");
    const component = catalog.requirements.find((row) => row.id === "requirement:component");

    expect(family).toMatchObject({
      sourceRef: "library:test#R1",
      sourceLocator: "R1",
      applicableProducts: [{ id: "product:tcu", name: "TCU" }],
      satisfaction: "satisfied",
    });
    expect(component?.relationships.find((relationship) => relationship.predicate === "addresses"))
      .toMatchObject({
        assertionIds: ["assertion:proposal"],
        assertionStatus: "proposed",
        established: false,
        reviewState: "proposed",
        evidence: ["The threat follows the diagnostic command path."],
        reviews: [{ id: "review:proposal", status: "pending", reviewer: null }],
        assertions: [{
          id: "assertion:proposal",
          status: "proposed",
          evidence: ["The threat follows the diagnostic command path."],
          reviews: [{ id: "review:proposal", status: "pending", reviewer: "party:human" }],
        }],
      });
    expect(component?.satisfaction).toBe("not_recorded");
  });

  it("searches source and text and filters by kind and product without inventing scope", () => {
    const searched = queryRequirements(catalog, {
      search: "clause 2", sort: "id", order: "asc", limit: 25, offset: 0,
    });
    expect(searched.rows.map((row) => row.id)).toEqual(["requirement:component"]);

    const scoped = queryRequirements(catalog, {
      kind: "technical", product: "product:tcu", sort: "id", order: "asc", limit: 25, offset: 0,
    });
    expect(scoped.rows.map((row) => row.id)).toEqual([
      "requirement:component", "requirement:family",
    ]);
    expect(scoped.rows.some((row) => row.id === "requirement:unscoped")).toBe(false);
  });

  it("sorts and paginates deterministically", () => {
    const first = queryRequirements(catalog, {
      sort: "name", order: "desc", limit: 2, offset: 0,
    });
    const second = queryRequirements(catalog, {
      sort: "name", order: "desc", limit: 2, offset: 2,
    });
    expect(first.total).toBe(3);
    expect(first.rows.map((row) => row.name)).toEqual(["Unscoped audit", "Family requirement"]);
    expect(second.rows.map((row) => row.name)).toEqual(["Component requirement"]);
  });

  it("distinguishes every recorded satisfaction state", () => {
    const rows = new Map(buildRequirementCatalog(requirementsGraphWithEverySatisfactionState())
      .requirements.map((row) => [row.id, row]));

    expect(rows.get("requirement:family")?.satisfaction).toBe("satisfied");
    expect(rows.get("requirement:progress")?.satisfaction).toBe("in_progress");
    expect(rows.get("requirement:component")?.satisfaction).toBe("not_recorded");
    expect(rows.get("requirement:planned")?.satisfaction).toBe("unsatisfied");
  });

  it("does not treat a proposed applies-to Assertion as established applicability", () => {
    const graph = structuredClone(REQUIREMENTS_GRAPH);
    const direct = graph.edges.find((edge) => edge.relationship_type === "applies_to");
    if (!direct) throw new Error("fixture lost applies_to");
    direct.authored = false;
    direct.assertions = [{
      id: "assertion:scope",
      assertion_status: "proposed",
      confidence: "medium",
      description: null,
      evidence: [],
      reviews: [],
    }];
    direct.properties = { assertion_ids: ["assertion:scope"], assertion_status: "proposed" };
    const row = buildRequirementCatalog(graph).requirements
      .find((candidate) => candidate.id === "requirement:component");
    expect(row?.applicableProducts).toEqual([]);
  });

  it("requires a justified human acceptance before treating an Assertion as established", () => {
    const graph = structuredClone(REQUIREMENTS_GRAPH);
    const asserted = graph.edges.find((edge) => edge.properties.assertion_ids);
    const assertion = graph.nodes.find((node) => node.id === "assertion:proposal");
    const review = graph.nodes.find((node) => node.id === "review:proposal");
    if (!asserted || !assertion || !review) throw new Error("fixture lost review evidence");
    asserted.properties = {
      ...asserted.properties,
      assertion_status: "accepted",
      review_status: "accepted",
    };
    asserted.assertions = asserted.assertions?.map((item) => ({
      ...item,
      assertion_status: "accepted",
      reviews: item.reviews.map((itemReview) => ({ ...itemReview, review_status: "accepted" })),
    }));
    assertion.properties = { ...assertion.properties, assertion_status: "accepted" };
    review.properties = { ...review.properties, review_status: "accepted" };
    const accepted = buildRequirementCatalog(graph).requirements
      .find((row) => row.id === "requirement:component")?.relationships
      .find((relationship) => relationship.assertionIds.includes("assertion:proposal"));
    expect(accepted?.established).toBe(true);

    review.properties = { ...review.properties, justification: "" };
    const unjustified = buildRequirementCatalog(graph).requirements
      .find((row) => row.id === "requirement:component")?.relationships
      .find((relationship) => relationship.assertionIds.includes("assertion:proposal"));
    expect(unjustified?.established).toBe(false);
  });
});
