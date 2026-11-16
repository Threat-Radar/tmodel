export const WEAKNESS_SORTS = [
  "id",
  "name",
  "abstraction",
  "structure",
  "status",
  "usage",
  "likelihood",
] as const;

export type WeaknessSort = typeof WEAKNESS_SORTS[number];
export type WeaknessFilter = "abstraction" | "structure" | "status" | "usage";
export type WeaknessSortOrder = "asc" | "desc";

export const WEAKNESS_FILTERS: readonly WeaknessFilter[] = [
  "abstraction",
  "structure",
  "status",
  "usage",
];

export const WEAKNESS_ENUMERATION_ORDER: Readonly<Record<string, readonly string[]>> = {
  abstraction: ["Pillar", "Class", "Base", "Variant", "Compound"],
  structure: ["Simple", "Chain", "Composite"],
  status: ["Stable", "Usable", "Draft", "Incomplete", "Obsolete", "Deprecated"],
  usage: ["Allowed", "Allowed-with-Review", "Discouraged", "Prohibited"],
  likelihood: ["High", "Medium", "Low", "Unknown"],
};

export interface WeaknessTableQuery {
  search?: string;
  abstraction?: string;
  structure?: string;
  status?: string;
  usage?: string;
  sort: WeaknessSort;
  order: WeaknessSortOrder;
  limit: number;
  offset: number;
}

export interface WeaknessCatalog {
  name: string;
  version: string;
  date: string;
  schema: string | null;
  file: string;
  sha256: string;
  weaknesses: number;
  categories: number;
  views: number;
  references: number;
  unknown_fields: number;
  notice: string;
  license: string;
  terms_url: string;
}

export interface WeaknessTableRow {
  id: string;
  weakness: string;
  name: string;
  abstraction: string | null;
  structure: string | null;
  status: string;
  usage: string | null;
  likelihood: string | null;
  description: string;
  attack_patterns: number;
  observed_examples: number;
  mitigations: number;
  url: string;
}

export interface WeaknessFacets {
  abstraction: Readonly<Record<string, number>>;
  structure: Readonly<Record<string, number>>;
  status: Readonly<Record<string, number>>;
  usage: Readonly<Record<string, number>>;
}

export interface WeaknessTableResponse {
  catalog: WeaknessCatalog;
  query: {
    filters: Readonly<Record<string, string>>;
    search: string | null;
    sort: string;
    order: WeaknessSortOrder;
    limit: number | null;
    offset: number;
  };
  total: number;
  count: number;
  rows: readonly WeaknessTableRow[];
  facets: WeaknessFacets;
  contextual_facets: WeaknessFacets;
}

export type CweFieldValue =
  | string
  | number
  | boolean
  | null
  | readonly CweFieldValue[]
  | { readonly [key: string]: CweFieldValue };

export interface WeaknessObservedExample {
  reference: string;
  description: string;
  link: string | null;
}

export interface WeaknessEntry {
  id: string;
  kind: string;
  name: string;
  status: string;
  abstraction: string | null;
  structure: string | null;
  view_type: string | null;
  usage: string | null;
  likelihood: string | null;
  description: string;
  alternate_terms: readonly string[];
  attack_patterns: readonly string[];
  observed_examples: readonly WeaknessObservedExample[];
  mitigations: number;
  url: string;
  fields: Readonly<Record<string, CweFieldValue>>;
}

export interface WeaknessAssertion {
  id: string;
  name: string;
  subject: string;
  predicate: string;
  object: string;
  assertion_status: string;
  asserted_by: string;
  generated_by: string;
  description?: string;
  evidence?: readonly string[];
}

export interface WeaknessObjects {
  parties: readonly Readonly<Record<string, unknown>>[];
  weaknesses: readonly Readonly<Record<string, unknown>>[];
  attack_patterns: readonly Readonly<Record<string, unknown>>[];
  vulnerabilities: readonly Readonly<Record<string, unknown>>[];
  assertions: readonly WeaknessAssertion[];
}

export interface WeaknessDetailResponse {
  catalog: WeaknessCatalog;
  id: string;
  entry: WeaknessEntry | null;
  objects: WeaknessObjects | null;
}

export interface WeaknessProviderMetadata {
  source: "engine" | "fixture";
  notice: string;
  detailLevel: "full" | "row-only";
}

export interface WeaknessDataProvider {
  readonly metadata: WeaknessProviderMetadata;
  getTable(query: WeaknessTableQuery, signal?: AbortSignal): Promise<WeaknessTableResponse>;
  getWeakness(id: string, signal?: AbortSignal): Promise<WeaknessDetailResponse | undefined>;
}

export const DEFAULT_WEAKNESS_QUERY: WeaknessTableQuery = {
  sort: "id",
  order: "asc",
  limit: 25,
  offset: 0,
};

export function isWeaknessSort(value: string): value is WeaknessSort {
  return (WEAKNESS_SORTS as readonly string[]).includes(value);
}
