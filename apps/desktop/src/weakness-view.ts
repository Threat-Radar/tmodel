import {
  bindClearFilters, EMPTY_INSPECTOR, LIBRARY_PAGE_SIZE, renderPagination, resetPagination,
  type LibraryPagination,
} from "./library-presentation";
import type { EngineState } from "./engine";
import { fieldItems, fieldValues, readableCweText, richTextToCode, safeHttpUrl } from "./weakness-fields";
import {
  DEFAULT_WEAKNESS_QUERY,
  isWeaknessSort,
  type CweFieldValue,
  type WeaknessAssertion,
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

interface DisclosureOptions {
  count?: number;
  open?: boolean;
}

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

  constructor(
    private readonly provider: WeaknessDataProvider,
    private readonly elements: WeaknessViewElements,
    private readonly documentRoot: Document = document,
  ) {
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
    sections.push(...this.fieldSection(entry, "Extended Description", "Extended_Description", { open: true }));
    sections.push(...this.alternateTerms(entry));
    sections.push(...this.backgroundAndPlatforms(entry));
    sections.push(...this.itemSection(entry, "Modes of Introduction", "Modes_Of_Introduction", ["Introduction"]));
    sections.push(...this.itemSection(entry, "Common Consequences", "Common_Consequences", ["Consequence"]));
    sections.push(...this.itemSection(entry, "Detection Methods", "Detection_Methods", ["Detection_Method"]));
    sections.push(...this.itemSection(entry, "Potential Mitigations", "Potential_Mitigations", ["Mitigation"]));
    sections.push(...this.itemSection(entry, "Demonstrative Examples", "Demonstrative_Examples", ["Demonstrative_Example"]));
    sections.push(...this.observedExamples(entry));
    sections.push(...this.stringListSection("Related CAPEC Attack Patterns", entry.attack_patterns, true));
    sections.push(...this.itemSection(entry, "Taxonomy Mappings", "Taxonomy_Mappings", ["Taxonomy_Mapping"]));
    sections.push(...this.assertions(response.objects?.assertions ?? []));
    sections.push(...this.additionalFields(entry));
    sections.push(...this.contentHistory(entry));
    this.elements.detailSections.replaceChildren(...sections);
  }

  private renderOverview(row: WeaknessTableRow): void {
    this.elements.detailBadges.replaceChildren(...(row.status ? [this.badge(row.status)] : []));
    const attributes: [string, string | null][] = [
      ["Abstraction", row.abstraction], ["Structure", row.structure], ["Usage", row.usage], ["Likelihood", row.likelihood],
    ];
    this.elements.detailList.replaceChildren(
      ...attributes.flatMap(([label, value]) => value ? [this.detailRow(label, value)] : []),
      this.detailRow("CAPEC mappings", String(row.attack_patterns)),
      this.detailRow("Observed examples", String(row.observed_examples)),
      this.detailRow("Mitigations", String(row.mitigations)),
      ...safeLinkRows(this.documentRoot, "Official definition", row.url, `View ${row.id} on cwe.mitre.org`),
    );
  }

  private fieldSection(
    entry: WeaknessEntry,
    title: string,
    field: string,
    options: DisclosureOptions = {},
  ): HTMLElement[] {
    return this.valuesSection(title, fieldValues(entry, field), options);
  }

  private itemSection(
    entry: WeaknessEntry,
    title: string,
    container: string,
    itemNames: readonly string[],
    options: DisclosureOptions = {},
  ): HTMLElement[] {
    const items = itemNames.flatMap((item) => fieldItems(entry, container, item));
    return this.valuesSection(title, items.length ? items : fieldValues(entry, container), {
      count: items.length || undefined,
      ...options,
    });
  }

  private alternateTerms(entry: WeaknessEntry): HTMLElement[] {
    const terms = fieldItems(entry, "Alternate_Terms", "Alternate_Term");
    return this.valuesSection("Alternate Terms", terms.length ? terms : entry.alternate_terms, {
      count: terms.length || entry.alternate_terms.length,
    });
  }

  private backgroundAndPlatforms(entry: WeaknessEntry): HTMLElement[] {
    const background = fieldItems(entry, "Background_Details", "Background_Detail");
    const backgroundValues = background.length ? background : fieldValues(entry, "Background_Details");
    const platforms = ["Language", "Operating_System", "Architecture", "Technology", "Class"]
      .flatMap((item) => fieldItems(entry, "Applicable_Platforms", item));
    const platformValues = platforms.length ? platforms : fieldValues(entry, "Applicable_Platforms");
    const groups = [
      this.valueGroup("Background", backgroundValues),
      this.valueGroup("Applicable Platforms", platformValues),
    ].filter((group): group is HTMLElement => group !== undefined);
    if (!groups.length) return [];
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = "weakness-detail-groups";
    wrapper.append(...groups);
    return [this.detailSection("Background and Applicable Platforms", wrapper, {
      count: backgroundValues.length + platformValues.length,
    })];
  }

  private valuesSection(
    title: string,
    values: readonly CweFieldValue[],
    options: DisclosureOptions = {},
  ): HTMLElement[] {
    const items = values.filter((value) => readableCweText(value));
    if (!items.length) return [];
    const list = this.valueList(items);
    return [this.detailSection(title, list, { count: options.count ?? items.length, ...options })];
  }

  private valueGroup(title: string, values: readonly CweFieldValue[]): HTMLElement | undefined {
    const items = values.filter((value) => readableCweText(value));
    if (!items.length) return undefined;
    const group = this.documentRoot.createElement("section");
    group.className = "weakness-detail-group";
    const heading = this.documentRoot.createElement("h4");
    heading.textContent = `${title} (${items.length})`;
    group.append(heading, this.valueList(items));
    return group;
  }

  private valueList(values: readonly CweFieldValue[]): HTMLUListElement {
    const list = this.documentRoot.createElement("ul");
    list.className = "weakness-detail-items";
    list.append(...values.map((value) => {
      const item = this.documentRoot.createElement("li");
      item.append(this.fieldValue(value));
      return item;
    }));
    return list;
  }

  private fieldValue(value: CweFieldValue, name?: string): HTMLElement {
    if (name === "Example_Code") return this.codeValue(value);
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = "weakness-field-value";
    if (value === null) return wrapper;
    if (typeof value !== "object") {
      wrapper.textContent = String(value);
      return wrapper;
    }
    if (Array.isArray(value)) {
      if (value.every((item) => item === null || typeof item !== "object")) {
        wrapper.textContent = value.map(readableCweText).filter(Boolean).join(" · ");
      } else {
        wrapper.className = "weakness-field-value weakness-field-collection";
        wrapper.append(...value
          .filter((item) => readableCweText(item))
          .map((item) => this.fieldValue(item)));
      }
      return wrapper;
    }
    for (const [key, child] of Object.entries(value)) {
      if (key === "#xhtml" || key === "#text") {
        const text = this.documentRoot.createElement("p");
        text.className = "weakness-field-text";
        text.textContent = key === "#xhtml" && typeof child === "string"
          ? readableCweText({ "#xhtml": child })
          : readableCweText(child);
        if (text.textContent) wrapper.append(text);
      } else if (key === "#items" && Array.isArray(child)) {
        for (const ordered of child) wrapper.append(this.fieldValue(ordered));
      } else {
        const row = this.documentRoot.createElement("div");
        row.className = key.startsWith("@") ? "weakness-field-attribute" : "weakness-field-row";
        const label = this.documentRoot.createElement("span");
        label.className = "weakness-field-label";
        label.textContent = displayValue(key.replace(/^@/, ""));
        row.append(label, this.fieldValue(child, key));
        wrapper.append(row);
      }
    }
    return wrapper;
  }

  private codeValue(value: CweFieldValue): HTMLElement {
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = "weakness-code-value";
    const values = Array.isArray(value) ? value : [value];
    for (const codeValue of values) {
      if (typeof codeValue === "object" && codeValue !== null && !Array.isArray(codeValue)) {
        const attributes = (Object.entries(codeValue) as Array<[string, CweFieldValue]>)
          .filter(([key]) => key.startsWith("@"));
        if (attributes.length) {
          const meta = this.documentRoot.createElement("div");
          meta.className = "weakness-code-meta";
          meta.textContent = attributes
            .map(([key, item]) => `${displayValue(key.slice(1))}: ${readableCweText(item)}`)
            .join(" · ");
          wrapper.append(meta);
        }
      }
      const markup = typeof codeValue === "object" && codeValue !== null && !Array.isArray(codeValue)
        ? codeValue["#xhtml"]
        : undefined;
      const code = this.documentRoot.createElement("code");
      code.textContent = typeof markup === "string" ? richTextToCode(markup) : readableCweText(codeValue);
      const pre = this.documentRoot.createElement("pre");
      pre.append(code);
      wrapper.append(pre);
    }
    return wrapper;
  }

  private stringListSection(title: string, items: readonly string[], capec = false): HTMLElement[] {
    if (!items.length) return [];
    const list = this.documentRoot.createElement("ul");
    list.className = "weakness-detail-items weakness-identifier-items";
    list.append(...items.map((text) => {
      const item = this.documentRoot.createElement("li");
      if (capec) {
        const link = safeHttpUrl(`https://capec.mitre.org/data/definitions/${text.replace(/^CAPEC-/i, "")}.html`);
        if (link) item.append(externalLink(this.documentRoot, text, link, "weakness-identifier-link"));
        else item.textContent = text;
      } else item.textContent = text;
      return item;
    }));
    return [this.detailSection(title, list, { count: items.length })];
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
        : identifierText(this.documentRoot, example.reference);
      item.append(reference, this.documentRoot.createTextNode(` — ${example.description}`));
      return item;
    }));
    return [this.detailSection("Observed Examples and CVE References", list, {
      count: entry.observed_examples.length,
    })];
  }

  private assertions(assertions: readonly WeaknessAssertion[]): HTMLElement[] {
    if (!assertions.length) return [];
    const list = this.documentRoot.createElement("ul");
    list.className = "weakness-assertions";
    list.append(...assertions.map((assertion) => {
      const item = this.documentRoot.createElement("li");
      const heading = this.documentRoot.createElement("div");
      const status = assertion.assertion_status.toLocaleLowerCase("und") === "proposed"
        ? "Proposed — not human-reviewed"
        : displayValue(assertion.assertion_status);
      heading.textContent = `${assertion.name} · ${status}`;
      const relation = this.documentRoot.createElement("code");
      relation.textContent = `${assertion.subject} ${assertion.predicate} ${assertion.object}`;
      const provenance = this.documentRoot.createElement("dl");
      provenance.className = "weakness-assertion-provenance";
      provenance.append(
        this.assertionProvenanceRow("Assertion ID", assertion.id, true),
        this.assertionProvenanceRow("Asserted by", assertion.asserted_by, true),
        this.assertionProvenanceRow("Generated by", assertion.generated_by),
      );
      item.append(heading, relation, provenance);
      if (assertion.description) {
        const description = this.documentRoot.createElement("p");
        description.textContent = assertion.description;
        item.append(description);
      }
      const evidence = assertion.evidence?.flatMap((url) => {
        const safe = safeHttpUrl(url);
        return safe ? [externalLink(this.documentRoot, "Evidence", safe)] : [];
      }) ?? [];
      if (evidence.length) item.append(...evidence);
      return item;
    }));
    const note = this.documentRoot.createElement("p");
    note.className = "weakness-proposal-note";
    note.textContent = "Imported relationships are proposals until a human accepts them through the review workflow.";
    const wrapper = this.documentRoot.createElement("div");
    wrapper.append(note, list);
    return [this.detailSection("Proposed Relationships", wrapper, { count: assertions.length })];
  }

  private assertionProvenanceRow(label: string, value: string, stableId = false): HTMLElement {
    const row = this.documentRoot.createElement("div");
    const term = this.documentRoot.createElement("dt");
    term.textContent = label;
    const description = this.documentRoot.createElement("dd");
    if (stableId) {
      const code = this.documentRoot.createElement("code");
      code.textContent = value;
      description.append(code);
    } else description.textContent = value;
    row.append(term, description);
    return row;
  }

  private additionalFields(entry: WeaknessEntry): HTMLElement[] {
    const alreadyShown = new Set([
      "@ID", "@Name", "@Abstraction", "@Structure", "@Status", "Description",
      "Extended_Description", "Background_Details", "Applicable_Platforms",
      "Alternate_Terms",
      "Modes_Of_Introduction", "Common_Consequences", "Detection_Methods",
      "Potential_Mitigations", "Demonstrative_Examples", "Observed_Examples",
      "Related_Attack_Patterns", "Taxonomy_Mappings", "Likelihood_Of_Exploit",
      "Content_History",
    ]);
    const groups = Object.entries(entry.fields).flatMap(([name, value]) => {
      if (alreadyShown.has(name)) return [];
      if (!readableCweText(value)) return [];
      const group = this.valueGroup(
        displayValue(name.replace(/^@/, "")),
        fieldValues(entry, name),
      );
      return group ? [group] : [];
    });
    if (!groups.length) return [];
    const wrapper = this.documentRoot.createElement("div");
    wrapper.className = "weakness-detail-groups";
    wrapper.append(...groups);
    return [this.detailSection("Additional Catalog Fields", wrapper, { count: groups.length })];
  }

  private contentHistory(entry: WeaknessEntry): HTMLElement[] {
    const values = fieldValues(entry, "Content_History");
    if (!values.length) return [];
    const eventCount = ["Submission", "Modification", "Contribution", "Previous_Entry_Name"]
      .reduce((count, item) => count + fieldItems(entry, "Content_History", item).length, 0);
    return this.valuesSection("Content History", values, { count: eventCount || undefined });
  }

  private detailSection(
    title: string,
    content: HTMLElement,
    options: DisclosureOptions = {},
  ): HTMLElement {
    const details = this.documentRoot.createElement("details");
    details.className = "weakness-detail-section";
    details.open = options.open ?? false;
    const summary = this.documentRoot.createElement("summary");
    const label = this.documentRoot.createElement("span");
    label.textContent = title;
    summary.append(label);
    if (options.count !== undefined) {
      const count = this.documentRoot.createElement("span");
      count.className = "weakness-section-count";
      count.textContent = String(options.count);
      count.setAttribute("aria-label", `${options.count} ${options.count === 1 ? "item" : "items"}`);
      summary.append(count);
    }
    const body = this.documentRoot.createElement("div");
    body.className = "weakness-detail-section-body";
    body.append(content);
    details.append(summary, body);
    return details;
  }

  private detailRow(label: string, value: string | HTMLElement): HTMLElement {
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

  private badge(value: string): HTMLElement {
    const badge = this.documentRoot.createElement("span");
    badge.className = "status-chip";
    badge.textContent = value;
    return badge;
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

function safeLinkRows(
  root: Document,
  label: string,
  value: string | null | undefined,
  linkLabel: string,
): HTMLElement[] {
  const url = safeHttpUrl(value);
  if (!url) return [];
  const wrapper = root.createElement("div");
  wrapper.className = "detail-row";
  const term = root.createElement("dt");
  term.textContent = label;
  const description = root.createElement("dd");
  description.append(externalLink(root, linkLabel, url));
  wrapper.append(term, description);
  return [wrapper];
}

function externalLink(root: Document, label: string, url: string, className = ""): HTMLAnchorElement {
  const link = root.createElement("a");
  link.textContent = label;
  link.className = className;
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  return link;
}

function identifierText(root: Document, value: string): HTMLElement {
  const identifier = root.createElement("span");
  identifier.className = "weakness-identifier-link";
  identifier.textContent = value;
  return identifier;
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

function displayValue(value: string): string {
  const words = value.replace(/_/gu, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}
