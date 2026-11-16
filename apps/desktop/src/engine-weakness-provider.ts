import { DEFAULT_ENGINE_URL } from "./engine";
import type {
  CweFieldValue,
  WeaknessAssertion,
  WeaknessCatalog,
  WeaknessDataProvider,
  WeaknessDetailResponse,
  WeaknessEntry,
  WeaknessFacets,
  WeaknessObjects,
  WeaknessTableQuery,
  WeaknessTableResponse,
  WeaknessTableRow,
} from "./weakness-types";

export class EngineWeaknessDataProvider implements WeaknessDataProvider {
  readonly metadata = {
    source: "engine" as const,
    notice: "CWE weaknesses from the local engine",
    detailLevel: "full" as const,
  };

  constructor(
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async getTable(query: WeaknessTableQuery, signal?: AbortSignal): Promise<WeaknessTableResponse> {
    const parameters: Record<string, string | undefined> = {
      search: query.search,
      abstraction: query.abstraction,
      structure: query.structure,
      status: query.status,
      usage: query.usage,
      sort: query.sort,
      order: query.order,
      limit: String(query.limit),
      offset: String(query.offset),
    };
    return parseWeaknessTableResponse(
      await this.request("/weaknesses/table", parameters, signal),
    );
  }

  async getWeakness(
    id: string,
    signal?: AbortSignal,
  ): Promise<WeaknessDetailResponse | undefined> {
    const response = parseWeaknessDetailResponse(
      await this.request("/weaknesses", { id }, signal),
    );
    return response.entry ? response : undefined;
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
        // Retain the status when the engine did not return its normal JSON error.
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

export function parseWeaknessTableResponse(value: unknown): WeaknessTableResponse {
  if (!isObject(value) || !isCatalog(value.catalog) || !isObject(value.query)
    || !Array.isArray(value.rows) || !value.rows.every(isTableRow)
    || !isFacets(value.facets) || !isFacets(value.contextual_facets)
    || !isNonnegativeInteger(value.total) || !isNonnegativeInteger(value.count)
    || value.count !== value.rows.length || value.count > value.total
    || !isStringRecord(value.query.filters) || optionalString(value.query.search) === false
    || typeof value.query.sort !== "string"
    || (value.query.order !== "asc" && value.query.order !== "desc")
    || !optionalPositiveInteger(value.query.limit)
    || !isNonnegativeInteger(value.query.offset)) {
    throw new Error("Engine returned a malformed weakness table response");
  }
  return value as unknown as WeaknessTableResponse;
}

export function parseWeaknessDetailResponse(value: unknown): WeaknessDetailResponse {
  if (!isObject(value) || !isCatalog(value.catalog) || typeof value.id !== "string"
    || !(value.entry === null || isEntry(value.entry))
    || !(value.objects === null || isObjects(value.objects))) {
    throw new Error("Engine returned a malformed weakness detail response");
  }
  return value as unknown as WeaknessDetailResponse;
}

function isCatalog(value: unknown): value is WeaknessCatalog {
  return isObject(value)
    && ["name", "version", "date", "file", "sha256", "notice", "license", "terms_url"]
      .every((key) => typeof value[key] === "string")
    && optionalString(value.schema)
    && ["weaknesses", "categories", "views", "references", "unknown_fields"]
      .every((key) => isNonnegativeInteger(value[key]));
}

function isTableRow(value: unknown): value is WeaknessTableRow {
  return isObject(value)
    && ["id", "weakness", "name", "status", "description", "url"]
      .every((key) => typeof value[key] === "string")
    && optionalString(value.abstraction) && optionalString(value.structure)
    && optionalString(value.usage) && optionalString(value.likelihood)
    && ["attack_patterns", "observed_examples", "mitigations"]
      .every((key) => isNonnegativeInteger(value[key]));
}

function isFacets(value: unknown): value is WeaknessFacets {
  return isObject(value)
    && ["abstraction", "structure", "status", "usage"]
      .every((key) => isCountRecord(value[key]));
}

function isEntry(value: unknown): value is WeaknessEntry {
  return isObject(value)
    && ["id", "kind", "name", "status", "description", "url"]
      .every((key) => typeof value[key] === "string")
    && optionalString(value.abstraction) && optionalString(value.structure)
    && optionalString(value.view_type) && optionalString(value.usage)
    && optionalString(value.likelihood) && isStringArray(value.alternate_terms)
    && isStringArray(value.attack_patterns)
    && Array.isArray(value.observed_examples)
    && value.observed_examples.every((example) => isObject(example)
      && typeof example.reference === "string"
      && typeof example.description === "string"
      && optionalString(example.link))
    && isNonnegativeInteger(value.mitigations)
    && isObject(value.fields) && Object.values(value.fields).every(isFieldValue);
}

function isObjects(value: unknown): value is WeaknessObjects {
  return isObject(value)
    && ["parties", "weaknesses", "attack_patterns", "vulnerabilities"]
      .every((key) => Array.isArray(value[key]) && value[key].every(isObject))
    && Array.isArray(value.assertions) && value.assertions.every(isAssertion);
}

function isAssertion(value: unknown): value is WeaknessAssertion {
  return isObject(value)
    && [
      "id",
      "name",
      "subject",
      "predicate",
      "object",
      "assertion_status",
      "asserted_by",
      "generated_by",
    ].every((key) => typeof value[key] === "string")
    && optionalString(value.description)
    && (value.evidence === undefined || isStringArray(value.evidence));
}

function isFieldValue(value: unknown): value is CweFieldValue {
  if (value === null || ["string", "number", "boolean"].includes(typeof value)) return true;
  if (Array.isArray(value)) return value.every(isFieldValue);
  return isObject(value) && Object.values(value).every(isFieldValue);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function optionalString(value: unknown): value is string | null | undefined {
  return value === null || value === undefined || typeof value === "string";
}

function optionalPositiveInteger(value: unknown): value is number | null {
  return value === null || (isNonnegativeInteger(value) && value > 0);
}

function isNonnegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isStringRecord(value: unknown): value is Record<string, string> {
  return isObject(value) && Object.values(value).every((item) => typeof item === "string");
}

function isCountRecord(value: unknown): value is Record<string, number> {
  return isObject(value) && Object.values(value).every(isNonnegativeInteger);
}
