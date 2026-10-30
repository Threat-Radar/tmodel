import { describe, expect, it } from "vitest";
import {
  FORCE_LAYOUT_MAX_EDGES,
  FORCE_LAYOUT_MAX_NODES,
  graphLayoutForSize,
  incrementalGraphLayoutForSize,
} from "./graph-layout";

describe("graph layout selection", () => {
  it("keeps CoSE for measured small-graph bounds", () => {
    expect(graphLayoutForSize(FORCE_LAYOUT_MAX_NODES, FORCE_LAYOUT_MAX_EDGES)).toMatchObject({
      name: "cose",
      numIter: 1200,
    });
  });

  it("preserves positions when extending a small neighborhood", () => {
    expect(graphLayoutForSize(7, 8, true)).toMatchObject({
      name: "cose",
      randomize: false,
      padding: 56,
    });
  });

  it("uses CoSE without viewport fitting for incremental small-graph updates", () => {
    expect(incrementalGraphLayoutForSize(7, 8)).toMatchObject({
      name: "cose",
      randomize: false,
      fit: false,
    });
  });

  it("uses the deterministic grid fallback above either measured bound", () => {
    expect(graphLayoutForSize(FORCE_LAYOUT_MAX_NODES + 1, 1)).toMatchObject({ name: "grid" });
    expect(graphLayoutForSize(1, FORCE_LAYOUT_MAX_EDGES + 1)).toMatchObject({ name: "grid" });
    expect(graphLayoutForSize(3_000, 5_997)).toMatchObject({
      name: "grid",
      animate: false,
      avoidOverlap: true,
    });
    expect(incrementalGraphLayoutForSize(3_000, 5_997)).toBeUndefined();
  });
});
