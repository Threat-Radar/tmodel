import { describe, expect, it } from "vitest";
import { createWeaknessProvider } from "./weakness-provider";

describe("weakness provider selection", () => {
  it("always uses the fixture in the browser preview", () => {
    expect(createWeaknessProvider(true, new URLSearchParams()).metadata.source).toBe("fixture");
  });

  it("supports the explicit development fixture without changing desktop's default", () => {
    expect(createWeaknessProvider(false, new URLSearchParams("weaknessSource=fixture"))
      .metadata.source).toBe("fixture");
    expect(createWeaknessProvider(false, new URLSearchParams()).metadata.source).toBe("engine");
  });
});
