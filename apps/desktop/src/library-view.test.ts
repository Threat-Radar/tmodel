import { afterEach, describe, expect, it, vi } from "vitest";
import type { EngineState } from "./engine";
import type {
  LibraryDataProvider,
  LibraryRecordDetails,
  LibraryTableQuery,
  LibraryTableResponse,
} from "./library-types";
import {
  LibraryDocumentsView,
  reviewedArtifactsLabel,
  type LibraryViewElements,
} from "./library-view";

afterEach(() => vi.useRealTimers());

describe("library documents view", () => {
  it("renders rows, the result count, null fields, and untrusted text as text", async () => {
    const baseResponse = tableResponse(["one"]);
    const response: LibraryTableResponse = {
      ...baseResponse,
      rows: [{
        ...baseResponse.rows[0],
        title: "<img src=x onerror=alert(1)>",
        topic: null,
        date: null,
        artifacts: 7,
        reviewed_artifacts: 3,
      }],
    };
    const { view, elements } = viewHarness(providerFor(response));

    view.activate();
    await settle();

    expect(elements.resultCount.textContent).toBe("1 document");
    expect(elements.tableBody.children).toHaveLength(1);
    const row = elements.tableBody.children[0] as FakeElement;
    const titleButton = (row.children[0] as FakeElement).children[0] as FakeElement;
    expect(titleButton.textContent).toBe("<img src=x onerror=alert(1)>");
    expect((row.children[3] as FakeElement).textContent).toBe("—");
    expect((row.children[4] as FakeElement).textContent).toBe("—");
    expect((row.children[5] as FakeElement).textContent).toBe("3 / 7 reviewed");
  });

  it("passes search, filters, and sorting to the provider without reordering its response", async () => {
    vi.useFakeTimers();
    const calls: LibraryTableQuery[] = [];
    const response = tableResponse(["server-second", "server-first"]);
    const provider = providerFor(response, (query) => calls.push({ ...query }));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    elements.search.value = "  canonicalization  ";
    elements.search.dispatch("input");
    await vi.advanceTimersByTimeAsync(250);
    elements.typeFilter.value = "paper";
    elements.typeFilter.dispatch("change");
    elements.statusFilter.value = "stub";
    elements.statusFilter.dispatch("change");
    elements.topicFilter.value = "evidence";
    elements.topicFilter.dispatch("change");
    elements.sortButtons.find((button) => button.dataset.sort === "date")?.dispatch("click");
    elements.sortButtons.find((button) => button.dataset.sort === "date")?.dispatch("click");
    await settle();

    expect(calls[calls.length - 1]).toEqual({
      search: "canonicalization",
      type: "paper",
      status: "stub",
      topic: "evidence",
      sort: "date",
      order: "desc",
    });
    expect(rowIds(elements.tableBody)).toEqual(["server-second", "server-first"]);
  });

  it("announces loading while the initial table request is pending", async () => {
    const pending = deferred<LibraryTableResponse>();
    const provider = providerFor(tableResponse([]));
    provider.getTable = vi.fn(() => pending.promise);
    const { view, elements } = viewHarness(provider);

    view.activate();
    expect(elements.workspace.getAttribute("aria-busy")).toBe("true");
    expect(elements.requestStatus.textContent).toBe("Loading library documents…");

    pending.resolve(tableResponse(["loaded"]));
    await settle();
    expect(elements.workspace.getAttribute("aria-busy")).toBe("false");
    expect(rowIds(elements.tableBody)).toEqual(["loaded"]);
  });

  it("shows sort indicators only for visible server-reported sort columns", async () => {
    const fixtureResponse = tableResponse(["fixture"]);
    fixtureResponse.query.sort = "id";
    const fixture = viewHarness(providerFor(fixtureResponse, () => undefined, false));
    fixture.view.activate();
    await settle();

    expect(fixture.elements.sortButtons.every((button) => button.dataset.order === "")).toBe(true);
    expect(fixture.elements.sortButtons.every(
      (button) => button.parentElement?.getAttribute("aria-sort") === "none",
    )).toBe(true);

    const liveResponse = tableResponse(["live"]);
    liveResponse.query.sort = "date";
    liveResponse.query.order = "desc";
    const live = viewHarness(providerFor(liveResponse));
    live.view.activate();
    await settle();

    const date = live.elements.sortButtons.find((button) => button.dataset.sort === "date");
    expect(date?.dataset.order).toBe("desc");
    expect(date?.parentElement?.getAttribute("aria-sort")).toBe("descending");
  });

  it("loads details, omits missing optional values, and prevents stale details from winning", async () => {
    const first = deferred<LibraryRecordDetails | undefined>();
    const second = deferred<LibraryRecordDetails | undefined>();
    const response = tableResponse(["first", "second"]);
    const provider = providerFor(response);
    provider.getRecord = vi.fn((id) => id === "first" ? first.promise : second.promise);
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    const firstSelection = view.selectRecord("first");
    const secondSelection = view.selectRecord("second");
    second.resolve(details("second", null));
    await secondSelection;
    first.resolve(details("first", "Old publisher"));
    await firstSelection;

    expect(view.currentSelection()).toBe("second");
    expect(elements.detailTitle.textContent).toBe("Document second");
    expect(elements.detailType.textContent).toBe("paper");
    expect(elements.detailRecordStatus.textContent).toBe("stub");
    expect(elements.detailId.textContent).toBe("second");
    expect(elements.detailStatus.textContent).toBe("");
    expect(detailLabels(elements.detailList)).toEqual([]);
    expect(elements.detailEvidence.hidden).toBe(true);
    expect(elements.detailAssessment.hidden).toBe(true);
  });

  it("renders populated optional metadata, wrapped tags, and a safe source link", async () => {
    const provider = providerFor(tableResponse(["complete"]));
    provider.getRecord = vi.fn(async () => ({
      ...details("complete", "Research Publisher"),
      topic: "software supply chain",
      date: "2026-10-31",
      authors: ["Ada Researcher", "A very long organization name that must wrap safely"],
      version: "v2.4",
      maturity: "best-practice",
      tags: ["evidence", "a-very-long-tag-that-must-wrap-within-the-panel"],
      content: { url: "https://example.test/a/very/long/source/document?query=threat-radar" },
    }));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    await view.selectRecord("complete");

    expect(detailLabels(elements.detailList)).toEqual([
      "Topic", "Date", "Publisher", "Authors", "Version", "Maturity", "Tags", "Source URL",
    ]);
    expect(detailValue(elements.detailList, "Authors")?.textContent)
      .toBe("Ada Researcher, A very long organization name that must wrap safely");
    const tags = detailValue(elements.detailList, "Tags")?.children[0];
    expect(tags?.children.map((tag) => tag.textContent)).toEqual([
      "evidence", "a-very-long-tag-that-must-wrap-within-the-panel",
    ]);
    const link = detailValue(elements.detailList, "Source URL")?.children[0];
    expect(link?.textContent).toContain("https://example.test/a/very/long/source/document");
    expect(link?.getAttribute("href"))
      .toBe("https://example.test/a/very/long/source/document?query=threat-radar");
    expect(link?.getAttribute("target")).toBe("_blank");
    expect(link?.getAttribute("rel")).toBe("noopener noreferrer");
  });

  it.each([
    "file:///private/sensitive-document",
    "mailto:reviewer@example.test",
    "javascript:alert('unsafe')",
  ])("omits a source link for unsupported URL %s", async (sourceUrl) => {
    const provider = providerFor(tableResponse(["unsafe-source"]));
    provider.getRecord = vi.fn(async () => ({
      ...details("unsafe-source", null),
      content: { url: sourceUrl },
    }));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    await view.selectRecord("unsafe-source");

    expect(detailLabels(elements.detailList)).not.toContain("Source URL");
  });

  it("shows exact reviewed and unreviewed artifact counts only when evidence exists", async () => {
    const provider = providerFor(tableResponse(["evidence"]));
    provider.getRecord = vi.fn(async () => ({
      ...details("evidence", null),
      artifacts: [artifact(true, "Human reviewer"), artifact(false), artifact(false)],
    }));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    await view.selectRecord("evidence");

    expect(elements.detailEvidence.hidden).toBe(false);
    expect(elements.detailEvidenceSummary.textContent)
      .toBe("3 extracted artifacts · 1 reviewed");
  });

  it("shows meaningful usefulness and applicability metadata when available", async () => {
    const provider = providerFor(tableResponse(["assessed"]));
    provider.getRecord = vi.fn(async () => ({
      ...details("assessed", null),
      usefulness: {
        verdict: "useful",
        reason: "Directly supports evidence-backed threat modeling.",
        assessed: "2026-10-02",
      },
      applicability: { security: "core", this_project: "adjacent" },
    }));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    await view.selectRecord("assessed");

    expect(elements.detailAssessment.hidden).toBe(false);
    expect(detailLabels(elements.detailAssessmentList))
      .toEqual(["Usefulness", "Reason", "Assessed", "Applicability"]);
    expect(detailValue(elements.detailAssessmentList, "Usefulness")?.textContent).toBe("useful");
    const applicability = detailValue(elements.detailAssessmentList, "Applicability")?.children[0];
    expect(applicability?.children.map((item) => item.textContent))
      .toEqual(["Security: core", "This project: adjacent"]);
  });

  it("reports a missing full record", async () => {
    const provider = providerFor(tableResponse(["missing"]));
    provider.getRecord = vi.fn(async () => undefined);
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    await view.selectRecord("missing");

    expect(elements.detailStatus.textContent).toBe("Full record details were not found.");
  });

  it("allows a failed detail request to be retried by selecting the row again", async () => {
    const provider = providerFor(tableResponse(["retry"]));
    provider.getRecord = vi.fn()
      .mockRejectedValueOnce(new Error("detail service unavailable"))
      .mockResolvedValueOnce(details("retry", "Recovered publisher"));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    await view.selectRecord("retry");
    expect(elements.detailStatus.textContent).toContain("detail service unavailable");

    await view.selectRecord("retry");
    expect(elements.detailStatus.textContent).toBe("");
    expect(detailValue(elements.detailList, "Publisher")?.textContent)
      .toBe("Recovered publisher");
    expect(provider.getRecord).toHaveBeenCalledTimes(2);
  });

  it("preserves a selected zero-count facet in the no-results state", async () => {
    const initial = tableResponse(["one"]);
    initial.contextual_facets.type = { paper: 1, rfc: 3 };
    const empty = tableResponse([]);
    empty.library.count = 4;
    empty.contextual_facets.type = { paper: 2 };
    const provider = providerFor(initial);
    provider.getTable = vi.fn(async (query) => structuredClone(query.type ? empty : initial));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    elements.typeFilter.value = "rfc";
    elements.typeFilter.dispatch("change");
    await settle();

    expect(elements.typeFilter.value).toBe("rfc");
    expect(elements.typeFilter.children.map((option) => option.value)).toEqual(["", "paper", "rfc"]);
    expect(elements.typeFilter.children.map((option) => option.textContent))
      .toEqual(["All types", "paper (2)", "rfc (0)"]);
    expect(view.currentQuery().type).toBe("rfc");
    expect(elements.emptyState.hidden).toBe(false);
    expect(elements.tableRegion.hidden).toBe(true);
  });

  it("shows search-contextual facet counts and restores full counts when search is cleared", async () => {
    vi.useFakeTimers();
    const full = tableResponse(["paper-one", "paper-two", "rfc"]);
    full.contextual_facets = {
      type: { paper: 2, rfc: 1 },
      status: { distilled: 1, stub: 2 },
      topic: { canonical: 1, composition: 2 },
    };
    const searched = tableResponse(["paper-one"]);
    searched.library.count = 3;
    searched.contextual_facets = {
      type: { paper: 1 },
      status: { stub: 1 },
      topic: { composition: 1 },
    };
    const provider = providerFor(full);
    provider.getTable = vi.fn(async (query) => structuredClone(query.search ? searched : full));
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    elements.search.value = "sbom";
    elements.search.dispatch("input");
    await vi.advanceTimersByTimeAsync(250);
    expect(elements.typeFilter.children.map((option) => option.textContent))
      .toEqual(["All types", "paper (1)"]);
    expect(elements.statusFilter.children.map((option) => option.textContent))
      .toEqual(["All statuses", "stub (1)"]);

    elements.search.value = "";
    elements.search.dispatch("input");
    await vi.advanceTimersByTimeAsync(250);
    expect(elements.typeFilter.children.map((option) => option.textContent))
      .toEqual(["All types", "paper (2)", "rfc (1)"]);
    expect(elements.statusFilter.children.map((option) => option.textContent))
      .toEqual(["All statuses", "distilled (1)", "stub (2)"]);
    expect(provider.getTable).toHaveBeenCalledTimes(3);
  });

  it("renders warning, empty, error, and retry states", async () => {
    const baseWarning = tableResponse(["one"]);
    const warning: LibraryTableResponse = {
      ...baseWarning,
      library: {
        ...baseWarning.library,
        problems: ["records/broken/record.yaml: invalid"],
      },
    };
    const provider = providerFor(warning);
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();
    expect(elements.warning.hidden).toBe(false);
    expect(elements.warning.textContent).toContain("1 library record");

    provider.getTable = vi.fn()
      .mockResolvedValueOnce(tableResponse([]))
      .mockRejectedValueOnce(new Error("no library configured"))
      .mockResolvedValueOnce(tableResponse(["recovered"]));
    await view.retry();
    expect(elements.emptyState.hidden).toBe(false);
    expect(elements.tableRegion.hidden).toBe(true);
    await view.retry();
    expect(elements.retryButton.hidden).toBe(false);
    expect(elements.requestStatus.textContent).toContain("no library configured");
    elements.retryButton.dispatch("click");
    await settle();
    expect(elements.retryButton.hidden).toBe(true);
    expect(rowIds(elements.tableBody)).toEqual(["recovered"]);
  });

  it("reloads once when the engine becomes healthy after the initial request fails", async () => {
    const provider = providerFor(tableResponse([]));
    provider.getTable = vi.fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce(tableResponse(["recovered"]));
    const { view, elements } = viewHarness(provider);

    view.activate();
    await settle();
    expect(provider.getTable).toHaveBeenCalledTimes(1);
    expect(elements.requestStatus.textContent).toContain("Failed to fetch");

    await view.engineStateChanged(unreachableEngine());
    await view.engineStateChanged(connectedEngine());
    expect(provider.getTable).toHaveBeenCalledTimes(2);
    expect(rowIds(elements.tableBody)).toEqual(["recovered"]);

    await view.engineStateChanged(connectedEngine());
    await view.engineStateChanged(connectedEngine());
    expect(provider.getTable).toHaveBeenCalledTimes(2);
  });

  it("waits for an in-flight startup request before recovering without overlap", async () => {
    const initial = deferred<LibraryTableResponse>();
    const provider = providerFor(tableResponse([]));
    provider.getTable = vi.fn()
      .mockImplementationOnce(() => initial.promise)
      .mockResolvedValueOnce(tableResponse(["recovered"]));
    const { view, elements } = viewHarness(provider);
    await view.engineStateChanged(unreachableEngine());

    view.activate();
    expect(provider.getTable).toHaveBeenCalledTimes(1);
    await view.engineStateChanged(connectedEngine());
    expect(provider.getTable).toHaveBeenCalledTimes(1);

    initial.reject(new TypeError("Failed to fetch"));
    await settle();
    expect(provider.getTable).toHaveBeenCalledTimes(2);
    expect(rowIds(elements.tableBody)).toEqual(["recovered"]);
  });

  it("does not automatically repeat a genuine failure while healthy and keeps manual retry", async () => {
    const provider = providerFor(tableResponse([]));
    provider.getTable = vi.fn()
      .mockRejectedValueOnce(new Error("Engine request failed: no library configured"))
      .mockResolvedValueOnce(tableResponse(["manual-retry"]));
    const { view, elements } = viewHarness(provider);
    await view.engineStateChanged(connectedEngine());

    view.activate();
    await settle();
    await view.engineStateChanged(connectedEngine());
    await view.engineStateChanged(connectedEngine());
    expect(provider.getTable).toHaveBeenCalledTimes(1);
    expect(elements.retryButton.hidden).toBe(false);

    await view.retry();
    expect(provider.getTable).toHaveBeenCalledTimes(2);
    expect(rowIds(elements.tableBody)).toEqual(["manual-retry"]);
  });

  it("does not let a stale table request overwrite a newer filter result", async () => {
    const initial = tableResponse(["initial"]);
    const oldRequest = deferred<LibraryTableResponse>();
    const newRequest = deferred<LibraryTableResponse>();
    const provider = providerFor(initial);
    provider.getTable = vi.fn()
      .mockResolvedValueOnce(initial)
      .mockImplementationOnce(() => oldRequest.promise)
      .mockImplementationOnce(() => newRequest.promise);
    const { view, elements } = viewHarness(provider);
    view.activate();
    await settle();

    elements.typeFilter.value = "paper";
    elements.typeFilter.dispatch("change");
    elements.typeFilter.value = "rfc";
    elements.typeFilter.dispatch("change");
    newRequest.resolve(tableResponse(["new"]));
    await settle();
    oldRequest.resolve(tableResponse(["old"]));
    await settle();

    expect(rowIds(elements.tableBody)).toEqual(["new"]);
  });
});

