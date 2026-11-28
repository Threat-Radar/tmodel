import { LIBRARY_PAGE_SIZE } from "./library-presentation";
import type { CweFieldValue } from "./weakness-types";

// The engine's GET /attack-patterns/table and GET /attack-patterns (#244, DL-0056).
export const ATTACK_PATTERN_SORTS = [
  "id",
  "name",
  "abstraction",
  "status",
  "likelihood",
  "severity",
] as const;

export type AttackPatternSort = typeof ATTACK_PATTERN_SORTS[number];
export type AttackPatternFilter = "abstraction" | "status" | "likelihood" | "severity";
export type AttackPatternSortOrder = "asc" | "desc";

export const ATTACK_PATTERN_FILTERS: readonly AttackPatternFilter[] = [
  "abstraction",
  "status",
  "likelihood",
  "severity",
];

/** CAPEC's own order for its enumerations (ap_schema_v3.5.xsd), as the engine sorts them. */
export const ATTACK_PATTERN_ENUMERATION_ORDER: Readonly<Record<string, readonly string[]>> = {
  abstraction: ["Meta", "Standard", "Detailed"],
  status: ["Stable", "Usable", "Draft", "Incomplete", "Obsolete", "Deprecated"],
  likelihood: ["High", "Medium", "Low", "Unknown"],
  severity: ["Very High", "High", "Medium", "Low", "Very Low"],
};

export interface AttackPatternTableQuery {
  search?: string;
  abstraction?: string;
  status?: string;
  likelihood?: string;
  severity?: string;
  sort: AttackPatternSort;
  order: AttackPatternSortOrder;
  limit: number;
  offset: number;
}

/** Which CAPEC release an answer comes from, with MITRE's notice and licence. */
export interface AttackPatternCatalog {
  name: string;
  version: string;
  date: string;
  schema: string | null;
  file: string;
  sha256: string;
  attack_patterns: number;
  categories: number;
  views: number;
  references: number;
  unknown_fields: number;
  notice: string;
  license: string;
  terms_url: string;
}

export interface AttackPatternTableRow {
  id: string;
  attack_pattern: string;
  name: string;
  abstraction: string | null;
  status: string;
  likelihood: string | null;
  severity: string | null;
  description: string;
  weaknesses: readonly string[];
  attack_techniques: readonly string[];
  related_attack_patterns: number;
  steps: number;
  mitigations: number;
  examples: number;
  url: string;
}

export interface AttackPatternFacets {
  abstraction: Readonly<Record<string, number>>;
  status: Readonly<Record<string, number>>;
  likelihood: Readonly<Record<string, number>>;
  severity: Readonly<Record<string, number>>;
}

export interface AttackPatternTableResponse {
  catalog: AttackPatternCatalog;
  query: {
    filters: Readonly<Record<string, string>>;
    search: string | null;
    sort: string;
    order: AttackPatternSortOrder;
    limit: number | null;
    offset: number;
  };
  total: number;
  count: number;
  rows: readonly AttackPatternTableRow[];
  facets: AttackPatternFacets;
  contextual_facets: AttackPatternFacets;
}

export interface AttackPatternRelation {
  nature: string;
  id: string;
}

/** One entry with every CAPEC field; `fields` follows the CWE reader's value rules (DL-0056). */
export interface AttackPatternEntry {
  id: string;
  kind: string;
  name: string;
  status: string;
  abstraction: string | null;
  view_type: string | null;
  likelihood: string | null;
  severity: string | null;
  description: string;
  alternate_terms: readonly string[];
  related_attack_patterns: readonly AttackPatternRelation[];
  weaknesses: readonly string[];
  attack_techniques: readonly string[];
  steps: number;
  mitigations: number;
  examples: number;
  url: string;
  fields: Readonly<Record<string, CweFieldValue>>;
}

/** A reference the entry cites, resolved to the External_Reference it names. */
export interface AttackPatternReference {
  id: string;
  section: string | null;
  resolved: boolean;
  title: string | null;
  authors: readonly string[];
  edition: string | null;
  publication: string | null;
  publisher: string | null;
  year: string | null;
  month: string | null;
  day: string | null;
  url: string | null;
  url_date: string | null;
}

export interface AttackPatternAssertion {
  id: string;
  name: string;
  subject: string;
  predicate: string;
  object: string;
  assertion_status: string;
  asserted_by: string;
  generated_by: string;
}

/** The tmodel objects the CAPEC import makes for one attack pattern. */
export interface AttackPatternObjects {
  parties: readonly Readonly<Record<string, unknown>>[];
  attack_patterns: readonly Readonly<Record<string, unknown>>[];
  weaknesses: readonly Readonly<Record<string, unknown>>[];
  assertions: readonly AttackPatternAssertion[];
}

export interface AttackPatternDetailResponse {
  catalog: AttackPatternCatalog;
  id: string;
  entry: AttackPatternEntry | null;
  references: readonly AttackPatternReference[] | null;
  objects: AttackPatternObjects | null;
}

export interface AttackPatternProviderMetadata {
  source: "engine" | "fixture";
  notice: string;
}

export interface AttackPatternDataProvider {
  readonly metadata: AttackPatternProviderMetadata;
  getTable(query: AttackPatternTableQuery, signal?: AbortSignal): Promise<AttackPatternTableResponse>;
  getAttackPattern(id: string, signal?: AbortSignal): Promise<AttackPatternDetailResponse | undefined>;
}

/** The first page, in id order, at the Library tables' page size (DL-0070). */
export const DEFAULT_ATTACK_PATTERN_QUERY: AttackPatternTableQuery = {
  sort: "id",
  order: "asc",
  limit: LIBRARY_PAGE_SIZE,
  offset: 0,
};

export function isAttackPatternSort(value: string): value is AttackPatternSort {
  return (ATTACK_PATTERN_SORTS as readonly string[]).includes(value);
}
