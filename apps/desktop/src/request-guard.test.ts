import { describe, expect, it } from "vitest";
import { LatestRequestGuard } from "./request-guard";

describe("latest-request guard", () => {
  it("invalidates a stale expansion when selection changes", () => {
    const guard = new LatestRequestGuard();
    const expansion = guard.begin();

    guard.cancel();

    expect(expansion.signal.aborted).toBe(true);
    expect(guard.isCurrent(expansion)).toBe(false);
  });

  it("allows only the newest overlapping expansion to apply", () => {
    const guard = new LatestRequestGuard();
    const firstExpansion = guard.begin();
    const secondExpansion = guard.begin();

    expect(firstExpansion.signal.aborted).toBe(true);
    expect(guard.isCurrent(firstExpansion)).toBe(false);
    expect(guard.isCurrent(secondExpansion)).toBe(true);
  });

  it("prevents a slow path selection from publishing after a newer selection or clear", () => {
    const guard = new LatestRequestGuard();
    const slowSelection = guard.begin();
    const fastSelection = guard.begin();
    expect(guard.isCurrent(slowSelection)).toBe(false);
    expect(guard.isCurrent(fastSelection)).toBe(true);

    guard.cancel();
    expect(fastSelection.signal.aborted).toBe(true);
    expect(guard.isCurrent(fastSelection)).toBe(false);
  });
});
