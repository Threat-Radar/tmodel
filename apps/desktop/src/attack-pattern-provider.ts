import { FixtureAttackPatternDataProvider } from "./attack-pattern-fixture";
import type { AttackPatternDataProvider } from "./attack-pattern-types";
import { EngineAttackPatternDataProvider } from "./engine-attack-pattern-provider";

/** Pages is always fixture-backed and therefore never constructs a localhost provider. */
export function createAttackPatternProvider(
  browserPreview: boolean,
  parameters: Pick<URLSearchParams, "get">,
): AttackPatternDataProvider {
  return browserPreview || parameters.get("attackPatternSource") === "fixture"
    ? new FixtureAttackPatternDataProvider()
    : new EngineAttackPatternDataProvider();
}
