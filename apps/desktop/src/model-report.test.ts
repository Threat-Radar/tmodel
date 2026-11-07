import { describe, expect, it } from "vitest";
import mvp01 from "./fixtures/report-input-mvp-01.json";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import mvp03 from "./fixtures/report-input-mvp-03.json";
import type { AttackPathResponse } from "./graph-types";
import {
  buildModelReport,
  humanize,
  readableDescription,
  readableText,
  threatSource,
  type ModelReport,
} from "./model-report";
import type { EngineGraphEdge, EngineGraphNode, ModelReportInput, ModelSummary } from "./model-types";

const MVP01 = mvp01 as unknown as ModelReportInput;
const MVP02 = mvp02 as unknown as ModelReportInput;
const MVP03 = mvp03 as unknown as ModelReportInput;

describe("model report from engine responses (mvp-02)", () => {
  const report = buildModelReport(MVP02);

  it("opens with the model's own title and counts threats by review status", () => {
    expect(report.model.title).toBe("Telematics Control Unit (TCU)");
    expect(report.threatSummary.total).toBe(2);
    expect(report.threatSummary.aiProposed).toBe(1);
    expect(report.threatSummary.byStatus).toEqual([
      { kind: "accepted", label: "accepted", count: 1 },
      { kind: "rejected", label: "rejected", count: 1 },
    ]);
    expect(report.reviewers).toEqual(["@av-reviewer"]);
  });

  it("marks the AI-proposed infotainment pivot as rejected, with the reviewer and reason", () => {
    const pivot = threat(report, "threat-instance:infotainment-pivot");
    expect(pivot.name).toBe("Lateral movement from infotainment domain into the safety CAN domain");
    expect(pivot.source).toEqual({ kind: "ai", label: "AI-proposed" });
    expect(pivot.status.kind).toBe("rejected");
    expect(pivot.status.label).toBe("Rejected");
    expect(pivot.status.reviewed).toBe(false);
    expect(pivot.status.reviewers).toEqual(["@av-reviewer"]);
    expect(pivot.status.assertionStatus).toBe("proposed");
    expect(pivot.status.reviewStatus).toBe("rejected");

    const path = report.attackPaths.find((row) => row.id === "attack-path:infotainment-pivot");
    expect(path?.status.kind).toBe("rejected");
    expect(path?.status.justification).toContain("domain gateway blocks the only claimed pivot");
  });

  it("shows the accepted remote path as reviewed, using the model's names", () => {
    const remote = threat(report, "threat-instance:remote-diag-injection");
    expect(remote.status).toMatchObject({ kind: "accepted", label: "Accepted", reviewed: true, reviewers: ["@av-reviewer"] });
    expect(remote.source.label).toBe("Human-elicited");
    expect(remote.damages.map((ref) => ref.label)).toEqual(["Unauthorized CAN command → unsafe vehicle behavior"]);
    expect(remote.mitigations.map((ref) => ref.label)).toEqual([
      "Require strong authentication on the diagnostic service",
      "Enforce a filtering gateway between infotainment and safety domains",
    ]);
    const path = report.attackPaths.find((row) => row.id === "attack-path:remote-diag-injection");
    expect(path?.name).toBe("Remote diagnostic-injection path");
    expect(path?.feasibility).toBe("High");
  });

  it("orders steps by precedes and records the AND gate", () => {
    const story = report.attackPaths.find((row) => row.id === "attack-path:remote-diag-injection")?.story;
    expect(story?.steps.map((step) => [step.number, step.name, step.gate, step.after, step.stage])).toEqual([
      [1, "Reach the modem's diagnostic port over the carrier network", null, [], 0],
      [2, "Bypass the missing/weak diagnostic authentication", null, [], 0],
      [3, "Inject a crafted CAN frame to a safety actuator", "and", [1, 2], 1],
    ]);
    expect(story?.steps[0].phase).toBe("Delivery");
    // The engine's computed alternative for an AND is one path through all three steps.
    expect(story?.alternatives).toEqual([[1, 2, 3]]);
  });

  it("records the OR gate and the engine's two alternatives through it", () => {
    const story = report.attackPaths.find((row) => row.id === "attack-path:infotainment-pivot")?.story;
    expect(story?.steps.map((step) => [step.number, step.gate, step.after])).toEqual([
      [1, null, []],
      [2, null, []],
      [3, "or", [1, 2]],
      [4, null, [3]],
    ]);
    expect(story?.alternatives).toEqual([[1, 3, 4], [2, 3, 4]]);
  });

  it("lists every TARA table in its own terms, without inventing missing data", () => {
    expect(report.assets.map((asset) => ({
      name: asset.name,
      properties: asset.securityProperties,
      processedBy: asset.processedBy.map((ref) => ref.label),
    }))).toEqual([
      {
        name: "Safety CAN commands (braking)",
        properties: ["Integrity", "Authenticity"],
        processedBy: ["Communications core"],
      },
      {
        name: "Remote diagnostic service",
        properties: ["Authorization"],
        processedBy: ["diagnostic-service library (firmware module)"],
      },
    ]);
    expect(report.components.map((row) => row.kind)).toEqual([
      "Product",
      "Product instance",
      "Component",
      "Component",
      "Component",
      "Component",
      "Component",
      "Component",
    ]);
    const soc = report.components.find((row) => row.id === "component:tcu-soc");
    expect(soc?.partOf.map((ref) => ref.label)).toEqual(["Telematics Control Unit (TCU)"]);
    expect(soc?.contains.map((ref) => ref.label)).toEqual(["Application core", "Communications core"]);

    const [damage] = report.damageScenarios;
    expect(damage.impactSource).toBe("risk assessment");
    expect(damage.impact).toEqual([
      { category: "Safety", rating: "Severe" },
      { category: "Financial", rating: "Major" },
      { category: "Operational", rating: "Severe" },
      { category: "Privacy", rating: "Negligible" },
    ]);

    const assessed = report.risks.filter((risk) => risk.assessed);
    expect(assessed).toHaveLength(1);
    expect(assessed[0]).toMatchObject({
      feasibility: "High",
      mitigationStatus: "In progress",
      risk: "safety 5 / financial 4 / operational 5 / privacy 1 (one attack path, feasibility High; 1 to 5 per ISO/SAE 21434 15.8, read from the Annex H example matrix, Table H.8)",
    });
    expect(assessed[0].stakeholder?.label).toBe("Fleet operator");
    // The rejected pivot has no RiskScore: it is listed as not assessed, not given a score.
    const notAssessed = report.risks.filter((risk) => !risk.assessed);
    expect(notAssessed.map((risk) => risk.threat?.id)).toEqual(["threat-instance:infotainment-pivot"]);
    expect(notAssessed[0].risk).toBeNull();

    const family = report.mitigations.find((row) => row.id === "mitigation:family-authenticated-diagnostics");
    expect(family?.threats).toEqual([]);
    expect(family?.status).toBeNull();
    expect(family?.statedAs.map((ref) => ref.label)).toEqual(["Connected-ECU family: authenticate remote diagnostics"]);
  });

  it("collects the CVE, CWE and CAPEC records with their names and relationships", () => {
    expect(report.vulnerabilities).toEqual([expect.objectContaining({
      name: "Unauthenticated remote diagnostic command on TCU modem (illustrative)",
      catalogRef: "CVE-2026-41200",
      weaknesses: [{ id: "weakness:cwe-306", label: "Missing Authentication for Critical Function (CWE-306)" }],
    })]);
    expect(report.weaknesses).toEqual([expect.objectContaining({
      name: "Missing Authentication for Critical Function",
      catalogRef: "CWE-306",
      vulnerabilities: [expect.objectContaining({ id: "vulnerability:cve-2026-41200" })],
      attackPatterns: [{ id: "attack-pattern:capec-115", label: "Authentication Bypass (CAPEC-115)" }],
    })]);
    expect(report.attackPatterns).toEqual([expect.objectContaining({
      name: "Authentication Bypass",
      catalogRef: "CAPEC-115",
      weaknesses: [expect.objectContaining({ id: "weakness:cwe-306" })],
    })]);
  });

  it("keeps the AI-proposed requirement link apart from the authored ones", () => {
    const requirement = report.requirements.find((row) => row.id === "requirement:family-authenticated-diagnostics");
    expect(requirement?.addresses.map((ref) => ref.label)).toEqual([
      "Missing Authentication for Critical Function (CWE-306)",
      "Authentication Bypass (CAPEC-115)",
    ]);
    expect(requirement?.proposedLinks).toHaveLength(1);
    expect(requirement?.proposedLinks[0].target.id).toBe("threat-instance:infotainment-pivot");
    expect(requirement?.proposedLinks[0].status.label).toBe("AI-proposed, not reviewed");
    expect(requirement?.clause).toBeNull();
    const rq = report.requirements.find((row) => row.id === "requirement:iso21434-rq-09-09");
    expect(rq?.clause).toBe("RQ-09-09 (§9.5.2)");
    expect(rq?.origin).toBe("Paraphrase");
    const gateway = report.requirements.find((row) => row.id === "requirement:gateway-filter-safety-can");
    expect(gateway?.name).toBe("Domain gateway: forward only allow-listed frames to the safety CAN");
    expect(gateway?.addresses.map((ref) => ref.label)).toEqual([
      "Remote unauthenticated diagnostic command injection onto CAN",
    ]);
    expect(gateway?.derivedFrom.map((ref) => ref.label)).toEqual([
      "ISO/SAE 21434 RQ-09-09: define the item's cybersecurity requirements",
    ]);
  });

  it("keeps ids, CPE strings and schema names in details only", () => {
    const soc = report.components.find((row) => row.id === "component:tcu-soc");
    expect(soc?.description.summary).toBe("Multi-core applications SoC hosting the telematics stack.");
    expect(soc?.description.full).toContain("(§3 structural node)");
    expect(soc?.details).toEqual(expect.arrayContaining([
      { label: "Model id", value: "component:tcu-soc" },
      { label: "Identifiers", value: "cpe:2.3:h:chipco:soc_t500:-:*:*:*:*:*:*:*" },
    ]));
  });
});

