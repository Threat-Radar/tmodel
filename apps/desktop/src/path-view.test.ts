import { describe, expect, it, vi } from "vitest";
import type cytoscape from "cytoscape";
import mvp01 from "./fixtures/report-input-mvp-01.json";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import { BOOKKEEPING_TYPES, buildModelReport } from "./model-report";
import type { ModelReportInput } from "./model-types";
import { layoutPathDiagram } from "./path-diagram";
import {
  AttackPathView,
  connectorGeometry,
  MAX_FIT_ZOOM,
  pathBannerText,
  pathOptionLabel,
  pathViewElements,
  type PathViewElements,
} from "./path-view";

const MVP02 = buildModelReport(mvp02 as unknown as ModelReportInput);
const MVP01 = buildModelReport(mvp01 as unknown as ModelReportInput);
const pivot = MVP02.attackPaths.find((row) => row.id === "attack-path:infotainment-pivot");
if (!pivot) throw new Error("fixture changed");

describe("attack-path view elements", () => {
  it("draws the shared layout at its own positions with a label on every node", () => {
    const diagram = layoutPathDiagram(pivot.story);
    const elements = pathViewElements(diagram);
    const nodes = elements.filter((element) => element.group === "nodes" && element.data.kind !== "edge-label");
    expect(nodes).toHaveLength(diagram.nodes.length);
    for (const [index, node] of nodes.entries()) {
      expect(node.position).toEqual({ x: diagram.nodes[index].x, y: diagram.nodes[index].y });
      expect(String(node.data.label).trim().length).toBeGreaterThan(0);
      expect(BOOKKEEPING_TYPES.has(String(node.data.kind))).toBe(false);
    }
    const threat = nodes.find((node) => node.data.kind === "threat");
    expect(threat?.classes).toBe("threat status-not_reviewed");
    expect(String(threat?.data.label).replace(/\n/g, " ")).toMatch(/^THREAT · AI-PROPOSED, NOT REVIEWED Lateral movement/);
    expect(elements.filter((element) => element.group === "edges").map((edge) => edge.data.label))
      .toEqual(expect.arrayContaining(["then", "realizes", "leads to", "mitigates"]));
  });

  it("draws each connector on the layout's own route, so the app and the report match", () => {
    for (const row of [...MVP01.attackPaths, ...MVP02.attackPaths]) {
      const diagram = layoutPathDiagram(row.story);
      const byId = new Map(diagram.nodes.map((node) => [node.id, node]));
      const edges = pathViewElements(diagram).filter((element) => element.group === "edges");
      expect(edges).toHaveLength(diagram.edges.length);
      for (const edge of diagram.edges) {
        const drawn = edges.find((element) => element.data.id === edge.id);
        const source = byId.get(edge.source);
        const target = byId.get(edge.target);
        if (!drawn || !source || !target) throw new Error(`missing ${edge.id}`);
        // Rebuild what Cytoscape draws (edge-distances: endpoints) and compare with the route.
        const parse = (value: unknown) => String(value).split(" ").map((part) => Number.parseFloat(part));
        const [sx, sy] = parse(drawn.data.sourceEndpoint);
        const [tx, ty] = parse(drawn.data.targetEndpoint);
        const first = { x: source.x + sx, y: source.y + sy };
        const last = { x: target.x + tx, y: target.y + ty };
        const dx = last.x - first.x;
        const dy = last.y - first.y;
        const length = Math.hypot(dx, dy);
        const weights = drawn.data.segmentWeights as number[];
        const distances = drawn.data.segmentDistances as number[];
        const rebuilt = [first, ...weights.map((weight, index) => ({
          x: first.x + weight * dx + (-dy / length) * distances[index],
          y: first.y + weight * dy + (dx / length) * distances[index],
        })), last];
        expect(rebuilt).toHaveLength(edge.points.length);
        rebuilt.forEach((point, index) => {
          expect(point.x).toBeCloseTo(edge.points[index].x, 0);
          expect(point.y).toBeCloseTo(edge.points[index].y, 0);
        });
        expect(drawn.classes).toContain(weights.length > 0 ? "routed" : "direct");
        expect(connectorGeometry(edge, source, target).segmentWeights).toEqual(weights);
      }
    }
  });

  it("puts each label as a small fixed box where the layout placed it, never as a selectable node", () => {
    const diagram = layoutPathDiagram(pivot.story);
    const labels = pathViewElements(diagram).filter((element) => element.data.kind === "edge-label");
    const placed = diagram.edges.filter((edge) => edge.labelAt && edge.label);
    expect(labels).toHaveLength(placed.length);
    for (const edge of placed) {
      const label = labels.find((element) => element.data.id === `label|${edge.id}`);
      expect(label?.position).toEqual(edge.labelAt);
      expect(label).toMatchObject({ selectable: false, grabbable: false, data: { label: edge.label, width: edge.labelWidth } });
    }
  });

  it("says in words what the path's review state means", () => {
    expect(pathOptionLabel(pivot)).toBe("Infotainment-to-CAN pivot path (Rejected)");
    expect(pathBannerText(pivot)).toBe(
      "Rejected by @av-reviewer: an AI-proposed hypothesis. This path is not an accepted part of the model.",
    );
    expect(pathBannerText(MVP02.attackPaths[0])).toBe("Accepted by @av-reviewer: a human reviewed this path and accepted it.");
    const imds = MVP01.attackPaths.find((row) => row.id === "attack-path:imds-pivot");
    expect(imds && pathBannerText(imds)).toBe("Changes requested by @sec-reviewer. This path is not an accepted part of the model.");
  });
});

