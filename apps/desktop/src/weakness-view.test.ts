import { afterEach, describe, expect, it, vi } from "vitest";
import fixture from "./fixtures/weakness-table.json";
import { parseWeaknessTableResponse } from "./engine-weakness-provider";
import { applyWeaknessQuery } from "./weakness-fixture";
import type {
  WeaknessDataProvider,
  WeaknessDetailResponse,
  WeaknessTableQuery,
} from "./weakness-types";
import { WeaknessesView, type WeaknessViewElements } from "./weakness-view";

const fixtureResponse = parseWeaknessTableResponse(fixture);

afterEach(() => vi.useRealTimers());

describe("weaknesses view", () => {
  it("renders the table, paging range, attribution, null values, and sort state", async () => {
    const { view, elements } = viewHarness(provider());
    view.activate();
    await settle();

    expect(elements.tableBody.children).toHaveLength(9);
    expect(elements.resultCount.textContent).toBe("9 weaknesses");
    expect(elements.pageStatus.textContent).toBe("1–9 of 9");
    expect(elements.attributionNotice.textContent).toBe(fixture.catalog.notice);
    expect(elements.attributionLicense.textContent).toBe(fixture.catalog.license);
    expect(elements.attributionTerms.href).toBe(fixture.catalog.terms_url);
    const xss = elements.tableBody.children[0];
    expect(xss.children[0].children[0].textContent).toBe("CWE-79");
    const deprecated = elements.tableBody.children[1];
    expect(deprecated.children[6].textContent).toBe("—");
    expect(elements.sortButtons[0].dataset.order).toBe("asc");
    expect(elements.sortButtons[0].parentElement?.getAttribute("aria-sort")).toBe("ascending");
  });

  it("debounces search and passes filters, semantic sorting, and paging to the provider", async () => {
    vi.useFakeTimers();
    const calls: WeaknessTableQuery[] = [];
    const { view, elements } = viewHarness(provider((query) => calls.push({ ...query })));
    view.activate();
    await settle();

    elements.search.value = "  xss  ";
    elements.search.dispatch("input");
    await vi.advanceTimersByTimeAsync(249);
    expect(calls).toHaveLength(1);
    await vi.advanceTimersByTimeAsync(1);
    elements.abstractionFilter.value = "Base";
    elements.abstractionFilter.dispatch("change");
    elements.usageFilter.value = "Allowed";
    elements.usageFilter.dispatch("change");
    const statusSort = elements.sortButtons.find((button) => button.dataset.sort === "status")!;
    statusSort.dispatch("click");
    statusSort.dispatch("click");
    elements.pageSize.value = "50";
    elements.pageSize.dispatch("change");
    await settle();

    expect(calls[calls.length - 1]).toEqual({
      search: "xss",
      abstraction: "Base",
      usage: "Allowed",
      sort: "status",
      order: "desc",
      limit: 50,
      offset: 0,
    });
  });

  it("shows only truthful row details for the fixture", async () => {
    const data = provider(undefined, "row-only");
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectWeakness("CWE-79");

    expect(elements.detailTitle.textContent).toContain("Cross-site Scripting");
    expect(elements.detailId.textContent).toBe("CWE-79");
    expect(elements.detailDescription.textContent).toBe(fixture.rows[0].description);
    expect(elements.detailStatus.textContent).toContain("table rows only");
    expect(elements.detailSections.children).toHaveLength(0);
    expect(elements.search.placeholder).toBe("CWE ID, name, or description");
    expect(data.getWeakness).not.toHaveBeenCalled();
  });

  it("renders full detail fields as text and labels imported assertions as unreviewed proposals", async () => {
    const data = provider();
    data.getWeakness = vi.fn(async () => detailResponse());
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectWeakness("CWE-79");

    const detailText = descendantText(elements.detailSections);
    expect(detailText).toContain("Extended Description");
    expect(detailText).toContain("Safe text alert(1)");
    expect(detailText).not.toContain("<script>");
    expect(detailText).toContain("Term XSS Description A common abbreviation for Cross-Site Scripting.");
    expect(detailText).toContain("Term HTML Injection Description Used as a synonym of stored XSS.");
    expect(detailText.match(/A common abbreviation for Cross-Site Scripting\./g)).toHaveLength(1);
    expect(detailText).toContain("Keep this note");
    expect(detailText).toContain("Encode untrusted output.");
    expect(detailText).toContain("Use a vetted framework.");
    expect(detailText).toContain("Nature: Bad · Language: JavaScript");
    expect(detailText).toContain("const unsafe = input;\nrender(unsafe);");
    expect(detailText).toContain("Updated examples");
    expect(detailText).toContain("Previous Entry Name");
    expect(detailText).toContain("Proposed — not human-reviewed");
    expect(detailText).toContain("Imported relationships are proposals until a human accepts them");
    expect(detailText).toContain("Assertion ID assertion:cwe-79-capec-63");
    expect(detailText).toContain("Asserted by party:mitre-cwe");
    expect(detailText).toContain("Generated by tmodel CWE import: CWE 4.20");
    const renderedLinks = descendantsByTag(elements.detailSections, "a");
    expect(renderedLinks.length).toBeGreaterThan(0);
    expect(renderedLinks.every((link) => {
      const protocol = new URL(link.href).protocol;
      return protocol === "http:" || protocol === "https:";
    })).toBe(true);
    expect(renderedLinks.some((link) => link.textContent === "CVE-2024-0001")).toBe(false);
    expect(descendantsByTag(elements.detailSections, "span").some((identifier) => (
      identifier.className === "weakness-identifier-link"
      && identifier.textContent === "CVE-2024-0001"
    ))).toBe(true);
  });

  it("uses independent native disclosures with accurate counts and deliberate defaults", async () => {
    const data = provider();
    data.getWeakness = vi.fn(async () => detailResponse());
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectWeakness("CWE-79");

    const disclosures = descendantsByTag(elements.detailSections, "details");
    expect(disclosures.length).toBeGreaterThan(10);
    expect(disclosures.every((details) => details.children[0]?.tagName === "summary")).toBe(true);
    expect(disclosure(elements, "Extended Description").open).toBe(true);
    expect(disclosure(elements, "Alternate Terms").open).toBe(true);
    expect(disclosure(elements, "Background and Applicable Platforms").open).toBe(true);
    expect(disclosure(elements, "Common Consequences").open).toBe(true);
    expect(disclosure(elements, "Potential Mitigations").open).toBe(false);
    expect(disclosure(elements, "Demonstrative Examples").open).toBe(false);
    expect(disclosure(elements, "Proposed Relationships").open).toBe(false);
    expect(disclosure(elements, "Content History").open).toBe(false);
    expect(summaryText(disclosure(elements, "Potential Mitigations"))).toContain("2");
    expect(summaryText(disclosure(elements, "Observed Examples and CVE References"))).toContain("1");
    expect(summaryText(disclosure(elements, "Content History"))).toContain("3");

    // Native details/summary controls provide Enter and Space keyboard activation
    // without custom roles or mutually exclusive accordion behavior.
    disclosure(elements, "Extended Description").open = false;
    disclosure(elements, "Alternate Terms").open = true;
    expect(disclosure(elements, "Alternate Terms").open).toBe(true);
  });

  it("resets disclosure defaults when a different weakness is selected", async () => {
    const data = provider();
    data.getWeakness = vi.fn(async (id) => ({
      ...detailResponse(),
      id,
      entry: { ...detailResponse().entry!, id, name: `${id} detail` },
    }));
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectWeakness("CWE-79");
    disclosure(elements, "Extended Description").open = false;
    disclosure(elements, "Potential Mitigations").open = true;

    await view.selectWeakness("CWE-373");
    expect(elements.detailTitle.textContent).toBe("CWE-373 detail");
    expect(disclosure(elements, "Extended Description").open).toBe(true);
    expect(disclosure(elements, "Potential Mitigations").open).toBe(false);
  });

  it("keeps table and detail failures independent and offers each retry", async () => {
    const data = provider();
    data.getWeakness = vi.fn()
      .mockRejectedValueOnce(new Error("detail unavailable"))
      .mockResolvedValueOnce(detailResponse());
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectWeakness("CWE-79");

    expect(elements.tableBody.children).toHaveLength(9);
    expect(elements.retryButton.hidden).toBe(true);
    expect(elements.detailStatus.textContent).toContain("detail unavailable");
    expect(elements.detailRetryButton.hidden).toBe(false);
    elements.detailRetryButton.dispatch("click");
    await settle();
    expect(elements.detailRetryButton.hidden).toBe(true);
    expect(elements.detailStatus.textContent).toBe("");
    expect(data.getWeakness).toHaveBeenCalledTimes(2);
  });

  it("announces loading, empty results, table errors, and a successful table retry", async () => {
    const pending = deferred<ReturnType<typeof applyWeaknessQuery>>();
    const data = provider();
    data.getTable = vi.fn()
      .mockImplementationOnce(() => pending.promise)
      .mockRejectedValueOnce(new Error("catalog unavailable"))
      .mockResolvedValueOnce(applyWeaknessQuery(fixtureResponse, {
        sort: "id", order: "asc", limit: 25, offset: 0,
      }));
    const { view, elements } = viewHarness(data);

    view.activate();
    expect(elements.workspace.getAttribute("aria-busy")).toBe("true");
    expect(elements.requestStatus.textContent).toBe("Loading CWE weaknesses…");
    pending.resolve(applyWeaknessQuery(fixtureResponse, {
      search: "no such weakness", sort: "id", order: "asc", limit: 25, offset: 0,
    }));
    await settle();
    expect(elements.emptyState.hidden).toBe(false);
    expect(elements.requestStatus.textContent).toContain("No CWE weaknesses");

    await view.retry();
    expect(elements.requestStatus.textContent).toContain("catalog unavailable");
    expect(elements.retryButton.hidden).toBe(false);
    elements.retryButton.dispatch("click");
    await settle();
    expect(elements.tableBody.children).toHaveLength(9);
    expect(elements.retryButton.hidden).toBe(true);
  });

  it("moves to the next and previous server page", async () => {
    const calls: WeaknessTableQuery[] = [];
    const data = provider((query) => calls.push({ ...query }));
    data.getTable = vi.fn(async (query) => {
      calls.push({ ...query });
      const page = applyWeaknessQuery(fixtureResponse, query);
      return { ...page, total: 60 };
    });
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();

    expect(elements.nextPage.disabled).toBe(false);
    elements.nextPage.dispatch("click");
    await settle();
    expect(calls[calls.length - 1].offset).toBe(25);
    elements.previousPage.dispatch("click");
    await settle();
    expect(calls[calls.length - 1].offset).toBe(0);
  });

  it("does not let stale table or detail requests replace newer selections", async () => {
    const firstTable = deferred<ReturnType<typeof applyWeaknessQuery>>();
    const secondTable = deferred<ReturnType<typeof applyWeaknessQuery>>();
    const firstDetail = deferred<WeaknessDetailResponse | undefined>();
    const secondDetail = deferred<WeaknessDetailResponse | undefined>();
    const data = provider();
    data.getTable = vi.fn()
      .mockResolvedValueOnce(applyWeaknessQuery(fixtureResponse, {
        sort: "id", order: "asc", limit: 25, offset: 0,
      }))
      .mockImplementationOnce(() => firstTable.promise)
      .mockImplementationOnce(() => secondTable.promise);
    data.getWeakness = vi.fn()
      .mockImplementationOnce(() => firstDetail.promise)
      .mockImplementationOnce(() => secondDetail.promise);
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();

    elements.statusFilter.value = "Stable";
    elements.statusFilter.dispatch("change");
    elements.statusFilter.value = "Draft";
    elements.statusFilter.dispatch("change");
    secondTable.resolve(applyWeaknessQuery(fixtureResponse, {
      status: "Draft", sort: "id", order: "asc", limit: 25, offset: 0,
    }));
    await settle();
    firstTable.resolve(applyWeaknessQuery(fixtureResponse, {
      status: "Stable", sort: "id", order: "asc", limit: 25, offset: 0,
    }));
    await settle();
    expect(elements.tableBody.children).toHaveLength(3);

    const selectFirst = view.selectWeakness("CWE-689");
    const selectSecond = view.selectWeakness("CWE-692");
    secondDetail.resolve({
      ...detailResponse(), id: "CWE-692", entry: { ...detailResponse().entry!, id: "CWE-692", name: "Newest detail" },
    });
    await selectSecond;
    firstDetail.resolve(detailResponse());
    await selectFirst;
    expect(elements.detailTitle.textContent).toBe("Newest detail");
  });
});

