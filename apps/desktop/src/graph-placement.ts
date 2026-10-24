// Collision-aware placement for nodes added to an already laid-out graph.
// Pure geometry in model coordinates: the view supplies what is on the canvas
// and applies the chosen position, so existing nodes are never moved here.

export interface Point {
  x: number;
  y: number;
}

export interface Box {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

/** A node's extent around its center, including its label. */
export interface Footprint {
  left: number;
  right: number;
  top: number;
  bottom: number;
}

export interface SceneNode {
  id: string;
  position: Point;
  /** Node body and label, as drawn. */
  box: Box;
}

export interface SceneEdge {
  id: string;
  sourceId: string;
  targetId: string;
  source: Point;
  target: Point;
  /** Radius of the target node, so the arrowhead can be located. */
  targetRadius: number;
  labelBox?: Box;
}

export interface PlacementScene {
  nodes: SceneNode[];
  edges: SceneEdge[];
  /** Preferred area, normally the visible viewport. */
  bounds?: Box;
}

export interface PlacementAnchor {
  id: string;
  position: Point;
  /** Unrotated size of the label drawn on the relationship to this anchor. */
  edgeLabel?: { width: number; height: number };
}

export interface PlacementRequest {
  footprint: Footprint;
  /** Already placed nodes this node connects to. */
  anchors: readonly PlacementAnchor[];
  /** Search center when the node has no placed neighbor. */
  fallbackCenter: Point;
}

export interface PlacementEvaluation {
  cost: number;
  /** Overlaps that make a position unreadable: nodes, labels, edges, arrows. */
  collisions: number;
}

export interface PlacementResult extends PlacementEvaluation {
  position: Point;
}

export interface PlacementOptions {
  clearance: number;
  firstRing: number;
  ringStep: number;
  maxRadius: number;
  arcSpacing: number;
  maxKeepDistance: number;
}

export const PLACEMENT_OPTIONS: Readonly<PlacementOptions> = {
  // Gap kept between a new node (with its label) and anything already drawn.
  clearance: 10,
  firstRing: 110,
  ringStep: 40,
  // Search this far from the connected nodes before settling for the least
  // overlapping position; beyond it the relationship would be hard to follow.
  maxRadius: 720,
  // Distance between candidates along a ring.
  arcSpacing: 36,
  // A position left by the layout is only kept if a placed neighbor is this
  // close (twice CoSE's ideal edge length); otherwise the edge is too long.
  maxKeepDistance: 380,
};

const COST = {
  nodeOverlap: 1000,
  edgeUnderNode: 400,
  arrowhead: 400,
  edgeLabel: 400,
  newEdgeThroughNode: 300,
  newEdgeCrossing: 60,
  // Crossings are a preference, not a collision: capped so they can never
  // outweigh keeping the node visible.
  maxCrossingsPerEdge: 4,
  // Leaving the preferred area: a flat cost plus a cost per unit outside, so
  // a node just inside the edge is cheap and one off-screen costs more than
  // an edge or label overlap.
  outsideBounds: 400,
  outsideBoundsPerUnit: 12,
  distance: 0.6,
} as const;

/**
 * Finds a position near the node's connected neighbors, searching rings of
 * increasing radius and stopping at the first ring that has a clear spot.
 * If none is clear within `maxRadius`, the least overlapping one is returned
 * and `collisions` reports how many overlaps remain.
 */
export function findPlacement(
  request: PlacementRequest,
  scene: PlacementScene,
  options: Partial<PlacementOptions> = {},
): PlacementResult {
  const settings = { ...PLACEMENT_OPTIONS, ...options };
  const center = searchCenter(request);
  const local = nearbyScene(scene, center, settings.maxRadius + 120);
  const facing = scene.bounds ? boxCenter(scene.bounds) : center;
  const baseAngle = Math.atan2(facing.y - center.y, facing.x - center.x);

  let best: PlacementResult | undefined;
  const consider = (position: Point) => {
    // Candidates that cannot beat the best so far stop scoring early.
    const evaluation = evaluatePlacement(position, request, local, settings, best?.cost);
    if (!best || evaluation.cost < best.cost) best = { position, ...evaluation };
  };

  if (request.anchors.length > 1) consider(center);
  for (let radius = settings.firstRing; radius <= settings.maxRadius; radius += settings.ringStep) {
    const count = Math.max(12, Math.ceil((2 * Math.PI * radius) / settings.arcSpacing));
    for (let index = 0; index < count; index += 1) {
      // Alternate either side of the direction facing the viewport center so
      // equal-cost candidates resolve toward the visible area.
      const step = Math.ceil(index / 2) * (index % 2 ? 1 : -1);
      const angle = baseAngle + (step * 2 * Math.PI) / count;
      consider({ x: center.x + Math.cos(angle) * radius, y: center.y + Math.sin(angle) * radius });
    }
    if (best && best.collisions === 0 && withinBounds(best.position, request, scene)) break;
  }
  return best ?? { position: center, cost: Number.POSITIVE_INFINITY, collisions: 0 };
}

/**
 * Scores one position; exported so a node that already sits well can stay put.
 * Scoring stops once the cost exceeds `budget`, since the position can then no
 * longer win; the returned cost is then only a lower bound.
 */
export function evaluatePlacement(
  position: Point,
  request: PlacementRequest,
  scene: PlacementScene,
  options: Partial<PlacementOptions> = {},
  budget = Number.POSITIVE_INFINITY,
): PlacementEvaluation {
  const { clearance } = { ...PLACEMENT_OPTIONS, ...options };
  const box = inflate(boxAt(position, request.footprint), clearance);
  let cost = COST.distance * meanDistance(position, request);
  const overflow = boundsOverflow(position, request, scene);
  if (overflow > 0) cost += COST.outsideBounds + COST.outsideBoundsPerUnit * overflow;
  let collisions = 0;
  if (cost > budget) return { cost, collisions };

  for (const node of scene.nodes) {
    const area = overlapArea(box, node.box);
    if (area > 0) {
      collisions += 1;
      cost += COST.nodeOverlap + area;
    }
  }
  if (cost > budget) return { cost, collisions };

  for (const edge of scene.edges) {
    if (segmentIntersectsBox(edge.source, edge.target, box)) {
      collisions += 1;
      cost += COST.edgeUnderNode;
    }
    if (overlapArea(box, arrowheadBox(edge)) > 0) {
      collisions += 1;
      cost += COST.arrowhead;
    }
    if (edge.labelBox && overlapArea(box, edge.labelBox) > 0) {
      collisions += 1;
      cost += COST.edgeLabel;
    }
  }
  if (cost > budget) return { cost, collisions };

  // The node's own relationships will be drawn to its anchors; keep those
  // lines and their labels off other nodes and labels, and limit how many
  // existing lines they cross.
  for (const anchor of request.anchors) {
    const labelBox = anchor.edgeLabel
      ? edgeLabelBox(position, anchor.position, anchor.edgeLabel)
      : undefined;
    for (const node of scene.nodes) {
      if (node.id === anchor.id) continue;
      if (segmentIntersectsBox(position, anchor.position, node.box)) {
        collisions += 1;
        cost += COST.newEdgeThroughNode;
      }
      if (labelBox && overlapArea(labelBox, node.box) > 0) {
        collisions += 1;
        cost += COST.edgeLabel;
      }
    }
    let crossings = 0;
    for (const edge of scene.edges) {
      if (crossings >= COST.maxCrossingsPerEdge) break;
      if (edge.sourceId === anchor.id || edge.targetId === anchor.id) continue;
      if (segmentsCross(position, anchor.position, edge.source, edge.target)) crossings += 1;
    }
    cost += COST.newEdgeCrossing * crossings;
    if (cost > budget) return { cost, collisions };
  }

  return { cost, collisions };
}

export function boxAt(position: Point, footprint: Footprint): Box {
  return {
    x1: position.x - footprint.left,
    y1: position.y - footprint.top,
    x2: position.x + footprint.right,
    y2: position.y + footprint.bottom,
  };
}

export function overlapArea(a: Box, b: Box): number {
  const width = Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1);
  const height = Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1);
  return width > 0 && height > 0 ? width * height : 0;
}

