import { describe, expect, it } from "vitest";
import { GRAPH_CATEGORY_TOKENS, REVIEW_STATE_EDGE_STYLES } from "./graph-view";
// @ts-expect-error The app deliberately does not install @types/node; Vitest runs this in Node.
import { readFileSync } from "node:fs";

const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
const theme = readFileSync(new URL("./theme.css", import.meta.url), "utf8");

const [light, dark] = [...theme.matchAll(/:root \{([^}]+)\}/g)].map((block) =>
  Object.fromEntries([...block[1].matchAll(/--([\w-]+):\s*(#[\da-f]{6});/gi)]
    .map(([, token, color]) => [token, color])),
);

describe.each([["light", light], ["dark", dark]] as const)("%s theme contrast", (_, colors) => {
  it.each([
    ["text", "background"], ["text-secondary", "welcome-center"], ["text-secondary", "welcome-powder"],
    ["text-muted", "surface"], ["text-muted", "surface-inset"], ["text-muted", "surface-subtle"],
    ["text-secondary", "surface-inset"], ["link", "selected"], ["link", "surface-striped"],
    ["disabled-text", "disabled-bg"],
    ["primary-text", "primary-bg"], ["primary-text", "primary-hover"], ["primary-text", "primary-active"],
    ["success-text", "success-bg"], ["warning-text", "warning-bg"], ["review-text", "review-bg"], ["danger-text", "danger-bg"],
    ["text", "graph-canvas"], ["text-secondary", "graph-canvas"], ["text-secondary", "surface"],
    ["text", "danger-bg"], ["text", "review-bg"], ["text", "success-bg"],
    ["graph-status-accepted", "graph-canvas"], ["graph-product", "graph-canvas"],
    ["text", "path-step-bg"], ["text", "path-threat-bg"], ["text", "path-damage-bg"],
    ["text", "path-mitigation-bg"], ["text", "path-target-bg"],
    // The CAPEC table's muted "Not stated" cells, on every row background (#236).
    ["text-muted", "surface-striped"], ["text-muted", "hover"], ["text-muted", "selected"],
  ])("keeps %s readable on %s", (foreground, background) => {
    expect(contrastRatio(colors[foreground], colors[background])).toBeGreaterThanOrEqual(4.5);
  });

  it.each([
    ["focus", "background"], ["focus", "surface"], ["focus", "selected"],
    ["control-border", "background"], ["control-border", "surface"],
    ...["surface", "surface-inset", "background", "surface-raised", "surface-subtle", "surface-striped", "graph-canvas"]
      .map((surface) => ["scroll-thumb", surface]),
    ["graph-edge", "graph-canvas"], ["graph-arrow", "graph-canvas"],
    ["graph-highlight", "graph-canvas"], ["focus", "graph-canvas"],
    ...Object.values(GRAPH_CATEGORY_TOKENS).map((token) => [token, "graph-canvas"]),
    ...Object.values(REVIEW_STATE_EDGE_STYLES).map(({ token }) => [token, "graph-canvas"]),
    ["graph-step", "path-step-bg"], ["graph-threat", "path-threat-bg"],
    ["path-damage-line", "path-damage-bg"], ["graph-status-accepted", "path-mitigation-bg"],
    ["graph-product", "path-target-bg"],
  ])("provides at least 3:1 for %s on %s", (foreground, background) => {
    expect(contrastRatio(colors[foreground], colors[background])).toBeGreaterThanOrEqual(3);
  });
});

describe("Library controls use shared theme colors", () => {
  it("keeps pagination status and disabled controls readable", () => {
    expect(styles).toMatch(/\.library-pagination \{[^}]+color: var\(--text-muted\)/);
    expect(styles).toMatch(/\.library-pagination button:disabled \{[^}]+background: var\(--disabled-bg\); color: var\(--disabled-text\)/);
  });

  it("indicates keyboard focus on pagination and disclosures", () => {
    for (const selector of [
      ".library-pagination button:focus-visible",
      ".weakness-detail-section > summary:focus-visible",
      ".attack-pattern-detail-section > summary:focus-visible",
      ".attack-pattern-attribution summary:focus-visible",
      ".attack-pattern-attribution-content:focus-visible",
    ]) {
      expect(styles.indexOf(selector), selector).toBeGreaterThan(-1);
      const rule = styles.slice(styles.indexOf(selector)).split("}")[0];
      expect(rule).toContain("outline: 2px solid var(--focus)");
    }
  });

  it("styles the CAPEC inspector's catalog fields as the CWE inspector's", () => {
    for (const name of [
      "detail-section-body", "detail-items", "field-value", "field-row", "field-attribute", "field-label",
      "field-text", "identifier-link", "assertions", "assertion-provenance", "proposal-note", "section-count",
    ]) {
      const rule = (styles as string).split("\n")
        .find((line: string) => line.includes(`.weakness-${name}`) && line.includes("{"));
      expect(rule, name).toContain(`.attack-pattern-${name}`);
    }
    expect(styles).toMatch(/\.attack-pattern-missing \{ color: var\(--text-muted\); \}/);
  });
});

function contrastRatio(foreground: string, background: string): number {
  const foregroundLuminance = relativeLuminance(foreground);
  const backgroundLuminance = relativeLuminance(background);
  const lighter = Math.max(foregroundLuminance, backgroundLuminance);
  const darker = Math.min(foregroundLuminance, backgroundLuminance);
  return (lighter + 0.05) / (darker + 0.05);
}

function relativeLuminance(color: string): number {
  const channels = [1, 3, 5].map((offset) => Number.parseInt(color.slice(offset, offset + 2), 16) / 255);
  const [red, green, blue] = channels.map((channel) => (
    channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
  ));
  return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
}
