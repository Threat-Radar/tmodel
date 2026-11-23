import { describe, expect, it, vi } from "vitest";
import catalogArtifact from "../public/data/requirements/catalog.json";
import { calculateCoverageFallback } from "./coverage-provider";
import {
  REQUIREMENTS_GRAPH,
  requirementsGraphWithEverySatisfactionState,
} from "./requirements-fixture.test-support";
import {
  parseRequirementStandardsCatalog,
} from "./requirements-catalog-provider";
import { buildRequirementCatalog, type RequirementCatalog } from "./requirements-model";
import { RequirementsView, type RequirementsViewElements } from "./requirements-view";

const STANDARDS_CATALOG = parseRequirementStandardsCatalog(catalogArtifact);
const ASVS_SOURCE = "owasp-asvs-5";
const CRA_SOURCE = "eu-cra-2024-2847";

describe("requirements view", () => {
  it("renders table rows and an accessible evidence inspector for the selection", async () => {
    const { view, elements } = harness();
    view.activate();
    await settle();

    expect(elements.resultCount.textContent).toBe("3 requirements");
    expect(elements.tableBody.children).toHaveLength(3);
    view.selectRequirement("requirement:component");

    expect(view.currentSelection()).toBe("requirement:component");
    expect(elements.detailTitle.textContent).toBe("Component requirement");
    expect(elements.detailText.textContent).toContain("reject unauthenticated commands");
    expect(detailValue(elements.detailList, "Source reference")?.textContent)
      .toBe("library:test#R2");
    expect(detailValue(elements.detailList, "Source locator")?.textContent).toBe("Clause 2");
    expect(deepText(elements.detailRelationships)).toContain("Assertion-backed relationships");
    expect(deepText(elements.detailRelationships)).toContain("assertion:proposal");
    expect(deepText(elements.detailRelationships)).toContain("review:proposal");
    expect(deepText(elements.detailRelationships)).toContain("by party:human");
    expect(occurrences(
      deepText(elements.detailRelationships),
      "Analytical relationship awaiting a decision.",
    )).toBe(1);
    expect(occurrences(deepText(elements.detailRelationships), "Review review:proposal")).toBe(1);
    expect((elements.tableBody.children[0] as FakeElement).getAttribute("aria-selected"))
      .toBe("true");
  });

  it("keeps multiple structured Assertions separate without repeating legacy summaries", async () => {
    const graph = structuredClone(REQUIREMENTS_GRAPH);
    const asserted = graph.edges.find((edge) => edge.assertions?.length);
    if (!asserted?.assertions) throw new Error("fixture lost asserted relationship");
    asserted.assertions = [...asserted.assertions, {
      id: "assertion:second",
      assertion_status: "accepted",
      confidence: "high",
      description: "Second independent basis.",
      evidence: ["Second independent evidence."],
      reviews: [{
        id: "review:second",
        review_status: "accepted",
        reviewer: "party:second-human",
        justification: "The second basis is sufficient.",
      }],
    }];
    asserted.properties = {
      assertion_ids: ["assertion:proposal", "assertion:second"],
      assertion_statuses: ["proposed", "accepted"],
      review_ids: ["review:proposal", "review:second"],
      review_statuses: ["pending", "accepted"],
    };
    const { view, elements } = harness(vi.fn(async () => graph));
    view.activate();
    await settle();
    view.selectRequirement("requirement:component");

    const text = deepText(elements.detailRelationships);
    expect(text).toContain("assertion:proposal");
    expect(text).toContain("assertion:second");
    expect(text).toContain("by party:human");
    expect(text).toContain("by party:second-human");
    expect(occurrences(text, "Analytical relationship awaiting a decision.")).toBe(1);
    expect(occurrences(text, "Second independent basis.")).toBe(1);
    expect(occurrences(text, "Review review:proposal")).toBe(1);
    expect(occurrences(text, "Review review:second")).toBe(1);
  });

  it("filters by product, loads coverage, and leaves the unscoped requirement out", async () => {
    const { view, elements, getCoverage } = harness();
    view.activate();
    await settle();

    elements.productFilter.value = "product:tcu";
    elements.productFilter.dispatch("change");
    await settle();

    expect(view.currentQuery().product).toBe("product:tcu");
    expect(elements.resultCount.textContent).toBe("2 requirements");
    expect(rowIds(elements.tableBody)).not.toContain("requirement:unscoped");
    expect(getCoverage).toHaveBeenCalledWith("product:tcu", expect.any(AbortSignal));
    expect(elements.coverageStatus.textContent).toContain("not verified compliance");
    expect(deepText(elements.coverageContent)).toContain("Proposed links — hypothetical only");
    expect(deepText(elements.coverageContent)).toContain("No recorded satisfaction evidence");
  });

  it("switches to a clearly separate standards-catalog mode without model coverage claims", async () => {
    const { view, elements, getCoverage } = harness();
    view.activate();
    await settle();

    elements.modeSelect.value = "standards";
    elements.modeSelect.dispatch("change");
    await settle();

    expect(view.currentMode()).toBe("standards");
    expect(elements.productControl.hidden).toBe(true);
    expect(elements.sourceControl.hidden).toBe(false);
    expect(elements.normativityControl.hidden).toBe(false);
    expect(elements.coverageSection.hidden).toBe(true);
    expect(elements.tableCaption.textContent).toContain("does not establish applicability");
    expect(elements.requestStatus.textContent).toContain("extracted standards catalog");
    expect(getCoverage).not.toHaveBeenCalled();

    view.selectRequirement("requirement:component");
    expect(elements.detailStatus.textContent).toContain("not automatically applicable");
    expect(deepText(elements.detailBadges)).toContain("Catalog entry only");
  });

  it("keeps a zero-count source visibly selected and restores its results after search", async () => {
    const getStandardsCatalog = vi.fn(async () => STANDARDS_CATALOG);
    const { view, elements } = harness(undefined, getStandardsCatalog);
    view.activate();
    await settle();
    switchMode(elements, "standards");
    await settle();

    elements.sourceFilter.value = ASVS_SOURCE;
    elements.sourceFilter.dispatch("change");
    expect(elements.resultCount.textContent).toBe("34 requirements");

    elements.search.value = "Annex I";
    elements.search.dispatch("search");
    expect(elements.resultCount.textContent).toBe("0 requirements");
    expect(elements.sourceFilter.value).toBe(ASVS_SOURCE);
    expect(elements.sourceFilter.children.find((option) => option.value === ASVS_SOURCE)?.textContent)
      .toContain("(0)");

    elements.search.value = "";
    elements.search.dispatch("search");
    expect(elements.sourceFilter.value).toBe(ASVS_SOURCE);
    expect(elements.resultCount.textContent).toBe("34 requirements");

    elements.sourceFilter.value = "";
    elements.sourceFilter.dispatch("change");
    expect(view.currentQuery().source).toBeUndefined();
    expect(elements.sourceFilter.value).toBe("");
    expect(elements.resultCount.textContent).toBe("109 requirements");
  });

  it("switches sources while the prior selected source has zero matches", async () => {
    const { view, elements } = harness(
      undefined,
      vi.fn(async () => STANDARDS_CATALOG),
    );
    view.activate();
    await settle();
    switchMode(elements, "standards");
    await settle();

    elements.sourceFilter.value = ASVS_SOURCE;
    elements.sourceFilter.dispatch("change");
    elements.search.value = "Annex I";
    elements.search.dispatch("search");
    expect(elements.resultCount.textContent).toBe("0 requirements");

    elements.sourceFilter.value = CRA_SOURCE;
    elements.sourceFilter.dispatch("change");
    expect(view.currentQuery().source).toBe(CRA_SOURCE);
    expect(elements.sourceFilter.value).toBe(CRA_SOURCE);
    expect(elements.resultCount.textContent).toBe("23 requirements");
  });

  it("loads a new model after catalog browsing and returns to a clean cached catalog", async () => {
    const getStandardsCatalog = vi.fn(async () => STANDARDS_CATALOG);
    const { view, elements, getCoverage } = harness(undefined, getStandardsCatalog);
    view.activate();
    await settle();
    switchMode(elements, "standards");
    await settle();

    elements.sourceFilter.value = ASVS_SOURCE;
    elements.sourceFilter.dispatch("change");
    view.selectRequirement(STANDARDS_CATALOG.requirements[0].id);
    expect(view.currentSelection()).toBeDefined();

    const secondGraph = singleRequirementGraph();
    const getSecondGraph = vi.fn(async () => secondGraph);
    view.openModel({
      file: secondGraph.file,
      title: "Second model",
      notice: "Second model requirements",
      getGraph: getSecondGraph,
      getCoverage,
    });
    switchMode(elements, "model");
    await settle();

    expect(getSecondGraph).toHaveBeenCalledTimes(1);
    expect(view.currentSelection()).toBeUndefined();
    expect(elements.resultCount.textContent).toBe("1 requirement");
    expect(elements.sourceControl.hidden).toBe(true);
    expect(elements.productControl.hidden).toBe(false);
    expect(elements.coverageSection.hidden).toBe(false);

    switchMode(elements, "standards");
    expect(getStandardsCatalog).toHaveBeenCalledTimes(1);
    expect(view.currentSelection()).toBeUndefined();
    expect(view.currentQuery().source).toBeUndefined();
    expect(elements.sourceFilter.value).toBe("");
    expect(elements.resultCount.textContent).toBe("109 requirements");
  });

  it("renders distinct labels for all four satisfaction evidence cases", async () => {
    const graph = requirementsGraphWithEverySatisfactionState();
    const { view, elements } = harness(vi.fn(async () => graph));
    view.activate();
    await settle();

    expect(rowStatus(elements.tableBody, "requirement:family")).toContain("Satisfied");
    expect(rowStatus(elements.tableBody, "requirement:progress")).toContain("In progress");
    expect(rowStatus(elements.tableBody, "requirement:component"))
      .toContain("No recorded satisfaction evidence");
    expect(rowStatus(elements.tableBody, "requirement:planned")).toContain("Not satisfied");
  });

  it("shows an error and recovers through the retry control", async () => {
    const getGraph = vi.fn()
      .mockRejectedValueOnce(new Error("engine unavailable"))
      .mockResolvedValueOnce(REQUIREMENTS_GRAPH);
    const { view, elements } = harness(getGraph);
    view.activate();
    await settle();

    expect(elements.requestStatus.textContent).toContain("engine unavailable");
    expect(elements.retryButton.hidden).toBe(false);
    elements.retryButton.dispatch("click");
    await settle();
    expect(elements.retryButton.hidden).toBe(true);
    expect(elements.resultCount.textContent).toBe("3 requirements");
  });
});