describe("model report review states (mvp-01)", () => {
  it("shows changes requested on the AI-proposed IMDS pivot, with its reviewer", () => {
    const report = buildModelReport(MVP01);
    const imds = threat(report, "threat-instance:imds-pivot");
    expect(imds.source.kind).toBe("ai");
    expect(imds.status).toMatchObject({ kind: "changes_requested", label: "Changes requested", reviewed: false });
    expect(imds.status.reviewers).toEqual(["@sec-reviewer"]);
    expect(report.threatSummary.byStatus.map((entry) => entry.kind)).toEqual(["accepted", "changes_requested"]);
  });
});

describe("model report engine prerequisites (mvp-03)", () => {
  const report = buildModelReport(MVP03);
  const cross = report.attackPaths.find((row) => row.id === "attack-path:cross-subsystem-chain");
  if (!cross) throw new Error("mvp-03 fixture changed");

  it("keeps the engine-computed JWT prerequisites outside the authored step list", () => {
    expect(cross.story.steps.map((step) => [step.number, step.id, step.gate, step.after, step.stage])).toEqual([
      [1, "attack-step:forge-jwt-none-alg", null, [], 0],
      [2, "attack-step:forge-jwt-weak-key", null, [], 0],
      [3, "attack-step:call-fleet-api", "or", [1, 2], 1],
      [4, "attack-step:chain-to-in-vehicle", null, [3], 2],
    ]);
    expect(cross.story.alternatives).toEqual([[1, 3, 4], [2, 3, 4]]);
    expect(cross.story.alternativesMissing).toBe(false);
  });

  it("marks an engine alternative incomplete when one of its computed steps is absent from the graph", () => {
    const input = structuredClone(MVP03);
    const response = input.attackPaths.find((answer) => answer.goal === "threat-instance:cross-subsystem-chain");
    if (!response) throw new Error("mvp-03 fixture changed");
    response.paths[0].steps[0] = "attack-step:engine-only-prerequisite";
    const changed = buildModelReport(input).attackPaths.find((row) => row.id === cross.id);
    expect(changed?.story.alternativesMissing).toBe(true);
  });
});

