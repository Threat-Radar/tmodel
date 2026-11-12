import { describe, expect, it, vi } from "vitest";
import { StaticPreviewApi } from "./static-api";

describe("static preview API", () => {
  it("maps the existing read-only engine routes to Pages JSON without localhost", async () => {
    const seen: string[] = [];
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      const url = new URL(String(input));
      seen.push(`${init?.method ?? "GET"} ${url.href}`);
      if (url.pathname.endsWith("/goals.json")) {
        return json({ goals: [{ goal: "threat:one", file: "goal-001.json" }] });
      }
      return json({ path: url.pathname });
    });
    const api = new StaticPreviewApi("https://threat-radar.github.io/tmodel/app/data/", fetchMock);

    await api.fetch(`${api.engineBase}models`);
    await api.fetch(`${api.engineBase}graph?file=mvp-01-software-doc-service.yaml`);
    await api.fetch(`${api.engineBase}attack-paths?file=mvp-01-software-doc-service.yaml`);
    await api.fetch(`${api.engineBase}attack-paths?file=mvp-01-software-doc-service.yaml&goal=threat%3Aone`);

    expect(seen).toEqual([
      "GET https://threat-radar.github.io/tmodel/app/data/models.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/graph.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/attack-paths/index.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/attack-paths/goals.json",
      "GET https://threat-radar.github.io/tmodel/app/data/models/mvp-01-software-doc-service/attack-paths/goal-001.json",
    ]);
    expect(seen.join(" ")).not.toContain("127.0.0.1");
    expect(seen.join(" ")).not.toContain("localhost");
  });

  it("rejects mutations and unsafe model paths without making a network request", async () => {
    const fetchMock = vi.fn<typeof fetch>();
    const api = new StaticPreviewApi("https://example.test/tmodel/app/data/", fetchMock);
    const mutation = await api.fetch(`${api.engineBase}models`, { method: "POST" });
    const escape = await api.fetch(`${api.engineBase}graph?file=..%2Fsecret.yaml`);

    expect(mutation.status).toBe(405);
    expect(await mutation.json()).toEqual({ error: "browser preview data is read-only" });
    expect(escape.status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

function json(value: unknown): Response {
  return new Response(JSON.stringify(value), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
