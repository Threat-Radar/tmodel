import { describe, expect, it } from "vitest";
import {
  attackTechniqueUrl,
  capecDefinitionUrl,
  CatalogEntryRenderer,
  cweDefinitionUrl,
  displayValue,
  PROPOSED_LABEL,
} from "./catalog-entry-render";

describe("catalog entry rendering", () => {
  it("links CAPEC, CWE and ATT&CK ids to their official pages, and nothing else", () => {
    expect(capecDefinitionUrl("CAPEC-66")).toBe("https://capec.mitre.org/data/definitions/66.html");
    expect(cweDefinitionUrl("CWE-1286")).toBe("https://cwe.mitre.org/data/definitions/1286.html");
    expect(attackTechniqueUrl("T1083")).toBe("https://attack.mitre.org/techniques/T1083/");
    expect(attackTechniqueUrl("T1574.011")).toBe("https://attack.mitre.org/techniques/T1574/011/");
    for (const id of ["CAPEC-", "CAPEC-66abc", "javascript:alert(1)", "248"]) {
      expect(capecDefinitionUrl(id)).toBeUndefined();
    }
    for (const id of ["CWE-", "CWE-89x", "89"]) expect(cweDefinitionUrl(id)).toBeUndefined();
    for (const id of ["1574.011", "T157", "T1574.01", "t1083"]) expect(attackTechniqueUrl(id)).toBeUndefined();
  });

  it("gives each inspector its own class names for the same structure", () => {
    for (const prefix of ["weakness", "attack-pattern"] as const) {
      const renderer = new CatalogEntryRenderer(new FakeDocument() as unknown as Document, prefix);
      const [section] = renderer.itemSection(
        { fields: { Prerequisites: [{ Prerequisite: ["SQL queries used by the application to store, retrieve or modify data."] }] } },
        "Prerequisites",
        "Prerequisites",
        ["Prerequisite"],
      );
      const body = section as unknown as FakeElement;
      expect(body.className).toBe(`${prefix}-detail-section`);
      expect(body.children[1].className).toBe(`${prefix}-detail-section-body`);
      expect(body.children[1].children[0].className).toBe(`${prefix}-detail-items`);
    }
  });

  it("labels a proposed assertion as unreviewed and shows its provenance", () => {
    const renderer = new CatalogEntryRenderer(new FakeDocument() as unknown as Document, "attack-pattern");
    // The CAPEC import's Assertion for CAPEC-66 and CWE-89 (attack-pattern-details.json).
    const [section] = renderer.assertions([{
      id: "assertion:capec-66-related-weakness-cwe-89",
      name: "CWE-89 is exploited by CAPEC-66",
      subject: "weakness:cwe-89",
      predicate: "exploited_by",
      object: "attack-pattern:capec-66",
      assertion_status: "proposed",
      asserted_by: "party:mitre-capec",
      generated_by: "tmodel CAPEC import: CAPEC 3.9 (2023-01-24)",
    }]);
    const text = allText(section as unknown as FakeElement);
    expect(text).toContain(`CWE-89 is exploited by CAPEC-66 · ${PROPOSED_LABEL}`);
    expect(PROPOSED_LABEL).toBe("Proposed, not human-reviewed");
    expect(text).toContain("weakness:cwe-89 exploited_by attack-pattern:capec-66");
    expect(displayValue("Likelihood_Of_Attack")).toBe("Likelihood Of Attack");
  });
});

function allText(element: FakeElement): string {
  return [element.textContent, ...element.children.map(allText)].filter(Boolean).join(" ");
}

class FakeDocument {
  createElement(tagName: string): FakeElement {
    return new FakeElement(tagName);
  }
}

class FakeElement {
  readonly children: FakeElement[] = [];
  textContent = "";
  className = "";
  open = false;
  href = "";
  target = "";
  rel = "";
  private readonly attributes = new Map<string, string>();

  constructor(readonly tagName: string) {}

  append(...nodes: FakeElement[]): void {
    this.children.push(...nodes);
  }

  setAttribute(name: string, value: string): void {
    this.attributes.set(name, value);
  }
}
