import { describe, expect, it, vi } from "vitest";
import catalogArtifact from "../public/data/requirements/catalog.json";
import {
  parseRequirementStandardsCatalog,
  StaticRequirementStandardsSource,
} from "./requirements-catalog-provider";
import { queryRequirements } from "./requirements-model";

describe("extracted standards catalog provider", () => {
  it("loads all 109 unique requirements with the authoritative per-source counts", () => {
    const catalog = parseRequirementStandardsCatalog(catalogArtifact);
    expect(catalog.requirements).toHaveLength(109);
    expect(new Set(catalog.requirements.map((row) => row.id))).toHaveLength(109);
    expect(Object.fromEntries(catalog.sources.map((source) => [source.id, source.count]))).toEqual({
      "owasp-asvs-5": 34,
      "eu-cra-2024-2847": 23,
      "iec-62443-4-1-2018": 52,
    });
    expect(catalog.products).toEqual([]);
  });

  it("searches attribution and filters source, kind, and normativity before paging", () => {
    const catalog = parseRequirementStandardsCatalog(catalogArtifact);
    const asvs = queryRequirements(catalog, {
      search: "V6.3.4",
      source: "owasp-asvs-5",
      kind: "technical",
      normativity: "mandatory",
      sort: "source",
      order: "asc",
      limit: 10,
      offset: 0,
    });
    expect(asvs.total).toBeGreaterThan(0);
    expect(asvs.rows.every((row) => row.catalogSource?.id === "owasp-asvs-5")).toBe(true);
    expect(asvs.rows.every((row) => row.kind === "technical" && row.normativity === "mandatory"))
      .toBe(true);

    const page = queryRequirements(catalog, {
      source: "iec-62443-4-1-2018",
      sort: "id",
      order: "asc",
      limit: 10,
      offset: 10,
    });
    expect(page.total).toBe(52);
    expect(page.rows).toHaveLength(10);
  });

  it("preserves accepted, rejected, and unreviewed Assertion provenance", () => {
    const catalog = parseRequirementStandardsCatalog(catalogArtifact);
    const assertions = [...new Map(catalog.requirements.flatMap((row) => row.relationships)
      .flatMap((relationship) => relationship.assertions)
      .map((assertion) => [assertion.id, assertion])).values()];
    expect(assertions.filter((assertion) => assertion.reviewState === "accepted")).toHaveLength(24);
    expect(assertions.filter((assertion) => assertion.reviewState === "rejected")).toHaveLength(3);
    expect(assertions.filter((assertion) => (
      assertion.reviewState === "proposed" && assertion.reviews.length === 0
    ))).toHaveLength(19);
  });

  it("fetches the same generated asset in a read-only provider", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => new Response(JSON.stringify(catalogArtifact), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }));
    const source = new StaticRequirementStandardsSource(
      "https://example.test/data/requirements/catalog.json",
      fetchMock,
    );
    await expect(source.getCatalog()).resolves.toMatchObject({ file: "extracted-standards-catalog.json" });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("rejects stale counts instead of silently dropping records", () => {
    expect(() => parseRequirementStandardsCatalog({ ...catalogArtifact, count: 108 }))
      .toThrow("109-entry catalog envelope");
  });
});
