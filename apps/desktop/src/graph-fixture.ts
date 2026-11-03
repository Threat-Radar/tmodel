import type {
  AttackPathResponse,
  GraphDataProvider,
  GraphEdge,
  GraphNode,
  GraphResponse,
} from "./graph-types";

export const FIXTURE_NOTICE = "Development fixture data — not live engine data";
export const FIXTURE_SOURCE_LABEL = "Development fixture data";

// Development-only projection of spec/vectors/mvp-01-software-doc-service.yaml.
// It preserves the vector's stable IDs and relationship directions. The browser
// never reads the YAML; a future engine provider can replace this provider.
// Schema-backed properties retain their sponsor-approved snake_case slot names.
// Any presentation-only property is explicitly prefixed with `derived_`.
const NODES: readonly GraphNode[] = [
  {
    id: "product:papermill-doc-service",
    domainType: "Product",
    label: "Papermill Document Service",
    expandable: true,
    properties: {
      description: "OSS document-ingest & rendering microservice.",
      identifiers: [
        "pkg:github/papermill/doc-service",
        "cpe:2.3:a:papermill:doc_service:3.1.0:*:*:*:*:*:*:*",
      ],
    },
  },
  {
    id: "component:papermill-api",
    domainType: "Component",
    label: "papermill-api",
    expandable: true,
    properties: {
      description: "The deployed service artifact (§0 authoritative component, not a DFD node).",
      identifiers: ["pkg:oci/papermill/doc-service@sha256:3b9e1d2a"],
    },
  },
  {
    id: "component:render-worker",
    domainType: "Component",
    label: "document render worker",
    expandable: true,
    properties: {
      description: "Parses and renders uploaded documents.",
      identifiers: ["pkg:github/papermill/doc-service@3.1.0#render"],
    },
  },
  {
    id: "component:libxml-parse",
    domainType: "Component",
    label: "libxml-parse",
    expandable: true,
    properties: {
      description: "Vulnerable OSS XML-parsing dependency along which the finding propagates (§5).",
      identifiers: [
        "pkg:pypi/libxml-parse@1.8.2",
        "cpe:2.3:a:libxml_parse:libxml_parse:1.8.2:*:*:*:*:*:*:*",
      ],
    },
  },
  {
    id: "vulnerability:cve-2026-30111",
    domainType: "Vulnerability",
    label: "CVE-2026-30111 (illustrative)",
    expandable: true,
    properties: {
      description: "Finding affecting the product; propagation to components is a reviewed Assertion (§5).",
      catalog_ref: "CVE-2026-30111",
    },
  },
  {
    id: "weakness:cwe-611",
    domainType: "Weakness",
    label: "CWE-611: XML External Entity",
    expandable: true,
    properties: {
      description: "Generic weakness class (CWE, §1 layer 3).",
      catalog_ref: "CWE-611",
    },
  },
  {
    id: "attack-pattern:capec-221",
    domainType: "AttackPattern",
    label: "CAPEC-221: External Entities Blowup",
    properties: {
      description: "Generic attack pattern (CAPEC = what, §2a). The CWE↔CAPEC link is a reviewed Assertion.",
      catalog_ref: "CAPEC-221",
    },
  },
  {
    id: "threat-instance:xxe-file-read",
    domainType: "ThreatInstance",
    label: "XXE via uploaded document",
    expandable: true,
    properties: {
      method_facet: ["stride"],
      source_method: "stride-dfd (human-elicited, reviewed)",
      violates_property: "I confidentiality",
    },
  },
  {
    id: "attack-path:xxe-file-read",
    domainType: "AttackPath",
    label: "XXE file-read path",
    expandable: true,
    properties: {
      attack_feasibility: "medium",
      derived_review_state: "reviewed from accepted realizes_threat assertion",
    },
  },
  {
    id: "attack-step:upload-crafted-doc",
    domainType: "AttackStep",
    label: "Upload crafted document",
    expandable: true,
    properties: { kill_chain_phase: "delivery" },
  },
  {
    id: "attack-step:parser-resolves-entity",
    domainType: "AttackStep",
    label: "Parser resolves external entity",
    expandable: true,
    properties: {},
  },
  {
    id: "attack-step:coerce-file-uri",
    domainType: "AttackStep",
    label: "Point entity at file URI",
    expandable: true,
    properties: {},
  },
  {
    id: "attack-step:read-internal-file",
    domainType: "AttackStep",
    label: "Read and exfiltrate internal file",
    properties: { gate: "and_gate", kill_chain_phase: "exploitation" },
  },
  {
    id: "attack-step:point-entity-at-metadata",
    domainType: "AttackStep",
    label: "Point entity at metadata endpoint",
    expandable: true,
    properties: {},
  },
  {
    id: "attack-step:dns-rebind-to-metadata",
    domainType: "AttackStep",
    label: "DNS rebind to metadata endpoint",
    expandable: true,
    properties: {},
  },
  {
    id: "attack-step:fetch-instance-credentials",
    domainType: "AttackStep",
    label: "Fetch instance-role credentials",
    properties: { gate: "or_gate", kill_chain_phase: "exploitation" },
  },
];

