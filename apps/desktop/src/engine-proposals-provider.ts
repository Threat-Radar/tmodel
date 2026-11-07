import { DEFAULT_ENGINE_URL } from "./engine";
import type { ProposalsDataProvider, ProposalsResponse } from "./proposal-types";

/** Reads pending proposals and saved KG views from the engine's GET /proposals (DL-0046). */
export class EngineProposalsDataProvider implements ProposalsDataProvider {
  constructor(
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async getProposals(file: string, signal?: AbortSignal): Promise<ProposalsResponse> {
    const url = new URL("/proposals", `${this.baseUrl.replace(/\/$/, "")}/`);
    url.searchParams.set("file", fileName(file));
    const response = await this.fetchImpl(url, { signal });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const body = await response.json() as { error?: unknown };
        if (typeof body.error === "string") detail = body.error;
      } catch {
        // Keep the HTTP status when the engine did not return JSON.
      }
      throw new Error(`Engine request failed: ${detail}`);
    }
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      throw new Error("Engine returned malformed JSON");
    }
    return parseProposals(body);
  }
}

export function parseProposals(value: unknown): ProposalsResponse {
  if (!isObject(value) || typeof value.file !== "string" || !Array.isArray(value.proposals)
    || !Array.isArray(value.views)
    || !value.views.every((v) => isObject(v) && typeof v.id === "string"
      && typeof v.state === "string" && Array.isArray(v.node_ids))
    || !value.proposals.every((p) => isObject(p) && typeof p.id === "string"
      && Array.isArray(p.objects) && Array.isArray(p.assertions))) {
    throw new Error("Engine returned an unexpected proposals payload");
  }
  return value as unknown as ProposalsResponse;
}

/** The engine takes a model name in its approved directory, never a local path. */
function fileName(file: string): string {
  return file.split(/[\\/]/).pop() ?? file;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
