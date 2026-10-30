import { checkEngine, describe, engineProcess } from "./engine";

const POLL_MS = 2000;

async function refresh(): Promise<void> {
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
}

window.addEventListener("DOMContentLoaded", () => {
  void refresh();
  window.setInterval(() => void refresh(), POLL_MS);
});
