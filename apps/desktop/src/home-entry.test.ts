import { describe, expect, it, vi } from "vitest";
import { FakeDocument, target, type FakeElement } from "./fake-dom.test-support";
import { HomeEntryPoints, homeOptions, renderHomeOptions } from "./home-entry";

const available = { projects: true, reason: "" };
const unavailable = { projects: false, reason: "Local projects are not connected in this build yet." };

describe("home page entry points (the team's design)", () => {
  it("offers the three options, each with its line of explanation", () => {
    const html = renderHomeOptions(homeOptions({ importProduct: vi.fn(), openThreatModel: vi.fn(), openProject: vi.fn() }, available));
    expect([...html.matchAll(/class="welcome-option-title">([^<]+)</g)].map((match) => match[1]))
      .toEqual(["Import New Product", "Open Existing Threat Model", "Open Existing Project"]);
    expect(html).toContain("Create a threat model from an SBOM and a vulnerability scan.");
    expect(html).toContain("Open a previously saved YAML file.");
    expect(html).toContain("Continue a project and its version history.");
    expect(html).toContain('aria-labelledby="home-project-title" aria-describedby="home-project-help"');
    expect(html).not.toContain("aria-disabled");
  });

  it("says honestly what is not available instead of pretending to work", () => {
    const html = renderHomeOptions(homeOptions({ openThreatModel: vi.fn(), openProject: vi.fn() }, unavailable));
    expect(html.match(/aria-disabled="true"/g)).toHaveLength(3);
    expect(html).toContain("Coming soon to the app. For now, import from a terminal with tmodel import-sbom.");
    expect(html).toContain("Local projects are not connected in this build yet.");
  });

  it("runs an available option and reports what happened", async () => {
    const doc = new FakeDocument();
    const openProject = vi.fn(async () => true);
    const openThreatModel = vi.fn(async () => { throw new Error("Could not open the project: no such folder"); });
    const importProduct = vi.fn();
    const home = new HomeEntryPoints({ importProduct, openThreatModel, openProject }, () => available, doc.as());
    await home.handleClick(target({ "data-home-action": "project" }));
    expect(openProject).toHaveBeenCalledOnce();
    expect(home.statusText).toBe("");
    await home.handleClick(target({ "data-home-action": "threat-model" }));
    expect(home.statusText).toBe("Could not open the project: no such folder");
    const opener = target({ "data-home-action": "import" });
    await home.handleClick(opener);
    expect(importProduct).toHaveBeenCalledWith(opener);
    const status = (home.element as unknown as FakeElement).children.find((child) => child.getAttribute("role") === "status");
    expect(status?.getAttribute("aria-live")).toBe("polite");
  });

  it("does nothing but explain when an option is unavailable, and runs one action at a time", async () => {
    const doc = new FakeDocument();
    let finish!: (value: boolean) => void;
    const openProject = vi.fn(() => new Promise<boolean>((resolve) => { finish = resolve; }));
    const home = new HomeEntryPoints({ openThreatModel: vi.fn(), openProject }, () => available, doc.as());
    const first = home.handleClick(target({ "data-home-action": "project" }));
    await home.handleClick(target({ "data-home-action": "project" }));
    expect(openProject).toHaveBeenCalledOnce();
    finish(false);
    await first;
    expect(home.statusText).toBe("Nothing was opened.");
    const closed = new HomeEntryPoints({ openThreatModel: vi.fn(), openProject }, () => unavailable, doc.as());
    await closed.handleClick(target({ "data-home-action": "project" }));
    expect(openProject).toHaveBeenCalledOnce();
    expect(closed.statusText).toBe("Open Existing Project: Local projects are not connected in this build yet.");
  });
});
