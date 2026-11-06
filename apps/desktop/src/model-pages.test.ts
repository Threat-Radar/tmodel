/// <reference types="vite/client" />
import { describe, expect, it } from "vitest";
import mvp01 from "./fixtures/report-input-mvp-01.json";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import { buildModelReport } from "./model-report";
import { modelPagePath, modelPagePaths, renderModelPages, type ModelPageBundle } from "./model-pages";
import type { ModelReportInput } from "./model-types";
import { defaultViewLeaks, renderModelReport } from "./report-render";

const inputs = [mvp01, mvp02] as unknown as ModelReportInput[];
const NAV = '<header class="site-nav"><a href="../index.html">tmodel</a></header>';
const bundle: ModelPageBundle = {
  nav_html: NAV,
  source_base_url: "https://github.com/Threat-Radar/tmodel/blob/main/spec/vectors",
  models: inputs.map((input) => ({ summary: input.model, graph: input.graph, attack_paths: input.attackPaths })),
  problems: [],
};

describe("static example-model pages", () => {
  const pages = renderModelPages(bundle, ".model-report{}");

  it("writes an index and one page per model", () => {
    expect(pages.map((page) => page.path)).toEqual([
      "index.html",
      "mvp-01-software-doc-service.html",
      "mvp-02-automotive-ecu.html",
    ]);
    const index = pages[0].content;
    expect(index).toContain('<a href="mvp-01-software-doc-service.html">Papermill Document Service</a>');
    expect(index).toContain('<a href="mvp-02-automotive-ecu.html">Telematics Control Unit (TCU)</a>');
    expect(index).toContain("Example data.");
  });

  it("renders each page with the app's own report renderer", () => {
    const page = pages[2].content;
    const report = renderModelReport(buildModelReport(inputs[1]), { contents: true });
    expect(page).toContain(report);
    expect(page).toContain(NAV);
    expect(page).toContain('<a href="index.html">Example models</a>');
    expect(page).toContain('href="https://github.com/Threat-Radar/tmodel/blob/main/spec/vectors/mvp-02-automotive-ecu.yaml"');
  });

  it("is self-contained: inline CSS, no script, relative links, no local path", () => {
    for (const page of pages) {
      expect(page.content.startsWith("<!doctype html>")).toBe(true);
      expect(page.content).not.toMatch(/<script/i);
      expect(page.content).not.toMatch(/<link\b/i);
      expect(page.content).not.toMatch(/\ssrc=/i);
      const hrefs = [...page.content.matchAll(/href="([^"]*)"/g)].map((match) => match[1]);
      for (const href of hrefs) {
        expect(href.startsWith("#") || /^[a-z0-9./-]+\.html(?:#.*)?$/.test(href) || href.startsWith("https://github.com/Threat-Radar/tmodel/")).toBe(true);
      }
      expect(page.content).not.toContain("/Users/");
    }
  });

  it("is deterministic, so a second build is a no-op", () => {
    expect(renderModelPages(structuredClone(bundle), ".model-report{}")).toEqual(pages);
  });

  it("names a page after its model id only", () => {
    expect(modelPagePath({ ...inputs[0].model, id: "Weird Name/../x" })).toBe("weird-name-x.html");
  });

  it("never gives two models the same page, nor one the index's name", () => {
    const summaries = [
      { ...inputs[0].model, id: "x", file: "x.yaml" },
      { ...inputs[0].model, id: "x", file: "x.yml" },
      { ...inputs[0].model, id: "X", file: "other.yaml" },
      { ...inputs[0].model, id: "index", file: "index.yaml" },
    ];
    expect([...modelPagePaths(summaries).values()]).toEqual(["x.html", "x-2.html", "x-3.html", "index-2.html"]);
  });

  it("puts each model's own disclaimer on its page, and the list notice on the index", () => {
    const index = pages[0].content;
    expect(index).toContain("The proposal examples were drafted by AI from published write-ups of real automotive attacks");
    for (const page of pages.slice(1)) {
      expect(page.content).toContain("illustrative threat model written for the tmodel project");
    }
  });
});

// The pages bin/publish-site wrote for every example model in spec/vectors:
// the same renderer the app uses, so this checks all eight models' default view.
const PUBLISHED = import.meta.glob("../../../docs/models/*.html", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

describe("published example-model pages (docs/models/)", () => {
  const entries = Object.entries(PUBLISHED).map(([path, content]) => [path.split("/").pop() ?? path, content] as const);

  it("has an index and a page for each of the eight example models", () => {
    expect(entries.map(([name]) => name)).toContain("index.html");
    expect(entries.length).toBeGreaterThanOrEqual(9);
  });

  it.each(entries)("%s shows no id, CURIE, CPE, purl or schema name with Details closed", (_name, content) => {
    expect(defaultViewLeaks(content)).toEqual([]);
  });

  it.each(entries.filter(([name]) => name !== "index.html"))(
    "%s has the six TARA tables in order: components, damage, threats, attack paths, mitigations, risk",
    (_name, content) => {
      const captions = [...content.matchAll(/<caption>([^<]+)<\/caption>/g)].map((match) => match[1]);
      const wanted = [
        "Products and components",
        "Damage scenarios: what could go wrong for the stakeholder",
        "Threats and their review status",
        "Attack paths: how each threat could be carried out",
        "Mitigations: what is done about the threats",
        "Risk: how likely and how bad, per threat",
      ];
      const positions = wanted.map((caption) => captions.indexOf(caption));
      expect(positions.every((position) => position > -1)).toBe(true);
      expect([...positions].sort((a, b) => a - b)).toEqual(positions);
    },
  );

  it("counts accepted reviews the same way in the model list (the engine) and on each page (the report)", () => {
    const index = entries.find(([name]) => name === "index.html")?.[1] ?? "";
    const listed = [...index.matchAll(/<a href="([^"]+\.html)">[^<]*<\/a><\/h2>[\s\S]*?(\d+) with an accepted human review/g)];
    expect(listed.length).toBe(entries.length - 1);
    for (const [, page, count] of listed) {
      const content = entries.find(([name]) => name === page)?.[1] ?? "";
      const chip = content.match(/<li class="summary-chip rs-accepted"><strong>(\d+)<\/strong>/);
      expect(Number(chip?.[1] ?? 0), page).toBe(Number(count));
    }
  });

  it("says a proposal model is drafted from a published attack, not an assessment of the real product", () => {
    const proposals = entries.filter(([name]) => name.startsWith("pv-"));
    expect(proposals.length).toBeGreaterThan(0);
    for (const [, content] of proposals) {
      expect(content).toContain("drafted by AI from the published write-up of a real automotive attack");
      expect(content).toContain("not a verified security assessment of the product it names");
      expect(content).not.toContain("not a security assessment of a real product");
    }
    for (const [name, content] of entries.filter(([file]) => /^(mvp|tv)-/.test(file))) {
      expect(content, name).toContain("illustrative threat model written for the tmodel project");
    }
  });
});
