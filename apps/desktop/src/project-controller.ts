// #290: one open project at a time. Opening a project, or choosing a version,
// reads that exact version's views with #289's refreshModel, and the existing
// views (report, attack paths, Explore graph, requirements, risk) all switch to
// it together through ModelSession, so none can show another version's data.
// A save hands back the new version's views, which replace every view the same
// way; the workspace (#288) supplies the version list.

import type { AppView } from "./app-navigation";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { buildModelReport, type ModelReport } from "./model-report";
import type { ModelDataSource } from "./model-session";
import type { ModelSummary } from "./model-types";
import type { ProjectChrome, ProjectPage } from "./project-view";
import {
  checkProjectVersions,
  currentVersion,
  findVersion,
  riskSummaryOf,
  versionLabel,
  type ProjectSource,
  type ProjectVersion,
  type ProjectVersions,
  type ProjectWorkspaceProvider,
  type VersionRiskSummary,
} from "./project-workspace";
import { LatestRequestGuard } from "./request-guard";
import { isAbort, type ReviewApiClient } from "./review-client";
import { REVIEW_MATRIX, type RevisionViews } from "./review-contract";
import { CLOSED_VERSION_API, isProjectVersionLabel, projectVersionLabel, RevisionApi, type VersionApi } from "./revision-api";
import type { RiskCalculation } from "./risk-calculation";
import type { ReviewTarget, ReviewWorkbench, ReviewWorkbenchHost } from "./review-workbench";

/** The ModelSummary kind of a project version (desktop-projects.ts relabels its report). */
export const PROJECT_KIND = "project";

export interface ProjectAppHooks {
  /** Shows a model in every view (ModelSession.open). */
  showModel(model: ModelSummary): Promise<void>;
  activate(view: AppView): void;
  currentView(): AppView | undefined;
  /** Back to the example models after a project closes. */
  reopenExample(): void;
  /** Leaves the home screen, if it is still shown. */
  enterWorkspace(): void;
}

interface ShownVersion {
  version: ProjectVersion;
  views: RevisionViews;
  label: string;
  api: RevisionApi;
  report: ModelReport;
}

export class ProjectController implements ReviewWorkbenchHost {
  private versions?: ProjectVersions;
  private shown?: ShownVersion;
  private loading?: string;
  private error?: string;
  private notice?: string;
  private retryVersion?: string;
  private shownExample?: ModelSummary;
  private readonly loads = new LatestRequestGuard();
  private readonly riskSummaries = new Map<string, Map<string, VersionRiskSummary>>();
  private workbench?: ReviewWorkbench;
  private busy = false;

  constructor(
    private readonly workspace: ProjectWorkspaceProvider,
    private readonly client: ReviewApiClient,
    private readonly chrome: ProjectChrome,
    private readonly hooks: ProjectAppHooks,
  ) {}

  attach(workbench: ReviewWorkbench): void {
    this.workbench = workbench;
  }

  /** Projects need both the workspace (#288) and a verified review session (#289). */
  projectsAvailable(): boolean {
    return this.workspace.status().available && this.client.hasSession;
  }

  unavailableReason(): string {
    const status = this.workspace.status();
    if (!status.available) return status.reason;
    return this.client.hasSession ? "" : "This app has no verified review session, so projects stay closed.";
  }

  get isOpen(): boolean {
    return this.versions !== undefined;
  }

  get openProjectVersions(): ProjectVersions | undefined {
    return this.versions;
  }

  // --- opening -------------------------------------------------------------

  createProject(source: ProjectSource): Promise<boolean> {
    return this.fromWorkspace(() => this.workspace.createProject(source), "create the project");
  }

  openProject(): Promise<boolean> {
    return this.fromWorkspace(() => this.workspace.openProject(), "open the project");
  }

  /** A saved YAML file, opened read-only; a project can be started from it. */
  openThreatModel(): Promise<boolean> {
    return this.fromWorkspace(() => this.workspace.openThreatModel(), "open the threat model file");
  }

