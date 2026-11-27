// #290: threat model projects, as #288 provides them (engine/MODEL_WORKSPACE.md),
// in the team's design for saving and reopening threat models. A project is a
// local folder the user picks (original.yaml, project.json, versions/v001.yaml,
// v002.yaml, ...); a saved YAML file can also be opened read-only. The engine
// manages both and the app only ever sees ids: `project:<32 hex>` with versions
// v001, v002, ..., or `file:<32 hex>` with one `sha256:` revision.
//
// The app calls #288's three GET routes with the host's token; choosing a folder
// or file is the host's step (project-host.ts). A version's views come from
// #289's refreshModel, and Save New Version is #289's saveModelChanges, which
// commits through #288: #288 has no save route of its own.

import { DEFAULT_ENGINE_URL } from "./engine";
import type { HostProjectStep, ProjectHost, ProjectStart } from "./project-host";
import { NO_HOST_REASON } from "./project-host";
import type { ReviewSessionSource } from "./review-client";
import { isAbort } from "./review-client";
import { malformed, ReviewApiError, reviewErrorFromResponse } from "./review-contract";
import type { RiskCalculation } from "./risk-calculation";

export interface ProjectSummary {
  id: string;
  name: string;
  /** A project (versions, editable) or a file opened read-only. */
  kind: "project" | "file";
  editable: boolean;
}

/** A version's risk, grouped by the engine's own impact categories. */
export interface VersionRiskSummary {
  /** The highest derived risk per category, null when none is calculated. */
  categories: readonly { category: string; highest: number | null }[];
  /** How many assessments it covers, when the summary says. */
  assessments: number | null;
  incomplete: number | null;
}

export interface ProjectVersion {
  /** Opaque version id: v004, or a file's sha256 revision. */
  id: string;
  /** The version's number for display ("Version 4"); null for a file. */
  number: number | null;
  description: string | null;
  /** When the version was saved, as the workspace records it. */
  date: string | null;
  riskSummary: VersionRiskSummary | null;
  current: boolean;
}

export interface ProjectVersions {
  project: ProjectSummary;
  /** Oldest first, exactly one current. A save never overwrites a version. */
  versions: readonly ProjectVersion[];
}

/** What a new project starts from; its original.yaml keeps it unmodified. */
export type ProjectSource =
  /** A bundled example, by the file name GET /models lists. */
  | { kind: "example"; file: string; title: string }
  /** A file opened read-only, by its `file:` model id. */
  | { kind: "file"; modelId: string }
  /** An imported model's text, such as POST /import/sbom's model_text. */
  | { kind: "model-text"; name: string; text: string };

export type WorkspaceStatus = { available: true } | { available: false; reason: string };

export interface ProjectWorkspaceProvider {
  status(): WorkspaceStatus;
  /** Creates a project in a folder the user chooses; null when the user cancels. */
  createProject(source: ProjectSource): Promise<ProjectVersions | null>;
  /** Opens a project folder the user chooses; null when the user cancels. */
  openProject(): Promise<ProjectVersions | null>;
  /** Opens a saved threat model file the user chooses, read-only; null when the user cancels. */
  openThreatModel(): Promise<ProjectVersions | null>;
  /** A model's versions, with description, date and risk summary. */
  listVersions(modelId: string): Promise<ProjectVersions>;
}

export class ProjectWorkspaceError extends Error {
  constructor(readonly code: string, message: string) {
    super(message);
    this.name = "ProjectWorkspaceError";
  }
}

/** #288's provider: the host's picker for paths, then the webview's GET routes. */
export class EngineProjectWorkspace implements ProjectWorkspaceProvider {
  constructor(private readonly host: ProjectHost, private readonly client: WorkspaceClient) {}

  status(): WorkspaceStatus {
    return this.host.session() ? { available: true } : { available: false, reason: NO_HOST_REASON };
  }

  createProject(source: ProjectSource): Promise<ProjectVersions | null> {
    const from: ProjectStart = source.kind === "example" ? { source_file: source.file }
      : source.kind === "file" ? { model_id: source.modelId }
      : { model_text: source.text, name: source.name };
    return this.step({ kind: "create-project", from });
  }

