import {
  ATTACK_PATTERN_ENUMERATION_ORDER,
  DEFAULT_ATTACK_PATTERN_QUERY,
  isAttackPatternSort,
  type AttackPatternDataProvider,
  type AttackPatternDetailResponse,
  type AttackPatternEntry,
  type AttackPatternFilter,
  type AttackPatternReference,
  type AttackPatternSort,
  type AttackPatternTableQuery,
  type AttackPatternTableResponse,
  type AttackPatternTableRow,
} from "./attack-pattern-types";
import {
  CatalogEntryRenderer, attackTechniqueUrl, capecDefinitionUrl, cweDefinitionUrl, externalLink,
  safeLinkRows,
} from "./catalog-entry-render";
import type { EngineState } from "./engine";
import {
  bindClearFilters, EMPTY_INSPECTOR, LIBRARY_PAGE_SIZE, renderPagination, resetPagination,
  type LibraryPagination,
} from "./library-presentation";
import { LatestRequestGuard } from "./request-guard";
import { fieldItems, readableCweText, safeHttpUrl } from "./weakness-fields";
import type { CweFieldValue } from "./weakness-types";

const SEARCH_DELAY_MS = 250;
/** What a cell shows when CAPEC gives the entry no value for that column. */
export const NOT_STATED = "Not stated";
// Every Attack_Pattern field of CAPEC XML Schema 3.5 (engine/engine/load/capec.py
// ENTRY_FIELDS) has a place in the inspector; a field a newer schema adds appears under
// Additional Catalog Fields.
const CAPEC_FIELDS_SHOWN: ReadonlySet<string> = new Set([
  "@ID", "@Name", "@Abstraction", "@Status", "Description", "Extended_Description",
  "Alternate_Terms", "Likelihood_Of_Attack", "Typical_Severity", "Related_Attack_Patterns",
  "Execution_Flow", "Prerequisites", "Skills_Required", "Resources_Required", "Indicators",
  "Consequences", "Mitigations", "Example_Instances", "Related_Weaknesses",
  "Taxonomy_Mappings", "References", "Notes", "Content_History",
]);
const SORT_LABELS: Readonly<Record<AttackPatternSort, string>> = {
  id: "ID",
  name: "Name",
  abstraction: "Abstraction",
  status: "Status",
  likelihood: "Likelihood",
  severity: "Severity",
};

export interface AttackPatternViewElements extends LibraryPagination {
  workspace: HTMLElement;
  sourceNotice: HTMLElement;
  search: HTMLInputElement;
  abstractionFilter: HTMLSelectElement;
  statusFilter: HTMLSelectElement;
  likelihoodFilter: HTMLSelectElement;
  severityFilter: HTMLSelectElement;
  sortButtons: readonly HTMLButtonElement[];
  clearFilters: HTMLButtonElement;
  requestStatus: HTMLElement;
  warning: HTMLElement;
  retryButton: HTMLButtonElement;
  tableRegion: HTMLElement;
  tableBody: HTMLTableSectionElement;
  emptyState: HTMLElement;
  sortHelp: HTMLElement;
  attribution: HTMLElement;
  attributionSummary: HTMLElement;
  attributionNotice: HTMLElement;
  attributionLicense: HTMLElement;
  attributionTerms: HTMLAnchorElement;
  inspector: HTMLElement;
  backToRow: HTMLButtonElement;
  detailTitle: HTMLElement;
  detailId: HTMLElement;
  detailBadges: HTMLElement;
  detailDescription: HTMLElement;
  detailList: HTMLDListElement;
  detailStatus: HTMLElement;
  detailRetryButton: HTMLButtonElement;
  detailSections: HTMLElement;
}

/** The CAPEC attack patterns table and its details inspector (#236), over the engine's feed. */
export class AttackPatternsView {
  private readonly tableRequests = new LatestRequestGuard();
  private readonly detailRequests = new LatestRequestGuard();
  private readonly rows = new Map<string, AttackPatternTableRow>();
  private readonly render: CatalogEntryRenderer;
  private readonly query: AttackPatternTableQuery;
  private started = false;
  private engineConnected?: boolean;
  private tableState: "idle" | "loading" | "loaded" | "failed" = "idle";
  private failedRequestStartedConnected = false;
  private selectedId?: string;
  private searchTimer?: ReturnType<typeof setTimeout>;

