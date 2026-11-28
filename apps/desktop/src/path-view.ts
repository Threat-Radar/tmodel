// The app's focused attack-path view (#208). Cytoscape draws the shared path
// layout (path-diagram.ts): ordered steps left to right, AND/OR gates where
// branches join, then the threat and its damage, mitigations underneath. Only
// path objects are drawn; bookkeeping records (Assertion, Review, Party,
// LifecyclePhase, View) never become nodes. The view is fitted to its canvas.
//
// It is a fixed drawing, not a graph to rearrange: boxes cannot be dragged,
// because their places carry the order and the routed lines depend on them.
// The reader can pan (drag the background) and zoom (scroll), and "Fit to view"
// restores the fitted drawing. The connectors are the layout's own routes,
// drawn exactly as the report's SVG draws them.

import { canvasTheme } from "./canvas-theme";
import cytoscape, { type Core, type ElementDefinition, type StylesheetJson } from "cytoscape";
import type { ModelReport, PathRow, ReportStatusKind } from "./model-report";
import {
  CONNECTOR_RADIUS,
  layoutPathDiagram,
  type DiagramEdge,
  type DiagramNode,
  type DiagramNodeKind,
  type PathDiagram,
} from "./path-diagram";
import { renderPathSummary } from "./report-render";

export interface PathViewElements {
  select: HTMLSelectElement;
  banner: HTMLElement;
  canvas: HTMLElement;
  summary: HTMLElement;
  /** "Fit to view": back to the fitted drawing after panning or zooming. */
  fit?: HTMLButtonElement;
}

// Largest zoom after fitting, so a short path is not blown up past its design size.
export const MAX_FIT_ZOOM = 1.25;
const FIT_PADDING = 24;

const NODE_TOKENS: Readonly<Record<DiagramNodeKind, { fill: string; line: string }>> = {
  step: { fill: "path-step-bg", line: "graph-step" },
  gate: { fill: "primary-bg", line: "primary-bg" },
  threat: { fill: "path-threat-bg", line: "graph-threat" },
  damage: { fill: "path-damage-bg", line: "path-damage-line" },
  mitigation: { fill: "path-mitigation-bg", line: "graph-status-accepted" },
  target: { fill: "path-target-bg", line: "graph-product" },
};

const STATUS_TOKENS: Partial<Record<ReportStatusKind, string>> = {
  rejected: "graph-status-rejected",
  changes_requested: "graph-status-changes",
  proposed: "graph-status-proposed",
  not_reviewed: "graph-status-proposed",
};

const LABEL_TOKENS: Partial<Record<string, string>> = {
  mitigates: "graph-status-accepted",
  targets: "graph-product",
};

/**
 * Cytoscape's form of a routed connector: its two end points as offsets from
 * the boxes' centres, and each corner as a weight along the line between those
 * end points and a distance across it (`edge-distances: endpoints`).
 */
export function connectorGeometry(item: DiagramEdge, source: DiagramNode, target: DiagramNode) {
  const first = item.points[0];
  const last = item.points[item.points.length - 1];
  const corners = item.points.slice(1, -1);
  const dx = last.x - first.x;
  const dy = last.y - first.y;
  const length = Math.hypot(dx, dy) || 1;
  return {
    sourceEndpoint: `${round(first.x - source.x)}px ${round(first.y - source.y)}px`,
    targetEndpoint: `${round(last.x - target.x)}px ${round(last.y - target.y)}px`,
    segmentWeights: corners.map((point) => round(((point.x - first.x) * dx + (point.y - first.y) * dy) / (length * length), 6)),
    segmentDistances: corners.map((point) => round(((point.x - first.x) * -dy + (point.y - first.y) * dx) / length)),
  };
}