describe("attack-path view", () => {
  it("highlights a step from its button, as Enter or Space on the focused button does, and says which is pressed", () => {
    const summary = new FakeStepSummary(["attack-step:a", "attack-step:b"]);
    const { view } = harness({ summary });
    view.setVisible(true);
    view.setReport(MVP02);
    // A native <button> turns Enter and Space into a click; the view listens for that click.
    summary.activate("attack-step:b");
    expect(summary.items.map((item) => item.active)).toEqual([false, true]);
    expect(summary.items.map((item) => item.button.pressed)).toEqual(["false", "true"]);
    summary.activate("attack-step:a");
    expect(summary.items.map((item) => item.button.pressed)).toEqual(["true", "false"]);
  });

  it("is a fixed drawing the reader can pan and zoom, and Fit to view restores it", () => {
    let options: Record<string, unknown> = {};
    const { view, elements, core } = harness({ onCreate: (value) => { options = value; } });
    view.setVisible(true);
    view.setReport(MVP02);
    expect(options).toMatchObject({ userPanningEnabled: true, userZoomingEnabled: true, autoungrabify: true });
    core.fit.mockClear();
    elements.fit.click();
    expect(core.fit).toHaveBeenCalledTimes(1);
  });

  it("fills the path picker, opens the first path and fits it to the canvas", () => {
    const { view, elements, core } = harness();
    view.setVisible(true);
    view.setReport(MVP02);

    expect(elements.select.options.map((option) => option.textContent)).toEqual([
      "Remote diagnostic-injection path (Accepted)",
      "Infotainment-to-CAN pivot path (Rejected)",
    ]);
    expect(view.currentPathId).toBe("attack-path:remote-diag-injection");
    expect(elements.banner.className).toBe("path-view-banner rs-accepted");
    expect(elements.summary.innerHTML).toContain("Remote diagnostic-injection path");
    expect(core.added).toHaveLength(1);
    expect(core.fit).toHaveBeenCalledWith(undefined, 24);
  });

  it("never zooms a short path past its design size", () => {
    const { view, core } = harness({ zoomAfterFit: 3 });
    view.setVisible(true);
    view.setReport(MVP02);
    expect(core.zoomTo).toHaveBeenCalledWith(MAX_FIT_ZOOM);
    expect(core.center).toHaveBeenCalled();
  });

  it("opens a path by id, marks it rejected, and keeps it when the same model reloads", () => {
    const { view, elements } = harness();
    view.setReport(MVP02);
    view.showPath("attack-path:infotainment-pivot");
    expect(elements.select.value).toBe("attack-path:infotainment-pivot");
    expect(elements.banner.className).toBe("path-view-banner rs-rejected");

    view.setReport(buildModelReport(mvp02 as unknown as ModelReportInput));
    expect(view.currentPathId).toBe("attack-path:infotainment-pivot");

    view.setReport(MVP01);
    expect(view.currentPathId).toBe("attack-path:xxe-file-read");
  });

  it("waits to fit a hidden canvas until the view is shown", () => {
    const { view, core } = harness();
    view.setReport(MVP02);
    expect(core.fit).not.toHaveBeenCalled();
    view.setVisible(true);
    view.resize();
    expect(core.fit).toHaveBeenCalledTimes(1);
    view.resize();
    expect(core.fit).toHaveBeenCalledTimes(1);
  });

  it("explains an empty state instead of drawing", () => {
    const { view, elements } = harness();
    view.setReport(undefined, "Loading Brake ECU…");
    expect(elements.banner.textContent).toBe("Loading Brake ECU…");
    expect(elements.select.disabled).toBe(true);
    view.setReport({ ...MVP02, attackPaths: [] });
    expect(elements.banner.textContent).toBe("This model records no attack paths.");
  });
});

