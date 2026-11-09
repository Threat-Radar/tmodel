import { describe, expect, it } from "vitest";
import mvp01 from "./fixtures/report-input-mvp-01.json";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import mvp03 from "./fixtures/report-input-mvp-03.json";
import { BOOKKEEPING_TYPES, buildModelReport, type PathStory, type ReportRef, type StoryStep } from "./model-report";
import type { ModelReportInput } from "./model-types";
import {
  crossesABox,
  layoutPathDiagram,
  pathDiagramSvg,
  roundedPath,
  wrapLabel,
  type PathDiagram,
} from "./path-diagram";

const report = buildModelReport(mvp02 as unknown as ModelReportInput);
const mvp03Report = buildModelReport(mvp03 as unknown as ModelReportInput);
const remote = report.attackPaths.find((row) => row.id === "attack-path:remote-diag-injection");
const pivot = report.attackPaths.find((row) => row.id === "attack-path:infotainment-pivot");
if (!remote || !pivot) throw new Error("fixture changed");
const remoteStory = remote.story;

describe("attack-path diagram layout", () => {
  it("draws steps left to right in order, an AND gate before the joining step, then threat and damage", () => {
    const diagram = layoutPathDiagram(remote.story);
    const node = (id: string) => {
      const found = diagram.nodes.find((candidate) => candidate.id === id);
      if (!found) throw new Error(`no node ${id}`);
      return found;
    };
    const reach = node("step|attack-step:reach-modem-over-cellular");
    const bypass = node("step|attack-step:bypass-diag-auth");
    const gate = node("gate|attack-step:inject-can-frame");
    const inject = node("step|attack-step:inject-can-frame");
    const threat = node("threat|threat-instance:remote-diag-injection");
    const damage = node("damage|damage-scenario:unauthorized-can-actuation");
    expect(reach.x).toBe(bypass.x); // the two AND branches share a column
    expect(reach.y).toBeLessThan(bypass.y);
    expect(gate.lines).toEqual(["AND"]);
    expect(reach.x).toBeLessThan(gate.x);
    expect(gate.x).toBeLessThan(inject.x);
    expect(inject.x).toBeLessThan(threat.x);
    expect(threat.x).toBeLessThan(damage.x);
    expect(diagram.edges.map((edge) => [edge.source, edge.target, edge.label])).toEqual(expect.arrayContaining([
      [reach.id, gate.id, ""],
      [bypass.id, gate.id, ""],
      [gate.id, inject.id, "then"],
      [inject.id, threat.id, "realizes"],
      [threat.id, damage.id, "leads to"],
    ]));
    const mitigations = diagram.nodes.filter((candidate) => candidate.kind === "mitigation");
    expect(mitigations).toHaveLength(2);
    for (const mitigation of mitigations) expect(mitigation.y).toBeGreaterThan(threat.y);
  });

  it("uses an OR gate where either branch is enough", () => {
    const diagram = layoutPathDiagram(pivot.story);
    const gates = diagram.nodes.filter((node) => node.kind === "gate");
    expect(gates.map((gate) => gate.lines[0])).toEqual(["OR"]);
    expect(gates[0].title).toBe("OR: step 3 needs any one of steps 1, 2");
    expect(diagram.status).toBe("rejected");
  });

  it("draws both engine-computed mvp-03 JWT prerequisites and their OR join", () => {
    const cross = mvp03Report.attackPaths.find((row) => row.id === "attack-path:cross-subsystem-chain");
    if (!cross) throw new Error("mvp-03 fixture changed");
    const diagram = layoutPathDiagram(cross.story);
    expect(diagram.nodes.filter((node) => node.kind === "step").map((node) => node.objectId)).toEqual([
      "attack-step:forge-jwt-none-alg",
      "attack-step:forge-jwt-weak-key",
      "attack-step:call-fleet-api",
      "attack-step:chain-to-in-vehicle",
    ]);
    expect(diagram.nodes.filter((node) => node.kind === "gate").map((node) => node.lines[0])).toEqual(["OR"]);
    expect(cross.story.alternatives).toEqual([[1, 3, 4], [2, 3, 4]]);
    expect(diagram.status).toBe("changes_requested");
  });

  it("labels every node, draws only path objects, and keeps everything inside its bounds", () => {
    for (const row of report.attackPaths) {
      const diagram = layoutPathDiagram(row.story);
      const objectTypes = new Set(diagram.nodes.map((node) => node.kind));
      expect([...objectTypes].every((kind) => ["step", "gate", "threat", "damage", "mitigation", "target"].includes(kind))).toBe(true);
      for (const node of diagram.nodes) {
        expect(node.lines.join(" ").trim().length).toBeGreaterThan(0);
        expect(node.x - node.width / 2).toBeGreaterThanOrEqual(0);
        expect(node.y - node.height / 2).toBeGreaterThanOrEqual(0);
        expect(node.x + node.width / 2).toBeLessThanOrEqual(diagram.width);
        expect(node.y + node.height / 2).toBeLessThanOrEqual(diagram.height);
      }
      for (const type of BOOKKEEPING_TYPES) expect(JSON.stringify(diagram)).not.toContain(`"kind":"${type}"`);
      // At the app's 1280-pixel width the diagram needs little or no scaling.
      expect(diagram.width).toBeLessThanOrEqual(1320);
    }
  });

  it("keeps a rejected path assertion separate from its AI-proposed, unreviewed threat", () => {
    const threat = layoutPathDiagram(pivot.story).nodes.find((node) => node.kind === "threat");
    expect(threat?.captionLines.join(" ")).toBe("Threat · AI-proposed, not reviewed");
    expect(threat?.lines.join(" ")).not.toContain("Reviewed by");
    expect(layoutPathDiagram(pivot.story).status).toBe("rejected");
  });
});

