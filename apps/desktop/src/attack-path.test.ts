import { describe, expect, it } from "vitest";
import {
  attackPathOptions,
  attackPathOptionsForResponses,
  attackPathPresentation,
  attackPathReviewLabel,
  attackPathReviewState,
} from "./attack-path";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { createGraphState, mergeGraph, selectNode } from "./graph-model";
import type { AttackPathResponse, GraphResponse } from "./graph-types";
import { LatestRequestGuard } from "./request-guard";

// Exact response shapes returned by PR #132 for the canonical MVP-01 vector.
const XXE_RESPONSE: AttackPathResponse = {
  file: "/models/mvp-01-software-doc-service.yaml",
  goal: "threat-instance:xxe-file-read",
  paths: [{
    steps: [
      "attack-step:upload-crafted-doc",
      "attack-step:parser-resolves-entity",
      "attack-step:coerce-file-uri",
      "attack-step:read-internal-file",
    ],
    goal_step: "attack-step:read-internal-file",
    authored_path: "attack-path:xxe-file-read",
    review: { reviewed: true, assertion_status: "accepted", review_status: "accepted" },
  }],
};

const IMDS_RESPONSE: AttackPathResponse = {
  file: "/models/mvp-01-software-doc-service.yaml",
  goal: "threat-instance:imds-pivot",
  paths: [
    {
      steps: ["attack-step:point-entity-at-metadata", "attack-step:fetch-instance-credentials"],
      goal_step: "attack-step:fetch-instance-credentials",
      authored_path: "attack-path:imds-pivot",
      review: { reviewed: false, assertion_status: "proposed", review_status: "changes_requested" },
    },
    {
      steps: ["attack-step:dns-rebind-to-metadata", "attack-step:fetch-instance-credentials"],
      goal_step: "attack-step:fetch-instance-credentials",
      authored_path: "attack-path:imds-pivot",
      review: { reviewed: false, assertion_status: "proposed", review_status: "changes_requested" },
    },
  ],
};

// mvp-02: assertion:ai-pivot-realizes is proposed and its Review rejected it.
const INFOTAINMENT_RESPONSE: AttackPathResponse = {
  file: "/models/mvp-02-automotive-ecu.yaml",
  goal: "threat-instance:infotainment-pivot",
  paths: [
    {
      steps: [
        "attack-step:compromise-companion-app",
        "attack-step:gain-infotainment-foothold",
        "attack-step:pivot-to-can",
      ],
      goal_step: "attack-step:pivot-to-can",
      authored_path: "attack-path:infotainment-pivot",
      review: { reviewed: false, assertion_status: "proposed", review_status: "rejected" },
    },
    {
      steps: [
        "attack-step:malicious-ota",
        "attack-step:gain-infotainment-foothold",
        "attack-step:pivot-to-can",
      ],
      goal_step: "attack-step:pivot-to-can",
      authored_path: "attack-path:infotainment-pivot",
      review: { reviewed: false, assertion_status: "proposed", review_status: "rejected" },
    },
  ],
};

const graph: GraphResponse = {
  source: "engine",
  nodes: [
    "upload-crafted-doc",
    "parser-resolves-entity",
    "coerce-file-uri",
    "read-internal-file",
    "point-entity-at-metadata",
    "dns-rebind-to-metadata",
    "fetch-instance-credentials",
  ].map((id) => ({ id: `attack-step:${id}`, domainType: "AttackStep", label: id, properties: {} })),
  edges: [
    edge("upload-parser", "upload-crafted-doc", "parser-resolves-entity", "precedes"),
    edge("parser-read", "parser-resolves-entity", "read-internal-file", "precedes"),
    edge("uri-read", "coerce-file-uri", "read-internal-file", "precedes"),
    edge("metadata-fetch", "point-entity-at-metadata", "fetch-instance-credentials", "precedes"),
    edge("dns-fetch", "dns-rebind-to-metadata", "fetch-instance-credentials", "precedes"),
    edge("reverse", "read-internal-file", "parser-resolves-entity", "related_to"),
  ],
};

