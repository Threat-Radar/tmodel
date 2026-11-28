import { describe, expect, it, vi } from "vitest";
import details from "./fixtures/attack-pattern-details.json";
import table from "./fixtures/attack-pattern-table.json";
import {
  applyAttackPatternQuery,
  FixtureAttackPatternDataProvider,
  loadAttackPatternDetailFixture,
  parseAttackPatternDetailFixture,
} from "./attack-pattern-fixture";
import { DEFAULT_ATTACK_PATTERN_QUERY, type AttackPatternTableQuery } from "./attack-pattern-types";
import { parseAttackPatternTableResponse } from "./engine-attack-pattern-provider";

const source = parseAttackPatternTableResponse(table);
const answers = parseAttackPatternDetailFixture(details);
const alternateTerms = new Map([...answers].map(([id, answer]) => [id, answer.entry?.alternate_terms ?? []]));
const BY_NUMBER = [
  "CAPEC-5", "CAPEC-7", "CAPEC-23", "CAPEC-63", "CAPEC-66", "CAPEC-88", "CAPEC-115",
  "CAPEC-192", "CAPEC-273", "CAPEC-478", "CAPEC-497", "CAPEC-602", "CAPEC-701",
];

function ids(query: Partial<AttackPatternTableQuery>): string[] {
  return applyAttackPatternQuery(source, { ...DEFAULT_ATTACK_PATTERN_QUERY, ...query }, alternateTerms)
    .rows.map((row) => row.id);
}

