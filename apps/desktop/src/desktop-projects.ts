// #290: the desktop app's projects, review and home entry points, wired into
// the existing shell. main.ts calls this only outside the browser preview
// build, so none of it (markup, styles or requests) reaches GitHub Pages.
//
// What is available follows what the engine and host provide: without the
// host's session (project-host.ts) the app stays exactly as read-only as
// before, apart from the home page saying so. A Vite development server can use
// the shared-example mock (?projectSource=mock) to try the screens.

import type { AppNavigation, AppView } from "./app-navigation";
import { HomeEntryPoints, type HomeActions } from "./home-entry";
import type { ModelListResponse, ModelSummary } from "./model-types";
import { AttackPathView } from "./path-view";
import { ModelReportView, type ReportViewElements } from "./report-view";
import { PROJECT_KIND, ProjectController } from "./project-controller";
import { connectProjectHost, ProjectHostHolder } from "./project-host";
import { MOCK_ENGINE_BASE, MOCK_SESSION, MockProjectBackend } from "./project-mock";
import { ProjectChrome } from "./project-view";
import { EngineProjectWorkspace, WorkspaceClient, type ProjectSource, type ProjectWorkspaceProvider } from "./project-workspace";
import { ReviewApiClient, type ReviewSessionSource } from "./review-client";
import { ReviewWorkbench } from "./review-workbench";
import type { ModelReport } from "./model-report";
import projectStyles from "./project-screens.css?inline";

/**
 * The model report, saying what a project version is. The shared renderer
 * calls every model an example (true of the bundled models and the browser
 * preview); a project starts from a model the user chose, so its header says
 * so instead. Only the header's two lines change.
 */
export class ProjectReportView extends ModelReportView {
  private readonly content: HTMLElement;

  constructor(elements: ReportViewElements, callbacks: ConstructorParameters<typeof ModelReportView>[1]) {
    super(elements, callbacks);
    this.content = elements.content;
  }

  override show(report: ModelReport): void {
    super.show(report);
    if (report.model.kind !== PROJECT_KIND) return;
    const root = this.content as HTMLElement & ParentNode;
    const eyebrow = root.querySelector?.(".report-header .eyebrow");
    if (eyebrow) eyebrow.textContent = `Threat model · ${report.model.kindLabel}`;
    const banner = root.querySelector?.(".report-header .example-banner");
    if (banner) banner.textContent = PROJECT_NOTICE;
  }
}

export const PROJECT_NOTICE = "Project version. A project starts from a model you chose and keeps every saved version. "
  + "AI-proposed threats and attack paths stay hypotheses until a human reviewer accepts them, and a review saved "
  + "here is recorded in the project, not the sponsor's acceptance of a proposal.";

/** The attack-path view, telling the review panel which path it shows. */
export class ProjectAttackPathView extends AttackPathView {
  onPathShown?: (pathId: string | undefined) => void;

  override setReport(report: ModelReport | undefined, message?: string): void {
    super.setReport(report, message);
    this.onPathShown?.(this.currentPathId);
  }

  override showPath(pathId: string): void {
    super.showPath(pathId);
    this.onPathShown?.(this.currentPathId);
  }
}

export interface ProjectBackend {
  workspace: ProjectWorkspaceProvider;
  /** The host's token, for #288's /workspace/* and #289's /reviews/* routes. */
  session: ReviewSessionSource;
  engineBase?: string;
  fetch?: typeof fetch;
  mock: boolean;
  /** Settles once the host has said whether it offers projects. */
  ready: Promise<void>;
}

/**
 * The local engine's #288 and #289 routes, with the token and pickers of the
 * desktop host (project-host.ts), which offers none until its commands exist:
 * then projects stay unavailable. `?projectSource=mock` selects the mock only
 * in a Vite development server: import.meta.env.DEV is false in every build,
 * so the mock and its examples are left out of the app.
 */
export function projectBackend(parameters: URLSearchParams): ProjectBackend {
  if (import.meta.env.DEV && parameters.get("projectSource") === "mock") {
    const mock = new MockProjectBackend();
    return { workspace: mock.workspace, session: MOCK_SESSION, engineBase: MOCK_ENGINE_BASE, fetch: mock.fetch, mock: true, ready: Promise.resolve() };
  }
  const host = new ProjectHostHolder();
  const session: ReviewSessionSource = {
    current: () => {
      const token = host.session();
      return token ? { token } : undefined;
    },
  };
  const ready = connectProjectHost().then((connected) => host.set(connected), () => undefined);
  return { workspace: new EngineProjectWorkspace(host, new WorkspaceClient(session)), session, mock: false, ready };
}

export interface DesktopProjectsOptions {
  documentRoot: Document;
  backend: ProjectBackend;
  workspace: HTMLElement;
  header: HTMLElement;
  appPanels: readonly HTMLElement[];
  pathSummary: HTMLElement;
  pathView: ProjectAttackPathView;
  navigation: Pick<AppNavigation, "activate" | "currentView">;
  showModel(model: ModelSummary): Promise<void>;
  reopenExample(model: ModelSummary | undefined): void;
}