describe("reviewed artifact presentation", () => {
  it("uses the agreed human-readable labels", () => {
    expect(reviewedArtifactsLabel({ artifacts: 0, reviewed_artifacts: 0 }))
      .toBe("No extracted artifacts");
    expect(reviewedArtifactsLabel({ artifacts: 7, reviewed_artifacts: 3 }))
      .toBe("3 / 7 reviewed");
  });
});

function providerFor(
  response: LibraryTableResponse,
  onQuery: (query: LibraryTableQuery) => void = () => undefined,
  supportsQueries = true,
): LibraryDataProvider {
  return {
    metadata: {
      source: supportsQueries ? "engine" : "fixture",
      notice: "test data",
      supportsQueries,
    },
    getTable: vi.fn(async (query) => {
      onQuery(query);
      return structuredClone(response);
    }),
    getRecord: vi.fn(async (id) => details(id, "Publisher")),
  };
}

function details(id: string, publisher: string | null): LibraryRecordDetails {
  return {
    id,
    title: `Document ${id}`,
    body: "academic",
    type: "paper",
    status: "stub",
    topic: null,
    date: null,
    publisher,
    authors: [],
    version: null,
    maturity: null,
    tags: [],
    content: { url: null },
    profile: null,
    artifacts: [],
    usefulness: null,
    applicability: {},
  };
}

