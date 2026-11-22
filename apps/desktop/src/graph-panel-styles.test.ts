import { describe, expect, it } from "vitest";
// @ts-expect-error The app deliberately does not install @types/node; Vitest runs this in Node.
import { readFileSync } from "node:fs";

const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf8");

/** The body of the top-level rule whose selector is exactly `selector`. */
function rule(selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = new RegExp(`(?:^|\\n)${escaped} \\{([^}]*)\\}`).exec(styles);
  if (!match) throw new Error(`styles.css has no top-level rule for ${selector}`);
  return match[1];
}

describe("graph panel layout (#247)", () => {
  it("gives the canvas whatever height the rows above it leave", () => {
    expect(rule(".graph-panel")).toContain("display: flex;");
    expect(rule(".graph-panel")).toContain("flex-direction: column;");
    expect(rule(".graph-canvas")).toContain("flex: 1 1 0;");
  });

  it("does not size the panel with a fixed list of rows", () => {
    // A fixed list broke when #227 added the saved-view and proposals rows: the canvas
    // fell into an extra row with no height in the desktop app (#247).
    expect(rule(".graph-panel")).not.toContain("grid-template-rows");
  });
});
