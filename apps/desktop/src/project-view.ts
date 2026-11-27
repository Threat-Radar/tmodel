// #290: the project view of the team's design. A project header names the
// project and has a version selector ("Version 4 (Current)"); a side
// navigation leads to Model Report, Attack Paths, Graph, Risk Score and
// Review & Edit; the Version History table lists every version with its
// description, risk summary and date. An older version can be viewed, always
// read-only. The existing views render the shown version; this module only
// adds the project's own chrome, and only in the desktop app.

import type { ModelReport } from "./model-report";
import {
  riskSummaryText,
  versionLabel,
  versionOptionLabel,
  type ProjectVersion,
  type ProjectVersions,
  type VersionRiskSummary,
} from "./project-workspace";
import type { RevisionViews } from "./review-contract";
import { renderRiskCalculation } from "./risk-calculation";
import { html } from "./safe-html";

export type ProjectPage = "report" | "paths" | "graph" | "risk" | "review";

export const PROJECT_PAGES: readonly { page: ProjectPage; label: string }[] = [
  { page: "report", label: "Model Report" },
  { page: "paths", label: "Attack Paths" },
  { page: "graph", label: "Graph" },
  { page: "risk", label: "Risk Score" },
  { page: "review", label: "Review & Edit" },
];

export interface ProjectChromeActions {
  selectVersion(versionId: string): void;
  navigate(page: ProjectPage): void;
  close(): void;
  retry(): void;
  /** A read-only threat model file: start a project from it. */
  startProject(): void;
}

export interface ProjectChromeState {
  versions: ProjectVersions;
  /** The version the views show, if one has loaded. */
  shown?: ProjectVersion;
  /** The version being opened, while it loads. */
  loading?: string;
  error?: string;
  notice?: string;
  riskSummaries: ReadonlyMap<string, VersionRiskSummary>;
  unsaved: number;
  saving: boolean;
}

export class ProjectChrome {
  readonly bar: HTMLElement;
  readonly navigation: HTMLElement;
  readonly riskPanel: HTMLElement;
  /** Announcements that must survive the project bar being hidden. */
  readonly announcer: HTMLElement;
  private readonly eyebrow: HTMLElement;
  private readonly name: HTMLElement;
  private readonly startButton: HTMLButtonElement;
  private readonly versionSelect: HTMLSelectElement;
  private readonly mode: HTMLElement;
  private readonly unsavedChip: HTMLElement;
  private readonly closeButton: HTMLButtonElement;
  private readonly status: HTMLElement;
  private readonly retryButton: HTMLButtonElement;
  private readonly historySummary: HTMLElement;
  private readonly historyBody: HTMLElement;
  private readonly pageButtons = new Map<ProjectPage, HTMLButtonElement>();
  private readonly reviewMarker: HTMLElement;
  private readonly riskHeading: HTMLElement;
  private readonly riskVersion: HTMLElement;
  private readonly riskContent: HTMLElement;
  private page: ProjectPage = "report";

