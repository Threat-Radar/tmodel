import { DEFAULT_ENGINE_URL } from "./engine";
import type {
  AttackPatternAssertion,
  AttackPatternCatalog,
  AttackPatternDataProvider,
  AttackPatternDetailResponse,
  AttackPatternEntry,
  AttackPatternFacets,
  AttackPatternObjects,
  AttackPatternReference,
  AttackPatternTableQuery,
  AttackPatternTableResponse,
  AttackPatternTableRow,
} from "./attack-pattern-types";
import type { CweFieldValue } from "./weakness-types";

export class EngineAttackPatternDataProvider implements AttackPatternDataProvider {
  readonly metadata = {
    source: "engine" as const,
    notice: "CAPEC attack patterns from the local engine",
  };

  constructor(
    private readonly baseUrl = DEFAULT_ENGINE_URL,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async getTable(
    query: AttackPatternTableQuery,
    signal?: AbortSignal,
  ): Promise<AttackPatternTableResponse> {
    const parameters: Record<string, string | undefined> = {
      search: query.search,
      abstraction: query.abstraction,
      status: query.status,
      likelihood: query.likelihood,
      severity: query.severity,
      sort: query.sort,
      order: query.order,
      limit: String(query.limit),
      offset: String(query.offset),
    };
    return parseAttackPatternTableResponse(
      await this.request("/attack-patterns/table", parameters, signal),
    );
  }

  async getAttackPattern(
    id: string,
    signal?: AbortSignal,
  ): Promise<AttackPatternDetailResponse | undefined> {
    const response = parseAttackPatternDetailResponse(
      await this.request("/attack-patterns", { id }, signal),
    );
    // The engine writes the id it was asked for as CAPEC-N; never show another entry's fields.
    if (capecNumber(response.id) === undefined || capecNumber(response.id) !== capecNumber(id)) {
      throw new Error(`Engine answered with ${response.id} for ${id}`);
    }
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
        // Keep the status when the engine did not answer with its usual JSON error.
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

export function parseAttackPatternTableResponse(value: unknown): AttackPatternTableResponse {
  if (!isObject(value) || !isCatalog(value.catalog) || !isObject(value.query)
    || !Array.isArray(value.rows) || !value.rows.every(isTableRow)
    || !isFacets(value.facets) || !isFacets(value.contextual_facets)
    || !isNonnegativeInteger(value.total) || !isNonnegativeInteger(value.count)
    || value.count !== value.rows.length || value.count > value.total
    || !isStringRecord(value.query.filters) || !optionalString(value.query.search)
    || typeof value.query.sort !== "string"
    || (value.query.order !== "asc" && value.query.order !== "desc")
    || !optionalPositiveInteger(value.query.limit)
    || !isNonnegativeInteger(value.query.offset)) {
    throw new Error("Engine returned a malformed attack-pattern table response");
  }
  return value as unknown as AttackPatternTableResponse;
}

export function parseAttackPatternDetailResponse(value: unknown): AttackPatternDetailResponse {
  // The engine gives `references` exactly when it found the entry, and `objects` only with one.
  if (!isObject(value) || !isCatalog(value.catalog) || typeof value.id !== "string"
    || !(value.entry === null || isEntry(value.entry))
    || !(value.references === null
      || (Array.isArray(value.references) && value.references.every(isReference)))
    || (value.entry === null) !== (value.references === null)
    || !(value.objects === null || (value.entry !== null && isObjects(value.objects)))) {
    throw new Error("Engine returned a malformed attack-pattern detail response");
  }
  return value as unknown as AttackPatternDetailResponse;
}

/** The number in a CAPEC id as the engine accepts it: CAPEC-66, capec-66 or 66. */
function capecNumber(id: string): number | undefined {
  const match = /^(?:capec-)?([0-9]+)$/i.exec(id.trim());
  return match ? Number(match[1]) : undefined;
}

function isCatalog(value: unknown): value is AttackPatternCatalog {
  return isObject(value)
    && ["name", "version", "date", "file", "sha256", "notice", "license", "terms_url"]
      .every((key) => typeof value[key] === "string")
    && optionalString(value.schema)
    && ["attack_patterns", "categories", "views", "references", "unknown_fields"]
      .every((key) => isNonnegativeInteger(value[key]));
}

function isTableRow(value: unknown): value is AttackPatternTableRow {
  return isObject(value)
    && ["id", "attack_pattern", "name", "status", "description", "url"]
      .every((key) => typeof value[key] === "string")
    && optionalString(value.abstraction) && optionalString(value.likelihood)
    && optionalString(value.severity)
    && isStringArray(value.weaknesses) && isStringArray(value.attack_techniques)
    && ["related_attack_patterns", "steps", "mitigations", "examples"]
      .every((key) => isNonnegativeInteger(value[key]));
}

function isFacets(value: unknown): value is AttackPatternFacets {
  return isObject(value)
    && ["abstraction", "status", "likelihood", "severity"]
      .every((key) => isCountRecord(value[key]));
}

function isEntry(value: unknown): value is AttackPatternEntry {
  return isObject(value)
    && ["id", "kind", "name", "status", "description", "url"]
      .every((key) => typeof value[key] === "string")
    && optionalString(value.abstraction) && optionalString(value.view_type)
    && optionalString(value.likelihood) && optionalString(value.severity)
    && isStringArray(value.alternate_terms)
    && Array.isArray(value.related_attack_patterns)
    && value.related_attack_patterns.every((related) => isObject(related)
      && typeof related.nature === "string" && typeof related.id === "string")
    && isStringArray(value.weaknesses) && isStringArray(value.attack_techniques)
    && ["steps", "mitigations", "examples"].every((key) => isNonnegativeInteger(value[key]))
    && isObject(value.fields) && Object.values(value.fields).every(isFieldValue);
}

function isReference(value: unknown): value is AttackPatternReference {
  return isObject(value)
    && typeof value.id === "string" && typeof value.resolved === "boolean"
    && isStringArray(value.authors)
    && ["section", "title", "edition", "publication", "publisher", "year", "month", "day", "url",
      "url_date"].every((key) => optionalString(value[key]));
}

function isObjects(value: unknown): value is AttackPatternObjects {
  return isObject(value)
    && ["parties", "attack_patterns", "weaknesses"]
      .every((key) => Array.isArray(value[key]) && value[key].every(isObject))
    && Array.isArray(value.assertions) && value.assertions.every(isAssertion);
}

function isAssertion(value: unknown): value is AttackPatternAssertion {
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
    ].every((key) => typeof value[key] === "string");
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
