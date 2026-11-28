import fixture from "./fixtures/attack-pattern-table.json";
import {
  parseAttackPatternDetailResponse,
  parseAttackPatternTableResponse,
} from "./engine-attack-pattern-provider";
import type {
  AttackPatternDataProvider,
  AttackPatternDetailResponse,
  AttackPatternFacets,
  AttackPatternFilter,
  AttackPatternTableQuery,
  AttackPatternTableResponse,
  AttackPatternTableRow,
} from "./attack-pattern-types";
import { ATTACK_PATTERN_ENUMERATION_ORDER, ATTACK_PATTERN_FILTERS } from "./attack-pattern-types";

const TABLE_FIXTURE = parseAttackPatternTableResponse(fixture);

/** The engine's GET /attack-patterns answer for each row of the table fixture, by CAPEC id. */
export type AttackPatternDetailFixture = ReadonlyMap<string, AttackPatternDetailResponse>;

/** Loads the detail answers on first use, as a chunk of their own, outside the main bundle. */
export async function loadAttackPatternDetailFixture(): Promise<AttackPatternDetailFixture> {
  const module = await import("./fixtures/attack-pattern-details.json");
  return parseAttackPatternDetailFixture(module.default);
}

export function parseAttackPatternDetailFixture(value: unknown): AttackPatternDetailFixture {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("The attack-pattern detail fixture is not an object of answers");
  }
  return new Map(Object.entries(value).map(([id, answer]) => {
    const response = parseAttackPatternDetailResponse(answer);
    if (response.id !== id || !response.entry) {
      throw new Error(`The attack-pattern detail fixture has no entry for ${id}`);
    }
    return [id, response];
  }));
}

export class FixtureAttackPatternDataProvider implements AttackPatternDataProvider {
  readonly metadata = {
    source: "fixture" as const,
    notice: `${TABLE_FIXTURE.catalog.name} ${TABLE_FIXTURE.catalog.version} development fixture · `
      + `${TABLE_FIXTURE.catalog.attack_patterns} sample attack patterns, not the complete catalog`,
  };
  private details?: Promise<AttackPatternDetailFixture>;

  constructor(
    private readonly loadDetails: () => Promise<AttackPatternDetailFixture> = loadAttackPatternDetailFixture,
  ) {}

  async getTable(
    query: AttackPatternTableQuery,
    signal?: AbortSignal,
  ): Promise<AttackPatternTableResponse> {
    throwIfAborted(signal);
    // The engine's search also reads alternate terms, which only the detail answers carry.
    const details = query.search?.trim() ? await this.detailFixture() : undefined;
    throwIfAborted(signal);
    return applyAttackPatternQuery(TABLE_FIXTURE, query, details && alternateTerms(details));
  }

  async getAttackPattern(
    id: string,
    signal?: AbortSignal,
  ): Promise<AttackPatternDetailResponse | undefined> {
    throwIfAborted(signal);
    const details = await this.detailFixture();
    throwIfAborted(signal);
    const response = details.get(id);
    return response ? structuredClone(response) : undefined;
  }

  private detailFixture(): Promise<AttackPatternDetailFixture> {
    this.details ??= this.loadDetails().catch((error: unknown) => {
      this.details = undefined; // let a retry load the chunk again
      throw error;
    });
    return this.details;
  }
}

/** The engine's GET /attack-patterns/table semantics (engine/engine/core.py), over the fixture. */
export function applyAttackPatternQuery(
  source: AttackPatternTableResponse,
  query: AttackPatternTableQuery,
  alternateTerms: ReadonlyMap<string, readonly string[]> = new Map(),
): AttackPatternTableResponse {
  const copy = structuredClone(source);
  const search = query.search?.trim() || undefined;
  const searched = copy.rows.filter((row) => (
    matchesSearch(row, search, alternateTerms.get(row.id) ?? [])
  ));
  const matched = searched.filter((row) => matchesFilters(row, query));
  const ordered = sortedAttackPatterns(matched, query.sort, query.order === "desc");
  const rows = ordered.slice(query.offset, query.offset + query.limit);
  return {
    ...copy,
    query: {
      filters: Object.fromEntries(ATTACK_PATTERN_FILTERS.flatMap((key) => (
        query[key] ? [[key, query[key]]] : []
      ))),
      search: search ?? null,
      sort: query.sort,
      order: query.order,
      limit: query.limit,
      offset: query.offset,
    },
    total: matched.length,
    count: rows.length,
    rows,
    contextual_facets: contextualFacets(searched, query),
  };
}

