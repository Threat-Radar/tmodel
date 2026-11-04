import { DEFAULT_ENGINE_URL } from "./engine";
import type {
  LibraryDataProvider,
  LibraryRecordDetails,
  LibraryTableQuery,
  LibraryTableResponse,
  LibraryTableRow,
} from "./library-types";

interface LibraryRecordResponse {
  count: number;
  records: LibraryRecordDetails[];
}

export class EngineLibraryDataProvider implements LibraryDataProvider {
  readonly metadata = {
    source: "engine" as const,
    notice: "Library documents from the local engine",
    supportsQueries: true,
  };

  constructor(
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async getTable(query: LibraryTableQuery, signal?: AbortSignal): Promise<LibraryTableResponse> {
    const parameters: Record<string, string | undefined> = {
      search: query.search,
      type: query.type,
      status: query.status,
      topic: query.topic,
      sort: query.sort,
      order: query.order,
    };
    return parseTableResponse(await this.request("/library/table", parameters, signal));
  }

  async getRecord(id: string, signal?: AbortSignal): Promise<LibraryRecordDetails | undefined> {
    const payload = parseRecordResponse(await this.request("/library", { id }, signal));
    return payload.records[0];
  }

  private async request(
    path: string,
    parameters: Readonly<Record<string, string | undefined>>,
    signal?: AbortSignal,
  ): Promise<unknown> {
    const url = new URL(path, `${this.baseUrl.replace(/\/$/, "")}/`);
    for (const [name, value] of Object.entries(parameters)) {
      if (value !== undefined && value !== "") url.searchParams.set(name, value);
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

export function parseTableResponse(value: unknown): LibraryTableResponse {
  if (!isObject(value) || !isObject(value.library) || !isObject(value.query)
    || !Array.isArray(value.rows) || !isFacets(value.facets)
    || typeof value.total !== "number" || typeof value.count !== "number"
    || typeof value.library.digest !== "string" || typeof value.library.count !== "number"
    || !isStringArray(value.library.problems)
    || !isObject(value.query.filters) || typeof value.query.sort !== "string"
    || (value.query.order !== "asc" && value.query.order !== "desc")
    || (value.contextual_facets !== undefined && !isFacets(value.contextual_facets))
    || !value.rows.every(isTableRow)) {
    throw new Error("Engine returned a malformed library table response");
  }
  const response = value as unknown as LibraryTableResponse;
  return value.contextual_facets === undefined
    ? { ...response, contextual_facets: response.facets }
    : response;
}

function parseRecordResponse(value: unknown): LibraryRecordResponse {
  if (!isObject(value) || typeof value.count !== "number" || !Array.isArray(value.records)
    || !value.records.every(isRecordDetails)) {
    throw new Error("Engine returned a malformed library record response");
  }
  return value as unknown as LibraryRecordResponse;
}

function isTableRow(value: unknown): value is LibraryTableRow {
  return isObject(value)
    && ["id", "title", "type", "shelf", "status"].every((key) => typeof value[key] === "string")
    && optionalString(value.short_title) && optionalString(value.maturity)
    && optionalString(value.date) && optionalString(value.publisher)
    && optionalString(value.topic) && optionalString(value.url) && optionalString(value.profile)
    && isStringArray(value.tags) && isNonnegativeInteger(value.artifacts)
    && isNonnegativeInteger(value.reviewed_artifacts)
    && value.reviewed_artifacts <= value.artifacts;
}

function isRecordDetails(value: unknown): value is LibraryRecordDetails {
  return isObject(value)
    && ["id", "title", "body", "type", "status"].every((key) => typeof value[key] === "string")
    && optionalString(value.topic) && optionalString(value.date)
    && optionalString(value.publisher) && isStringArray(value.authors)
    && optionalString(value.version) && optionalString(value.maturity)
    && isStringArray(value.tags) && isObject(value.content)
    && optionalString(value.content.url) && optionalString(value.profile)
    && Array.isArray(value.artifacts) && value.artifacts.every(isArtifact)
    && (value.usefulness === null || isUsefulness(value.usefulness))
    && isStringRecord(value.applicability);
}

function isArtifact(value: unknown): boolean {
  return isObject(value)
    && typeof value.kind === "string"
    && typeof value.path === "string"
    && typeof value.coverage === "string"
    && typeof value.reviewed_by === "string"
    && optionalString(value.generated_from)
    && typeof value.reviewed === "boolean";
}

function isUsefulness(value: unknown): boolean {
  return isObject(value)
    && typeof value.verdict === "string"
    && optionalString(value.reason)
    && optionalString(value.assessed);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function optionalString(value: unknown): value is string | null | undefined {
  return value === null || value === undefined || typeof value === "string";
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isStringRecord(value: unknown): value is Record<string, string> {
  return isObject(value) && Object.values(value).every((item) => typeof item === "string");
}

function isFacet(value: unknown): value is Record<string, number> {
  return isObject(value) && Object.values(value).every((count) => typeof count === "number");
}

function isFacets(value: unknown): boolean {
  return isObject(value) && isFacet(value.type) && isFacet(value.status) && isFacet(value.topic);
}

function isNonnegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}
