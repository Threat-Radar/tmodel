import { describe, expect, it } from "vitest";
import { EngineSdlDataProvider, parseSdlModels, parseSdlView } from "./engine-sdl-provider";
import fixture from "./fixtures/sdl-01-view.json";

function fetchReturning(status: number, body: unknown, seen: URL[] = []): typeof fetch {
  return (async (input: RequestInfo | URL) => {
    seen.push(new URL(String(input)));
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
  }) as typeof fetch;
}

describe("engine SDL provider", () => {
  it("lists models and loads a view with file and program parameters", async () => {
    const seen: URL[] = [];
    const list = new EngineSdlDataProvider("http://127.0.0.1:47811", fetchReturning(200, { models: [{ file: "sdl-01.yaml" }] }, seen));
    expect(await list.listModels()).toEqual([{ file: "sdl-01.yaml" }]);
    expect(seen[0].pathname).toBe("/sdl");
    expect(seen[0].search).toBe("");

    const view = new EngineSdlDataProvider("http://127.0.0.1:47811/", fetchReturning(200, fixture, seen));
    const loaded = await view.getView("sdl-01-tmodel-desktop.yaml", "security-program:tmodel-sdl");
    expect(loaded.phases.length).toBeGreaterThan(0);
    expect(seen[1].searchParams.get("file")).toBe("sdl-01-tmodel-desktop.yaml");
    expect(seen[1].searchParams.get("program")).toBe("security-program:tmodel-sdl");
  });

  it("surfaces the engine's error message", async () => {
    const provider = new EngineSdlDataProvider(undefined, fetchReturning(400, { error: "mvp-01.yaml: not an SDL model" }));
    await expect(provider.getView("mvp-01.yaml")).rejects.toThrow("not an SDL model");
  });

  it("rejects payloads of the wrong shape", () => {
    expect(() => parseSdlModels({ models: [{}] })).toThrow();
    expect(() => parseSdlView({ file: "x" })).toThrow();
    expect(parseSdlView(fixture).file).toBe("sdl-01-tmodel-desktop.yaml");
  });
});
