// #290: development and test stand-ins for the desktop host's step (project-host.ts),
// #288's workspace routes and #289's review routes, built from the shared
// examples: engine/examples/human-review/contract.json and the review
// service's own answers in fixtures/human-review-revisions.json. Answers have
// the shapes of #288's contract (fixtures/model-workspace-contract.json). The
// desktop app uses them only in a Vite development server opened with
// ?projectSource=mock; production builds leave this module out. The app labels
// them as a mock wherever it uses them.
//
// The mock does not run the engine: whatever a save sends, it answers with the
// contract's saved revision, so the values shown after a save are the shared
// example's, not a calculation of the request.

import contract from "../../../engine/examples/human-review/contract.json";
import revisions from "./fixtures/human-review-revisions.json";
import type { HostProjectStep, ProjectHost } from "./project-host";
import type { ReviewSessionSource } from "./review-client";
import { EngineProjectWorkspace, WorkspaceClient } from "./project-workspace";

/** A placeholder token for the in-memory mock; it is never a credential and never leaves the page. */
export const MOCK_TOKEN = "development-mock-session-not-a-credential";
export const MOCK_SESSION: ReviewSessionSource = { current: () => ({ token: MOCK_TOKEN }) };
export const MOCK_ENGINE_BASE = "https://review-mock.invalid/";

const CONTRACT_MODEL = "local:one";
const FILE_DIGEST = "sha256:fedede9403741ecde657609801c84f6ef919a376ac74479408d88b801a77cd9f";

interface MockVersion {
  number: number | null;
  version: string;
  description: string | null;
  created_at: string;
  /** Which contract revision this version answers with (r1 before a save, r2 after). */
  data: "r1" | "r2";
}

interface MockModel {
  model_id: string;
  kind: "project" | "file";
  name: string;
  editable: boolean;
  versions: MockVersion[];
}

/** Retags every model_id and revision field of a contract answer for a mock model version. */
export function retag<T>(value: T, modelId: string, revision: string, from = CONTRACT_MODEL): T {
  const visit = (item: unknown): unknown => {
    if (Array.isArray(item)) return item.map(visit);
    if (typeof item !== "object" || item === null) return item;
    return Object.fromEntries(Object.entries(item).map(([key, entry]) => {
      if ((key === "model_id" || key === "file" || key === "id") && entry === from) return [key, modelId];
      if (key === "revision" && typeof entry === "string") return [key, revision];
      return [key, visit(entry)];
    }));
  };
  return visit(value) as T;
}

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

function error(status: number, code: string, message: string, extra: Record<string, unknown> = {}): Response {
  return json(status, { error: { code, message, ...extra } });
}

type FailCode = "validation_error" | "permission_denied" | "revision_conflict" | "save_failure" | "workspace_failure" | "not_found";

/**
 * One store for all three stand-ins, so a mock save adds a version the mock
 * workspace then lists. `failWith` makes the next review operation fail with
 * one of the contract's error examples, for tests and demonstrations.
 */
export class MockProjectBackend {
  readonly models = new Map<string, MockModel>();
  readonly requests: { path: string; body: unknown }[] = [];
  readonly steps: HostProjectStep[] = [];
  readonly host: ProjectHost;
  readonly workspace: EngineProjectWorkspace;
  private failNext?: { code: FailCode; status: number };
  private counter = 0;
  private clock = Date.parse("2026-11-27T12:00:00Z");

  constructor(private readonly options: { cancelPickers?: boolean } = {}) {
    this.host = {
      session: () => MOCK_TOKEN,
      hostProjectStep: (step) => this.hostStep(step),
    };
    this.workspace = new EngineProjectWorkspace(this.host, new WorkspaceClient(MOCK_SESSION, MOCK_ENGINE_BASE, this.fetch));
  }

  failWith(code: FailCode, status: number): void {
    this.failNext = { code, status };
  }

  /** The host's step: a picker (here, always the same choice) and #288's host route. */
  private async hostStep(step: HostProjectStep): Promise<string | null> {
    this.steps.push(step);
    if (this.options.cancelPickers) return null;
    if (step.kind === "open-project") {
      const project = [...this.models.values()].find((model) => model.kind === "project");
      return project?.model_id ?? this.create("Example Threat Model", "workspace-example.yaml");
    }
    if (step.kind === "open-file") {
      const model_id = this.id("file");
      this.models.set(model_id, {
        model_id, kind: "file", name: "imported-model.yaml", editable: false,
        versions: [{ number: null, version: FILE_DIGEST, description: "Opened read-only from imported-model.yaml", created_at: this.tick(), data: "r1" }],
      });
      return model_id;
    }
    const from = step.from;
    if ("source_file" in from) return this.create(from.source_file.replace(/\.ya?ml$/, ""), from.source_file);
    if ("model_id" in from) return this.create(this.models.get(from.model_id)?.name.replace(/\.ya?ml$/, "") ?? "Project", this.models.get(from.model_id)?.name ?? "model");
    return this.create(from.name, `${from.name}.yaml`);
  }

  private create(name: string, source: string): string {
    const model_id = this.id("project");
    this.models.set(model_id, {
      model_id, kind: "project", name: `${name} (mock project)`, editable: true,
      versions: [{ number: 1, version: "v001", description: `Initial model, copied from ${source}`, created_at: this.tick(), data: "r1" }],
    });
    return model_id;
  }

  private id(kind: "project" | "file"): string {
    this.counter += 1;
    return `${kind}:${this.counter.toString(16).padStart(32, "0")}`;
  }

