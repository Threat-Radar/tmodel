import type { EngineState } from "./engine";
import type { CoverageLoadResult, CoverageRequirement } from "./coverage-provider";
import type { EngineGraphResponse } from "./model-types";
import { LatestRequestGuard } from "./request-guard";
import type { RequirementStandardsSource } from "./requirements-catalog-provider";
import {
  buildRequirementCatalog,
  DEFAULT_REQUIREMENT_QUERY,
  isRequirementSort,
  queryRequirements,
  type RequirementCatalog,
  type RequirementQuery,
  type RequirementRelationship,
  type RequirementRow,
  type RequirementSatisfaction,
} from "./requirements-model";

const SEARCH_DELAY_MS = 250;
export type RequirementViewMode = "model" | "standards";

export interface RequirementModelSource {
  file: string;
  title: string;
  notice: string;
  getGraph(signal?: AbortSignal): Promise<EngineGraphResponse>;
  getCoverage(product: string, signal?: AbortSignal): Promise<CoverageLoadResult>;
}

export interface RequirementsViewElements {
  workspace: HTMLElement;
  headingEyebrow: HTMLElement;
  sourceNotice: HTMLElement;
  retryButton: HTMLButtonElement;
  modeSelect: HTMLSelectElement;
  search: HTMLInputElement;
  kindFilter: HTMLSelectElement;
  normativityControl: HTMLElement;
  normativityFilter: HTMLSelectElement;
  sourceControl: HTMLElement;
  sourceFilter: HTMLSelectElement;
  productControl: HTMLElement;
  productFilter: HTMLSelectElement;
  sortButtons: readonly HTMLButtonElement[];
  resultCount: HTMLElement;
  requestStatus: HTMLElement;
  emptyState: HTMLElement;
  tableRegion: HTMLElement;
  tableCaption: HTMLElement;
  scopeHeading: HTMLElement;
  satisfactionHeading: HTMLElement;
  tableBody: HTMLTableSectionElement;
  pageSize: HTMLSelectElement;
  previousPage: HTMLButtonElement;
  nextPage: HTMLButtonElement;
  pageStatus: HTMLElement;
  sortHelp: HTMLElement;
  coverageSection: HTMLElement;
  coverageStatus: HTMLElement;
  coverageContent: HTMLElement;
  detailTitle: HTMLElement;
  detailId: HTMLElement;
  detailBadges: HTMLElement;
  detailText: HTMLElement;
  detailStatus: HTMLElement;
  detailList: HTMLDListElement;
  detailRelationships: HTMLElement;
}

export class RequirementsView {
  private readonly modelRequests = new LatestRequestGuard();
  private readonly coverageRequests = new LatestRequestGuard();
  private source?: RequirementModelSource;
  private catalog?: RequirementCatalog;
  private modelCatalog?: RequirementCatalog;
  private standardsCatalog?: RequirementCatalog;
  private mode: RequirementViewMode = "model";
  private query: RequirementQuery = { ...DEFAULT_REQUIREMENT_QUERY };
  private active = false;
  private state: "idle" | "loading" | "loaded" | "failed" = "idle";
  private selectedId?: string;
  private engineConnected?: boolean;
  private failedRequestStartedConnected = false;
  private searchTimer?: ReturnType<typeof setTimeout>;

  constructor(
    private readonly elements: RequirementsViewElements,
    private readonly standardsSource?: RequirementStandardsSource,
    private readonly documentRoot: Document = document,
  ) {
    this.bindControls();
    this.updateModeChrome();
    this.updateSortIndicators();
  }

  openModel(source: RequirementModelSource): void {
    this.source = source;
    this.modelCatalog = undefined;
    if (this.mode === "model") {
      this.catalog = undefined;
      this.selectedId = undefined;
      this.query.product = undefined;
      this.query.offset = 0;
      this.elements.sourceNotice.textContent = source.notice;
      this.clearDetails();
      this.clearCoverage("Select a product to see recorded coverage.");
      if (this.active) void this.loadCurrentMode();
    }
  }

  activate(): void {
    this.active = true;
    if (!this.catalog && this.state !== "loading") void this.loadCurrentMode();
  }

  currentMode(): RequirementViewMode { return this.mode; }

  currentQuery(): RequirementQuery {
    return { ...this.query };
  }

  currentSelection(): string | undefined {
    return this.selectedId;
  }

  async retry(): Promise<void> {
    await this.loadCurrentMode();
  }