describe("model report edge cases", () => {
  it("marks a threat with no recorded review as not reviewed, whatever its source claims", () => {
    const input = tinyModel({
      threatSource: "stride (human-elicited, reviewed)",
      assertion: undefined,
    });
    const [row] = buildModelReport(input).threats;
    expect(row.source.label).toBe("Human-elicited");
    expect(row.status).toMatchObject({ kind: "not_reviewed", label: "Not reviewed", reviewed: false, reviewers: [] });
  });

  it("labels a proposed AI path with no review as AI-proposed, not reviewed", () => {
    const input = tinyModel({ threatSource: "ai:llm (hypothesis)", assertion: { assertion_status: "proposed" } });
    const report = buildModelReport(input);
    expect(report.threats[0].status.label).toBe("AI-proposed, not reviewed");
    expect(report.attackPaths[0].status.kind).toBe("proposed");
    expect(report.threatSummary.byStatus).toEqual([{ kind: "proposed", label: "proposed, not reviewed", count: 1 }]);
  });

  it("never shows a review verdict contradicting an accepted assertion as accepted", () => {
    const input = tinyModel({ assertion: { assertion_status: "accepted", review_status: "rejected" } });
    expect(buildModelReport(input).threats[0].status.kind).toBe("rejected");
  });

  it("projects ADR-0011 assets and the damage that names them", () => {
    const input = tinyModel({});
    const report = buildModelReport(input);
    expect(report.assets).toEqual([expect.objectContaining({
      name: "Brake commands",
      securityProperties: ["Integrity", "Authenticity"],
    })]);
    expect(report.damageScenarios[0].assets.map((ref) => ref.label)).toEqual(["Brake commands"]);
    expect(report.damageScenarios[0].impact).toEqual([]);
    expect(report.damageScenarios[0].impactSource).toBeNull();
  });

  it("keeps partially populated catalog rows instead of inventing fields", () => {
    const input = tinyModel({});
    input.graph = {
      ...input.graph,
      nodes: [
        ...input.graph.nodes,
        { id: "vulnerability:v", domain_type: "Vulnerability", label: "Observed flaw", properties: {} },
        { id: "weakness:w", domain_type: "Weakness", label: "Weakness with no catalog entry", properties: { catalog_ref: "" } },
        { id: "attack-pattern:a", domain_type: "AttackPattern", label: "Unnamed catalog mapping", properties: {} },
      ],
    };
    const report = buildModelReport(input);
    expect(report.vulnerabilities[0]).toMatchObject({ name: "Observed flaw", catalogRef: null, weaknesses: [] });
    expect(report.weaknesses[0]).toMatchObject({ catalogRef: null, vulnerabilities: [], attackPatterns: [] });
    expect(report.attackPatterns[0]).toMatchObject({ catalogRef: null, weaknesses: [] });
  });

  it("is deterministic", () => {
    expect(buildModelReport(MVP02)).toEqual(buildModelReport(structuredClone(MVP02)));
  });
});

