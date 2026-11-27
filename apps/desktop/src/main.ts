import { bindInfoDisclosures } from "./library-presentation";
import { AppNavigation, type AppView, type LibraryView } from "./app-navigation";
import { staticDataBase } from "./app-mode";
import { checkEngine, describe, engineProcess, type EngineState } from "./engine";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { EngineProposalsDataProvider } from "./engine-proposals-provider";
import { SavedViewsPanel, savedViewElements, savedViewFile } from "./graph-saved-views";
import { EngineLibraryDataProvider } from "./engine-library-provider";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { connectGraphStartup, GraphStartup } from "./graph-startup";
import { KnowledgeGraphView } from "./graph-view";
import { FixtureLibraryDataProvider } from "./library-fixture";
import { libraryViewElements, LibraryDocumentsView } from "./library-view";
import {
  EngineModelCatalogProvider,
  ModelPicker,
  readRememberedModel,
  rememberModel,
  requestedModel,
  syncModelUrl,
} from "./model-catalog";
import { BOOKKEEPING_TYPES } from "./model-report";
import { ModelSession } from "./model-session";
import { AttackPathView } from "./path-view";
import { ModelReportView } from "./report-view";
import { EngineSdlDataProvider } from "./engine-sdl-provider";
import { SdlProgramView, sdlViewElements } from "./sdl-view";
import { StaticPreviewApi } from "./static-api";
import { StaticLibraryDataProvider } from "./static-library-provider";
import { configurePreviewChrome, openInitialModel } from "./preview-bootstrap";
import { createWeaknessProvider } from "./weakness-provider";
import { weaknessViewElements, WeaknessesView } from "./weakness-view";
import { CompatibleCoverageProvider } from "./coverage-provider";
import { RequirementsView, requirementsViewElements } from "./requirements-view";
import { StaticRequirementStandardsSource } from "./requirements-catalog-provider";

import { initializeWelcome } from "./welcome";
import radarMark from "./assets/radar.svg?raw";
// #290: projects, review and the home entry points (desktop only; see desktop-projects.ts).
import { DesktopProjects, ProjectAttackPathView, ProjectReportView, projectBackend } from "./desktop-projects";
import type { ModelSummary } from "./model-types";
import type { VersionApi } from "./revision-api";
// Import New Product (#290's import screen, in its own files: import-*.ts).
import { createImportScreen } from "./import-screen";

const POLL_MS = 2000;
// Vite replaces MODE at build time; the Pages bundle can therefore eliminate
// the desktop health-polling and Tauri sidecar branch entirely.
const BROWSER_PREVIEW_BUILD = import.meta.env.MODE === "pages";

async function refresh(): Promise<EngineState> {
  const state = await checkEngine();
  const process = state.kind === "unreachable" ? await engineProcess() : null;
  const { text, hint, tone } = describe(state, process);
  const statusEl = document.querySelector<HTMLElement>("#engine-status");
  const hintEl = document.querySelector<HTMLElement>("#engine-hint");
  if (statusEl) {
    statusEl.textContent = text;
    statusEl.className = `status status-${tone}`;
  }
  if (hintEl) hintEl.textContent = hint;
  return state;
}

interface ExploreGraph {
  savedViews?: SavedViewsPanel;
  startup: GraphStartup;
  usesEngine: boolean;
  view: KnowledgeGraphView;
}

/**
 * The developer "Explore graph" view for one model. It opens on the model's
 * threats and their neighbours, every other node is reached by expanding (or
 * "Show whole model"), and bookkeeping records stay out unless the reader asks
 * for them (#208). `?graphSource=fixture` keeps the development fixture.
 */
