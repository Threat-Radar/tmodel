// The focused attack-path diagram (#208): one layout, drawn two ways.
//
// `layoutPathDiagram` places a path's steps left to right in `precedes` order,
// with an AND/OR gate node in front of every step that joins two or more
// branches, then the threat the path realises and the damage it leads to.
// Mitigations sit under the threat, and elements the attack targets above it.
// It also routes every connector: right-angled lines that leave a box from its
// side (or top/bottom), join at a shared line just before the box they enter,
// and never cross another box; each label sits on a straight part of its line.
// The app draws this layout with Cytoscape; the static Pages renderer draws the
// same layout, routes included, as inline SVG (`pathDiagramSvg`), so both show
// the same picture.
//
// Node runs this file directly (type stripping): `.ts` value imports only.

import type { PathStory, ReportStatusKind } from "./model-report";
import { escapeHtml } from "./safe-html.ts";

export type DiagramNodeKind = "step" | "gate" | "threat" | "damage" | "mitigation" | "target";
export type DiagramEdgeKind = "then" | "joins" | "realizes" | "leads_to" | "mitigates" | "targets";

export interface DiagramNode {
  id: string;
  /** The model object this node stands for; a gate stands for its gated step. */
  objectId: string;
  kind: DiagramNodeKind;
  /** Small heading above the text, e.g. "Step 3" or "Threat"; `captionLines` is it wrapped. */
  caption: string;
  captionLines: string[];
  /** The wrapped text lines, in reading order. */
  lines: string[];
  /** One-line text for an accessible name or a tooltip. */
  title: string;
  /** Centre of the node. */
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Point {
  x: number;
  y: number;
}

export interface DiagramEdge {
  id: string;
  source: string;
  target: string;
  kind: DiagramEdgeKind;
  label: string;
  /**
   * The connector as a right-angled polyline in layout coordinates: the first
   * point is on the source box's edge, the last on the target box's edge.
   */
  points: Point[];
  /**
   * Centre of the label, or null when the edge has no label or shares a line
   * (and so its label) with another edge of the same kind.
   */
  labelAt: Point | null;
  /** Width the label needs, for its background. */
  labelWidth: number;
}

export interface PathDiagram {
  pathId: string;
  status: ReportStatusKind;
  nodes: DiagramNode[];
  edges: DiagramEdge[];
  width: number;
  height: number;
}

const MARGIN = 20;
const COLUMN_GAP = 58;
// Before a gate: the lines joining into it carry no label.
const JOIN_GAP = 40;
// Between a gate and the step it gates: room for "then".
const GATE_GAP = 50;
// Before the threat and the damage: room for "realizes" and "leads to".
const END_GAP = 80;
const ROW_GAP = 22;
const BAND_GAP = 48;
// Connectors turn this far before the box they enter, so lines into one box join there.
const BUS_OFFSET = 14;
// A line that would cross a box runs this far outside the main band instead.
const LANE_OFFSET = 16;
// Corner radius of the connectors (SVG and Cytoscape).
export const CONNECTOR_RADIUS = 6;
const LABEL_HEIGHT = 16;
const STEP = { width: 178, chars: 21 };
const END = { width: 192, chars: 22 };
const SIDE = { width: 186, chars: 21 };
const GATE = { width: 50, height: 30 };
const LINE_HEIGHT = 16;
const CAPTION_HEIGHT = 18;
const PADDING_Y = 12;
const MAX_LINES = 4;

export const EDGE_LABELS: Readonly<Record<DiagramEdgeKind, string>> = {
  then: "then",
  joins: "",
  realizes: "realizes",
  leads_to: "leads to",
  mitigates: "mitigates",
  targets: "targets",
};

const GATE_TEXT: Readonly<Record<string, { label: string; title: string }>> = {
  and: { label: "AND", title: "needs all of" },
  or: { label: "OR", title: "needs any one of" },
  unspecified: { label: "?", title: "gate not recorded for" },
};

/** Lays out one path's story. Pure and deterministic. */
export function layoutPathDiagram(story: PathStory): PathDiagram {
  const nodes: DiagramNode[] = [];
  const edges: DiagramEdge[] = [];
  const stepNodeId = (stepId: string) => `step|${stepId}`;
  const maxStage = Math.max(0, ...story.steps.map((step) => step.stage));
  // Drawing columns: each step's stage, except that a step with no predecessor
  // is drawn in the column just before its first successor (or with the last
  // steps, if it has none), so its line does not run past other columns. The
  // order of the steps, their numbers and the AND/OR gates are unchanged.
  const column = new Map(story.steps.map((step) => {
    if (step.after.length > 0) return [step.id, step.stage] as const;
    const successors = story.steps.filter((candidate) => candidate.after.includes(step.number));
    const drawn = successors.length === 0
      ? maxStage
      : Math.max(step.stage, Math.min(...successors.map((successor) => successor.stage)) - 1);
    return [step.id, drawn] as const;
  }));
  const stages = groupBy(story.steps, (step) => column.get(step.id) ?? step.stage);

  // Columns, left to right: an optional gate slot before each stage, then the
  // stage. Lines into a gate carry no label, so the gap before it is narrower;
  // the gaps before the threat and the damage are wider, for their longer labels.
  const stepX = new Map<number, number>();
  const gateX = new Map<number, number>();
  let x = MARGIN;
  for (let stage = 0; stage <= maxStage; stage += 1) {
    const gated = (stages.get(stage) ?? []).some((step) => step.gate !== null);
    if (stage > 0) x += gated ? JOIN_GAP : COLUMN_GAP;
    if (gated) {
      gateX.set(stage, x + GATE.width / 2);
      x += GATE.width + GATE_GAP;
    }
    stepX.set(stage, x + STEP.width / 2);
    x += STEP.width;
  }
  if (story.threat) x += END_GAP;
  const threatX = x + END.width / 2;
  if (story.threat) x += END.width;
  if (story.threat && story.damages.length > 0) x += END_GAP;
  const damageX = x + END.width / 2;
  if (story.threat && story.damages.length > 0) x += END.width;
  const contentRight = x;

  // Build node boxes first (heights depend on wrapped text), then place rows.
  const stepBoxes = story.steps.map((step) => box(
    stepNodeId(step.id),
    step.id,
    "step",
    step.phase ? `Step ${step.number} · ${step.phase}` : `Step ${step.number}`,
    step.name,
    STEP,
  ));
  const threatBox = story.threat
    ? box(
      `threat|${story.threat.id}`,
      story.threat.id,
      "threat",
      `Threat · ${story.status.label}`,
      story.threat.label,
      END,
      reviewerLine(story),
    )
    : undefined;
  const damageBoxes = story.threat
    ? story.damages.map((damage) => box(`damage|${damage.id}`, damage.id, "damage", "Damage scenario", damage.label, END))
    : [];
  const mitigationBoxes = story.threat
    ? story.mitigations.map((mitigation) => box(
      `mitigation|${mitigation.id}`,
      mitigation.id,
      "mitigation",
      "Mitigation",
      mitigation.label,
      SIDE,
    ))
    : [];
  const targetBoxes = story.threat
    ? story.targets.map((target) => box(`target|${target.id}`, target.id, "target", "Targeted", target.label, SIDE))
    : [];

  const targetBand = rowHeight(targetBoxes);
  const mainColumns: DiagramNode[][] = [
    ...[...stages.keys()].sort((a, b) => a - b).map((stage) => (
      (stages.get(stage) ?? []).map((step) => stepBoxes[story.steps.indexOf(step)])
    )),
    threatBox ? [threatBox] : [],
    damageBoxes,
  ];
  const mainBand = Math.max(0, ...mainColumns.map(columnHeight));
  const top = MARGIN + (targetBand > 0 ? targetBand + BAND_GAP : 0);
  const middle = top + mainBand / 2;

  for (const [stage, steps] of stages) {
    stack(steps.map((step) => stepBoxes[story.steps.indexOf(step)]), stepX.get(stage) ?? 0, middle);
  }
  if (threatBox) stack([threatBox], threatX, middle);
  stack(damageBoxes, damageX, middle);
  const anchorX = threatBox ? threatX : (stepX.get(maxStage) ?? MARGIN);
  spread(targetBoxes, anchorX, MARGIN + targetBand / 2);
  const bottomY = top + mainBand + BAND_GAP;
  spread(mitigationBoxes, anchorX, bottomY + rowHeight(mitigationBoxes) / 2);

  nodes.push(...stepBoxes);
  for (const step of story.steps) {
    const target = stepBoxes[story.steps.indexOf(step)];
    const predecessors = step.after
      .map((number) => story.steps.find((candidate) => candidate.number === number))
      .filter((candidate) => candidate !== undefined);
    if (step.gate) {
      const gate = GATE_TEXT[step.gate];
      const gateNode: DiagramNode = {
        id: `gate|${step.id}`,
        objectId: step.id,
        kind: "gate",
        caption: "",
        captionLines: [],
        lines: [gate.label],
        title: `${gate.label}: step ${step.number} ${gate.title} steps ${step.after.join(", ")}`,
        x: gateX.get(column.get(step.id) ?? step.stage) ?? target.x - STEP.width / 2 - GATE_GAP - GATE.width / 2,
        y: target.y,
        width: GATE.width,
        height: GATE.height,
      };
      nodes.push(gateNode);
      for (const before of predecessors) {
        edges.push(edge(stepNodeId(before.id), gateNode.id, "joins"));
      }
      edges.push(edge(gateNode.id, target.id, "then"));
    } else {
      for (const before of predecessors) edges.push(edge(stepNodeId(before.id), target.id, "then"));
    }
  }
  if (threatBox) {
    nodes.push(threatBox);
    const hasSuccessor = new Set(story.steps.flatMap((step) => step.after));
    for (const step of story.steps.filter((candidate) => !hasSuccessor.has(candidate.number))) {
      edges.push(edge(stepNodeId(step.id), threatBox.id, "realizes"));
    }
    for (const damage of damageBoxes) {
      nodes.push(damage);
      edges.push(edge(threatBox.id, damage.id, "leads_to"));
    }
    for (const mitigation of mitigationBoxes) {
      nodes.push(mitigation);
      edges.push(edge(mitigation.id, threatBox.id, "mitigates"));
    }
    for (const target of targetBoxes) {
      nodes.push(target);
      edges.push(edge(threatBox.id, target.id, "targets"));
    }
  }

  routeEdges(nodes, edges, {
    mainTop: top,
    mainBottom: top + mainBand,
    targetRowBottom: MARGIN + targetBand,
    mitigationRowTop: bottomY,
  });
  const right = Math.max(
    contentRight,
    ...nodes.map((node) => node.x + node.width / 2),
    ...edges.flatMap((item) => (item.labelAt ? [item.labelAt.x + item.labelWidth / 2] : [])),
  );
  const bottom = Math.max(
    ...nodes.map((node) => node.y + node.height / 2),
    top + mainBand,
    ...edges.flatMap((item) => item.points.map((point) => point.y)),
  );
  return {
    pathId: story.pathId,
    status: story.status.kind,
    nodes,
    edges,
    width: Math.ceil(right + MARGIN),
    height: Math.ceil(bottom + MARGIN),
  };
}

/**
 * Inline SVG for a laid-out diagram: no script, no external reference, every
 * label escaped. It scales to the width of its container.
 */
export function pathDiagramSvg(diagram: PathDiagram, accessibleName: string, anchor?: string): string {
  // The arrow marker's id must be unique in the page: the caller passes the
  // path's unique anchor when a page holds several diagrams.
  const uid = (anchor ?? diagram.pathId).replace(/[^A-Za-z0-9_-]/g, "-");
  const marker = `arrow-${uid}`;
  const known = new Set(diagram.nodes.map((node) => node.id));
  const routed = diagram.edges.filter((edgeValue) => known.has(edgeValue.source) && known.has(edgeValue.target));
  // Lines first, then every label on top, so no line is drawn over a label.
  const edgeMarkup = routed.map((edgeValue) => (
    `<g class="pd-edge pd-edge-${edgeValue.kind}"><path d="${roundedPath(edgeValue.points, CONNECTOR_RADIUS)}" marker-end="url(#${marker})"/></g>`
  )).join("");
  const labelMarkup = routed.map((edgeValue) => {
    if (!edgeValue.labelAt || !edgeValue.label) return "";
    const { x, y } = edgeValue.labelAt;
    return `<g class="pd-edge-label-group pd-edge-${edgeValue.kind}">`
      + `<rect class="pd-edge-label-bg" x="${num(x - edgeValue.labelWidth / 2)}" y="${num(y - LABEL_HEIGHT / 2)}" `
      + `width="${num(edgeValue.labelWidth)}" height="${LABEL_HEIGHT}" rx="4"/>`
      + `<text class="pd-edge-label" x="${num(x)}" y="${num(y + 4)}" text-anchor="middle">${escapeHtml(edgeValue.label)}</text></g>`;
  }).join("");
  const nodeMarkup = diagram.nodes.map((node) => {
    const left = node.x - node.width / 2;
    const topY = node.y - node.height / 2;
    const rx = node.kind === "gate" ? node.height / 2 : 8;
    const caption = node.captionLines.map((line, index) => (
      `<text class="pd-caption" x="${num(left + 10)}" y="${num(topY + PADDING_Y + 9 + index * CAPTION_HEIGHT)}">${escapeHtml(line)}</text>`
    )).join("");
    const firstLineY = node.kind === "gate"
      ? node.y + 5
      : topY + PADDING_Y + node.captionLines.length * CAPTION_HEIGHT + 11;
    const anchor = node.kind === "gate" ? "middle" : "start";
    const textX = node.kind === "gate" ? node.x : left + 10;
    const lines = node.lines.map((line, index) => (
      `<tspan x="${num(textX)}" y="${num(firstLineY + index * LINE_HEIGHT)}">${escapeHtml(line)}</tspan>`
    )).join("");
    return `<g class="pd-node pd-${node.kind}"><title>${escapeHtml(node.title)}</title>`
      + `<rect x="${num(left)}" y="${num(topY)}" width="${num(node.width)}" height="${num(node.height)}" rx="${rx}"/>`
      + `${caption}<text class="pd-text" text-anchor="${anchor}">${lines}</text></g>`;
  }).join("");
  return `<svg class="path-diagram pd-status-${diagram.status}" viewBox="0 0 ${diagram.width} ${diagram.height}" `
    + `width="${diagram.width}" height="${diagram.height}" role="img" aria-label="${escapeHtml(accessibleName)}" `
    + `preserveAspectRatio="xMinYMin meet" xmlns="http://www.w3.org/2000/svg">`
    + `<defs><marker id="${marker}" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">`
    + `<path d="M0,0.5 L10,5 L0,9.5 z" class="pd-arrow"/></marker></defs>`
    + `${edgeMarkup}${nodeMarkup}${labelMarkup}</svg>`;
}

/** Wraps text to lines of at most `width` characters, ending with "…" past `maxLines`. */
export function wrapLabel(text: string, width: number, maxLines = MAX_LINES): string[] {
  const words = text.replace(/\s+/g, " ").trim().split(" ").filter(Boolean);
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length <= width || !current) {
      current = candidate.length > width ? `${candidate.slice(0, width - 1)}…` : candidate;
    } else {
      lines.push(current);
      current = word.length > width ? `${word.slice(0, width - 1)}…` : word;
    }
  }
  if (current) lines.push(current);
  if (lines.length <= maxLines) return lines;
  const kept = lines.slice(0, maxLines);
  const last = kept[maxLines - 1];
  kept[maxLines - 1] = `${(last.length >= width ? last.slice(0, width - 1) : last).trimEnd()}…`;
  return kept;
}

