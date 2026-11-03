import { describe, expect, it } from "vitest";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import {
  createGraphState,
  mergeGraph,
  relationshipsForNode,
  selectNode,
  toCytoscapeEdgeElement,
  toCytoscapeElements,
} from "./graph-model";
import type { GraphEdge, GraphResponse } from "./graph-types";

const response: GraphResponse = {
  source: "development-fixture",
  nodes: [
    { id: "component:a", domainType: "Component", label: "A", properties: { tags: ["one"] } },
    { id: "component:b", domainType: "Component", label: "B", properties: {} },
  ],
  edges: [
    {
      id: "edge:a-b",
      source: "component:a",
      target: "component:b",
      relationshipType: "uses_component",
      properties: {},
    },
  ],
};

describe("graph domain mapping", () => {
  it("preserves stable IDs, domain types, and edge direction", () => {
    const state = createGraphState(response);
    const elements = toCytoscapeElements(state);
    expect(elements[0]).toMatchObject({
      group: "nodes",
      data: { id: "component:a", domainType: "Component" },
    });
    expect(elements[2]).toMatchObject({
      group: "edges",
      data: { source: "component:a", target: "component:b", relationshipType: "uses_component" },
    });
  });

  it("maps incoming and outgoing relationships without losing direction", () => {
    const state = createGraphState(response);
    expect(relationshipsForNode(state, "component:a")[0]).toMatchObject({
      direction: "outgoing",
      connectedNodeId: "component:b",
    });
    expect(relationshipsForNode(state, "component:b")[0]).toMatchObject({
      direction: "incoming",
      connectedNodeId: "component:a",
    });
  });

  it("does not mutate the source response or nested property arrays", () => {
    const before = structuredClone(response);
    const state = createGraphState(response);
    (state.nodes[0].properties.tags as string[]).push("two");
    expect(response).toEqual(before);
  });

  it("keeps selection for known nodes and ignores missing nodes", () => {
    const state = createGraphState(response);
    const selected = selectNode(state, "component:a");
    expect(selected.selectedNodeId).toBe("component:a");
    expect(selectNode(selected, "missing")).toBe(selected);
  });

  it("prevents duplicate nodes and edges while merging neighborhoods", () => {
    const state = createGraphState(response);
    const merged = mergeGraph(state, response);
    expect(merged.nodes).toHaveLength(2);
    expect(merged.edges).toHaveLength(1);
  });

  it("omits dangling edges from Cytoscape while retaining them for inspection", () => {
    const dangling: GraphResponse = {
      source: "engine",
      nodes: [response.nodes[0]],
      edges: [{ ...response.edges[0], target: "missing:node" }],
    };
    const state = createGraphState(dangling);
    expect(toCytoscapeElements(state)).toHaveLength(1);
    expect(relationshipsForNode(state, "component:a")[0]).toMatchObject({
      connectedNodeId: "missing:node",
      connectedNode: undefined,
    });
  });
});

