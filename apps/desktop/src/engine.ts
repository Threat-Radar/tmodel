// Client for the tmodel engine's local API (loopback only, ADR-0003).
// The GUI only displays; all logic lives in the Python engine (APP-0001 A-030).

export const DEFAULT_ENGINE_URL: string =
  import.meta.env?.VITE_TMODEL_ENGINE_URL ?? "http://127.0.0.1:47811";

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

export function describe(state: EngineState): { text: string; hint: string } {
  switch (state.kind) {
    case "connected":
      return { text: `connected to local engine · v${state.health.version}`, hint: "" };
    case "unhealthy":
      return {
        text: `local engine unhealthy (${state.health.status}) · v${state.health.version}`,
        hint: "",
      };
    case "unreachable":
      return {
        text: "local engine not running",
        hint: "Start it with: tmodel serve — this window retries automatically.",
      };
  }
}
