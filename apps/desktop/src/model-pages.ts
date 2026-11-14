// Static Pages output for the example models (#208, #204, #202 item 1).
//
// Wraps the app's own report renderer in a self-contained page: CSS inline, no
// script, no remote asset, relative links only (docs/publishing/SKILL.md). The
// input is a bundle of engine responses written by docs/publishing/render_models.py,
// so a page shows exactly what the app shows for the same model.
//
// Node runs this file directly (type stripping): `.ts` value imports only.

import type { AttackPathResponse } from "./graph-types";
import type { EngineGraphResponse, ModelListProblem, ModelSummary } from "./model-types";
import { buildModelReport, readableDescription } from "./model-report.ts";
import { exampleNotice, MODEL_LIST_NOTICE, renderModelReport } from "./report-render.ts";
import { html, join, trusted } from "./safe-html.ts";

export interface ModelBundleEntry {
  summary: ModelSummary;
  graph: EngineGraphResponse;
  attack_paths: readonly AttackPathResponse[];
}

/** What render_models.py hands to the page writer. */
export interface ModelPageBundle {
  /** The shared site navigation for a page one directory below docs/ (site_nav.py). */
  nav_html: string;
  /** Where readers can see each model's source, e.g. the GitHub tree of spec/vectors. */
  source_base_url: string;
  models: readonly ModelBundleEntry[];
  problems: readonly ModelListProblem[];
}

export interface RenderedPage {
  /** File name inside docs/models/. */
  path: string;
  content: string;
}

// The static pages wear the site's look (docs/index.html, the bibliography and
// the reports): warm paper, one green accent, cards, light only. PAGE_CSS comes
// before report.css and SITE_REPORT_CSS after it, so the app's own report view
// keeps its look and only these pages change.
const PAGE_CSS = `
:root { --ink: #1a1916; --muted: #5c574e; --line: #e2dcd0; --paper: #f6f3ec; --card: #fffcf7; --accent: #1e4d3a; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }
.model-page { max-width: 920px; margin: 0 auto; padding: 22px 24px 40px; }
.breadcrumb { margin: 0 0 12px; font-size: 0.85rem; color: var(--muted); }
.breadcrumb a, .model-page-footer a, .model-index a { color: var(--accent); }
.model-page-footer { margin-top: 32px; padding-top: 14px; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.8rem; }
.model-page-footer code { font-size: 0.78rem; }
.model-index h1 { margin: 6px 0 6px; font-size: clamp(1.7rem, 3vw, 2.3rem); letter-spacing: -0.03em; }
.model-index .lead { max-width: 75ch; margin: 0 0 14px; color: var(--muted); font-size: 1.05rem; }
.model-list { display: grid; gap: 12px; margin: 16px 0 0; padding: 0; list-style: none; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
.model-list li { padding: 14px 16px; border: 1px solid var(--line); border-radius: 12px; background: var(--card); }
.model-list h2 { margin: 2px 0 6px; font-size: 1.05rem; }
.model-list p { margin: 0 0 6px; font-size: 0.88rem; }
.model-list .meta { color: var(--muted); font-size: 0.8rem; }
.model-list .kind { color: var(--accent); font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.problems { margin-top: 16px; color: #991b1b; font-size: 0.85rem; }
`;

// After report.css: its colours in the site palette, and its dark-mode values
// undone, since the rest of the site has no dark mode.
const SITE_REPORT_CSS = `
.model-report {
  --rp-text: #1a1916; --rp-muted: #5c574e; --rp-faint: #8a8377;
  --rp-surface: #fffcf7; --rp-subtle: #f6f3ec; --rp-border: #e2dcd0; --rp-accent: #1e4d3a;
  --rp-ok-bg: #e5efe8; --rp-ok-fg: #1e4d3a; --rp-ok-line: #6f9c80;
  --rp-bad-bg: #f6e4dc; --rp-bad-fg: #7f1d1d; --rp-bad-line: #c27a6a;
  --rp-warn-bg: #ffedd5; --rp-warn-fg: #9a3412; --rp-warn-line: #ea580c;
  --rp-hyp-bg: #f3ead3; --rp-hyp-fg: #6b4e16; --rp-hyp-line: #c99a3a;
  --rp-neutral-bg: #ece6da; --rp-neutral-fg: #5c574e;
  --rp-step-bg: #f5f3ff; --rp-step-line: #7c3aed;
  --rp-threat-bg: #fff1f2; --rp-threat-line: #be123c;
  --rp-damage-bg: #fff7ed; --rp-damage-line: #c2410c;
  --rp-mit-bg: #f0fdf4; --rp-mit-line: #15803d;
  --rp-target-bg: #eff6ff; --rp-target-line: #2563eb;
  --rp-gate-bg: #1a1916; --rp-gate-fg: #ffffff;
  --rp-edge: #6b665c;
}
.example-banner { border-color: #e0cfa3; background: #f3ead3; color: #6b4e16; }
.report-warning { border-color: #e3b5a8; background: #f6e4dc; color: #7f1d1d; }
.model-report .warning-note { color: #991b1b; }
`;