// Everything that makes a connector hard to follow, as a list of problems.
function routingProblems(diagram: PathDiagram): string[] {
  const problems: string[] = [];
  const byId = new Map(diagram.nodes.map((node) => [node.id, node]));
  const labels: { id: string; left: number; right: number; top: number; bottom: number }[] = [];
  for (const edge of diagram.edges) {
    const source = byId.get(edge.source);
    const target = byId.get(edge.target);
    if (!source || !target) { problems.push(`${edge.id}: missing end`); continue; }
    const points = edge.points;
    if (points.length < 2) { problems.push(`${edge.id}: not routed`); continue; }
    for (let index = 1; index < points.length; index += 1) {
      const [a, b] = [points[index - 1], points[index]];
      if (Math.abs(a.x - b.x) > 0.01 && Math.abs(a.y - b.y) > 0.01) problems.push(`${edge.id}: diagonal segment ${index}`);
    }
    const [first, last] = [points[0], points[points.length - 1]];
    if (edge.kind === "mitigates" || edge.kind === "targets") {
      if (first.x !== source.x || first.y !== source.y - source.height / 2) problems.push(`${edge.id}: does not leave the source's top`);
      if (last.x !== target.x || last.y !== target.y + target.height / 2) problems.push(`${edge.id}: does not enter the target's bottom`);
    } else {
      if (first.x !== source.x + source.width / 2 || first.y !== source.y) problems.push(`${edge.id}: does not leave the source's right side`);
      if (last.x !== target.x - target.width / 2 || last.y !== target.y) problems.push(`${edge.id}: does not enter the target's left side`);
    }
    if (crossesABox(points, diagram.nodes, source, target)) problems.push(`${edge.id}: crosses a box`);
    if (edge.labelAt) {
      const box = {
        id: edge.id,
        left: edge.labelAt.x - edge.labelWidth / 2,
        right: edge.labelAt.x + edge.labelWidth / 2,
        top: edge.labelAt.y - 8,
        bottom: edge.labelAt.y + 8,
      };
      for (const node of diagram.nodes) {
        const overlaps = box.right > node.x - node.width / 2 && box.left < node.x + node.width / 2
          && box.bottom > node.y - node.height / 2 && box.top < node.y + node.height / 2;
        if (overlaps) problems.push(`${edge.id}: label covers ${node.id}`);
      }
      for (const other of labels) {
        if (box.right > other.left && box.left < other.right && box.bottom > other.top && box.top < other.bottom) {
          problems.push(`${edge.id}: label covers the label of ${other.id}`);
        }
      }
      labels.push(box);
    }
  }
  // Every kind of labelled connector shows its word at least once.
  for (const kind of new Set(diagram.edges.filter((edge) => edge.label).map((edge) => edge.kind))) {
    if (!diagram.edges.some((edge) => edge.kind === kind && edge.labelAt)) problems.push(`no "${kind}" label shown`);
  }
  return problems;
}