export class DesktopProjects {
  readonly controller: ProjectController;
  readonly workbench: ReviewWorkbench;
  readonly chrome: ProjectChrome;
  private examples: readonly ModelSummary[] = [];
  private lastExample?: ModelSummary;
  private enterWorkspace: () => void = () => {};
  private readonly beforeEnter: (() => void)[] = [];
  private home?: HomeEntryPoints;

  constructor(private readonly options: DesktopProjectsOptions) {
    const { documentRoot, backend } = options;
    const style = documentRoot.createElement("style");
    style.textContent = projectStyles;
    documentRoot.head.append(style);
    const client = new ReviewApiClient(backend.session, backend.engineBase, backend.fetch);
    this.chrome = new ProjectChrome(options.workspace, options.appPanels, {
      selectVersion: (id) => void this.controller.viewVersion(id),
      navigate: (page) => this.controller.navigate(page),
      close: () => this.controller.close(),
      retry: () => this.controller.retry(),
      startProject: () => this.controller.startProjectFromFile(),
    }, documentRoot);
    this.controller = new ProjectController(backend.workspace, client, this.chrome, {
      showModel: (model) => options.showModel(model),
      activate: (view) => options.navigation.activate(view),
      currentView: () => options.navigation.currentView,
      reopenExample: () => options.reopenExample(this.lastExample ?? this.examples[0]),
      enterWorkspace: () => {
        for (const callback of this.beforeEnter) callback();
        this.enterWorkspace();
      },
    });
    this.workbench = new ReviewWorkbench(client, this.controller, documentRoot);
    this.controller.attach(this.workbench);
    options.pathView.onPathShown = (pathId) => this.workbench.pathChanged(pathId);

    // The project bar and side navigation follow the header; the Risk Score panel joins the views.
    options.header.after(this.chrome.bar, this.chrome.navigation);
    options.workspace.append(this.chrome.riskPanel, this.chrome.announcer);
    // The review panel sits under the path summary in the attack-path view's side column.
    const side = documentRoot.createElement("div");
    side.className = "path-side";
    options.pathSummary.replaceWith(side);
    side.append(options.pathSummary, this.workbench.element);
    // Unsaved review input lives in memory: ask before the window unloads with some.
    documentRoot.defaultView?.addEventListener("beforeunload", (event) => {
      if (this.workbench.unsavedEverywhere > 0) event.preventDefault();
    });
    // A development server's mock only: builds leave the banner out with the mock.
    if (import.meta.env.DEV && backend.mock) {
      const banner = documentRoot.createElement("p");
      banner.className = "project-mock-banner";
      banner.setAttribute("role", "note");
      banner.textContent = "Development mock: projects, versions and reviews use the shared contract examples in memory. Nothing is saved, and the values after a save are the example's, not your input's.";
      options.header.before(banner);
    }
  }

  // --- main.ts hooks -------------------------------------------------------------

  get isOpen(): boolean {
    return this.controller.isOpen;
  }

  isProjectFile(file: string | undefined): boolean {
    return this.controller.isProjectFile(file);
  }

  source(model: ModelSummary) {
    return this.controller.source(model);
  }

  revisionApi(file: string | undefined) {
    return this.controller.revisionApi(file);
  }

  calculateRisk(file: string, matrix: string) {
    return this.controller.calculateRisk(file, matrix);
  }

  /** The picker shows an example: remember it, for "Start a project" and closing a project. */
  exampleShown(model: ModelSummary): void {
    this.lastExample = model;
    this.controller.exampleShown(model);
  }

  examplesListed(response: ModelListResponse): void {
    this.examples = response.models;
  }

  viewShown(view: AppView): void {
    this.controller.viewShown(view);
  }

  createProject(source: ProjectSource): Promise<boolean> {
    return this.controller.createProject(source);
  }

  projectsAvailable(): boolean {
    return this.controller.projectsAvailable();
  }

  /** Runs before a project takes over the window, such as closing a screen opened from home. */
  onEnterWorkspace(callback: () => void): void {
    this.beforeEnter.push(callback);
  }

  unavailableReason(): string {
    return this.controller.unavailableReason();
  }

  /**
   * Adds the entry points to the welcome screen. `start` is its "Get started"
   * button, whose click leaves the welcome screen, so opening a project leaves
   * it the same way.
   */
  installHome(welcome: HTMLElement, start: HTMLButtonElement, extra: Pick<HomeActions, "importProduct"> = {}): HomeEntryPoints {
    this.home = new HomeEntryPoints({
      ...extra,
      openThreatModel: () => this.controller.openThreatModel(),
      openProject: () => this.controller.openProject(),
    }, () => ({ projects: this.controller.projectsAvailable(), reason: this.controller.unavailableReason() }), this.options.documentRoot);
    start.before(this.home.element);
    // The host answers after start-up: show what it offers once it has.
    void this.options.backend.ready.then(() => {
      this.home?.render();
      this.workbench.targetChanged();
    });
    this.enterWorkspace = () => {
      if (welcome.isConnected) start.click();
    };
    return this.home;
  }
}
