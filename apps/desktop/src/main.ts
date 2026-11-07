import { AppNavigation } from "./app-navigation";
import { checkEngine, describe, engineProcess, type EngineState } from "./engine";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { EngineLibraryDataProvider } from "./engine-library-provider";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { connectGraphStartup, type GraphStartup } from "./graph-startup";
import { KnowledgeGraphView } from "./graph-view";
import { FixtureLibraryDataProvider } from "./library-fixture";
import { libraryViewElements, LibraryDocumentsView } from "./library-view";
import { EngineSdlDataProvider } from "./engine-sdl-provider";
import { SdlProgramView, sdlViewElements } from "./sdl-view";

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

function createKnowledgeGraphStartup(parameters: URLSearchParams): {
  startup: GraphStartup;
  usesEngine: boolean;
  view: KnowledgeGraphView;
} {
  const usesEngine = parameters.get("graphSource") !== "fixture";
  const provider = usesEngine
    ? new EngineGraphDataProvider(parameters.get("file") ?? undefined)
    : new DevelopmentFixtureProvider();
  // One view per window: navigation and retries reuse it, so Cytoscape and its
  // listeners are never duplicated.
  const view = new KnowledgeGraphView(provider);
  const startup = connectGraphStartup(() => view.start(), usesEngine, {
    notice: document.querySelector<HTMLElement>("#data-source-notice"),
    retryButton: document.querySelector<HTMLButtonElement>("#graph-retry"),
  });
  return { startup, usesEngine, view };
}

window.addEventListener("DOMContentLoaded", () => {
  const parameters = new URLSearchParams(window.location.search);
  const libraryProvider = parameters.get("librarySource") === "fixture"
    ? new FixtureLibraryDataProvider()
    : new EngineLibraryDataProvider();
  const libraryUsesEngine = libraryProvider.metadata.source === "engine";
  const libraryView = new LibraryDocumentsView(libraryProvider, libraryViewElements());
  const graph = createKnowledgeGraphStartup(parameters);
  let graphVisible = false;
  let lastEngineState: EngineState | undefined;

  const required = <T extends HTMLElement>(id: string): T => {
    const element = document.getElementById(id);
    if (!element) throw new Error(`Missing required application element #${id}`);
    return element as T;
  };
  const sdlView = new SdlProgramView(new EngineSdlDataProvider(), sdlViewElements());
  let sdlVisible = false;
  const hideGraph = () => {
    graphVisible = false;
    graph.view.setVisible(false);
  };
  const navigation = new AppNavigation([
    {
      view: "library",
      button: required("library-tab"),
      panel: required("library-view-panel"),
      activated: () => {
        hideGraph();
        sdlVisible = false;
        libraryView.activate();
      },
    },
    {
      view: "graph",
      button: required("graph-tab"),
      panel: required("graph-view-panel"),
      activated: () => {
        sdlVisible = false;
        graphVisible = true;
        graph.view.setVisible(true);
        requestAnimationFrame(() => graph.view.resize());
        if (!graph.startup.started && graph.usesEngine && lastEngineState) {
          void graph.startup.engineStateChanged(lastEngineState);
        } else if (!graph.startup.started && !graph.usesEngine) {
          void graph.startup.startNow();
        }
      },
    },
    {
      view: "sdl",
      button: required("sdl-tab"),
      panel: required("sdl-view-panel"),
      activated: () => {
        hideGraph();
        sdlVisible = true;
        sdlView.activate();
      },
    },
  ]);
  navigation.start();

  const poll = async () => {
    lastEngineState = await refresh();
    if (libraryUsesEngine) void libraryView.engineStateChanged(lastEngineState);
    if (graphVisible && graph.usesEngine) void graph.startup.engineStateChanged(lastEngineState);
    if (sdlVisible) void sdlView.engineStateChanged(lastEngineState);
  };
  void poll();
  window.setInterval(() => void poll(), POLL_MS);
});
