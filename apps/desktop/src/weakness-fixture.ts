import fixture from "./fixtures/weakness-table.json";
import { parseWeaknessTableResponse } from "./engine-weakness-provider";
import type {
  WeaknessDataProvider,
  WeaknessDetailResponse,
  WeaknessFacets,
  WeaknessFilter,
  WeaknessTableQuery,
  WeaknessTableResponse,
  WeaknessTableRow,
} from "./weakness-types";
import { WEAKNESS_ENUMERATION_ORDER, WEAKNESS_FILTERS } from "./weakness-types";

const TABLE_FIXTURE = parseWeaknessTableResponse(fixture);

export class FixtureWeaknessDataProvider implements WeaknessDataProvider {
  readonly metadata = {
    source: "fixture" as const,
    notice: "CWE 4.20 development fixture · 9 sample weaknesses, not the complete catalog",
    detailLevel: "row-only" as const,
  };

  async getTable(query: WeaknessTableQuery, signal?: AbortSignal): Promise<WeaknessTableResponse> {
    throwIfAborted(signal);
    return applyWeaknessQuery(TABLE_FIXTURE, query);
  }

  async getWeakness(
    _id: string,
    signal?: AbortSignal,
  ): Promise<WeaknessDetailResponse | undefined> {
    throwIfAborted(signal);
    return undefined;
  }
}

export function applyWeaknessQuery(
  source: WeaknessTableResponse,
  query: WeaknessTableQuery,
): WeaknessTableResponse {
  const searched = source.rows.filter((row) => matchesSearch(row, query.search));
  const matched = searched.filter((row) => matchesFilters(row, query));
  const ordered = sortedWeaknesses(matched, query.sort, query.order === "desc");
  const rows = ordered.slice(query.offset, query.offset + query.limit);
  return {
    ...structuredClone(source),
    query: {
      filters: Object.fromEntries(WEAKNESS_FILTERS.flatMap((key) => (
        query[key] ? [[key, query[key]]] : []
      ))),
      search: query.search ?? null,
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

export function sortedWeaknesses(
  rows: readonly WeaknessTableRow[],
  field: WeaknessTableQuery["sort"],
  descending: boolean,
): WeaknessTableRow[] {
  const byId = [...rows].sort((left, right) => weaknessNumber(left.id) - weaknessNumber(right.id));
  if (field === "id") return descending ? byId.reverse() : byId;
  const present = byId.filter((row) => row[field] !== null && row[field] !== "");
  const missing = byId.filter((row) => row[field] === null || row[field] === "");
  const semantic = WEAKNESS_ENUMERATION_ORDER[field] ?? [];
  present.sort((left, right) => {
    const comparison = semantic.length
      ? compareSemantic(String(left[field]), String(right[field]), semantic)
      : compare(casefold(String(left[field])), casefold(String(right[field])));
    return descending ? -comparison : comparison;
  });
  return [...present, ...missing];
}

function matchesSearch(row: WeaknessTableRow, search?: string): boolean {
  if (!search) return true;
  return casefold([row.id, row.name, row.description].join(" ")).includes(casefold(search));
}

function matchesFilters(
  row: WeaknessTableRow,
  query: WeaknessTableQuery,
  omit?: WeaknessFilter,
): boolean {
  return WEAKNESS_FILTERS.every((key) => key === omit || !query[key] || row[key] === query[key]);
}

function contextualFacets(
  searched: readonly WeaknessTableRow[],
  query: WeaknessTableQuery,
): WeaknessFacets {
  return {
    abstraction: counts(searched.filter((row) => matchesFilters(row, query, "abstraction")), "abstraction"),
    structure: counts(searched.filter((row) => matchesFilters(row, query, "structure")), "structure"),
    status: counts(searched.filter((row) => matchesFilters(row, query, "status")), "status"),
    usage: counts(searched.filter((row) => matchesFilters(row, query, "usage")), "usage"),
  };
}

function counts(
  rows: readonly WeaknessTableRow[],
  key: WeaknessFilter,
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

function weaknessNumber(id: string): number {
  const number = Number(id.replace(/^CWE-/i, ""));
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
