import { DEFAULT_ENGINE_URL } from "./engine";
import type { SdlDataProvider, SdlModel, SdlView } from "./sdl-types";

/** Reads SDL models from the local engine's GET /sdl (DL-0043). */
export class EngineSdlDataProvider implements SdlDataProvider {
  constructor(
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async listModels(signal?: AbortSignal): Promise<SdlModel[]> {
    return parseSdlModels(await this.request({}, signal));
  }

  async getView(file: string, program?: string, signal?: AbortSignal): Promise<SdlView> {
    return parseSdlView(await this.request({ file, program }, signal));
  }

  private async request(
    parameters: Readonly<Record<string, string | undefined>>,
    signal?: AbortSignal,
  ): Promise<unknown> {
    const url = new URL("/sdl", `${this.baseUrl.replace(/\/$/, "")}/`);
    for (const [name, value] of Object.entries(parameters)) {
      if (value) url.searchParams.set(name, value);
    }
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
    try {
      return await response.json();
    } catch {
      throw new Error("Engine returned malformed JSON");
    }
  }
}

export function parseSdlModels(value: unknown): SdlModel[] {
  if (!isObject(value) || !Array.isArray(value.models)
    || !value.models.every((m) => isObject(m) && typeof m.file === "string")) {
    throw new Error("Engine returned an unexpected SDL model list");
  }
  return value.models as SdlModel[];
}

export function parseSdlView(value: unknown): SdlView {
  if (!isObject(value) || typeof value.file !== "string" || !isObject(value.program)
    || !isObject(value.product) || !Array.isArray(value.phases) || !Array.isArray(value.sets)
    || !Array.isArray(value.nodes) || !Array.isArray(value.gaps)
    || !Array.isArray(value.awaiting_review)
    || !value.phases.every((p) => isObject(p) && Array.isArray(p.items))) {
    throw new Error("Engine returned an unexpected SDL view");
  }
  return value as unknown as SdlView;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
