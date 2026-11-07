// Writes the static example-model pages (#208) with the app's own report renderer.
//
//   node --experimental-strip-types apps/desktop/scripts/render-model-pages.mjs BUNDLE.json OUT_DIR
//
// Needs Node 22.6 or newer (type stripping).
// BUNDLE.json comes from docs/publishing/render_models.py, which runs the engine.
// Normally run through that script (or bin/publish-site), not by hand.
import { mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { renderModelPages } from "../src/model-pages.ts";
import { defaultViewLeaks } from "../src/report-render.ts";

const [bundlePath, outDir] = process.argv.slice(2);
if (!bundlePath || !outDir) {
  console.error("usage: render-model-pages.mjs BUNDLE.json OUT_DIR");
  process.exit(2);
}

const here = dirname(fileURLToPath(import.meta.url));
const bundle = JSON.parse(readFileSync(bundlePath, "utf8"));
const css = readFileSync(join(here, "..", "src", "report.css"), "utf8");
const pages = renderModelPages(bundle, css);

// #208: no id, CURIE, CPE, purl or schema name in a page's default view (Details
// toggles closed). Checked before anything is written, so a bad page never lands.
const leaks = pages.flatMap((page) => defaultViewLeaks(page.content).map((leak) => `${page.path}: ${leak}`));
if (leaks.length > 0) {
  console.error(`render-model-pages: technical identifiers in the default view:\n  ${leaks.join("\n  ")}`);
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
// This builder owns every page in OUT_DIR: drop one whose model is gone.
const written = new Set(pages.map((page) => page.path));
for (const name of readdirSync(outDir)) {
  if (name.endsWith(".html") && !written.has(name)) rmSync(join(outDir, name));
}
for (const page of pages) writeFileSync(join(outDir, page.path), page.content.replace(/[\t ]+$/gm, ''));
console.log(`render-model-pages: ${pages.length - 1} model pages and an index in ${outDir}`);