function provider(
  onQuery: ((query: WeaknessTableQuery) => void) | undefined = undefined,
  detailLevel: "full" | "row-only" = "full",
): WeaknessDataProvider {
  return {
    metadata: { source: detailLevel === "full" ? "engine" : "fixture", notice: "test CWE data", detailLevel },
    getTable: vi.fn(async (query) => {
      onQuery?.(query);
      return applyWeaknessQuery(fixtureResponse, query);
    }),
    getWeakness: vi.fn(async () => detailLevel === "full" ? detailResponse() : undefined),
  };
}

function detailResponse(): WeaknessDetailResponse {
  return {
    catalog: fixtureResponse.catalog,
    id: "CWE-79",
    entry: {
      id: "CWE-79",
      kind: "Weakness",
      name: fixture.rows[0].name,
      status: "Stable",
      abstraction: "Base",
      structure: "Simple",
      view_type: null,
      usage: "Allowed",
      likelihood: "High",
      description: fixture.rows[0].description,
      alternate_terms: ["XSS"],
      attack_patterns: ["CAPEC-63"],
      observed_examples: [{
        reference: "CVE-2024-0001",
        description: "Observed in the wild",
        link: "javascript:alert(1)",
      }],
      mitigations: 2,
      url: fixture.rows[0].url,
      fields: {
        Extended_Description: [{ "#xhtml": "<p>Safe text</p><script>alert(1)</script>" }],
        Alternate_Terms: [{
          Alternate_Term: [
            {
              Term: ["XSS"],
              Description: ["A common abbreviation for Cross-Site Scripting."],
            },
            {
              Term: ["HTML Injection"],
              Description: ["Used as a synonym of stored XSS."],
            },
          ],
        }],
        Background_Details: [{
          Background_Detail: [{ "#xhtml": "<p>Browser security model background.</p>" }],
        }],
        Applicable_Platforms: [{
          Language: [{ "@Class": "Not Language-Specific" }],
          Technology: [{ "@Class": "Web Based", "@Prevalence": "Often" }],
        }],
        Modes_Of_Introduction: [{
          Introduction: [{ Phase: ["Implementation"], Note: ["Introduced during implementation."] }],
        }],
        Common_Consequences: [{
          Consequence: [{ Scope: ["Confidentiality"], Impact: ["Read Application Data"] }],
        }],
        Detection_Methods: [{
          Detection_Method: [{ Method: ["Automated Static Analysis"], Description: ["Inspect output encoding."] }],
        }],
        Potential_Mitigations: [{
          Mitigation: [
            { Phase: ["Implementation"], Description: ["Encode untrusted output."] },
            { Phase: ["Architecture and Design"], Description: ["Use a vetted framework."] },
          ],
        }],
        Demonstrative_Examples: [{
          Demonstrative_Example: [{
            "#items": [
              { Intro_Text: "Untrusted input is rendered directly." },
              {
                Example_Code: {
                  "@Nature": "Bad",
                  "@Language": "JavaScript",
                  "#xhtml": "<div>const unsafe = input;<br/>render(unsafe);</div>",
                },
              },
              { Body_Text: "The browser interprets the untrusted value." },
            ],
          }],
        }],
        Taxonomy_Mappings: [{
          Taxonomy_Mapping: [{ "@Taxonomy_Name": "OWASP Top Ten", Entry_ID: ["A03"] }],
        }],
        Notes: [{ Note: ["Keep this note"] }],
        Content_History: [{
          Submission: [{ Submission_Date: ["2006-07-19"] }],
          Modification: [
            { Modification_Date: ["2025-01-01"], Modification_Comment: ["Updated examples"] },
          ],
          Previous_Entry_Name: [{ "@Date": "2008-04-11", "#text": "Cross-site Scripting" }],
        }],
      },
    },
    objects: {
      parties: [],
      weaknesses: [],
      attack_patterns: [],
      vulnerabilities: [],
      assertions: [{
        id: "assertion:cwe-79-capec-63",
        name: "CWE-79 is exploited by CAPEC-63",
        subject: "weakness:cwe-79",
        predicate: "exploited_by",
        object: "attack-pattern:capec-63",
        assertion_status: "proposed",
        asserted_by: "party:mitre-cwe",
        generated_by: "tmodel CWE import: CWE 4.20 (2026-04-30), cwec_v4.20.xml.zip, SHA-256 3976f599",
      }],
    },
  };
}

