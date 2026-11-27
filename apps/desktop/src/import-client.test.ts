// Contract tests for POST /import/sbom, from the route's shapes and the
// importer's own output for its alpine test files (fixtures/sbom-import-responses.json).
import { describe, expect, it, vi } from "vitest";
import responses from "./fixtures/sbom-import-responses.json";
import {
  fileBase64,
  ImportError,
  importErrorFrom,
  parseImportResult,
  platformProblem,
  SbomImportClient,
  suggestedPlatforms,
} from "./import-client";

const answer = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

describe("SBOM import client", () => {
  it("sends only sbom, scan and platform, with each file's exact bytes in base64", async () => {
    const fetchImpl = vi.fn(async () => answer(responses.success.status, responses.success.body));
    const client = new SbomImportClient("http://127.0.0.1:47811", fetchImpl as unknown as typeof fetch);
    // Bytes that are not UTF-8 must arrive unchanged, which text() would not guarantee.
    const bytes = new Uint8Array([0x7b, 0xff, 0x00, 0xc3, 0x28, 0x7d, 0x0a]);
    const base64 = await fileBase64(new Blob([bytes]));
    expect(Uint8Array.from(atob(base64), (character) => character.charCodeAt(0))).toEqual(bytes);
    await client.importSbom({ sbom: { name: "alpine-3.24.2.cdx.json", base64 }, scan: null, platform: "  " });
    const [url, init] = fetchImpl.mock.calls[0] as unknown as [URL, RequestInit];
    expect(String(url)).toBe("http://127.0.0.1:47811/import/sbom");
    expect(init.method).toBe("POST");
    expect(init.headers).toEqual({ "Content-Type": "application/json" });
    const body = JSON.parse(String(init.body));
    expect(Object.keys(body)).toEqual(["sbom", "scan", "platform"]);
    expect(body).toEqual({ sbom: { name: "alpine-3.24.2.cdx.json", base64 }, scan: null, platform: null });
  });

  it("encodes a file larger than one chunk as one valid base64 text", async () => {
    const bytes = Uint8Array.from({ length: 3 * 0x2000 * 2 + 7 }, (_, index) => (index * 31) % 256);
    const base64 = await fileBase64(new Blob([bytes]));
    expect(Uint8Array.from(atob(base64), (character) => character.charCodeAt(0))).toEqual(bytes);
  });

  it("reads the importer's real answers: model, report, counts and warnings", () => {
    const success = parseImportResult(responses.success.body);
    expect(success.counts).toMatchObject({ components: 17, vulnerabilities: 15, weaknesses: 9, assertions: 45, parties: 4 });
    expect(success.platform).toBe("linux/arm64/v8");
    expect(success.model_text.startsWith("# STARTER MODEL, imported by `tmodel import-sbom`")).toBe(true);
    expect(success.warnings).toEqual([]);
    const warning = parseImportResult(responses.warning.body);
    expect(warning.warnings).toHaveLength(1);
    expect(warning.warnings[0]).toContain("16 of the SBOM's packages are built for arm64");
    expect(suggestedPlatforms(warning.warnings)).toEqual(["linux/arm64/v8"]);
    expect(() => parseImportResult({ ...responses.success.body, counts: { components: -1 } })).toThrow(ImportError);
    expect(() => parseImportResult({ ...responses.success.body, model_text: "" })).toThrow(/no model/);
  });

  it("keeps the importer's refusal message exactly, with its notes and the platform it suggests", async () => {
    const client = new SbomImportClient("http://127.0.0.1:47811", (async () => answer(responses.refusal.status, responses.refusal.body)) as typeof fetch);
    const refusal = await client.importSbom({ sbom: { name: "a.json", base64: "e30=" }, scan: null, platform: null }).catch((error: unknown) => error);
    expect(refusal).toBeInstanceOf(ImportError);
    expect(refusal).toMatchObject({ code: "import_refused", message: responses.refusal.body.error.message, details: { status: 422 } });
    expect(suggestedPlatforms([(refusal as ImportError).message])).toEqual(["linux/arm64/v8"]);
    const noted = importErrorFrom(422, { error: { code: "import_refused", message: "Refused.", notes: ["pass --platform linux/arm/v7", 3] } });
    expect(noted.notes).toEqual(["pass --platform linux/arm/v7"]);
  });

  it.each([
    [422, { error: { code: "validation_error", message: "Bad request.", fields: [{ field: "platform", message: "Not a platform." }] } }, "validation_error"],
    [503, { error: { code: "not_enabled", message: "This engine was started without importing." } }, "not_enabled"],
    [503, { error: { code: "busy", message: "Another import is running." } }, "busy"],
    [408, { error: { code: "request_timeout", message: "The request body did not arrive in time." } }, "request_timeout"],
    [403, { error: { code: "permission_denied", message: "Forbidden host or origin." } }, "permission_denied"],
    [404, { error: { code: "not_found", message: "Unknown operation." } }, "not_found"],
    [500, { error: { code: "internal_error", message: "Import failed." } }, "internal_error"],
  ])("reads an HTTP %i error envelope", (status, body, code) => {
    const error = importErrorFrom(status, body);
    expect(error.code).toBe(code);
    expect(error.message).toBe(body.error.message);
    if (code === "validation_error") expect(error.fields).toEqual([{ field: "platform", message: "Not a platform." }]);
  });

  it("reports an unreachable engine and an unreadable answer", async () => {
    const offline = new SbomImportClient("http://127.0.0.1:47811", (async () => { throw new TypeError("Failed to fetch"); }) as typeof fetch);
    await expect(offline.importSbom({ sbom: { name: "a.json", base64: "" }, scan: null, platform: null })).rejects.toMatchObject({ code: "network_error" });
    const garbled = new SbomImportClient("http://127.0.0.1:47811", (async () => new Response("<html>", { status: 502 })) as typeof fetch);
    await expect(garbled.importSbom({ sbom: { name: "a.json", base64: "" }, scan: null, platform: null })).rejects.toMatchObject({ code: "internal_error", message: "The engine answered HTTP 502." });
  });

  it("checks only the platform's shape, leaving its values to the engine", () => {
    expect(platformProblem("")).toBeNull();
    expect(platformProblem("linux/arm64/v8")).toBeNull();
    expect(platformProblem("linux/amd64")).toBeNull();
    expect(platformProblem("arm64")).toContain("OS/ARCH");
    expect(platformProblem("linux/arm64/v8/extra")).toContain("OS/ARCH");
  });
});
