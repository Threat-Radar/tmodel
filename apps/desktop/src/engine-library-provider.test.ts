import { describe, expect, it, vi } from "vitest";
import { EngineLibraryDataProvider, parseTableResponse } from "./engine-library-provider";
import type { LibraryTableResponse } from "./library-types";

describe("engine library provider", () => {
  it("constructs table requests without pagination and preserves the server row order", async () => {
    const response = tableResponse(["second", "first"]);
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(response));
    const provider = new EngineLibraryDataProvider("http://engine.test", fetchMock);

    const result = await provider.getTable({
      search: "supply chain",
      type: "paper",
      status: "stub",
      topic: "product-composition",
      sort: "date",
      order: "desc",
    });

    const url = new URL(String(fetchMock.mock.calls[0][0]));
    expect(url.pathname).toBe("/library/table");
    expect(Object.fromEntries(url.searchParams)).toEqual({
      search: "supply chain",
      type: "paper",
      status: "stub",
      topic: "product-composition",
      sort: "date",
      order: "desc",
    });
    expect(url.searchParams.has("limit")).toBe(false);
    expect(url.searchParams.has("offset")).toBe(false);
    expect(result.rows.map((row) => row.id)).toEqual(["second", "first"]);
  });

  it("uses contextual facets and falls back to whole-library facets from an older engine", () => {
    const current = tableResponse(["one"]);
    current.facets.type = { paper: 12 };
    current.contextual_facets.type = { rfc: 1 };
    expect(parseTableResponse(current).contextual_facets.type).toEqual({ rfc: 1 });

    const legacy = { ...current, contextual_facets: undefined };
    expect(parseTableResponse(legacy).contextual_facets).toEqual(current.facets);
  });

  it("requests one full record by id", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({
      count: 1,
      records: [{
        id: "rfc-8785",
        title: "JSON Canonicalization Scheme",
        body: "ietf",
        type: "rfc",
        status: "distilled",
        topic: "canonicalization",
        date: "2020-06",
        publisher: "RFC Editor",
        authors: ["A. Rundgren"],
        version: "RFC 8785",
        maturity: "informational",
        tags: ["canonicalization"],
        content: { url: "https://example.test/rfc" },
        profile: "full",
        artifacts: [{
          kind: "requirements",
          path: "requirements.yaml",
          coverage: "full",
          reviewed_by: "test-reviewer",
          generated_from: null,
          reviewed: true,
        }],
        usefulness: {
          verdict: "useful",
          reason: "Defines canonical JSON.",
          assessed: "2026-10-31",
        },
        applicability: { security: "core" },
      }],
    }));
    const provider = new EngineLibraryDataProvider("http://engine.test", fetchMock);

    const record = await provider.getRecord("rfc-8785");

    expect(String(fetchMock.mock.calls[0][0])).toBe("http://engine.test/library?id=rfc-8785");
    expect(record).toMatchObject({
      id: "rfc-8785",
      body: "ietf",
      profile: "full",
      authors: ["A. Rundgren"],
      usefulness: { verdict: "useful" },
      applicability: { security: "core" },
    });
  });

  it("surfaces 400, 503, network, and malformed response failures", async () => {
    const badRequest = new EngineLibraryDataProvider(
      "http://engine.test",
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({ error: "bad sort" }, 400)),
    );
    await expect(badRequest.getTable({ sort: "title", order: "asc" }))
      .rejects.toThrow("Engine request failed: bad sort");

    const unavailable = new EngineLibraryDataProvider(
      "http://engine.test",
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({ error: "no library configured" }, 503)),
    );
    await expect(unavailable.getTable({ sort: "title", order: "asc" }))
      .rejects.toThrow("Engine request failed: no library configured");

    const offline = new EngineLibraryDataProvider(
      "http://engine.test",
      vi.fn<typeof fetch>().mockRejectedValue(new TypeError("Failed to fetch")),
    );
    await expect(offline.getTable({ sort: "title", order: "asc" }))
      .rejects.toThrow("Failed to fetch");

    expect(() => parseTableResponse({ rows: [] }))
      .toThrow("malformed library table response");
  });

  it("passes cancellation to fetch", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockImplementation(async (_input, init) => {
      if (init?.signal?.aborted) throw new DOMException("aborted", "AbortError");
      return jsonResponse(tableResponse([]));
    });
    const controller = new AbortController();
    controller.abort();
    const provider = new EngineLibraryDataProvider("http://engine.test", fetchMock);

    await expect(provider.getTable({ sort: "title", order: "asc" }, controller.signal))
      .rejects.toMatchObject({ name: "AbortError" });
    expect(fetchMock.mock.calls[0][1]?.signal).toBe(controller.signal);
  });

  it("accepts valid artifact count boundaries", () => {
    const empty = tableResponse(["empty"]);
    expect(parseTableResponse(empty).rows[0]).toMatchObject({ artifacts: 0, reviewed_artifacts: 0 });

    const fullyReviewed = withArtifactCounts(tableResponse(["reviewed"]), 3, 3);
    expect(parseTableResponse(fullyReviewed).rows[0]).toMatchObject({
      artifacts: 3,
      reviewed_artifacts: 3,
    });
  });

  it("rejects invalid artifact counts", () => {
    for (const [artifacts, reviewed] of [[-1, 0], [1.5, 0], [1, -1], [1, 0.5], [1, 2]]) {
      expect(() => parseTableResponse(withArtifactCounts(tableResponse(["bad"]), artifacts, reviewed)))
        .toThrow("malformed library table response");
    }
  });

  it("rejects malformed full-record artifacts", async () => {
    const malformed = {
      count: 1,
      records: [{
        id: "record",
        title: "Record",
        body: "academic",
        type: "paper",
        status: "distilled",
        topic: null,
        date: null,
        publisher: null,
        authors: [],
        version: null,
        maturity: null,
        tags: [],
        content: { url: null },
        profile: "full",
        artifacts: [{
          kind: "requirements",
          path: "requirements.yaml",
          coverage: "full",
          reviewed_by: "test-reviewer",
          generated_from: null,
          reviewed: "yes",
        }],
        usefulness: null,
        applicability: {},
      }],
    };
    const provider = new EngineLibraryDataProvider(
      "http://engine.test",
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(malformed)),
    );

    await expect(provider.getRecord("record"))
      .rejects.toThrow("malformed library record response");
  });
});

function withArtifactCounts(
  response: LibraryTableResponse,
  artifacts: number,
  reviewedArtifacts: number,
): unknown {
  return {
    ...response,
    rows: [{ ...response.rows[0], artifacts, reviewed_artifacts: reviewedArtifacts }],
  };
}

export function tableResponse(ids: readonly string[]): LibraryTableResponse {
  return {
    library: { digest: "digest", count: ids.length, problems: [] },
    query: {
      filters: {},
      search: null,
      sort: "title",
      order: "asc",
      limit: null,
      offset: 0,
    },
    total: ids.length,
    count: ids.length,
    rows: ids.map((id) => ({
      id,
      title: `Title ${id}`,
      short_title: null,
      type: "paper",
      shelf: "academic",
      status: "stub",
      maturity: null,
      date: null,
      publisher: null,
      topic: null,
      tags: [],
      url: null,
      artifacts: 0,
      reviewed_artifacts: 0,
      profile: null,
    })),
    facets: { type: { paper: ids.length }, status: { stub: ids.length }, topic: {} },
    contextual_facets: {
      type: { paper: ids.length },
      status: { stub: ids.length },
      topic: {},
    },
  };
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
