// #290's review flow, end to end through the real controller, workbench and
// client, against the shared-example backend (project-mock.ts): open a project,
// select a path, review, rate, save, see every view refresh from the saved
// version, and each failure keep the unsaved input.
import { describe, expect, it, vi } from "vitest";
import contract from "../../../engine/examples/human-review/contract.json";
import type { AppView } from "./app-navigation";
import { FakeDocument, target, tick, type FakeElement } from "./fake-dom.test-support";
import type { ModelSummary } from "./model-types";
import { ProjectController } from "./project-controller";
import { MOCK_ENGINE_BASE, MOCK_SESSION, MockProjectBackend } from "./project-mock";
import { ProjectChrome } from "./project-view";
import { NO_REVIEW_SESSION, ReviewApiClient, type ReviewSessionSource } from "./review-client";
import { ReviewWorkbench } from "./review-workbench";
import { projectVersionLabel } from "./revision-api";

/** The mock host's first project, as #288 names projects: project: and 32 hex digits. */
const ID = `project:${"1".padStart(32, "0")}`;
const label = (version: string) => projectVersionLabel(ID, version);

const EXAMPLE: ModelSummary = {
  id: "mvp-01", file: "mvp-01.yaml", title: "Example model", description: null,
  kind: "mvp", kind_label: "Example", counts: {}, reviewed_threats: 0,
};

function harness({ session = MOCK_SESSION, backend = new MockProjectBackend(), fetchImpl }: {
  session?: ReviewSessionSource;
  backend?: MockProjectBackend;
  fetchImpl?: typeof fetch;
} = {}) {
  const doc = new FakeDocument();
  const workspace = doc.createElement("main");
  const panels = ["report", "paths", "library", "graph"].map(() => doc.createElement("section"));
  const client = new ReviewApiClient(session, MOCK_ENGINE_BASE, fetchImpl ?? backend.fetch);
  const shown: ModelSummary[] = [];
  const activated: AppView[] = [];
  let controller!: ProjectController;
  const chrome = new ProjectChrome(workspace.as(), panels.map((panel) => panel.as()), {
    selectVersion: (id) => void controller.viewVersion(id),
    navigate: (page) => controller.navigate(page),
    close: () => controller.close(),
    retry: () => controller.retry(),
    startProject: () => controller.startProjectFromFile(),
  }, doc.as());
  const reopenExample = vi.fn();
  controller = new ProjectController(backend.workspace, client, chrome, {
    showModel: async (model) => { shown.push(model); },
    activate: (view) => activated.push(view),
    currentView: () => activated[activated.length - 1],
    reopenExample,
    enterWorkspace: vi.fn(),
  });
  const workbench = new ReviewWorkbench(client, controller, doc.as());
  controller.attach(workbench);
  const panel = workbench.element as unknown as FakeElement;
  const region = (className: string) => panel.children.find((child) => child.classList.contains(className))!;
  return {
    doc, backend, controller, workbench, chrome, shown, activated, reopenExample,
    body: () => region("review-body").innerHTML,
    changes: () => region("review-changes").innerHTML,
    alert: () => region("review-alert"),
    status: () => region("review-status").textContent,
    save: () => region("review-actions").children[0],
    bar: () => (chrome.bar as unknown as FakeElement).text,
  };
}

type Harness = ReturnType<typeof harness>;

async function openForReview(h: Harness) {
  expect(await h.controller.createProject({ kind: "example", file: EXAMPLE.file, title: EXAMPLE.title })).toBe(true);
  h.workbench.pathChanged("path:a");
  h.controller.navigate("review");
  await tick();
}

function review(h: Harness) {
  h.workbench.handleChange(target({ "data-review-field": "verdict", "data-target": "assertion:path" }, { value: "accepted", checked: true }));
  h.workbench.handleInput(target({ "data-review-field": "rationale", "data-target": "assertion:path" }, { value: "Test-only human input supplied by the test client." }));
  h.workbench.handleInput(target({ "data-review-field": "annotation", "data-target": "assertion:path" }, { value: "Synthetic contract example" }));
}