  /** Starts a project from the read-only file being shown. */
  startProjectFromFile(): void {
    const versions = this.versions;
    if (!versions || versions.project.kind !== "file") return;
    this.chrome.announce(`Starting a project from ${versions.project.name}…`);
    void this.createProject({ kind: "file", modelId: versions.project.id }).then(
      (opened) => { if (!opened) this.chrome.announce("No project was started."); },
      (error: unknown) => this.chrome.announce(message(error)),
    );
  }

  private async fromWorkspace(run: () => Promise<ProjectVersions | null>, what: string): Promise<boolean> {
    if (!this.projectsAvailable()) throw new Error(this.unavailableReason());
    if (this.busy || this.workbench?.isSaving) throw new Error("Wait for the current project action to finish.");
    this.busy = true;
    try {
      const versions = await run();
      if (!versions) return false;
      return await this.open(versions);
    } catch (error) {
      throw new Error(`Could not ${what}: ${message(error)}`);
    } finally {
      this.busy = false;
    }
  }

  /** Shows a project at its current version (or `versionId`). */
  async open(versions: ProjectVersions, versionId?: string): Promise<boolean> {
    const checked = checkProjectVersions(versions);
    const wanted = versionId ?? currentVersion(checked).id;
    if (this.versions?.project.id !== checked.project.id) this.shown = undefined;
    this.versions = checked;
    this.error = undefined;
    this.notice = undefined;
    this.chrome.enter();
    this.hooks.enterWorkspace();
    this.navigate(this.chrome.currentPage);
    return this.load(wanted);
  }

  /** Version selector and history table. Never while a save is in flight. */
  viewVersion(versionId: string): Promise<boolean> {
    if (this.workbench?.isSaving) {
      this.renderChrome();
      this.chrome.announce("Wait for the save to finish before changing the version.");
      return Promise.resolve(false);
    }
    if (versionId === this.shown?.version.id && !this.loading) return Promise.resolve(true);
    return this.load(versionId);
  }

  retry(): void {
    if (this.retryVersion) void this.load(this.retryVersion);
  }

  close(): void {
    if (!this.versions) return;
    if (this.workbench?.isSaving) {
      this.chrome.announce("Wait for the save to finish before closing the project.");
      return;
    }
    const unsaved = this.workbench?.unsavedCount ?? 0;
    const name = this.versions.project.name;
    this.loads.cancel();
    this.versions = undefined;
    this.shown = undefined;
    this.loading = undefined;
    this.chrome.exit();
    this.hooks.activate(this.hooks.currentView() ?? "report");
    this.workbench?.setMode("view");
    this.workbench?.targetChanged();
    this.hooks.reopenExample();
    this.chrome.announce(unsaved
      ? `Closed ${name}. Its ${unsaved} unsaved ${unsaved === 1 ? "change is" : "changes are"} kept until you quit tmodel; reopen the project to save them.`
      : `Closed ${name}.`);
  }

  private async load(versionId: string): Promise<boolean> {
    const versions = this.versions;
    const version = findVersion(versions, versionId);
    if (!versions || !version) {
      this.error = `This project has no version ${versionId}.`;
      this.renderChrome();
      return false;
    }
    const request = this.loads.begin();
    this.loading = versionId;
    this.error = undefined;
    this.retryVersion = undefined;
    this.renderChrome();
    try {
      const views = await this.client.refreshModel(
        { model_id: versions.project.id, revision: versionId, matrix: REVIEW_MATRIX },
        request.signal,
      );
      if (!this.loads.isCurrent(request) || this.versions !== versions) return false;
      this.loads.complete(request);
      await this.show(version, views);
      return true;
    } catch (error) {
      if (isAbort(error) || !this.loads.isCurrent(request)) return false;
      this.loads.complete(request);
      this.loading = undefined;
      this.error = `Could not open ${versionLabel(version)}: ${message(error)}${this.shown ? ` ${versionLabel(this.shown.version)} is still shown.` : ""}`;
      this.retryVersion = versionId;
      this.renderChrome();
      return false;
    }
  }