/** Cytoscape elements for a laid-out diagram, at the layout's own positions and on its own routes. */
export function pathViewElements(diagram: PathDiagram): ElementDefinition[] {
  const nodes: ElementDefinition[] = diagram.nodes.map((node) => ({
    group: "nodes",
    data: {
      id: node.id,
      objectId: node.objectId,
      kind: node.kind,
      label: [...node.captionLines.map((line) => line.toUpperCase()), ...node.lines].join("\n"),
      title: node.title,
      width: node.width,
      height: node.height,
    },
    position: { x: node.x, y: node.y },
    classes: [
      node.kind,
      node.kind === "step" && diagram.status !== "accepted" ? `status-${diagram.status}` : "",
      node.kind === "threat" && diagram.threatStatus !== "accepted" ? `status-${diagram.threatStatus}` : "",
    ]
      .filter(Boolean)
      .join(" "),
  }));
  const byId = new Map(diagram.nodes.map((node) => [node.id, node]));
  const edges: ElementDefinition[] = [];
  const labels: ElementDefinition[] = [];
  for (const edge of diagram.edges) {
    const source = byId.get(edge.source);
    const target = byId.get(edge.target);
    if (!source || !target || edge.points.length < 2) continue;
    const geometry = connectorGeometry(edge, source, target);
    edges.push({
      group: "edges",
      data: { id: edge.id, source: edge.source, target: edge.target, label: edge.label, kind: edge.kind, ...geometry },
      classes: [edge.kind, geometry.segmentWeights.length > 0 ? "routed" : "direct"].join(" "),
    });
    // Labels are drawn as small fixed boxes at the layout's label positions, so
    // they sit on a straight stretch of their line, exactly where the SVG puts them.
    if (edge.labelAt && edge.label) {
      labels.push({
        group: "nodes",
        data: { id: `label|${edge.id}`, label: edge.label, kind: "edge-label", edgeKind: edge.kind, width: edge.labelWidth },
        position: { x: edge.labelAt.x, y: edge.labelAt.y },
        classes: "edge-label",
        selectable: false,
        grabbable: false,
      });
    }
  }
  return [...nodes, ...edges, ...labels];
}

export function pathOptionLabel(row: PathRow): string {
  return `${row.name} (${row.status.label})`;
}

/** The one-line banner above the drawing: status, reviewer and what it means. */
export function pathBannerText(row: PathRow): string {
  if (row.status.kind === "accepted" && !row.status.reviewed) {
    return "Human acceptance is not established. This path is not shown as reviewed.";
  }
  const reviewers = row.status.reviewers.length > 0 ? ` by ${row.status.reviewers.join(", ")}` : "";
  switch (row.status.kind) {
    case "accepted":
      return `Accepted${reviewers}: a human reviewed this path and accepted it.`;
    case "rejected":
      return `Rejected${reviewers}${row.source.kind === "ai" ? ": an AI-proposed hypothesis" : ""}. This path is not an accepted part of the model.`;
    case "changes_requested":
      return `Changes requested${reviewers}. This path is not an accepted part of the model.`;
    case "mixed":
      return "Mixed review states. This path is not shown as reviewed.";
    default:
      return `${row.status.label}. This path is a hypothesis until a human reviewer accepts it.`;
  }
}

export class AttackPathView {
  private cy?: Core;
  private report?: ModelReport;
  private current?: PathRow;
  private visible = false;
  private needsFit = false;

  constructor(
    private readonly elements: PathViewElements,
    private readonly documentRoot: Document = document,
    private readonly createCore: typeof cytoscape = cytoscape,
  ) {
    elements.select.addEventListener("change", () => this.showPath(elements.select.value));
    elements.fit?.addEventListener("click", () => this.fit());
    // A step's button: clicked, or pressed with Enter or Space (a native button turns both into a click).
    elements.summary.addEventListener("click", (event) => {
      const item = (event.target as Element | null)?.closest?.("li[data-step]");
      const stepId = item?.getAttribute("data-step");
      if (stepId) this.highlight(`step|${stepId}`);
    });
  }