function rate(h: Harness) {
  h.workbench.handleChange(target({ "data-review-field": "feasibility", "data-target": "path:a" }, { value: "high" }));
  h.workbench.handleChange(target({ "data-review-field": "impact", "data-target": "risk:r", "data-category": "privacy" }, { value: "major" }));
}

const saves = (h: Harness) => h.backend.requests.filter((request) => request.path === "/reviews/changes");
const reviewCalls = (h: Harness) => h.backend.requests.filter((request) => request.path.startsWith("/reviews/"));

describe("Review & Edit (#290)", () => {
  it("opens a project at its current version and shows it in every view through one model", async () => {
    const h = harness();
    await h.controller.createProject({ kind: "example", file: EXAMPLE.file, title: EXAMPLE.title });
    // The host step starts the project from the example's file; the app then reads it by id.
    expect(h.backend.steps).toEqual([{ kind: "create-project", from: { source_file: "mvp-01.yaml" } }]);
    expect(h.backend.requests.map((request) => request.path)).toEqual(["/workspace/models", "/workspace/versions", "/reviews/refresh"]);
    expect(reviewCalls(h)[0].body).toEqual({ model_id: ID, revision: "v001", matrix: "annex-h-table-h8" });
    expect(h.shown.map((model) => [model.file, model.title])).toEqual([[label("v001"), "mvp-01 (mock project)"]]);
    expect(h.bar()).toContain("Version 1 (Current)");
    expect(h.bar()).toContain("Current version");
  });

  it("reviews, annotates and rates a route, then saves everything in one request", async () => {
    const h = harness();
    await openForReview(h);
    const form = h.body();
    expect(form).toContain('data-review-field="verdict"');
    expect(form).toContain("Rationale (required)");
    expect(form).toContain('id="review-p0-feasibility"');
    expect(form).toContain('data-category="privacy"');
    expect(form).toContain("Route feasibility");
    expect(form).toContain("applies to this route only");
    expect(form).toContain("Scenario impact");
    expect(form).toContain("applies to every route of this threat");
    review(h);
    rate(h);
    expect(h.changes()).toContain("3 unsaved changes");
    expect(h.save().getAttribute("aria-disabled")).toBe("false");
    expect(h.bar()).toContain("3 unsaved changes");
    await h.workbench.save();
    await tick();
    expect(saves(h)).toHaveLength(1);
    expect(saves(h)[0].body).toEqual({ ...contract.save.request, model_id: ID, expected_revision: "v001" });
  });

  it("refreshes every view from the saved version and shows the recalculated risk", async () => {
    const h = harness();
    await openForReview(h);
    review(h);
    rate(h);
    await h.workbench.save();
    await tick();
    expect(h.shown.map((model) => model.file)).toEqual([label("v001"), label("v002")]);
    expect(h.status()).toBe("Saved as Version 2. The report, attack paths, graph and risk now show Version 2. Recalculated risk for this route: Safety 5 (was 3) · Financial 4 (was 2) · Operational 3 (was 2) · Privacy 4 (was 1).");
    // The context reloads at the saved version: the review is now the reviewer's own, to correct.
    const context = h.backend.requests.filter((request) => request.path === "/reviews/context").pop();
    expect(context?.body).toMatchObject({ model_id: ID, revision: "v002" });
    expect(h.body()).toContain("Correct your review");
    expect(h.body()).toContain("(you)");
    expect(h.workbench.unsavedCount).toBe(0);
    expect(h.bar()).toContain("Version 2 (Current)");
    expect(h.bar()).toContain("Safety 5 · Financial 4 · Operational 3 · Privacy 4");
    // The project's views read the saved version in memory, never the approved-vector routes.
    const risk = await h.controller.calculateRisk(label("v002"), "annex-h-table-h8");
    expect(risk?.assessments[0].derived_risk.safety).toBe(5);
  });

  it("checks the input before sending: a decision needs a verdict and a rationale", async () => {
    const h = harness();
    await openForReview(h);
    h.workbench.handleChange(target({ "data-review-field": "verdict", "data-target": "assertion:path" }, { value: "rejected", checked: true }));
    await h.workbench.save();
    expect(saves(h)).toHaveLength(0);
    expect(h.alert().innerHTML).toContain("Explain the decision: a rationale is required.");
    expect(h.alert().innerHTML).toContain('data-review-action="focus-field" data-field="review-a0-rationale"');
    expect(h.doc.activeElement).toBe(h.alert());
    expect(h.body()).toContain('aria-invalid="true"');
    expect(h.workbench.unsavedCount).toBe(1);
  });

  it.each([
    ["validation_error", 422, "The engine refused the save: Explain the review decision."],
    ["permission_denied", 403, "This session cannot make this change: This session cannot submit reviews."],
    ["save_failure", 503, "The model could not be saved. Retry your changes. Nothing was saved."],
    ["workspace_failure", 503, "Saving is not available"],
  ] as const)("keeps the unsaved input when a save fails with %s", async (code, status, text) => {
    const h = harness();
    await openForReview(h);
    review(h);
    rate(h);
    h.backend.failWith(code, status);
    await h.workbench.save();
    expect(h.alert().innerHTML).toContain(text);
    expect(h.alert().innerHTML).toContain("Your changes are kept.");
    expect(h.workbench.unsavedCount).toBe(3);
    expect(h.shown).toHaveLength(1);
    expect(h.body()).toContain("Test-only human input supplied by the test client.");
    // Permission and workspace failures stop saving until the review reloads; the others allow a retry.
    const retryable = code === "validation_error" || code === "save_failure";
    expect(h.save().getAttribute("aria-disabled")).toBe(String(!retryable));
    if (retryable) {
      await h.workbench.save();
      await tick();
      expect(h.shown.map((model) => model.file)).toContain(label("v002"));
    }
  });

  it("refuses to overwrite a newer version, keeps the input, and saves on top of it once loaded", async () => {
    const h = harness();
    await openForReview(h);
    review(h);
    rate(h);
    h.backend.addVersionElsewhere(ID);
    await h.workbench.save();
    expect(h.alert().innerHTML).toContain("so nothing was saved and no version was overwritten");
    expect(h.alert().innerHTML).toContain('data-review-action="load-version" data-version="v002"');
    expect(h.workbench.unsavedCount).toBe(3);
    h.workbench.handleClick(target({ "data-review-action": "load-version", "data-version": "v002" }));
    await tick();
    await tick();
    expect(h.shown.map((model) => model.file).pop()).toBe(label("v002"));
    expect(h.body()).toContain("These unsaved changes were made on Version 1. This is Version 2");
    expect(h.workbench.unsavedCount).toBe(3);
    await h.workbench.save();
    expect(saves(h).pop()?.body).toMatchObject({ expected_revision: "v002" });
    await tick();
    expect(h.bar()).toContain("Version 3 (Current)");
  });

  it("keeps the input when the engine cannot be reached or its answer cannot be read", async () => {
    const backend = new MockProjectBackend();
    let mode: "ok" | "network" | "garbage" = "ok";
    const fetchImpl = (async (input: RequestInfo | URL, init?: RequestInit) => {
      if (new URL(String(input)).pathname === "/reviews/changes") {
        if (mode === "network") throw new TypeError("Failed to fetch");
        if (mode === "garbage") return new Response(JSON.stringify({ model_id: ID }), { status: 200 });
      }
      return backend.fetch(input, init);
    }) as typeof fetch;
    const h = harness({ backend, fetchImpl });
    await openForReview(h);
    review(h);
    mode = "network";
    await h.workbench.save();
    expect(h.alert().innerHTML).toContain("Could not reach the local engine.");
    mode = "garbage";
    await h.workbench.save();
    expect(h.alert().innerHTML).toContain("cannot tell whether a new version was saved");
    expect(h.alert().innerHTML).toContain('data-review-action="refresh-versions"');
    expect(h.workbench.unsavedCount).toBe(1);
  });

  it("sends one save for a double click and takes no input while saving", async () => {
    let release!: () => void;
    const backend = new MockProjectBackend();
    const fetchImpl = (async (input: RequestInfo | URL, init?: RequestInit) => {
      if (new URL(String(input)).pathname === "/reviews/changes") await new Promise<void>((resolve) => { release = resolve; });
      return backend.fetch(input, init);
    }) as typeof fetch;
    const h = harness({ backend, fetchImpl });
    await openForReview(h);
    rate(h);
    const first = h.workbench.save();
    const second = h.workbench.save();
    expect(h.workbench.isSaving).toBe(true);
    expect(h.body()).toContain(" disabled");
    h.workbench.handleChange(target({ "data-review-field": "impact", "data-target": "risk:r", "data-category": "safety" }, { value: "major" }));
    // Neither a version change nor closing the project interrupts a save.
    expect(await h.controller.viewVersion("v001")).toBe(false);
    expect((h.chrome.announcer as unknown as FakeElement).textContent).toBe("Wait for the save to finish before changing the version.");
    h.controller.close();
    expect(h.controller.isOpen).toBe(true);
    release();
    await Promise.all([first, second]);
    await tick();
    expect(saves(h)).toHaveLength(1);
    expect(saves(h)[0].body).not.toHaveProperty("impacts.0.values.safety");
    expect(h.workbench.unsavedCount).toBe(0);
  });

  it("drops a review context that arrives after another version was chosen", async () => {
    const backend = new MockProjectBackend();
    const gates: (() => void)[] = [];
    const fetchImpl = (async (input: RequestInfo | URL, init?: RequestInit) => {
      if (new URL(String(input)).pathname === "/reviews/context") await new Promise<void>((resolve) => gates.push(resolve));
      return backend.fetch(input, init);
    }) as typeof fetch;
    const h = harness({ backend, fetchImpl });
    await h.controller.createProject({ kind: "example", file: EXAMPLE.file, title: EXAMPLE.title });
    backend.addVersionElsewhere(ID);
    await h.controller.refreshVersions();
    h.workbench.pathChanged("path:a");
    h.controller.navigate("review");
    expect(h.body()).toContain("Loading the review");
    await h.controller.viewVersion("v002");
    gates.forEach((open) => open());
    await tick();
    gates.forEach((open) => open());
    await tick();
    const contexts = backend.requests.filter((request) => request.path === "/reviews/context").map((request) => request.body);
    expect(contexts).toEqual([expect.objectContaining({ revision: "v001" }), expect.objectContaining({ revision: "v002" })]);
    expect(h.body()).toContain("Correct your review");
  });
});

