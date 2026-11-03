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

suite("describe, with the bundled engine's process state (#124)", () => {
  const down = { kind: "unreachable", error: "Failed to fetch" } as const;

  it("shows starting, not an error, while the sidecar boots", () => {
    expect(describe(down, { kind: "started" })).toEqual({
      text: "starting local engine…",
      hint: "",
      tone: "pending",
    });
  });

  it("explains a port held by another program", () => {
    const d = describe(down, { kind: "port_busy", port: 47811 });
    expect(d.text).toBe("port 47811 is in use by another program");
    expect(d.hint).toContain("Quit the program using it");
    expect(d.tone).toBe("unreachable");
  });

  it("shows the exit code and the engine's last error line", () => {
    const d = describe(down, {
      kind: "exited",
      code: 1,
      stderr: "Traceback...\nerror: [Errno 48] Address already in use",
    });
    expect(d.text).toBe("local engine stopped (exit code 1)");
    expect(d.hint).toBe("error: [Errno 48] Address already in use — reopen tmodel to restart it.");
  });

  it("reports a sidecar that could not start", () => {
    const d = describe(down, { kind: "spawn_failed", error: "No such file" });
    expect(d.text).toBe("could not start the local engine");
    expect(d.hint).toBe("No such file");
  });

  it("explains an external engine that went away", () => {
    expect(describe(down, { kind: "external" }).hint).toContain("tmodel serve");
  });

  it("ignores the process state when the engine answers", () => {
    expect(describe({ kind: "connected", health: okHealth }, { kind: "started" }).tone).toBe(
      "connected",
    );
  });
});
