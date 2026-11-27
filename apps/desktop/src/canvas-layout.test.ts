import { beforeAll, describe, expect, it } from "vitest";
import { bindInfoDisclosures } from "./library-presentation";
import attackPatternFixture from "./fixtures/attack-pattern-table.json";
import weaknessFixture from "./fixtures/weakness-table.json";
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
 * can quietly resize the other (#247, and the #255 review). Also measure the
 * Library toolbar and the space the CWE attribution disclosure returns to the table,
 * and lay the CAPEC table (#236) out with its attribution showing, as it does with rows.
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
  library: {
    selectorRightInset: number;
    selectorCenterOffset: number;
    selectorOverlapsTabs: boolean;
    collapsedFooterHeight: number;
    collapsedTableHeight: number;
    popovers: {
      nextControlId: string;
      focusStaysInside: boolean;
      closesOnOutsideFocus: boolean;
      escapeRestoresFocus: boolean;
      outsideEscapePreservesFocus: boolean;
      outsideClickCloses: boolean;
    }[];
    shortRequirements: {
      coverageOpen: boolean;
      scrolls: boolean;
      footerReachable: boolean;
    };
    expandedTableHeight: number;
    tables: {
      prefix: string;
      fullTableHeight: number;
      scrolls: boolean;
      footerOffsets: number[];
      rightAligned: boolean;
      clearAddsHeight: boolean;
    }[];
  };
}

const WIDTHS = [700, 1000, 1280, 1600];
const SHORT_VIEWPORTS = [[721, 468], [800, 500]] as const;
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

/** Runs in the page and measures each workspace independently. */
const PROBE = `window.addEventListener("load", () => {
  document.getElementById("workspace").hidden = false;
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
  const library = () => {
    const bindDisclosures = ${bindInfoDisclosures.toString()};
    bindDisclosures(document);
    if (innerHeight < 600) document.getElementById("preview-banner").hidden = false;
    const panel = document.getElementById("library-view-panel");
    document.getElementById("paths-view-panel").hidden = true;
    panel.hidden = false;
    panel.querySelector('[data-library-view="records"]').hidden = true;
    panel.querySelector('[data-library-view="weaknesses"]').hidden = false;
    const table = document.getElementById("weakness-table-region");
    table.hidden = false;
    const selector = document.getElementById("library-view-select");
    selector.hidden = false;
    const position = selector.getBoundingClientRect();
    const tabs = document.querySelector(".view-tabs").getBoundingClientRect();
    const nav = document.querySelector(".app-navigation").getBoundingClientRect();
    document.getElementById("weakness-attribution-notice").textContent = ${JSON.stringify(weaknessFixture.catalog.notice)};
    document.getElementById("weakness-attribution-license").textContent = ${JSON.stringify(weaknessFixture.catalog.license)};
    const footer = document.querySelector(".weakness-attribution");
    const collapsedFooterHeight = footer.offsetHeight;
    const collapsedTableHeight = table.offsetHeight;
    footer.open = true;
    const expandedTableHeight = table.offsetHeight;
    footer.open = false;

    const popovers = [];
    const exercisePopover = (disclosure, nextControl) => {
      const summary = disclosure.querySelector("summary");
      const contents = disclosure.querySelector(".info-panel");
      summary.focus();
      summary.click();
      contents.focus();
      const focusStaysInside = disclosure.open && document.activeElement === contents;
      nextControl.focus();
      const closesOnOutsideFocus = !disclosure.open && document.activeElement === nextControl;
      disclosure.open = true;
      contents.focus();
      const escape = new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true });
      contents.dispatchEvent(escape);
      const escapeRestoresFocus = !disclosure.open && document.activeElement === summary && escape.defaultPrevented;
      nextControl.focus();
      // Pointer activation can leave focus on an outside control.
      summary.click();
      const outsideEscape = new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true });
      nextControl.dispatchEvent(outsideEscape);
      const outsideEscapePreservesFocus =
        !disclosure.open && document.activeElement === nextControl && !outsideEscape.defaultPrevented;
      summary.click();
      nextControl.click();
      return {
        nextControlId: nextControl.id, focusStaysInside, closesOnOutsideFocus, escapeRestoresFocus,
        outsideEscapePreservesFocus, outsideClickCloses: !disclosure.open,
      };
    };

    const modelInfo = document.getElementById("model-picker-info");
    modelInfo.hidden = false;
    popovers.push(exercisePopover(modelInfo, document.getElementById("report-tab")));

    document.getElementById("attack-pattern-attribution").hidden = false;
    document.getElementById("attack-pattern-attribution-notice").textContent = ${JSON.stringify(attackPatternFixture.catalog.notice)};
    document.getElementById("attack-pattern-attribution-license").textContent = ${JSON.stringify(attackPatternFixture.catalog.license)};
    const tables = [
      ["records", "library"], ["weaknesses", "weakness"], ["attack-patterns", "attack-pattern"], ["requirements", "requirements"],
    ].map(([view, prefix]) => {
      for (const section of panel.querySelectorAll(".library-subview")) section.hidden = section.dataset.libraryView !== view;
      const main = document.querySelector("#" + prefix + "-workspace .library-main");
      popovers.push(exercisePopover(main.querySelector(".info-disclosure"), document.getElementById(prefix + "-search")));
      const footer = main.querySelector(".library-pagination");
      const count = document.getElementById(prefix + "-page-status");
      const next = document.getElementById(prefix + "-page-next");
      const previous = document.getElementById(prefix + "-page-previous");
      const region = document.getElementById(prefix + "-table-region");
      const empty = document.getElementById(prefix + "-empty");
      const body = document.getElementById(prefix + "-table-body");
      document.getElementById(prefix + "-request-status").textContent = "";
      if (prefix === "requirements") {
        document.getElementById("requirements-coverage-content").innerHTML = "<p>Recorded evidence</p>".repeat(20);
      }
      const controls = main.querySelector(".library-controls");
      const before = controls.offsetHeight;
      document.getElementById(prefix + "-clear-filters").hidden = false;
      const clearAddsHeight = controls.offsetHeight > before;
      const trailingAttribution = main.querySelector(".weakness-attribution, .attack-pattern-attribution");
      const attributionSpace = trailingAttribution
        ? trailingAttribution.offsetHeight + parseFloat(getComputedStyle(trailingAttribution).marginTop)
        : 0;
      const footerOffsets = [0, 3, 50].map((rows) => {
        region.hidden = !rows;
        empty.hidden = !!rows;
        next.hidden = previous.hidden = rows !== 50;
        count.textContent = rows === 50 ? "1–50 of 80" : rows ? "1–3 of 3" : "0 of 0";
        body.innerHTML = "<tr><td>Example record</td></tr>".repeat(rows);
        const contentBottom = main.getBoundingClientRect().bottom - parseFloat(getComputedStyle(main).paddingBottom);
        return Math.round(contentBottom - attributionSpace - footer.getBoundingClientRect().bottom);
      });
      return {
        prefix,
        fullTableHeight: region.clientHeight,
        scrolls: region.scrollHeight > region.clientHeight,
        footerOffsets,
        rightAligned: Math.abs(next.getBoundingClientRect().right - footer.getBoundingClientRect().right) < 1,
        clearAddsHeight,
      };
    });
    const requirementsMain = panel.querySelector(".requirements-main");
    const requirementsFooter = requirementsMain.querySelector(".library-pagination");
    requirementsMain.scrollTop = requirementsMain.scrollHeight;
    const shortRequirements = {
      coverageOpen: document.getElementById("requirements-coverage").open,
      scrolls: requirementsMain.scrollTop > 0,
      footerReachable: requirementsFooter.getBoundingClientRect().bottom <= requirementsMain.getBoundingClientRect().bottom,
    };
    return {
      popovers,
      shortRequirements,
      selectorRightInset: Math.round(nav.right - position.right),
      selectorCenterOffset: Math.round((position.top + position.bottom - tabs.top - tabs.bottom) / 2),
      selectorOverlapsTabs: position.left < tabs.right,
      collapsedFooterHeight,
      collapsedTableHeight,
      expandedTableHeight,
      tables,
    };
  };
  const layout = {
    width: innerWidth,
    height: innerHeight,
    explore: size("graph-view-panel", "graph-canvas"),
    paths: size("paths-view-panel", "path-view-canvas"),
    library: library(),
  };
  document.body.setAttribute("data-layout", JSON.stringify(layout));
});`;

function measure(): Map<number, Layout> {
  if (CHROME === undefined) throw new Error("No Chrome found for the layout test; set CHROME_PATH");
  const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  const body = /<body[^>]*>([\s\S]*)<\/body>/u.exec(html)?.[1];
  if (body === undefined) throw new Error("index.html has no <body>");
  // The app's own script loads from <head>, so the page below runs only the probe.
  if (/<script/iu.test(body)) throw new Error("index.html's <body> has a script; this test expects none");
  const css = ["./theme.css", "./styles.css", "./report.css", "./welcome.css"]
    .map((file) => readFileSync(new URL(file, import.meta.url), "utf8"))
    .join("\n");
  const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><style>${css}</style></head>`
    + `<body>${body}<script>${PROBE}</script></body></html>`;
  const dir = mkdtempSync(join(tmpdir(), "tmodel-layout-"));
  try {
    const file = join(dir, "page.html");
    writeFileSync(file, page);
    const layouts = new Map<number, Layout>();
    const viewports = [...WIDTHS.map((width) => [width, 900] as const), ...SHORT_VIEWPORTS];
    for (const [width, height] of viewports) {
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
        `--window-size=${width},${height}`,
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

describe.skipIf(!MEASURE)("application layout in a real browser", () => {
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

  it.each(WIDTHS)("aligns the Library selector to the right of the tabs at %ipx", (width) => {
    const { library } = layouts.get(width) as Layout;
    expect(library.selectorRightInset).toBe(0);
    expect(Math.abs(library.selectorCenterOffset)).toBeLessThanOrEqual(1);
    expect(library.selectorOverlapsTabs).toBe(false);
  });

  it.each(WIDTHS.filter((width) => width > 720))("gives the CWE table the space saved by the collapsed footer at %ipx", (width) => {
    const { library } = layouts.get(width) as Layout;
    expect(library.collapsedFooterHeight).toBeLessThanOrEqual(24);
    expect(library.collapsedTableHeight).toBeGreaterThan(library.expandedTableHeight);
  });

  it.each(WIDTHS)("anchors the four Library record tables to a right-aligned footer at %ipx", (width) => {
    const { library } = layouts.get(width) as Layout;
    expect(library.tables.map((table) => table.prefix)).toEqual(["library", "weakness", "attack-pattern", "requirements"]);
    for (const table of library.tables) {
      expect(table.footerOffsets, table.prefix).toEqual([0, 0, 0]);
      expect(table.rightAligned, table.prefix).toBe(true);
      expect(table.clearAddsHeight, table.prefix).toBe(false);
      expect(table.scrolls, table.prefix).toBe(true);
      expect(table.fullTableHeight, table.prefix).toBeGreaterThan(100);
    }
  });

  it("dismisses source and model popovers as focus travels and returns focus on Escape", () => {
    for (const { library, width, height } of layouts.values()) {
      expect(library.popovers).toHaveLength(5);
      for (const popover of library.popovers) {
        expect(popover, `${popover.nextControlId} at ${width} × ${height}`).toMatchObject({
          focusStaysInside: true,
          closesOnOutsideFocus: true,
          escapeRestoresFocus: true,
          outsideEscapePreservesFocus: true,
          outsideClickCloses: true,
        });
      }
    }
  });

  it.each(SHORT_VIEWPORTS)("keeps expanded coverage and a scrollable requirements table at %i × %i", (width, height) => {
    const layout = layouts.get(width) as Layout;
    expect(layout.width).toBe(width);
    // Chrome headless uses an outer window size. The viewport excludes its chrome.
    expect(layout.height).toBeLessThanOrEqual(height);
    const requirements = layout.library.tables.find((table) => table.prefix === "requirements");
    expect(requirements?.fullTableHeight).toBeGreaterThanOrEqual(178);
    expect(layout.library.shortRequirements).toEqual({
      coverageOpen: true, scrolls: true, footerReachable: true,
    });
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