describe("readable text", () => {
  it("drops spec cross-references and stops before the first modelling note", () => {
    expect(readableText("Multi-core SoC (§3 structural node). Hosts the stack.")).toEqual({
      summary: "Multi-core SoC. Hosts the stack.",
      full: "Multi-core SoC (§3 structural node). Hosts the stack.",
      trimmed: true,
    });
    expect(readableText("AI-PROPOSED hypothesis. Its edge is a `proposed` Assertion. More.").summary)
      .toBe("AI-PROPOSED hypothesis.");
    expect(readableText("See mitigation:authenticate-diag-service for this.").summary).toBeNull();
    expect(readableText("Ships cpe:2.3:a:x:y:1 and pkg:pypi/z@1.").summary).toBeNull();
    expect(readableText("Stored in stated_as for now.").summary).toBeNull();
    expect(readableText("Composite vector per ADR-0006.").summary).toBeNull();
    expect(readableText("A plain sentence, e.g. a simple one.")).toMatchObject({ summary: "A plain sentence, e.g. a simple one.", trimmed: false });
    expect(readableText(null)).toEqual({ summary: null, full: null, trimmed: false });
  });

  it("humanizes stored values and reads threat sources", () => {
    expect(humanize("very_low")).toBe("Very low");
    expect(humanize("lateral_movement")).toBe("Lateral movement");
    expect(threatSource("ai:maestro-agent (hypothesis, unreviewed)").kind).toBe("ai");
    expect(threatSource("published attack (AI-drafted, unreviewed)").label).toBe("AI-drafted");
    expect(threatSource("stride-dfd (human-elicited, reviewed)").label).toBe("Human-elicited");
    expect(threatSource("stride").kind).toBe("unrecorded");
    expect(threatSource(null).kind).toBe("unrecorded");
  });
});

