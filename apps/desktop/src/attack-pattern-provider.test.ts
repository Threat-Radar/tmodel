import { describe, expect, it } from "vitest";
import { createAttackPatternProvider } from "./attack-pattern-provider";

describe("attack-pattern provider selection", () => {
  it("always uses the fixture in the browser preview", () => {
    expect(createAttackPatternProvider(true, new URLSearchParams()).metadata.source).toBe("fixture");
    expect(createAttackPatternProvider(true, new URLSearchParams("attackPatternSource=engine"))
      .metadata.source).toBe("fixture");
  });

  it("supports the explicit development fixture without changing desktop's default", () => {
    expect(createAttackPatternProvider(false, new URLSearchParams("attackPatternSource=fixture"))
      .metadata.source).toBe("fixture");
    expect(createAttackPatternProvider(false, new URLSearchParams()).metadata.source).toBe("engine");
    // The weakness switch is its own: it does not move the CAPEC table off the engine.
    expect(createAttackPatternProvider(false, new URLSearchParams("weaknessSource=fixture"))
      .metadata.source).toBe("engine");
  });
});
