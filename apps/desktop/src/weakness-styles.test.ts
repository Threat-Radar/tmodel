import { describe, expect, it } from "vitest";
// @ts-expect-error The app deliberately does not install @types/node; Vitest runs this in Node.
import { readFileSync } from "node:fs";

const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf8");

describe("weakness view color contrast", () => {
  it("keeps pagination status text readable in light and dark mode", () => {
    const [light, dark] = cssRules(".library-pagination");
    expect(contrastRatio(cssProperty(light, "color"), "#ffffff")).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(cssProperty(dark, "color"), "#111827")).toBeGreaterThanOrEqual(4.5);
  });

  it("keeps disabled controls legible and focus indicators explicit", () => {
    const [lightDisabled, darkDisabled] = cssRules(".library-pagination button:disabled");
    const [lightFocus, darkFocus] = cssRules(
      ".library-pagination button:focus-visible, .library-clear-filters:focus-visible, .requirements-coverage > summary:focus-visible, .coverage-body:focus-visible",
    );
    expect(contrastRatio(
      cssProperty(lightDisabled, "color"),
      cssProperty(lightDisabled, "background"),
    )).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(
      cssProperty(darkDisabled, "color"),
      cssProperty(darkDisabled, "background"),
    )).toBeGreaterThanOrEqual(4.5);
    expect(lightFocus).toContain("outline: 2px solid #4f46e5;");
    expect(darkFocus).toContain("outline-color: #a5b4fc;");
    expect(contrastRatio("#4f46e5", "#ffffff")).toBeGreaterThanOrEqual(3);
    expect(contrastRatio("#a5b4fc", "#111827")).toBeGreaterThanOrEqual(3);
  });

  it("keeps disclosure summaries and their keyboard focus visible in both themes", () => {
    const [lightSummary, darkSummary] = cssRules(".weakness-detail-section > summary");
    const [lightFocus, darkFocus] = cssRules(".weakness-detail-section > summary:focus-visible");
    expect(contrastRatio(cssProperty(lightSummary, "color"), "#ffffff")).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(cssProperty(darkSummary, "color"), "#111827")).toBeGreaterThanOrEqual(4.5);
    expect(lightFocus).toContain("outline: 2px solid #4f46e5;");
    expect(darkFocus).toContain("outline-color: #a5b4fc;");
  });
});

function cssRules(selector: string): string[] {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&");
  return [...styles.matchAll(new RegExp(`${escaped} \\{([^}]*)\\}`, "gu"))]
    .map((match) => match[1]);
}

function cssProperty(rule: string | undefined, name: string): string {
  const match = rule?.match(new RegExp(`(?:^|;)\\s*${name}:\\s*(#[0-9a-f]{6})`, "iu"));
  if (!match) throw new Error(`Missing ${name} in CSS rule`);
  return match[1];
}

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
