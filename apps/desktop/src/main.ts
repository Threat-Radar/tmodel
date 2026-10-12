import { checkEngine, describe } from "./engine";

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

window.addEventListener("DOMContentLoaded", () => {
  void refresh();
  window.setInterval(() => void refresh(), POLL_MS);
});
