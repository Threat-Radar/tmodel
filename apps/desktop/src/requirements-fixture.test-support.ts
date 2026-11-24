import type { EngineGraphEdge, EngineGraphNode, EngineGraphResponse } from "./model-types";

const nodes: EngineGraphNode[] = [
  { id: "product:tcu", domain_type: "Product", label: "TCU", properties: { classifications: ["automotive"] } },
  { id: "component:diag", domain_type: "Component", label: "Diagnostic service", properties: {} },
  { id: "threat:one", domain_type: "ThreatInstance", label: "Recorded threat", properties: {} },
  { id: "threat:two", domain_type: "ThreatInstance", label: "Unaddressed threat", properties: {} },
  { id: "mitigation:auth", domain_type: "Mitigation", label: "Authenticate diagnostics", properties: { mitigation_status: "complete" } },
  { id: "requirement:family", domain_type: "Requirement", label: "Family requirement", properties: {
    text: "Connected ECUs shall authenticate diagnostic requests.",
    description: "A family-scoped technical requirement.",
    requirement_kind: "technical",
    normativity: "mandatory",
    text_origin: "authored",
    source_ref: "library:test#R1",
    source_locator: "R1",
    applies_to_family: ["automotive"],
  } },
  { id: "requirement:component", domain_type: "Requirement", label: "Component requirement", properties: {
    text: "The diagnostic service shall reject unauthenticated commands.",
    requirement_kind: "technical",
    normativity: "mandatory",
    text_origin: "paraphrase",
    source_ref: "library:test#R2",
    source_locator: "Clause 2",
  } },
  { id: "requirement:unscoped", domain_type: "Requirement", label: "Unscoped audit", properties: {
    text: "Independently audit the process.",
    requirement_kind: "audit",
    normativity: "recommended",
    source_ref: "library:test#R3",
  } },
  { id: "assertion:proposal", domain_type: "Assertion", label: "Proposed threat link", properties: {
    assertion_status: "proposed",
    confidence: "medium",
    description: "Analytical relationship awaiting a decision.",
    evidence: ["The threat follows the diagnostic command path."],
  } },
  { id: "review:proposal", domain_type: "Review", label: "Pending human review", properties: {
    review_status: "pending",
    justification: "Human decision has not been recorded.",
  } },
  { id: "party:human", domain_type: "Party", label: "Human reviewer", properties: { party_kind: "person" } },
];

const edges: EngineGraphEdge[] = [
  edge("product:tcu", "composed_of", "component:diag"),
  edge("requirement:family", "satisfied_by", "mitigation:auth"),
  edge("requirement:family", "addresses", "threat:one"),
  edge("requirement:component", "applies_to", "component:diag"),
  edge("requirement:component", "addresses", "threat:two", {
    assertion_ids: ["assertion:proposal"],
    assertion_status: "proposed",
    confidence: "medium",
    assertion_descriptions: ["Analytical relationship awaiting a decision."],
    assertion_evidence: ["The threat follows the diagnostic command path."],
    review_ids: ["review:proposal"],
    review_status: "pending",
    review_statuses: ["pending"],
    review_justifications: ["Human decision has not been recorded."],
  }, false, [{
    id: "assertion:proposal",
    assertion_status: "proposed",
    confidence: "medium",
    description: "Analytical relationship awaiting a decision.",
    evidence: ["The threat follows the diagnostic command path."],
    reviews: [{
      id: "review:proposal",
      review_status: "pending",
      reviewer: "party:human",
      justification: "Human decision has not been recorded.",
    }],
  }]),
  edge("review:proposal", "reviews", "assertion:proposal"),
  edge("review:proposal", "reviewer", "party:human"),
];

export const REQUIREMENTS_GRAPH: EngineGraphResponse = {
  file: "/models/mvp-02-automotive-ecu.yaml",
  nodes,
  edges,
};

export function requirementsGraphWithEverySatisfactionState(): EngineGraphResponse {
  const graph = structuredClone(REQUIREMENTS_GRAPH);
  const additionalNodes: EngineGraphNode[] = [
    {
      id: "mitigation:progress",
      domain_type: "Mitigation",
      label: "Deploy stronger authentication",
      properties: { mitigation_status: "in_progress" },
    },
    {
      id: "mitigation:planned",
      domain_type: "Mitigation",
      label: "Plan independent audit",
      properties: { mitigation_status: "planned" },
    },
    {
      id: "requirement:progress",
      domain_type: "Requirement",
      label: "In-progress requirement",
      properties: {
        text: "The diagnostic service shall deploy stronger authentication.",
        requirement_kind: "technical",
        normativity: "mandatory",
        source_ref: "library:test#R4",
        source_locator: "Clause 4",
      },
    },
    {
      id: "requirement:planned",
      domain_type: "Requirement",
      label: "Recorded incomplete requirement",
      properties: {
        text: "The diagnostic service shall complete an independent audit.",
        requirement_kind: "audit",
        normativity: "mandatory",
        source_ref: "library:test#R5",
        source_locator: "Clause 5",
      },
    },
  ];
  const additionalEdges: EngineGraphEdge[] = [
    edge("requirement:progress", "applies_to", "component:diag"),
    edge("requirement:progress", "satisfied_by", "mitigation:progress"),
    edge("requirement:planned", "applies_to", "component:diag"),
    edge("requirement:planned", "satisfied_by", "mitigation:planned"),
  ];
  return {
    ...graph,
    nodes: [...graph.nodes, ...additionalNodes],
    edges: [...graph.edges, ...additionalEdges],
  };
}

function edge(
  source: string,
  relationship_type: string,
  target: string,
  properties: EngineGraphEdge["properties"] = {},
  authored = true,
  assertions: EngineGraphEdge["assertions"] = [],
): EngineGraphEdge {
  return {
    id: `relationship:${source}|${relationship_type}|${target}`,
    source,
    target,
    relationship_type,
    authored,
    assertions,
    properties,
  };
}