  get currentPathId(): string | undefined {
    return this.current?.id;
  }

  /** Shows a new model's paths, keeping the open path when the model still has it. */
  setReport(report: ModelReport | undefined, message?: string): void {
    this.report = report;
    const rows = report?.attackPaths ?? [];
    const options = rows.map((row) => {
      const option = this.documentRoot.createElement("option");
      option.value = row.id;
      option.textContent = pathOptionLabel(row);
      return option;
    });
    this.elements.select.replaceChildren(...options);
    this.elements.select.disabled = rows.length === 0;
    this.current = rows.find((row) => row.id === this.current?.id) ?? rows[0];
    if (!report) this.showMessage(message ?? "Open a model to see its attack paths.");
    else if (!this.current) this.showMessage("This model records no attack paths.");
    else this.render();
  }

  showPath(pathId: string): void {
    const row = this.report?.attackPaths.find((candidate) => candidate.id === pathId);
    if (!row) return;
    this.current = row;
    this.render();
  }

  setVisible(visible: boolean): void {
    this.visible = visible;
  }

  /** Re-measures the canvas after the view becomes visible and fits the path into it. */
  resize(): void {
    if (!this.visible || !this.cy) return;
    this.cy.resize();
    if (this.needsFit) this.fit();
  }

  dispose(): void {
    this.cy?.destroy();
    this.cy = undefined;
  }

  private showMessage(message: string): void {
    this.current = undefined;
    this.elements.banner.textContent = message;
    this.elements.banner.className = "path-view-banner";
    this.elements.summary.replaceChildren();
    this.cy?.elements().remove();
  }

  private render(): void {
    const row = this.current;
    if (!row) return;
    this.elements.select.value = row.id;
    this.elements.banner.textContent = pathBannerText(row);
    this.elements.banner.className = `path-view-banner rs-${row.status.kind}`;
    // The shared renderer escapes every model value (safe-html.ts).
    this.elements.summary.innerHTML = renderPathSummary(row);
    const cy = this.ensureCore();
    cy.batch(() => {
      cy.elements().remove();
      cy.add(pathViewElements(layoutPathDiagram(row.story)));
    });
    this.needsFit = true;
    if (this.visible) this.fit();
  }

  private fit(): void {
    const cy = this.cy;
    if (!cy || cy.elements().length === 0) return;
    cy.resize();
    cy.fit(undefined, FIT_PADDING);
    if (cy.zoom() > MAX_FIT_ZOOM) {
      cy.zoom(MAX_FIT_ZOOM);
      cy.center();
    }
    this.needsFit = false;
  }

  private highlight(nodeId: string): void {
    const cy = this.cy;
    if (!cy) return;
    cy.nodes().unselect();
    cy.getElementById(nodeId).select();
    const objectId = cy.getElementById(nodeId).data("objectId") as string | undefined;
    for (const item of this.elements.summary.querySelectorAll("li[data-step]")) {
      const active = item.getAttribute("data-step") === objectId;
      item.classList.toggle("is-active", active);
      // The step's button says whether its step is the one shown (keyboard and screen-reader users).
      item.querySelector("button.step-button")?.setAttribute("aria-pressed", String(active));
    }
  }

  refreshTheme(): void {
    this.cy?.style(pathViewStyle(this.documentRoot));
  }

  private ensureCore(): Core {
    if (this.cy) return this.cy;
    this.cy = this.createCore({
      container: this.elements.canvas,
      elements: [],
      layout: { name: "preset" },
      minZoom: 0.25,
      maxZoom: 2.5,
      // A fixed drawing: pan and zoom, but the boxes stay where the layout put them.
      userPanningEnabled: true,
      userZoomingEnabled: true,
      autoungrabify: true,
      boxSelectionEnabled: false,
      style: pathViewStyle(this.documentRoot),
    });
    this.cy.on("tap", "node[kind != 'edge-label']", (event) => this.highlight(event.target.id()));
    return this.cy;
  }
}