function viewHarness(data: WeaknessDataProvider) {
  const documentRoot = new FakeDocument();
  const make = (tag = "div") => documentRoot.createElement(tag);
  const sortButtons = ["id", "name", "abstraction", "structure", "status", "usage", "likelihood"]
    .map((sort) => {
      const header = make("th");
      const button = make("button");
      button.dataset.sort = sort;
      header.append(button);
      return button;
    });
  const elements = {
    workspace: make(),
    sourceNotice: make(),
    search: make("input"),
    abstractionFilter: make("select"),
    structureFilter: make("select"),
    statusFilter: make("select"),
    usageFilter: make("select"),
    sortButtons,
    resultCount: make(),
    requestStatus: make(),
    warning: make(),
    retryButton: make("button"),
    tableRegion: make(),
    tableBody: make("tbody"),
    emptyState: make(),
    pageSize: make("select"),
    previousPage: make("button"),
    nextPage: make("button"),
    pageStatus: make(),
    sortHelp: make(),
    attributionNotice: make(),
    attributionLicense: make(),
    attributionTerms: make("a"),
    detailTitle: make(),
    detailId: make(),
    detailBadges: make(),
    detailDescription: make(),
    detailList: make("dl"),
    detailStatus: make(),
    detailRetryButton: make("button"),
    detailSections: make(),
  };
  elements.pageSize.value = "25";
  elements.warning.hidden = true;
  elements.retryButton.hidden = true;
  elements.detailRetryButton.hidden = true;
  elements.tableRegion.hidden = true;
  elements.emptyState.hidden = true;
  return {
    elements,
    view: new WeaknessesView(
      data,
      elements as unknown as WeaknessViewElements,
      documentRoot as unknown as Document,
    ),
  };
}