function harness(
  getGraph = vi.fn(async () => REQUIREMENTS_GRAPH),
  getStandardsCatalog = vi.fn(async (): Promise<RequirementCatalog> => (
    buildRequirementCatalog(REQUIREMENTS_GRAPH, {
      id: "test-standard",
      name: "Test Standard",
      version: "1.0",
    })
  )),
) {
  const documentRoot = new FakeDocument();
  const make = (tag = "div") => documentRoot.createElement(tag);
  const sortButtons = ["id", "name", "kind", "normativity", "source", "satisfaction"].map((sort) => {
    const header = make("th");
    const button = make("button");
    button.dataset.sort = sort;
    header.append(button);
    return button;
  });
  const elements = {
    workspace: make(), headingEyebrow: make(), sourceNotice: make(), retryButton: make("button"),
    modeSelect: make("select"), search: make("input"), kindFilter: make("select"),
    normativityControl: make("label"), normativityFilter: make("select"),
    sourceControl: make("label"), sourceFilter: make("select"),
    productControl: make("label"), productFilter: make("select"),
    sortButtons, resultCount: make(), requestStatus: make(), emptyState: make(),
    tableRegion: make(), tableCaption: make("caption"), scopeHeading: make("th"),
    satisfactionHeading: make("button"), tableBody: make("tbody"), pageSize: make("select"),
    previousPage: make("button"), nextPage: make("button"), pageStatus: make(),
    sortHelp: make(), coverageSection: make("details"), coverageStatus: make(),
    coverageContent: make(), detailTitle: make(),
    detailId: make(), detailBadges: make(), detailText: make(), detailStatus: make(),
    detailList: make("dl"), detailRelationships: make(),
  };
  elements.modeSelect.value = "model";
  elements.pageSize.value = "25";
  const coverage = calculateCoverageFallback(REQUIREMENTS_GRAPH, "product:tcu");
  const getCoverage = vi.fn(async () => ({
    response: coverage,
    source: "frontend-fallback" as const,
    notice: "Test fallback.",
  }));
  const view = new RequirementsView(
    elements as unknown as RequirementsViewElements,
    {
      notice: "Test extracted standards catalog",
      getCatalog: getStandardsCatalog,
    },
    documentRoot as unknown as Document,
  );
  view.openModel({
    file: REQUIREMENTS_GRAPH.file,
    title: "TCU",
    notice: "Test model",
    getGraph,
    getCoverage,
  });
  return { view, elements, getCoverage, getStandardsCatalog };
}

