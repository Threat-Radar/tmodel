import type {
  LibraryDataProvider,
  LibraryRecordDetails,
  LibrarySort,
  LibraryTableQuery,
  LibraryTableResponse,
  LibraryTableRow,
} from "./library-types";
import type { EngineState } from "./engine";
import { DEFAULT_LIBRARY_QUERY, isLibrarySort } from "./library-types";
import { LatestRequestGuard } from "./request-guard";

const SEARCH_DELAY_MS = 250;

export interface LibraryViewElements {
  workspace: HTMLElement;
  sourceNotice: HTMLElement;
  search: HTMLInputElement;
  typeFilter: HTMLSelectElement;
  statusFilter: HTMLSelectElement;
  topicFilter: HTMLSelectElement;
  sortButtons: readonly HTMLButtonElement[];
  resultCount: HTMLElement;
  requestStatus: HTMLElement;
  warning: HTMLElement;
  retryButton: HTMLButtonElement;
  tableRegion: HTMLElement;
  tableBody: HTMLTableSectionElement;
  emptyState: HTMLElement;
  detailTitle: HTMLElement;
  detailType: HTMLElement;
  detailRecordStatus: HTMLElement;
  detailId: HTMLElement;
  detailStatus: HTMLElement;
  detailList: HTMLDListElement;
  detailEvidence: HTMLElement;
  detailEvidenceSummary: HTMLElement;
  detailAssessment: HTMLElement;
  detailAssessmentList: HTMLDListElement;
}

export class LibraryDocumentsView {
  private readonly tableRequests = new LatestRequestGuard();
  private readonly detailRequests = new LatestRequestGuard();
  private readonly rows = new Map<string, LibraryTableRow>();
  private query: LibraryTableQuery = { ...DEFAULT_LIBRARY_QUERY };
  private started = false;
  private engineConnected?: boolean;
  private tableState: "idle" | "loading" | "loaded" | "failed" = "idle";
  private failedRequestStartedConnected = false;
  private selectedId?: string;
  private searchTimer?: ReturnType<typeof setTimeout>;

  constructor(
    private readonly provider: LibraryDataProvider,
    private readonly elements: LibraryViewElements,
    private readonly documentRoot: Document = document,
  ) {
    this.bindControls();
    elements.sourceNotice.textContent = provider.metadata.notice;
    this.setQueryControlsEnabled(provider.metadata.supportsQueries);
  }

  activate(): void {
    if (!this.started) {
      this.started = true;
      void this.loadTable();
    }
  }

  async retry(): Promise<void> {
    await this.loadTable();
  }

  /** Retry one failed startup request when the local engine first becomes healthy. */
  async engineStateChanged(state: EngineState): Promise<void> {
    const wasConnected = this.engineConnected;
    this.engineConnected = state.kind === "connected";
    if (!this.engineConnected) {
      // A failed request made against stale health information becomes eligible
      // for recovery after the engine is observed down and then comes back.
      if (this.tableState === "failed") this.failedRequestStartedConnected = false;
      return;
    }
    if (!this.started || wasConnected === true || this.tableState !== "failed"
      || this.failedRequestStartedConnected) return;
    await this.loadTable();
  }

  currentQuery(): LibraryTableQuery {
    return { ...this.query };
  }

  currentSelection(): string | undefined {
    return this.selectedId;
  }

  async selectRecord(id: string): Promise<void> {
    const row = this.rows.get(id);
    if (!row) return;
    this.selectedId = id;
    this.updateSelectedRow();
    this.renderRowDetails(row, true);

    const request = this.detailRequests.begin();
    try {
      const details = await this.provider.getRecord(id, request.signal);
      if (!this.detailRequests.isCurrent(request) || this.selectedId !== id) return;
      if (details) this.renderDetails(details);
      else this.elements.detailStatus.textContent = "Full record details were not found.";
    } catch (error) {
      if (!this.detailRequests.isCurrent(request) || isAbortError(error)) return;
      this.elements.detailStatus.textContent = `Unable to load full details: ${errorMessage(error)}`;
    } finally {
      this.detailRequests.complete(request);
    }
  }