/** Liang–Barsky clip: does the segment pass through the box? */
export function segmentIntersectsBox(from: Point, to: Point, box: Box): boolean {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  let enter = 0;
  let exit = 1;
  const edges: [number, number][] = [
    [-dx, from.x - box.x1],
    [dx, box.x2 - from.x],
    [-dy, from.y - box.y1],
    [dy, box.y2 - from.y],
  ];
  for (const [p, q] of edges) {
    if (p === 0) {
      if (q < 0) return false;
      continue;
    }
    const t = q / p;
    if (p < 0) enter = Math.max(enter, t);
    else exit = Math.min(exit, t);
    if (enter > exit) return false;
  }
  return true;
}

/** True when two segments cross at a point that is not a shared endpoint. */
export function segmentsCross(a1: Point, a2: Point, b1: Point, b2: Point): boolean {
  const d1 = cross(b1, b2, a1);
  const d2 = cross(b1, b2, a2);
  const d3 = cross(a1, a2, b1);
  const d4 = cross(a1, a2, b2);
  return d1 * d2 < 0 && d3 * d4 < 0;
}

/** Area around the arrowhead drawn where an edge meets its target node. */
export function arrowheadBox(edge: SceneEdge): Box {
  const dx = edge.target.x - edge.source.x;
  const dy = edge.target.y - edge.source.y;
  const length = Math.hypot(dx, dy) || 1;
  const back = edge.targetRadius + 6;
  const tip = { x: edge.target.x - (dx / length) * back, y: edge.target.y - (dy / length) * back };
  return { x1: tip.x - 8, y1: tip.y - 8, x2: tip.x + 8, y2: tip.y + 8 };
}

