import { describe, expect, it } from "vitest";
import html from "../index.html?raw";

describe("integrated application shell", () => {
  it("puts all five Library views under a single application tab", () => {
    const navigation = html.slice(html.indexOf('<nav class="app-navigation"'), html.indexOf("</nav>"));
    const tabs = [...navigation.matchAll(/role="tab"[^>]*>([^<]+)/g)].map((match) => match[1]);
    expect(tabs).toEqual(["Model report", "Attack paths", "Explore graph", "Library"]);
    const library = html.slice(html.indexOf('id="library-view-panel"'), html.indexOf('id="graph-view-panel"'));
    expect(library).toContain('role="tabpanel" aria-labelledby="library-tab"');
    expect(navigation).toMatch(/<\/div>\s*<select [^>]*id="library-view-select"[^>]*aria-label="Library view"[^>]* hidden>/);
    expect([...navigation.matchAll(/<option value="[^"]+">([^<]+)/g)].map((match) => match[1]))
      .toEqual(["All Library Records", "CWE Weaknesses", "CAPEC Attack Patterns", "Security Requirements", "SDL"]);
    expect([...navigation.matchAll(/<option value="([^"]+)">/g)].map((match) => match[1]))
      .toEqual(["records", "weaknesses", "attack-patterns", "requirements", "sdl"]);
    expect(library).not.toContain('id="library-view-select"');
    for (const [view, workspace] of [
      ["records", "library"], ["weaknesses", "weakness"], ["attack-patterns", "attack-pattern"],
      ["requirements", "requirements"], ["sdl", "sdl"],
    ]) {
      const section = library.split(`data-library-view="${view}"`)[1].split('data-library-view=')[0];
      expect(section).toContain(`id="${workspace}-workspace"`);
      expect(section.split(">")[0].includes(" hidden")).toBe(view !== "records");
    }
  });

  it("keeps the compact header's brand, model picker, summary and engine indicator", () => {
    const header = html.slice(html.indexOf('<header class="app-header"'), html.indexOf("</header>"));
    expect(header).toContain("THREAT RADAR");
    expect(header).toContain('class="brand-radar" aria-hidden="true"');
    expect(header).toContain('<h1 class="brand-wordmark">tmodel</h1>');
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

  it("keeps the full CAPEC attribution in a disclosure after pagination, shown with the rows", () => {
    const attribution = html.match(/<details id="attack-pattern-attribution" class="attack-pattern-attribution" hidden>([\s\S]*?)<\/details>/);
    expect(attribution?.index).toBeGreaterThan(html.indexOf('id="attack-pattern-page-next"'));
    expect(attribution?.[1]).toContain('<summary id="attack-pattern-attribution-summary">© The MITRE Corporation · CAPEC Terms of Use</summary>');
    expect(attribution?.[1]).toContain('role="region" aria-label="CAPEC copyright and license" tabindex="0"');
    expect(attribution?.[1]).toContain('id="attack-pattern-attribution-notice"');
    expect(attribution?.[1]).toContain('id="attack-pattern-attribution-license"');
    expect(attribution?.[1]).toContain('id="attack-pattern-attribution-terms" href="https://capec.mitre.org/about/termsofuse.html"');
  });

  it("gives the CAPEC table sortable enumeration columns, labelled counts and a focusable inspector", () => {
    const section = html.split('data-library-view="attack-patterns"')[1].split("data-library-view=")[0];
    expect([...section.matchAll(/data-attack-pattern-sort data-sort="([^"]+)"/g)].map((match) => match[1]))
      .toEqual(["id", "name", "abstraction", "status", "likelihood", "severity"]);
    expect(section.match(/<th scope="col" aria-sort="ascending">/g)).toHaveLength(1);
    expect([...section.matchAll(/<th scope="col" title="[^"]+">([^<]+)<\/th>/g)].map((match) => match[1]))
      .toEqual(["CWE", "ATT&amp;CK", "Steps", "Mitigations"]);
    expect(section).toContain("<caption>CAPEC attack pattern records</caption>");
    expect(section).toContain('id="attack-pattern-table-region" class="library-table-region attack-pattern-table-region" role="region" aria-label="CAPEC attack patterns" tabindex="0" hidden');
    expect(section).toContain('id="attack-pattern-request-status" class="library-request-status" role="status" aria-live="polite"');
    expect(section).toContain('id="attack-pattern-sort-help" class="visually-hidden" aria-live="polite"');
    expect(section).toContain('id="attack-pattern-inspector" class="panel library-inspector attack-pattern-inspector" aria-labelledby="attack-pattern-inspector-heading" tabindex="0"');
    for (const filter of ["abstraction", "status", "likelihood", "severity"]) {
      expect(section).toContain(`<label for="attack-pattern-${filter}-filter">`);
    }
    // A label on a plain div is not announced; the group role makes it the controls' name.
    expect(section).toContain('class="library-controls attack-pattern-controls" role="group" aria-label="CAPEC attack pattern search and filters"');
  });

  it("keeps source disclosures and details prompts for the four Library record views", () => {
    const library = html.slice(html.indexOf('id="library-view-panel"'), html.indexOf('id="graph-view-panel"'));
    expect(library.match(/class="info-disclosure"/g)).toHaveLength(4);
    expect(library.match(/class="library-inspector-heading">Details<\/h2>/g)).toHaveLength(4);
    expect(library.match(/Select a row to view its details\./g)).toHaveLength(4);
    expect(library).not.toContain('class="data-source-notice"');
  });

  it("gives the four record tables a shared footer and accessible filter reset in the controls", () => {
    const library = html.slice(html.indexOf('id="library-view-panel"'), html.indexOf('id="graph-view-panel"'));
    expect(library.match(/class="library-pagination" role="group"/g)).toHaveLength(4);
    expect(library).not.toMatch(/-result-count|Rows per page/);
    for (const prefix of ["library", "weakness", "attack-pattern", "requirements"]) {
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
