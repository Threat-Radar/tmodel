import { checkEngine, describe } from "./engine";
import { EngineGraphDataProvider } from "./engine-graph-provider";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { KnowledgeGraphView } from "./graph-view";

const POLL_MS = 2000;

async function refresh(): Promise<void> {
  const state = await checkEngine();
  const { text, hint } = describe(state);
  const statusEl = document.querySelector<HTMLElement>("#engine-status");
  const hintEl = document.querySelector<HTMLElement>("#engine-hint");
  if (statusEl) {
    statusEl.textContent = text;
    statusEl.className = `status status-${state.kind}`;
  }
  if (hintEl) hintEl.textContent = hint;
}

async function startKnowledgeGraph(): Promise<void> {
  try {
    const parameters = new URLSearchParams(window.location.search);
    const provider = parameters.get("graphSource") === "fixture"
      ? new DevelopmentFixtureProvider()
      : new EngineGraphDataProvider(parameters.get("file") ?? undefined);
    await new KnowledgeGraphView(provider).start();
  } catch (error) {
    console.error("Unable to start the knowledge graph", error);
    const notice = document.querySelector<HTMLElement>("#data-source-notice");
    if (notice) {
      notice.textContent = "Unable to load the knowledge graph. Check the developer console for details.";
      notice.classList.add("is-error");
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  void refresh();
  window.setInterval(() => void refresh(), POLL_MS);
  void startKnowledgeGraph();
});
