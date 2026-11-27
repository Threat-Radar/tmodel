import { describe, expect, it, vi } from "vitest";
import contract from "../../../engine/examples/human-review/contract.json";
import { FakeDocument, target, type FakeElement } from "./fake-dom.test-support";
import { buildModelReport } from "./model-report";
import { formatVersionDate, ProjectChrome, renderVersionHistory } from "./project-view";
import { riskSummaryOf, type ProjectVersions } from "./project-workspace";
import { parseRevisionViews } from "./review-contract";

const views = parseRevisionViews(contract.save.response, { model_id: "local:one" });
const summary = riskSummaryOf(views.risk);
const versions: ProjectVersions = {
  project: { id: "p", name: "Brake ECU review", kind: "project", editable: true },
  versions: [
    { id: "v001", number: 1, description: "Starting model", date: "2026-11-20T10:00:00Z", riskSummary: null, current: false },
    { id: "v002", number: 2, description: null, date: null, riskSummary: summary, current: false },
    { id: "v003", number: 3, description: "Ratings after review", date: "not a date", riskSummary: null, current: false },
    { id: "v004", number: 4, description: "Accepted the CAN route", date: "2026-11-27T09:30:00Z", riskSummary: summary, current: true },
  ],
};

function chrome() {
  const doc = new FakeDocument();
  const workspace = doc.createElement("main");
  const panels = [doc.createElement("section"), doc.createElement("section")];
  const actions = { selectVersion: vi.fn(), navigate: vi.fn(), close: vi.fn(), retry: vi.fn(), startProject: vi.fn() };
  const view = new ProjectChrome(workspace.as(), panels.map((panel) => panel.as()), actions, doc.as());
  return { view, workspace, panels, actions, bar: view.bar as unknown as FakeElement, nav: view.navigation as unknown as FakeElement };
}