  async engineStateChanged(state: EngineState): Promise<void> {
    const wasConnected = this.engineConnected;
    this.engineConnected = state.kind === "connected";
    if (!this.engineConnected) {
      if (this.state === "failed") this.failedRequestStartedConnected = false;
      return;
    }
    if (this.mode !== "model" || !this.active || wasConnected === true || this.state !== "failed"
      || this.failedRequestStartedConnected) return;
    await this.loadModel();
  }

  selectRequirement(id: string): void {
    const row = this.catalog?.requirements.find((requirement) => requirement.id === id);
    if (!row) return;
    this.selectedId = id;
    this.updateSelectedRow();
    this.renderDetails(row);
  }

  private async loadCurrentMode(): Promise<void> {
    if (this.mode === "standards") await this.loadStandards();
    else await this.loadModel();
  }

  private bindControls(): void {
    this.elements.modeSelect.addEventListener("change", () => {
      const mode = this.elements.modeSelect.value;
      if (mode !== "model" && mode !== "standards") return;
      this.switchMode(mode);
    });
    this.elements.search.addEventListener("input", () => {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.query.search = cleanValue(this.elements.search.value);
        this.query.offset = 0;
        this.renderTable();
      }, SEARCH_DELAY_MS);
    });
    this.elements.search.addEventListener("search", () => {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.query.search = cleanValue(this.elements.search.value);
      this.query.offset = 0;
      this.renderTable();
    });
    this.elements.kindFilter.addEventListener("change", () => {
      this.query.kind = cleanValue(this.elements.kindFilter.value);
      this.query.offset = 0;
      this.renderTable();
    });
    this.elements.normativityFilter.addEventListener("change", () => {
      this.query.normativity = cleanValue(this.elements.normativityFilter.value);
      this.query.offset = 0;
      this.renderTable();
    });
    this.elements.sourceFilter.addEventListener("change", () => {
      this.query.source = cleanValue(this.elements.sourceFilter.value);
      this.query.offset = 0;
      this.renderTable();
    });
    this.elements.productFilter.addEventListener("change", () => {
      this.query.product = cleanValue(this.elements.productFilter.value);
      this.query.offset = 0;
      this.renderTable();
      if (this.query.product) void this.loadCoverage(this.query.product);
      else this.clearCoverage("Select a product to see recorded coverage.");
    });
    for (const button of this.elements.sortButtons) {
      button.addEventListener("click", () => {
        const sort = button.dataset.sort;
        if (!sort || !isRequirementSort(sort)) return;
        if (this.query.sort === sort) this.query.order = this.query.order === "asc" ? "desc" : "asc";
        else {
          this.query.sort = sort;
          this.query.order = "asc";
        }
        this.query.offset = 0;
        this.updateSortIndicators();
        this.renderTable();
      });
    }
    this.elements.pageSize.addEventListener("change", () => {
      const value = Number(this.elements.pageSize.value);
      if (![10, 25, 50].includes(value)) return;
      this.query.limit = value;
      this.query.offset = 0;
      this.renderTable();
    });
    this.elements.previousPage.addEventListener("click", () => {
      this.query.offset = Math.max(0, this.query.offset - this.query.limit);
      this.renderTable();
    });
    this.elements.nextPage.addEventListener("click", () => {
      this.query.offset += this.query.limit;
      this.renderTable();
    });
    this.elements.retryButton.addEventListener("click", () => void this.retry());
  }

  private switchMode(mode: RequirementViewMode): void {
    if (mode === this.mode) return;
    this.modelRequests.cancel();
    this.coverageRequests.cancel();
    this.mode = mode;
    this.catalog = mode === "model" ? this.modelCatalog : this.standardsCatalog;
    this.selectedId = undefined;
    this.query = {
      ...this.query,
      normativity: undefined,
      product: undefined,
      source: undefined,
      offset: 0,
    };
    this.elements.normativityFilter.value = "";
    this.elements.productFilter.value = "";
    this.elements.sourceFilter.value = "";
    this.elements.modeSelect.value = mode;
    this.updateModeChrome();
    this.clearDetails();
    if (this.catalog) {
      this.populateControls(this.catalog);
      this.renderTable();
      this.state = "loaded";
    } else if (this.active) void this.loadCurrentMode();
  }

  private async loadModel(): Promise<void> {
    const source = this.source;
    if (!source) {
      this.renderError(new Error("Open an example model first."));
      return;
    }
    const requestStartedConnected = this.engineConnected === true;
    const request = this.modelRequests.begin();
    this.coverageRequests.cancel();
    this.state = "loading";
    this.setLoading(true);
    try {
      const graph = await source.getGraph(request.signal);
      if (!this.modelRequests.isCurrent(request) || this.source !== source) return;
      this.modelCatalog = buildRequirementCatalog(graph);
      this.catalog = this.modelCatalog;
      this.populateControls(this.catalog);
      this.renderTable();
      this.state = "loaded";
      this.failedRequestStartedConnected = false;
    } catch (error) {
      if (!this.modelRequests.isCurrent(request) || isAbortError(error)) return;
      this.state = "failed";
      this.failedRequestStartedConnected = requestStartedConnected;
      this.renderError(error);
    } finally {
      if (this.modelRequests.isCurrent(request)) this.setLoading(false);
      this.modelRequests.complete(request);
    }
  }

  private async loadStandards(): Promise<void> {
    const source = this.standardsSource;
    if (!source) {
      this.renderError(new Error("The extracted standards catalog is not configured."));
      return;
    }
    const request = this.modelRequests.begin();
    this.coverageRequests.cancel();
    this.state = "loading";
    this.setLoading(true);
    try {
      const catalog = await source.getCatalog(request.signal);
      if (!this.modelRequests.isCurrent(request) || this.mode !== "standards") return;
      this.standardsCatalog = catalog;
      this.catalog = catalog;
      this.elements.sourceNotice.textContent = source.notice;
      this.populateControls(catalog);
      this.renderTable();
      this.state = "loaded";
      this.failedRequestStartedConnected = false;
    } catch (error) {
      if (!this.modelRequests.isCurrent(request) || isAbortError(error)) return;
      this.state = "failed";
      this.failedRequestStartedConnected = false;
      this.renderError(error);
    } finally {
      if (this.modelRequests.isCurrent(request)) this.setLoading(false);
      this.modelRequests.complete(request);
    }
  }

  private updateModeChrome(): void {
    const standards = this.mode === "standards";
    this.elements.modeSelect.value = this.mode;
    this.elements.headingEyebrow.textContent = standards
      ? "Reference material · not model scope"
      : "Recorded product evidence";
    this.elements.productControl.hidden = standards;
    this.elements.sourceControl.hidden = !standards;
    this.elements.normativityControl.hidden = !standards;
    this.elements.coverageSection.hidden = standards;
    this.elements.tableCaption.textContent = standards
      ? "Requirements in the extracted standards catalog; visibility does not establish applicability or compliance"
      : "Requirements recorded in the selected model";
    this.elements.scopeHeading.textContent = standards ? "Model applicability" : "Applies to product";
    this.elements.satisfactionHeading.textContent = standards
      ? "Model satisfaction"
      : "Recorded satisfaction";
    if (standards) {
      this.elements.sourceNotice.textContent = this.standardsSource?.notice
        ?? "Extracted standards catalog is not configured.";
      this.clearCoverage("Catalog entries are not evaluated against the selected model.");
    } else {
      this.elements.sourceNotice.textContent = this.source?.notice
        ?? "Open an example model to load its requirements.";
      this.clearCoverage("Select a product to see recorded coverage.");
    }
  }

  private renderTable(): void {
    if (!this.catalog) return;
    if (this.query.offset >= this.catalog.requirements.length) this.query.offset = 0;
    const response = queryRequirements(this.catalog, this.query);
    if (response.total > 0 && response.count === 0) {
      this.query.offset = Math.max(0, Math.floor((response.total - 1) / this.query.limit) * this.query.limit);
      return this.renderTable();
    }
    this.populateKinds(response.kinds);
    this.populateNormativities(response.normativities);
    this.populateSources(response.sources);
    this.elements.tableBody.replaceChildren(...response.rows.map((row) => this.createRow(row)));
    this.elements.resultCount.textContent = `${response.total} ${response.total === 1 ? "requirement" : "requirements"}`;
    this.elements.requestStatus.textContent = response.total === 0
      ? "No requirements match the current search and filters."
      : `Showing ${response.query.offset + 1}–${response.query.offset + response.count} of ${response.total} matching requirements in ${this.mode === "standards" ? "the extracted standards catalog" : this.source?.title ?? "this model"}.`;
    this.elements.requestStatus.className = "library-request-status";
    this.elements.emptyState.hidden = response.total !== 0;
    this.elements.tableRegion.hidden = response.total === 0;
    this.elements.retryButton.hidden = true;
    this.renderPagination(response.total, response.count);
    if (this.selectedId && response.rows.some((row) => row.id === this.selectedId)) {
      this.updateSelectedRow();
    } else if (this.selectedId) this.clearDetails();
  }

  private createRow(row: RequirementRow): HTMLTableRowElement {
    const tr = this.documentRoot.createElement("tr");
    tr.dataset.requirementId = row.id;
    tr.setAttribute("aria-selected", String(row.id === this.selectedId));
    const identity = this.documentRoot.createElement("td");
    const button = this.documentRoot.createElement("button");
    button.type = "button";
    button.className = "library-title-button requirement-title-button";
    button.textContent = row.name;
    button.addEventListener("click", () => this.selectRequirement(row.id));
    const id = this.documentRoot.createElement("code");
    id.className = "requirement-row-id";
    id.textContent = row.id;
    identity.append(button, id);
    tr.append(
      identity,
      textCell(this.documentRoot, displayValue(row.kind)),
      textCell(this.documentRoot, displayValue(row.normativity)),
      sourceCell(this.documentRoot, row),
      textCell(this.documentRoot, this.mode === "standards"
        ? "Not assigned to the selected model"
        : scopeLabel(row)),
      this.mode === "standards"
        ? catalogStatusCell(this.documentRoot)
        : statusCell(this.documentRoot, row.satisfaction),
    );
    return tr;
  }

  private renderDetails(row: RequirementRow): void {
    this.elements.detailTitle.textContent = row.name;
    this.elements.detailId.textContent = row.id;
    this.elements.detailText.textContent = row.text ?? "No requirement statement recorded.";
    this.elements.detailStatus.textContent = "";
    this.elements.detailBadges.replaceChildren(...[
      row.kind && displayValue(row.kind),
      row.normativity && displayValue(row.normativity),
      satisfactionLabel(row.satisfaction),
    ].flatMap((value) => value ? [badge(this.documentRoot, value)] : []));
    if (this.mode === "standards") {
      this.elements.detailBadges.replaceChildren(...[
        row.kind && displayValue(row.kind),
        row.normativity && displayValue(row.normativity),
        "Catalog entry only",
      ].flatMap((value) => value ? [badge(this.documentRoot, value)] : []));
      this.elements.detailStatus.textContent = "This extracted entry is reference material. It is not automatically applicable to, or satisfied by, the selected model.";
    }
    const scope = [
      ...row.appliesTo.map((id) => `Object: ${id}`),
      ...row.appliesToFamilies.map((family) => `Family: ${family}`),
    ];
    this.elements.detailList.replaceChildren(...[
      ["Description", row.description],
      ["Text origin", row.textOrigin && displayValue(row.textOrigin)],
      ["Source reference", row.sourceRef],
      ["Source locator", row.sourceLocator],
      ["Catalog source", row.catalogSource
        ? `${row.catalogSource.name} ${row.catalogSource.version ?? ""}`.trim() : null],
      ["Recorded scope", scope.length ? scope.join(" · ") : "Not recorded"],
      ["Applicable products", row.applicableProducts.length
        ? row.applicableProducts.map((product) => product.name).join(", ") : "Not recorded"],
      ["Mitigation evidence", row.mitigations.length
        ? row.mitigations.map((item) => `${item.name} (${item.status ?? "status not recorded"})`).join(" · ")
        : this.mode === "standards" ? "None in the extraction; no model satisfaction is asserted" : "Not recorded"],
    ].map(([label, value]) => detailRow(this.documentRoot, label ?? "", value ?? "Not recorded")));
    const established = row.relationships.filter((relationship) => relationship.established);
    const assertions = row.relationships.filter((relationship) => relationship.assertionIds.length > 0);
    this.elements.detailRelationships.replaceChildren(
      relationshipSection(this.documentRoot, "Established relationships", established),
      relationshipSection(this.documentRoot, "Assertion-backed relationships and Reviews", assertions),
    );
  }

  private async loadCoverage(product: string): Promise<void> {
    const source = this.source;
    if (!source) return;
    const request = this.coverageRequests.begin();
    this.elements.coverageStatus.textContent = "Loading recorded coverage…";
    this.elements.coverageStatus.className = "library-request-status";
    this.elements.coverageContent.replaceChildren();
    try {
      const result = await source.getCoverage(product, request.signal);
      if (!this.coverageRequests.isCurrent(request) || this.query.product !== product) return;
      this.renderCoverage(result);
    } catch (error) {
      if (!this.coverageRequests.isCurrent(request) || isAbortError(error)) return;
      this.elements.coverageStatus.textContent = `Coverage unavailable: ${errorMessage(error)}`;
      this.elements.coverageStatus.className = "library-request-status is-error";
      this.elements.coverageContent.replaceChildren();
    } finally {
      this.coverageRequests.complete(request);
    }
  }

  private renderCoverage(result: CoverageLoadResult): void {
    const coverage = result.response;
    this.elements.coverageStatus.textContent = `${result.notice} ${coverage.interpretation}`;
    this.elements.coverageStatus.className = "library-request-status";
    const counts = this.documentRoot.createElement("div");
    counts.className = "coverage-counts";
    for (const [label, value, kind] of [
      ["Satisfied", coverage.counts.satisfied, "satisfied"],
      ["In progress", coverage.counts.in_progress, "in-progress"],
      ["No recorded / not satisfied", coverage.counts.unsatisfied, "unsatisfied"],
    ] as const) {
      const card = this.documentRoot.createElement("div");
      card.className = `coverage-count coverage-${kind}`;
      const number = this.documentRoot.createElement("strong");
      number.textContent = String(value);
      const text = this.documentRoot.createElement("span");
      text.textContent = label;
      card.append(number, text);
      counts.append(card);
    }
    const requirements = this.documentRoot.createElement("ul");
    requirements.className = "coverage-items";
    requirements.append(...coverage.requirements.map((row) => {
      const item = this.documentRoot.createElement("li");
      const heading = this.documentRoot.createElement("strong");
      heading.textContent = `${row.name} — ${coverageStatusLabel(row)}`;
      const evidence = this.documentRoot.createElement("span");
      evidence.textContent = row.mitigations.length
        ? `Mitigations: ${row.mitigations.map((mitigation) => `${mitigation.id} (${mitigation.status ?? "status not recorded"})`).join(", ")}`
        : "No satisfying mitigation is recorded.";
      item.append(heading, evidence);
      return item;
    }));
    const gaps = simpleList(
      this.documentRoot,
      "Unaddressed threats",
      coverage.unaddressed_threats,
      "No unaddressed ThreatInstances in this recorded result.",
    );
    const proposals = simpleList(
      this.documentRoot,
      "Proposed links — hypothetical only",
      coverage.proposed_assertions.map((proposal) => (
        `${proposal.id} · ${proposal.effect.replace(/_/g, " ")} · if accepted: ${proposal.if_accepted.counts.satisfied} satisfied, ${proposal.if_accepted.unaddressed_threats.length} unaddressed threats`
      )),
      "No proposed Assertion changes this coverage result.",
    );
    const joint = this.documentRoot.createElement("p");
    joint.className = "coverage-joint";
    joint.textContent = `Joint hypothetical if all listed proposals were accepted: ${coverage.if_all_proposed_accepted.counts.satisfied} satisfied, ${coverage.if_all_proposed_accepted.counts.in_progress} in progress, ${coverage.if_all_proposed_accepted.counts.unsatisfied} with no recorded satisfaction or a recorded non-complete status; ${coverage.if_all_proposed_accepted.unaddressed_threats.length} unaddressed threats. This is not an acceptance or compliance result.`;
    this.elements.coverageContent.replaceChildren(counts, requirements, gaps, proposals, joint);
  }

  private clearCoverage(message: string): void {
    this.coverageRequests.cancel();
    this.elements.coverageStatus.textContent = message;
    this.elements.coverageStatus.className = "library-request-status";
    this.elements.coverageContent.replaceChildren();
  }

  private renderError(error: unknown): void {
    this.catalog = undefined;
    this.elements.requestStatus.textContent = `Unable to load ${this.mode === "standards" ? "the extracted standards catalog" : "requirements"}: ${errorMessage(error)}`;
    this.elements.requestStatus.className = "library-request-status is-error";
    this.elements.resultCount.textContent = "Unavailable";
    this.elements.tableRegion.hidden = true;
    this.elements.emptyState.hidden = true;
    this.elements.retryButton.hidden = false;
    this.elements.previousPage.disabled = true;
    this.elements.nextPage.disabled = true;
    this.elements.pageStatus.textContent = "Unavailable";
  }

  private populateControls(catalog: RequirementCatalog): void {
    const allProducts = this.documentRoot.createElement("option");
    allProducts.value = "";
    allProducts.textContent = "All products";
    this.elements.productFilter.replaceChildren(allProducts, ...catalog.products.map((product) => {
      const option = this.documentRoot.createElement("option");
      option.value = product.id;
      option.textContent = product.name;
      return option;
    }));
    this.elements.productFilter.value = this.query.product ?? "";
    this.populateKinds(catalog.kinds);
    this.populateNormativities(catalog.normativities);
    this.populateSources(catalog.sources);
  }

  private populateKinds(kinds: Readonly<Record<string, number>>): void {
    const selected = this.elements.kindFilter.value;
    const entries = Object.entries(kinds).sort(([left], [right]) => left.localeCompare(right));
    if (selected && !entries.some(([value]) => value === selected)) entries.push([selected, 0]);
    const all = this.documentRoot.createElement("option");
    all.value = "";
    all.textContent = "All kinds";
    this.elements.kindFilter.replaceChildren(all, ...entries.map(([value, count]) => {
      const option = this.documentRoot.createElement("option");
      option.value = value;
      option.textContent = `${displayValue(value)} (${count})`;
      return option;
    }));
    this.elements.kindFilter.value = selected;
  }

  private populateNormativities(normativities: Readonly<Record<string, number>>): void {
    populateValueFilter(
      this.documentRoot,
      this.elements.normativityFilter,
      "All normativity",
      normativities,
      displayValue,
    );
  }

  private populateSources(sources: readonly { id: string; name: string; version: string | null; count: number }[]): void {
    const selected = this.elements.sourceFilter.value;
    const entries = [...sources];
    if (selected && !entries.some((source) => source.id === selected)) {
      const source = this.catalog?.sources.find((candidate) => candidate.id === selected);
      entries.push(source
        ? { ...source, count: 0 }
        : { id: selected, name: selected, version: null, count: 0 });
      entries.sort((left, right) => (
        left.name.localeCompare(right.name) || left.id.localeCompare(right.id)
      ));
    }
    const all = this.documentRoot.createElement("option");
    all.value = "";
    all.textContent = "All standards";
    this.elements.sourceFilter.replaceChildren(all, ...entries.map((source) => {
      const option = this.documentRoot.createElement("option");
      option.value = source.id;
      option.textContent = `${source.name} ${source.version ?? ""} (${source.count})`.replace(/\s+/g, " ").trim();
      return option;
    }));
    this.elements.sourceFilter.value = selected;
  }

  private renderPagination(total: number, count: number): void {
    const start = total === 0 ? 0 : this.query.offset + 1;
    const end = Math.min(total, this.query.offset + count);
    this.elements.pageStatus.textContent = count === 0 ? `0 of ${total}` : `${start}–${end} of ${total}`;
    this.elements.previousPage.disabled = this.query.offset === 0;
    this.elements.nextPage.disabled = end >= total;
    this.elements.pageSize.value = String(this.query.limit);
  }

  private updateSelectedRow(): void {
    for (const row of this.elements.tableBody.querySelectorAll<HTMLTableRowElement>("tr")) {
      const selected = row.dataset.requirementId === this.selectedId;
      row.classList.toggle("is-selected", selected);
      row.setAttribute("aria-selected", String(selected));
    }
  }

  private clearDetails(): void {
    this.selectedId = undefined;
    this.elements.detailTitle.textContent = "Select a requirement";
    this.elements.detailId.textContent = "";
    this.elements.detailBadges.replaceChildren();
    this.elements.detailText.textContent = "";
    this.elements.detailList.replaceChildren();
    this.elements.detailRelationships.replaceChildren();
    this.elements.detailStatus.textContent = this.mode === "standards"
      ? "Choose a catalog row to inspect its statement, source locator, relationship proposals, and Review decisions."
      : "Choose a row to inspect its full statement, provenance, scope, relationships, Assertions, and Reviews.";
  }

  private updateSortIndicators(): void {
    for (const button of this.elements.sortButtons) {
      const active = button.dataset.sort === this.query.sort;
      button.closest("th")?.setAttribute("aria-sort", active
        ? this.query.order === "asc" ? "ascending" : "descending"
        : "none");
      button.dataset.order = active ? this.query.order : "";
    }
    this.elements.sortHelp.textContent = `${displayValue(this.query.sort)} sorted ${this.query.order === "asc" ? "ascending" : "descending"}. Select the column again to reverse it.`;
  }

  private setLoading(loading: boolean): void {
    this.elements.workspace.setAttribute("aria-busy", String(loading));
    if (loading) {
      this.elements.requestStatus.textContent = this.mode === "standards"
        ? "Loading the extracted standards catalog…"
        : "Loading requirements from the selected model…";
      this.elements.requestStatus.className = "library-request-status";
      this.elements.retryButton.hidden = true;
    }
  }
}

