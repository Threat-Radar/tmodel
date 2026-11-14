import { parseTableResponse } from "./engine-library-provider";
import { detailsFromRow } from "./library-fixture";
import type {
  LibraryDataProvider,
  LibraryFacets,
  LibraryRecordDetails,
  LibraryTableQuery,
  LibraryTableResponse,
  LibraryTableRow,
} from "./library-types";

/** Complete published table with the engine's filtering performed in-browser. */
export class StaticLibraryDataProvider implements LibraryDataProvider {
  readonly metadata = {
    source: "static-preview" as const,
    notice: "Published reference library · read-only preview",
    supportsQueries: true,
  };
  private tablePromise?: Promise<LibraryTableResponse>;

  constructor(
    private readonly tableUrl: string,
    private readonly fetchImpl: typeof fetch = (input, init) => globalThis.fetch(input, init),
  ) {}

  async getTable(query: LibraryTableQuery, signal?: AbortSignal): Promise<LibraryTableResponse> {
    throwIfAborted(signal);
    const source = await this.table();
    throwIfAborted(signal);
    const searched = source.rows.filter((row) => matchesSearch(row, query.search));
    const matched = searched.filter((row) => matchesFilters(row, query));
    const rows = sorted(matched, query.sort, query.order === "desc");
    return {
      ...source,
      query: {
        filters: Object.fromEntries(["type", "status", "topic"].flatMap((key) => {
          const value = query[key as "type" | "status" | "topic"];
          return value ? [[key, value]] : [];
        })),
        search: query.search ?? null,
        sort: query.sort,
        order: query.order,
        limit: null,
        offset: 0,
      },
      total: rows.length,
      count: rows.length,
      rows,
      contextual_facets: contextualFacets(searched, query),
    };
  }

  async getRecord(id: string, signal?: AbortSignal): Promise<LibraryRecordDetails | undefined> {
    throwIfAborted(signal);
    const source = await this.table();
    throwIfAborted(signal);
    const row = source.rows.find((candidate) => candidate.id === id);
    return row ? detailsFromRow(row, "published-preview") : undefined;
  }

  private table(): Promise<LibraryTableResponse> {
    if (!this.tablePromise) {
      const pending = this.fetchImpl(this.tableUrl, { method: "GET" }).then(async (response) => {
        if (!response.ok) throw new Error(`Static library request failed: HTTP ${response.status}`);
        try {
          return parseTableResponse(await response.json());
        } catch (error) {
          if (error instanceof Error && error.message.startsWith("Engine returned")) {
            throw new Error(error.message.replace("Engine", "Static preview"));
          }
          throw error;
        }
      });
      this.tablePromise = pending;
      pending.catch(() => {
        if (this.tablePromise === pending) this.tablePromise = undefined;
      });
    }
    return this.tablePromise;
  }
}

function matchesSearch(row: LibraryTableRow, search?: string): boolean {
  if (!search) return true;
  return libraryCasefold([row.id, row.title, row.short_title, row.publisher, row.topic, ...row.tags]
    .filter((value): value is string => Boolean(value))
    .join(" "))
    .includes(libraryCasefold(search));
}

function matchesFilters(row: LibraryTableRow, query: LibraryTableQuery, omit?: "type" | "status" | "topic"): boolean {
  return (["type", "status", "topic"] as const).every((key) => (
    key === omit || !query[key] || row[key] === query[key]
  ));
}

function sorted(
  rows: readonly LibraryTableRow[],
  field: LibraryTableQuery["sort"],
  descending: boolean,
): LibraryTableRow[] {
  const byId = [...rows].sort((a, b) => compare(a.id, b.id));
  const present = byId.filter((row) => value(row, field) !== null);
  const missing = byId.filter((row) => value(row, field) === null);
  present.sort((a, b) => (descending ? -1 : 1) * compare(value(a, field) ?? "", value(b, field) ?? ""));
  return [...present, ...missing];
}

function value(row: LibraryTableRow, field: LibraryTableQuery["sort"]): string | null {
  const candidate = row[field];
  return typeof candidate === "string" && candidate ? libraryCasefold(candidate) : null;
}

/**
 * Python's `str.casefold` semantics for the scripts used by the public library.
 * ECMAScript lowercasing handles the ordinary mappings; these expansions are
 * the material differences for Latin/Greek library titles without adding a
 * locale-dependent collation or a large Unicode data dependency.
 */
export function libraryCasefold(input: string): string {
  return Array.from(input, (character) => {
    const lower = character.toLocaleLowerCase("und");
    if (lower === "ß") return "ss";
    if (lower === "ς") return "σ";
    if (lower === "ſ") return "s";
    const upper = character.toLocaleUpperCase("und");
    // Full casefold expansions (ligatures, Greek combining forms, Armenian
    // ligatures, and similar) are exposed by Unicode uppercasing as multiple
    // code points. Do not uppercase single-code-point mappings: that would
    // incorrectly turn dotless ı into i, unlike Python.
    return Array.from(upper).length > 1
      ? upper.toLocaleLowerCase("und").replace(/ς/gu, "σ").replace(/ß/gu, "ss")
      : lower;
  }).join("");
}

function compare(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

function contextualFacets(rows: readonly LibraryTableRow[], query: LibraryTableQuery): LibraryFacets {
  return {
    type: counts(rows.filter((row) => matchesFilters(row, query, "type")), "type"),
    status: counts(rows.filter((row) => matchesFilters(row, query, "status")), "status"),
    topic: counts(rows.filter((row) => matchesFilters(row, query, "topic")), "topic"),
  };
}

function counts(rows: readonly LibraryTableRow[], key: "type" | "status" | "topic"): Record<string, number> {
  const result: Record<string, number> = {};
  for (const row of rows) {
    const entry = row[key];
    if (entry) result[entry] = (result[entry] ?? 0) + 1;
  }
  return Object.fromEntries(Object.entries(result).sort(([a], [b]) => compare(a, b)));
}

function throwIfAborted(signal?: AbortSignal): void {
  if (signal?.aborted) throw new DOMException("The request was aborted", "AbortError");
}
