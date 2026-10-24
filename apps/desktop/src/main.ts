import { checkEngine, describe, type EngineState } from "./engine";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { connectGraphStartup, type GraphStartup } from "./graph-startup";
import { KnowledgeGraphView } from "./graph-view";

const POLL_MS = 2000;

async function refresh(): Promise<EngineState> {
  const state = await checkEngine();
  const { text, hint } = describe(state);
  const statusEl = document.querySelector<HTMLElement>("#engine-status");
  const hintEl = document.querySelector<HTMLElement>("#engine-hint");
  if (statusEl) {
    statusEl.textContent = text;
    statusEl.className = `status status-${state.kind}`;
  }
  if (hintEl) hintEl.textContent = hint;
  return state;
}

function createKnowledgeGraphStartup(): { startup: GraphStartup; usesEngine: boolean } {
  const parameters = new URLSearchParams(window.location.search);
  const usesEngine = parameters.get("graphSource") !== "fixture";
  const provider = usesEngine
    ? new EngineGraphDataProvider(parameters.get("file") ?? undefined)
    : new DevelopmentFixtureProvider();
  // One view per window: retries reuse it, so a recovered start never creates
  // a second Cytoscape instance or duplicate listeners.
  const view = new KnowledgeGraphView(provider);
  const startup = connectGraphStartup(() => view.start(), usesEngine, {
    notice: document.querySelector<HTMLElement>("#data-source-notice"),
    retryButton: document.querySelector<HTMLButtonElement>("#graph-retry"),
  });
  return { startup, usesEngine };
}

window.addEventListener("DOMContentLoaded", () => {
  const { startup, usesEngine } = createKnowledgeGraphStartup();
  const poll = async () => {
    const state = await refresh();
    if (usesEngine) void startup.engineStateChanged(state);
  };
  void poll();
  window.setInterval(() => void poll(), POLL_MS);
  if (!usesEngine) void startup.startNow();
});