describe("attack-pattern fixture provider", () => {
  it("identifies itself as the 13-pattern CAPEC 3.9 sample, not the catalog", () => {
    expect(new FixtureAttackPatternDataProvider().metadata).toEqual({
      source: "fixture",
      notice: "CAPEC 3.9 development fixture · 13 sample attack patterns, not the complete catalog",
    });
  });

  it("answers the default query with the engine's rows and facets", () => {
    const response = applyAttackPatternQuery(source, DEFAULT_ATTACK_PATTERN_QUERY);
    expect(response.rows).toEqual(table.rows);
    expect(response.facets).toEqual(table.facets);
    expect(response.contextual_facets).toEqual(table.contextual_facets);
    expect(response.catalog).toEqual(table.catalog);
    expect(response.query).toEqual({ filters: {}, search: null, sort: "id", order: "asc", limit: 50, offset: 0 });
    expect([response.total, response.count]).toEqual([13, 13]);
  });

  // The cases and answers of engine/tests/test_attack_pattern_table.py::test_table_queries.
  it.each<[Partial<AttackPatternTableQuery>, string[]]>([
    [{}, BY_NUMBER],
    [{ order: "desc" }, [...BY_NUMBER].reverse()],
    [{ status: "Deprecated" }, ["CAPEC-602"]],
    [{ abstraction: "Meta" }, ["CAPEC-115", "CAPEC-192", "CAPEC-602"]],
    [{ severity: "Very High" }, ["CAPEC-5", "CAPEC-23", "CAPEC-63"]],
    [{ abstraction: "Standard", likelihood: "High" }, ["CAPEC-23", "CAPEC-63", "CAPEC-66", "CAPEC-88", "CAPEC-497"]],
    [{ search: "sql" }, ["CAPEC-7", "CAPEC-66"]],
    [{ search: "CWE-89" }, ["CAPEC-7", "CAPEC-66"]],
    [{ search: "t1574" }, ["CAPEC-478"]],
    [{ search: "HTTP Desync" }, ["CAPEC-273"]],
    [{ search: "capec-115" }, ["CAPEC-115"]],
    [{ search: "nothing like this" }, []],
    [{ sort: "abstraction" }, [
      "CAPEC-115", "CAPEC-192", "CAPEC-602", "CAPEC-23", "CAPEC-63", "CAPEC-66", "CAPEC-88",
      "CAPEC-497", "CAPEC-701", "CAPEC-5", "CAPEC-7", "CAPEC-273", "CAPEC-478",
    ]],
    [{ sort: "severity" }, [
      "CAPEC-5", "CAPEC-23", "CAPEC-63", "CAPEC-7", "CAPEC-66", "CAPEC-88", "CAPEC-273",
      "CAPEC-478", "CAPEC-701", "CAPEC-115", "CAPEC-192", "CAPEC-497", "CAPEC-602",
    ]],
    [{ limit: 2, offset: 1 }, ["CAPEC-7", "CAPEC-23"]],
  ])("gives the engine's answer to %o", (query, expected) => {
    expect(ids(query)).toEqual(expected);
  });

  it("reports the total and the query when paging", () => {
    const response = applyAttackPatternQuery(source, { ...DEFAULT_ATTACK_PATTERN_QUERY, limit: 4, offset: 12, sort: "name" });
    expect([response.total, response.count]).toEqual([13, 1]);
    expect(response.query).toEqual({ filters: {}, search: null, sort: "name", order: "asc", limit: 4, offset: 12 });
  });

  it("pages to the last row and past it without losing the total", () => {
    expect(ids({ limit: 5 })).toEqual(BY_NUMBER.slice(0, 5));
    expect(ids({ limit: 5, offset: 5 })).toEqual(BY_NUMBER.slice(5, 10));
    expect(ids({ limit: 5, offset: 10 })).toEqual(BY_NUMBER.slice(10));
    const past = applyAttackPatternQuery(source, { ...DEFAULT_ATTACK_PATTERN_QUERY, limit: 5, offset: 15 });
    expect([past.total, past.count, past.rows]).toEqual([13, 0, []]);
  });

  it("keeps attack patterns without the sort value last in both orders", () => {
    const asc = ids({ sort: "likelihood" });
    const desc = ids({ sort: "likelihood", order: "desc" });
    expect(asc.slice(-2)).toEqual(["CAPEC-115", "CAPEC-602"]);
    expect(desc.slice(-2)).toEqual(["CAPEC-115", "CAPEC-602"]);
    expect(ids({ sort: "severity", order: "desc" }).slice(-1)).toEqual(["CAPEC-602"]);
  });

  it("sorts stably: equal values keep id order in both directions", () => {
    const draft = ["CAPEC-7", "CAPEC-23", "CAPEC-63", "CAPEC-66", "CAPEC-88", "CAPEC-115", "CAPEC-497", "CAPEC-701"];
    expect(ids({ sort: "status" })).toEqual(["CAPEC-192", "CAPEC-273", "CAPEC-478", ...draft, "CAPEC-5", "CAPEC-602"]);
    expect(ids({ sort: "status", order: "desc" }))
      .toEqual(["CAPEC-602", "CAPEC-5", ...draft, "CAPEC-478", "CAPEC-192", "CAPEC-273"]);
    expect(ids({ sort: "name" })[0]).toBe("CAPEC-115"); // Authentication Bypass
  });

  it("counts the whole catalog in facets and the query, less each facet's own filter, in contextual ones", () => {
    // engine/tests/test_attack_pattern_table.py::test_facets_count_the_whole_catalog_...
    const response = applyAttackPatternQuery(source, { ...DEFAULT_ATTACK_PATTERN_QUERY, status: "Draft", search: "e" }, alternateTerms);
    expect(response.facets).toEqual(table.facets);
    expect(response.contextual_facets.status).toEqual(table.facets.status);
    expect(response.contextual_facets.severity).toEqual({ High: 4, Medium: 1, "Very High": 2, "Very Low": 1 });
    expect(response.query.filters).toEqual({ status: "Draft" });
  });

  it("reads alternate terms only from the detail answers, loading them once and only to search", async () => {
    const load = vi.fn(async () => answers);
    const provider = new FixtureAttackPatternDataProvider(load);
    await provider.getTable(DEFAULT_ATTACK_PATTERN_QUERY);
    expect(load).not.toHaveBeenCalled();
    const desync = await provider.getTable({ ...DEFAULT_ATTACK_PATTERN_QUERY, search: "HTTP Desync" });
    expect(desync.rows.map((row) => row.id)).toEqual(["CAPEC-273"]);
    await provider.getTable({ ...DEFAULT_ATTACK_PATTERN_QUERY, search: "sql" });
    await provider.getAttackPattern("CAPEC-66");
    expect(load).toHaveBeenCalledTimes(1);
  });

  it("serves the engine's details answer for each of its rows and none for another id", async () => {
    const provider = new FixtureAttackPatternDataProvider(loadAttackPatternDetailFixture);
    for (const row of table.rows) {
      await expect(provider.getAttackPattern(row.id)).resolves.toEqual(details[row.id as keyof typeof details]);
    }
    await expect(provider.getAttackPattern("CAPEC-1")).resolves.toBeUndefined();
  });

  it("gives each caller its own copy, so the shared fixture cannot be changed", async () => {
    const provider = new FixtureAttackPatternDataProvider(async () => answers);
    const first = await provider.getAttackPattern("CAPEC-66");
    first!.entry!.name = "changed";
    expect((await provider.getAttackPattern("CAPEC-66"))?.entry?.name).toBe("SQL Injection");
    const page = await provider.getTable(DEFAULT_ATTACK_PATTERN_QUERY);
    (page.rows[0] as { name: string }).name = "changed";
    expect((await provider.getTable(DEFAULT_ATTACK_PATTERN_QUERY)).rows[0].name).toBe("Blue Boxing");
  });

  it("lets a request after a failed load try the chunk again", async () => {
    const load = vi.fn()
      .mockRejectedValueOnce(new Error("Failed to fetch dynamically imported module"))
      .mockResolvedValueOnce(answers);
    const provider = new FixtureAttackPatternDataProvider(load);
    await expect(provider.getAttackPattern("CAPEC-66")).rejects.toThrow("dynamically imported module");
    await expect(provider.getAttackPattern("CAPEC-66")).resolves.toMatchObject({ id: "CAPEC-66" });
    expect(load).toHaveBeenCalledTimes(2);
  });

  it("honours an aborted request", async () => {
    const provider = new FixtureAttackPatternDataProvider(async () => answers);
    const controller = new AbortController();
    controller.abort();
    await expect(provider.getTable(DEFAULT_ATTACK_PATTERN_QUERY, controller.signal)).rejects.toThrow("aborted");
    await expect(provider.getAttackPattern("CAPEC-66", controller.signal)).rejects.toThrow("aborted");
  });

  it("refuses a details fixture whose answer is filed under another id", () => {
    expect(() => parseAttackPatternDetailFixture({ "CAPEC-7": details["CAPEC-66"] }))
      .toThrow("no entry for CAPEC-7");
    expect(() => parseAttackPatternDetailFixture([details["CAPEC-66"]])).toThrow("not an object of answers");
  });
});
