// Client for the tmodel engine's local API (loopback only, ADR-0003).
// The GUI only displays; all logic lives in the Python engine (APP-0001 A-030).

import { invoke, isTauri } from "@tauri-apps/api/core";

export const ENGINE_PORT = 47811;
export const DEFAULT_ENGINE_URL: string =
  import.meta.env?.VITE_TMODEL_ENGINE_URL ?? `http://127.0.0.1:${ENGINE_PORT}`;

export interface Health {
  status: string;
  engine: string;
  version: string;
  python?: string;
}

export type EngineState =
  | { kind: "connected"; health: Health }
  | { kind: "unhealthy"; health: Health }
  | { kind: "unreachable"; error: string };

// What the app shell knows about the bundled engine process (#124; src-tauri/src/engine.rs).
// null outside the desktop app (e.g. `npm run dev` in a browser) or before the shell decides.
export type EngineProcess =
  | { kind: "started" }
  | { kind: "external" }
  | { kind: "port_busy"; port: number }
  | { kind: "spawn_failed"; error: string }
  | { kind: "exited"; code: number | null; stderr: string }
  | null;

export type Tone = "pending" | "connected" | "unhealthy" | "unreachable";

export async function checkEngine(
  baseUrl: string = DEFAULT_ENGINE_URL,
  fetchImpl: typeof fetch = fetch,
): Promise<EngineState> {
  try {
    const resp = await fetchImpl(`${baseUrl.replace(/\/$/, "")}/health`);
    if (!resp.ok) {
      return { kind: "unreachable", error: `HTTP ${resp.status}` };
    }
    const health = (await resp.json()) as Health;
    return health.status === "ok"
      ? { kind: "connected", health }
      : { kind: "unhealthy", health };
  } catch (err) {
    return { kind: "unreachable", error: err instanceof Error ? err.message : String(err) };
  }
}

export async function engineProcess(): Promise<EngineProcess> {
  if (!isTauri()) return null;
  try {
    return await invoke<EngineProcess>("engine_process");
  } catch {
    return null;
  }
}

export function describe(
  state: EngineState,
  process: EngineProcess = null,
): { text: string; hint: string; tone: Tone } {
  switch (state.kind) {
    case "connected":
      return {
        text: `connected to local engine · v${state.health.version}`,
        hint: "",
        tone: "connected",
      };
    case "unhealthy":
      return {
        text: `local engine unhealthy (${state.health.status}) · v${state.health.version}`,
        hint: "",
        tone: "unhealthy",
      };
    case "unreachable":
      return whyUnreachable(process);
  }
}

function whyUnreachable(process: EngineProcess): { text: string; hint: string; tone: Tone } {
  switch (process?.kind) {
    case "started":
      return { text: "starting local engine…", hint: "", tone: "pending" };
    case "port_busy":
      return {
        text: `port ${process.port} is in use by another program`,
        hint: `tmodel runs its engine on port ${process.port}. Quit the program using it, then reopen tmodel.`,
        tone: "unreachable",
      };
    case "spawn_failed":
      return {
        text: "could not start the local engine",
        hint: process.error,
        tone: "unreachable",
      };
    case "exited": {
      const code = process.code === null ? "" : ` (exit code ${process.code})`;
      const last = process.stderr.trim().split("\n").pop() ?? "";
      return {
        text: `local engine stopped${code}`,
        hint: last ? `${last} — reopen tmodel to restart it.` : "Reopen tmodel to restart it.",
        tone: "unreachable",
      };
    }
    case "external":
      return {
        text: "local engine not running",
        hint: "The engine started outside the app (tmodel serve) stopped answering. Start it again, or quit it and reopen tmodel.",
        tone: "unreachable",
      };
    default:
      return {
        text: "local engine not running",
        hint: "Start it with: tmodel serve — this window retries automatically.",
        tone: "unreachable",
      };
  }
}
