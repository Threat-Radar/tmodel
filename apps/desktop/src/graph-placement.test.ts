import { describe, expect, it } from "vitest";
import {
  PLACEMENT_OPTIONS,
  arrowheadBox,
  boxAt,
  edgeLabelBox,
  evaluatePlacement,
  findPlacement,
  isClearPlacement,
  overlapArea,
  segmentIntersectsBox,
  type Box,
  type Footprint,
  type PlacementAnchor,
  type PlacementRequest,
  type PlacementScene,
  type Point,
  type SceneEdge,
  type SceneNode,
} from "./graph-placement";

// The real style draws a 28px node with a wrapped label (76px wide) below it.
const FOOTPRINT: Footprint = { left: 38, right: 38, top: 15, bottom: 45 };
const ANCHOR = { id: "component:anchor", position: { x: 0, y: 0 } };

function sceneNode(id: string, position: Point, footprint = FOOTPRINT): SceneNode {
  return { id, position, box: boxAt(position, footprint) };
}

function sceneEdge(id: string, source: SceneNode, target: SceneNode, labelBox?: Box): SceneEdge {
  return {
    id,
    sourceId: source.id,
    targetId: target.id,
    source: source.position,
    target: target.position,
    targetRadius: 14,
    labelBox,
  };
}

function request(anchors: readonly PlacementAnchor[] = [ANCHOR], footprint = FOOTPRINT): PlacementRequest {
  return { footprint, anchors, fallbackCenter: { x: 0, y: 0 } };
}

function overlapsAny(position: Point, nodes: readonly SceneNode[], footprint = FOOTPRINT): boolean {
  const box = boxAt(position, footprint);
  return nodes.some((node) => overlapArea(box, node.box) > 0);
}

function distance(a: Point, b: Point): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