  openProject(): Promise<ProjectVersions | null> {
    return this.step({ kind: "open-project" });
  }

  openThreatModel(): Promise<ProjectVersions | null> {
    return this.step({ kind: "open-file" });
  }

  async listVersions(modelId: string): Promise<ProjectVersions> {
    const [models, versions] = await Promise.all([this.client.listModels(), this.client.versions(modelId)]);
    const entry = models.find((model) => model.model_id === modelId);
    if (!entry) throw new ProjectWorkspaceError("not_found", "This model is not open in the engine.");
    return toProjectVersions(entry, versions);
  }

  private async step(step: HostProjectStep): Promise<ProjectVersions | null> {
    const modelId = await this.host.hostProjectStep(step);
    return modelId === null ? null : this.listVersions(modelId);
  }
}

/** A model the engine has open: GET /workspace/models' entries. */
export interface WorkspaceModel {
  model_id: string;
  kind: "project" | "file";
  name: string;
  editable: boolean;
  current_revision: string;
}

export interface WorkspaceVersion {
  number: number | null;
  version: string;
  description: string | null;
  created_at: string | null;
  summary: unknown;
}

export interface WorkspaceVersions {
  model_id: string;
  current_revision: string;
  versions: WorkspaceVersion[];
}

/** #288's routes the webview may call, each with the host's bearer token. */
export class WorkspaceClient {
  constructor(
    private readonly session: ReviewSessionSource,
    private readonly baseUrl: string = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async listModels(): Promise<WorkspaceModel[]> {
    return parseWorkspaceModels(await this.get("/workspace/models", {}));
  }

  async versions(modelId: string): Promise<WorkspaceVersions> {
    return parseWorkspaceVersions(await this.get("/workspace/versions", { model_id: modelId }), modelId);
  }

  private async get(path: string, query: Record<string, string>): Promise<unknown> {
    const session = this.session.current();
    if (!session) throw new ReviewApiError("permission_denied", "The host's session token is required.");
    const url = new URL(path, `${this.baseUrl.replace(/\/$/, "")}/`);
    for (const [name, value] of Object.entries(query)) url.searchParams.set(name, value);
    let response: Response;
    try {
      response = await this.fetchImpl(url, { headers: { Authorization: `Bearer ${session.token}` } });
    } catch (error) {
      if (isAbort(error)) throw error;
      throw new ReviewApiError("network_error", "Could not reach the local engine.");
    }
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      if (!response.ok) throw reviewErrorFromResponse(response.status, undefined);
      throw malformed("it is not JSON");
    }
    if (!response.ok) throw reviewErrorFromResponse(response.status, body);
    return body;
  }
}

export function parseWorkspaceModels(value: unknown): WorkspaceModel[] {
  if (!isRecord(value) || !Array.isArray(value.models)) throw malformed("the open models are not a list");
  return value.models.map((model) => {
    if (!isRecord(model) || typeof model.model_id !== "string" || (model.kind !== "project" && model.kind !== "file")
      || typeof model.name !== "string" || typeof model.editable !== "boolean" || typeof model.current_revision !== "string") {
      throw malformed("an open model is incomplete");
    }
    return {
      model_id: model.model_id,
      kind: model.kind,
      name: model.name,
      editable: model.editable,
      current_revision: model.current_revision,
    };
  });
}

export function parseWorkspaceVersions(value: unknown, modelId: string): WorkspaceVersions {
  if (!isRecord(value) || value.model_id !== modelId || typeof value.current_revision !== "string" || !Array.isArray(value.versions)) {
    throw malformed("the version list names another model");
  }
  return {
    model_id: modelId,
    current_revision: value.current_revision,
    versions: value.versions.map((version) => {
      if (!isRecord(version) || typeof version.version !== "string"
        || !(version.number === null || Number.isInteger(version.number))
        || !(version.description === null || version.description === undefined || typeof version.description === "string")
        || !(version.created_at === null || version.created_at === undefined || typeof version.created_at === "string")) {
        throw malformed("a version is incomplete");
      }
      return {
        number: version.number as number | null,
        version: version.version,
        description: (version.description ?? null) as string | null,
        created_at: (version.created_at ?? null) as string | null,
        summary: version.summary ?? null,
      };
    }),
  };
}

