import { describe, expect, it } from "vitest";
import html from "../index.html?raw";

describe("integrated application shell", () => {
  it("keeps the Requirements and Weaknesses tabs and panels as distinct siblings", () => {
    expect(html).toContain(
      'id="requirements-tab" type="button" role="tab" aria-controls="requirements-view-panel"',
    );
    expect(html).toContain(
      'id="weakness-tab" type="button" role="tab" aria-controls="weakness-view-panel"',
    );
    expect(html).toContain(
      'id="requirements-view-panel" class="view-panel" role="tabpanel" aria-labelledby="requirements-tab"',
    );
    expect(html).toContain(
      'id="weakness-view-panel" class="view-panel" role="tabpanel" aria-labelledby="weakness-tab"',
    );
    expect(html).toMatch(
      /<div id="weakness-detail-sections"><\/div>\s*<\/aside>\s*<\/div>\s*<\/section>\s*<section id="requirements-view-panel"/,
    );
  });

  it("does not reuse an HTML id across the combined application shell", () => {
    const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
