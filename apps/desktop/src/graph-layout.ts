export const FORCE_LAYOUT_MAX_NODES = 250;
export const FORCE_LAYOUT_MAX_EDGES = 500;

const COSE_LAYOUT = {
  name: "cose",
  animate: false,
  fit: true,
  padding: 48,
  idealEdgeLength: 190,
  nodeOverlap: 48,
  nodeRepulsion: 18000,
  nodeDimensionsIncludeLabels: true,
  componentSpacing: 60,
  gravity: 0.4,
  numIter: 1200,
} as const;

const LARGE_GRAPH_LAYOUT = {
  name: "grid",
  animate: false,
  fit: true,
  padding: 48,
  avoidOverlap: true,
  condense: true,
} as const;

export function graphLayoutForSize(
  nodeCount: number,
  edgeCount: number,
  preservePositions = false,
) {
  if (nodeCount <= FORCE_LAYOUT_MAX_NODES && edgeCount <= FORCE_LAYOUT_MAX_EDGES) {
    return preservePositions
      ? { ...COSE_LAYOUT, randomize: false, padding: 56 }
      : COSE_LAYOUT;
  }
  return LARGE_GRAPH_LAYOUT;
}

export function incrementalGraphLayoutForSize(nodeCount: number, edgeCount: number) {
  if (nodeCount > FORCE_LAYOUT_MAX_NODES || edgeCount > FORCE_LAYOUT_MAX_EDGES) return undefined;
  return { ...COSE_LAYOUT, randomize: false, fit: false } as const;
}