/** Every page for a bundle: the index first, then one page per model, in list order. */
export function renderModelPages(bundle: ModelPageBundle, reportCss: string): RenderedPage[] {
  const paths = modelPagePaths(bundle.models.map((entry) => entry.summary));
  const pages: RenderedPage[] = [{ path: "index.html", content: renderModelIndex(bundle, reportCss, paths) }];
  for (const entry of bundle.models) {
    pages.push({
      path: paths.get(entry.summary.file) ?? modelPagePath(entry.summary),
      content: renderModelPage(entry, bundle, reportCss),
    });
  }
  return pages;
}

export function modelPagePath(summary: ModelSummary): string {
  return `${summary.id.toLowerCase().replace(/[^a-z0-9-]+/g, "-")}.html`;
}

/**
 * Page file names by model file, unique even when two models share an id (e.g.
 * `x.yaml` and `x.yml`) or slug alike: later ones get "-2", "-3" …, never "index".
 */
export function modelPagePaths(summaries: readonly ModelSummary[]): Map<string, string> {
  const used = new Set(["index.html"]);
  const out = new Map<string, string>();
  for (const summary of summaries) {
    const base = modelPagePath(summary).replace(/\.html$/, "");
    let candidate = `${base}.html`;
    for (let suffix = 2; used.has(candidate); suffix += 1) candidate = `${base}-${suffix}.html`;
    used.add(candidate);
    out.set(summary.file, candidate);
  }
  return out;
}

export function renderModelPage(entry: ModelBundleEntry, bundle: ModelPageBundle, reportCss: string): string {
  const report = buildModelReport({
    model: entry.summary,
    graph: entry.graph,
    attackPaths: entry.attack_paths,
  });
  const source = `${bundle.source_base_url.replace(/\/$/, "")}/${encodeURIComponent(entry.summary.file)}`;
  const body = html`<main class="model-page">
<p class="breadcrumb"><a href="index.html">Example models</a> › ${entry.summary.title}</p>
${trusted(renderModelReport(report, { contents: true }))}
<footer class="model-page-footer">
<p>Built by the tmodel engine from <code>spec/vectors/${entry.summary.file}</code> (<a href="${source}">view the model source</a>). The same renderer draws the report in the tmodel app. Model ids and raw values are under each row's Details.</p>
</footer>
</main>`;
  return page(
    `${entry.summary.title}: example threat model`,
    `Example data. ${exampleNotice(report)}`,
    bundle.nav_html,
    reportCss,
    body.value,
  );
}

export function renderModelIndex(
  bundle: ModelPageBundle,
  reportCss: string,
  paths: ReadonlyMap<string, string> = modelPagePaths(bundle.models.map((entry) => entry.summary)),
): string {
  const items = bundle.models.map(({ summary }) => {
    const threats = summary.counts.threats ?? 0;
    const pathCount = summary.counts.attack_paths ?? 0;
    // The same reader text as the report header (every product): modelling notes stay out.
    const description = readableDescription(summary.description).summary?.replace(/\n/g, " ") ?? null;
    return html`<li>
<p class="kind">${summary.kind_label}</p>
<h2><a href="${paths.get(summary.file) ?? modelPagePath(summary)}">${summary.title}</a></h2>
${description ? html`<p>${description}</p>` : ""}
<p class="meta">${threats} ${threats === 1 ? "threat" : "threats"}, ${summary.reviewed_threats} with an accepted human review · ${pathCount} attack ${pathCount === 1 ? "path" : "paths"}</p>
</li>`;
  });
  const problems = bundle.problems.length > 0
    ? html`<div class="problems"><p>These model files could not be loaded:</p><ul>${bundle.problems.map((problem) => html`<li>${problem.file}: ${problem.error}</li>`)}</ul></div>`
    : "";
  const body = html`<main class="model-page model-index">
<h1>Example threat models</h1>
<p class="lead">Worked examples of what tmodel produces: each page is a threat-model report, in the order a TARA reads it, with every threat and attack path marked with its review status.</p>
<div class="model-report"><p class="example-banner" role="note"><strong>Example data.</strong> ${MODEL_LIST_NOTICE}</p></div>
<ul class="model-list">${join(items)}</ul>
${problems}
</main>`;
  return page("Example threat models", `Example data. ${MODEL_LIST_NOTICE}`, bundle.nav_html, reportCss, body.value);
}

function page(title: string, description: string, navHtml: string, reportCss: string, body: string): string {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
${html`<title>${title} · tmodel</title>
<meta name="description" content="${description}">`.value}
<style>${PAGE_CSS}
${reportCss}
${SITE_REPORT_CSS}</style>
</head>
<body>
${navHtml}
${body}
</body>
</html>
`;
}