/** "Reviewed by @handle" under a threat whose path a human decided; otherwise nothing. */
function reviewerLine(story: PathStory): string | undefined {
  const decided = ["accepted", "rejected", "changes_requested"].includes(story.status.kind);
  return decided && story.status.reviewers.length > 0
    ? `Reviewed by ${story.status.reviewers.join(", ")}`
    : undefined;
}

function box(
  id: string,
  objectId: string,
  kind: DiagramNodeKind,
  caption: string,
  label: string,
  size: { width: number; chars: number },
  note?: string,
): DiagramNode {
  const lines = [...wrapLabel(label, size.chars), ...(note ? wrapLabel(note, size.chars, 2) : [])];
  // Captions are small capitals with letter spacing: about as many characters fit as in the text.
  const captionLines = wrapLabel(caption, size.chars, 2);
  return {
    id,
    objectId,
    kind,
    caption,
    captionLines,
    lines,
    title: `${caption}: ${label}${note ? ` (${note})` : ""}`,
    x: 0,
    y: 0,
    width: size.width,
    height: PADDING_Y * 2 + captionLines.length * CAPTION_HEIGHT + lines.length * LINE_HEIGHT,
  };
}

function edge(source: string, target: string, kind: DiagramEdgeKind): DiagramEdge {
  const label = EDGE_LABELS[kind];
  return { id: `${source}->${target}`, source, target, kind, label, points: [], labelAt: null, labelWidth: labelWidth(label) };
}