describe("development fixture provider", () => {
  it("starts focused and expands neighborhoods with stable IDs", async () => {
    const provider = new DevelopmentFixtureProvider();
    const initial = await provider.getInitialGraph();
    const neighborhood = await provider.getNeighborhood("component:papermill-api");
    const merged = mergeGraph(createGraphState(initial), neighborhood);

    expect(initial.source).toBe("development-fixture");
    expect(initial.nodes.some((node) => node.id === "component:papermill-api")).toBe(true);
    expect(initial.nodes.find((node) => node.id === "component:papermill-api")?.expandable)
      .toBe(true);
    expect(neighborhood.nodes.find((node) => node.id === "component:papermill-api")?.expandable)
      .toBe(false);
    expect(merged.nodes.some((node) => node.id === "component:libxml-parse")).toBe(true);
    expect(new Set(merged.nodes.map((node) => node.id)).size).toBe(merged.nodes.length);
    expect(new Set(merged.edges.map((edge) => edge.id)).size).toBe(merged.edges.length);
  });

  it("returns an empty neighborhood for an unknown stable ID", async () => {
    const response = await new DevelopmentFixtureProvider().getNeighborhood("missing:node");
    expect(response.nodes).toEqual([]);
    expect(response.edges).toEqual([]);
  });

  it("projects the accepted CVE-to-CWE assertion with its schema direction", async () => {
    const neighborhood = await new DevelopmentFixtureProvider().getNeighborhood(
      "vulnerability:cve-2026-30111",
    );
    expect(neighborhood.edges).toContainEqual({
      id: "assertion-cve-cwe-instance",
      source: "vulnerability:cve-2026-30111",
      target: "weakness:cwe-611",
      relationshipType: "instance_of",
      properties: {
        derived_from_assertion: "assertion:cve-cwe-instance",
        assertion_status: "accepted",
        review_status: "accepted",
      },
    });
  });

  it("uses schema property names and explicitly marks derived fixture values", async () => {
    const provider = new DevelopmentFixtureProvider();
    const neighborhood = await provider.getNeighborhood("vulnerability:cve-2026-30111");
    const vulnerability = neighborhood.nodes.find(
      (node) => node.id === "vulnerability:cve-2026-30111",
    );
    expect(vulnerability?.properties).toMatchObject({ catalog_ref: "CVE-2026-30111" });
    expect(vulnerability?.properties).not.toHaveProperty("catalogRef");

    const path = (await provider.getInitialGraph()).nodes.find(
      (node) => node.id === "attack-path:xxe-file-read",
    );
    expect(path?.properties).toMatchObject({
      attack_feasibility: "medium",
      derived_review_state: expect.any(String),
    });
  });
});

describe("relationship review metadata", () => {
  function assertedEdge(properties: GraphEdge["properties"]): GraphEdge {
    return {
      id: "relationship:attack-path:imds-pivot|realizes_threat|threat-instance:imds-pivot",
      source: "attack-path:imds-pivot",
      target: "threat-instance:imds-pivot",
      relationshipType: "realizes_threat",
      properties,
    };
  }

  it.each([
    ["accepted", "accepted", "accepted", "realizes_threat"],
    ["proposed", null, "proposed", "realizes_threat · proposed"],
    ["proposed", "changes_requested", "changes_requested", "realizes_threat · changes requested"],
    ["proposed", "rejected", "rejected", "realizes_threat · rejected"],
    ["accepted", "rejected", "rejected", "realizes_threat · rejected"],
    ["triaged", null, "unknown", "realizes_threat · unknown status"],
  ] as const)(
    "carries assertion %s / review %s into Cytoscape edge data as %s",
    (assertionStatus, reviewStatus, reviewState, label) => {
      const properties = {
        assertion_ids: ["assertion:a"],
        assertion_status: assertionStatus,
        ...(reviewStatus ? { review_ids: ["review:a"], review_status: reviewStatus } : {}),
      };
      const element = toCytoscapeEdgeElement(assertedEdge(properties));
      expect(element.data).toMatchObject({
        id: "relationship:attack-path:imds-pivot|realizes_threat|threat-instance:imds-pivot",
        source: "attack-path:imds-pivot",
        target: "threat-instance:imds-pivot",
        relationshipType: "realizes_threat",
        reviewState,
        assertionStatus,
        reviewStatus: reviewStatus ?? null,
        label,
      });
    },
  );

  it("keeps structural relationships free of review styling data", () => {
    const element = toCytoscapeEdgeElement(response.edges[0]);
    expect(element.data).toEqual({
      id: "edge:a-b",
      source: "component:a",
      target: "component:b",
      relationshipType: "uses_component",
      label: "uses_component",
    });
  });

  it("exposes each relationship's own properties to the inspector", () => {
    const properties = {
      assertion_ids: ["assertion:ai-imds-pivot-realizes"],
      assertion_status: "proposed",
      review_ids: ["review:ai-triage"],
      review_status: "changes_requested",
    };
    const state = createGraphState({
      source: "engine",
      nodes: [
        { id: "attack-path:imds-pivot", domainType: "AttackPath", label: "Path", properties: {} },
        { id: "threat-instance:imds-pivot", domainType: "ThreatInstance", label: "Threat", properties: {} },
      ],
      edges: [assertedEdge(properties)],
    });

    expect(relationshipsForNode(state, "attack-path:imds-pivot")[0].properties).toEqual(properties);
    expect(relationshipsForNode(state, "threat-instance:imds-pivot")[0].properties).toEqual(properties);
  });
});