describe("review controls stay out of read-only views", () => {
  it("shows no review controls on an older version", async () => {
    const h = harness();
    await openForReview(h);
    rate(h);
    await h.workbench.save();
    await tick();
    await h.controller.viewVersion("v001");
    await tick();
    expect(h.bar()).toContain("Older version: read-only");
    expect(h.body()).toContain("You are viewing Version 1, an older version");
    expect(h.body()).toContain('data-review-action="load-version" data-version="v002"');
    expect(h.body()).not.toContain("data-review-field");
    expect((h.workbench.element as unknown as FakeElement).children.find((child) => child.classList.contains("review-actions"))?.hidden).toBe(true);
  });

  it("shows no review controls when the engine has no review workspace", async () => {
    const h = harness();
    await h.controller.createProject({ kind: "example", file: EXAMPLE.file, title: EXAMPLE.title });
    h.backend.failWith("workspace_failure", 503);
    h.workbench.pathChanged("path:a");
    h.controller.navigate("review");
    await tick();
    expect(h.body()).toContain("Reviewing is not available");
    expect(h.body()).not.toContain("data-review-field");
  });

  it("shows no review controls when the session may only read", async () => {
    const backend = new MockProjectBackend();
    const fetchImpl = (async (input: RequestInfo | URL, init?: RequestInit) => {
      const response = await backend.fetch(input, init);
      if (new URL(String(input)).pathname !== "/reviews/context") return response;
      const body = await response.json();
      body.permitted_actions = { submit_review: false, save_feasibility: false, save_impacts: false, correct_own_review: false, accept_proposal: false };
      return new Response(JSON.stringify(body), { status: 200 });
    }) as typeof fetch;
    const h = harness({ backend, fetchImpl });
    await openForReview(h);
    expect(h.body()).toContain("This session can read this version but cannot review or rate it.");
    expect(h.body()).not.toContain("data-review-field");
    expect(h.body()).toContain("Feasibility of");
  });

  it("offers nothing without a verified session, even for an example", () => {
    const h = harness({ session: NO_REVIEW_SESSION });
    expect(h.controller.projectsAvailable()).toBe(false);
    h.controller.exampleShown(EXAMPLE);
    expect(h.workbench.element.hidden).toBe(true);
    return expect(h.controller.openProject()).rejects.toThrow("no verified review session");
  });

  it("offers to start a project from an example only when projects are available", async () => {
    const h = harness();
    h.controller.exampleShown(EXAMPLE);
    expect(h.workbench.element.hidden).toBe(false);
    expect(h.body()).toContain('data-review-action="start-project"');
    expect(h.body()).not.toContain("data-review-field");
    h.workbench.handleClick(target({ "data-review-action": "start-project" }));
    await tick();
    await tick();
    expect(h.shown.map((model) => model.title)).toEqual(["mvp-01 (mock project)"]);
  });

  it("keeps Attack Paths read-only and points to Review & Edit", async () => {
    const h = harness();
    await h.controller.createProject({ kind: "example", file: EXAMPLE.file, title: EXAMPLE.title });
    h.workbench.pathChanged("path:a");
    h.controller.navigate("paths");
    expect(h.body()).toContain('data-review-action="review"');
    expect(h.body()).not.toContain("data-review-field");
    expect(h.backend.requests.filter((request) => request.path === "/reviews/context")).toHaveLength(0);
    expect(h.activated.pop()).toBe("paths");
  });

  it("opens a saved threat model file read-only, and starts a project from it", async () => {
    const h = harness();
    expect(await h.controller.openThreatModel()).toBe(true);
    expect(h.backend.steps).toEqual([{ kind: "open-file" }]);
    expect(h.bar()).toContain("Threat model file");
    expect(h.bar()).toContain("Opened file");
    expect(h.bar()).toContain("Read-only file");
    h.workbench.pathChanged("path:a");
    h.controller.navigate("review");
    await tick();
    expect(h.body()).toContain("This threat model file is open read-only.");
    expect(h.body()).not.toContain("data-review-field");
    h.controller.startProjectFromFile();
    await tick();
    await tick();
    expect(h.backend.steps[1]).toEqual({ kind: "create-project", from: { model_id: `file:${"1".padStart(32, "0")}` } });
    expect(h.bar()).toContain("Version 1 (Current)");
    await tick();
    expect(h.body()).toContain('data-review-field="verdict"');
  });

  it("opens nothing when the user cancels the host's picker", async () => {
    const h = harness({ backend: new MockProjectBackend({ cancelPickers: true }) });
    expect(await h.controller.openProject()).toBe(false);
    expect(await h.controller.openThreatModel()).toBe(false);
    expect(h.controller.isOpen).toBe(false);
    expect(h.backend.requests).toEqual([]);
  });

  it("keeps unsaved input when the project closes, and offers it again on reopening", async () => {
    const h = harness();
    await openForReview(h);
    rate(h);
    h.controller.close();
    expect(h.controller.isOpen).toBe(false);
    expect((h.chrome.announcer as unknown as FakeElement).textContent).toContain("2 unsaved changes are kept until you quit tmodel");
    expect(h.reopenExample).toHaveBeenCalled();
    expect(await h.controller.openProject()).toBe(true);
    h.controller.navigate("review");
    await tick();
    expect(h.workbench.unsavedCount).toBe(2);
  });
});