  private tick(): string {
    this.clock += 60_000;
    return new Date(this.clock).toISOString().replace(".000Z", "Z");
  }

  /** In-memory engine routes: #288's GET /workspace/* and #289's POST /reviews/*. */
  readonly fetch: typeof fetch = async (input, init) => {
    const url = new URL(typeof input === "string" ? input : input instanceof URL ? input.href : input.url);
    const headers = (init?.headers ?? {}) as Record<string, string>;
    const body = init?.body ? JSON.parse(String(init.body)) as Record<string, string> : {};
    this.requests.push({ path: url.pathname, body: init?.body ? body : Object.fromEntries(url.searchParams) });
    if (headers.Authorization !== `Bearer ${MOCK_TOKEN}`) return error(403, "permission_denied", "The host's session token is required.");
    if (url.pathname.startsWith("/workspace/")) return this.workspaceRoute(url);
    if (init?.method !== "POST") return error(404, "not_found", "Unknown operation.");
    if (this.failNext) {
      const { code, status } = this.failNext;
      this.failNext = undefined;
      const example = contract.errors.find((item) => item.error.code === code)?.error;
      const extra: Record<string, unknown> = { ...example };
      if (code === "revision_conflict") extra.current_revision = this.current(this.models.get(body.model_id))?.version ?? "v002";
      return json(status, { error: { message: `Mock ${code}.`, ...extra, code } });
    }
    const model = this.models.get(body.model_id);
    if (!model) return error(404, "not_found", "Model revision not found.");
    if (url.pathname === "/reviews/refresh") return this.refresh(model, body);
    if (url.pathname === "/reviews/context") return this.context(model, body);
    if (url.pathname === "/reviews/changes") return this.save(model, body);
    return error(404, "not_found", "Unknown operation.");
  };

  private workspaceRoute(url: URL): Response {
    if (url.pathname === "/workspace/models") {
      const models = [...this.models.values()].map((model) => this.entry(model));
      return json(200, { count: models.length, models, problems: [], schema_validation: false });
    }
    const model = this.models.get(url.searchParams.get("model_id") ?? "");
    if (!model) return error(404, "not_found", "This model is not open in the engine, or has no such version.");
    if (url.pathname === "/workspace/versions") {
      const current = this.current(model)!;
      return json(200, {
        model_id: model.model_id,
        revision: current.version,
        current_revision: current.version,
        versions: model.versions.map(({ data: _data, ...version }) => ({ ...version, parent_version: null, sha256: FILE_DIGEST.slice(7), summary: null })),
      });
    }
    return error(404, "not_found", "Unknown operation.");
  }

  private entry(model: MockModel) {
    const current = this.current(model)!;
    return {
      model_id: model.model_id, kind: model.kind, name: model.name, editable: model.editable,
      container: "ExampleModelProposed", created_at: model.versions[0].created_at,
      current_revision: current.version, version_count: model.versions.length,
      source: { file: model.name, sha256: FILE_DIGEST.slice(7), origin: model.kind === "file" ? "file" : "example" },
    };
  }

  private current(model: MockModel | undefined): MockVersion | undefined {
    return model?.versions[model.versions.length - 1];
  }

  private refresh(model: MockModel, body: Record<string, string>): Response {
    const version = model.versions.find((candidate) => candidate.version === body.revision);
    if (!version) return error(404, "not_found", "Model revision not found.");
    const answer = version.data === "r1" ? revisions.refresh_r1.response : contract.save.response;
    return json(200, retag(answer, model.model_id, version.version));
  }

  private context(model: MockModel, body: Record<string, string>): Response {
    const version = model.versions.find((candidate) => candidate.version === body.revision);
    if (!version) return error(404, "not_found", "Model revision not found.");
    const answer = version.data === "r1" ? contract.context.response : revisions.context_r2.response;
    if (body.route_id !== answer.route.id || body.threat_id !== answer.threat.id) {
      return error(422, "validation_error", "This route does not belong to the selected threat and revision.", { fields: [{ field: "route_id", message: "This route does not belong to the selected threat and revision." }] });
    }
    const tagged = retag(answer, model.model_id, version.version);
    // A read-only file and an older version are snapshots: the engine permits nothing on them.
    if (!model.editable || version !== this.current(model)) {
      tagged.permitted_actions = { submit_review: false, save_feasibility: false, save_impacts: false, correct_own_review: false, accept_proposal: false };
    }
    return json(200, tagged);
  }

  private save(model: MockModel, body: Record<string, string>): Response {
    if (!model.editable) return error(403, "permission_denied", "Create an editable copy before saving.");
    const current = this.current(model)!;
    if (body.expected_revision !== current.version) {
      return error(409, "revision_conflict", "A newer version was saved. Reload before retrying.", { current_revision: current.version });
    }
    const number = model.versions.length + 1;
    const version = `v${String(number).padStart(3, "0")}`;
    // #289's commit stores no description or summary yet (MODEL_WORKSPACE.md).
    model.versions.push({ number, version, description: null, created_at: this.tick(), data: "r2" });
    return json(200, retag(contract.save.response, model.model_id, version));
  }

  /** Adds a version as if another window saved it, for conflict demonstrations and tests. */
  addVersionElsewhere(modelId: string): string {
    const model = this.models.get(modelId)!;
    const number = model.versions.length + 1;
    const version = `v${String(number).padStart(3, "0")}`;
    model.versions.push({ number, version, description: "Saved from another window (mock)", created_at: this.tick(), data: "r2" });
    return version;
  }
}