/** Width of an edge label's background: about 5.9 px per character at 11 px bold, plus padding. */
function labelWidth(label: string): number {
  return label ? Math.ceil(label.length * 5.9 + 10) : 0;
}

interface Bands {
  mainTop: number;
  mainBottom: number;
  /** Bottom of the row of targeted elements above the main band. */
  targetRowBottom: number;
  /** Top of the row of mitigations below the main band. */
  mitigationRowTop: number;
}

/**
 * Routes every connector as a right-angled line and places its label.
 *
 * Left-to-right connectors leave the source's right side and enter the target's
 * left side; when the two are at different heights the line turns BUS_OFFSET
 * before the target, so every line into one box joins on one vertical line.
 * Lines from two or more final steps into the threat join just after the steps
 * instead, leaving room for one "realizes" on the shared stretch. A line that
 * would cross a box runs just outside the main band. Mitigations and targeted
 * elements connect from below and above through a shared line halfway across
 * the gap. A label is drawn once per shared line, on a straight stretch.
 */
function routeEdges(nodes: readonly DiagramNode[], edges: DiagramEdge[], bands: Bands): void {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  const count = (key: string) => edges.filter((item) => groupKey(item, "in") === key).length;
  const countOut = (key: string) => edges.filter((item) => groupKey(item, "out") === key).length;
  const labelled = new Set<string>();
  const middle = (bands.mainTop + bands.mainBottom) / 2;

  for (const item of edges) {
    const source = byId.get(item.source);
    const target = byId.get(item.target);
    if (!source || !target) continue;
    const fanIn = count(groupKey(item, "in")) > 1;
    const fanOut = countOut(groupKey(item, "out")) > 1;

    if (item.kind === "mitigates" || item.kind === "targets") {
      // Both point upwards: a mitigation (below) into the threat, the threat into
      // a targeted element (above). Out of the source's top, into the target's bottom.
      const start = { x: source.x, y: top(source) };
      const end = { x: target.x, y: bottom(target) };
      const busY = item.kind === "mitigates"
        ? (bands.mainBottom + bands.mitigationRowTop) / 2
        : (bands.targetRowBottom + bands.mainTop) / 2;
      item.points = Math.abs(start.x - end.x) < 0.5
        ? [start, end]
        : [start, { x: start.x, y: busY }, { x: end.x, y: busY }, end];
      // The label goes beside the stretch next to the threat, which every line in the group shares.
      const key = item.kind === "mitigates" ? groupKey(item, "in") : groupKey(item, "out");
      if (item.label && !labelled.has(key)) {
        labelled.add(key);
        const trunkX = item.kind === "mitigates" ? end.x : start.x;
        const trunkY = item.kind === "mitigates" ? (end.y + busY) / 2 : (start.y + busY) / 2;
        item.labelAt = { x: trunkX + 6 + item.labelWidth / 2, y: trunkY };
      }
      continue;
    }

    const start = { x: source.x + source.width / 2, y: source.y };
    const end = { x: target.x - target.width / 2, y: target.y };
    const joinNearSources = item.kind === "realizes" && fanIn;
    const busX = joinNearSources
      ? Math.max(...edges
        .filter((other) => groupKey(other, "in") === groupKey(item, "in"))
        .map((other) => {
          const node = byId.get(other.source);
          return node ? node.x + node.width / 2 : start.x;
        })) + BUS_OFFSET
      : end.x - BUS_OFFSET;
    let points: Point[] = Math.abs(start.y - end.y) < 0.5
      ? [start, end]
      : [start, { x: busX, y: start.y }, { x: busX, y: end.y }, end];
    if (crossesABox(points, nodes, source, target)) {
      // Run outside the main band, on the side nearer the two ends.
      const laneY = (start.y + end.y) / 2 <= middle ? bands.mainTop - LANE_OFFSET : bands.mainBottom + LANE_OFFSET;
      const outX = start.x + BUS_OFFSET;
      points = [start, { x: outX, y: start.y }, { x: outX, y: laneY }, { x: busX, y: laneY }, { x: busX, y: end.y }, end];
    }
    item.points = points;

    if (!item.label) continue;
    // One label per shared line: the stretch into a joined box, or out of a forking one.
    const key = joinNearSources ? groupKey(item, "in") : fanOut ? groupKey(item, "out") : item.id;
    if (labelled.has(key)) continue;
    labelled.add(key);
    let from: Point;
    let to: Point;
    if (joinNearSources) {
      [from, to] = [{ x: busX, y: end.y }, end];
    } else if (fanOut) {
      [from, to] = [start, { x: Math.min(busX, end.x), y: start.y }];
    } else {
      [from, to] = longestHorizontal(points);
    }
    item.labelAt = { x: (from.x + to.x) / 2, y: from.y - 9 };
  }
}

