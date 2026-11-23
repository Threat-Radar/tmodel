import { beforeAll, describe, expect, it } from "vitest";
// @ts-expect-error The app deliberately does not install @types/node; Vitest runs this in Node.
import { spawnSync } from "node:child_process";
// @ts-expect-error See above.
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
// @ts-expect-error See above.
import { tmpdir } from "node:os";
// @ts-expect-error See above.
import { join } from "node:path";
// @ts-expect-error See above.
import process from "node:process";
// @ts-expect-error See above.
import { pathToFileURL } from "node:url";

/**
 * Real layout, not CSS text: the app's own page and stylesheets, measured in
 * headless Chrome at widths on both sides of the 720, 1100 and 1500 px
 * breakpoints. The two canvases share `.graph-canvas`, so a rule meant for one
 * can quietly resize the other (#247, and the #255 review).
 */

interface CanvasSize {
  height: number;
  /** The height its parent has left once the parent's other children are laid out. */
  leftover: number;
}

interface Layout {
  width: number;
  height: number;
  explore: CanvasSize;
  paths: CanvasSize;
}

const WIDTHS = [700, 1000, 1280, 1600];
/** A usable drawing area; the Explore canvas measured 363 to 381 px in an 813 px viewport. */
const MIN_DRAWING_HEIGHT = 200;

const CHROME = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
].find((path) => typeof path === "string" && path !== "" && existsSync(path)) as string | undefined;

// GitHub's runners include Chrome, so CI always measures. A machine without it skips
// (set CHROME_PATH to use another Chrome or Chromium).
const MEASURE = CHROME !== undefined || Boolean(process.env.CI);

/** Runs in the page: show one view at a time and report its canvas's height. */
const PROBE = `(() => {
  const size = (panelId, canvasId) => {
    for (const panel of document.querySelectorAll(".view-panel")) panel.hidden = panel.id !== panelId;
    const canvas = document.getElementById(canvasId);
    const parent = canvas.parentElement;
    const style = getComputedStyle(parent);
    const used = [...parent.children].filter((child) => child !== canvas).reduce((sum, child) => {
      const margins = getComputedStyle(child);
      return sum + child.getBoundingClientRect().height + parseFloat(margins.marginTop) + parseFloat(margins.marginBottom);
    }, 0);
    const content = parent.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
    return { height: Math.round(canvas.getBoundingClientRect().height), leftover: Math.round(content - used) };
  };
  const layout = {
    width: innerWidth,
    height: innerHeight,
    explore: size("graph-view-panel", "graph-canvas"),
    paths: size("paths-view-panel", "path-view-canvas"),
  };
  document.body.setAttribute("data-layout", JSON.stringify(layout));
})();`;

function measure(): Map<number, Layout> {
  if (CHROME === undefined) throw new Error("No Chrome found for the layout test; set CHROME_PATH");
  const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  const body = /<body[^>]*>([\s\S]*)<\/body>/u.exec(html)?.[1];
  if (body === undefined) throw new Error("index.html has no <body>");
  const css = ["./styles.css", "./report.css"]
    .map((file) => readFileSync(new URL(file, import.meta.url), "utf8"))
    .join("\n");
  const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><style>${css}</style></head>`
    + `<body>${body.replace(/<script\b[\s\S]*?<\/script>/gu, "")}<script>${PROBE}</script></body></html>`;
  const dir = mkdtempSync(join(tmpdir(), "tmodel-layout-"));
  try {
    const file = join(dir, "page.html");
    writeFileSync(file, page);
    const layouts = new Map<number, Layout>();
    for (const width of WIDTHS) {
      const run = spawnSync(CHROME, [
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        // Linux runners can't start Chrome's sandbox; the page is this repo's own files, offline.
        ...(process.platform === "linux" ? ["--no-sandbox"] : []),
        `--user-data-dir=${join(dir, "profile")}`,
        `--window-size=${width},900`,
        "--dump-dom",
        pathToFileURL(file).href,
      ], { encoding: "utf8", timeout: 60_000 });
      const found = /data-layout="([^"]*)"/u.exec(String(run.stdout ?? ""));
      if (!found) throw new Error(`Chrome gave no layout at ${width}px: ${String(run.stderr ?? "").slice(0, 300)}`);
      layouts.set(width, JSON.parse(found[1].replace(/&quot;/gu, "\"").replace(/&amp;/gu, "&")) as Layout);
    }
    return layouts;
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

describe.skipIf(!MEASURE)("canvas heights in a real browser (#247)", () => {
  let layouts = new Map<number, Layout>();
  beforeAll(() => {
    layouts = measure();
  }, 120_000);

  it.each(WIDTHS)("lays the page out at the asked width (%ipx)", (width) => {
    expect(layouts.get(width)?.width).toBe(width);
  });

  it.each(WIDTHS)("gives the Explore canvas the panel's leftover height at %ipx", (width) => {
    const { explore } = layouts.get(width) as Layout;
    expect(Math.abs(explore.height - explore.leftover), JSON.stringify(explore)).toBeLessThanOrEqual(1);
    // At 720px and below, .graph-canvas has a 430px floor.
    expect(explore.height).toBeGreaterThanOrEqual(width <= 720 ? 430 : MIN_DRAWING_HEIGHT);
  });

  it.each(WIDTHS)("keeps the Attack paths canvas at its own height at %ipx", (width) => {
    const { height, paths } = layouts.get(width) as Layout;
    if (width >= 1500) {
      // Wide screens give the canvas the column beside the summary (flex: 1).
      expect(Math.abs(paths.height - paths.leftover), JSON.stringify(paths)).toBeLessThanOrEqual(1);
      expect(paths.height).toBeGreaterThanOrEqual(MIN_DRAWING_HEIGHT);
    } else {
      // .path-view-canvas: height: max(380px, calc(100vh - 290px)).
      expect(Math.abs(paths.height - Math.max(380, height - 290)), JSON.stringify(paths)).toBeLessThanOrEqual(1);
    }
  });
});