function createExploreGraph(
  parameters: URLSearchParams,
  file: string | undefined,
  showBookkeeping: boolean,
  staticApi?: StaticPreviewApi,
): ExploreGraph {
  const usesEngine = !staticApi && parameters.get("graphSource") !== "fixture";
  const provider = staticApi
    ? new EngineGraphDataProvider(file, staticApi.engineBase, staticApi.fetch, {
      hiddenDomainTypes: showBookkeeping ? undefined : BOOKKEEPING_TYPES,
      initialView: "threats",
      metadata: {
        source: "static-preview",
        label: "Published example data",
        notice: `Published example data from ${file ?? "the selected model"}`,
      },
    })
    : usesEngine
    ? new EngineGraphDataProvider(file, undefined, undefined, {
      hiddenDomainTypes: showBookkeeping ? undefined : BOOKKEEPING_TYPES,
      initialView: "threats",
    })
    : new DevelopmentFixtureProvider();
  // One view per model: switching model disposes the old one first, so
  // Cytoscape and its listeners are never duplicated.
  const view = new KnowledgeGraphView(provider);
  // Saved KG views and pending proposals (DL-0046) come from the engine's read-only
  // GET /proposals; a failure there stays in the view toolbar.
  const savedViews = usesEngine
    ? new SavedViewsPanel(
      new EngineProposalsDataProvider(),
      savedViewFile(file, parameters.get("file")),
      savedViewElements(),
      (ids) => view.focusSavedView(ids),
    )
    : undefined;
  const startup = connectGraphStartup(async () => {
    await view.start();
    await savedViews?.load();
  }, usesEngine, {
    notice: document.querySelector<HTMLElement>("#data-source-notice"),
    retryButton: document.querySelector<HTMLButtonElement>("#graph-retry"),
  });
  return { savedViews, startup, usesEngine, view };
}

/**
 * #290: the Explore graph for one project version, from that version's views
 * in memory (revision-api.ts). Desktop only: the browser preview has no projects.
 */
function createProjectExploreGraph(file: string, title: string, showBookkeeping: boolean, api: VersionApi): ExploreGraph {
  const view = new KnowledgeGraphView(new EngineGraphDataProvider(file, api.engineBase, api.fetch, {
    hiddenDomainTypes: showBookkeeping ? undefined : BOOKKEEPING_TYPES,
    initialView: "threats",
    metadata: { source: "engine", label: "Project version", notice: `Project version: ${title}` },
  }));
  const startup = connectGraphStartup(() => view.start(), false, {
    notice: document.querySelector<HTMLElement>("#data-source-notice"),
    retryButton: document.querySelector<HTMLButtonElement>("#graph-retry"),
  });
  return { startup, usesEngine: false, view };
}