function descendantText(element: FakeElement): string {
  return [element.textContent, ...element.children.map(descendantText)].filter(Boolean).join(" ");
}

function descendantsByTag(element: FakeElement, tagName: string): FakeElement[] {
  return element.children.flatMap((child) => [
    ...(child.tagName === tagName ? [child] : []),
    ...descendantsByTag(child, tagName),
  ]);
}

function disclosure(elements: { detailSections: FakeElement }, title: string): FakeElement {
  const match = descendantsByTag(elements.detailSections, "details")
    .find((details) => summaryText(details).includes(title));
  if (!match) throw new Error(`Missing disclosure ${title}`);
  return match;
}

function summaryText(details: FakeElement): string {
  const summary = details.children.find((child) => child.tagName === "summary");
  return summary ? descendantText(summary) : "";
}

async function settle(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((done, fail) => {
    resolve = done;
    reject = fail;
  });
  return { promise, resolve, reject };
}

class FakeDocument {
  createElement(tagName: string): FakeElement {
    return new FakeElement(tagName);
  }

  createTextNode(text: string): FakeElement {
    const node = new FakeElement("#text");
    node.textContent = text;
    return node;
  }
}

class FakeElement {
  readonly children: FakeElement[] = [];
  readonly dataset: Record<string, string> = {};
  readonly classList = new FakeClassList(this);
  parentElement?: FakeElement;
  textContent = "";
  className = "";
  hidden = false;
  disabled = false;
  value = "";
  type = "";
  title = "";
  placeholder = "";
  href = "";
  target = "";
  rel = "";
  open = false;
  private readonly attributes = new Map<string, string>();
  private readonly listeners = new Map<string, Array<() => void>>();