  constructor(
    private readonly workspace: HTMLElement,
    private readonly appPanels: readonly HTMLElement[],
    actions: ProjectChromeActions,
    documentRoot: Pick<Document, "createElement"> = document,
  ) {
    const make = <K extends keyof HTMLElementTagNameMap>(tag: K, className = ""): HTMLElementTagNameMap[K] => {
      const element = documentRoot.createElement(tag);
      if (className) element.className = className;
      return element;
    };
    this.bar = make("section", "project-bar");
    this.bar.setAttribute("aria-labelledby", "project-bar-name");
    this.bar.hidden = true;
    const main = make("div", "project-bar-main");
    const title = make("div", "project-bar-title");
    this.eyebrow = make("p", "eyebrow");
    this.eyebrow.textContent = "Project";
    this.name = make("h2", "project-bar-name");
    this.name.id = "project-bar-name";
    title.append(this.eyebrow, this.name);
    const version = make("div", "project-bar-version");
    const label = make("label");
    label.htmlFor = "project-version-select";
    label.textContent = "Version";
    this.versionSelect = make("select", "project-version-select");
    this.versionSelect.id = "project-version-select";
    this.versionSelect.addEventListener("change", () => actions.selectVersion(this.versionSelect.value));
    this.mode = make("span", "project-version-mode");
    version.append(label, this.versionSelect, this.mode);
    this.unsavedChip = make("span", "project-unsaved");
    this.unsavedChip.hidden = true;
    this.startButton = make("button", "review-secondary project-start");
    this.startButton.type = "button";
    this.startButton.textContent = "Start a project from this file";
    this.startButton.hidden = true;
    this.startButton.addEventListener("click", () => actions.startProject());
    this.closeButton = make("button", "review-secondary project-close");
    this.closeButton.type = "button";
    this.closeButton.textContent = "Close project";
    this.closeButton.addEventListener("click", () => actions.close());
    main.append(title, version, this.unsavedChip, this.startButton, this.closeButton);
    const statusRow = make("div", "project-bar-status-row");
    this.status = make("p", "project-bar-status");
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.retryButton = make("button", "retry-button");
    this.retryButton.type = "button";
    this.retryButton.textContent = "Retry";
    this.retryButton.hidden = true;
    this.retryButton.addEventListener("click", () => actions.retry());
    statusRow.append(this.status, this.retryButton);
    const history = make("details", "version-history");
    this.historySummary = make("summary");
    this.historySummary.textContent = "Version history";
    this.historyBody = make("div", "version-history-body");
    this.historyBody.addEventListener("click", (event) => {
      const button = (event.target as Element | null)?.closest?.("[data-project-version]");
      const id = button?.getAttribute("data-project-version");
      if (id) actions.selectVersion(id);
    });
    history.append(this.historySummary, this.historyBody);
    this.bar.append(main, statusRow, history);

    this.navigation = make("nav", "project-navigation");
    this.navigation.setAttribute("aria-label", "Project views");
    this.navigation.hidden = true;
    const list = make("ul");
    this.reviewMarker = make("span", "project-nav-unsaved");
    this.reviewMarker.hidden = true;
    for (const { page, label: text } of PROJECT_PAGES) {
      const item = make("li");
      const button = make("button", "project-nav-button");
      button.type = "button";
      button.textContent = text;
      button.addEventListener("click", () => actions.navigate(page));
      if (page === "review") button.append(this.reviewMarker);
      this.pageButtons.set(page, button);
      item.append(button);
      list.append(item);
    }
    this.navigation.append(list);

    this.riskPanel = make("section", "view-panel risk-score-panel");
    this.riskPanel.id = "risk-score-panel";
    this.riskPanel.setAttribute("aria-labelledby", "risk-score-heading");
    this.riskPanel.hidden = true;
    const scroll = make("div", "risk-score-scroll");
    this.riskHeading = make("h2", "risk-score-heading");
    this.riskHeading.id = "risk-score-heading";
    this.riskHeading.tabIndex = -1;
    this.riskHeading.textContent = "Risk Score";
    this.riskVersion = make("p", "risk-score-version");
    this.riskContent = make("div", "model-report risk-score-content");
    scroll.append(this.riskHeading, this.riskVersion, this.riskContent);
    this.riskPanel.append(scroll);

    this.announcer = make("p", "visually-hidden");
    this.announcer.setAttribute("role", "status");
    this.announcer.setAttribute("aria-live", "polite");
  }

  get currentPage(): ProjectPage {
    return this.page;
  }

  enter(): void {
    this.workspace.classList.add("is-project");
    this.bar.hidden = false;
    this.navigation.hidden = false;
  }

  exit(): void {
    this.workspace.classList.remove("is-project");
    this.bar.hidden = true;
    this.navigation.hidden = true;
    this.riskPanel.hidden = true;
    this.page = "report";
  }

  /** Marks the side navigation and shows or hides the Risk Score panel. */
  setPage(page: ProjectPage): void {
    this.page = page;
    for (const [candidate, button] of this.pageButtons) {
      if (candidate === page) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    }
    this.riskPanel.hidden = page !== "risk";
    if (page === "risk") for (const panel of this.appPanels) panel.hidden = true;
  }

  focusRisk(): void {
    this.riskHeading.focus();
  }

  announce(text: string): void {
    this.announcer.textContent = text;
  }