export function requirementsViewElements(root: Document = document): RequirementsViewElements {
  const required = <T extends HTMLElement>(id: string): T => {
    const element = root.getElementById(id);
    if (!element) throw new Error(`Missing required requirements element #${id}`);
    return element as T;
  };
  return {
    workspace: required("requirements-workspace"),
    headingEyebrow: required("requirements-heading-eyebrow"),
    sourceNotice: required("requirements-source-notice"),
    retryButton: required("requirements-retry"),
    modeSelect: required("requirements-mode"),
    search: required("requirements-search"),
    kindFilter: required("requirements-kind-filter"),
    normativityControl: required("requirements-normativity-control"),
    normativityFilter: required("requirements-normativity-filter"),
    sourceControl: required("requirements-source-control"),
    sourceFilter: required("requirements-source-filter"),
    productControl: required("requirements-product-control"),
    productFilter: required("requirements-product-filter"),
    sortButtons: [...root.querySelectorAll<HTMLButtonElement>("[data-requirement-sort]")],
    resultCount: required("requirements-result-count"),
    requestStatus: required("requirements-request-status"),
    emptyState: required("requirements-empty"),
    tableRegion: required("requirements-table-region"),
    tableCaption: required("requirements-table-caption"),
    scopeHeading: required("requirements-scope-heading"),
    satisfactionHeading: required("requirements-satisfaction-heading"),
    tableBody: required("requirements-table-body"),
    pageSize: required("requirements-page-size"),
    previousPage: required("requirements-page-previous"),
    nextPage: required("requirements-page-next"),
    pageStatus: required("requirements-page-status"),
    sortHelp: required("requirements-sort-help"),
    coverageSection: required("requirements-coverage"),
    coverageStatus: required("requirements-coverage-status"),
    coverageContent: required("requirements-coverage-content"),
    detailTitle: required("requirements-detail-title"),
    detailId: required("requirements-detail-id"),
    detailBadges: required("requirements-detail-badges"),
    detailText: required("requirements-detail-text"),
    detailStatus: required("requirements-detail-status"),
    detailList: required("requirements-detail-list"),
    detailRelationships: required("requirements-detail-relationships"),
  };
}