function harness({ zoomAfterFit = 0.9, onCreate, summary }: {
  zoomAfterFit?: number;
  onCreate?: (options: Record<string, unknown>) => void;
  summary?: FakeSummary | FakeStepSummary;
} = {}) {
  const elements = {
    select: new FakeSelect(),
    banner: { textContent: "", className: "" },
    canvas: {},
    summary: summary ?? new FakeSummary(),
    fit: new FakeButton(),
  };
  let zoom = 1;
  const collection = { remove: vi.fn(), length: 0 };
  const core = {
    added: [] as unknown[],
    fit: vi.fn(() => { zoom = zoomAfterFit; }),
    zoomTo: vi.fn((value: number) => { zoom = value; }),
    center: vi.fn(),
  };
  const fakeCore = {
    batch: (callback: () => void) => callback(),
    elements: () => ({ ...collection, length: core.added.length }),
    add: (elements: unknown) => core.added.push(elements),
    resize: vi.fn(),
    fit: core.fit,
    zoom: (value?: number) => {
      if (value === undefined) return zoom;
      core.zoomTo(value);
      return undefined;
    },
    center: core.center,
    on: vi.fn(),
    nodes: () => ({ unselect: vi.fn() }),
    // A step's drawing node is "step|<step id>" and stands for that step.
    getElementById: (id: string) => ({ select: vi.fn(), data: () => id.split("|")[1] }),
    destroy: vi.fn(),
  };
  const createCore = ((options: Record<string, unknown>) => {
    onCreate?.(options);
    return fakeCore;
  }) as unknown as typeof cytoscape;
  const documentRoot = { createElement: () => ({ value: "", textContent: "" }) } as unknown as Document;
  const view = new AttackPathView(elements as unknown as PathViewElements, documentRoot, createCore);
  return { view, elements, core };
}

class FakeButton {
  private listener?: () => void;
  addEventListener(_type: string, listener: () => void): void {
    this.listener = listener;
  }
  click(): void {
    this.listener?.();
  }
}

class FakeStepItem {
  active = false;
  readonly button = { pressed: "false", setAttribute: (_name: string, value: string) => { this.button.pressed = value; } };
  readonly classList = { toggle: (_name: string, on: boolean) => { this.active = on; } };
  constructor(readonly stepId: string) {}
  getAttribute(): string { return this.stepId; }
  querySelector(): FakeStepItem["button"] { return this.button; }
  closest(): FakeStepItem { return this; }
}

class FakeStepSummary {
  innerHTML = "";
  readonly items: FakeStepItem[];
  private listener?: (event: unknown) => void;
  constructor(stepIds: string[]) {
    this.items = stepIds.map((id) => new FakeStepItem(id));
  }
  addEventListener(_type: string, listener: (event: unknown) => void): void {
    this.listener = listener;
  }
  replaceChildren(): void {}
  querySelectorAll(): FakeStepItem[] {
    return this.items;
  }
  activate(stepId: string): void {
    this.listener?.({ target: this.items.find((item) => item.stepId === stepId) });
  }
}

class FakeSelect {
  value = "";
  disabled = false;
  options: { value: string; textContent: string }[] = [];
  addEventListener(): void {}
  replaceChildren(...options: { value: string; textContent: string }[]): void {
    this.options = options;
  }
}

class FakeSummary {
  innerHTML = "";
  addEventListener(): void {}
  replaceChildren(): void {
    this.innerHTML = "";
  }
  querySelectorAll(): never[] {
    return [];
  }
}