describe("attack-path presentation", () => {
  it("maps the PR #132 response without losing file, stable IDs, or review metadata", () => {
    const options = attackPathOptions(IMDS_RESPONSE);
    expect(options).toHaveLength(2);
    expect(options[0].id).not.toBe(options[1].id);
    expect(options[0].sourceFile).toBe(IMDS_RESPONSE.file);
    expect(options[0].goalId).toBe(IMDS_RESPONSE.goal);
    expect(options[0].result).toEqual(IMDS_RESPONSE.paths[0]);
    expect(options[0].label).toBe("IMDS Pivot — Alternative 1 (Changes Requested)");
    expect(options[1].label).toBe("IMDS Pivot — Alternative 2 (Changes Requested)");
    expect(attackPathOptions(XXE_RESPONSE)[0].label).toBe(
      "XXE File Read — Reviewed (Accepted)",
    );
  });

  it("keeps separate PR #132 responses selectable for each goal", () => {
    const options = attackPathOptionsForResponses([XXE_RESPONSE, IMDS_RESPONSE]);
    expect(options).toHaveLength(3);
    expect(options.map((option) => option.goalId)).toEqual([
      "threat-instance:xxe-file-read",
      "threat-instance:imds-pivot",
      "threat-instance:imds-pivot",
    ]);
    expect(options.every((option) => option.sourceFile === XXE_RESPONSE.file)).toBe(true);
    expect(options.map((option) => option.label)).toEqual([
      "XXE File Read — Reviewed (Accepted)",
      "IMDS Pivot — Alternative 1 (Changes Requested)",
      "IMDS Pivot — Alternative 2 (Changes Requested)",
    ]);
  });

  it("labels a human-rejected path Rejected rather than Proposed (mvp-02 infotainment pivot)", () => {
    const options = attackPathOptions(INFOTAINMENT_RESPONSE);
    expect(options.map((option) => option.label)).toEqual([
      "Infotainment Pivot — Alternative 1 (Rejected)",
      "Infotainment Pivot — Alternative 2 (Rejected)",
    ]);
    expect(options[0].result.review).toEqual(INFOTAINMENT_RESPONSE.paths[0].review);
    expect(attackPathReviewState(options[0].result.review).kind).toBe("rejected");
    expect(attackPathOptions({ ...INFOTAINMENT_RESPONSE, paths: [INFOTAINMENT_RESPONSE.paths[0]] })[0]
      .label).toBe("Infotainment Pivot — Rejected");
  });

  it("never labels a path Reviewed when its Review is negative, even if the engine flag is set", () => {
    const contradictory = (reviewStatus: string): AttackPathResponse => ({
      ...XXE_RESPONSE,
      paths: [{
        ...XXE_RESPONSE.paths[0],
        review: { reviewed: true, assertion_status: "accepted", review_status: reviewStatus },
      }],
    });
    const rejected = attackPathOptions(contradictory("rejected"))[0];
    const changes = attackPathOptions(contradictory("changes_requested"))[0];
    expect(rejected.label).toBe("XXE File Read — Rejected");
    expect(changes.label).toBe("XXE File Read — Changes Requested");
    expect(rejected.label).not.toContain("Reviewed");
    expect(attackPathReviewLabel(rejected.result.review)).toBe(
      "rejected, not accepted · assertion: accepted · review: rejected",
    );
    // The engine's own record is preserved unchanged.
    expect(rejected.result.review.reviewed).toBe(true);
  });

  it("highlights every directed precedes edge in the actual XXE AND path", () => {
    const presentation = attackPathPresentation(createGraphState(graph), XXE_RESPONSE.paths[0]);
    expect(presentation.stepNodeIds).toEqual(XXE_RESPONSE.paths[0].steps);
    expect(presentation.pathEdgeIds).toEqual(["upload-parser", "parser-read", "uri-read"]);
    expect(presentation.pathEdgeIds).not.toContain("reverse");
    expect(presentation.pathEdgeIds).not.toContain("metadata-fetch");
  });

  it("keeps the actual IMDS OR alternatives distinct", () => {
    const state = createGraphState(graph);
    expect(attackPathPresentation(state, IMDS_RESPONSE.paths[0]).pathEdgeIds).toEqual([
      "metadata-fetch",
    ]);
    expect(attackPathPresentation(state, IMDS_RESPONSE.paths[1]).pathEdgeIds).toEqual([
      "dns-fetch",
    ]);
    expect(attackPathPresentation(state, IMDS_RESPONSE.paths[0]).dimmedNodeIds).toContain(
      "attack-step:dns-rebind-to-metadata",
    );
  });

  it("describes reviewed, proposed, and unrecorded review states clearly", () => {
    expect(attackPathReviewLabel(XXE_RESPONSE.paths[0].review)).toBe(
      "reviewed and accepted · assertion: accepted · review: accepted",
    );
    expect(attackPathReviewLabel(IMDS_RESPONSE.paths[0].review)).toBe(
      "changes requested, not accepted · assertion: proposed · review: changes requested",
    );
    expect(attackPathReviewLabel({ reviewed: false, assertion_status: "proposed", review_status: null }))
      .toBe("proposed, not accepted · assertion: proposed");
    expect(attackPathReviewLabel({ reviewed: false, assertion_status: null, review_status: null }))
      .toBe("not reviewed, no status recorded");
    expect(attackPathOptions({
      ...XXE_RESPONSE,
      paths: [{ ...XXE_RESPONSE.paths[0], review: { reviewed: false, assertion_status: null, review_status: null } }],
    })[0].label).toBe("XXE File Read — Not Reviewed");
  });

  it("allows only the latest asynchronous path selection to publish results", () => {
    const guard = new LatestRequestGuard();
    const first = guard.begin();
    const second = guard.begin();
    expect(guard.isCurrent(first)).toBe(false);
    expect(first.signal.aborted).toBe(true);
    expect(guard.isCurrent(second)).toBe(true);
    guard.cancel();
    expect(guard.isCurrent(second)).toBe(false);
  });

  it("loads a required path edge even when every path node already exists", async () => {
    const provider = new DevelopmentFixtureProvider();
    const responses = await provider.getAttackPaths();
    const path = responses.find((response) => response.goal === IMDS_RESPONSE.goal)?.paths[0];
    if (!path) throw new Error("Missing IMDS fixture path");
    let state = createGraphState({
      source: "development-fixture",
      nodes: graph.nodes.filter((node) => path.steps.includes(node.id)),
      edges: [],
    });
    expect(attackPathPresentation(state, path).stepNodeIds).toEqual(path.steps);
    expect(attackPathPresentation(state, path).pathEdgeIds).toEqual([]);

    for (const stepId of new Set(path.steps)) {
      state = mergeGraph(state, await provider.getNeighborhood(stepId));
    }

    expect(attackPathPresentation(state, path).pathEdgeIds).toEqual([
      "metadata-precedes-fetch",
    ]);
    expect(new Set(state.nodes.map((node) => node.id)).size).toBe(state.nodes.length);
    expect(new Set(state.edges.map((item) => item.id)).size).toBe(state.edges.length);
  });

  it("clears transient presentation state without changing selection", () => {
    const selected = selectNode(createGraphState(graph), "attack-step:parser-resolves-entity");
    expect(attackPathPresentation(selected)).toEqual({
      stepNodeIds: [], pathEdgeIds: [], dimmedNodeIds: [], dimmedEdgeIds: [],
    });
    expect(selected.selectedNodeId).toBe("attack-step:parser-resolves-entity");
  });

  it("does not mutate the response, path, or graph state", () => {
    const responseBefore = structuredClone(IMDS_RESPONSE);
    const state = createGraphState(graph);
    const stateBefore = structuredClone(state);
    const options = attackPathOptions(IMDS_RESPONSE);
    attackPathPresentation(state, options[0].result);
    expect(IMDS_RESPONSE).toEqual(responseBefore);
    expect(state).toEqual(stateBefore);
  });

  it("presents the reviewed fixture AND path with all required directed edges", async () => {
    const provider = new DevelopmentFixtureProvider();
    const responses = await provider.getAttackPaths();
    const fixtureResponse = responses.find((response) => response.goal === XXE_RESPONSE.goal);
    if (!fixtureResponse) throw new Error("Missing XXE fixture path");
    const path = fixtureResponse.paths[0];
    let state = selectNode(createGraphState(await provider.getInitialGraph()), "component:papermill-api");
    for (const stepId of path.steps) {
      state = mergeGraph(state, await provider.getNeighborhood(stepId));
    }
    const presentation = attackPathPresentation(state, path);
    expect(fixtureResponse.file).toBe("spec/vectors/mvp-01-software-doc-service.yaml");
    expect(path.review).toEqual({
      reviewed: true,
      assertion_status: "accepted",
      review_status: "accepted",
    });
    expect(presentation.stepNodeIds).toEqual(path.steps);
    expect(presentation.pathEdgeIds).toEqual([
      "upload-precedes-parser",
      "parser-precedes-read",
      "uri-precedes-read",
    ]);
    expect(state.selectedNodeId).toBe("component:papermill-api");
  });

  it("presents each proposed fixture OR alternative without the other branch", async () => {
    const provider = new DevelopmentFixtureProvider();
    const responses = await provider.getAttackPaths();
    const fixtureResponse = responses.find((response) => response.goal === IMDS_RESPONSE.goal);
    if (!fixtureResponse) throw new Error("Missing IMDS fixture paths");
    const expectedEdges = ["metadata-precedes-fetch", "dns-rebind-precedes-fetch"];

    for (const [index, path] of fixtureResponse.paths.entries()) {
      let state = createGraphState(await provider.getInitialGraph());
      for (const stepId of path.steps) {
        state = mergeGraph(state, await provider.getNeighborhood(stepId));
      }
      const presentation = attackPathPresentation(state, path);
      expect(path.review).toEqual({
        reviewed: false,
        assertion_status: "proposed",
        review_status: "changes_requested",
      });
      expect(presentation.stepNodeIds).toEqual(path.steps);
      expect(presentation.pathEdgeIds).toEqual([expectedEdges[index]]);
      expect(presentation.pathEdgeIds).not.toContain(expectedEdges[1 - index]);
    }
  });

  it("exposes fixture source identity through provider metadata", () => {
    const metadata = new DevelopmentFixtureProvider().metadata;
    expect(metadata).toEqual({
      source: "development-fixture",
      label: "Development fixture data",
      notice: "Development fixture data — not live engine data",
    });
  });
});

function edge(id: string, source: string, target: string, relationshipType: string) {
  return {
    id,
    source: `attack-step:${source}`,
    target: `attack-step:${target}`,
    relationshipType,
    properties: {},
  };
}