function relationshipSection(
  root: Document,
  title: string,
  relationships: readonly RequirementRelationship[],
): HTMLElement {
  const details = root.createElement("details");
  details.className = "requirement-relationship-section";
  details.open = title.startsWith("Established");
  const summary = root.createElement("summary");
  summary.textContent = `${title} (${relationships.length})`;
  const list = root.createElement("ul");
  list.className = "requirement-relationship-list";
  if (!relationships.length) {
    const empty = root.createElement("li");
    empty.className = "empty-state";
    empty.textContent = "None recorded.";
    list.append(empty);
  } else {
    list.append(...relationships.map((relationship) => {
      const item = root.createElement("li");
      item.className = `requirement-relationship review-${relationship.reviewState}`;
      const heading = root.createElement("strong");
      heading.textContent = `${relationship.direction === "outgoing" ? "→" : "←"} ${relationship.predicate} · ${relationship.targetName}`;
      const target = root.createElement("code");
      target.textContent = `${relationship.targetType}: ${relationship.targetId}`;
      item.append(heading, target);
      if (relationship.authored && relationship.assertions.length) {
        item.append(paragraph(root, "Direct authored relationship remains established independently of the Assertions below."));
      }
      if (relationship.assertions.length) {
        for (const assertion of relationship.assertions) {
          const status = root.createElement("span");
          status.className = "review-badge";
          status.textContent = `${assertionDecisionLabel(assertion)} · assertion ${assertion.status ?? "status not recorded"}${assertion.confidence ? ` · ${assertion.confidence} confidence` : ""}`;
          item.append(status);
          const id = root.createElement("code");
          id.textContent = assertion.id;
          item.append(id);
          if (assertion.description) item.append(paragraph(root, assertion.description));
          for (const evidence of assertion.evidence) item.append(paragraph(root, `Evidence: ${evidence}`));
          for (const review of assertion.reviews) {
            item.append(paragraph(root, `Review ${review.id} — ${review.status ?? "status not recorded"}${review.reviewer ? ` by ${review.reviewer}` : ""}${review.justification ? `: ${review.justification}` : ""}`));
          }
        }
        return item;
      }
      if (relationship.assertionIds.length) {
        const status = root.createElement("span");
        status.className = "review-badge";
        status.textContent = `${displayValue(relationship.reviewState)} · assertion ${relationship.assertionStatus ?? "status not recorded"}${relationship.confidence ? ` · ${relationship.confidence} confidence` : ""}`;
        item.append(status);
        const ids = root.createElement("code");
        ids.textContent = relationship.assertionIds.join(", ");
        item.append(ids);
      }
      for (const description of relationship.descriptions) item.append(paragraph(root, description));
      for (const evidence of relationship.evidence) item.append(paragraph(root, `Evidence: ${evidence}`));
      for (const review of relationship.reviews) {
        item.append(paragraph(root, `Review ${review.id} — ${review.status ?? "status not recorded"}${review.justification ? `: ${review.justification}` : ""}`));
      }
      return item;
    }));
  }
  details.append(summary, list);
  return details;
}