function storyWith(steps: Partial<StoryStep>[], extra: Partial<PathStory> = {}): PathStory {
  return {
    ...structuredClone(remoteStory),
    steps: steps.map((step, index) => ({
      id: `attack-step:s${index + 1}`,
      number: index + 1,
      name: `Step ${index + 1} of a synthetic path`,
      description: { summary: null, full: null, trimmed: false },
      phase: null,
      gate: null,
      after: [],
      stage: 0,
      ...step,
    })),
    ...extra,
  };
}

const ref = (id: string, label: string): ReportRef => ({ id, label });

describe("attack-path connectors", () => {
  const fixturePaths = [
    ...buildModelReport(mvp01 as unknown as ModelReportInput).attackPaths,
    ...report.attackPaths,
    ...mvp03Report.attackPaths,
  ];

  it.each(fixturePaths.map((row) => [row.id, row] as const))(
    "%s: right-angled lines from side to side, through no box, with readable labels",
    (_id, row) => {
      expect(routingProblems(layoutPathDiagram(row.story))).toEqual([]);
    },
  );

  it("draws a step with no predecessor next to its successor's column, not far to its left", () => {
    const xxe = fixturePaths.find((row) => row.id === "attack-path:xxe-file-read");
    if (!xxe) throw new Error("fixture changed");
    const diagram = layoutPathDiagram(xxe.story);
    const step = (number: number) => diagram.nodes.find((node) => node.id === `step|${xxe.story.steps[number - 1].id}`);
    // Step 3 starts a branch of its own and feeds step 4's AND gate, as step 2 does.
    expect(xxe.story.steps[2].after).toEqual([]);
    expect(step(3)?.x).toBe(step(2)?.x);
    expect(step(1)?.x).toBeLessThan(step(2)?.x ?? 0);
  });

  it("joins every line into a gate on one vertical line just before it", () => {
    const diagram = layoutPathDiagram(pivot.story);
    const joins = diagram.edges.filter((edge) => edge.kind === "joins");
    expect(joins.length).toBe(2);
    const busX = joins.map((edge) => edge.points[edge.points.length - 2].x);
    expect(new Set(busX).size).toBe(1);
    expect(joins.every((edge) => edge.labelAt === null)).toBe(true);
  });

  it("goes around the boxes in between when a step joins one several columns later", () => {
    // Step 1 feeds step 2 and also, through an AND gate, step 4: that line would cross steps 2 and 3.
    const story = storyWith([
      { stage: 0 },
      { stage: 1, after: [1] },
      { stage: 2, after: [2] },
      { stage: 3, after: [1, 3], gate: "and" },
    ]);
    const diagram = layoutPathDiagram(story);
    expect(routingProblems(diagram)).toEqual([]);
    const skip = diagram.edges.find((edge) => edge.source === "step|attack-step:s1" && edge.kind === "joins");
    expect(skip?.points.length).toBe(6);
    const band = diagram.nodes.filter((node) => node.kind === "step");
    const laneY = skip?.points[2].y ?? 0;
    expect(band.every((node) => laneY < node.y - node.height / 2 || laneY > node.y + node.height / 2)).toBe(true);
  });

  it("shares one line, and one label, between several final steps, damages, mitigations and targets", () => {
    const story = storyWith([{ stage: 0 }, { stage: 0 }], {
      damages: [ref("damage:a", "First damage"), ref("damage:b", "Second damage")],
      mitigations: [ref("mitigation:a", "First mitigation"), ref("mitigation:b", "Second mitigation"), ref("mitigation:c", "Third mitigation")],
      targets: [ref("asset:a", "First asset"), ref("asset:b", "Second asset")],
    });
    const diagram = layoutPathDiagram(story);
    expect(routingProblems(diagram)).toEqual([]);
    for (const kind of ["realizes", "leads_to", "mitigates", "targets"] as const) {
      const edges = diagram.edges.filter((edge) => edge.kind === kind);
      expect(edges.length).toBeGreaterThan(1);
      expect(edges.filter((edge) => edge.labelAt).length).toBe(1);
    }
    // The mitigations' lines meet on one horizontal line before rising into the threat.
    const mitigations = diagram.edges.filter((edge) => edge.kind === "mitigates");
    const busY = new Set(mitigations.filter((edge) => edge.points.length === 4).map((edge) => edge.points[1].y));
    expect(busY.size).toBe(1);
  });
});