const EDGES: readonly GraphEdge[] = [
  edge("product-composed-api", "product:papermill-doc-service", "component:papermill-api", "composed_of"),
  edge("api-composed-worker", "component:papermill-api", "component:render-worker", "composed_of"),
  edge("api-uses-libxml", "component:papermill-api", "component:libxml-parse", "uses_component"),
  edge("worker-uses-libxml", "component:render-worker", "component:libxml-parse", "uses_component"),
  edge("vulnerability-affects-product", "vulnerability:cve-2026-30111", "product:papermill-doc-service", "affects"),
  edge("assertion-vuln-propagates", "vulnerability:cve-2026-30111", "component:papermill-api", "propagates_to", { derived_from_assertion: "assertion:vuln-propagation", assertion_status: "accepted", review_status: "accepted" }),
  edge("assertion-cve-cwe-instance", "vulnerability:cve-2026-30111", "weakness:cwe-611", "instance_of", { derived_from_assertion: "assertion:cve-cwe-instance", assertion_status: "accepted", review_status: "accepted" }),
  edge("assertion-cwe-exploited-by-capec", "weakness:cwe-611", "attack-pattern:capec-221", "exploited_by", { derived_from_assertion: "assertion:cwe-capec-map", assertion_status: "accepted", review_status: "accepted" }),
  edge("path-realizes-threat", "attack-path:xxe-file-read", "threat-instance:xxe-file-read", "realizes_threat"),
  edge("path-step-upload", "attack-path:xxe-file-read", "attack-step:upload-crafted-doc", "steps"),
  edge("path-step-parser", "attack-path:xxe-file-read", "attack-step:parser-resolves-entity", "steps"),
  edge("path-step-uri", "attack-path:xxe-file-read", "attack-step:coerce-file-uri", "steps"),
  edge("path-step-read", "attack-path:xxe-file-read", "attack-step:read-internal-file", "steps"),
  edge("upload-precedes-parser", "attack-step:upload-crafted-doc", "attack-step:parser-resolves-entity", "precedes"),
  edge("parser-precedes-read", "attack-step:parser-resolves-entity", "attack-step:read-internal-file", "precedes"),
  edge("uri-precedes-read", "attack-step:coerce-file-uri", "attack-step:read-internal-file", "precedes"),
  edge("metadata-precedes-fetch", "attack-step:point-entity-at-metadata", "attack-step:fetch-instance-credentials", "precedes"),
  edge("dns-rebind-precedes-fetch", "attack-step:dns-rebind-to-metadata", "attack-step:fetch-instance-credentials", "precedes"),
];

const VECTOR_SOURCE = "spec/vectors/mvp-01-software-doc-service.yaml";

const ATTACK_PATH_RESPONSES: readonly AttackPathResponse[] = [
  {
    file: VECTOR_SOURCE,
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
  },
  {
    file: VECTOR_SOURCE,
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
  },
];

const INITIAL_NODE_IDS = new Set([
  "product:papermill-doc-service",
  "component:papermill-api",
  "vulnerability:cve-2026-30111",
  "threat-instance:xxe-file-read",
  "attack-path:xxe-file-read",
]);

export class DevelopmentFixtureProvider implements GraphDataProvider {
  readonly metadata = {
    source: "development-fixture" as const,
    label: FIXTURE_SOURCE_LABEL,
    notice: FIXTURE_NOTICE,
  };

  async getInitialGraph(): Promise<GraphResponse> {
    return responseFor(INITIAL_NODE_IDS, "component:papermill-api");
  }

  async getNeighborhood(nodeId: string): Promise<GraphResponse> {
    if (!NODES.some((node) => node.id === nodeId)) return responseFor(new Set(), nodeId);
    const ids = new Set([nodeId]);
    for (const edge of EDGES) {
      if (edge.source === nodeId) ids.add(edge.target);
      if (edge.target === nodeId) ids.add(edge.source);
    }
    return responseFor(ids, nodeId);
  }

  async getAttackPaths(): Promise<readonly AttackPathResponse[]> {
    return ATTACK_PATH_RESPONSES.map((response) => ({
      file: response.file,
      goal: response.goal,
      paths: response.paths.map((path) => ({
        ...path,
        steps: [...path.steps],
        review: { ...path.review },
      })),
    }));
  }
}

function responseFor(ids: ReadonlySet<string>, focusId: string): GraphResponse {
  const adjacency = new Map<string, Set<string>>();
  for (const edge of EDGES) {
    const sourceNeighbors = adjacency.get(edge.source) ?? new Set<string>();
    sourceNeighbors.add(edge.target);
    adjacency.set(edge.source, sourceNeighbors);
    const targetNeighbors = adjacency.get(edge.target) ?? new Set<string>();
    targetNeighbors.add(edge.source);
    adjacency.set(edge.target, targetNeighbors);
  }
  const nodes = NODES
    .filter((node) => ids.has(node.id))
    .map((node) => ({
      ...node,
      expandable: [...(adjacency.get(node.id) ?? [])].some((neighbor) => !ids.has(neighbor)),
    }));
  const edges = EDGES.filter((edge) => ids.has(edge.source) && ids.has(edge.target));
  return {
    source: "development-fixture",
    notice: FIXTURE_NOTICE,
    focusId,
    nodes,
    edges,
  };
}

function edge(
  id: string,
  source: string,
  target: string,
  relationshipType: string,
  properties: GraphEdge["properties"] = {},
): GraphEdge {
  return { id, source, target, relationshipType, properties };
}