  /** Every view switches to `views`, which all belong to `version`. */
  private async show(version: ProjectVersion, views: RevisionViews): Promise<void> {
    const versions = this.versions;
    if (!versions || views.model_id !== versions.project.id || views.revision !== version.id) {
      throw new Error("The engine returned another project's or version's views.");
    }
    const label = projectVersionLabel(versions.project.id, version.id);
    const model = views.reportInput.model;
    const summary: ModelSummary = {
      id: versions.project.id,
      file: label,
      title: versions.project.name,
      description: model.description,
      kind: PROJECT_KIND,
      kind_label: versions.project.kind === "file" ? "Threat model file, read-only" : "Project version",
      counts: model.counts,
      reviewed_threats: model.reviewed_threats,
    };
    const report = buildModelReport({ model: summary, graph: views.graph, attackPaths: views.attackPaths });
    this.shown = { version, views, label, api: new RevisionApi(label, views), report };
    this.summaries(versions.project.id).set(version.id, riskSummaryOf(views.risk));
    this.loading = undefined;
    this.error = undefined;
    await this.hooks.showModel(summary);
    if (this.shown?.label !== label) return;
    this.renderChrome();
    this.chrome.renderRisk(views, report, version, this.summaries(versions.project.id).get(version.id)!);
    this.workbench?.targetChanged();
  }

  // --- the review workbench's host --------------------------------------------

  target(): ReviewTarget | undefined {
    const { versions, shown } = this;
    if (!versions || !shown) return undefined;
    return {
      projectId: versions.project.id,
      projectName: versions.project.name,
      kind: versions.project.kind,
      versions,
      version: shown.version,
      editable: versions.project.editable && shown.version.current,
      views: shown.views,
      report: shown.report,
    };
  }

  exampleShown(model: ModelSummary): void {
    this.shownExample = model;
    if (!this.versions) this.workbench?.targetChanged();
  }

  example(): { title: string } | undefined {
    return this.versions ? undefined : this.shownExample;
  }

  async saved(views: RevisionViews): Promise<void> {
    const versions = this.versions;
    if (!versions || views.model_id !== versions.project.id) return;
    let next: ProjectVersions;
    this.notice = undefined;
    try {
      next = checkProjectVersions(await this.workspace.listVersions(versions.project.id));
      if (!findVersion(next, views.revision)) throw new Error("the saved version is missing from the list");
    } catch {
      next = withSavedVersion(versions, views.revision);
      this.notice = "The version list could not be refreshed, so the new version is shown without its description or date.";
    }
    if (this.versions !== versions) return;
    this.versions = next;
    // A version load that started before the save is older than it: drop it.
    this.loads.cancel();
    await this.show(findVersion(next, views.revision)!, views);
  }

  async loadVersion(versionId: string): Promise<boolean> {
    if (!findVersion(this.versions, versionId)) await this.refreshVersions();
    return this.load(versionId);
  }

  async refreshVersions(): Promise<void> {
    const versions = this.versions;
    if (!versions) return;
    try {
      const next = checkProjectVersions(await this.workspace.listVersions(versions.project.id));
      if (this.versions !== versions) return;
      this.versions = next;
      const shown = this.shown && findVersion(next, this.shown.version.id);
      if (this.shown && shown) this.shown = { ...this.shown, version: shown };
      this.notice = `The version list was reloaded. ${versionLabel(currentVersion(next))} is the current version.`;
      this.error = undefined;
      this.renderChrome();
      this.workbench?.targetChanged();
    } catch (error) {
      this.error = `Could not reload the version list: ${message(error)}`;
      this.renderChrome();
    }
  }

