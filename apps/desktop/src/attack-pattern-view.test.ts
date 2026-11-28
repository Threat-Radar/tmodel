import { afterEach, describe, expect, it, vi } from "vitest";
import details from "./fixtures/attack-pattern-details.json";
import table from "./fixtures/attack-pattern-table.json";
import {
  applyAttackPatternQuery,
  FixtureAttackPatternDataProvider,
  parseAttackPatternDetailFixture,
} from "./attack-pattern-fixture";
import type {
  AttackPatternDataProvider,
  AttackPatternDetailResponse,
  AttackPatternTableQuery,
  AttackPatternTableResponse,
} from "./attack-pattern-types";
import {
  AttackPatternsView,
  attributionSummary,
  NOT_STATED,
  publicationDate,
  type AttackPatternViewElements,
} from "./attack-pattern-view";
import { parseAttackPatternTableResponse } from "./engine-attack-pattern-provider";

// Every row and answer below is the engine's, over the 13 CAPEC 3.9 entries of the sample.
const source = parseAttackPatternTableResponse(table);
const answers = parseAttackPatternDetailFixture(details);
const alternateTerms = new Map([...answers].map(([id, answer]) => [id, answer.entry?.alternate_terms ?? []]));
const SORTS = ["id", "name", "abstraction", "status", "likelihood", "severity"];

afterEach(() => vi.useRealTimers());