/** The screens' view of one open model: its versions, oldest first, the current one marked. */
export function toProjectVersions(model: WorkspaceModel, versions: WorkspaceVersions): ProjectVersions {
  return checkProjectVersions({
    project: { id: model.model_id, name: model.name, kind: model.kind, editable: model.editable },
    versions: versions.versions.map((version) => ({
      id: version.version,
      number: version.number,
      description: version.description,
      date: version.created_at,
      riskSummary: riskSummaryFromMetadata(version.summary),
      current: version.version === versions.current_revision,
    })),
  });
}

/**
 * A summary the version recorded, when it groups derived risk by impact
 * category; the engine stores whatever summary it was given, so any other
 * shape is not shown.
 */
export function riskSummaryFromMetadata(summary: unknown): VersionRiskSummary | null {
  if (!isRecord(summary) || !isRecord(summary.derived_risk)) return null;
  const entries = Object.entries(summary.derived_risk);
  if (entries.length === 0 || !entries.every(([, value]) => value === null || (typeof value === "number" && Number.isFinite(value)))) return null;
  return { categories: entries.map(([category, highest]) => ({ category, highest: highest as number | null })), assessments: null, incomplete: null };
}

/** Refuses a version list the screens cannot show truthfully. */
export function checkProjectVersions(value: ProjectVersions): ProjectVersions {
  const ids = value.versions.map((version) => version.id);
  if (!value.project.id || value.versions.length === 0 || new Set(ids).size !== ids.length
    || ids.some((id) => !id) || value.versions.filter((version) => version.current).length !== 1) {
    throw new ProjectWorkspaceError("workspace_failure", "The project workspace returned an inconsistent version list.");
  }
  return value;
}

export function currentVersion(versions: ProjectVersions): ProjectVersion {
  const current = versions.versions.find((version) => version.current);
  if (!current) throw new ProjectWorkspaceError("workspace_failure", "The project has no current version.");
  return current;
}

export function findVersion(versions: ProjectVersions | undefined, id: string): ProjectVersion | undefined {
  return versions?.versions.find((version) => version.id === id);
}

/** "Version 4"; a read-only file's one revision is "Opened file". */
export function versionLabel(version: Pick<ProjectVersion, "id" | "number">): string {
  if (version.id.startsWith("sha256:")) return "Opened file";
  return version.number === null ? `Version ${version.id}` : `Version ${version.number}`;
}

export function versionOptionLabel(version: ProjectVersion): string {
  return version.current && !version.id.startsWith("sha256:") ? `${versionLabel(version)} (Current)` : versionLabel(version);
}

/**
 * The version-level summary of an engine risk answer: its own categories, in
 * its own order, each with the highest value any assessment derived. Nothing is
 * calculated here beyond choosing that highest value.
 */
export function riskSummaryOf(risk: RiskCalculation): VersionRiskSummary {
  const categories: { category: string; highest: number | null }[] = [];
  for (const assessment of risk.assessments) {
    for (const [category, value] of Object.entries(assessment.derived_risk) as [string, number | null][]) {
      let entry = categories.find((item) => item.category === category);
      if (!entry) {
        entry = { category, highest: null };
        categories.push(entry);
      }
      if (value !== null && (entry.highest === null || value > entry.highest)) entry.highest = value;
    }
  }
  return {
    categories,
    assessments: risk.assessments.length,
    incomplete: risk.assessments.filter((assessment) => !assessment.complete).length,
  };
}

export function riskSummaryText(summary: VersionRiskSummary | null): string {
  if (!summary) return "Not recorded";
  if (summary.assessments === 0) return "No risk assessments";
  const values = summary.categories
    .map(({ category, highest }) => `${categoryLabel(category)} ${highest === null ? "not calculated" : highest}`)
    .join(" · ");
  if (summary.assessments === null) return `${values} (recorded with the version)`;
  const count = `${summary.assessments} ${summary.assessments === 1 ? "assessment" : "assessments"}`;
  const incomplete = summary.incomplete ? `, ${summary.incomplete} incomplete` : "";
  return `${values} (highest of ${count}${incomplete})`;
}

export function categoryLabel(category: string): string {
  const words = category.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
