import {
  bindClearFilters, EMPTY_INSPECTOR, LIBRARY_PAGE_SIZE, renderPagination, resetPagination,
  type LibraryPagination,
} from "./library-presentation";
import {
  CatalogEntryRenderer, capecDefinitionUrl, displayValue, externalLink, safeLinkRows,
} from "./catalog-entry-render";
import type { EngineState } from "./engine";
import { fieldItems, fieldValues, safeHttpUrl } from "./weakness-fields";
import {
  DEFAULT_WEAKNESS_QUERY,
  isWeaknessSort,
  type WeaknessDataProvider,
  type WeaknessDetailResponse,
  type WeaknessEntry,
  type WeaknessSort,
  type WeaknessTableQuery,
  type WeaknessTableResponse,
  type WeaknessTableRow,
} from "./weakness-types";
import { LatestRequestGuard } from "./request-guard";

const SEARCH_DELAY_MS = 250;
// The CWE fields the inspector's named sections show; any other appears under Additional Catalog Fields.
const CWE_FIELDS_SHOWN: ReadonlySet<string> = new Set([
  "@ID", "@Name", "@Abstraction", "@Structure", "@Status", "Description",
  "Extended_Description", "Background_Details", "Applicable_Platforms",
  "Alternate_Terms",
  "Modes_Of_Introduction", "Common_Consequences", "Detection_Methods",
  "Potential_Mitigations", "Demonstrative_Examples", "Observed_Examples",
  "Related_Attack_Patterns", "Taxonomy_Mappings", "Likelihood_Of_Exploit",
  "Content_History",
]);

export interface WeaknessViewElements extends LibraryPagination {
  workspace: HTMLElement;
  sourceNotice: HTMLElement;
  search: HTMLInputElement;
  abstractionFilter: HTMLSelectElement;
  structureFilter: HTMLSelectElement;
  statusFilter: HTMLSelectElement;
  usageFilter: HTMLSelectElement;
  sortButtons: readonly HTMLButtonElement[];
  clearFilters: HTMLButtonElement;
  requestStatus: HTMLElement;
  warning: HTMLElement;
  retryButton: HTMLButtonElement;
  tableRegion: HTMLElement;
  tableBody: HTMLTableSectionElement;
  emptyState: HTMLElement;
  sortHelp: HTMLElement;
  attributionNotice: HTMLElement;
  attributionLicense: HTMLElement;
  attributionTerms: HTMLAnchorElement;
  detailTitle: HTMLElement;
  detailId: HTMLElement;
  detailBadges: HTMLElement;
  detailDescription: HTMLElement;
  detailList: HTMLDListElement;
  detailStatus: HTMLElement;
  detailRetryButton: HTMLButtonElement;
  detailSections: HTMLElement;
}

export class WeaknessesView {
  private readonly tableRequests = new LatestRequestGuard();
  private readonly detailRequests = new LatestRequestGuard();
  private readonly rows = new Map<string, WeaknessTableRow>();
  private query: WeaknessTableQuery = { ...DEFAULT_WEAKNESS_QUERY, limit: LIBRARY_PAGE_SIZE };
  private started = false;
  private engineConnected?: boolean;
  private tableState: "idle" | "loading" | "loaded" | "failed" = "idle";
  private failedRequestStartedConnected = false;
  private selectedId?: string;
  private searchTimer?: ReturnType<typeof setTimeout>;
  private readonly render: CatalogEntryRenderer;

  constructor(
    private readonly provider: WeaknessDataProvider,
    private readonly elements: WeaknessViewElements,
    private readonly documentRoot: Document = document,
  ) {
    this.render = new CatalogEntryRenderer(documentRoot, "weakness");
    this.bindControls();
    elements.sourceNotice.textContent = provider.metadata.notice;
    if (provider.metadata.detailLevel === "row-only") {
      elements.search.placeholder = "CWE ID, name, or description";
      elements.search.title = "The sample table does not include alternate terms";
    }
    this.updateSortIndicators();
  }

