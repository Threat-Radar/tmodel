import { describe, expect, it, vi } from "vitest";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import { FakeDocument, type FakeElement } from "./fake-dom.test-support";
import { DesktopProjects, PROJECT_NOTICE, ProjectAttackPathView, ProjectReportView, projectBackend } from "./desktop-projects";
import { renderModelReport } from "./report-render";
import { buildModelReport } from "./model-report";
import type { ModelReportInput } from "./model-types";
import { NO_HOST_REASON } from "./project-host";
import { EngineProjectWorkspace } from "./project-workspace";
import type { PathViewElements } from "./path-view";
// @ts-expect-error The app deliberately does not install @types/node; Vitest runs this in Node.
import { readFileSync } from "node:fs";

const MAIN: string = readFileSync(new URL("./main.ts", import.meta.url), "utf8");

function pathView(doc: FakeDocument) {
  const select = Object.assign(doc.createElement("select"), { replaceChildren: () => {} });
  const core = {
    batch: (callback: () => void) => callback(), elements: () => ({ remove: () => {}, length: 0 }), add: () => {},
    resize: () => {}, fit: () => {}, zoom: () => 1, center: () => {}, on: () => {}, style: () => {}, destroy: () => {},
  };
  const elements = { select, banner: doc.createElement("p"), canvas: {}, summary: doc.createElement("aside") };
  return new ProjectAttackPathView(elements as unknown as PathViewElements, doc.as(), (() => core) as never);
}

describe("desktop projects wiring (#290)", () => {
  it("uses #288's routes, and offers no projects until the desktop host gives its session", async () => {
    const backend = projectBackend(new URLSearchParams());
    await backend.ready;
    expect(backend.mock).toBe(false);
    expect(backend.workspace).toBeInstanceOf(EngineProjectWorkspace);
    expect(backend.workspace.status()).toEqual({ available: false, reason: NO_HOST_REASON });
    expect(backend.session.current()).toBeUndefined();
  });

  it("uses the shared-example mock only when a development server asks for it", () => {
    // Vitest runs with import.meta.env.DEV true, like `npm run dev`; every build has it false.
    expect(import.meta.env.DEV).toBe(true);
    const backend = projectBackend(new URLSearchParams("projectSource=mock"));
    expect(backend.mock).toBe(true);
    expect(backend.workspace.status()).toEqual({ available: true });
    expect(backend.session.current()?.token).toBe("development-mock-session-not-a-credential");
  });

  it("tells the review panel which path the attack-path view shows", () => {
    const doc = new FakeDocument();
    const view = pathView(doc);
    const shown = vi.fn();
    view.onPathShown = shown;
    const report = buildModelReport(mvp02 as unknown as ModelReportInput);
    view.setReport(report);
    view.showPath(report.attackPaths[1].id);
    expect(shown.mock.calls.map(([id]) => id)).toEqual([report.attackPaths[0].id, report.attackPaths[1].id]);
  });

  it("adds its chrome to the workspace and its review panel under the path summary", () => {
    const doc = new FakeDocument();
    const workspace = doc.createElement("main");
    doc.body.append(workspace);
    const header = doc.createElement("header");
    const side = doc.createElement("section");
    const summary = doc.createElement("aside");
    workspace.append(header, side);
    side.append(summary);
    const projects = new DesktopProjects({
      documentRoot: doc.as(),
      backend: projectBackend(new URLSearchParams()),
      workspace: workspace.as(),
      header: header.as(),
      appPanels: [],
      pathSummary: summary.as(),
      pathView: pathView(doc),
      navigation: { activate: vi.fn(), currentView: undefined },
      showModel: vi.fn(),
      reopenExample: vi.fn(),
    });
    expect(workspace.children.map((child) => child.tagName)).toEqual(["header", "section", "nav", "section", "section", "p"]);
    const column = side.children[0];
    expect(column.className).toBe("path-side");
    expect(column.children.map((child) => child.tagName)).toEqual(["aside", "section"]);
    expect(doc.head.children[0].tagName).toBe("style");
    expect(projects.projectsAvailable()).toBe(false);
    // Read-only by default: the project bar, navigation and review panel all start hidden.
    expect((projects.chrome.bar as unknown as FakeElement).hidden).toBe(true);
    expect((projects.workbench.element as unknown as FakeElement).hidden).toBe(true);
  });

  it("says what a project version is in the report header, and leaves an example's header alone", () => {
    const input = mvp02 as unknown as ModelReportInput;
    const project = buildModelReport({ ...input, model: { ...input.model, kind: "project", kind_label: "Project version" } });
    // The shared renderer's header lines that the project report relabels.
    const markup = renderModelReport(project, { interactive: true });
    expect(markup).toContain('<p class="eyebrow">Example threat model · Project version</p>');
    expect(markup).toContain('<p class="example-banner" role="note"><strong>Example data.</strong>');
    const eyebrow = { textContent: "" };
    const banner = { textContent: "" };
    const content = {
      innerHTML: "",
      addEventListener: () => {},
      querySelector: (selector: string) => selector === ".report-header .eyebrow" ? eyebrow
        : selector === ".report-header .example-banner" ? banner : null,
    };
    const view = new ProjectReportView({
      status: { textContent: "", hidden: false, className: "" } as unknown as HTMLElement,
      content: content as unknown as HTMLElement,
      retry: { hidden: true, addEventListener: () => {} } as unknown as HTMLButtonElement,
    }, { openPath: () => {}, retry: () => {} });
    view.show(buildModelReport(input));
    expect(eyebrow.textContent).toBe("");
    view.show(project);
    expect(eyebrow.textContent).toBe("Threat model · Project version");
    expect(banner.textContent).toBe(PROJECT_NOTICE);
  });

  it("keeps every main.ts change for projects outside the browser preview build", () => {
    // render_app.py --check proves the Pages bundle is unchanged; this names the guards.
    expect(MAIN).toContain("const pathView = new (preview ? AttackPathView : ProjectAttackPathView)(");
    expect(MAIN).toContain("const reportView = new (preview ? ModelReportView : ProjectReportView)(");
    expect(MAIN).toContain("source: preview ? exampleSource : (model) => projects?.source(model) ?? exampleSource(model),");
    expect(MAIN).toContain("const projectApi = preview ? undefined : projects?.revisionApi(file);");
    expect(MAIN).toContain("if (!preview) projects?.viewShown(view);");
    expect(MAIN).toMatch(/if \(!preview\) \{\n\s+\/\/ #290: projects, Review & Edit/);
    const uses = MAIN.split("\n").filter((text) => !text.trim().startsWith("//") && /(^|[^\w-])projects\??\.[a-z]/i.test(text));
    expect(uses.length).toBeGreaterThan(10);
    for (const line of uses) {
      expect(line, line).toMatch(/preview|projects\?\.|projects\.(installHome|onEnterWorkspace)|=> projects/);
    }
  });
});
