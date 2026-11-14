import { describe, expect, it, vi } from "vitest";
import fixture from "./fixtures/library-table.json";
import { libraryCasefold, StaticLibraryDataProvider } from "./static-library-provider";

describe("published static library", () => {
  it("keeps search, filters, sorting and document selection useful", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify(fixture)));
    const provider = new StaticLibraryDataProvider(
      "https://threat-radar.github.io/tmodel/app/data/library/table.json",
      fetchMock,
    );
    const response = await provider.getTable({
      search: "sbom",
      type: "paper",
      sort: "date",
      order: "desc",
    });

    expect(provider.metadata).toMatchObject({ source: "static-preview", supportsQueries: true });
    expect(response.rows.map((row) => row.id)).toEqual([
      "sbomproof-2025",
      "benedetti-2024-sbom-python",
    ]);
    expect(response.contextual_facets.type.paper).toBe(2);
    expect(response.contextual_facets.type.rfc).toBe(1);

    const details = await provider.getRecord("sbomproof-2025");
    expect(details).toMatchObject({
      id: "sbomproof-2025",
      title: expect.any(String),
      content: { url: expect.any(String) },
    });
    expect(details?.artifacts).toHaveLength(
      fixture.rows.find((row) => row.id === "sbomproof-2025")?.artifacts ?? -1,
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("puts missing sort values last in either direction", async () => {
    const provider = new StaticLibraryDataProvider(
      "https://example.test/table.json",
      vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify(fixture))),
    );
    for (const order of ["asc", "desc"] as const) {
      const response = await provider.getTable({ sort: "date", order });
      const firstMissing = response.rows.findIndex((row) => row.date === null);
      expect(firstMissing).toBeGreaterThan(0);
      expect(response.rows.slice(firstMissing).every((row) => row.date === null)).toBe(true);
    }
  });

  it("uses engine-compatible Unicode casefolding for search and stable sorting", async () => {
    const rows = [
      { ...fixture.rows[0], id: "z-plain", title: "Strasse", short_title: "ΟΣ" },
      { ...fixture.rows[1], id: "a-sharp", title: "Straße", short_title: "ος" },
    ];
    const unicodeTable = {
      ...fixture,
      count: rows.length,
      total: rows.length,
      rows,
      library: { ...fixture.library, count: rows.length },
    };
    const provider = new StaticLibraryDataProvider(
      "https://example.test/table.json",
      vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify(unicodeTable))),
    );

    const german = await provider.getTable({ search: "STRASSE", sort: "title", order: "asc" });
    expect(german.rows.map((row) => row.id)).toEqual(["a-sharp", "z-plain"]);
    const greek = await provider.getTable({ search: "οσ", sort: "title", order: "asc" });
    expect(greek.rows.map((row) => row.id)).toEqual(["a-sharp", "z-plain"]);
  });

  it("matches Python casefold expansions without changing dotless i", () => {
    expect(["Straße", "ΟΣ", "ſ", "ﬃ", "ı", "ᾲ", "և"].map(libraryCasefold)).toEqual([
      "strasse", "οσ", "s", "ffi", "ı", "ὰι", "եւ",
    ]);
  });
});