  activate(): void {
    if (!this.started) {
      this.started = true;
      void this.loadTable();
    }
  }

  currentQuery(): WeaknessTableQuery {
    return { ...this.query };
  }

  currentSelection(): string | undefined {
    return this.selectedId;
  }

  async retry(): Promise<void> {
    await this.loadTable();
  }

  async engineStateChanged(state: EngineState): Promise<void> {
    const wasConnected = this.engineConnected;
    this.engineConnected = state.kind === "connected";
    if (!this.engineConnected) {
      if (this.tableState === "failed") this.failedRequestStartedConnected = false;
      return;
    }
    if (!this.started || wasConnected === true || this.tableState !== "failed"
      || this.failedRequestStartedConnected) return;
    await this.loadTable();
  }

  async selectWeakness(id: string): Promise<void> {
    const row = this.rows.get(id);
    if (!row) return;
    this.selectedId = id;
    this.updateSelectedRow();
    this.renderRowDetails(row);
    if (this.provider.metadata.detailLevel === "row-only") {
      this.elements.detailStatus.textContent =
        "This nine-record preview contains table rows only. Connect the local engine to inspect the full CWE entry.";
      return;
    }
    await this.loadDetails(id);
  }

  private bindControls(): void {
    this.elements.search.addEventListener("input", () => {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.query.search = cleanValue(this.elements.search.value);
        this.query.offset = 0;
        void this.loadTable();
      }, SEARCH_DELAY_MS);
    });
    this.elements.search.addEventListener("search", () => {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.query.search = cleanValue(this.elements.search.value);
      this.query.offset = 0;
      void this.loadTable();
    });
    for (const [element, key] of [
      [this.elements.abstractionFilter, "abstraction"],
      [this.elements.structureFilter, "structure"],
      [this.elements.statusFilter, "status"],
      [this.elements.usageFilter, "usage"],
    ] as const) {
      element.addEventListener("change", () => {
        this.query[key] = cleanValue(element.value);
        this.query.offset = 0;
        void this.loadTable();
      });
    }
    for (const button of this.elements.sortButtons) {
      button.addEventListener("click", () => {
        const sort = button.dataset.sort;
        if (!sort || !isWeaknessSort(sort)) return;
        if (this.query.sort === sort) this.query.order = this.query.order === "asc" ? "desc" : "asc";
        else {
          this.query.sort = sort;
          this.query.order = "asc";
        }
        this.query.offset = 0;
        this.updateSortIndicators();
        void this.loadTable();
      });
    }
    const { clearFilters, search, abstractionFilter, structureFilter, statusFilter, usageFilter } = this.elements;
    bindClearFilters(clearFilters, search, [abstractionFilter, structureFilter, statusFilter, usageFilter], () => {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.query.search = this.query.abstraction = this.query.structure = this.query.status = this.query.usage = undefined;
      this.query.offset = 0;
      void this.loadTable();
    });
    this.elements.previousPage.addEventListener("click", () => {
      if (this.tableState !== "loaded") return;
      this.query.offset = Math.max(0, this.query.offset - this.query.limit);
      void this.loadTable();
    });
    this.elements.nextPage.addEventListener("click", () => {
      if (this.tableState !== "loaded") return;
      this.query.offset += this.query.limit;
      void this.loadTable();
    });
    this.elements.retryButton.addEventListener("click", () => void this.retry());
    this.elements.detailRetryButton.addEventListener("click", () => {
      if (this.selectedId) void this.loadDetails(this.selectedId);
    });
  }

  private async loadTable(): Promise<void> {
    const requestStartedConnected = this.engineConnected === true;
    const request = this.tableRequests.begin();
    this.tableState = "loading";
    this.setLoading(true);
    let recoverAfterFailure = false;
    try {
      const response = await this.provider.getTable(this.query, request.signal);
      if (!this.tableRequests.isCurrent(request)) return;
      if (response.count === 0 && response.query.offset > 0) {
        this.query.offset = Math.max(0, Math.floor((response.total - 1) / this.query.limit) * this.query.limit);
        if (this.query.offset < response.query.offset) {
          await this.loadTable();
          return;
        }
      }
      this.renderResponse(response);
      this.tableState = "loaded";
    } catch (error) {
      if (!this.tableRequests.isCurrent(request) || isAbortError(error)) return;
      this.tableState = "failed";
      this.failedRequestStartedConnected = requestStartedConnected;
      this.renderError(error);
      recoverAfterFailure = this.engineConnected === true && !requestStartedConnected;
    } finally {
      if (this.tableRequests.isCurrent(request)) this.setLoading(false);
      this.tableRequests.complete(request);
    }
    if (recoverAfterFailure) await this.loadTable();
  }

  private async loadDetails(id: string): Promise<void> {
    const request = this.detailRequests.begin();
    this.elements.detailStatus.textContent = "Loading full CWE details…";
    this.elements.detailRetryButton.hidden = true;
    try {
      const response = await this.provider.getWeakness(id, request.signal);
      if (!this.detailRequests.isCurrent(request) || this.selectedId !== id) return;
      if (response?.entry) this.renderDetails(response);
      else this.elements.detailStatus.textContent = "The full CWE entry was not found.";
    } catch (error) {
      if (!this.detailRequests.isCurrent(request) || isAbortError(error)) return;
      this.elements.detailStatus.textContent = `Unable to load full CWE details: ${errorMessage(error)}`;
      this.elements.detailRetryButton.hidden = false;
    } finally {
      this.detailRequests.complete(request);
    }
  }

  private renderResponse(response: WeaknessTableResponse): void {
    this.rows.clear();
    for (const row of response.rows) this.rows.set(row.id, row);
    this.populateFacet(this.elements.abstractionFilter, response.contextual_facets.abstraction, "All abstractions");
    this.populateFacet(this.elements.structureFilter, response.contextual_facets.structure, "All structures");
    this.populateFacet(this.elements.statusFilter, response.contextual_facets.status, "All statuses");
    this.populateFacet(this.elements.usageFilter, response.contextual_facets.usage, "All usages");
    this.updateSortIndicators(
      isWeaknessSort(response.query.sort) ? response.query.sort : null,
      response.query.order,
    );
    this.elements.tableBody.replaceChildren(...response.rows.map((row) => this.createRow(row)));
    this.elements.tableRegion.scrollTop = 0;
    this.elements.requestStatus.textContent = "";
    this.elements.requestStatus.className = "library-request-status";
    this.elements.emptyState.textContent = response.catalog.weaknesses === 0
      ? "No CWE weaknesses are available."
      : "No CWE weaknesses match the current search and filters.";
    this.elements.emptyState.hidden = response.total !== 0;
    this.elements.tableRegion.hidden = response.total === 0;
    this.elements.retryButton.hidden = true;
    renderPagination(this.elements, response.query.offset, response.count, response.total);
    this.renderAttribution(response);
    const unknown = response.catalog.unknown_fields;
    this.elements.warning.hidden = unknown === 0;
    this.elements.warning.textContent = unknown === 0
      ? ""
      : `${unknown} catalog ${unknown === 1 ? "field is" : "fields are"} not recognized by this importer. The raw fields remain preserved in entry details.`;
    if (this.selectedId && this.rows.has(this.selectedId)) this.updateSelectedRow();
    else if (this.selectedId) this.clearDetails();
  }

  private renderAttribution(response: WeaknessTableResponse): void {
    this.elements.attributionNotice.textContent = response.catalog.notice;
    this.elements.attributionLicense.textContent = response.catalog.license;
    const terms = safeHttpUrl(response.catalog.terms_url);
    this.elements.attributionTerms.hidden = !terms;
    if (terms) this.elements.attributionTerms.href = terms;
  }

  private renderError(error: unknown): void {
    this.elements.requestStatus.textContent = `Unable to load CWE weaknesses: ${errorMessage(error)}`;
    this.elements.requestStatus.className = "library-request-status is-error";
    this.rows.clear();
    this.clearDetails();
    this.elements.tableRegion.hidden = true;
    this.elements.emptyState.hidden = true;
    this.elements.warning.hidden = true;
    this.elements.retryButton.hidden = false;
    resetPagination(this.elements);
  }

  private createRow(row: WeaknessTableRow): HTMLTableRowElement {
    const tr = this.documentRoot.createElement("tr");
    tr.dataset.weaknessId = row.id;
    tr.setAttribute("aria-selected", String(row.id === this.selectedId));
    const idCell = this.documentRoot.createElement("td");
    const button = this.documentRoot.createElement("button");
    button.type = "button";
    button.className = "library-title-button";
    button.textContent = row.id;
    button.addEventListener("click", () => void this.selectWeakness(row.id));
    idCell.append(button);
    tr.append(
      idCell,
      textCell(this.documentRoot, row.name),
      textCell(this.documentRoot, row.abstraction ?? "—"),
      textCell(this.documentRoot, row.structure ?? "—"),
      textCell(this.documentRoot, row.status),
      textCell(this.documentRoot, row.usage ?? "—"),
      textCell(this.documentRoot, row.likelihood ?? "—"),
      numericCell(this.documentRoot, row.attack_patterns, "CAPEC mappings"),
      numericCell(this.documentRoot, row.observed_examples, "observed examples"),
      numericCell(this.documentRoot, row.mitigations, "mitigations"),
    );
    return tr;
  }

  private updateSelectedRow(): void {
    for (const row of this.elements.tableBody.querySelectorAll<HTMLTableRowElement>("tr")) {
      const selected = row.dataset.weaknessId === this.selectedId;
      row.classList.toggle("is-selected", selected);
      row.setAttribute("aria-selected", String(selected));
    }
  }

  private renderRowDetails(row: WeaknessTableRow): void {
    this.elements.detailTitle.textContent = row.name;
    this.elements.detailId.textContent = row.id;
    this.elements.detailDescription.textContent = row.description;
    this.renderOverview(row);
    this.elements.detailSections.replaceChildren();
    this.elements.detailRetryButton.hidden = true;
  }

  private renderDetails(response: WeaknessDetailResponse): void {
    const entry = response.entry;
    if (!entry) return;
    this.elements.detailTitle.textContent = entry.name;
    this.elements.detailId.textContent = entry.id;
    this.elements.detailDescription.textContent = entry.description;
    const row = this.rows.get(entry.id);
    if (row) this.renderOverview({
      ...row,
      abstraction: entry.abstraction,
      structure: entry.structure,
      usage: entry.usage,
      likelihood: entry.likelihood,
      status: entry.status,
    });
    this.elements.detailStatus.textContent = "";
    this.elements.detailRetryButton.hidden = true;
    const sections: HTMLElement[] = [];
    sections.push(...this.render.fieldSection(entry, "Extended Description", "Extended_Description", { open: true }));
    sections.push(...this.render.alternateTerms(entry));
    sections.push(...this.backgroundAndPlatforms(entry));
    sections.push(...this.render.itemSection(entry, "Modes of Introduction", "Modes_Of_Introduction", ["Introduction"]));
    sections.push(...this.render.itemSection(entry, "Common Consequences", "Common_Consequences", ["Consequence"]));
    sections.push(...this.render.itemSection(entry, "Detection Methods", "Detection_Methods", ["Detection_Method"]));
    sections.push(...this.render.itemSection(entry, "Potential Mitigations", "Potential_Mitigations", ["Mitigation"]));
    sections.push(...this.render.itemSection(entry, "Demonstrative Examples", "Demonstrative_Examples", ["Demonstrative_Example"]));
    sections.push(...this.observedExamples(entry));
    sections.push(...this.render.identifierList("Related CAPEC Attack Patterns", entry.attack_patterns, capecDefinitionUrl));
    sections.push(...this.render.itemSection(entry, "Taxonomy Mappings", "Taxonomy_Mappings", ["Taxonomy_Mapping"]));
    sections.push(...this.render.assertions(response.objects?.assertions ?? []));
    sections.push(...this.render.additionalFields(entry, CWE_FIELDS_SHOWN));
    sections.push(...this.render.contentHistory(entry));
    this.elements.detailSections.replaceChildren(...sections);
  }

  private renderOverview(row: WeaknessTableRow): void {
    this.elements.detailBadges.replaceChildren(...(row.status ? [this.render.badge(row.status)] : []));
    const attributes: [string, string | null][] = [
      ["Abstraction", row.abstraction], ["Structure", row.structure], ["Usage", row.usage], ["Likelihood", row.likelihood],
    ];
    this.elements.detailList.replaceChildren(
      ...attributes.flatMap(([label, value]) => value ? [this.render.detailRow(label, value)] : []),
      this.render.detailRow("CAPEC mappings", String(row.attack_patterns)),
      this.render.detailRow("Observed examples", String(row.observed_examples)),
      this.render.detailRow("Mitigations", String(row.mitigations)),
      ...safeLinkRows(this.documentRoot, "Official definition", row.url, `View ${row.id} on cwe.mitre.org`),
    );
  }

  private backgroundAndPlatforms(entry: WeaknessEntry): HTMLElement[] {
    const background = fieldItems(entry, "Background_Details", "Background_Detail");
    const backgroundValues = background.length ? background : fieldValues(entry, "Background_Details");
    const platforms = ["Language", "Operating_System", "Architecture", "Technology", "Class"]
      .flatMap((item) => fieldItems(entry, "Applicable_Platforms", item));
    const platformValues = platforms.length ? platforms : fieldValues(entry, "Applicable_Platforms");
    const groups = [
      this.render.valueGroup("Background", backgroundValues),
      this.render.valueGroup("Applicable Platforms", platformValues),
    ].filter((group): group is HTMLElement => group !== undefined);
    if (!groups.length) return [];
    return [this.render.detailSection("Background and Applicable Platforms", this.render.groups(groups), {
      count: backgroundValues.length + platformValues.length,
    })];
  }

  private observedExamples(entry: WeaknessEntry): HTMLElement[] {
    if (!entry.observed_examples.length) return [];
    const list = this.documentRoot.createElement("ul");
    list.className = "weakness-detail-items";
    list.append(...entry.observed_examples.map((example) => {
      const item = this.documentRoot.createElement("li");
      const reference = safeHttpUrl(example.link)
        ? externalLink(
          this.documentRoot,
          example.reference,
          safeHttpUrl(example.link)!,
          "weakness-identifier-link",
        )
        : this.render.identifier(example.reference);
      item.append(reference, this.documentRoot.createTextNode(` — ${example.description}`));
      return item;
    }));
    return [this.render.detailSection("Observed Examples and CVE References", list, {
      count: entry.observed_examples.length,
    })];
  }

  private clearDetails(): void {
    this.selectedId = undefined;
    this.detailRequests.cancel();
    this.elements.detailTitle.textContent = "";
    this.elements.detailId.textContent = "";
    this.elements.detailBadges.replaceChildren();
    this.elements.detailDescription.textContent = "";
    this.elements.detailList.replaceChildren();
    this.elements.detailSections.replaceChildren();
    this.elements.detailRetryButton.hidden = true;
    this.elements.detailStatus.textContent = EMPTY_INSPECTOR;
  }

  private populateFacet(
    select: HTMLSelectElement,
    values: Readonly<Record<string, number>>,
    allLabel: string,
  ): void {
    const selected = select.value;
    const entries = Object.entries(values);
    if (selected && !entries.some(([value]) => value === selected)) entries.push([selected, 0]);
    entries.sort(([left], [right]) => left.localeCompare(right));
    const all = this.documentRoot.createElement("option");
    all.value = "";
    all.textContent = allLabel;
    const options = entries.map(([value, count]) => {
      const option = this.documentRoot.createElement("option");
      option.value = value;
      option.textContent = `${value} (${count})`;
      return option;
    });
    select.replaceChildren(all, ...options);
    select.value = selected;
  }

  private updateSortIndicators(
    activeSort: WeaknessSort | null = this.query.sort,
    order = this.query.order,
  ): void {
    for (const button of this.elements.sortButtons) {
      const active = button.dataset.sort === activeSort;
      button.closest("th")?.setAttribute("aria-sort", active
        ? (order === "asc" ? "ascending" : "descending")
        : "none");
      button.dataset.order = active ? order : "";
    }
    const semanticHelp = activeSort === "likelihood"
      ? " Ascending follows CWE order: High → Medium → Low → Unknown; unrated entries follow."
      : "";
    this.elements.sortHelp.textContent = activeSort
      ? `${displayValue(activeSort)} sorted ${order === "asc" ? "ascending" : "descending"}.${semanticHelp} Select the column again to reverse it.`
      : "Select a column heading to sort.";
  }

  private setLoading(loading: boolean): void {
    this.elements.workspace.setAttribute("aria-busy", String(loading));
    if (loading) {
      this.elements.requestStatus.textContent = "Loading CWE weaknesses…";
      this.elements.requestStatus.className = "library-request-status";
      this.elements.retryButton.hidden = true;
      this.elements.emptyState.hidden = true;
    }
  }
}

