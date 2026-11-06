import { describe, expect, it } from "vitest";
import mvp01 from "./fixtures/report-input-mvp-01.json";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import { buildModelReport } from "./model-report";
import type { ModelReportInput } from "./model-types";
import {
  defaultViewLeaks,
  exampleNotice,
  REPORT_SECTIONS,
  renderModelReport,
  renderPathSummary,
} from "./report-render";
import { escapeHtml, html, join, trusted } from "./safe-html";

const MVP01 = mvp01 as unknown as ModelReportInput;
const MVP02 = mvp02 as unknown as ModelReportInput;

/** What a reader sees by default: tag text outside every closed <details> toggle. */
function visibleText(markup: string): string {
  return markup
    .replace(/<details[\s\S]*?<\/details>/g, " ")
    .replace(/<svg[\s\S]*?<\/svg>/g, (svg) => svg.replace(/<title>[\s\S]*?<\/title>/g, " "))
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z#0-9]+;/g, " ")
    .replace(/\s+/g, " ");
}

describe("model report renderer", () => {
  const markup = renderModelReport(buildModelReport(MVP02));

  it("shows the title, the example-data banner and threat counts before any table or graph", () => {
    const title = markup.indexOf("Telematics Control Unit (TCU)");
    const banner = markup.indexOf("Example data.");
    const counts = markup.indexOf("1</strong> accepted");
    const firstTable = markup.indexOf("<table");
    const firstGraph = markup.indexOf("<svg");
    expect(title).toBeGreaterThan(-1);
    expect(banner).toBeGreaterThan(title);
    expect(counts).toBeGreaterThan(banner);
    expect(markup).toContain("1</strong> rejected");
    expect(firstTable).toBeGreaterThan(counts);
    expect(firstGraph).toBeGreaterThan(firstTable);
  });

  it("puts the sections in TARA order", () => {
    const positions = REPORT_SECTIONS.map((section) => markup.indexOf(`id="${section.id}"`));
    expect(positions.every((position) => position > -1)).toBe(true);
    expect([...positions].sort((a, b) => a - b)).toEqual(positions);
    expect(REPORT_SECTIONS.map((section) => section.title)).toEqual([
      "Assets and components",
      "Damage scenarios",
      "Threats",
      "Attack paths",
      "Mitigations",
      "Risk",
      "Requirements",
    ]);
  });

  it.each([
    ["mvp-01", MVP01],
    ["mvp-02", MVP02],
  ])("shows no model id, CPE, purl or schema name by default (%s)", (_name, input) => {
    const text = visibleText(renderModelReport(buildModelReport(input)));
    for (const node of input.graph.nodes) expect(text).not.toContain(node.id);
    expect(text).not.toMatch(/cpe:2\.3|pkg:[a-z]+\/|sha256:|swid:/);
    expect(text).not.toMatch(/\b(?:composed_of|uses_component|applies_in_phase|realizes_threat|realizes_damage|assertion_status|review_status|source_method|stated_as)\b/);
    expect(text).not.toMatch(/\b(?:ThreatInstance|AttackStep|AttackPath|AttackPattern|DamageScenario|RiskScore|LifecyclePhase)\b/);
  });

  it("keeps the technical record reachable behind Details", () => {
    expect(markup).toContain("<details class=\"row-details\"><summary>Details</summary>");
    expect(markup).toContain("component:tcu-soc");
    expect(markup).toContain("cpe:2.3:h:chipco:soc_t500");
  });

  it("marks the rejected AI pivot as rejected in the threat table and the path card", () => {
    const threatsSection = markup.slice(markup.indexOf('id="report-threats"'), markup.indexOf('id="report-paths"'));
    const pivotRow = threatsSection.slice(threatsSection.indexOf("Lateral movement from infotainment"));
    expect(pivotRow).toMatch(/<span class="status-badge rs-rejected">Rejected<\/span><div class="cell-note">Reviewer: <span class="handle">@av-reviewer<\/span><\/div><div class="cell-note">Rejected AI hypothesis<\/div>/);
    const card = markup.slice(markup.lastIndexOf("<article", markup.indexOf('id="path-attack-path-infotainment-pivot"')));
    expect(card.startsWith('<article class="path-card row-status-rejected"')).toBe(true);
    expect(card).toContain("<strong>Rejected:</strong> this path is not an accepted part of the model.");
    expect(card).toContain("pd-status-rejected");
  });

  it("writes AND/OR and step order into the text, not only the drawing", () => {
    expect(markup).toContain('<span class="gate gate-and">AND</span> <span class="cell-note">needs all of steps 1 and 2</span>');
    expect(markup).toContain('<span class="gate gate-or">OR</span> <span class="cell-note">needs any one of steps 1 or 2</span>');
    expect(markup).toContain("steps 1 → 3 → 4; steps 2 → 3 → 4");
  });

  it("states missing data as missing", () => {
    expect(markup).toContain("No assets are recorded in this model.");
    expect(markup).toContain("Not assessed: the model records no risk score for this threat.");
  });

  it("adds path-view buttons only in the app", () => {
    expect(markup).not.toContain("data-open-path");
    const interactive = renderModelReport(buildModelReport(MVP02), { interactive: true });
    expect(interactive).toContain('data-open-path="attack-path:infotainment-pivot"');
  });

  it("escapes model text and emits no script, handler or external reference", () => {
    const hostile = structuredClone(MVP02) as unknown as { graph: { nodes: { id: string; label: string; properties: Record<string, unknown> }[] } };
    const pivot = hostile.graph.nodes.find((node) => node.id === "threat-instance:infotainment-pivot");
    if (!pivot) throw new Error("fixture changed");
    pivot.label = "<img src=x onerror=alert(1)>";
    pivot.properties.description = "<script>alert(1)</script> Plain words.";
    const output = renderModelReport(buildModelReport(hostile as unknown as ModelReportInput), { contents: true, interactive: true });
    expect(output).not.toContain("<img");
    expect(output).not.toMatch(/<script/i);
    expect(output).toContain("&lt;img src=x onerror=alert(1)&gt;");
    expect(output).not.toMatch(/<[^>]*\son[a-z]+\s*=/i); // no handler attribute on any real tag
    expect(output).not.toMatch(/(?:src|href)="(?:https?:|javascript:|\/\/)/i);
  });

  it("renders a path summary for the app's path view from the same pieces", () => {
    const report = buildModelReport(MVP02);
    const summary = renderPathSummary(report.attackPaths[1]);
    expect(summary).toContain("Infotainment-to-CAN pivot path");
    expect(summary).toContain("rs-rejected");
    expect(summary).toContain('data-step="attack-step:gain-infotainment-foothold"');
    expect(summary).not.toContain("<svg");
  });
});

// The six TARA tables #208 asks for, in order, each inside its own section.
const SIX_TABLES = [
  ["report-components", "Products and components"],
  ["report-damage", "Damage scenarios: what could go wrong for the stakeholder"],
  ["report-threats", "Threats and their review status"],
  ["report-paths", "Attack paths: how each threat could be carried out"],
  ["report-mitigations", "Mitigations: what is done about the threats"],
  ["report-risk", "Risk: how likely and how bad, per threat"],
] as const;

function sectionMarkup(markup: string, id: string): string {
  const start = markup.indexOf(`<section class="report-section" id="${id}"`);
  const end = markup.indexOf("</section>", start);
  return start < 0 || end < 0 ? "" : markup.slice(start, end);
}

describe("the six TARA tables (#208)", () => {
  it.each([
    ["mvp-01", MVP01],
    ["mvp-02", MVP02],
  ])("has assets/components, damage, threats, attack paths, mitigations and risk tables, in order (%s)", (_name, input) => {
    const markup = renderModelReport(buildModelReport(input));
    const captions = [...markup.matchAll(/<caption>([^<]+)<\/caption>/g)].map((match) => match[1]);
    const positions = SIX_TABLES.map(([, caption]) => captions.indexOf(caption));
    expect(positions.every((position) => position > -1)).toBe(true);
    expect([...positions].sort((a, b) => a - b)).toEqual(positions);
    for (const [id, caption] of SIX_TABLES) {
      expect(sectionMarkup(markup, id)).toContain(`<caption>${caption}</caption>`);
    }
  });

  it("lists every attack path with its threat, ordered steps, feasibility, review status and reviewer", () => {
    const report = buildModelReport(MVP02);
    const section = sectionMarkup(renderModelReport(report), "report-paths");
    const table = section.slice(section.indexOf("<table"), section.indexOf("</table>"));
    const rows = table.split("<tr").slice(2); // after the header row
    expect(rows).toHaveLength(report.attackPaths.length);
    const pivot = rows.find((row) => row.includes("Infotainment-to-CAN pivot path")) ?? "";
    expect(pivot).toContain('href="#path-attack-path-infotainment-pivot"');
    expect(pivot).toContain("Lateral movement from infotainment domain into the safety CAN domain");
    const steps = [...pivot.matchAll(/<li value="(\d+)">([^<]+)<\/li>/g)].map((match) => [Number(match[1]), match[2]]);
    expect(steps.map(([number]) => number)).toEqual([1, 2, 3, 4]);
    expect(steps[3][1]).toBe("Pivot across the domain gateway onto the safety CAN bus");
    expect(pivot).toContain("Very low");
    expect(pivot).toContain('<span class="status-badge rs-rejected">Rejected</span>');
    expect(pivot).toContain('Reviewer: <span class="handle">@av-reviewer</span>');
    // The table sits before the detailed cards it links to, which are kept.
    expect(section.indexOf("<table")).toBeLessThan(section.indexOf('id="path-attack-path-infotainment-pivot"'));
    expect(section).toContain('<figure class="path-figure">');
  });
});

describe("renderer fixes from the #208 review", () => {
  it("shows every product of a multi-product model in the header, one line each", () => {
    const input = {
      ...MVP02,
      model: {
        ...MVP02.model,
        description: "Crypto Server Appliance: Product A, a server appliance. AFFECTED.\nEdge Sensor: Product X, an edge sensor (§1). It uses `composed_of`.",
      },
    };
    const markup = renderModelReport(buildModelReport(input));
    expect(markup).toContain('<p class="report-scope">Crypto Server Appliance: Product A, a server appliance. AFFECTED.</p>');
    expect(markup).toContain('<p class="report-scope">Edge Sensor: Product X, an edge sensor.</p>');
    expect(defaultViewLeaks(markup)).toEqual([]);
  });

  it("makes each step in the app's path view a keyboard-operable button, and leaves the report's steps as text", () => {
    const row = buildModelReport(MVP02).attackPaths[1];
    const summary = renderPathSummary(row);
    const buttons = [...summary.matchAll(/<li value="\d+" data-step="[^"]+"><button type="button" class="step-name step-button" aria-pressed="false" title="Show step (\d+) in the drawing">/g)];
    expect(buttons.map((match) => Number(match[1]))).toEqual(row.story.steps.map((step) => step.number));
    expect(renderModelReport(buildModelReport(MVP02))).not.toContain("step-button");
  });

  it("keeps a product description's modelling notes behind Details in the header", () => {
    const input = {
      ...MVP02,
      model: {
        ...MVP02.model,
        description: "A SYSTEM product (ADR-0002) that composes two subsystems. Recursive `composed_of` is the structural layer (§3).",
      },
    };
    const markup = renderModelReport(buildModelReport(input));
    expect(defaultViewLeaks(markup)).toEqual([]);
    expect(markup).toContain('<p class="report-scope">A SYSTEM product that composes two subsystems.</p>');
    expect(markup).toContain("Recursive `composed_of` is the structural layer (§3).</dd>");
  });

  it("tells a proposal drafted from a published attack apart from an illustrative model", () => {
    const proposal = exampleNotice({ model: { ...buildModelReport(MVP02).model, kind: "proposal" }, reviewers: [] });
    expect(proposal).toContain("drafted by AI from the published write-up of a real automotive attack");
    expect(proposal).toContain("not a verified security assessment of the product it names");
    expect(proposal).toContain("No human review is recorded in it");
    expect(proposal).not.toContain("not a security assessment of a real product");
    const core = exampleNotice(buildModelReport(MVP02));
    expect(core).toContain("illustrative threat model written for the tmodel project");
    // mvp-02 records reviews, so it does not claim none exist.
    expect(core).not.toContain("No human review is recorded");
  });

  it("warns when the engine could not compute some attack paths, at the top and on the path", () => {
    const report = buildModelReport({
      ...MVP02,
      attackPathFailures: [{ goal: "threat-instance:infotainment-pivot", message: "Engine request failed: timed out" }],
    });
    const markup = renderModelReport(report);
    const warning = markup.indexOf('<div class="report-warning"');
    expect(warning).toBeGreaterThan(-1);
    expect(warning).toBeLessThan(markup.indexOf("<table"));
    expect(markup).toContain("Engine request failed: timed out");
    expect(markup.match(/could not compute the ways through this path/g)).toHaveLength(1);
    const pivot = report.attackPaths.find((row) => row.story.alternativesMissing);
    expect(renderPathSummary(pivot ?? report.attackPaths[0])).toContain("could not compute the ways through this path");
  });

  it("gives every path card and diagram arrow a unique id, even when two path ids slug alike", () => {
    const report = buildModelReport(MVP02);
    report.attackPaths = report.attackPaths.map((row, index) => {
      const id = index === 0 ? "attack-path:a.b" : "attack-path:a-b";
      return { ...row, id, story: { ...row.story, pathId: id } };
    });
    const ids = [...renderModelReport(report).matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
    expect(new Set(ids).size).toBe(ids.length);
    expect(ids).toContain("path-attack-path-a-b");
    expect(ids).toContain("path-attack-path-a-b-2");
  });

  it("finds technical identifiers in the default view, and none behind Details", () => {
    const leaks = defaultViewLeaks(
      "<p>See threat-instance:x and composed_of in a ThreatInstance.</p>"
      + "<details><summary>Details</summary><dd>cpe:2.3:a:x and pkg:npm/y and realizes_threat</dd></details>"
      + '<p>Reviewed at <a href="https://example.test">https://example.test</a>.</p>',
    );
    expect(leaks).toEqual([
      "id (CURIE, CPE or purl): threat-instance:x",
      "schema field name: composed_of",
      "schema class name: ThreatInstance",
    ]);
    expect(defaultViewLeaks(renderModelReport(buildModelReport(MVP01)))).toEqual([]);
    expect(defaultViewLeaks(renderModelReport(buildModelReport(MVP02)))).toEqual([]);
  });
});

describe("safe html", () => {
  it("escapes interpolations and passes trusted fragments through", () => {
    const name = `"Tom" & <Jerry>'s`;
    expect(escapeHtml(name)).toBe("&quot;Tom&quot; &amp; &lt;Jerry&gt;&#39;s");
    expect(html`<b title="${name}">${name}</b>`.value).toBe(
      "<b title=\"&quot;Tom&quot; &amp; &lt;Jerry&gt;&#39;s\">&quot;Tom&quot; &amp; &lt;Jerry&gt;&#39;s</b>",
    );
    expect(html`${trusted("<i>x</i>")}${null}${undefined}${false}${[html`<u>${"<"}</u>`, "&"]}`.value)
      .toBe("<i>x</i><u>&lt;</u>&amp;");
    expect(join(["<a>", trusted("<b>")], ", ").value).toBe("&lt;a&gt;, <b>");
  });
});
