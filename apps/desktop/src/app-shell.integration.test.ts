import { describe, expect, it } from "vitest";
import html from "../index.html?raw";

describe("integrated application shell", () => {
  it("puts all four Library views under a single application tab", () => {
    const navigation = html.slice(html.indexOf('<nav class="app-navigation"'), html.indexOf("</nav>"));
    const tabs = [...navigation.matchAll(/role="tab"[^>]*>([^<]+)/g)].map((match) => match[1]);
    expect(tabs).toEqual(["Model report", "Attack paths", "Explore graph", "Library"]);
    const library = html.slice(html.indexOf('id="library-view-panel"'), html.indexOf('id="graph-view-panel"'));
    expect(library).toContain('role="tabpanel" aria-labelledby="library-tab"');
    expect(navigation).toMatch(/<\/div>\s*<select [^>]*id="library-view-select"[^>]*aria-label="Library view"[^>]* hidden>/);
    expect([...navigation.matchAll(/<option value="[^"]+">([^<]+)/g)].map((match) => match[1]))
      .toEqual(["All Library Records", "CWE Weaknesses", "Security Requirements", "SDL"]);
    expect(library).not.toContain('id="library-view-select"');
    for (const [view, workspace] of [
      ["records", "library"], ["weaknesses", "weakness"], ["requirements", "requirements"], ["sdl", "sdl"],
    ]) {
      const section = library.split(`data-library-view="${view}"`)[1].split('data-library-view=')[0];
      expect(section).toContain(`id="${workspace}-workspace"`);
      expect(section.split(">")[0].includes(" hidden")).toBe(view !== "records");
    }
  });

  it("keeps the compact header's brand, model picker, summary and engine indicator", () => {
    const header = html.slice(html.indexOf('<header class="app-header"'), html.indexOf("</header>"));
    expect(header).toContain("Threat Radar");
    expect(header).toContain("<h1>tmodel</h1>");
    for (const id of ["model-select", "model-picker-status", "model-picker-summary", "engine-status"]) {
      expect(header).toContain(`id="${id}"`);
    }
    expect(header).not.toContain("Read example threat models");
    expect(header).toContain('<label for="model-select">Model</label>');
  });

  it("keeps the full CWE attribution in a collapsed disclosure after pagination", () => {
    const attribution = html.match(/<details class="weakness-attribution">([\s\S]*?)<\/details>/);
    expect(attribution?.index).toBeGreaterThan(html.indexOf('id="weakness-page-next"'));
    expect(attribution?.[1]).toContain("<summary>© 2006–2026 The MITRE Corporation · CWE Terms of Use</summary>");
    expect(attribution?.[1]).toContain('id="weakness-attribution-notice"');
    expect(attribution?.[1]).toContain('id="weakness-attribution-license"');
    expect(attribution?.[1]).toContain('id="weakness-attribution-terms" href="https://cwe.mitre.org/about/termsofuse.html"');
  });

  it("keeps source disclosures and details prompts for the three Library record views", () => {
    const library = html.slice(html.indexOf('id="library-view-panel"'), html.indexOf('id="graph-view-panel"'));
    expect(library.match(/class="info-disclosure"/g)).toHaveLength(3);
    expect(library.match(/class="library-inspector-heading">Details<\/h2>/g)).toHaveLength(3);
    expect(library.match(/Select a row to view its details\./g)).toHaveLength(3);
    expect(library).not.toContain('class="data-source-notice"');
  });

  it("gives the three record tables a shared footer and accessible filter reset in the controls", () => {
    const library = html.slice(html.indexOf('id="library-view-panel"'), html.indexOf('id="graph-view-panel"'));
    expect(library.match(/class="library-pagination" role="group"/g)).toHaveLength(3);
    expect(library).not.toMatch(/-result-count|Rows per page/);
    for (const prefix of ["library", "weakness", "requirements"]) {
      expect(library.indexOf(`id="${prefix}-page-status"`)).toBeGreaterThan(library.indexOf(`id="${prefix}-table-region"`));
      expect(library).toContain(`id="${prefix}-page-previous" type="button" hidden disabled`);
      expect(library).toContain(`id="${prefix}-page-next" type="button" hidden disabled`);
      expect(library).toContain(`<label for="${prefix}-search">Search</label><button id="${prefix}-clear-filters"`);
    }
    expect(library).toContain('id="requirements-coverage" class="requirements-coverage" open');
    expect(library).toContain("cannot verify regulatory compliance or mitigation effectiveness");
  });

  it("keeps SDL's original model selector, status, and full-width content within Library", () => {
    const sdl = html.split('data-library-view="sdl"')[1].split('id="graph-view-panel"')[0];
    expect(sdl).toContain('<h2 id="sdl-heading">tmodel SDL</h2>');
    expect(sdl).toContain('<label for="sdl-model-select"><span>SDL model</span><select id="sdl-model-select"></select></label>');
    expect(sdl).toContain('id="sdl-status" class="library-request-status" role="status"');
    expect(sdl).toContain('<div id="sdl-content" class="sdl-content"></div>');
    expect(sdl).not.toMatch(/-search|-filter|-page-|data-sdl-sort|<aside|<button|<details/);
  });

  it("does not reuse an HTML id across the combined application shell", () => {
    const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
