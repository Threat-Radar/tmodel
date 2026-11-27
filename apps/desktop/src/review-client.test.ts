import { describe, expect, it, vi } from "vitest";
import contract from "../../../engine/examples/human-review/contract.json";
import { NO_REVIEW_SESSION, ReviewApiClient } from "./review-client";
import { ReviewApiError, type ContextRequest, type SaveRequest } from "./review-contract";

const TOKEN = "host-issued-token-of-at-least-thirty-two-characters";
const session = { current: () => ({ token: TOKEN }) };

function answer(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("review client (#289 operations)", () => {
  it("posts JSON with the host's bearer session to the documented routes", async () => {
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const path = new URL(String(input)).pathname;
      return answer(200, path === "/reviews/context" ? contract.context.response : contract.save.response);
    });
    const client = new ReviewApiClient(session, "http://127.0.0.1:47811", fetchImpl as unknown as typeof fetch);
    await client.getReviewContext(contract.context.request as ContextRequest);
    await client.saveModelChanges(contract.save.request as SaveRequest);
    await client.refreshModel(contract.refresh_request);
    expect(fetchImpl.mock.calls.map(([url]) => new URL(String(url)).pathname)).toEqual(["/reviews/context", "/reviews/changes", "/reviews/refresh"]);
    for (const [url, init] of fetchImpl.mock.calls as unknown as [URL, RequestInit][]) {
      expect(init.method).toBe("POST");
      expect(init.headers).toEqual({ Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" });
      // The token travels only in the Authorization header.
      expect(String(url)).not.toContain(TOKEN);
      expect(String(init.body)).not.toContain(TOKEN);
    }
    expect(JSON.parse(String((fetchImpl.mock.calls[1] as unknown as [URL, RequestInit])[1].body))).toEqual(contract.save.request);
  });

  it("sends nothing without a verified session, so the app stays read-only", async () => {
    const fetchImpl = vi.fn();
    const client = new ReviewApiClient(NO_REVIEW_SESSION, undefined, fetchImpl as unknown as typeof fetch);
    expect(client.hasSession).toBe(false);
    await expect(client.refreshModel(contract.refresh_request)).rejects.toMatchObject({ kind: "permission" });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("turns engine errors, unreadable answers and an unreachable engine into structured failures", async () => {
    const conflict = contract.errors.find((example) => example.error.code === "revision_conflict");
    const client = (response: () => Promise<Response>) => new ReviewApiClient(session, "http://127.0.0.1:47811", response as unknown as typeof fetch);
    await expect(client(async () => answer(409, conflict)).saveModelChanges(contract.save.request as SaveRequest))
      .rejects.toMatchObject({ kind: "conflict", details: { status: 409, currentRevision: "r2" } });
    await expect(client(async () => new Response("<html>", { status: 502 })).refreshModel(contract.refresh_request))
      .rejects.toMatchObject({ kind: "unexpected", message: "The engine answered HTTP 502." });
    await expect(client(async () => new Response("not json", { status: 200 })).refreshModel(contract.refresh_request))
      .rejects.toMatchObject({ kind: "malformed" });
    await expect(client(async () => { throw new TypeError("Failed to fetch"); }).refreshModel(contract.refresh_request))
      .rejects.toMatchObject({ kind: "network", message: "Could not reach the local engine." });
    // A save answer for the revision it started from is not a new version.
    await expect(client(async () => answer(200, contract.save.response)).saveModelChanges({ ...contract.save.request, expected_revision: "r2" } as SaveRequest))
      .rejects.toBeInstanceOf(ReviewApiError);
  });

  it("lets an abandoned refresh stay abandoned", async () => {
    const controller = new AbortController();
    const client = new ReviewApiClient(session, "http://127.0.0.1:47811", (async (_input: RequestInfo | URL, init?: RequestInit) => {
      controller.abort();
      if (init?.signal?.aborted) throw new DOMException("aborted", "AbortError");
      return answer(200, contract.save.response);
    }) as typeof fetch);
    await expect(client.refreshModel(contract.refresh_request, controller.signal)).rejects.toMatchObject({ name: "AbortError" });
  });
});