function simpleList(root: Document, title: string, items: readonly string[], empty: string): HTMLElement {
  const section = root.createElement("section");
  const heading = root.createElement("h4");
  heading.textContent = title;
  const list = root.createElement("ul");
  list.className = "coverage-items";
  const values = items.length ? items : [empty];
  list.append(...values.map((value) => {
    const item = root.createElement("li");
    item.textContent = value;
    return item;
  }));
  section.append(heading, list);
  return section;
}

function detailRow(root: Document, label: string, value: string): HTMLElement {
  const row = root.createElement("div");
  row.className = "detail-row";
  const term = root.createElement("dt");
  term.textContent = label;
  const description = root.createElement("dd");
  description.textContent = value;
  row.append(term, description);
  return row;
}

function paragraph(root: Document, value: string): HTMLParagraphElement {
  const paragraph = root.createElement("p");
  paragraph.textContent = value;
  return paragraph;
}

function textCell(root: Document, value: string): HTMLTableCellElement {
  const cell = root.createElement("td");
  cell.textContent = value;
  return cell;
}

function sourceCell(root: Document, row: RequirementRow): HTMLTableCellElement {
  const cell = root.createElement("td");
  const reference = root.createElement("code");
  reference.textContent = row.sourceRef ?? "Not recorded";
  const locator = root.createElement("span");
  locator.className = "requirement-source-locator";
  locator.textContent = row.sourceLocator ?? "Locator not recorded";
  cell.append(reference, locator);
  return cell;
}

