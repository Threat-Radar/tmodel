import { describe, expect, it } from "vitest";
// @ts-expect-error Vitest runs in Node; the app does not install @types/node.
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

const chrome = [process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
].find((path) => typeof path === "string" && path !== "" && existsSync(path));

function luminance(color: string): number {
  const channels = color.match(/[\d.]+/g)?.slice(0, 3).map(Number);
  if (!channels || channels.length !== 3) throw new Error(`Not an RGB color: ${color}`);
  const linear = channels.map((value) => {
    const channel = value / 255;
    return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

describe.skipIf(!chrome && !process.env.CI)("risk button contrast in a real browser", () => {
  it.each([false, true])("keeps normal text readable with dark mode = %s", (dark) => {
    if (!chrome) throw new Error("Set CHROME_PATH to run the contrast check");
    const dir = mkdtempSync(join(tmpdir(), "tmodel-risk-contrast-"));
    try {
      const css = readFileSync(new URL("./report.css", import.meta.url), "utf8");
      const page = join(dir, "page.html");
      writeFileSync(page, `<!doctype html><style>${css}</style><body>
        <div class="model-report"><div class="risk-calculator"><button>Calculate risk</button></div></div>
        <script>const style=getComputedStyle(document.querySelector('button'));
        document.body.setAttribute('data-colors',JSON.stringify({dark:matchMedia('(prefers-color-scheme: dark)').matches,
        foreground:style.color,background:style.backgroundColor}));</script></body>`);
      const run = spawnSync(chrome, ["--headless=new", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", ...(dark ? ["--force-dark-mode"] : []),
        ...(process.platform === "linux" ? ["--no-sandbox"] : []),
        `--user-data-dir=${join(dir, "profile")}`, "--dump-dom", pathToFileURL(page).href,
      ], { encoding: "utf8", timeout: 30_000 });
      const found = /data-colors="([^"]*)"/u.exec(String(run.stdout ?? ""));
      if (!found) throw new Error(`Chrome did not return colors: ${String(run.stderr ?? "").slice(0, 300)}`);
      const colors = JSON.parse(found[1].replace(/&quot;/gu, '"').replace(/&amp;/gu, "&"));
      expect(colors.dark).toBe(dark);
      const light = [luminance(colors.foreground), luminance(colors.background)].sort((a, b) => a - b);
      expect((light[1] + 0.05) / (light[0] + 0.05)).toBeGreaterThanOrEqual(4.5);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  }, 40_000);
});