describe("collision-aware node placement", () => {
  it("uses the nearest free spot around the parent, facing the visible area", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    const scene: PlacementScene = {
      nodes: [anchor],
      edges: [],
      bounds: { x1: -100, y1: -400, x2: 600, y2: 400 },
    };

    const result = findPlacement(request(), scene);

    expect(result.collisions).toBe(0);
    expect(distance(result.position, ANCHOR.position)).toBeCloseTo(PLACEMENT_OPTIONS.firstRing);
    // The bounds' center lies to the right of the anchor.
    expect(result.position.x).toBeGreaterThan(0);
  });

  it("avoids every occupied node position, not only the parent's neighbors", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    const unrelated = [0, 1, 2, 3].map((index) => sceneNode(
      `component:other-${index}`,
      { x: 110 * Math.cos((index * Math.PI) / 2), y: 110 * Math.sin((index * Math.PI) / 2) },
    ));
    const scene: PlacementScene = { nodes: [anchor, ...unrelated], edges: [] };

    const result = findPlacement(request(), scene);

    expect(result.collisions).toBe(0);
    expect(overlapsAny(result.position, scene.nodes)).toBe(false);
  });

  it("keeps labels apart even where node centers are already far enough apart", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    // A neighbor whose long label hangs 90px below it: its body is clear of
    // the first-ring spot below the anchor, but its label is not.
    const tallLabel = sceneNode(
      "component:long-label",
      { x: 60, y: 40 },
      { left: 38, right: 38, top: 15, bottom: 90 },
    );
    const scene: PlacementScene = {
      nodes: [anchor, tallLabel],
      edges: [],
      bounds: { x1: -200, y1: 0, x2: 200, y2: 600 },
    };
    const below = { x: 0, y: PLACEMENT_OPTIONS.firstRing };
    expect(distance(below, tallLabel.position)).toBeGreaterThan(28);
    expect(evaluatePlacement(below, request(), scene).collisions).toBeGreaterThan(0);

    const result = findPlacement(request(), scene);

    expect(result.collisions).toBe(0);
    expect(overlapsAny(result.position, scene.nodes)).toBe(false);
  });

  it("treats existing edges, arrowheads and edge labels as occupied", () => {
    const small: Footprint = { left: 4, right: 4, top: 4, bottom: 4 };
    // Unlabelled endpoints, so the arrowhead lies outside the target's box.
    const source = sceneNode("component:source", { x: -300, y: 0 }, small);
    const target = sceneNode("component:target", { x: 300, y: 0 }, small);
    const label = { x1: -20, y1: -6, x2: 20, y2: 6 };
    const edge = sceneEdge("edge:source-target", source, target, label);
    const scene: PlacementScene = { nodes: [source, target], edges: [edge] };
    const far = { id: "component:far", position: { x: 0, y: 400 } };
    const probe = (position: Point) => evaluatePlacement(position, request([far], small), scene, {
      clearance: 0,
    }).collisions;

    // Under the line, away from its label and arrowhead.
    expect(probe({ x: -150, y: 0 })).toBe(1);
    // On the arrowhead, just before the target.
    const arrow = arrowheadBox(edge);
    expect(probe({ x: (arrow.x1 + arrow.x2) / 2, y: 20 })).toBe(0);
    expect(probe({ x: (arrow.x1 + arrow.x2) / 2, y: (arrow.y1 + arrow.y2) / 2 })).toBeGreaterThanOrEqual(2);
    // On the edge label, which also sits on the line.
    expect(probe({ x: 0, y: 0 })).toBe(2);
    expect(probe({ x: 0, y: 30 })).toBe(0);
  });

  it("does not place a node over an existing relationship running past its parent", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    const left = sceneNode("component:left", { x: -500, y: 110 });
    const right = sceneNode("component:right", { x: 500, y: 110 });
    const edge = sceneEdge("edge:left-right", left, right, { x1: -25, y1: 104, x2: 25, y2: 116 });
    const scene: PlacementScene = {
      nodes: [anchor, left, right],
      edges: [edge],
      // Below the anchor is where the viewport is, and where the line runs.
      bounds: { x1: -600, y1: -300, x2: 600, y2: 500 },
    };

    const result = findPlacement(request(), scene);
    const box = boxAt(result.position, FOOTPRINT);

    expect(result.collisions).toBe(0);
    expect(segmentIntersectsBox(edge.source, edge.target, box)).toBe(false);
    expect(overlapArea(box, arrowheadBox(edge))).toBe(0);
  });

  it("keeps the new relationship and its label off other nodes", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    const blocker = sceneNode("component:blocker", { x: 0, y: 150 });
    const scene: PlacementScene = { nodes: [anchor, blocker], edges: [] };
    const withLabel = request([{ ...ANCHOR, edgeLabel: { width: 60, height: 12 } }]);

    // Directly behind the blocker the new edge would run through it.
    expect(evaluatePlacement({ x: 0, y: 300 }, withLabel, scene).collisions).toBeGreaterThan(0);
    const label = edgeLabelBox({ x: 0, y: 300 }, ANCHOR.position, { width: 60, height: 12 });
    expect(overlapArea(label, blocker.box)).toBeGreaterThan(0);

    const result = findPlacement(withLabel, scene);
    expect(result.collisions).toBe(0);
    expect(segmentIntersectsBox(result.position, ANCHOR.position, blocker.box)).toBe(false);
  });

  it("searches progressively farther out of a crowded neighborhood, but stays close", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    // Every first-ring spot is taken; narrow gaps remain for the new edge.
    const crowd: SceneNode[] = [];
    for (let index = 0; index < 8; index += 1) {
      const angle = (index * Math.PI) / 4;
      crowd.push(sceneNode(`component:crowd-${index}`, {
        x: 110 * Math.cos(angle),
        y: 110 * Math.sin(angle),
      }, { left: 30, right: 30, top: 15, bottom: 35 }));
    }
    const scene: PlacementScene = { nodes: [anchor, ...crowd], edges: [] };
    const firstRing = Array.from({ length: 36 }, (_, index) => ({
      x: PLACEMENT_OPTIONS.firstRing * Math.cos((index * Math.PI) / 18),
      y: PLACEMENT_OPTIONS.firstRing * Math.sin((index * Math.PI) / 18),
    }));
    expect(firstRing.every((spot) => evaluatePlacement(spot, request(), scene).collisions > 0))
      .toBe(true);

    const result = findPlacement(request(), scene);

    expect(result.collisions).toBe(0);
    expect(overlapsAny(result.position, scene.nodes)).toBe(false);
    expect(distance(result.position, ANCHOR.position)).toBeGreaterThan(PLACEMENT_OPTIONS.firstRing);
    expect(distance(result.position, ANCHOR.position)).toBeLessThan(400);
  });

  it("reports remaining overlap when no clear position exists within the search radius", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    const filler: SceneNode[] = [];
    for (let x = -900; x <= 900; x += 80) {
      for (let y = -900; y <= 900; y += 60) {
        if (x !== 0 || y !== 0) filler.push(sceneNode(`component:${x}:${y}`, { x, y }));
      }
    }
    const scene: PlacementScene = { nodes: [anchor, ...filler], edges: [] };

    const result = findPlacement(request(), scene);

    expect(result.collisions).toBeGreaterThan(0);
    expect(Number.isFinite(result.cost)).toBe(true);
    expect(distance(result.position, ANCHOR.position)).toBeLessThanOrEqual(PLACEMENT_OPTIONS.maxRadius);
  });

  it("places a node with two placed neighbors between them, off the line joining them", () => {
    const a = sceneNode("component:a", { x: -200, y: 0 });
    const b = sceneNode("component:b", { x: 200, y: 0 });
    const scene: PlacementScene = { nodes: [a, b], edges: [sceneEdge("edge:a-b", a, b)] };

    const result = findPlacement(request([
      { id: a.id, position: a.position },
      { id: b.id, position: b.position },
    ]), scene);

    expect(result.collisions).toBe(0);
    expect(Math.abs(result.position.x)).toBeLessThan(120);
    expect(segmentIntersectsBox(a.position, b.position, boxAt(result.position, FOOTPRINT))).toBe(false);
  });

  it("prefers a visible spot over one outside the viewport, even at a longer distance", () => {
    const anchor = sceneNode(ANCHOR.id, { x: 0, y: 0 });
    // The anchor sits at the right edge of the view; the nearest ring spots
    // to its right would leave the node off-screen.
    const scene: PlacementScene = {
      nodes: [anchor],
      edges: [],
      bounds: { x1: -800, y1: -300, x2: 60, y2: 300 },
    };
    const result = findPlacement(request(), scene);
    const box = boxAt(result.position, FOOTPRINT);
    expect(box.x2).toBeLessThanOrEqual(60);
    expect(result.collisions).toBe(0);
  });

  it("keeps a clear layout position only when it is near a placed neighbor", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    const scene: PlacementScene = { nodes: [anchor], edges: [] };
    expect(isClearPlacement({ x: 200, y: 0 }, request(), scene)).toBe(true);
    expect(isClearPlacement({ x: PLACEMENT_OPTIONS.maxKeepDistance + 50, y: 0 }, request(), scene))
      .toBe(false);
    // On top of the neighbor is never kept.
    expect(isClearPlacement({ x: 10, y: 0 }, request(), scene)).toBe(false);
  });

  it("limits how much edge crossings can count against a position", () => {
    const anchor = sceneNode(ANCHOR.id, { x: 0, y: 0 });
    const small: Footprint = { left: 2, right: 2, top: 2, bottom: 2 };
    // Ten parallel lines between the anchor and the candidate.
    const edges = Array.from({ length: 10 }, (_, index) => {
      const x = 20 + index * 10;
      return sceneEdge(
        `edge:${index}`,
        sceneNode(`component:top-${index}`, { x, y: -500 }, small),
        sceneNode(`component:bottom-${index}`, { x, y: 500 }, small),
      );
    });
    const scene: PlacementScene = { nodes: [anchor], edges };
    const far = evaluatePlacement({ x: 200, y: 0 }, request([ANCHOR], small), scene, { clearance: 0 });
    const near = evaluatePlacement({ x: 15, y: 0 }, request([ANCHOR], small), scene, { clearance: 0 });
    // At most four crossings (60 each) are counted for the one new edge.
    expect(far.cost - near.cost).toBeLessThanOrEqual(4 * 60 + 0.6 * (200 - 15) + 1);
    expect(far.collisions).toBe(0);
  });

  it("is deterministic for the same scene", () => {
    const anchor = sceneNode(ANCHOR.id, ANCHOR.position);
    const scene: PlacementScene = { nodes: [anchor, sceneNode("component:x", { x: 110, y: 0 })], edges: [] };
    expect(findPlacement(request(), scene)).toEqual(findPlacement(request(), scene));
  });
});