window.addEventListener("DOMContentLoaded", () => {
  const parameters = new URLSearchParams(window.location.search);
  const preview = BROWSER_PREVIEW_BUILD;
  const staticApi = preview ? new StaticPreviewApi(staticDataBase()) : undefined;
  const required = <T extends HTMLElement>(id: string): T => {
    const element = document.getElementById(id);
    if (!element) throw new Error(`Missing required application element #${id}`);
    return element as T;
  };

  // Keep the mark in the page's SVG tree so it inherits the window theme,
  // including when the webview appearance differs from the system appearance.
  const radarTemplate = document.createElement("template");
  radarTemplate.innerHTML = radarMark;
  for (const icon of document.querySelectorAll(".brand-radar")) {
    icon.append(radarTemplate.content.cloneNode(true));
  }

  bindInfoDisclosures(document);
  if (preview) {
    configurePreviewChrome({
      body: document.body,
      banner: required("preview-banner"),
      enginePanel: required("engine-panel"),
      proposals: required("graph-proposals"),
      savedViews: required("saved-view-toolbar"),
      modelSelect: required<HTMLSelectElement>("model-select"),
      modelStatus: required("model-picker-status"),
      reportStatus: required("report-status"),
    });
  }

  // Library uses the complete published table in preview mode and retains all
  // client-side search, filtering, sorting and row-selection interactions.
  const libraryProvider = preview
    ? new StaticLibraryDataProvider(new URL("library/table.json", staticDataBase()).href)
    : parameters.get("librarySource") === "fixture"
    ? new FixtureLibraryDataProvider()
    : new EngineLibraryDataProvider();
  const libraryUsesEngine = libraryProvider.metadata.source === "engine";
  const libraryView = new LibraryDocumentsView(libraryProvider, libraryViewElements());
  // The published Pages app deliberately carries the small table fixture, while
  // desktop uses the complete locally configured catalog unless explicitly
  // switched to the development fixture.
  const weaknessProvider = createWeaknessProvider(preview, parameters);
  const weaknessUsesEngine = weaknessProvider.metadata.source === "engine";
  const weaknessView = new WeaknessesView(weaknessProvider, weaknessViewElements());
  const requirementsView = new RequirementsView(
    requirementsViewElements(),
    new StaticRequirementStandardsSource(),
  );

  let lastEngineState: EngineState | undefined;
  let visibleView: AppView | undefined;
  const bookkeepingToggle = required<HTMLInputElement>("graph-show-bookkeeping");
  if (preview) bookkeepingToggle.disabled = true;
  // Desktop keeps its eager engine graph so health polling behaves exactly as
  // before. Preview mode has no default graph: ModelSession.open constructs it
  // only after the catalog has resolved the URL's requested model.
  let explore = preview
    ? undefined
    : createExploreGraph(
      parameters,
      parameters.get("file") ?? undefined,
      bookkeepingToggle.checked,
      staticApi,
    );

  // #290: set below, outside the browser preview, once the views it wires exist.
  let projects: DesktopProjects | undefined;
  const pathView = new (preview ? AttackPathView : ProjectAttackPathView)({
    select: required("path-view-select"),
    banner: required("path-view-banner"),
    canvas: required("path-view-canvas"),
    summary: required("path-view-summary"),
    fit: required("path-view-fit"),
  });
  const reportView = new (preview ? ModelReportView : ProjectReportView)({
    status: required("report-status"),
    content: required("report-content"),
    retry: required("report-retry"),
  }, {
    openPath: (pathId) => {
      pathView.showPath(pathId);
      navigation.activate("paths");
    },
    retry: () => {
      if (session.current) void session.open(session.current);
      else void catalogStartup.retryNow();
    },
    calculateRisk: preview
      ? (file, matrix) => new EngineGraphDataProvider(
        file, staticApi?.engineBase, staticApi?.fetch,
      ).getRiskCalculation(matrix)
      // #290: a project version's risk comes from its own views, never the approved-vector route.
      : (file, matrix) => projects?.calculateRisk(file, matrix) ?? new EngineGraphDataProvider(file).getRiskCalculation(matrix),
  });
  const picker = new ModelPicker(required("model-select"), required("model-picker-status"), {
    disclosure: required("model-picker-info"),
    label: required("model-review-label"),
    summary: required("model-picker-summary"),
  }, (model) => {
    void session.open(model);
  });

  const startExploreIfVisible = () => {
    if (visibleView !== "graph" || !explore) return;
    if (!explore.startup.started && explore.usesEngine && lastEngineState) {
      void explore.startup.engineStateChanged(lastEngineState);
    } else if (!explore.startup.started && !explore.usesEngine) {
      void explore.startup.startNow();
    }
  };

  const replaceExplore = (file: string | undefined) => {
    explore?.savedViews?.dispose();
    explore?.view.dispose();
    const projectApi = preview ? undefined : projects?.revisionApi(file);
    explore = projectApi && file
      ? createProjectExploreGraph(file, session.current?.title ?? file, bookkeepingToggle.checked, projectApi)
      : createExploreGraph(parameters, file, bookkeepingToggle.checked, staticApi);
    explore.view.setVisible(visibleView === "graph");
    startExploreIfVisible();
  };
  bookkeepingToggle.addEventListener("change", () => {
    if (!preview || session.current) replaceExplore(session.current?.file);
  });

  const exampleSource = (model: ModelSummary) => new EngineGraphDataProvider(
    model.file,
    staticApi?.engineBase,
    staticApi?.fetch,
    staticApi ? {
      metadata: {
        source: "static-preview",
        label: "Published example data",
        notice: `Published example data from ${model.file}`,
      },
    } : {},
  );
  const exampleChanged = (model: ModelSummary) => {
    required("report-scroll").scrollTop = 0;
    if (preview) syncModelUrl(model);
    replaceExplore(model.file);
    const graphProvider = new EngineGraphDataProvider(
      model.file,
      staticApi?.engineBase,
      staticApi?.fetch,
    );
    const coverageProvider = new CompatibleCoverageProvider(
      model.file,
      graphProvider,
      staticApi?.engineBase,
      staticApi?.fetch,
    );
    requirementsView.openModel({
      file: model.file,
      notice: staticApi
        ? `Published example requirements from ${model.file}`
        : `Requirements from the local engine model ${model.file}`,
      getGraph: () => graphProvider.getModelGraph(),
      getCoverage: (product, signal) => coverageProvider.getCoverage(product, signal),
    });
    bookkeepingToggle.disabled = false;
  };
  // #290: a project version reads its own views in memory; examples are unchanged.
  const projectChanged = (model: ModelSummary, api: VersionApi) => {
    required("report-scroll").scrollTop = 0;
    replaceExplore(model.file);
    const graphProvider = new EngineGraphDataProvider(model.file, api.engineBase, api.fetch);
    const coverageProvider = new CompatibleCoverageProvider(model.file, graphProvider, api.engineBase, api.fetch);
    requirementsView.openModel({
      file: model.file,
      notice: `Requirements from the project ${model.title}, as the shown version records them`,
      getGraph: () => graphProvider.getModelGraph(),
      getCoverage: (product, signal) => coverageProvider.getCoverage(product, signal),
    });
    bookkeepingToggle.disabled = false;
  };

  // Only the latest choice is shown; see model-session.ts.
  const session = new ModelSession({
    views: {
      picker: preview ? picker : {
        show: (model) => {
          if (projects?.isProjectFile(model.file)) return;
          projects?.exampleShown(model);
          picker.show(model);
        },
      },
      report: reportView,
      paths: pathView,
    },
    source: preview ? exampleSource : (model) => projects?.source(model) ?? exampleSource(model),
    modelChanged: preview ? exampleChanged : (model) => {
      const api = projects?.revisionApi(model.file);
      if (api) projectChanged(model, api);
      else exampleChanged(model);
    },
    remember: preview ? rememberModel : (file) => {
      if (!projects?.isProjectFile(file)) rememberModel(file);
    },
  });

  // The model list loads once the engine answers, and retries like the graph does.
  const catalog = new EngineModelCatalogProvider(staticApi?.engineBase, staticApi?.fetch);
  const catalogStartup = new GraphStartup({
    start: async () => {
      const requested = requestedModel(parameters);
      await openInitialModel({
        catalog,
        requested,
        remembered: readRememberedModel(),
        setModels: preview ? (response) => picker.setModels(response) : (response) => {
          projects?.examplesListed(response);
          picker.setModels(response);
        },
        notice: (message) => picker.notice(message),
        empty: preview ? () => reportView.failed("The engine lists no example models.") : () => {
          if (!projects?.isOpen) reportView.failed("The engine lists no example models.");
        },
        // #290: an example arriving after a project opened must not replace it.
        open: preview ? (model) => session.open(model) : (model) => projects?.isOpen ? Promise.resolve() : session.open(model),
      });
    },
    onWaiting: () => {
      const source = preview ? "published example data" : "the local engine";
      picker.waiting(`Waiting for ${source}…`);
      if (!session.current) reportView.waiting(`Waiting for ${source}… The report opens as soon as it answers.`);
    },
    onFailure: (error, willRetry) => {
      const message = error instanceof Error ? error.message : String(error);
      picker.waiting("Could not list the example models.");
      if (!preview && projects?.isOpen) return;
      reportView.failed(`Could not list the example models: ${message}${willRetry ? " · retrying" : ""}`);
    },
  }, !preview);

  const sdlView = new SdlProgramView(
    new EngineSdlDataProvider(staticApi?.engineBase, staticApi?.fetch),
    sdlViewElements(),
  );
  const libraryPanel = required("library-view-panel");
  const librarySelect = required<HTMLSelectElement>("library-view-select");
  const librarySections = libraryPanel.querySelectorAll<HTMLElement>("[data-library-view]");
  const libraryViews = { records: libraryView, weaknesses: weaknessView, requirements: requirementsView, sdl: sdlView };

  const navigation = new AppNavigation([
    {
      view: "report",
      button: required("report-tab"),
      panel: required("report-view-panel"),
      activated: () => show("report"),
    },
    {
      view: "paths",
      button: required("paths-tab"),
      panel: required("paths-view-panel"),
      activated: () => {
        show("paths");
        requestAnimationFrame(() => pathView.resize());
      },
    },
    {
      view: "graph",
      button: required("graph-tab"),
      panel: required("graph-view-panel"),
      activated: () => {
        show("graph");
        requestAnimationFrame(() => explore?.view.resize());
        startExploreIfVisible();
      },
    },
    {
      view: "library",
      button: required("library-tab"),
      panel: libraryPanel,
      activated: (view) => {
        show("library");
        librarySelect.value = view;
        for (const section of librarySections) section.hidden = section.dataset.libraryView !== view;
        libraryViews[view].activate();
      },
    },
  ]);
  librarySelect.addEventListener("change", () => navigation.activateLibrary(librarySelect.value as LibraryView));

  function show(view: AppView): void {
    visibleView = view;
    librarySelect.hidden = view !== "library";
    pathView.setVisible(view === "paths");
    explore?.view.setVisible(view === "graph");
    if (!preview) projects?.viewShown(view);
  }

  if (!preview) {
    // #290: projects, Review & Edit and the home entry points of the team's design.
    const header = required("workspace").querySelector<HTMLElement>(":scope > .app-header");
    if (!header) throw new Error("Missing required application element .app-header");
    projects = new DesktopProjects({
      documentRoot: document,
      backend: projectBackend(parameters),
      workspace: required("workspace"),
      header,
      appPanels: [required("report-view-panel"), required("paths-view-panel"), libraryPanel, required("graph-view-panel")],
      pathSummary: required("path-view-summary"),
      pathView: pathView as ProjectAttackPathView,
      navigation,
      showModel: (model) => session.open(model),
      reopenExample: (model) => {
        if (model) void session.open(model);
        else void catalogStartup.retryNow();
      },
    });
    // Import New Product: its own screen, opened from the home page.
    const importScreen = createImportScreen(document, parameters, projects);
    document.body.append(importScreen.element);
    projects.onEnterWorkspace(() => importScreen.hide());
    const welcome = required("welcome");
    projects.installHome(welcome, required<HTMLButtonElement>("get-started"), {
      importProduct: (opener) => importScreen.open(welcome, opener),
    });
  }

  initializeWelcome({
    welcome: required("welcome"),
    workspace: required("workspace"),
    start: required("get-started"),
  }, {
    isPreview: preview,
    location: window.location,
    navigation,
    events: window,
    reducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)"),
  });
  navigation.start();
  const refreshCanvasThemes = () => {
    pathView.refreshTheme();
    explore?.view.refreshTheme();
  };
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", refreshCanvasThemes);
  void document.fonts.ready.then(refreshCanvasThemes);

  if (preview) {
    void catalogStartup.startNow();
  } else {
    const poll = async () => {
      lastEngineState = await refresh();
      void catalogStartup.engineStateChanged(lastEngineState);
      if (libraryUsesEngine) void libraryView.engineStateChanged(lastEngineState);
      if (weaknessUsesEngine) void weaknessView.engineStateChanged(lastEngineState);
      if (navigation.currentLibraryView === "requirements") void requirementsView.engineStateChanged(lastEngineState);
      if (visibleView === "graph" && explore?.usesEngine) void explore.startup.engineStateChanged(lastEngineState);
      if (navigation.currentLibraryView === "sdl") void sdlView.engineStateChanged(lastEngineState);
    };
    void poll();
    window.setInterval(() => void poll(), POLL_MS);
  }
});
