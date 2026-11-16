import { describe, expect, it } from "vitest";
import fixture from "./fixtures/weakness-table.json";
import {
  EngineWeaknessDataProvider,
  parseWeaknessDetailResponse,
  parseWeaknessTableResponse,
} from "./engine-weakness-provider";
import { DEFAULT_WEAKNESS_QUERY } from "./weakness-types";

describe("engine weakness provider", () => {
  it("sends the complete table query and accepts the documented response", async () => {
    let requested: RequestInfo | URL | undefined;
    const fetchImpl: typeof fetch = async (input) => {
      requested = input;
      return new Response(JSON.stringify(fixture));
    };
    const provider = new EngineWeaknessDataProvider("http://127.0.0.1:7777", fetchImpl);

    const response = await provider.getTable({
      ...DEFAULT_WEAKNESS_QUERY,
      search: "xss",
      abstraction: "Base",
      structure: "Simple",
      status: "Stable",
      usage: "Allowed",
      sort: "likelihood",
      order: "desc",
      limit: 50,
      offset: 100,
    });

    expect(response.catalog.version).toBe("4.20");
    const url = new URL(String(requested));
    expect(url.pathname).toBe("/weaknesses/table");
    expect(Object.fromEntries(url.searchParams)).toEqual({
      search: "xss",
      abstraction: "Base",
      structure: "Simple",
      status: "Stable",
      usage: "Allowed",
      sort: "likelihood",
      order: "desc",
      limit: "50",
      offset: "100",
    });
  });

  it("surfaces engine errors and rejects malformed success responses", async () => {
    const failed = new EngineWeaknessDataProvider("http://engine", async () => new Response(
      JSON.stringify({ error: "set TMODEL_CWE_CATALOG" }),
      { status: 503 },
    ));
    await expect(failed.getTable(DEFAULT_WEAKNESS_QUERY))
      .rejects.toThrow("set TMODEL_CWE_CATALOG");

    expect(() => parseWeaknessTableResponse({ ...fixture, count: 99 }))
      .toThrow("malformed weakness table response");
    expect(() => parseWeaknessTableResponse({ ...fixture, rows: [{ id: "CWE-79" }] }))
      .toThrow("malformed weakness table response");
  });

  it("validates a full entry and its proposed assertions", () => {
    const detail = detailResponse();
    expect(parseWeaknessDetailResponse(detail)).toEqual(detail);
    expect(() => parseWeaknessDetailResponse({ ...detail, objects: { assertions: "yes" } }))
      .toThrow("malformed weakness detail response");
  });
});

function detailResponse() {
  return {
    catalog: fixture.catalog,
    id: "CWE-79",
    entry: {
      id: "CWE-79",
      kind: "Weakness",
      name: "Cross-site scripting",
      status: "Stable",
      abstraction: "Base",
      structure: "Simple",
      view_type: null,
      usage: "Allowed",
      likelihood: "High",
      description: "Untrusted input reaches a page.",
      alternate_terms: ["XSS"],
      attack_patterns: ["CAPEC-63"],
      observed_examples: [{ reference: "CVE-2024-0001", description: "Example", link: null }],
      mitigations: 1,
      url: "https://cwe.mitre.org/data/definitions/79.html",
      fields: { Extended_Description: [{ "#xhtml": "<p>More detail</p>" }] },
    },
    objects: {
      parties: [],
      weaknesses: [],
      attack_patterns: [],
      vulnerabilities: [],
      assertions: [{
        id: "assertion:cwe-79-capec-63",
        name: "CWE-79 is exploited by CAPEC-63",
        subject: "weakness:cwe-79",
        predicate: "exploited_by",
        object: "attack-pattern:capec-63",
        assertion_status: "proposed",
        asserted_by: "party:mitre-cwe",
        generated_by: "CWE 4.20",
      }],
    },
  };
}