describe("attack-path SVG", () => {
  it("draws the routed lines with rounded corners, and every label on top with a background", () => {
    const diagram = layoutPathDiagram(pivot.story);
    const svg = pathDiagramSvg(diagram, "Pivot");
    const paths = [...svg.matchAll(/<g class="pd-edge [^"]*"><path d="([^"]+)"/g)].map((match) => match[1]);
    expect(paths).toHaveLength(diagram.edges.length);
    for (const d of paths) expect(d).toMatch(/^M[\d.,-]+(?: [LQ][\d.,\s-]+)+$/);
    expect(svg.lastIndexOf('class="pd-node')).toBeLessThan(svg.indexOf('class="pd-edge-label-group'));
    expect(svg.match(/class="pd-edge-label-bg"/g)?.length).toBe(diagram.edges.filter((edge) => edge.labelAt).length);
    expect(roundedPath([{ x: 0, y: 0 }, { x: 20, y: 0 }, { x: 20, y: 30 }], 6)).toBe("M0,0 L14,0 Q20,0 20,6 L20,30");
  });

  it("is inline SVG with escaped labels and no script or external reference", () => {
    const story = structuredClone(remote.story);
    story.steps[0].name = "<script>alert(1)</script>";
    const svg = pathDiagramSvg(layoutPathDiagram(story), "Diagram & <path>");
    expect(svg.startsWith("<svg class=\"path-diagram pd-status-accepted pd-threat-status-not_reviewed\"")).toBe(true);
    expect(svg).toContain('aria-label="Diagram &amp; &lt;path&gt;"');
    expect(svg).not.toMatch(/<script/i);
    expect(svg).toContain("&lt;script&gt;alert(1)");
    expect(svg).not.toMatch(/(?:href|src)=/);
    expect(svg).toContain('marker-end="url(#arrow-attack-path-remote-diag-injection)"');
  });
});

describe("label wrapping", () => {
  it("wraps on words and ellipsizes past the line budget", () => {
    expect(wrapLabel("Reach the modem's diagnostic port over the carrier network", 21)).toEqual([
      "Reach the modem's",
      "diagnostic port over",
      "the carrier network",
    ]);
    expect(wrapLabel("a b c d e f g h", 3, 2)).toEqual(["a b", "c…"]);
    expect(wrapLabel("Supercalifragilistic", 8)).toEqual(["Superca…"]);
  });
});