function statusCell(root: Document, status: RequirementSatisfaction): HTMLTableCellElement {
  const cell = root.createElement("td");
  const chip = badge(root, satisfactionLabel(status));
  chip.classList.add(`requirement-status-${status.replace(/_/g, "-")}`);
  cell.append(chip);
  return cell;
}

function catalogStatusCell(root: Document): HTMLTableCellElement {
  const cell = root.createElement("td");
  const chip = badge(root, "Catalog only");
  chip.classList.add("requirement-status-catalog-only");
  cell.append(chip);
  return cell;
}

function badge(root: Document, value: string): HTMLSpanElement {
  const element = root.createElement("span");
  element.className = "status-chip";
  element.textContent = value;
  return element;
}

function satisfactionLabel(status: RequirementSatisfaction): string {
  switch (status) {
    case "satisfied": return "Satisfied";
    case "in_progress": return "In progress";
    case "unsatisfied": return "Not satisfied";
    case "not_recorded": return "No recorded satisfaction evidence";
  }
}

function coverageStatusLabel(row: CoverageRequirement): string {
  if (row.status === "satisfied") return "Satisfied";
  if (row.status === "in_progress") return "In progress";
  return row.mitigations.length === 0
    ? "No recorded satisfaction evidence"
    : "Not satisfied (recorded mitigation is not complete)";
}

