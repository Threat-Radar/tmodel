export const LIBRARY_SORTS = ["title", "type", "status", "topic", "date"] as const;
export type LibrarySort = typeof LIBRARY_SORTS[number];
export type SortOrder = "asc" | "desc";

export function isLibrarySort(value: string): value is LibrarySort {
  return (LIBRARY_SORTS as readonly string[]).includes(value);
}

export interface LibraryTableQuery {
  search?: string;
  type?: string;
  status?: string;
  topic?: string;
  sort: LibrarySort;
  order: SortOrder;
}

export interface LibraryTableRow {
  id: string;
  title: string;
  short_title: string | null;
  type: string;
  shelf: string;
  status: string;
  maturity: string | null;
  date: string | null;
  publisher: string | null;
  topic: string | null;
  tags: readonly string[];
  url: string | null;
  artifacts: number;
  reviewed_artifacts: number;
  profile: string | null;
}

export interface LibraryTableResponse {
  library: {
    digest: string;
    count: number;
    problems: readonly string[];
  };
  query: {
    filters: Readonly<Record<string, string>>;
    search: string | null;
    sort: string;
    order: SortOrder;
    limit: number | null;
    offset: number;
  };
  total: number;
  count: number;
  rows: readonly LibraryTableRow[];
  /** Whole-library counts for type, status, and topic. */
  facets: LibraryFacets;
  /** Counts constrained by search and other filters, excluding each facet's own filter. */
  contextual_facets: LibraryFacets;
}

export interface LibraryFacets {
  type: Readonly<Record<string, number>>;
  status: Readonly<Record<string, number>>;
  topic: Readonly<Record<string, number>>;
}

export interface LibraryArtifact {
  kind: string;
  path: string;
  coverage: string;
  reviewed_by: string;
  generated_from: string | null;
  reviewed: boolean;
}

export interface LibraryUsefulness {
  verdict: string;
  reason: string | null;
  assessed: string | null;
}

export interface LibraryRecordDetails {
  id: string;
  title: string;
  body: string;
  type: string;
  status: string;
  topic: string | null;
  date: string | null;
  publisher: string | null;
  authors: readonly string[];
  version: string | null;
  maturity: string | null;
  tags: readonly string[];
  content: { url?: string | null; [key: string]: unknown };
  profile: string | null;
  artifacts: readonly LibraryArtifact[];
  usefulness: LibraryUsefulness | null;
  applicability: Readonly<Record<string, string>>;
}

export interface LibraryProviderMetadata {
  source: "fixture" | "engine";
  notice: string;
  supportsQueries: boolean;
}

export interface LibraryDataProvider {
  readonly metadata: LibraryProviderMetadata;
  getTable(query: LibraryTableQuery, signal?: AbortSignal): Promise<LibraryTableResponse>;
  getRecord(id: string, signal?: AbortSignal): Promise<LibraryRecordDetails | undefined>;
}

export const DEFAULT_LIBRARY_QUERY: LibraryTableQuery = {
  sort: "title",
  order: "asc",
};