  constructor(
    private readonly provider: AttackPatternDataProvider,
    private readonly elements: AttackPatternViewElements,
    private readonly documentRoot: Document = document,
    private readonly pageSize: number = LIBRARY_PAGE_SIZE,
  ) {
    this.render = new CatalogEntryRenderer(documentRoot, "attack-pattern");
    this.query = { ...DEFAULT_ATTACK_PATTERN_QUERY, limit: pageSize };
    this.bindControls();
    elements.sourceNotice.textContent = provider.metadata.notice;
    this.updateSortIndicators();
  }

  activate(): void {
    if (!this.started) {
      this.started = true;
      void this.loadTable();
    }
  }

  currentQuery(): AttackPatternTableQuery {
    return { ...this.query };
  }

  currentSelection(): string | undefined {
    return this.selectedId;
  }

  async retry(): Promise<void> {
    await this.loadTable();
  }

  /** Retry one failed startup request when the local engine first becomes healthy. */
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

  async selectAttackPattern(id: string): Promise<void> {
    const row = this.rows.get(id);
    if (!row) return;
    this.selectedId = id;
    this.updateSelectedRow();
    this.renderRowDetails(row);
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
    for (const [element, key] of this.filters()) {
      element.addEventListener("change", () => {
        this.query[key] = cleanValue(element.value);
        this.query.offset = 0;
        void this.loadTable();
      });
    }
    for (const button of this.elements.sortButtons) {
      button.addEventListener("click", () => {
        const sort = button.dataset.sort;
        if (!sort || !isAttackPatternSort(sort)) return;
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
    bindClearFilters(this.elements.clearFilters, this.elements.search, this.filters().map(([element]) => element), () => {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.query.search = this.query.abstraction = this.query.status = undefined;
      this.query.likelihood = this.query.severity = undefined;
      this.query.offset = 0;
      void this.loadTable();
    });
    this.elements.previousPage.addEventListener("click", () => this.changePage("previous"));
    this.elements.nextPage.addEventListener("click", () => this.changePage("next"));
    this.elements.backToRow.addEventListener("click", () => this.focusTable(this.selectedId));
    this.elements.retryButton.addEventListener("click", () => {
      // The button hides while the table loads; keep a keyboard user's focus in the view.
      const hadFocus = this.documentRoot.activeElement === this.elements.retryButton;
      void this.retry();
      if (hadFocus) this.elements.search.focus();
    });
    this.elements.detailRetryButton.addEventListener("click", () => {
      if (!this.selectedId) return;
      const hadFocus = this.documentRoot.activeElement === this.elements.detailRetryButton;
      void this.loadDetails(this.selectedId);
      if (hadFocus) this.elements.inspector.focus();
    });
  }

  private filters(): readonly (readonly [HTMLSelectElement, AttackPatternFilter])[] {
    return [
      [this.elements.abstractionFilter, "abstraction"],
      [this.elements.statusFilter, "status"],
      [this.elements.likelihoodFilter, "likelihood"],
      [this.elements.severityFilter, "severity"],
    ];
  }

  private changePage(direction: "previous" | "next"): void {
    if (this.tableState !== "loaded") return;
    this.query.offset = direction === "previous"
      ? Math.max(0, this.query.offset - this.query.limit)
      : this.query.offset + this.query.limit;
    void this.loadTable();
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
        // The catalog has fewer pages than the asked offset: show its last page instead.
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
    this.elements.detailStatus.textContent = "Loading full CAPEC details…";
    this.elements.detailRetryButton.hidden = true;
    try {
      const response = await this.provider.getAttackPattern(id, request.signal);
      if (!this.detailRequests.isCurrent(request) || this.selectedId !== id) return;
      if (response?.entry) this.renderDetails(response, response.entry);
      else this.elements.detailStatus.textContent = "The full CAPEC entry was not found.";
    } catch (error) {
      if (!this.detailRequests.isCurrent(request) || isAbortError(error)) return;
      this.elements.detailStatus.textContent = `Unable to load full CAPEC details: ${errorMessage(error)}`;
      this.elements.detailRetryButton.hidden = false;
    } finally {
      this.detailRequests.complete(request);
    }
  }

  private renderResponse(response: AttackPatternTableResponse): void {
    const active = this.documentRoot.activeElement;
    const tableHadFocus = this.focusInTable();
    const focusedRow = active && this.elements.tableBody.contains(active)
      ? active.closest<HTMLTableRowElement>("tr")?.dataset.attackPatternId
      : undefined;
    this.rows.clear();
    for (const row of response.rows) this.rows.set(row.id, row);
    const facets = response.contextual_facets;
    this.populateFacet(this.elements.abstractionFilter, facets.abstraction, "All abstractions", "abstraction");
    this.populateFacet(this.elements.statusFilter, facets.status, "All statuses", "status");
    this.populateFacet(this.elements.likelihoodFilter, facets.likelihood, "All likelihoods", "likelihood");
    this.populateFacet(this.elements.severityFilter, facets.severity, "All severities", "severity");
    this.updateSortIndicators(
      isAttackPatternSort(response.query.sort) ? response.query.sort : null,
      response.query.order,
    );
    this.elements.tableBody.replaceChildren(...response.rows.map((row) => this.createRow(row)));
    this.elements.tableRegion.scrollTop = 0;
    this.elements.requestStatus.textContent = "";
    this.elements.requestStatus.className = "library-request-status";
    this.elements.emptyState.textContent = response.catalog.attack_patterns === 0
      ? "No CAPEC attack patterns are available."
      : "No CAPEC attack patterns match the current search and filters.";
    this.elements.emptyState.hidden = response.total !== 0;
    this.elements.tableRegion.hidden = response.total === 0;
    this.elements.retryButton.hidden = true;
    renderPagination(this.elements, response.query.offset, response.count, response.total, this.pageSize);
    this.renderSource(response);
    this.renderAttribution(response);
    const unknown = response.catalog.unknown_fields;
    this.elements.warning.hidden = unknown === 0;
    this.elements.warning.textContent = unknown === 0
      ? ""
      : `${unknown} catalog ${unknown === 1 ? "field is" : "fields are"} not recognized by this importer. The raw fields remain preserved in entry details.`;
    if (this.selectedId && this.rows.has(this.selectedId)) this.updateSelectedRow();
    else if (this.selectedId) {
      if (this.elements.inspector.contains(active)) this.focusTable();
      this.clearDetails();
    }
    if (focusedRow || (tableHadFocus && response.total === 0)) this.focusTable(focusedRow);
    else this.restorePageFocus(active);
  }

  /** A page control that becomes unavailable hands focus to the other one or the table. */
  private restorePageFocus(active: Element | null): void {
    const { previousPage, nextPage } = this.elements;
    if (active !== previousPage && active !== nextPage) return;
    const [kept, other] = active === previousPage ? [previousPage, nextPage] : [nextPage, previousPage];
    if (!kept.disabled && !kept.hidden) return;
    if (!other.disabled && !other.hidden) other.focus();
    else this.focusTable();
  }

  private focusTable(id?: string): void {
    const { search, tableBody, tableRegion } = this.elements;
    if (tableRegion.hidden) {
      search.focus();
      return;
    }
    const button = id ? [...tableBody.querySelectorAll("tr")]
      .find((row) => row.dataset.attackPatternId === id)?.querySelector("button") : undefined;
    (button ?? tableRegion).focus();
  }

  private renderSource(response: AttackPatternTableResponse): void {
    const { catalog } = response;
    this.elements.sourceNotice.textContent = this.provider.metadata.source === "engine"
      ? `${this.provider.metadata.notice} · ${catalog.name} ${catalog.version} (${catalog.date}), `
        + `${catalog.attack_patterns} attack patterns`
      : this.provider.metadata.notice;
  }

  private renderAttribution(response: AttackPatternTableResponse): void {
    this.elements.attributionSummary.textContent = attributionSummary(response.catalog.notice);
    this.elements.attributionNotice.textContent = response.catalog.notice;
    this.elements.attributionLicense.textContent = response.catalog.license;
    const terms = safeHttpUrl(response.catalog.terms_url);
    this.elements.attributionTerms.hidden = !terms;
    if (terms) this.elements.attributionTerms.href = terms;
    this.elements.attribution.hidden = false;
  }

  /** Whether keyboard focus is on something a failed or empty answer hides: the table or its pager. */
  private focusInTable(): boolean {
    const active = this.documentRoot.activeElement;
    return active !== null && (this.elements.tableRegion.contains(active)
      || active === this.elements.previousPage || active === this.elements.nextPage);
  }

  private renderError(error: unknown): void {
    const active = this.documentRoot.activeElement;
    const needsFocus = this.focusInTable() || this.elements.inspector.contains(active);
    this.elements.requestStatus.textContent = `Unable to load CAPEC attack patterns: ${errorMessage(error)}`;
    this.elements.requestStatus.className = "library-request-status is-error";
    this.rows.clear();
    this.clearDetails();
    this.elements.tableRegion.hidden = true;
    this.elements.emptyState.hidden = true;
    this.elements.warning.hidden = true;
    this.elements.attribution.hidden = true;
    this.elements.retryButton.hidden = false;
    resetPagination(this.elements);
    if (needsFocus) this.elements.retryButton.focus();
  }

  private createRow(row: AttackPatternTableRow): HTMLTableRowElement {
    const tr = this.documentRoot.createElement("tr");
    tr.dataset.attackPatternId = row.id;
    tr.setAttribute("aria-selected", String(row.id === this.selectedId));
    const idCell = this.documentRoot.createElement("td");
    const button = this.documentRoot.createElement("button");
    button.type = "button";
    button.className = "library-title-button";
    button.textContent = row.id;
    button.setAttribute("aria-controls", "attack-pattern-inspector");
    button.addEventListener("click", (event) => {
      void this.selectAttackPattern(row.id);
      // Native button activation by keyboard or assistive technology has no click count.
      if (event.detail === 0) {
        this.elements.inspector.scrollTop = 0;
        this.elements.inspector.focus();
      }
    });
    idCell.append(button);
    tr.append(
      idCell,
      textCell(this.documentRoot, row.name),
      optionalCell(this.documentRoot, row.abstraction),
      textCell(this.documentRoot, row.status),
      optionalCell(this.documentRoot, row.likelihood),
      optionalCell(this.documentRoot, row.severity),
      numericCell(this.documentRoot, row.weaknesses.length, "related CWE weakness", "related CWE weaknesses"),
      numericCell(this.documentRoot, row.attack_techniques.length, "ATT&CK technique", "ATT&CK techniques"),
      numericCell(this.documentRoot, row.steps, "attack step", "attack steps"),
      numericCell(this.documentRoot, row.mitigations, "mitigation", "mitigations"),
    );
    return tr;
  }

  private updateSelectedRow(): void {
    for (const row of this.elements.tableBody.querySelectorAll<HTMLTableRowElement>("tr")) {
      const selected = row.dataset.attackPatternId === this.selectedId;
      row.classList.toggle("is-selected", selected);
      row.setAttribute("aria-selected", String(selected));
      const button = row.querySelector("button");
      if (selected) button?.setAttribute("aria-current", "true");
      else button?.removeAttribute("aria-current");
    }
  }

  private renderRowDetails(row: AttackPatternTableRow): void {
    this.elements.backToRow.hidden = false;
    this.elements.detailTitle.textContent = row.name;
    this.elements.detailId.textContent = row.id;
    this.elements.detailDescription.textContent = row.description;
    this.renderOverview(row);
    this.elements.detailSections.replaceChildren();
    this.elements.detailRetryButton.hidden = true;
  }

  private renderDetails(response: AttackPatternDetailResponse, entry: AttackPatternEntry): void {
    this.elements.detailTitle.textContent = entry.name;
    this.elements.detailId.textContent = entry.id;
    this.elements.detailDescription.textContent = entry.description;
    const row = this.rows.get(entry.id);
    const { detailList, inspector } = this.elements;
    const overviewHadFocus = detailList.contains(this.documentRoot.activeElement);
    if (row) this.renderOverview({
      ...row,
      name: entry.name,
      abstraction: entry.abstraction,
      status: entry.status,
      likelihood: entry.likelihood,
      severity: entry.severity,
      weaknesses: entry.weaknesses,
      attack_techniques: entry.attack_techniques,
      related_attack_patterns: entry.related_attack_patterns.length,
      steps: entry.steps,
      mitigations: entry.mitigations,
      examples: entry.examples,
      url: entry.url,
    });
    if (overviewHadFocus) (detailList.querySelector("a") ?? inspector).focus();
    this.elements.detailStatus.textContent = "";
    this.elements.detailRetryButton.hidden = true;
    const sections: HTMLElement[] = [];
    sections.push(...this.render.fieldSection(entry, "Extended Description", "Extended_Description", { open: true }));
    sections.push(...this.render.alternateTerms(entry));
    sections.push(...this.relatedAttackPatterns(entry));
    sections.push(...this.executionFlow(entry));
    sections.push(...this.render.itemSection(entry, "Prerequisites", "Prerequisites", ["Prerequisite"]));
    sections.push(...this.render.itemSection(entry, "Skills Required", "Skills_Required", ["Skill"]));
    sections.push(...this.render.itemSection(entry, "Resources Required", "Resources_Required", ["Resource"]));
    sections.push(...this.render.itemSection(entry, "Indicators", "Indicators", ["Indicator"]));
    sections.push(...this.render.itemSection(entry, "Consequences", "Consequences", ["Consequence"]));
    sections.push(...this.render.itemSection(entry, "Mitigations", "Mitigations", ["Mitigation"]));
    sections.push(...this.render.itemSection(entry, "Example Instances", "Example_Instances", ["Example"]));
    sections.push(...this.render.identifierList("Related CWE Weaknesses", entry.weaknesses, cweDefinitionUrl));
    sections.push(...this.render.identifierList("ATT&CK Techniques", entry.attack_techniques, attackTechniqueUrl));
    sections.push(...this.render.itemSection(entry, "Taxonomy Mappings", "Taxonomy_Mappings", ["Taxonomy_Mapping"]));
    sections.push(...this.references(response.references ?? []));
    sections.push(...this.render.itemSection(entry, "Notes", "Notes", ["Note"]));
    sections.push(...this.render.assertions(response.objects?.assertions ?? []));
    sections.push(...this.render.additionalFields(entry, CAPEC_FIELDS_SHOWN));
    sections.push(...this.render.contentHistory(entry));
    this.elements.detailSections.replaceChildren(...sections);
  }

  private renderOverview(row: AttackPatternTableRow): void {
    this.elements.detailBadges.replaceChildren(...(row.status ? [this.render.badge(row.status)] : []));
    const attributes: [string, string | null][] = [
      ["Abstraction", row.abstraction],
      ["Likelihood of attack", row.likelihood],
      ["Typical severity", row.severity],
    ];
    const objectId = this.documentRoot.createElement("code");
    objectId.textContent = row.attack_pattern;
    this.elements.detailList.replaceChildren(
      ...attributes.flatMap(([label, value]) => value ? [this.render.detailRow(label, value)] : []),
      this.render.detailRow("Related CWE weaknesses", String(row.weaknesses.length)),
      this.render.detailRow("ATT&CK techniques", String(row.attack_techniques.length)),
      this.render.detailRow("Related attack patterns", String(row.related_attack_patterns)),
      this.render.detailRow("Attack steps", String(row.steps)),
      this.render.detailRow("Mitigations", String(row.mitigations)),
      this.render.detailRow("Examples", String(row.examples)),
      this.render.detailRow("tmodel object", objectId),
      ...safeLinkRows(this.documentRoot, "Official definition", row.url, `View ${row.id} on capec.mitre.org`),
    );
  }

  /** Each Attack_Step in order: its number and phase, what the adversary does, and how. */
  private executionFlow(entry: AttackPatternEntry): HTMLElement[] {
    const steps = fieldItems(entry, "Execution_Flow", "Attack_Step");
    if (!steps.length) return this.render.fieldSection(entry, "Execution Flow", "Execution_Flow");
    const list = this.documentRoot.createElement("ol");
    list.className = "attack-pattern-detail-items attack-pattern-steps";
    list.append(...steps.map((step) => {
      const item = this.documentRoot.createElement("li");
      if (!isFieldRecord(step)) {
        item.append(this.render.fieldValue(step));
        return item;
      }
      const { Step: stepNumber, Phase: phase, Description: description, Technique: technique, ...rest } = step;
      const heading = this.documentRoot.createElement("div");
      heading.className = "attack-pattern-step-heading";
      heading.textContent = [
        stepNumber === undefined ? "" : `Step ${readableCweText(stepNumber)}`,
        phase === undefined ? "" : readableCweText(phase),
      ].filter(Boolean).join(" · ");
      if (heading.textContent) item.append(heading);
      if (description !== undefined && readableCweText(description)) item.append(this.render.fieldValue(description));
      const techniques = (Array.isArray(technique) ? technique : technique === undefined ? [] : [technique])
        .filter((value) => readableCweText(value));
      if (techniques.length) {
        const label = this.documentRoot.createElement("div");
        label.className = "attack-pattern-field-label";
        label.textContent = techniques.length === 1 ? "Technique" : "Techniques";
        const techniqueList = this.documentRoot.createElement("ul");
        techniqueList.className = "attack-pattern-techniques";
        techniqueList.append(...techniques.map((value) => {
          const techniqueItem = this.documentRoot.createElement("li");
          techniqueItem.append(this.render.fieldValue(value));
          return techniqueItem;
        }));
        item.append(label, techniqueList);
      }
      if (Object.keys(rest).length && readableCweText(rest)) item.append(this.render.fieldValue(rest));
      return item;
    }));
    return [this.render.detailSection("Execution Flow", list, { count: steps.length })];
  }

  /** Each Related_Attack_Pattern as CAPEC writes it: its nature, its target and anything else. */
  private relatedAttackPatterns(entry: AttackPatternEntry): HTMLElement[] {
    const related = fieldItems(entry, "Related_Attack_Patterns", "Related_Attack_Pattern");
    if (!related.length) return [];
    const list = this.documentRoot.createElement("ul");
    list.className = "attack-pattern-detail-items attack-pattern-identifier-items";
    list.append(...related.map((relation) => {
      const item = this.documentRoot.createElement("li");
      if (!isFieldRecord(relation)) {
        item.append(this.render.fieldValue(relation));
        return item;
      }
      const nature = this.documentRoot.createElement("span");
      nature.className = "attack-pattern-field-label";
      nature.textContent = readableCweText(relation["@Nature"] ?? null);
      const written = readableCweText(relation["@CAPEC_ID"] ?? null);
      const target = /^[0-9]+$/.test(written) ? `CAPEC-${Number(written)}` : written;
      const link = safeHttpUrl(capecDefinitionUrl(target));
      item.append(
        nature,
        this.documentRoot.createTextNode(" "),
        link
          ? externalLink(this.documentRoot, target, link, "attack-pattern-identifier-link")
          : this.render.identifier(target),
      );
      const rest = Object.entries(relation).filter(([key]) => key !== "@Nature" && key !== "@CAPEC_ID");
      if (rest.length) {
        const extra: Record<string, CweFieldValue> = Object.fromEntries(rest);
        if (readableCweText(extra)) item.append(this.render.fieldValue(extra));
      }
      return item;
    }));
    return [this.render.detailSection("Related Attack Patterns", list, { count: related.length })];
  }

  /** The references the entry cites, each resolved to its title, authors and publication. */
  private references(references: readonly AttackPatternReference[]): HTMLElement[] {
    if (!references.length) return [];
    const list = this.documentRoot.createElement("ul");
    list.className = "attack-pattern-detail-items attack-pattern-references";
    list.append(...references.map((reference) => {
      const item = this.documentRoot.createElement("li");
      const heading = this.documentRoot.createElement("div");
      heading.className = "attack-pattern-reference-heading";
      heading.append(this.render.identifier(reference.id));
      const url = safeHttpUrl(reference.url);
      const title = reference.title ?? (url ? reference.url : null);
      if (!reference.resolved) {
        heading.append(this.text(" Not defined in this CAPEC release"));
      } else if (title) {
        heading.append(
          this.documentRoot.createTextNode(" "),
          url ? externalLink(this.documentRoot, title, url) : this.text(title),
        );
      }
      item.append(heading);
      const details: [string, string | null][] = [
        ["Section", reference.section],
        ["Authors", reference.authors.join(", ") || null],
        ["Edition", reference.edition],
        ["Publication", reference.publication],
        ["Publisher", reference.publisher],
        ["Publication date", publicationDate(reference)],
        // A URL that cannot be a link is still shown, as text.
        ["URL", reference.url && !url ? reference.url : null],
        ["URL date", reference.url_date],
      ];
      for (const [label, value] of details) {
        if (value) item.append(this.labelled(label, value));
      }
      return item;
    }));
    return [this.render.detailSection("References", list, { count: references.length })];
  }

  private labelled(label: string, value: string): HTMLElement {
    const row = this.documentRoot.createElement("div");
    row.className = "attack-pattern-field-attribute";
    const term = this.documentRoot.createElement("span");
    term.className = "attack-pattern-field-label";
    term.textContent = label;
    const description = this.documentRoot.createElement("span");
    description.textContent = value;
    row.append(term, description);
    return row;
  }

  private text(value: string): HTMLElement {
    const span = this.documentRoot.createElement("span");
    span.textContent = value;
    return span;
  }

  private clearDetails(): void {
    this.selectedId = undefined;
    this.detailRequests.cancel();
    this.elements.backToRow.hidden = true;
    this.elements.detailTitle.textContent = "";
    this.elements.detailId.textContent = "";
    this.elements.detailBadges.replaceChildren();
    this.elements.detailDescription.textContent = "";
    this.elements.detailList.replaceChildren();
    this.elements.detailSections.replaceChildren();
    this.elements.detailRetryButton.hidden = true;
    this.elements.detailStatus.textContent = EMPTY_INSPECTOR;
  }

  /** Options in CAPEC's own order (Meta to Detailed, Very High to Very Low), then by name. */
  private populateFacet(
    select: HTMLSelectElement,
    values: Readonly<Record<string, number>>,
    allLabel: string,
    field: AttackPatternFilter,
  ): void {
    const selected = select.value;
    const entries = Object.entries(values);
    if (selected && !entries.some(([value]) => value === selected)) entries.push([selected, 0]);
    const order = ATTACK_PATTERN_ENUMERATION_ORDER[field] ?? [];
    const rank = (value: string) => (order.includes(value) ? order.indexOf(value) : order.length);
    entries.sort(([left], [right]) => rank(left) - rank(right) || left.localeCompare(right));
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
    activeSort: AttackPatternSort | null = this.query.sort,
    order = this.query.order,
  ): void {
    for (const button of this.elements.sortButtons) {
      const active = button.dataset.sort === activeSort;
      button.closest("th")?.setAttribute("aria-sort", active
        ? (order === "asc" ? "ascending" : "descending")
        : "none");
      button.dataset.order = active ? order : "";
    }
    const semantic = activeSort ? ATTACK_PATTERN_ENUMERATION_ORDER[activeSort] : undefined;
    const semanticHelp = semantic
      ? ` Ascending follows CAPEC's order: ${semantic.join(", ")}. Attack patterns without a value come last either way.`
      : "";
    this.elements.sortHelp.textContent = activeSort
      ? `${SORT_LABELS[activeSort]} sorted ${order === "asc" ? "ascending" : "descending"}.${semanticHelp} Select the column again to reverse it.`
      : "Select a column heading to sort.";
  }

  private setLoading(loading: boolean): void {
    this.elements.workspace.setAttribute("aria-busy", String(loading));
    if (loading) {
      this.elements.requestStatus.textContent = "Loading CAPEC attack patterns…";
      this.elements.requestStatus.className = "library-request-status";
      this.elements.retryButton.hidden = true;
      this.elements.emptyState.hidden = true;
    }
  }
}

export function attackPatternViewElements(root: Document = document): AttackPatternViewElements {
  const required = <T extends HTMLElement>(id: string): T => {
    const element = root.getElementById(id);
    if (!element) throw new Error(`Missing required attack-pattern element #${id}`);
    return element as T;
  };
  return {
    workspace: required("attack-pattern-workspace"),
    sourceNotice: required("attack-pattern-source-notice"),
    search: required("attack-pattern-search"),
    abstractionFilter: required("attack-pattern-abstraction-filter"),
    statusFilter: required("attack-pattern-status-filter"),
    likelihoodFilter: required("attack-pattern-likelihood-filter"),
    severityFilter: required("attack-pattern-severity-filter"),
    sortButtons: [...root.querySelectorAll<HTMLButtonElement>("[data-attack-pattern-sort]")],
    clearFilters: required("attack-pattern-clear-filters"),
    requestStatus: required("attack-pattern-request-status"),
    warning: required("attack-pattern-warning"),
    retryButton: required("attack-pattern-retry"),
    tableRegion: required("attack-pattern-table-region"),
    tableBody: required("attack-pattern-table-body"),
    emptyState: required("attack-pattern-empty"),
    previousPage: required("attack-pattern-page-previous"),
    nextPage: required("attack-pattern-page-next"),
    pageStatus: required("attack-pattern-page-status"),
    sortHelp: required("attack-pattern-sort-help"),
    attribution: required("attack-pattern-attribution"),
    attributionSummary: required("attack-pattern-attribution-summary"),
    attributionNotice: required("attack-pattern-attribution-notice"),
    attributionLicense: required("attack-pattern-attribution-license"),
    attributionTerms: required("attack-pattern-attribution-terms"),
    inspector: required("attack-pattern-inspector"),
    backToRow: required("attack-pattern-back-to-row"),
    detailTitle: required("attack-pattern-detail-title"),
    detailId: required("attack-pattern-detail-id"),
    detailBadges: required("attack-pattern-detail-badges"),
    detailDescription: required("attack-pattern-detail-description"),
    detailList: required("attack-pattern-detail-list"),
    detailStatus: required("attack-pattern-detail-status"),
    detailRetryButton: required("attack-pattern-detail-retry"),
    detailSections: required("attack-pattern-detail-sections"),
  };
}

/** The disclosure's label: MITRE's copyright years as the notice gives them, and the terms. */
export function attributionSummary(notice: string): string {
  const years = /©\s*([0-9]{4}(?:-[0-9]{4})?)/u.exec(notice)?.[1];
  return `© ${years ? `${years} ` : ""}The MITRE Corporation · CAPEC Terms of Use`;
}

/** A reference's date from CAPEC's Publication_Year, _Month (--MM) and _Day (---DD). */
export function publicationDate(
  reference: Pick<AttackPatternReference, "year" | "month" | "day">,
): string | null {
  const { year, month, day } = reference;
  const monthNumber = month ? /^--([0-9]{2})$/.exec(month)?.[1] : undefined;
  const dayNumber = day ? /^---([0-9]{2})$/.exec(day)?.[1] : undefined;
  if (year && (!month || monthNumber) && (!day || (dayNumber && monthNumber))) {
    return [year, monthNumber, dayNumber].filter(Boolean).join("-");
  }
  const written = [year, month, day].filter(Boolean).join(" ");
  return written || null;
}

function isFieldRecord(value: CweFieldValue): value is { readonly [key: string]: CweFieldValue } {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function textCell(root: Document, value: string): HTMLTableCellElement {
  const cell = root.createElement("td");
  cell.textContent = value;
  return cell;
}

function optionalCell(root: Document, value: string | null): HTMLTableCellElement {
  if (value) return textCell(root, value);
  const cell = root.createElement("td");
  const missing = root.createElement("span");
  missing.className = "attack-pattern-missing";
  missing.textContent = NOT_STATED;
  cell.append(missing);
  return cell;
}

function numericCell(root: Document, value: number, singular: string, plural: string): HTMLTableCellElement {
  const cell = textCell(root, String(value));
  cell.className = "attack-pattern-count-cell";
  cell.setAttribute("aria-label", `${value} ${value === 1 ? singular : plural}`);
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