/**
 * Id order by number; an enumeration in CAPEC's order, other values after it by name.
 * Rows without a value come last in both orders, and ties keep id order.
 */
export function sortedAttackPatterns(
  rows: readonly AttackPatternTableRow[],
  field: AttackPatternTableQuery["sort"],
  descending: boolean,
): AttackPatternTableRow[] {
  const byId = [...rows].sort((left, right) => capecNumber(left.id) - capecNumber(right.id));
  if (field === "id") return descending ? byId.reverse() : byId;
  const present = byId.filter((row) => row[field] !== null && row[field] !== "");
  const missing = byId.filter((row) => row[field] === null || row[field] === "");
  const semantic = ATTACK_PATTERN_ENUMERATION_ORDER[field] ?? [];
  present.sort((left, right) => {
    const comparison = semantic.length
      ? compareSemantic(String(left[field]), String(right[field]), semantic)
      : compare(casefold(String(left[field])), casefold(String(right[field])));
    return descending ? -comparison : comparison;
  });
  return [...present, ...missing];
}

function alternateTerms(details: AttackPatternDetailFixture): ReadonlyMap<string, readonly string[]> {
  return new Map([...details].map(([id, response]) => [id, response.entry?.alternate_terms ?? []]));
}

function matchesSearch(
  row: AttackPatternTableRow,
  search: string | undefined,
  terms: readonly string[],
): boolean {
  if (!search) return true;
  const text = [row.id, row.name, row.description, ...terms, ...row.weaknesses, ...row.attack_techniques];
  return casefold(text.join(" ")).includes(casefold(search));
}

function matchesFilters(
  row: AttackPatternTableRow,
  query: AttackPatternTableQuery,
  omit?: AttackPatternFilter,
): boolean {
  return ATTACK_PATTERN_FILTERS.every((key) => key === omit || !query[key] || row[key] === query[key]);
}

function contextualFacets(
  searched: readonly AttackPatternTableRow[],
  query: AttackPatternTableQuery,
): AttackPatternFacets {
  const facet = (key: AttackPatternFilter) => counts(
    searched.filter((row) => matchesFilters(row, query, key)),
    key,
  );
  return {
    abstraction: facet("abstraction"),
    status: facet("status"),
    likelihood: facet("likelihood"),
    severity: facet("severity"),
  };
}

function counts(
  rows: readonly AttackPatternTableRow[],
  key: AttackPatternFilter,
): Record<string, number> {
  const result: Record<string, number> = {};
  for (const row of rows) {
    const value = row[key];
    if (value) result[value] = (result[value] ?? 0) + 1;
  }
  return Object.fromEntries(Object.entries(result).sort(([left], [right]) => compare(left, right)));
}

function compareSemantic(left: string, right: string, order: readonly string[]): number {
  const leftRank = order.indexOf(left);
  const rightRank = order.indexOf(right);
  const knownLeft = leftRank >= 0 ? leftRank : order.length;
  const knownRight = rightRank >= 0 ? rightRank : order.length;
  return knownLeft - knownRight || compare(casefold(left), casefold(right));
}

function capecNumber(id: string): number {
  const number = Number(id.replace(/^CAPEC-/i, ""));
  return Number.isFinite(number) ? number : Number.MAX_SAFE_INTEGER;
}

function casefold(value: string): string {
  return value.toLocaleLowerCase("und");
}

function compare(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

function throwIfAborted(signal?: AbortSignal): void {
  if (signal?.aborted) throw new DOMException("The request was aborted", "AbortError");
}