  private bindControls(): void {
    this.elements.search.addEventListener("input", () => {
      if (!this.provider.metadata.supportsQueries) return;
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.query.search = cleanValue(this.elements.search.value);
        void this.loadTable();
      }, SEARCH_DELAY_MS);
    });
    this.elements.search.addEventListener("search", () => {
      if (!this.provider.metadata.supportsQueries) return;
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.query.search = cleanValue(this.elements.search.value);
      void this.loadTable();
    });
    for (const [element, key] of [
      [this.elements.typeFilter, "type"],
      [this.elements.statusFilter, "status"],
      [this.elements.topicFilter, "topic"],
    ] as const) {
      element.addEventListener("change", () => {
        this.query[key] = cleanValue(element.value);
        void this.loadTable();
      });
    }
    for (const button of this.elements.sortButtons) {
      button.addEventListener("click", () => {
        const sort = button.dataset.sort as LibrarySort | undefined;
        if (!sort || !this.provider.metadata.supportsQueries) return;
        if (this.query.sort === sort) this.query.order = this.query.order === "asc" ? "desc" : "asc";
        else {
          this.query.sort = sort;
          this.query.order = "asc";
        }
        this.updateSortIndicators();
        void this.loadTable();
      });
    }
    this.elements.retryButton.addEventListener("click", () => void this.retry());
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

  private renderResponse(response: LibraryTableResponse): void {
    this.rows.clear();
    for (const row of response.rows) this.rows.set(row.id, row);
    this.populateFacet(this.elements.typeFilter, response.contextual_facets.type, "All types");
    this.populateFacet(this.elements.statusFilter, response.contextual_facets.status, "All statuses");
    this.populateFacet(this.elements.topicFilter, response.contextual_facets.topic, "All topics");
    this.updateSortIndicators(
      isLibrarySort(response.query.sort) ? response.query.sort : null,
      response.query.order,
    );
    this.elements.tableBody.replaceChildren(...response.rows.map((row) => this.createRow(row)));
    this.elements.resultCount.textContent = resultCountText(response.total, response.library.count);
    this.elements.requestStatus.textContent = response.total === 0
      ? "No library documents match the current search and filters."
      : `${response.total} matching library ${response.total === 1 ? "document" : "documents"}.`;
    this.elements.requestStatus.className = "library-request-status";
    this.elements.emptyState.hidden = response.total !== 0;
    this.elements.tableRegion.hidden = response.total === 0;
    this.elements.retryButton.hidden = true;
    this.elements.warning.hidden = response.library.problems.length === 0;
    this.elements.warning.textContent = response.library.problems.length === 0
      ? ""
      : `${response.library.problems.length} library ${response.library.problems.length === 1 ? "record could" : "records could"} not be loaded. Showing the available documents.`;
    if (this.selectedId && this.rows.has(this.selectedId)) this.updateSelectedRow();
    else if (this.selectedId) this.clearDetails();
  }

  private renderError(error: unknown): void {
    this.elements.requestStatus.textContent = `Unable to load library documents: ${errorMessage(error)}`;
    this.elements.requestStatus.className = "library-request-status is-error";
    this.elements.resultCount.textContent = "Unavailable";
    this.elements.tableRegion.hidden = true;
    this.elements.emptyState.hidden = true;
    this.elements.warning.hidden = true;
    this.elements.retryButton.hidden = false;
  }

  private createRow(row: LibraryTableRow): HTMLTableRowElement {
    const tr = this.documentRoot.createElement("tr");
    tr.dataset.recordId = row.id;
    tr.setAttribute("aria-selected", String(row.id === this.selectedId));
    const titleCell = this.documentRoot.createElement("td");
    const titleButton = this.documentRoot.createElement("button");
    titleButton.type = "button";
    titleButton.className = "library-title-button";
    titleButton.textContent = row.title;
    titleButton.addEventListener("click", () => void this.selectRecord(row.id));
    titleCell.append(titleButton);
    tr.append(
      titleCell,
      textCell(this.documentRoot, row.type),
      textCell(this.documentRoot, row.status),
      textCell(this.documentRoot, row.topic ?? "—"),
      textCell(this.documentRoot, row.date ?? "—"),
      textCell(this.documentRoot, reviewedArtifactsLabel(row)),
    );
    return tr;
  }

  private updateSelectedRow(): void {
    for (const row of this.elements.tableBody.querySelectorAll<HTMLTableRowElement>("tr")) {
      const selected = row.dataset.recordId === this.selectedId;
      row.classList.toggle("is-selected", selected);
      row.setAttribute("aria-selected", String(selected));
    }
  }

  private renderRowDetails(row: LibraryTableRow, loading: boolean): void {
    this.renderDetailIdentity(row.title, row.type, row.status, row.id);
    this.elements.detailStatus.textContent = loading ? "Loading full record details…" : "";
    this.renderDetailList([
      ["Topic", row.topic],
      ["Date", row.date],
      ["Publisher", row.publisher],
      ["Maturity", row.maturity],
    ], row.tags, row.url);
    this.renderEvidence(row.artifacts, row.reviewed_artifacts);
    this.renderAssessment(null, {});
  }

  private renderDetails(details: LibraryRecordDetails): void {
    this.renderDetailIdentity(details.title, details.type, details.status, details.id);
    this.elements.detailStatus.textContent = "";
    const reviewed = details.artifacts.filter((artifact) => artifact.reviewed === true).length;
    this.renderDetailList([
      ["Topic", details.topic],
      ["Date", details.date],
      ["Publisher", details.publisher],
      ["Authors", meaningfulValues(details.authors).join(", ")],
      ["Version", details.version],
      ["Maturity", details.maturity],
    ], details.tags, details.content.url ?? null);
    this.renderEvidence(details.artifacts.length, reviewed);
    this.renderAssessment(details.usefulness, details.applicability);
  }

  private renderDetailIdentity(title: string, type: string, status: string, id: string): void {
    this.elements.detailTitle.textContent = title;
    this.elements.detailType.textContent = type;
    this.elements.detailType.hidden = false;
    this.elements.detailRecordStatus.textContent = status;
    this.elements.detailRecordStatus.hidden = false;
    this.elements.detailId.textContent = id;
  }

  private renderDetailList(
    entries: readonly (readonly [string, string | null])[],
    tags: readonly string[],
    sourceUrl: string | null,
  ): void {
    const nodes = entries.flatMap(([label, value]) => {
      const text = meaningfulText(value);
      return text ? [this.createDetailRow(label, text)] : [];
    });
    const populatedTags = meaningfulValues(tags);
    if (populatedTags.length) {
      const tagsList = this.documentRoot.createElement("div");
      tagsList.className = "library-tag-list";
      tagsList.append(...populatedTags.map((tag) => {
        const chip = this.documentRoot.createElement("span");
        chip.className = "library-tag";
        chip.textContent = tag;
        return chip;
      }));
      nodes.push(this.createDetailRow("Tags", tagsList));
    }
    const url = meaningfulText(sourceUrl);
    if (url && isExternalSourceUrl(url)) {
      const link = this.documentRoot.createElement("a");
      link.className = "library-source-link";
      link.textContent = url;
      link.setAttribute("href", url);
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
      link.setAttribute("title", "Open source document");
      nodes.push(this.createDetailRow("Source URL", link));
    }
    this.elements.detailList.replaceChildren(...nodes);
  }

  private createDetailRow(label: string, value: string | HTMLElement): HTMLElement {
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = "detail-row";
    const term = this.documentRoot.createElement("dt");
    term.textContent = label;
    const description = this.documentRoot.createElement("dd");
    if (typeof value === "string") description.textContent = value;
    else description.append(value);
    wrapper.append(term, description);
    return wrapper;
  }

  private renderEvidence(artifacts: number, reviewed: number): void {
    this.elements.detailEvidence.hidden = artifacts === 0;
    this.elements.detailEvidenceSummary.textContent = artifacts === 0
      ? ""
      : `${artifacts} extracted ${artifacts === 1 ? "artifact" : "artifacts"} · ${reviewed} reviewed`;
  }

  private renderAssessment(
    usefulness: LibraryRecordDetails["usefulness"],
    applicability: LibraryRecordDetails["applicability"],
  ): void {
    const entries: Array<readonly [string, string | HTMLElement]> = [];
    const verdict = meaningfulText(usefulness?.verdict);
    const reason = meaningfulText(usefulness?.reason);
    const assessed = meaningfulText(usefulness?.assessed);
    if (verdict) entries.push(["Usefulness", verdict]);
    if (reason) entries.push(["Reason", reason]);
    if (assessed) entries.push(["Assessed", assessed]);
    const applicable = Object.entries(applicability)
      .filter(([key, value]) => meaningfulText(key) && meaningfulText(value));
    if (applicable.length) {
      const list = this.documentRoot.createElement("div");
      list.className = "library-applicability-list";
      list.append(...applicable.map(([key, value]) => {
        const item = this.documentRoot.createElement("span");
        item.className = "library-applicability";
        item.textContent = `${displayKey(key)}: ${value.trim()}`;
        return item;
      }));
      entries.push(["Applicability", list]);
    }
    this.elements.detailAssessment.hidden = entries.length === 0;
    this.elements.detailAssessmentList.replaceChildren(
      ...entries.map(([label, value]) => this.createDetailRow(label, value)),
    );
  }

  private clearDetails(): void {
    this.selectedId = undefined;
    this.detailRequests.cancel();
    this.elements.detailTitle.textContent = "Select a document";
    this.elements.detailType.textContent = "";
    this.elements.detailType.hidden = true;
    this.elements.detailRecordStatus.textContent = "";
    this.elements.detailRecordStatus.hidden = true;
    this.elements.detailId.textContent = "";
    this.elements.detailStatus.textContent = "Choose a row to inspect its full library record.";
    this.elements.detailList.replaceChildren();
    this.renderEvidence(0, 0);
    this.renderAssessment(null, {});
  }

  private populateFacet(
    select: HTMLSelectElement,
    values: Readonly<Record<string, number>>,
    allLabel: string,
  ): void {
    const selected = select.value;
    const all = this.documentRoot.createElement("option");
    all.value = "";
    all.textContent = allLabel;
    const entries = Object.entries(values);
    if (selected && !entries.some(([value]) => value === selected)) entries.push([selected, 0]);
    entries.sort(([left], [right]) => left.localeCompare(right));
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
    activeSort: LibrarySort | null = this.query.sort,
    order = this.query.order,
  ): void {
    for (const button of this.elements.sortButtons) {
      const sort = button.dataset.sort as LibrarySort | undefined;
      const active = sort === activeSort;
      const header = button.closest("th");
      header?.setAttribute("aria-sort", active
        ? (order === "asc" ? "ascending" : "descending")
        : "none");
      button.dataset.order = active ? order : "";
    }
  }

  private setLoading(loading: boolean): void {
    this.elements.workspace.setAttribute("aria-busy", String(loading));
    if (loading) {
      this.elements.requestStatus.textContent = "Loading library documents…";
      this.elements.requestStatus.className = "library-request-status";
      this.elements.retryButton.hidden = true;
    }
  }

  private setQueryControlsEnabled(enabled: boolean): void {
    this.elements.search.disabled = !enabled;
    this.elements.typeFilter.disabled = !enabled;
    this.elements.statusFilter.disabled = !enabled;
    this.elements.topicFilter.disabled = !enabled;
    for (const button of this.elements.sortButtons) button.disabled = !enabled;
    if (!enabled) this.elements.search.title = "Search and filters use the live engine API";
    this.updateSortIndicators();
  }
}