function artifact(reviewed: boolean, reviewedBy = "") {
  return {
    kind: "requirements",
    path: "distilled/requirements.yaml",
    coverage: "full",
    reviewed_by: reviewedBy,
    generated_from: null,
    reviewed,
  };
}

function viewHarness(provider: LibraryDataProvider) {
  const documentRoot = new FakeDocument();
  const make = (tag = "div") => documentRoot.createElement(tag);
  const sortButtons = (["title", "type", "status", "topic", "date"] as const).map((sort) => {
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
    typeFilter: make("select"),
    statusFilter: make("select"),
    topicFilter: make("select"),
    sortButtons,
    resultCount: make(),
    requestStatus: make(),
    warning: make(),
    retryButton: make("button"),
    tableRegion: make(),
    tableBody: make("tbody"),
    emptyState: make(),
    detailTitle: make(),
    detailType: make(),
    detailRecordStatus: make(),
    detailId: make(),
    detailStatus: make(),
    detailList: make("dl"),
    detailEvidence: make("section"),
    detailEvidenceSummary: make(),
    detailAssessment: make("section"),
    detailAssessmentList: make("dl"),
  };
  elements.warning.hidden = true;
  elements.retryButton.hidden = true;
  elements.emptyState.hidden = true;
  elements.tableRegion.hidden = true;
  return {
    elements,
    view: new LibraryDocumentsView(
      provider,
      elements as unknown as LibraryViewElements,
      documentRoot as unknown as Document,
    ),
  };
}

function tableResponse(ids: readonly string[]): LibraryTableResponse {
  return {
    library: { digest: "digest", count: ids.length, problems: [] },
    query: {
      filters: {},
      search: null,
      sort: "title",
      order: "asc",
      limit: null,
      offset: 0,
    },
    total: ids.length,
    count: ids.length,
    rows: ids.map((id) => ({
      id,
      title: `Title ${id}`,
      short_title: null,
      type: "paper",
      shelf: "academic",
      status: "stub",
      maturity: null,
      date: null,
      publisher: null,
      topic: null,
      tags: [],
      url: null,
      artifacts: 0,
      reviewed_artifacts: 0,
      profile: null,
    })),
    facets: { type: { paper: ids.length }, status: { stub: ids.length }, topic: {} },
    contextual_facets: {
      type: { paper: ids.length },
      status: { stub: ids.length },
      topic: {},
    },
  };
}

function rowIds(body: FakeElement): string[] {
  return body.children.map((row) => (row as FakeElement).dataset.recordId ?? "");
}

function detailLabels(list: FakeElement): string[] {
  return list.children.map((wrapper) => wrapper.children[0].textContent);
}

function detailValue(list: FakeElement, label: string): FakeElement | undefined {
  return list.children.find((wrapper) => wrapper.children[0].textContent === label)?.children[1];
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

function connectedEngine(): EngineState {
  return {
    kind: "connected",
    health: { status: "ok", engine: "tmodel-engine", version: "0.1.0" },
  };
}

function unreachableEngine(): EngineState {
  return { kind: "unreachable", error: "connection refused" };
}

class FakeDocument {
  createElement(tagName: string): FakeElement {
    return new FakeElement(tagName);
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
  tabIndex = 0;
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

  add(...names: string[]): void {
    for (const name of names) this.values.add(name);
    this.owner.className = [...this.values].join(" ");
  }

  remove(...names: string[]): void {
    for (const name of names) this.values.delete(name);
    this.owner.className = [...this.values].join(" ");
  }
}
