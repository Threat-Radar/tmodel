import { AppNavigation } from "./app-navigation";
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

window.addEventListener("DOMContentLoaded", () => {
  const parameters = new URLSearchParams(window.location.search);
  const preview = BROWSER_PREVIEW_BUILD;
  const staticApi = preview ? new StaticPreviewApi(staticDataBase()) : undefined;
  const required = <T extends HTMLElement>(id: string): T => {
    const element = document.getElementById(id);
    if (!element) throw new Error(`Missing required application element #${id}`);
    return element as T;
  };

  if (preview) {
    configurePreviewChrome({
      body: document.body,
      banner: required("preview-banner"),
      enginePanel: required("engine-panel"),
      sdlTab: required("sdl-tab"),
      sdlPanel: required("sdl-view-panel"),
      proposals: required("graph-proposals"),
      savedViews: required("saved-view-toolbar"),
      libraryTab: required("library-tab"),
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

  let lastEngineState: EngineState | undefined;
  let visibleView: string | undefined;
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

  const pathView = new AttackPathView({
    select: required("path-view-select"),
    banner: required("path-view-banner"),
    canvas: required("path-view-canvas"),
    summary: required("path-view-summary"),
    fit: required("path-view-fit"),
  });
  const reportView = new ModelReportView({
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
  });
  const picker = new ModelPicker(required("model-select"), required("model-picker-status"), (model) => {
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
    explore = createExploreGraph(parameters, file, bookkeepingToggle.checked, staticApi);
    explore.view.setVisible(visibleView === "graph");
    startExploreIfVisible();
  };
  bookkeepingToggle.addEventListener("change", () => {
    if (!preview || session.current) replaceExplore(session.current?.file);
  });

  // Only the latest choice is shown; see model-session.ts.
  const session = new ModelSession({
    views: { picker, report: reportView, paths: pathView },
    source: (model) => new EngineGraphDataProvider(
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
    ),
    modelChanged: (model) => {
      required("report-scroll").scrollTop = 0;
      if (preview) syncModelUrl(model);
      replaceExplore(model.file);
      bookkeepingToggle.disabled = false;
    },
    remember: rememberModel,
  });

  // The model list loads once the engine answers, and retries like the graph does.
  const catalog = new EngineModelCatalogProvider(staticApi?.engineBase, staticApi?.fetch);
  const catalogStartup = new GraphStartup({
    start: async () => {
      const requested = parameters.get("model") ?? parameters.get("file");
      await openInitialModel({
        catalog,
        requested,
        remembered: readRememberedModel(),
        setModels: (response) => picker.setModels(response),
        notice: (message) => picker.notice(message),
        empty: () => reportView.failed("The engine lists no example models."),
        open: (model) => session.open(model),
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
      reportView.failed(`Could not list the example models: ${message}${willRetry ? " · retrying" : ""}`);
    },
  }, !preview);

  const sdlView = new SdlProgramView(new EngineSdlDataProvider(), sdlViewElements());

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
      panel: required("library-view-panel"),
      activated: () => {
        show("library");
        libraryView.activate();
      },
    },
    ...(!preview ? [{
      view: "sdl" as const,
      button: required<HTMLButtonElement>("sdl-tab"),
      panel: required("sdl-view-panel"),
      activated: () => {
        show("sdl");
        sdlView.activate();
      },
    }] : []),
  ]);

  function show(view: string): void {
    visibleView = view;
    pathView.setVisible(view === "paths");
    explore?.view.setVisible(view === "graph");
  }

  navigation.start();

  if (preview) {
    void catalogStartup.startNow();
  } else {
    const poll = async () => {
      lastEngineState = await refresh();
      void catalogStartup.engineStateChanged(lastEngineState);
      if (libraryUsesEngine) void libraryView.engineStateChanged(lastEngineState);
      if (visibleView === "graph" && explore?.usesEngine) void explore.startup.engineStateChanged(lastEngineState);
      if (visibleView === "sdl") void sdlView.engineStateChanged(lastEngineState);
    };
    void poll();
    window.setInterval(() => void poll(), POLL_MS);
  }
});