function groupKey(item: DiagramEdge, side: "in" | "out"): string {
  return side === "in" ? `in|${item.target}|${item.kind}` : `out|${item.source}|${item.kind}`;
}

function top(node: DiagramNode): number {
  return node.y - node.height / 2;
}

function bottom(node: DiagramNode): number {
  return node.y + node.height / 2;
}

function longestHorizontal(points: readonly Point[]): [Point, Point] {
  let best: [Point, Point] = [points[0], points[points.length - 1]];
  let length = -1;
  for (let index = 1; index < points.length; index += 1) {
    const [a, b] = [points[index - 1], points[index]];
    if (Math.abs(a.y - b.y) < 0.5 && Math.abs(b.x - a.x) > length) {
      length = Math.abs(b.x - a.x);
      best = [a, b];
    }
  }
  return best;
}

/** True when a segment of the line passes through a box other than its own two ends (4 px clearance). */
export function crossesABox(
  points: readonly Point[],
  nodes: readonly DiagramNode[],
  source?: DiagramNode,
  target?: DiagramNode,
): boolean {
  const clearance = 4;
  for (let index = 1; index < points.length; index += 1) {
    const [a, b] = [points[index - 1], points[index]];
    const [x1, x2] = [Math.min(a.x, b.x), Math.max(a.x, b.x)];
    const [y1, y2] = [Math.min(a.y, b.y), Math.max(a.y, b.y)];
    for (const node of nodes) {
      if (node === source || node === target) continue;
      const left = node.x - node.width / 2 - clearance;
      const right = node.x + node.width / 2 + clearance;
      const upper = node.y - node.height / 2 - clearance;
      const lower = node.y + node.height / 2 + clearance;
      if (x2 > left && x1 < right && y2 > upper && y1 < lower) return true;
    }
  }
  return false;
}

