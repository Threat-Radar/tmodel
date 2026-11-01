import { describe, expect, it } from "vitest";
import fixture from "./fixtures/library-table.json";
import { parseTableResponse } from "./engine-library-provider";
import { FixtureLibraryDataProvider } from "./library-fixture";

describe("library fixture contract", () => {
  it("matches PR #188's response contract and contains the 12 sample records", () => {
    const response = parseTableResponse(fixture);

    expect(response.rows).toHaveLength(12);
    expect(response.count).toBe(12);
    expect(response.query.limit).toBeNull();
    expect(response.rows[0]).toEqual(expect.objectContaining({
      id: expect.any(String),
      title: expect.any(String),
      artifacts: expect.any(Number),
      reviewed_artifacts: expect.any(Number),
    }));
  });

  it("supports deterministic initial rendering and row-backed details without query logic", async () => {
    const provider = new FixtureLibraryDataProvider();
    const response = await provider.getTable({ sort: "title", order: "desc", search: "ignored" });
    const details = await provider.getRecord("rfc-8785");

    expect(provider.metadata.supportsQueries).toBe(false);
    expect(response.rows.map((row) => row.id)).toEqual(
      parseTableResponse(fixture).rows.map((row) => row.id),
    );
    expect(details).toMatchObject({
      id: "rfc-8785",
      body: "ietf",
      profile: "full",
    });
    expect(details?.artifacts).toHaveLength(7);
  });
});
