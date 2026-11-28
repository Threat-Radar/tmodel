import { describe, expect, it } from "vitest";
import details from "./fixtures/attack-pattern-details.json";
import table from "./fixtures/attack-pattern-table.json";
import { DEFAULT_ATTACK_PATTERN_QUERY } from "./attack-pattern-types";
import {
  EngineAttackPatternDataProvider,
  parseAttackPatternDetailResponse,
  parseAttackPatternTableResponse,
} from "./engine-attack-pattern-provider";

// Both fixtures are the engine's own answers over the CAPEC 3.9 sample, and
// engine/tests/test_attack_pattern_table.py fails when either drifts from the engine.
const sqlInjection = details["CAPEC-66"];

describe("engine attack-pattern provider", () => {
  it("sends the complete table query and accepts the engine's table answer", async () => {
    let requested: RequestInfo | URL | undefined;
    const provider = new EngineAttackPatternDataProvider("http://127.0.0.1:7777/", async (input) => {
      requested = input;
      return new Response(JSON.stringify(table));
    });

    const response = await provider.getTable({
      ...DEFAULT_ATTACK_PATTERN_QUERY,
      search: "injection",
      abstraction: "Standard",
      status: "Draft",
      likelihood: "High",
      severity: "Very High",
      sort: "severity",
      order: "desc",
      limit: 50,
      offset: 100,
    });

    expect(response.catalog).toMatchObject({ name: "CAPEC", version: "3.9", attack_patterns: 13 });
    const url = new URL(String(requested));
    expect(`${url.origin}${url.pathname}`).toBe("http://127.0.0.1:7777/attack-patterns/table");
    expect(Object.fromEntries(url.searchParams)).toEqual({
      search: "injection",
      abstraction: "Standard",
      status: "Draft",
      likelihood: "High",
      severity: "Very High",
      sort: "severity",
      order: "desc",
      limit: "50",
      offset: "100",
    });
  });

  it("leaves unset filters out of the request, as the engine refuses empty ones", async () => {
    let requested: RequestInfo | URL | undefined;
    const provider = new EngineAttackPatternDataProvider("http://engine", async (input) => {
      requested = input;
      return new Response(JSON.stringify(table));
    });
    await provider.getTable({ ...DEFAULT_ATTACK_PATTERN_QUERY, search: "" });
    expect(Object.fromEntries(new URL(String(requested)).searchParams)).toEqual({
      sort: "id",
      order: "asc",
      limit: "50",
      offset: "0",
    });
  });

  it("asks for one entry by id and accepts the engine's details answer", async () => {
    let requested: RequestInfo | URL | undefined;
    const provider = new EngineAttackPatternDataProvider("http://engine", async (input) => {
      requested = input;
      return new Response(JSON.stringify(sqlInjection));
    });

    const response = await provider.getAttackPattern("CAPEC-66");

    const url = new URL(String(requested));
    expect(url.pathname).toBe("/attack-patterns");
    expect(Object.fromEntries(url.searchParams)).toEqual({ id: "CAPEC-66" });
    expect(response?.entry).toMatchObject({ id: "CAPEC-66", kind: "Attack_Pattern", name: "SQL Injection" });
    expect(response?.references?.map((reference) => [reference.id, reference.resolved, reference.title]))
      .toEqual([["REF-607", true, "OWASP Web Security Testing Guide"]]);
    expect(response?.objects?.assertions.map((assertion) => assertion.assertion_status))
      .toEqual(["proposed", "proposed"]);
  });

  it("accepts every answer in the details fixture as the documented shape", () => {
    for (const [id, answer] of Object.entries(details)) {
      const parsed = parseAttackPatternDetailResponse(answer);
      expect(parsed.id).toBe(id);
      expect(parsed.entry?.kind).toBe("Attack_Pattern");
      expect(parsed.catalog).toEqual(table.catalog);
    }
    expect(Object.keys(details)).toEqual(table.rows.map((row) => row.id));
  });

  it("gives no entry for an id the release does not have", async () => {
    // The engine's answer for CAPEC-99999 (engine/tests/test_attack_pattern_table.py).
    const missing = { catalog: table.catalog, id: "CAPEC-99999", entry: null, references: null, objects: null };
    const provider = new EngineAttackPatternDataProvider("http://engine", async () => (
      new Response(JSON.stringify(missing))
    ));
    expect(parseAttackPatternDetailResponse(missing).entry).toBeNull();
    await expect(provider.getAttackPattern("CAPEC-99999")).resolves.toBeUndefined();
  });

  it("refuses to show another entry than the one asked for", async () => {
    const provider = new EngineAttackPatternDataProvider("http://engine", async () => (
      new Response(JSON.stringify(sqlInjection))
    ));
    await expect(provider.getAttackPattern("CAPEC-7")).rejects.toThrow("Engine answered with CAPEC-66 for CAPEC-7");
    await expect(provider.getAttackPattern("capec-66")).resolves.toBeDefined();
  });

  it("surfaces the engine's error message, or the status when there is none", async () => {
    const unavailable = new EngineAttackPatternDataProvider("http://engine", async () => new Response(
      JSON.stringify({
        error: "no CAPEC catalog: download https://capec.mitre.org/data/xml/capec_v3.9.xml "
          + "(SHA-256 70279a2dff0cb0ad79e546adb07828335a704ad5210e047e09e986172fc9e34d) "
          + "and set TMODEL_CAPEC_CATALOG to that file",
      }),
      { status: 503 },
    ));
    await expect(unavailable.getTable(DEFAULT_ATTACK_PATTERN_QUERY))
      .rejects.toThrow("Engine request failed: no CAPEC catalog: download");

    const plain = new EngineAttackPatternDataProvider("http://engine", async () => (
      new Response("<html>bad gateway</html>", { status: 502 })
    ));
    await expect(plain.getAttackPattern("CAPEC-66")).rejects.toThrow("Engine request failed: HTTP 502");

    const garbled = new EngineAttackPatternDataProvider("http://engine", async () => new Response("{"));
    await expect(garbled.getTable(DEFAULT_ATTACK_PATTERN_QUERY)).rejects.toThrow("Engine returned malformed JSON");
  });

  it("rejects table answers that break the documented shape", () => {
    expect(parseAttackPatternTableResponse(table).rows).toHaveLength(13);
    const [first] = table.rows;
    const broken: unknown[] = [
      { ...table, count: 12 },
      { ...table, total: 12 },
      { ...table, rows: [{ id: "CAPEC-5" }], count: 1 },
      { ...table, rows: [{ ...first, weaknesses: "CWE-285" }], count: 1 },
      { ...table, rows: [{ ...first, steps: -1 }], count: 1 },
      { ...table, rows: [{ ...first, url: null }], count: 1 },
      { ...table, facets: { ...table.facets, severity: { High: "6" } } },
      { ...table, contextual_facets: { abstraction: {}, status: {}, likelihood: {} } },
      { ...table, query: { ...table.query, order: "up" } },
      { ...table, query: { ...table.query, limit: 0 } },
      { ...table, catalog: { ...table.catalog, attack_patterns: undefined } },
    ];
    for (const answer of broken) {
      expect(() => parseAttackPatternTableResponse(answer)).toThrow("malformed attack-pattern table response");
    }
  });

  it("rejects details answers that break the documented shape", () => {
    const broken: unknown[] = [
      { ...sqlInjection, entry: null },
      { ...sqlInjection, references: null },
      { ...sqlInjection, entry: null, references: null },
      { ...sqlInjection, references: [{ ...sqlInjection.references[0], resolved: "yes" }] },
      { ...sqlInjection, references: [{ ...sqlInjection.references[0], authors: [7] }] },
      { ...sqlInjection, entry: { ...sqlInjection.entry, related_attack_patterns: ["CAPEC-248"] } },
      { ...sqlInjection, entry: { ...sqlInjection.entry, fields: { "@ID": () => 66 } } },
      { ...sqlInjection, objects: { ...sqlInjection.objects, assertions: [{ id: "x" }] } },
    ];
    for (const answer of broken) {
      expect(() => parseAttackPatternDetailResponse(answer)).toThrow("malformed attack-pattern detail response");
    }
  });
});