describe("attack patterns view", () => {
  it("renders every row with the API's fields, the paging range, attribution and sort state", async () => {
    const { view, elements } = viewHarness(provider());
    view.activate();
    await settle();

    expect(elements.tableBody.children).toHaveLength(13);
    expect(elements.pageStatus.textContent).toBe("1–13 of 13");
    expect([elements.previousPage.hidden, elements.nextPage.hidden]).toEqual([true, true]);
    expect(elements.tableRegion.hidden).toBe(false);
    expect(elements.emptyState.hidden).toBe(true);
    const sql = rowFor(elements, "CAPEC-66");
    expect(sql.children.map((cell) => descendantText(cell))).toEqual([
      "CAPEC-66", "SQL Injection", "Standard", "Draft", "High", "High", "2", "0", "4", "3",
    ]);
    expect(sql.children.slice(6).map((cell) => cell.getAttribute("aria-label"))).toEqual([
      "2 related CWE weaknesses", "0 ATT&CK techniques", "4 attack steps", "3 mitigations",
    ]);
    expect(rowFor(elements, "CAPEC-497").children[7].getAttribute("aria-label")).toBe("1 ATT&CK technique");
    // CAPEC gives CAPEC-115 no likelihood of attack and CAPEC-602 no likelihood or severity.
    expect(descendantText(rowFor(elements, "CAPEC-115").children[4])).toBe(NOT_STATED);
    expect(descendantsByClass(rowFor(elements, "CAPEC-602"), "attack-pattern-missing")).toHaveLength(2);
    expect(elements.attribution.hidden).toBe(false);
    expect(elements.attributionSummary.textContent).toBe("© 2007-2023 The MITRE Corporation · CAPEC Terms of Use");
    expect(elements.attributionNotice.textContent).toBe(table.catalog.notice);
    expect(elements.attributionLicense.textContent).toBe(table.catalog.license);
    expect(elements.attributionTerms.href).toBe("https://capec.mitre.org/about/termsofuse.html");
    expect(elements.sortButtons[0].dataset.order).toBe("asc");
    expect(elements.sortButtons[0].parentElement?.getAttribute("aria-sort")).toBe("ascending");
    expect(elements.sortButtons.slice(1).every((button) => button.parentElement?.getAttribute("aria-sort") === "none"))
      .toBe(true);
    expect(elements.sourceNotice.textContent).toBe("test CAPEC data");
    expect(elements.workspace.getAttribute("aria-busy")).toBe("false");
  });

  it("debounces search and sends filters, sort direction and a reset offset to the provider", async () => {
    vi.useFakeTimers();
    const calls: AttackPatternTableQuery[] = [];
    const { view, elements } = viewHarness(provider((query) => calls.push({ ...query })));
    view.activate();
    await settle();

    elements.search.value = "  injection  ";
    elements.search.dispatch("input");
    await vi.advanceTimersByTimeAsync(249);
    expect(calls).toHaveLength(1);
    await vi.advanceTimersByTimeAsync(1);
    expect(calls[1]).toMatchObject({ search: "injection", offset: 0 });
    for (const [filter, value] of [
      [elements.abstractionFilter, "Standard"],
      [elements.statusFilter, "Draft"],
      [elements.likelihoodFilter, "High"],
      [elements.severityFilter, "High"],
    ] as const) {
      filter.value = value;
      filter.dispatch("change");
    }
    const severity = elements.sortButtons.find((button) => button.dataset.sort === "severity")!;
    severity.dispatch("click");
    severity.dispatch("click");
    await settle();

    expect(calls[calls.length - 1]).toEqual({
      search: "injection",
      abstraction: "Standard",
      status: "Draft",
      likelihood: "High",
      severity: "High",
      sort: "severity",
      order: "desc",
      limit: 50,
      offset: 0,
    });
    expect(elements.tableBody.children.map((row) => row.dataset.attackPatternId)).toEqual(["CAPEC-66", "CAPEC-88"]);
    expect(severity.parentElement?.getAttribute("aria-sort")).toBe("descending");
    expect(elements.sortHelp.textContent).toBe(
      "Severity sorted descending. Ascending follows CAPEC's order: Very High, High, Medium, Low, Very Low. "
        + "Attack patterns without a value come last either way. Select the column again to reverse it.",
    );
  });

  it("searches immediately on Enter or clearing and keeps the debounce from firing twice", async () => {
    vi.useFakeTimers();
    const calls: AttackPatternTableQuery[] = [];
    const { view, elements } = viewHarness(provider((query) => calls.push({ ...query })));
    view.activate();
    await settle();
    elements.search.value = "HTTP Desync";
    elements.search.dispatch("input");
    elements.search.dispatch("search");
    await settle();
    await vi.advanceTimersByTimeAsync(300);
    expect(calls.map((query) => query.search)).toEqual([undefined, "HTTP Desync"]);
    expect(elements.tableBody.children.map((row) => row.dataset.attackPatternId)).toEqual(["CAPEC-273"]);
  });

  it("lists each filter's values in CAPEC's own order with contextual counts", async () => {
    const { view, elements } = viewHarness(provider());
    view.activate();
    await settle();

    expect(optionTexts(elements.abstractionFilter)).toEqual(["All abstractions", "Meta (3)", "Standard (6)", "Detailed (4)"]);
    expect(optionTexts(elements.statusFilter)).toEqual([
      "All statuses", "Stable (2)", "Usable (1)", "Draft (8)", "Obsolete (1)", "Deprecated (1)",
    ]);
    expect(optionTexts(elements.likelihoodFilter)).toEqual(["All likelihoods", "High (6)", "Medium (3)", "Low (2)"]);
    expect(optionTexts(elements.severityFilter)).toEqual([
      "All severities", "Very High (3)", "High (6)", "Medium (1)", "Low (1)", "Very Low (1)",
    ]);

    elements.statusFilter.value = "Draft";
    elements.statusFilter.dispatch("change");
    await settle();
    // Each facet leaves out its own filter, so every status stays selectable.
    expect(optionTexts(elements.statusFilter)).toHaveLength(6);
    expect(optionTexts(elements.severityFilter)).toEqual([
      "All severities", "Very High (2)", "High (4)", "Medium (1)", "Very Low (1)",
    ]);
    expect(elements.statusFilter.value).toBe("Draft");
  });

  it("opens the inspector from keyboard activation and returns focus to the selected row", async () => {
    const data = provider();
    const pending = deferred<AttackPatternDetailResponse | undefined>();
    data.getAttackPattern = vi.fn(() => pending.promise);
    const { view, elements, documentRoot } = viewHarness(data);
    view.activate();
    await settle();

    const firstRowButton = rowFor(elements, "CAPEC-5").children[0].children[0];
    const secondRowButton = rowFor(elements, "CAPEC-7").children[0].children[0];
    expect(elements.backToRow.hidden).toBe(true);
    firstRowButton.focus();
    firstRowButton.dispatch("click", 0);
    expect(documentRoot.activeElement).toBe(elements.inspector);
    expect(elements.detailId.textContent).toBe("CAPEC-5");
    expect(elements.detailStatus.textContent).toBe("Loading full CAPEC details…");
    expect(firstRowButton.getAttribute("aria-current")).toBe("true");
    expect(elements.backToRow.hidden).toBe(false);

    elements.backToRow.focus();
    pending.resolve(answers.get("CAPEC-5"));
    await settle();
    expect(documentRoot.activeElement).toBe(elements.backToRow);
    elements.backToRow.dispatch("click", 0);
    expect(documentRoot.activeElement).toBe(firstRowButton);

    secondRowButton.focus();
    secondRowButton.dispatch("click", 1);
    expect(documentRoot.activeElement).toBe(secondRowButton);
    expect(secondRowButton.getAttribute("aria-current")).toBe("true");
    expect(firstRowButton.getAttribute("aria-current")).toBeNull();
    elements.backToRow.dispatch("click", 0);
    expect(documentRoot.activeElement).toBe(secondRowButton);
  });

  it("keeps focus on sort and filter controls and returns to the selected row after sorting", async () => {
    const { view, elements, documentRoot } = viewHarness(provider());
    view.activate();
    await settle();

    rowFor(elements, "CAPEC-66").children[0].children[0].dispatch("click", 0);
    const nameSort = elements.sortButtons.find((button) => button.dataset.sort === "name")!;
    nameSort.focus();
    nameSort.dispatch("click", 0);
    await settle();
    expect(documentRoot.activeElement).toBe(nameSort);
    const selectedButton = rowFor(elements, "CAPEC-66").children[0].children[0];
    elements.backToRow.dispatch("click", 0);
    expect(documentRoot.activeElement).toBe(selectedButton);
    expect(selectedButton.getAttribute("aria-current")).toBe("true");

    elements.statusFilter.focus();
    elements.statusFilter.value = "Deprecated";
    elements.statusFilter.dispatch("change");
    await settle();
    expect(documentRoot.activeElement).toBe(elements.statusFilter);
    expect(elements.backToRow.hidden).toBe(true);
    expect(view.currentSelection()).toBeUndefined();
  });

  it("keeps keyboard focus on the inspector's definition link when full details arrive", async () => {
    const data = provider();
    const pending = deferred<AttackPatternDetailResponse | undefined>();
    data.getAttackPattern = vi.fn(() => pending.promise);
    const { view, elements, documentRoot } = viewHarness(data);
    view.activate();
    await settle();

    rowFor(elements, "CAPEC-66").children[0].children[0].dispatch("click", 0);
    const [previewLink] = descendantsByTag(elements.detailList, "a");
    previewLink.focus();
    pending.resolve(answers.get("CAPEC-66"));
    await settle();

    const fullDetailLink = elements.detailList.querySelector("a");
    expect(fullDetailLink).not.toBe(previewLink);
    expect(documentRoot.activeElement).toBe(fullDetailLink);
  });

  it("restores row focus after a table refresh while that row stays visible", async () => {
    const { view, elements, documentRoot } = viewHarness(provider());
    view.activate();
    await settle();

    const rowButton = rowFor(elements, "CAPEC-66").children[0].children[0];
    rowButton.focus();
    await view.retry();
    const refreshedButton = rowFor(elements, "CAPEC-66").children[0].children[0];
    expect(refreshedButton).not.toBe(rowButton);
    expect(documentRoot.activeElement).toBe(refreshedButton);
  });

  it("moves focus from the inspector to the table when a search removes the selected row", async () => {
    const data = provider();
    const pending = deferred<AttackPatternTableResponse>();
    vi.mocked(data.getTable).mockResolvedValueOnce(answer({})).mockReturnValueOnce(pending.promise);
    const { view, elements, documentRoot } = viewHarness(data);
    view.activate();
    await settle();

    rowFor(elements, "CAPEC-66").children[0].children[0].dispatch("click", 0);
    await settle();
    elements.search.focus();
    elements.search.value = "HTTP Desync";
    elements.search.dispatch("search");
    expect(documentRoot.activeElement).toBe(elements.search);
    disclosure(elements, "Related CWE Weaknesses").children[0].focus();
    pending.resolve(answer({ search: "HTTP Desync" }));
    await settle();

    expect(view.currentSelection()).toBeUndefined();
    expect(elements.backToRow.hidden).toBe(true);
    expect(documentRoot.activeElement).toBe(elements.tableRegion);
  });

  it("shows a selected row's summary at once, then every field of the engine's entry", async () => {
    const data = provider();
    const pending = deferred<AttackPatternDetailResponse | undefined>();
    data.getAttackPattern = vi.fn(() => pending.promise);
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();

    const selection = view.selectAttackPattern("CAPEC-66");
    expect(elements.detailTitle.textContent).toBe("SQL Injection");
    expect(elements.detailId.textContent).toBe("CAPEC-66");
    expect(elements.detailDescription.textContent).toBe(table.rows[4].description);
    expect(elements.detailStatus.textContent).toBe("Loading full CAPEC details…");
    expect(detailRows(elements)).toEqual([
      ["Abstraction", "Standard"],
      ["Likelihood of attack", "High"],
      ["Typical severity", "High"],
      ["Related CWE weaknesses", "2"],
      ["ATT&CK techniques", "0"],
      ["Related attack patterns", "1"],
      ["Attack steps", "4"],
      ["Mitigations", "3"],
      ["Examples", "1"],
      ["tmodel object", "attack-pattern:capec-66"],
      ["Official definition", "View CAPEC-66 on capec.mitre.org"],
    ]);
    const selected = rowFor(elements, "CAPEC-66");
    expect([selected.getAttribute("aria-selected"), selected.className]).toEqual(["true", "is-selected"]);
    expect(selected.children[0].children[0].getAttribute("aria-current")).toBe("true");
    expect(rowFor(elements, "CAPEC-7").getAttribute("aria-selected")).toBe("false");
    expect(elements.detailSections.children).toHaveLength(0);

    pending.resolve(answers.get("CAPEC-66"));
    await selection;
    expect(elements.detailStatus.textContent).toBe("");
    expect(sectionSummaries(elements)).toEqual([
      ["Extended Description", "1"],
      ["Related Attack Patterns", "1"],
      ["Execution Flow", "4"],
      ["Prerequisites", "2"],
      ["Skills Required", "1"],
      ["Resources Required", "1"],
      ["Indicators", "1"],
      ["Consequences", "4"],
      ["Mitigations", "3"],
      ["Example Instances", "1"],
      ["Related CWE Weaknesses", "2"],
      ["Taxonomy Mappings", "2"],
      ["References", "1"],
      ["Proposed Relationships", "2"],
      ["Content History", "8"], // one submission and seven modifications
    ]);
    expect(disclosure(elements, "Extended Description").open).toBe(true);
    expect(descendantsByTag(elements.detailSections, "details").filter((section) => section.open)).toHaveLength(1);
    const text = descendantText(elements.detailSections);
    expect(text).toContain("When specially crafted user-controlled input consisting of SQL syntax");
    const steps = descendantsByTag(disclosure(elements, "Execution Flow"), "ol")[0];
    expect(steps.children.map((step) => descendantText(step.children[0]))).toEqual([
      "Step 1 · Explore", "Step 2 · Experiment", "Step 3 · Experiment", "Step 4 · Exploit",
    ]);
    expect(descendantText(steps.children[0])).toBe(
      "Step 1 · Explore [Survey application] The attacker first takes an inventory of the functionality "
        + "exposed by the application. Techniques Spider web sites for all available links "
        + "Sniff network communications with application using a utility such as WireShark.",
    );
    expect(descendantsByTag(steps.children[1], "li")).toHaveLength(4); // its four techniques
    expect(descendantText(steps.children[3])).toContain("Technique Craft and Execute underlying SQL query");
    expect(text).toContain("Use of parameterized queries or stored procedures");
    expect(text).toContain("ChildOf CAPEC-248");
    expect(text).toContain("CWE-89 is exploited by CAPEC-66 · Proposed, not human-reviewed");
    expect(text).toContain("Imported relationships are proposals until a human accepts them");
    expect(text).toContain("Asserted by party:mitre-capec");
    expect(text).toContain("REF-607 OWASP Web Security Testing Guide Section Testing for SQL Injection");
    expect(text).toContain("Publisher The Open Web Application Security Project (OWASP)");
    expect(text).not.toContain("Additional Catalog Fields");
    expect(linksIn(elements.detailSections, "Related CWE Weaknesses")).toEqual([
      ["CWE-89", "https://cwe.mitre.org/data/definitions/89.html"],
      ["CWE-1286", "https://cwe.mitre.org/data/definitions/1286.html"],
    ]);
    expect(linksIn(elements.detailSections, "Related Attack Patterns"))
      .toEqual([["CAPEC-248", "https://capec.mitre.org/data/definitions/248.html"]]);
    expect(linksIn(elements.detailSections, "References")).toEqual([[
      "OWASP Web Security Testing Guide",
      details["CAPEC-66"].references[0].url,
    ]]);
  });

  it("links ATT&CK techniques, shows alternate terms and resolves references with their dates", async () => {
    const { view, elements } = viewHarness(provider());
    view.activate();
    await settle();

    await view.selectAttackPattern("CAPEC-478");
    expect(linksIn(elements.detailSections, "ATT&CK Techniques")).toEqual([
      ["T1574.011", "https://attack.mitre.org/techniques/T1574/011/"],
      ["T1543.003", "https://attack.mitre.org/techniques/T1543/003/"],
    ]);
    expect(descendantText(disclosure(elements, "Taxonomy Mappings")))
      .toContain("Hijack Execution Flow:Service Registry Permissions Weakness");
    expect(sectionSummaries(elements).map(([title]) => title)).not.toContain("References");

    await view.selectAttackPattern("CAPEC-273");
    expect(descendantText(disclosure(elements, "Alternate Terms"))).toContain("Term HTTP Desync Description Modification");
    expect(summaryText(disclosure(elements, "Related Attack Patterns"))).toBe("Related Attack Patterns 8");
    expect(descendantText(disclosure(elements, "Related Attack Patterns"))).toContain("PeerOf CAPEC-33");
    expect(summaryText(disclosure(elements, "Notes"))).toContain("Notes");
    expect(descendantText(disclosure(elements, "References")))
      .toContain("Authors Robert Auger Publisher The Web Application Security Consortium Publication date 2011-02");

    await view.selectAttackPattern("CAPEC-5");
    const blueBoxing = descendantText(disclosure(elements, "References"));
    expect(blueBoxing).toContain("REF-1 Exploiting Software: How to Break Code");
    expect(blueBoxing).toContain("Authors G. Hoglund, G. McGraw Publisher Addison-Wesley Publication date 2004-02");
    // REF-1 has no URL, so its title is text, not a link.
    expect(linksIn(elements.detailSections, "References")).toEqual([]);

    const links = descendantsByTag(elements.detailSections, "a");
    expect(links.length).toBeGreaterThan(0);
    expect(links.every((link) => ["http:", "https:"].includes(new URL(link.href).protocol)
      && link.target === "_blank" && link.rel === "noopener noreferrer")).toBe(true);
  });

  it("renders the deprecated entry's few fields and none it does not have", async () => {
    const { view, elements } = viewHarness(provider());
    view.activate();
    await settle();
    await view.selectAttackPattern("CAPEC-602");
    expect(elements.detailTitle.textContent).toBe("DEPRECATED: Degradation");
    expect(detailRows(elements).map(([label]) => label)).toEqual([
      "Abstraction", "Related CWE weaknesses", "ATT&CK techniques", "Related attack patterns",
      "Attack steps", "Mitigations", "Examples", "tmodel object", "Official definition",
    ]);
    expect(sectionSummaries(elements).map(([title]) => title)).toEqual(["Content History"]);
  });

  it("names a citation the release does not define, and keeps a field a newer schema adds", async () => {
    const data = provider();
    const real = answers.get("CAPEC-63")!;
    data.getAttackPattern = vi.fn(async () => ({
      ...real,
      // CAPEC 3.9's one unresolved citation: CAPEC-244 cites REF-97 (DL-0056).
      references: [{
        id: "REF-97", section: "XSS Filter Evasion Cheat Sheet", resolved: false, title: null, authors: [],
        edition: null, publication: null, publisher: null, year: null, month: null, day: null,
        url: null, url_date: null,
      }],
      entry: { ...real.entry!, fields: { ...real.entry!.fields, Example_Future_Field: ["kept as written"] } },
    }));
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectAttackPattern("CAPEC-63");

    expect(descendantText(disclosure(elements, "References")))
      .toBe("References 1 REF-97 Not defined in this CAPEC release Section XSS Filter Evasion Cheat Sheet");
    expect(descendantText(disclosure(elements, "Additional Catalog Fields")))
      .toContain("Example Future Field (1) kept as written");
  });

  it("keeps table and detail failures apart and offers each its retry", async () => {
    const data = provider();
    data.getAttackPattern = vi.fn()
      .mockRejectedValueOnce(new Error("detail unavailable"))
      .mockResolvedValueOnce(answers.get("CAPEC-66"));
    const { view, elements, documentRoot } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectAttackPattern("CAPEC-66");

    expect(elements.tableBody.children).toHaveLength(13);
    expect(elements.retryButton.hidden).toBe(true);
    expect(elements.detailStatus.textContent).toBe("Unable to load full CAPEC details: detail unavailable");
    expect(elements.detailRetryButton.hidden).toBe(false);
    expect(elements.detailTitle.textContent).toBe("SQL Injection"); // the row's summary stays
    elements.detailRetryButton.focus();
    elements.detailRetryButton.dispatch("click");
    // The retry button hides while it loads, so focus moves to the inspector, not the page.
    expect(documentRoot.activeElement).toBe(elements.inspector);
    await settle();
    expect(elements.detailRetryButton.hidden).toBe(true);
    expect(elements.detailStatus.textContent).toBe("");
    expect(sectionSummaries(elements)).toHaveLength(15);
    expect(data.getAttackPattern).toHaveBeenCalledTimes(2);
  });

  it("says when the engine has no entry for a row", async () => {
    const data = provider();
    data.getAttackPattern = vi.fn(async () => undefined);
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    await view.selectAttackPattern("CAPEC-66");
    expect(elements.detailStatus.textContent).toBe("The full CAPEC entry was not found.");
    expect(elements.detailRetryButton.hidden).toBe(true);
  });

  it("announces loading, empty results, a failure and a successful retry", async () => {
    const pending = deferred<AttackPatternTableResponse>();
    const data = provider();
    data.getTable = vi.fn()
      .mockImplementationOnce(() => pending.promise)
      .mockRejectedValueOnce(new Error("Engine request failed: no CAPEC catalog"))
      .mockResolvedValueOnce(answer({}));
    const { view, elements, documentRoot } = viewHarness(data);

    view.activate();
    expect(elements.workspace.getAttribute("aria-busy")).toBe("true");
    expect(elements.requestStatus.textContent).toBe("Loading CAPEC attack patterns…");
    expect(elements.attribution.hidden).toBe(true);
    pending.resolve(answer({ search: "nothing like this" }));
    await settle();
    expect(elements.workspace.getAttribute("aria-busy")).toBe("false");
    expect(elements.emptyState.hidden).toBe(false);
    expect(elements.emptyState.textContent).toBe("No CAPEC attack patterns match the current search and filters.");
    expect(elements.tableRegion.hidden).toBe(true);
    expect(elements.requestStatus.textContent).toBe("");
    expect(elements.pageStatus.textContent).toBe("0 of 0");

    await view.retry();
    expect(elements.requestStatus.textContent)
      .toBe("Unable to load CAPEC attack patterns: Engine request failed: no CAPEC catalog");
    expect(elements.requestStatus.className).toBe("library-request-status is-error");
    expect(elements.retryButton.hidden).toBe(false);
    expect([elements.tableRegion.hidden, elements.emptyState.hidden, elements.attribution.hidden])
      .toEqual([true, true, true]);
    expect(elements.pageStatus.textContent).toBe("");

    elements.retryButton.focus();
    elements.retryButton.dispatch("click");
    expect(elements.retryButton.hidden).toBe(true);
    expect(documentRoot.activeElement).toBe(elements.search);
    await settle();
    expect(elements.tableBody.children).toHaveLength(13);
    expect(elements.attribution.hidden).toBe(false);
  });

  it("keeps keyboard focus in the view when a failure or an empty answer hides the table", async () => {
    const data = provider();
    data.getTable = vi.fn()
      .mockResolvedValueOnce(answer({}))
      .mockRejectedValueOnce(new Error("Failed to fetch"))
      .mockResolvedValueOnce(answer({}))
      .mockResolvedValueOnce(answer({ search: "nothing like this" }));
    const { view, elements, documentRoot } = viewHarness(data);
    view.activate();
    await settle();

    // The sort buttons are in the table's header, inside the region a failure hides.
    const nameSort = elements.sortButtons.find((button) => button.dataset.sort === "name")!;
    nameSort.focus();
    nameSort.dispatch("click");
    await settle();
    expect(elements.tableRegion.hidden).toBe(true);
    expect(documentRoot.activeElement).toBe(elements.retryButton);

    await view.retry();
    rowFor(elements, "CAPEC-66").children[0].children[0].focus();
    await view.retry();
    expect(elements.emptyState.hidden).toBe(false);
    expect(documentRoot.activeElement).toBe(elements.search);
  });

  it("tells an empty catalog from a search with no matches", async () => {
    const data = provider();
    data.getTable = vi.fn(async () => ({
      ...source,
      catalog: { ...source.catalog, attack_patterns: 0 },
      total: 0,
      count: 0,
      rows: [],
    }));
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    expect(elements.emptyState.textContent).toBe("No CAPEC attack patterns are available.");
  });

  it("pages forward and back, and moves keyboard focus off a page button that becomes disabled", async () => {
    const calls: AttackPatternTableQuery[] = [];
    const { view, elements, documentRoot } = viewHarness(provider((query) => calls.push({ ...query })), 5);
    view.activate();
    await settle();

    expect(elements.pageStatus.textContent).toBe("1–5 of 13");
    expect([elements.previousPage.hidden, elements.previousPage.disabled, elements.nextPage.disabled])
      .toEqual([false, true, false]);
    elements.nextPage.focus();
    elements.nextPage.dispatch("click");
    await settle();
    expect(elements.pageStatus.textContent).toBe("6–10 of 13");
    expect(documentRoot.activeElement).toBe(elements.nextPage);
    elements.nextPage.dispatch("click");
    await settle();
    expect(elements.pageStatus.textContent).toBe("11–13 of 13");
    expect(elements.tableBody.children.map((row) => row.dataset.attackPatternId))
      .toEqual(["CAPEC-497", "CAPEC-602", "CAPEC-701"]);
    expect(elements.nextPage.disabled).toBe(true);
    expect(documentRoot.activeElement).toBe(elements.previousPage);
    expect(calls.map((query) => query.offset)).toEqual([0, 5, 10]);

    // A page past the end (a browser would not send this click, but a shrinking catalog can)
    // answers with no rows, and the view asks again for the last page.
    elements.nextPage.dispatch("click");
    await settle();
    expect(calls.slice(-2).map((query) => query.offset)).toEqual([15, 10]);
    expect(elements.pageStatus.textContent).toBe("11–13 of 13");

    elements.previousPage.dispatch("click");
    elements.previousPage.dispatch("click"); // ignored while the first click loads
    await settle();
    expect(elements.pageStatus.textContent).toBe("6–10 of 13");
    elements.previousPage.focus();
    elements.previousPage.dispatch("click");
    await settle();
    expect(elements.pageStatus.textContent).toBe("1–5 of 13");
    expect(documentRoot.activeElement).toBe(elements.nextPage);
  });

  it("returns to the first page when a filter, sort or clearing changes the query", async () => {
    const calls: AttackPatternTableQuery[] = [];
    const { view, elements } = viewHarness(provider((query) => calls.push({ ...query })), 5);
    view.activate();
    await settle();
    elements.nextPage.dispatch("click");
    await settle();
    elements.likelihoodFilter.value = "High";
    elements.likelihoodFilter.dispatch("change");
    await settle();
    expect(calls[calls.length - 1]).toMatchObject({ likelihood: "High", offset: 0 });
    expect(elements.pageStatus.textContent).toBe("1–5 of 6");
    elements.nextPage.dispatch("click");
    await settle();
    elements.sortButtons.find((button) => button.dataset.sort === "name")!.dispatch("click");
    await settle();
    expect(calls[calls.length - 1]).toMatchObject({ sort: "name", order: "asc", offset: 0 });

    elements.search.value = "e";
    elements.search.dispatch("search");
    await settle();
    expect(elements.clearFilters.hidden).toBe(false);
    elements.clearFilters.dispatch("click");
    await settle();
    expect(calls[calls.length - 1]).toEqual({
      search: undefined, abstraction: undefined, status: undefined, likelihood: undefined,
      severity: undefined, sort: "name", order: "asc", limit: 5, offset: 0,
    });
    expect(elements.clearFilters.hidden).toBe(true);
    expect(elements.likelihoodFilter.value).toBe("");
  });

  it("clears the selection on a page change and leaves focus where the user moved it", async () => {
    const data = provider();
    const pending = deferred<AttackPatternTableResponse>();
    vi.mocked(data.getTable).mockResolvedValueOnce(answer({ limit: 10 })).mockReturnValueOnce(pending.promise);
    const { view, elements, documentRoot } = viewHarness(data, 10);
    view.activate();
    await settle();

    rowFor(elements, "CAPEC-5").children[0].children[0].dispatch("click", 0);
    elements.nextPage.focus();
    elements.nextPage.dispatch("click", 0);
    elements.search.focus();
    pending.resolve(answer({ limit: 10, offset: 10 }));
    await settle();

    expect(elements.pageStatus.textContent).toBe("11–13 of 13");
    expect(elements.nextPage.disabled).toBe(true);
    expect(view.currentSelection()).toBeUndefined();
    expect(elements.backToRow.hidden).toBe(true);
    expect(documentRoot.activeElement).toBe(elements.search);
  });

  it("clears the inspector when the selected row leaves the page, and keeps it when it stays", async () => {
    const { view, elements } = viewHarness(provider());
    view.activate();
    await settle();
    await view.selectAttackPattern("CAPEC-66");

    elements.statusFilter.value = "Draft";
    elements.statusFilter.dispatch("change");
    await settle();
    expect(view.currentSelection()).toBe("CAPEC-66");
    expect(rowFor(elements, "CAPEC-66").getAttribute("aria-selected")).toBe("true");

    elements.statusFilter.value = "Stable";
    elements.statusFilter.dispatch("change");
    await settle();
    expect(view.currentSelection()).toBeUndefined();
    expect(elements.detailStatus.textContent).toBe("Select a row to view its details.");
    expect(elements.detailTitle.textContent).toBe("");
    expect(elements.detailSections.children).toHaveLength(0);
  });

  it("does not let stale table or detail answers replace newer ones", async () => {
    const firstTable = deferred<AttackPatternTableResponse>();
    const secondTable = deferred<AttackPatternTableResponse>();
    const firstDetail = deferred<AttackPatternDetailResponse | undefined>();
    const secondDetail = deferred<AttackPatternDetailResponse | undefined>();
    const data = provider();
    data.getTable = vi.fn()
      .mockResolvedValueOnce(answer({}))
      .mockImplementationOnce(() => firstTable.promise)
      .mockImplementationOnce(() => secondTable.promise);
    data.getAttackPattern = vi.fn()
      .mockImplementationOnce(() => firstDetail.promise)
      .mockImplementationOnce(() => secondDetail.promise);
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();

    elements.abstractionFilter.value = "Meta";
    elements.abstractionFilter.dispatch("change");
    elements.abstractionFilter.value = "Detailed";
    elements.abstractionFilter.dispatch("change");
    secondTable.resolve(answer({ abstraction: "Detailed" }));
    await settle();
    firstTable.resolve(answer({ abstraction: "Meta" }));
    await settle();
    expect(elements.tableBody.children.map((row) => row.dataset.attackPatternId))
      .toEqual(["CAPEC-5", "CAPEC-7", "CAPEC-273", "CAPEC-478"]);

    const selectFirst = view.selectAttackPattern("CAPEC-5");
    const selectSecond = view.selectAttackPattern("CAPEC-7");
    secondDetail.resolve(answers.get("CAPEC-7"));
    await selectSecond;
    firstDetail.resolve(answers.get("CAPEC-5"));
    await selectFirst;
    expect(elements.detailTitle.textContent).toBe("Blind SQL Injection");
    expect(elements.detailId.textContent).toBe("CAPEC-7");
  });

  it("loads once on first activation and recovers once when the engine comes up", async () => {
    const data = provider();
    data.getTable = vi.fn()
      .mockRejectedValueOnce(new Error("Failed to fetch"))
      .mockResolvedValue(answer({}));
    const { view, elements } = viewHarness(data);
    await view.engineStateChanged({ kind: "unreachable", error: "connection refused" });
    view.activate();
    view.activate();
    await settle();
    expect(data.getTable).toHaveBeenCalledTimes(1);
    expect(elements.retryButton.hidden).toBe(false);

    const connected = { kind: "connected", health: { status: "ok", engine: "tmodel-engine", version: "0.1.0" } } as const;
    await view.engineStateChanged(connected);
    await settle();
    expect(data.getTable).toHaveBeenCalledTimes(2);
    expect(elements.tableBody.children).toHaveLength(13);
    await view.engineStateChanged(connected);
    expect(data.getTable).toHaveBeenCalledTimes(2);
  });

  it("warns when the release has fields this importer does not know", async () => {
    const data = provider();
    data.getTable = vi.fn(async () => ({ ...answer({}), catalog: { ...source.catalog, unknown_fields: 2 } }));
    const { view, elements } = viewHarness(data);
    view.activate();
    await settle();
    expect(elements.warning.hidden).toBe(false);
    expect(elements.warning.textContent)
      .toBe("2 catalog fields are not recognized by this importer. The raw fields remain preserved in entry details.");
  });

  it("names the engine's release in the source notice", async () => {
    const data = provider(undefined, { source: "engine", notice: "CAPEC attack patterns from the local engine" });
    const { view, elements } = viewHarness(data);
    expect(elements.sourceNotice.textContent).toBe("CAPEC attack patterns from the local engine");
    view.activate();
    await settle();
    expect(elements.sourceNotice.textContent)
      .toBe("CAPEC attack patterns from the local engine · CAPEC 3.9 (2023-01-24), 13 attack patterns");
  });

  it("works end to end over the fixture provider, details included", async () => {
    const fixtureProvider = new FixtureAttackPatternDataProvider();
    const { view, elements } = viewHarness(fixtureProvider);
    expect(elements.sourceNotice.textContent)
      .toBe("CAPEC 3.9 development fixture · 13 sample attack patterns, not the complete catalog");
    view.activate();
    await settle();
    await vi.waitFor(() => expect(elements.tableBody.children).toHaveLength(13));
    await view.selectAttackPattern("CAPEC-88");
    expect(elements.detailTitle.textContent).toBe("OS Command Injection");
    expect(summaryText(disclosure(elements, "Execution Flow"))).toBe("Execution Flow 4");
    expect(elements.detailStatus.textContent).toBe("");
  });
});