/** An SVG path through right-angled points, with corners rounded to `radius`. */
export function roundedPath(points: readonly Point[], radius: number): string {
  if (points.length === 0) return "";
  let d = `M${num(points[0].x)},${num(points[0].y)}`;
  for (let index = 1; index < points.length - 1; index += 1) {
    const [before, corner, after] = [points[index - 1], points[index], points[index + 1]];
    const inLength = Math.hypot(corner.x - before.x, corner.y - before.y);
    const outLength = Math.hypot(after.x - corner.x, after.y - corner.y);
    const r = Math.min(radius, inLength / 2, outLength / 2);
    if (r < 0.5) {
      d += ` L${num(corner.x)},${num(corner.y)}`;
      continue;
    }
    const enter = { x: corner.x - ((corner.x - before.x) / inLength) * r, y: corner.y - ((corner.y - before.y) / inLength) * r };
    const leave = { x: corner.x + ((after.x - corner.x) / outLength) * r, y: corner.y + ((after.y - corner.y) / outLength) * r };
    d += ` L${num(enter.x)},${num(enter.y)} Q${num(corner.x)},${num(corner.y)} ${num(leave.x)},${num(leave.y)}`;
  }
  const last = points[points.length - 1];
  return `${d} L${num(last.x)},${num(last.y)}`;
}

