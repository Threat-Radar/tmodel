import { EngineWeaknessDataProvider } from "./engine-weakness-provider";
import { FixtureWeaknessDataProvider } from "./weakness-fixture";
import type { WeaknessDataProvider } from "./weakness-types";

/** Pages is always fixture-backed and therefore never constructs a localhost provider. */
export function createWeaknessProvider(
  browserPreview: boolean,
  parameters: Pick<URLSearchParams, "get">,
): WeaknessDataProvider {
  return browserPreview || parameters.get("weaknessSource") === "fixture"
    ? new FixtureWeaknessDataProvider()
    : new EngineWeaknessDataProvider();
}