function round(value: number, digits = 2): number {
  const scale = 10 ** digits;
  return Math.round(value * scale) / scale;
}

function pathViewStyle(documentRoot: Document): StylesheetJson {
  const theme = canvasTheme(documentRoot);
  return [
    {
      selector: "node",
      style: {
        shape: "round-rectangle",
        width: "data(width)",
        height: "data(height)",
        label: "data(label)",
        "text-wrap": "wrap",
        "text-max-width": (element: cytoscape.NodeSingular) => `${Number(element.data("width")) - 16}px`,
        "text-valign": "center",
        "text-halign": "center",
        "text-justification": "left",
        "font-size": 12.5,
        "font-weight": 600,
        "font-family": theme("font-ui"),
        "line-height": 1.25,
        color: (element: cytoscape.NodeSingular) => theme(element.data("kind") === "gate" ? "primary-text" : "text"),
        "background-color": (element: cytoscape.NodeSingular) => theme(NODE_TOKENS[element.data("kind") as DiagramNodeKind]?.fill ?? "surface"),
        "border-width": 1.8,
        "border-color": (element: cytoscape.NodeSingular) => theme(NODE_TOKENS[element.data("kind") as DiagramNodeKind]?.line ?? "graph-arrow"),
      },
    },
    { selector: "node.gate", style: { "font-size": 13, "font-weight": 800, "text-justification": "center", "corner-radius": 15 } },
    { selector: "node.threat", style: { "border-width": 2.6 } },
    ...(Object.entries(STATUS_TOKENS).map(([kind, token]) => ({
      selector: `node.status-${kind}`,
      style: { "border-color": theme(token), "border-style": "dashed" as const },
    }))),
    {
      selector: "edge",
      style: {
        width: 1.6,
        "curve-style": "straight",
        "source-endpoint": (element: cytoscape.EdgeSingular) => String(element.data("sourceEndpoint")),
        "target-endpoint": (element: cytoscape.EdgeSingular) => String(element.data("targetEndpoint")),
        "line-color": theme("graph-arrow"),
        "target-arrow-color": theme("graph-arrow"),
        "target-arrow-shape": "triangle",
        "arrow-scale": 0.85,
      },
    },
    {
      selector: "edge.routed",
      style: {
        "curve-style": "round-segments",
        "edge-distances": "endpoints",
        "segment-weights": (element: cytoscape.EdgeSingular) => element.data("segmentWeights") as number[],
        "segment-distances": (element: cytoscape.EdgeSingular) => element.data("segmentDistances") as number[],
        "segment-radii": CONNECTOR_RADIUS,
      },
    },
    { selector: "edge.mitigates", style: { "line-color": theme("graph-status-accepted"), "target-arrow-color": theme("graph-status-accepted"), "line-style": "dashed", "line-dash-pattern": [6, 4] } },
    { selector: "edge.targets", style: { "line-color": theme("graph-product"), "target-arrow-color": theme("graph-product"), "line-style": "dashed", "line-dash-pattern": [2, 3] } },
    {
      selector: "node.edge-label",
      style: {
        shape: "round-rectangle",
        width: "data(width)",
        height: 16,
        label: "data(label)",
        "font-size": 11,
        "font-weight": 700,
        "font-family": theme("font-ui"),
        color: (element: cytoscape.NodeSingular) => theme(LABEL_TOKENS[String(element.data("edgeKind"))] ?? "text-secondary"),
        "text-valign": "center",
        "text-halign": "center",
        "text-max-width": "200px",
        "background-color": theme("graph-canvas"),
        "background-opacity": 1,
        "border-width": 0,
        events: "no",
      },
    },
    {
      selector: "node:selected",
      style: { "border-width": 4, "border-color": theme("focus"), "overlay-color": theme("focus"), "overlay-opacity": 0.12 },
    },
  ] as StylesheetJson;
}