describe("attack pattern view helpers", () => {
  it("labels the attribution with the notice's years, or without them", () => {
    expect(attributionSummary(table.catalog.notice)).toBe("© 2007-2023 The MITRE Corporation · CAPEC Terms of Use");
    expect(attributionSummary("The MITRE Corporation")).toBe("© The MITRE Corporation · CAPEC Terms of Use");
  });

  it("writes CAPEC's publication year, month and day as a date, and anything else as written", () => {
    expect(publicationDate({ year: "2004", month: "--02", day: null })).toBe("2004-02");
    expect(publicationDate({ year: "2011", month: "--02", day: "---15" })).toBe("2011-02-15");
    expect(publicationDate({ year: "2019", month: null, day: null })).toBe("2019");
    expect(publicationDate({ year: null, month: "--02", day: null })).toBe("--02");
    expect(publicationDate({ year: "2019", month: null, day: "---15" })).toBe("2019 ---15");
    expect(publicationDate({ year: null, month: null, day: null })).toBeNull();
  });
});

function provider(
  onQuery?: (query: AttackPatternTableQuery) => void,
  metadata: AttackPatternDataProvider["metadata"] = { source: "fixture", notice: "test CAPEC data" },
): AttackPatternDataProvider {
  return {
    metadata,
    getTable: vi.fn(async (query: AttackPatternTableQuery) => {
      onQuery?.(query);
      return applyAttackPatternQuery(source, query, alternateTerms);
    }),
    getAttackPattern: vi.fn(async (id: string) => answers.get(id)),
  };
}