export function libraryViewElements(root: Document = document): LibraryViewElements {
  const required = <T extends HTMLElement>(id: string): T => {
    const element = root.getElementById(id);
    if (!element) throw new Error(`Missing required library element #${id}`);
    return element as T;
  };
  return {
    workspace: required("library-workspace"),
    sourceNotice: required("library-source-notice"),
    search: required("library-search"),
    typeFilter: required("library-type-filter"),
    statusFilter: required("library-status-filter"),
    topicFilter: required("library-topic-filter"),
    sortButtons: [...root.querySelectorAll<HTMLButtonElement>("[data-library-sort]")],
    resultCount: required("library-result-count"),
    requestStatus: required("library-request-status"),
    warning: required("library-warning"),
    retryButton: required("library-retry"),
    tableRegion: required("library-table-region"),
    tableBody: required("library-table-body"),
    emptyState: required("library-empty"),
    detailTitle: required("library-detail-title"),
    detailType: required("library-detail-type"),
    detailRecordStatus: required("library-detail-record-status"),
    detailId: required("library-detail-id"),
    detailStatus: required("library-detail-status"),
    detailList: required("library-detail-list"),
    detailEvidence: required("library-detail-evidence"),
    detailEvidenceSummary: required("library-detail-evidence-summary"),
    detailAssessment: required("library-detail-assessment"),
    detailAssessmentList: required("library-detail-assessment-list"),
  };
}