/**
 * A position that needs no adjustment: nothing overlaps, it is in view and
 * it stays reasonably close to at least one placed neighbor.
 */
export function isClearPlacement(
  position: Point,
  request: PlacementRequest,
  scene: PlacementScene,
  options: Partial<PlacementOptions> = {},
): boolean {
  const { maxKeepDistance } = { ...PLACEMENT_OPTIONS, ...options };
  const nearAnchor = request.anchors.length === 0
    || request.anchors.some((anchor) => distance(position, anchor.position) <= maxKeepDistance);
  return nearAnchor
    && withinBounds(position, request, scene)
    && evaluatePlacement(position, request, scene).collisions === 0;
}

/** Axis-aligned extent of a relationship label drawn along its edge. */
export function edgeLabelBox(from: Point, to: Point, size: { width: number; height: number }): Box {
  const angle = Math.atan2(to.y - from.y, to.x - from.x);
  const width = Math.abs(size.width * Math.cos(angle)) + Math.abs(size.height * Math.sin(angle));
  const height = Math.abs(size.width * Math.sin(angle)) + Math.abs(size.height * Math.cos(angle));
  const middle = { x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 };
  return {
    x1: middle.x - width / 2,
    y1: middle.y - height / 2,
    x2: middle.x + width / 2,
    y2: middle.y + height / 2,
  };
}

/** How far the node and its label extend beyond the preferred area. */
function boundsOverflow(position: Point, request: PlacementRequest, scene: PlacementScene): number {
  if (!scene.bounds) return 0;
  const box = boxAt(position, request.footprint);
  const { bounds } = scene;
  return Math.max(0, bounds.x1 - box.x1, bounds.y1 - box.y1, box.x2 - bounds.x2, box.y2 - bounds.y2);
}

function withinBounds(position: Point, request: PlacementRequest, scene: PlacementScene): boolean {
  return boundsOverflow(position, request, scene) === 0;
}

function searchCenter(request: PlacementRequest): Point {
  if (request.anchors.length === 0) return request.fallbackCenter;
  const sum = request.anchors.reduce(
    (total, anchor) => ({ x: total.x + anchor.position.x, y: total.y + anchor.position.y }),
    { x: 0, y: 0 },
  );
  return { x: sum.x / request.anchors.length, y: sum.y / request.anchors.length };
}

function meanDistance(position: Point, request: PlacementRequest): number {
  const targets = request.anchors.length > 0
    ? request.anchors.map((anchor) => anchor.position)
    : [request.fallbackCenter];
  return targets.reduce((total, target) => total + distance(position, target), 0) / targets.length;
}

/** Restricts obstacles to the search area so large graphs stay cheap. */
function nearbyScene(scene: PlacementScene, center: Point, reach: number): PlacementScene {
  const area = { x1: center.x - reach, y1: center.y - reach, x2: center.x + reach, y2: center.y + reach };
  return {
    bounds: scene.bounds,
    nodes: scene.nodes.filter((node) => overlapArea(area, node.box) > 0),
    edges: scene.edges.filter((edge) => segmentIntersectsBox(edge.source, edge.target, area)),
  };
}

function inflate(box: Box, amount: number): Box {
  return { x1: box.x1 - amount, y1: box.y1 - amount, x2: box.x2 + amount, y2: box.y2 + amount };
}

function boxCenter(box: Box): Point {
  return { x: (box.x1 + box.x2) / 2, y: (box.y1 + box.y2) / 2 };
}

function cross(origin: Point, a: Point, b: Point): number {
  return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x);
}

function distance(a: Point, b: Point): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}