function answer(query: Partial<AttackPatternTableQuery>): AttackPatternTableResponse {
  return applyAttackPatternQuery(source, { sort: "id", order: "asc", limit: 50, offset: 0, ...query }, alternateTerms);
}

function viewHarness(data: AttackPatternDataProvider, pageSize?: number) {
  const documentRoot = new FakeDocument();
  const make = (tag = "div") => documentRoot.createElement(tag);
  const sortButtons = SORTS.map((sort) => {
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
    statusFilter: make("select"),
    likelihoodFilter: make("select"),
    severityFilter: make("select"),
    sortButtons,
    clearFilters: make("button"),
    requestStatus: make(),
    warning: make(),
    retryButton: make("button"),
    tableRegion: make(),
    tableBody: make("tbody"),
    emptyState: make(),
    previousPage: make("button"),
    nextPage: make("button"),
    pageStatus: make(),
    sortHelp: make(),
    attribution: make("details"),
    attributionSummary: make("summary"),
    attributionNotice: make(),
    attributionLicense: make(),
    attributionTerms: make("a"),
    inspector: make("aside"),
    backToRow: make("button"),
    detailTitle: make(),
    detailId: make(),
    detailBadges: make(),
    detailDescription: make(),
    detailList: make("dl"),
    detailStatus: make(),
    detailRetryButton: make("button"),
    detailSections: make(),
  };
  for (const hidden of [
    elements.warning, elements.retryButton, elements.backToRow, elements.detailRetryButton, elements.tableRegion,
    elements.emptyState, elements.attribution, elements.previousPage, elements.nextPage,
  ]) hidden.hidden = true;
  // As in index.html: the header row of sort buttons and the body sit inside the table region.
  const headerRow = make("tr");
  headerRow.append(...sortButtons.map((button) => button.parentElement!));
  elements.tableRegion.append(headerRow, elements.tableBody);
  elements.inspector.append(elements.backToRow, elements.detailList, elements.detailRetryButton, elements.detailSections);
  return {
    documentRoot,
    elements,
    view: new AttackPatternsView(
      data,
      elements as unknown as AttackPatternViewElements,
      documentRoot as unknown as Document,
      pageSize,
    ),
  };
}

function rowFor(elements: { tableBody: FakeElement }, id: string): FakeElement {
  const row = elements.tableBody.children.find((child) => child.dataset.attackPatternId === id);
  if (!row) throw new Error(`No row for ${id}`);
  return row;
}

function detailRows(elements: { detailList: FakeElement }): [string, string][] {
  return elements.detailList.children.map((row) => [
    descendantText(row.children[0]),
    descendantText(row.children[1]),
  ]);
}

function sectionSummaries(elements: { detailSections: FakeElement }): [string, string][] {
  return elements.detailSections.children.map((section) => {
    const summary = section.children[0];
    return [summary.children[0]?.textContent ?? "", summary.children[1]?.textContent ?? ""];
  });
}

function linksIn(root: FakeElement, title: string): [string, string][] {
  const section = root.children.find((child) => summaryText(child).startsWith(title));
  if (!section) return [];
  return descendantsByTag(section, "a").map((link) => [link.textContent, link.href]);
}

function optionTexts(select: FakeElement): string[] {
  return select.children.map((option) => option.textContent);
}

/** The text a reader meets, with runs of white space read as one space. */
function descendantText(element: FakeElement): string {
  return [element.textContent, ...element.children.map(descendantText)]
    .filter(Boolean).join(" ").replace(/\s+/gu, " ").trim();
}

function descendantsByTag(element: FakeElement, tagName: string): FakeElement[] {
  return element.children.flatMap((child) => [
    ...(child.tagName === tagName ? [child] : []),
    ...descendantsByTag(child, tagName),
  ]);
}

function descendantsByClass(element: FakeElement, className: string): FakeElement[] {
  return element.children.flatMap((child) => [
    ...(child.className.split(" ").includes(className) ? [child] : []),
    ...descendantsByClass(child, className),
  ]);
}

function disclosure(elements: { detailSections: FakeElement }, title: string): FakeElement {
  const match = descendantsByTag(elements.detailSections, "details")
    .find((details) => summaryText(details).startsWith(title));
  if (!match) throw new Error(`Missing disclosure ${title}`);
  return match;
}

function summaryText(details: FakeElement): string {
  const summary = details.children.find((child) => child.tagName === "summary");
  return summary ? descendantText(summary) : "";
}

async function settle(): Promise<void> {
  for (let index = 0; index < 6; index += 1) await Promise.resolve();
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
  activeElement: FakeElement | null = null;

  createElement(tagName: string): FakeElement {
    return new FakeElement(tagName, this);
  }

  createTextNode(text: string): FakeElement {
    const node = new FakeElement("#text", this);
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
  scrollTop = 0;
  private readonly attributes = new Map<string, string>();
  private readonly listeners = new Map<string, Array<(event: Event) => void>>();

  constructor(readonly tagName: string, private readonly ownerDocument: FakeDocument) {}

  focus(): void {
    this.ownerDocument.activeElement = this;
  }

  addEventListener(type: string, listener: EventListenerOrEventListenerObject): void {
    const callbacks = this.listeners.get(type) ?? [];
    callbacks.push((event) => typeof listener === "function"
      ? listener(event)
      : listener.handleEvent(event));
    this.listeners.set(type, callbacks);
  }

  dispatch(type: string, clickCount = 1): void {
    const event = type === "click" ? Object.assign(new Event(type), { detail: clickCount }) : new Event(type);
    for (const callback of this.listeners.get(type) ?? []) callback(event);
  }

  append(...nodes: FakeElement[]): void {
    for (const node of nodes) {
      node.parentElement = this;
      this.children.push(node);
    }
  }

  replaceChildren(...nodes: FakeElement[]): void {
    for (const child of this.children) {
      if (child.contains(this.ownerDocument.activeElement)) this.ownerDocument.activeElement = null;
      child.parentElement = undefined;
    }
    this.children.length = 0;
    this.append(...nodes);
  }

  setAttribute(name: string, value: string): void {
    this.attributes.set(name, value);
  }

  getAttribute(name: string): string | null {
    return this.attributes.get(name) ?? null;
  }

  removeAttribute(name: string): void {
    this.attributes.delete(name);
  }

  contains(node: FakeElement | null): boolean {
    for (let current: FakeElement | undefined = node ?? undefined; current; current = current.parentElement) {
      if (current === this) return true;
    }
    return false;
  }

  querySelectorAll<T extends Element>(selector: string): T[] {
    return this.descendants(selector) as unknown as T[];
  }

  querySelector<T extends Element>(selector: string): T | null {
    return (this.descendants(selector)[0] ?? null) as unknown as T | null;
  }

  closest(selector: string): FakeElement | null {
    let current: FakeElement | undefined = this;
    while (current) {
      if (current.tagName === selector) return current;
      current = current.parentElement;
    }
    return null;
  }

  private descendants(tagName: string): FakeElement[] {
    const matches: FakeElement[] = [];
    const visit = (node: FakeElement) => {
      if (node.tagName === tagName) matches.push(node);
      for (const child of node.children) visit(child);
    };
    for (const child of this.children) visit(child);
    return matches;
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
