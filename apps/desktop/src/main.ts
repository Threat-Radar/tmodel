import { AppNavigation } from "./app-navigation";
import { checkEngine, describe, engineProcess, type EngineState } from "./engine";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { EngineLibraryDataProvider } from "./engine-library-provider";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { connectGraphStartup, GraphStartup } from "./graph-startup";
import { KnowledgeGraphView } from "./graph-view";
import { FixtureLibraryDataProvider } from "./library-fixture";
import { libraryViewElements, LibraryDocumentsView } from "./library-view";
import {
  chooseModel,
  EngineModelCatalogProvider,
  ModelPicker,
  readRememberedModel,
  rememberModel,
} from "./model-catalog";
import { BOOKKEEPING_TYPES } from "./model-report";
import { ModelSession } from "./model-session";
import type { ModelSummary } from "./model-types";
import { AttackPathView } from "./path-view";
import { ModelReportView } from "./report-view";

const POLL_MS = 2000;

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
function createExploreGraph(parameters: URLSearchParams, file: string | undefined, showBookkeeping: boolean): ExploreGraph {
  const usesEngine = parameters.get("graphSource") !== "fixture";
  const provider = usesEngine
    ? new EngineGraphDataProvider(file, undefined, undefined, {
      hiddenDomainTypes: showBookkeeping ? undefined : BOOKKEEPING_TYPES,
      initialView: "threats",
    })
    : new DevelopmentFixtureProvider();
  // One view per model: switching model disposes the old one first, so
  // Cytoscape and its listeners are never duplicated.
  const view = new KnowledgeGraphView(provider);
  const startup = connectGraphStartup(() => view.start(), usesEngine, {
    notice: document.querySelector<HTMLElement>("#data-source-notice"),
    retryButton: document.querySelector<HTMLButtonElement>("#graph-retry"),
  });
  return { startup, usesEngine, view };
}

window.addEventListener("DOMContentLoaded", () => {
  const parameters = new URLSearchParams(window.location.search);
  const required = <T extends HTMLElement>(id: string): T => {
    const element = document.getElementById(id);
    if (!element) throw new Error(`Missing required application element #${id}`);
    return element as T;
  };

  // Library (unchanged by #208).
  const libraryProvider = parameters.get("librarySource") === "fixture"
    ? new FixtureLibraryDataProvider()
    : new EngineLibraryDataProvider();
  const libraryUsesEngine = libraryProvider.metadata.source === "engine";
  const libraryView = new LibraryDocumentsView(libraryProvider, libraryViewElements());

  let lastEngineState: EngineState | undefined;
  let models: readonly ModelSummary[] = [];
  let visibleView: string | undefined;
  const bookkeepingToggle = required<HTMLInputElement>("graph-show-bookkeeping");
  let explore = createExploreGraph(parameters, parameters.get("file") ?? undefined, bookkeepingToggle.checked);

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
    if (visibleView !== "graph") return;
    if (!explore.startup.started && explore.usesEngine && lastEngineState) {
      void explore.startup.engineStateChanged(lastEngineState);
    } else if (!explore.startup.started && !explore.usesEngine) {
      void explore.startup.startNow();
    }
  };

  const replaceExplore = (file: string | undefined) => {
    explore.view.dispose();
    explore = createExploreGraph(parameters, file, bookkeepingToggle.checked);
    explore.view.setVisible(visibleView === "graph");
    startExploreIfVisible();
  };
  bookkeepingToggle.addEventListener("change", () => replaceExplore(session.current?.file));

  // Only the latest choice is shown; see model-session.ts.
  const session = new ModelSession({
    views: { picker, report: reportView, paths: pathView },
    source: (model) => new EngineGraphDataProvider(model.file),
    modelChanged: (model) => {
      required("report-scroll").scrollTop = 0;
      replaceExplore(model.file);
    },
    remember: rememberModel,
  });

  // The model list loads once the engine answers, and retries like the graph does.
  const catalog = new EngineModelCatalogProvider();
  const catalogStartup = new GraphStartup({
    start: async () => {
      const response = await catalog.listModels();
      models = response.models;
      picker.setModels(response);
      const model = chooseModel(models, {
        requested: parameters.get("model") ?? parameters.get("file"),
        remembered: readRememberedModel(),
      });
      if (!model) {
        reportView.failed("The engine lists no example models.");
        return;
      }
      await session.open(model);
    },
    onWaiting: () => {
      picker.waiting("Waiting for the local engine…");
      if (!session.current) reportView.waiting("Waiting for the local engine… The report opens as soon as it answers.");
    },
    onFailure: (error, willRetry) => {
      const message = error instanceof Error ? error.message : String(error);
      picker.waiting("Could not list the example models.");
      reportView.failed(`Could not list the example models: ${message}${willRetry ? " · retrying" : ""}`);
    },
  });

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
        requestAnimationFrame(() => explore.view.resize());
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
  ]);

  function show(view: string): void {
    visibleView = view;
    pathView.setVisible(view === "paths");
    explore.view.setVisible(view === "graph");
  }

  navigation.start();

  const poll = async () => {
    lastEngineState = await refresh();
    void catalogStartup.engineStateChanged(lastEngineState);
    if (libraryUsesEngine) void libraryView.engineStateChanged(lastEngineState);
    if (visibleView === "graph" && explore.usesEngine) void explore.startup.engineStateChanged(lastEngineState);
  };
  void poll();
  window.setInterval(() => void poll(), POLL_MS);
});