describe("project view (the team's design)", () => {
  it("names the project and offers every version, newest first, with the current one marked", () => {
    const { view, bar, actions } = chrome();
    view.enter();
    view.render({ versions, shown: versions.versions[3], riskSummaries: new Map(), unsaved: 0, saving: false });
    expect(bar.text).toContain("Brake ECU review");
    const select = bar.querySelector("#project-version-select")!;
    expect(select.innerHTML.match(/>[^<]+<\/option>/g)).toEqual([
      ">Version 4 (Current)</option>", ">Version 3</option>", ">Version 2</option>", ">Version 1</option>",
    ]);
    expect(select.value).toBe("v004");
    select.value = "v002";
    select.dispatch("change");
    expect(actions.selectVersion).toHaveBeenCalledWith("v002");
    expect(bar.text).toContain("Current version");
    expect(bar.text).toContain("Close project");
    expect(bar.querySelector(".project-start")?.hidden).toBe(true);
  });

  it("names a read-only file as a file, and offers to start a project from it", () => {
    const { view, bar, actions } = chrome();
    const file: ProjectVersions = {
      project: { id: "file:1", name: "imported-model.yaml", kind: "file", editable: false },
      versions: [{ id: "sha256:abc", number: null, description: "Opened read-only from imported-model.yaml", date: null, riskSummary: null, current: true }],
    };
    view.render({ versions: file, shown: file.versions[0], riskSummaries: new Map(), unsaved: 0, saving: false });
    expect(bar.text).toContain("Threat model file");
    expect(bar.text).toContain("Read-only file");
    expect(bar.text).toContain("Close file");
    expect(bar.querySelector("#project-version-select")!.innerHTML).toContain(">Opened file</option>");
    const start = bar.querySelector(".project-start")!;
    expect(start.hidden).toBe(false);
    start.click();
    expect(actions.startProject).toHaveBeenCalledOnce();
  });

  it("marks an older version read-only, and disables the selector while a version loads or a save runs", () => {
    const { view, bar } = chrome();
    view.render({ versions, shown: versions.versions[1], riskSummaries: new Map(), unsaved: 2, saving: false });
    expect(bar.text).toContain("Older version: read-only");
    expect(bar.text).toContain("2 unsaved changes");
    view.render({ versions, shown: versions.versions[1], loading: "v004", riskSummaries: new Map(), unsaved: 0, saving: false });
    expect(bar.querySelector("#project-version-select")!.disabled).toBe(true);
    expect(bar.text).toContain("Loading Version 4…");
    expect(bar.getAttribute("aria-busy")).toBe("true");
  });

  it("lists Version, Description, Risk summary and Date, and opens any version from the table", () => {
    const html = renderVersionHistory(versions, "v002", new Map([["v001", summary]]));
    expect(html.match(/<th scope="col">([^<]+)<\/th>/g)).toEqual([
      '<th scope="col">Version</th>', '<th scope="col">Description</th>', '<th scope="col">Risk summary</th>', '<th scope="col">Date</th>',
    ]);
    expect(html.indexOf("Version 4")).toBeLessThan(html.indexOf("Version 1"));
    expect(html).toContain('<span class="version-chip is-current">Current</span>');
    expect(html).toContain('data-project-version="v002" aria-current="true"');
    expect(html).toContain("No description recorded");
    // A summary from the metadata, or from views this session read, in the engine's categories.
    expect(html).toContain("Safety 5 · Financial 4 · Operational 3 · Privacy 4 (highest of 1 assessment)");
    expect(html).toContain("<td>Not recorded</td>");
    expect(html).toContain('<time datetime="2026-11-27T09:30:00Z">');
    expect(html).toContain("<td>not a date</td>");
    const { view, bar, actions } = chrome();
    view.render({ versions, shown: versions.versions[3], riskSummaries: new Map(), unsaved: 0, saving: false });
    const body = bar.all().find((element) => element.classList.contains("version-history-body"))!;
    body.dispatch("click", target({ "data-project-version": "v001" }));
    expect(actions.selectVersion).toHaveBeenCalledWith("v001");
  });

  it("formats a recorded date and keeps an unreadable one as written", () => {
    expect(formatVersionDate(null)).toEqual({ text: "Not recorded", datetime: null });
    expect(formatVersionDate("soon")).toEqual({ text: "soon", datetime: null });
    expect(formatVersionDate("2026-11-27T09:30:00Z").datetime).toBe("2026-11-27T09:30:00Z");
  });

  it("navigates with Model Report, Attack Paths, Graph, Risk Score and Review & Edit", () => {
    const { view, nav, actions, panels } = chrome();
    const buttons = nav.all().filter((element) => element.tagName === "button");
    expect(buttons.map((button) => button.textContent)).toEqual(["Model Report", "Attack Paths", "Graph", "Risk Score", "Review & Edit"]);
    buttons[3].click();
    expect(actions.navigate).toHaveBeenCalledWith("risk");
    view.setPage("risk");
    expect(buttons[3].getAttribute("aria-current")).toBe("page");
    expect(view.riskPanel.hidden).toBe(false);
    expect(panels.every((panel) => panel.hidden)).toBe(true);
    view.setPage("report");
    expect(buttons[3].getAttribute("aria-current")).toBeNull();
    expect(view.riskPanel.hidden).toBe(true);
  });

  it("shows the version's own calculated risk on Risk Score", () => {
    const { view } = chrome();
    view.renderRisk(views, buildModelReport(views.reportInput), versions.versions[3], summary);
    const panel = view.riskPanel as unknown as FakeElement;
    expect(panel.text).toContain("Version 4 (Current): Safety 5 · Financial 4 · Operational 3 · Privacy 4 (highest of 1 assessment).");
    expect(panel.text).toContain("Calculated risk vector");
  });

  it("enters and leaves the project layout", () => {
    const { view, workspace } = chrome();
    view.enter();
    expect(workspace.classList.contains("is-project")).toBe(true);
    view.exit();
    expect(workspace.classList.contains("is-project")).toBe(false);
    expect(view.bar.hidden).toBe(true);
    expect(view.navigation.hidden).toBe(true);
  });
});