export function reviewedArtifactsLabel(row: Pick<LibraryTableRow, "artifacts" | "reviewed_artifacts">): string {
  return row.artifacts === 0
    ? "No extracted artifacts"
    : `${row.reviewed_artifacts} / ${row.artifacts} reviewed`;
}

function resultCountText(total: number, libraryCount: number): string {
  const totalLabel = `${total} ${total === 1 ? "document" : "documents"}`;
  if (total === libraryCount) return totalLabel;
  return `${totalLabel} of ${libraryCount} ${libraryCount === 1 ? "document" : "documents"}`;
}

function cleanValue(value: string): string | undefined {
  const cleaned = value.trim();
  return cleaned || undefined;
}

function meaningfulText(value: string | null | undefined): string | undefined {
  const cleaned = value?.trim();
  return cleaned || undefined;
}

function meaningfulValues(values: readonly string[]): string[] {
  return values.map((value) => value.trim()).filter(Boolean);
}

function isExternalSourceUrl(value: string): boolean {
  try {
    const protocol = new URL(value).protocol;
    return protocol === "http:" || protocol === "https:";
  } catch {
    return false;
  }
}

function displayKey(value: string): string {
  const words = value.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function textCell(root: Document, text: string): HTMLTableCellElement {
  const cell = root.createElement("td");
  cell.textContent = text;
  return cell;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}