  constructor(readonly tagName: string) {}

  addEventListener(type: string, listener: EventListenerOrEventListenerObject): void {
    const callbacks = this.listeners.get(type) ?? [];
    callbacks.push(() => typeof listener === "function"
      ? listener(new Event(type))
      : listener.handleEvent(new Event(type)));
    this.listeners.set(type, callbacks);
  }

  dispatch(type: string): void {
    for (const callback of this.listeners.get(type) ?? []) callback();
  }

  append(...nodes: FakeElement[]): void {
    for (const node of nodes) {
      node.parentElement = this;
      this.children.push(node);
    }
  }

  replaceChildren(...nodes: FakeElement[]): void {
    this.children.length = 0;
    this.append(...nodes);
  }

  setAttribute(name: string, value: string): void {
    this.attributes.set(name, value);
  }

  getAttribute(name: string): string | null {
    return this.attributes.get(name) ?? null;
  }

  querySelectorAll<T extends Element>(selector: string): T[] {
    const matches: FakeElement[] = [];
    const visit = (node: FakeElement) => {
      if (selector === "tr" && node.tagName === "tr") matches.push(node);
      for (const child of node.children) visit(child);
    };
    for (const child of this.children) visit(child);
    return matches as unknown as T[];
  }

  closest(selector: string): FakeElement | null {
    let current: FakeElement | undefined = this;
    while (current) {
      if (selector === "th" && current.tagName === "th") return current;
      current = current.parentElement;
    }
    return null;
  }
}

class FakeClassList {
  private readonly values = new Set<string>();
  constructor(private readonly owner: FakeElement) {}

  toggle(name: string, force?: boolean): boolean {
    const add = force ?? !this.values.has(name);
    if (add) this.values.add(name);
    else this.values.delete(name);
    this.owner.className = [...this.values].join(" ");
    return add;
  }
}