function assertionDecisionLabel(assertion: RequirementRelationship["assertions"][number]): string {
  switch (assertion.reviewState) {
    case "accepted": return "Accepted relationship";
    case "rejected": return "Rejected relationship";
    case "changes_requested": return "Relationship changes requested";
    case "proposed": return assertion.reviews.length
      ? "Proposed relationship · review pending"
      : "Proposed relationship · unreviewed";
    case "unknown": return "Relationship review status unknown";
  }
}

function populateValueFilter(
  root: Document,
  select: HTMLSelectElement,
  allLabel: string,
  values: Readonly<Record<string, number>>,
  label: (value: string) => string,
): void {
  const selected = select.value;
  const entries = Object.entries(values).sort(([left], [right]) => left.localeCompare(right));
  if (selected && !entries.some(([value]) => value === selected)) entries.push([selected, 0]);
  const all = root.createElement("option");
  all.value = "";
  all.textContent = allLabel;
  select.replaceChildren(all, ...entries.map(([value, count]) => {
    const option = root.createElement("option");
    option.value = value;
    option.textContent = `${label(value)} (${count})`;
    return option;
  }));
  select.value = selected;
}

function scopeLabel(row: RequirementRow): string {
  if (row.applicableProducts.length) return row.applicableProducts.map((product) => product.name).join(", ");
  if (row.appliesTo.length || row.appliesToFamilies.length) return "Recorded scope does not match a model product";
  return "Not recorded";
}

function displayValue(value: string | null): string {
  if (!value) return "Not recorded";
  const words = value.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function cleanValue(value: string): string | undefined {
  const cleaned = value.trim();
  return cleaned || undefined;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}