function stack(column: readonly DiagramNode[], x: number, middle: number): void {
  const height = columnHeight(column);
  let y = middle - height / 2;
  for (const node of column) {
    node.x = x;
    node.y = y + node.height / 2;
    y += node.height + ROW_GAP;
  }
}

function spread(row: readonly DiagramNode[], centreX: number, y: number): void {
  const width = row.reduce((sum, node) => sum + node.width, 0) + Math.max(0, row.length - 1) * ROW_GAP;
  let x = Math.max(MARGIN, centreX - width / 2);
  for (const node of row) {
    node.x = x + node.width / 2;
    node.y = y;
    x += node.width + ROW_GAP;
  }
}

function columnHeight(column: readonly DiagramNode[]): number {
  if (column.length === 0) return 0;
  return column.reduce((sum, node) => sum + node.height, 0) + (column.length - 1) * ROW_GAP;
}

function rowHeight(row: readonly DiagramNode[]): number {
  return Math.max(0, ...row.map((node) => node.height));
}

function groupBy<T>(values: readonly T[], key: (value: T) => number): Map<number, T[]> {
  const groups = new Map<number, T[]>();
  for (const value of values) {
    const group = groups.get(key(value));
    if (group) group.push(value);
    else groups.set(key(value), [value]);
  }
  return groups;
}

function num(value: number): string {
  return String(Math.round(value * 10) / 10);
}