// mvp-03's product description, as the model records it.
const MVP03_DESCRIPTION = "A SYSTEM product (ADR-0002) that hierarchically composes an in-vehicle platform "
  + "subsystem and a cloud-backend subsystem. Recursive `composed_of` is the structural layer (§3).";

describe("report fixes from the #208 review", () => {
  it("drops parenthetical spec references such as (ADR-0002) from reader text", () => {
    const text = readableText(MVP03_DESCRIPTION);
    expect(text.summary).toBe(
      "A SYSTEM product that hierarchically composes an in-vehicle platform subsystem and a cloud-backend subsystem.",
    );
    expect(text.trimmed).toBe(true);
    expect(text.full).toContain("`composed_of`");
  });

  it("reads each product of a multi-product model on its own, so a note in one cannot hide another", () => {
    // mvp-18's two products, as the engine lists them (one line per product).
    const mvp18 = "Crypto Server Appliance: Product A — a TLS-terminating server appliance that embeds the SoC. AFFECTED.\n"
      + "Edge Sensor: Product X — an edge sensor that embeds the SAME SoC/IP core, but is VEX NOT_AFFECTED: the vulnerable RNG path is not on its execute path.";
    const both = readableDescription(mvp18);
    expect(both.summary?.split("\n").map((line) => line.split(":")[0])).toEqual(["Crypto Server Appliance", "Edge Sensor"]);
    const noted = readableDescription("Alpha: A note (ADR-0002) about `composed_of`.\nBeta: The second product.");
    // Alpha's only sentence is a modelling note, so it stays under Details; Beta still shows.
    expect(noted.summary).toBe("Beta: The second product.");
    expect(noted.trimmed).toBe(true);
    expect(readableDescription("One product only.")).toEqual(readableText("One product only."));
    expect(readableDescription(null)).toEqual({ summary: null, full: null, trimmed: false });
  });

  it("gives the report header the product description as reader text, keeping the full text", () => {
    const input = tinyModel({});
    input.model = { ...input.model, description: MVP03_DESCRIPTION };
    const { description } = buildModelReport(input).model;
    expect(description.summary).not.toContain("composed_of");
    expect(description.summary).not.toContain("ADR-0002");
    expect(description.full).toBe(MVP03_DESCRIPTION);
  });

  it("names an unnamed object by its type, never by its id", () => {
    const input = tinyModel({});
    input.graph = {
      ...input.graph,
      nodes: input.graph.nodes.map((node) => (node.id === "step:a" ? { ...node, label: "step:a" } : node)),
    };
    const report = buildModelReport(input);
    expect(report.attackPaths[0].story.steps[0].name).toBe("Unnamed attack step");
  });

  it("reads #209's richer mvp-02 shape (threat targets, damaged assets) with no code change", () => {
    const input = tinyModel({});
    input.graph = {
      ...input.graph,
      nodes: [
        ...input.graph.nodes.map((node) => (node.id === "threat:t"
          ? { ...node, properties: { ...node.properties, targets_element: ["asset:brake", "component:diag"] } }
          : node)),
        { id: "component:diag", domain_type: "Component", label: "Diagnostic service", properties: {} },
      ],
    };
    const report = buildModelReport(input);
    expect(report.attackPaths[0].story.targets.map((ref) => ref.label)).toEqual(["Brake commands", "Diagnostic service"]);
    expect(report.damageScenarios[0].assets.map((ref) => ref.label)).toEqual(["Brake commands"]);
  });

  it("lists a second, asserted threat link apart from the path's own threat", () => {
    const input = tinyModel({});
    input.graph = {
      ...input.graph,
      nodes: [
        ...input.graph.nodes,
        { id: "threat:t2", domain_type: "ThreatInstance", label: "Second threat", properties: {} },
      ],
      edges: [
        ...input.graph.edges,
        {
          id: "relationship:path:p|realizes_threat|threat:t2",
          source: "path:p",
          target: "threat:t2",
          relationship_type: "realizes_threat",
          properties: { assertion_ids: ["assertion:extra"], assertion_status: "proposed" },
        },
      ],
    };
    const row = buildModelReport(input).attackPaths[0];
    expect(row.threat?.id).toBe("threat:t");
    expect(row.otherThreats).toEqual([{
      target: { id: "threat:t2", label: "Second threat" },
      status: expect.objectContaining({ kind: "proposed", reviewed: false }),
    }]);
  });

  it("marks only the paths whose threat failed as missing their computed alternatives", () => {
    const report = buildModelReport({
      ...MVP02,
      attackPathFailures: [{ goal: "threat-instance:infotainment-pivot", message: "timed out" }],
    });
    expect(report.attackPathProblems).toEqual([{
      threat: { id: "threat-instance:infotainment-pivot", label: expect.any(String) },
      message: "timed out",
    }]);
    const missing = report.attackPaths.filter((row) => row.story.alternativesMissing).map((row) => row.threat?.id);
    expect(missing).toEqual(["threat-instance:infotainment-pivot"]);
  });
});

