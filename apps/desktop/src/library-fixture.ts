import fixture from "./fixtures/library-table.json";
import { parseTableResponse } from "./engine-library-provider";
import type {
  LibraryDataProvider,
  LibraryRecordDetails,
  LibraryTableQuery,
  LibraryTableResponse,
  LibraryTableRow,
} from "./library-types";

const TABLE_FIXTURE = parseTableResponse(fixture);

export class FixtureLibraryDataProvider implements LibraryDataProvider {
  readonly metadata = {
    source: "fixture" as const,
    notice: "Development fixture · 12 sample library documents",
    supportsQueries: false,
  };

  async getTable(_query: LibraryTableQuery, signal?: AbortSignal): Promise<LibraryTableResponse> {
    throwIfAborted(signal);
    return structuredClone(TABLE_FIXTURE);
  }

  async getRecord(id: string, signal?: AbortSignal): Promise<LibraryRecordDetails | undefined> {
    throwIfAborted(signal);
    const row = TABLE_FIXTURE.rows.find((candidate) => candidate.id === id);
    return row ? detailsFromRow(row) : undefined;
  }
}

function detailsFromRow(row: LibraryTableRow): LibraryRecordDetails {
  return {
    id: row.id,
    title: row.title,
    body: row.shelf,
    type: row.type,
    status: row.status,
    topic: row.topic,
    date: row.date,
    publisher: row.publisher,
    authors: [],
    version: null,
    maturity: row.maturity,
    tags: [...row.tags],
    content: { url: row.url },
    profile: row.profile,
    artifacts: Array.from({ length: row.artifacts }, (_unused, index) => {
      const reviewed = index < row.reviewed_artifacts;
      return {
        kind: "fixture",
        path: `fixture-artifact-${index + 1}`,
        coverage: "",
        reviewed_by: reviewed ? "fixture-reviewer" : "",
        generated_from: null,
        reviewed,
      };
    }),
    usefulness: null,
    applicability: {},
  };
}

function throwIfAborted(signal?: AbortSignal): void {
  if (signal?.aborted) throw new DOMException("The request was aborted", "AbortError");
}