function switchMode(elements: { modeSelect: FakeElement }, mode: "model" | "standards"): void {
  elements.modeSelect.value = mode;
  elements.modeSelect.dispatch("change");
}

function singleRequirementGraph() {
  const graph = structuredClone(REQUIREMENTS_GRAPH);
  graph.file = "/models/second-model.yaml";
  graph.nodes = graph.nodes.filter((node) => (
    node.domain_type !== "Requirement" || node.id === "requirement:family"
  ));
  const nodeIds = new Set(graph.nodes.map((node) => node.id));
  graph.edges = graph.edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target));
  return graph;
}

function rowIds(body: FakeElement): string[] {
  return body.children.map((row) => row.dataset.requirementId ?? "");
}

function rowStatus(body: FakeElement, id: string): string {
  const row = body.children.find((candidate) => candidate.dataset.requirementId === id);
  if (!row) throw new Error(`missing row ${id}`);
  return deepText(row.children[5]);
}

function detailValue(list: FakeElement, label: string): FakeElement | undefined {
  return list.children.find((wrapper) => wrapper.children[0]?.textContent === label)?.children[1];
}

function deepText(element: FakeElement): string {
  return [element.textContent, ...element.children.map(deepText)].join(" ");
}

function occurrences(value: string, needle: string): number {
  return value.split(needle).length - 1;
}