  render(state: ProjectChromeState): void {
    const { versions, shown } = state;
    const file = versions.project.kind === "file";
    this.eyebrow.textContent = file ? "Threat model file" : "Project";
    this.name.textContent = versions.project.name;
    this.startButton.hidden = !file;
    this.startButton.disabled = state.saving;
    this.closeButton.textContent = file ? "Close file" : "Close project";
    const newestFirst = [...versions.versions].reverse();
    this.versionSelect.innerHTML = html`${newestFirst.map((version) => html`<option value="${version.id}"${version.id === (state.loading ?? shown?.id) ? html` selected` : ""}>${versionOptionLabel(version)}</option>`)}`.value;
    this.versionSelect.value = state.loading ?? shown?.id ?? "";
    this.versionSelect.disabled = state.saving || state.loading !== undefined;
    this.mode.textContent = !shown ? "" : file || !versions.project.editable ? "Read-only file"
      : shown.current ? "Current version" : "Older version: read-only";
    this.mode.className = `project-version-mode ${shown?.current && !file ? "is-current" : "is-older"}`;
    this.unsavedChip.hidden = state.unsaved === 0;
    this.unsavedChip.textContent = `${state.unsaved} unsaved ${state.unsaved === 1 ? "change" : "changes"}`;
    this.reviewMarker.hidden = state.unsaved === 0;
    this.reviewMarker.textContent = state.unsaved ? ` (${state.unsaved} unsaved)` : "";
    this.closeButton.disabled = state.saving;
    const loadingName = state.loading ? versionLabelOf(versions, state.loading) : "";
    this.status.textContent = state.error ?? (state.loading ? `Loading ${loadingName}…` : state.notice ?? "");
    this.status.className = `project-bar-status${state.error ? " is-error" : ""}`;
    this.retryButton.hidden = !state.error;
    this.bar.setAttribute("aria-busy", String(state.loading !== undefined));
    this.historySummary.textContent = `Version history · ${versions.versions.length} ${versions.versions.length === 1 ? "version" : "versions"}${shown ? ` · viewing ${versionLabel(shown)}` : ""}`;
    this.historyBody.innerHTML = renderVersionHistory(versions, shown?.id, state.riskSummaries);
  }

  renderRisk(views: RevisionViews, report: ModelReport, version: ProjectVersion, summary: VersionRiskSummary): void {
    this.riskVersion.textContent = `${versionLabel(version)}${version.current ? " (Current)" : ", an older version"}: ${riskSummaryText(summary)}.`;
    // #63's renderer: the engine's calculation for exactly this version, never recalculated here.
    this.riskContent.innerHTML = renderRiskCalculation(views.risk, report);
  }
}

function versionLabelOf(versions: ProjectVersions, id: string): string {
  const version = versions.versions.find((candidate) => candidate.id === id);
  return version ? versionLabel(version) : `version ${id}`;
}

export function formatVersionDate(value: string | null): { text: string; datetime: string | null } {
  if (!value) return { text: "Not recorded", datetime: null };
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return { text: value, datetime: null };
  return { text: parsed.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }), datetime: value };
}

/** Version, Description, Risk summary and Date, newest first; the current and viewed versions are marked. */
export function renderVersionHistory(
  versions: ProjectVersions,
  viewing: string | undefined,
  riskSummaries: ReadonlyMap<string, VersionRiskSummary>,
): string {
  const rows = [...versions.versions].reverse().map((version) => {
    const summary = version.riskSummary ?? riskSummaries.get(version.id) ?? null;
    const date = formatVersionDate(version.date);
    const shown = version.id === viewing;
    return html`<tr${shown ? html` class="is-viewing"` : ""}>
<th scope="row"><button type="button" class="version-button" data-project-version="${version.id}"${shown ? html` aria-current="true"` : ""}>${versionLabel(version)}</button>${version.current ? html` <span class="version-chip is-current">Current</span>` : ""}${shown ? html` <span class="version-chip">Viewing</span>` : ""}</th>
<td>${version.description ?? "No description recorded"}</td>
<td>${riskSummaryText(summary)}</td>
<td>${date.datetime ? html`<time datetime="${date.datetime}">${date.text}</time>` : date.text}</td>
</tr>`;
  });
  return html`<div class="report-table-scroll"><table class="version-table">
<caption>Versions of ${versions.project.name}. Older versions open read-only; a save always adds a new version.</caption>
<thead><tr><th scope="col">Version</th><th scope="col">Description</th><th scope="col">Risk summary</th><th scope="col">Date</th></tr></thead>
<tbody>${rows}</tbody></table></div>`.value;
}