function threat(report: ModelReport, id: string) {
  const row = report.threats.find((candidate) => candidate.id === id);
  if (!row) throw new Error(`no threat ${id}`);
  return row;
}

function tinyModel(options: {
  threatSource?: string;
  assertion?: { assertion_status?: string; review_status?: string };
}): ModelReportInput {
  const node = (id: string, domain_type: string, label: string, properties: EngineGraphNode["properties"] = {}): EngineGraphNode => ({
    id,
    domain_type,
    label,
    properties,
  });
  const edge = (source: string, relationship_type: string, target: string, properties: EngineGraphEdge["properties"] = {}): EngineGraphEdge => ({
    id: `relationship:${source}|${relationship_type}|${target}`,
    source,
    target,
    relationship_type,
    properties,
  });
  const realizes = options.assertion
    ? { assertion_ids: ["assertion:a"], ...options.assertion }
    : {};
  const model: ModelSummary = {
    id: "tiny",
    file: "tiny.yaml",
    title: "Tiny",
    description: null,
    kind: "core",
    kind_label: "Core example",
    counts: {},
    reviewed_threats: 0,
  };
  const paths: AttackPathResponse[] = [];
  return {
    model,
    graph: {
      file: "tiny.yaml",
      nodes: [
        node("asset:brake", "Asset", "Brake commands", { security_properties: ["integrity", "authenticity"] }),
        node("damage:crash", "DamageScenario", "Unwanted braking", { damages_asset: ["asset:brake"] }),
        node("threat:t", "ThreatInstance", "Forged brake command", options.threatSource ? { source_method: options.threatSource } : {}),
        node("step:a", "AttackStep", "Reach the bus"),
        node("path:p", "AttackPath", "Bus path"),
      ],
      edges: [
        edge("threat:t", "realizes_damage", "damage:crash"),
        edge("path:p", "steps", "step:a"),
        edge("path:p", "realizes_threat", "threat:t", realizes),
      ],
    },
    attackPaths: paths,
  };
}
