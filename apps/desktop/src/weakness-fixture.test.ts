import { describe, expect, it } from "vitest";
import fixture from "./fixtures/weakness-table.json";
import { parseWeaknessTableResponse } from "./engine-weakness-provider";
import { applyWeaknessQuery, FixtureWeaknessDataProvider } from "./weakness-fixture";
import { DEFAULT_WEAKNESS_QUERY } from "./weakness-types";

const source = parseWeaknessTableResponse(fixture);

describe("weakness fixture provider", () => {
  it("identifies itself as a nine-row, row-only development source", () => {
    const provider = new FixtureWeaknessDataProvider();
    expect(provider.metadata).toMatchObject({ source: "fixture", detailLevel: "row-only" });
    expect(provider.metadata.notice).toContain("9 sample weaknesses");
  });

  it("searches, filters, pages, and reports contextual facets", () => {
    const response = applyWeaknessQuery(source, {
      ...DEFAULT_WEAKNESS_QUERY,
      search: "deprecated",
      status: "Deprecated",
      limit: 2,
      offset: 1,
    });
    expect(response.total).toBe(3);
    expect(response.rows.map((row) => row.id)).toEqual(["CWE-769", "CWE-1187"]);
    expect(response.contextual_facets.status).toEqual({ Deprecated: 3 });
    expect(response.contextual_facets.usage).toEqual({ Prohibited: 3 });
  });

  it("supports each table filter and combined exact-match filters", () => {
    expect(applyWeaknessQuery(source, { ...DEFAULT_WEAKNESS_QUERY, abstraction: "Compound" })
      .rows.map((row) => row.id)).toEqual(["CWE-689", "CWE-692"]);
    expect(applyWeaknessQuery(source, { ...DEFAULT_WEAKNESS_QUERY, structure: "Chain" })
      .rows.map((row) => row.id)).toEqual(["CWE-692"]);
    expect(applyWeaknessQuery(source, { ...DEFAULT_WEAKNESS_QUERY, status: "Stable" })
      .rows.map((row) => row.id)).toEqual(["CWE-79"]);
    expect(applyWeaknessQuery(source, { ...DEFAULT_WEAKNESS_QUERY, usage: "Prohibited" })
      .rows.map((row) => row.id)).toEqual(["CWE-373", "CWE-769", "CWE-1187"]);
    expect(applyWeaknessQuery(source, {
      ...DEFAULT_WEAKNESS_QUERY,
      abstraction: "Compound",
      structure: "Chain",
      status: "Draft",
      usage: "Discouraged",
    }).rows.map((row) => row.id)).toEqual(["CWE-692"]);
  });

  it("uses CWE semantic order, keeps nulls last in both directions, and numeric ids", () => {
    const abstraction = applyWeaknessQuery(source, {
      ...DEFAULT_WEAKNESS_QUERY,
      sort: "abstraction",
    });
    expect(abstraction.rows.map((row) => row.abstraction)).toEqual([
      "Pillar", "Class", "Base", "Base", "Base", "Base", "Variant", "Compound", "Compound",
    ]);

    const likelihoodDesc = applyWeaknessQuery(source, {
      ...DEFAULT_WEAKNESS_QUERY,
      sort: "likelihood",
      order: "desc",
    });
    expect(likelihoodDesc.rows[0].id).toBe("CWE-79");
    expect(likelihoodDesc.rows.slice(1).every((row) => row.likelihood === null)).toBe(true);

    expect(applyWeaknessQuery(source, { ...DEFAULT_WEAKNESS_QUERY, order: "desc" })
      .rows.map((row) => row.id)[0]).toBe("CWE-1187");
  });

  it("returns no fabricated detail record", async () => {
    await expect(new FixtureWeaknessDataProvider().getWeakness("CWE-79")).resolves.toBeUndefined();
  });
});