export function weaknessViewElements(root: Document = document): WeaknessViewElements {
  const required = <T extends HTMLElement>(id: string): T => {
    const element = root.getElementById(id);
    if (!element) throw new Error(`Missing required weakness element #${id}`);
    return element as T;
  };
  return {
    workspace: required("weakness-workspace"),
    sourceNotice: required("weakness-source-notice"),
    search: required("weakness-search"),
    abstractionFilter: required("weakness-abstraction-filter"),
    structureFilter: required("weakness-structure-filter"),
    statusFilter: required("weakness-status-filter"),
    usageFilter: required("weakness-usage-filter"),
    sortButtons: [...root.querySelectorAll<HTMLButtonElement>("[data-weakness-sort]")],
    clearFilters: required("weakness-clear-filters"),
    requestStatus: required("weakness-request-status"),
    warning: required("weakness-warning"),
    retryButton: required("weakness-retry"),
    tableRegion: required("weakness-table-region"),
    tableBody: required("weakness-table-body"),
    emptyState: required("weakness-empty"),
    previousPage: required("weakness-page-previous"),
    nextPage: required("weakness-page-next"),
    pageStatus: required("weakness-page-status"),
    sortHelp: required("weakness-sort-help"),
    attributionNotice: required("weakness-attribution-notice"),
    attributionLicense: required("weakness-attribution-license"),
    attributionTerms: required("weakness-attribution-terms"),
    detailTitle: required("weakness-detail-title"),
    detailId: required("weakness-detail-id"),
    detailBadges: required("weakness-detail-badges"),
    detailDescription: required("weakness-detail-description"),
    detailList: required("weakness-detail-list"),
    detailStatus: required("weakness-detail-status"),
    detailRetryButton: required("weakness-detail-retry"),
    detailSections: required("weakness-detail-sections"),
  };
}

function textCell(root: Document, value: string): HTMLTableCellElement {
  const cell = root.createElement("td");
  cell.textContent = value;
  return cell;
}

function numericCell(root: Document, value: number, label: string): HTMLTableCellElement {
  const cell = textCell(root, String(value));
  cell.className = "weakness-count-cell";
  cell.setAttribute("aria-label", `${value} ${label}`);
  return cell;
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