  startProjectFromExample(): void {
    const example = this.shownExample;
    if (!example || this.versions) return;
    this.chrome.announce(`Starting a project from ${example.title}…`);
    void this.createProject({ kind: "example", file: example.file, title: example.title }).then(
      (opened) => { if (!opened) this.chrome.announce("No project was started."); },
      (error: unknown) => this.chrome.announce(message(error)),
    );
  }

  showReview(): void {
    this.navigate("review");
  }

  unsavedChanged(): void {
    if (this.versions) this.renderChrome();
  }

  // --- navigation -----------------------------------------------------------------

  navigate(page: ProjectPage): void {
    this.chrome.setPage(page);
    if (page === "risk") {
      this.chrome.focusRisk();
      return;
    }
    this.workbench?.setMode(page === "review" ? "review" : "view");
    this.hooks.activate(page === "review" ? "paths" : page);
    if (page === "review") this.workbench?.focus();
  }

  /** The app activated a view on its own (such as "Open in path view"). */
  viewShown(view: AppView): void {
    if (!this.versions) return;
    const page: ProjectPage = view === "paths" && this.chrome.currentPage === "review" ? "review"
      : view === "graph" ? "graph" : view === "paths" ? "paths" : "report";
    if (page === this.chrome.currentPage) return;
    this.chrome.setPage(page);
    this.workbench?.setMode(page === "review" ? "review" : "view");
  }

  // --- ModelSession and provider integration ---------------------------------------

  isProjectFile(file: string | undefined): boolean {
    return isProjectVersionLabel(file);
  }

  /** The shown version's in-memory views; another project label gets nothing, not the engine. */
  source(model: ModelSummary): ModelDataSource | undefined {
    if (!isProjectVersionLabel(model.file)) return undefined;
    const shown = this.shown;
    if (!shown || shown.label !== model.file) {
      const closed = () => Promise.reject(new Error("This project version is no longer open."));
      return { getModelGraph: closed, getAttackPathResults: closed };
    }
    return {
      getModelGraph: () => Promise.resolve(shown.views.graph),
      getAttackPathResults: () => Promise.resolve({ responses: [...shown.views.attackPaths], failures: [] }),
    };
  }

  revisionApi(file: string | undefined): VersionApi | undefined {
    if (!isProjectVersionLabel(file)) return undefined;
    const shown = this.shown;
    return shown && shown.label === file ? shown.api : CLOSED_VERSION_API;
  }

  calculateRisk(file: string, matrix: string): Promise<RiskCalculation> | undefined {
    const api = this.revisionApi(file);
    return api ? new EngineGraphDataProvider(file, api.engineBase, api.fetch).getRiskCalculation(matrix) : undefined;
  }

  private summaries(projectId: string): Map<string, VersionRiskSummary> {
    let summaries = this.riskSummaries.get(projectId);
    if (!summaries) {
      summaries = new Map();
      this.riskSummaries.set(projectId, summaries);
    }
    return summaries;
  }

  private renderChrome(): void {
    const versions = this.versions;
    if (!versions) return;
    this.chrome.render({
      versions,
      shown: this.shown?.version,
      loading: this.loading,
      error: this.error,
      notice: this.notice,
      riskSummaries: this.summaries(versions.project.id),
      unsaved: this.workbench?.unsavedCount ?? 0,
      saving: this.workbench?.isSaving ?? false,
    });
  }
}

/** The version list after a save when the workspace cannot list it: the saved version is current. */
export function withSavedVersion(versions: ProjectVersions, revision: string): ProjectVersions {
  if (findVersion(versions, revision)) {
    return { ...versions, versions: versions.versions.map((version) => ({ ...version, current: version.id === revision })) };
  }
  return {
    ...versions,
    versions: [
      ...versions.versions.map((version) => ({ ...version, current: false })),
      { id: revision, number: null, description: null, date: null, riskSummary: null, current: true },
    ],
  };
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
