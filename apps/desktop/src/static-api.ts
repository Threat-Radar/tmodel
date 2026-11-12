/**
 * GET-only adapter from the existing engine clients to the JSON files emitted
 * by docs/publishing/render_app.py. It deliberately has no localhost fallback.
 */

interface GoalFile {
  goal: string;
  file: string;
}

interface GoalManifest {
  goals: GoalFile[];
}

const API_ORIGIN = "https://static-preview.invalid/";
const SAFE_MODEL_FILE = /^[a-z0-9][a-z0-9._-]*\.ya?ml$/i;

export class StaticPreviewApi {
  readonly engineBase = API_ORIGIN;
  readonly fetch: typeof fetch;
  private readonly goalManifests = new Map<string, Promise<GoalManifest>>();

  constructor(
    private readonly dataBase: string,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {
    this.fetch = (input, init) => this.request(input, init);
  }

  private async request(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    const method = (init?.method ?? (input instanceof Request ? input.method : "GET")).toUpperCase();
    if (method !== "GET") return jsonError(405, "browser preview data is read-only");

    const request = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url);
    if (request.origin !== new URL(API_ORIGIN).origin) return jsonError(400, "unexpected preview API origin");
    if (request.pathname === "/models") return this.get("models.json", init);

    const file = request.searchParams.get("file");
    const model = file ? modelId(file) : undefined;
    if (!model) return jsonError(400, "missing or invalid model file");
    const root = `models/${encodeURIComponent(model)}/`;
    if (request.pathname === "/graph") return this.get(`${root}graph.json`, init);
    if (request.pathname !== "/attack-paths") return jsonError(404, "static preview route not found");

    const goal = request.searchParams.get("goal");
    if (!goal) return this.get(`${root}attack-paths/index.json`, init);
    const manifest = await this.goalManifest(model, root, init);
    const entry = manifest.goals.find((candidate) => candidate.goal === goal);
    if (!entry || !/^goal-[0-9]{3}\.json$/.test(entry.file)) return jsonError(404, `unknown goal: ${goal}`);
    return this.get(`${root}attack-paths/${entry.file}`, init);
  }

  private goalManifest(model: string, root: string, init?: RequestInit): Promise<GoalManifest> {
    let pending = this.goalManifests.get(model);
    if (!pending) {
      pending = this.get(`${root}attack-paths/goals.json`, init).then(async (response) => {
        if (!response.ok) throw new Error(`Static preview request failed: HTTP ${response.status}`);
        const value = await response.json() as GoalManifest;
        if (!value || !Array.isArray(value.goals)
          || !value.goals.every((entry) => typeof entry.goal === "string" && typeof entry.file === "string")) {
          throw new Error("Static preview returned a malformed attack-path manifest");
        }
        return value;
      });
      this.goalManifests.set(model, pending);
      pending.catch(() => {
        if (this.goalManifests.get(model) === pending) this.goalManifests.delete(model);
      });
    }
    return pending;
  }

  private get(path: string, init?: RequestInit): Promise<Response> {
    return this.fetchImpl(new URL(path, this.dataBase), { ...init, method: "GET" });
  }
}

function modelId(file: string): string | undefined {
  if (!SAFE_MODEL_FILE.test(file)) return undefined;
  return file.replace(/\.ya?ml$/i, "");
}

function jsonError(status: number, error: string): Response {
  return new Response(JSON.stringify({ error }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