async function settle(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
}

class FakeDocument {
  createElement(tagName: string): FakeElement { return new FakeElement(tagName); }
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
  type = "";
  open = false;
  private controlValue = "";
  private readonly attributes = new Map<string, string>();
  private readonly listeners = new Map<string, Array<() => void>>();

  constructor(readonly tagName: string) {}

  get value(): string { return this.controlValue; }

  set value(value: string) {
    if (this.tagName === "select" && this.children.length > 0
      && !this.children.some((option) => option.value === value)) {
      this.controlValue = "";
      return;
    }
    this.controlValue = value;
  }

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
    const previous = this.controlValue;
    this.children.length = 0;
    this.append(...nodes);
    if (this.tagName === "select") {
      this.controlValue = this.children.some((option) => option.value === previous)
        ? previous
        : this.children[0]?.value ?? "";
    }
  }

  setAttribute(name: string, value: string): void { this.attributes.set(name, value); }
  getAttribute(name: string): string | null { return this.attributes.get(name) ?? null; }

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
    if (add) this.values.add(name); else this.values.delete(name);
    this.owner.className = [...this.values].join(" ");
    return add;
  }
  add(...names: string[]): void {
    names.forEach((name) => this.values.add(name));
    this.owner.className = [...this.values].join(" ");
  }
}
