import { describe as suite, expect, it } from "vitest";
import { checkEngine, describe } from "./engine";

const okHealth = { status: "ok", engine: "tmodel-engine", version: "0.1.0", python: "3.11.1" };

function fakeFetch(body: unknown, status = 200): typeof fetch {
  return (async () => new Response(JSON.stringify(body), { status })) as typeof fetch;
}

suite("checkEngine", () => {
  it("reports connected when /health says ok", async () => {
    const state = await checkEngine("http://127.0.0.1:1", fakeFetch(okHealth));
    expect(state).toEqual({ kind: "connected", health: okHealth });
  });

  it("reports unhealthy when status is not ok", async () => {
    const state = await checkEngine("http://127.0.0.1:1", fakeFetch({ ...okHealth, status: "degraded" }));
    expect(state.kind).toBe("unhealthy");
  });

  it("reports unreachable on HTTP errors and network failures", async () => {
    expect((await checkEngine("http://x", fakeFetch({}, 500))).kind).toBe("unreachable");
    const failing = (async () => {
      throw new TypeError("Failed to fetch");
    }) as typeof fetch;
    expect(await checkEngine("http://x", failing)).toEqual({
      kind: "unreachable",
      error: "Failed to fetch",
    });
  });
});

suite("describe", () => {
  it("shows the skeleton's success line", () => {
    expect(describe({ kind: "connected", health: okHealth }).text).toBe(
      "connected to local engine · v0.1.0",
    );
  });

  it("tells the user how to start the engine", () => {
    expect(describe({ kind: "unreachable", error: "x" }).hint).toContain("tmodel serve");
  });
});
