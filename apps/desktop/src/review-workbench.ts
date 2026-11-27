// #290: Review & Edit, inside the attack-path view's side column. For the path
// the attack-path view shows, it lists the engine's computed routes (#63 route
// ids, never built from labels), reads the route's review context at the
// version being viewed, and collects decisions, rationale, annotations and
// ratings into one draft per route. "Save New Version" sends that draft as one
// saveModelChanges request against the version the context was read from.
//
// Input is never lost: a draft is cleared only after the engine confirms the
// save, and a conflict, refusal or failure keeps it. Saves work only on the
// current version and only for actions the engine's permitted_actions allow;
// every other case renders read-only.

import { LatestRequestGuard } from "./request-guard";
import type { ModelReport } from "./model-report";
import { versionLabel, type ProjectVersion, type ProjectVersions } from "./project-workspace";
import type { ReviewApiClient } from "./review-client";
import { isAbort } from "./review-client";
import {
  FEASIBILITY_VALUES,
  IMPACT_CATEGORIES,
  REVIEW_MATRIX,
  ReviewApiError,
  SEVERITY_VALUES,
  type FeasibilityValue,
  type ImpactCategory,
  type ReviewContext,
  type RevisionViews,
  type SeverityValue,
} from "./review-contract";
import {
  clearSaved,
  draftChangeCount,
  planSave,
  routeKey,
  RouteDraft,
  setFeasibility,
  setImpact,
  setReviewField,
  snapshot,
  type DraftProblem,
} from "./review-drafts";
import {
  changeLines,
  renderReviewContext,
  revisionName,
  ReviewNames,
  riskValues,
  routeRisk,
} from "./review-render";
import { html } from "./safe-html";

export type ReviewMode = "view" | "review";

/** The project version the app shows, with the views it was built from. */
export interface ReviewTarget {
  projectId: string;
  projectName: string;
  /** A project, or a threat model file opened read-only. */
  kind: "project" | "file";
  versions: ProjectVersions;
  version: ProjectVersion;
  /** Only a project's current version can be reviewed and saved. */
  editable: boolean;
  views: RevisionViews;
  report: ModelReport;
}

export interface ReviewWorkbenchHost {
  target(): ReviewTarget | undefined;
  /** The read-only example shown when no project is open. */
  example(): { title: string } | undefined;
  projectsAvailable(): boolean;
  /** A save was confirmed: show its views, from its revision, everywhere. */
  saved(views: RevisionViews): Promise<void>;
  /** Shows another version (after a conflict, or to return to the current one). */
  loadVersion(versionId: string): Promise<boolean>;
  /** Re-reads the version list, for when a save's outcome is unknown. */
  refreshVersions(): Promise<void>;
  startProjectFromExample(): void;
  showReview(): void;
  unsavedChanged(count: number): void;
}

interface RouteChoice {
  id: string;
  label: string;
  threatId: string;
}

type ContextState =
  | { status: "idle" }
  | { status: "loading"; key: string }
  | { status: "ready"; key: string; context: ReviewContext }
  | { status: "failed"; key: string; error: unknown };

interface SaveOutcome {
  revision: string;
  text: string;
}

export class ReviewWorkbench {
  readonly element: HTMLElement;
  private readonly heading: HTMLElement;
  private readonly targetLine: HTMLElement;
  private readonly routeRow: HTMLElement;
  private readonly routeSelect: HTMLSelectElement;
  private readonly body: HTMLElement;
  private readonly changes: HTMLElement;
  private readonly actions: HTMLElement;
  private readonly saveButton: HTMLButtonElement;
  private readonly discardButton: HTMLButtonElement;
  private readonly status: HTMLElement;
  private readonly alert: HTMLElement;

  private mode: ReviewMode = "view";
  private pathId?: string;
  private routes: RouteChoice[] = [];
  private routeId?: string;
  private readonly routeChoices = new Map<string, string>();
  private context: ContextState = { status: "idle" };
  private readonly contextRequests = new LatestRequestGuard();
  /** Unsaved input, per project and route, kept until saved or discarded. */
  private readonly drafts = new Map<string, Map<string, RouteDraft>>();
  private saving = false;
  private blocked?: string;
  private problems: DraftProblem[] = [];
  private confirmingDiscard = false;
  private outcome?: SaveOutcome;
  private names = new ReviewNames(undefined, undefined);
  private targetKey = "";

  constructor(
    private readonly client: ReviewApiClient,
    private readonly host: ReviewWorkbenchHost,
    documentRoot: Pick<Document, "createElement"> = document,
  ) {
    const make = <K extends keyof HTMLElementTagNameMap>(tag: K, className: string): HTMLElementTagNameMap[K] => {
      const element = documentRoot.createElement(tag);
      element.className = className;
      return element;
    };
    this.element = make("section", "review-panel");
    this.element.setAttribute("aria-labelledby", "review-panel-heading");
    this.element.hidden = true;
    const header = make("div", "review-panel-header");
    this.heading = make("h2", "review-panel-heading");
    this.heading.id = "review-panel-heading";
    this.heading.tabIndex = -1;
    this.heading.textContent = "Review & Edit";
    this.targetLine = make("p", "review-target");
    header.append(this.heading, this.targetLine);
    this.routeRow = make("div", "review-route");
    const routeLabel = make("label", "review-label");
    routeLabel.htmlFor = "review-route-select";
    routeLabel.textContent = "Route";
    this.routeSelect = make("select", "review-route-select");
    this.routeSelect.id = "review-route-select";
    this.routeRow.append(routeLabel, this.routeSelect);
    this.body = make("div", "review-body");
    this.body.setAttribute("aria-busy", "false");
    this.changes = make("div", "review-changes");
    this.actions = make("div", "review-actions");
    this.saveButton = make("button", "primary-button review-save");
    this.saveButton.type = "button";
    this.saveButton.textContent = "Save New Version";
    this.saveButton.setAttribute("data-review-action", "save");
    this.discardButton = make("button", "review-secondary");
    this.discardButton.type = "button";
    this.discardButton.textContent = "Discard changes";
    this.discardButton.setAttribute("data-review-action", "discard");
    this.actions.append(this.saveButton, this.discardButton);
    this.status = make("p", "review-status");
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.alert = make("div", "review-alert");
    this.alert.setAttribute("role", "alert");
    this.alert.tabIndex = -1;
    this.element.append(header, this.routeRow, this.body, this.changes, this.actions, this.status, this.alert);

    this.element.addEventListener("change", (event) => this.handleChange(event.target as Element | null));
    this.element.addEventListener("input", (event) => this.handleInput(event.target as Element | null));
    this.element.addEventListener("click", (event) => this.handleClick(event.target as Element | null));
  }

  /** "review" for the Review & Edit view, "view" for Attack Paths. */
  setMode(mode: ReviewMode): void {
    this.mode = mode;
    this.render();
    this.ensureContext();
  }

  focus(): void {
    // Under 1500px the form sits below the diagram: scroll no further than the heading
    // needs, so the diagram stays in view above it.
    this.heading.focus({ preventScroll: true });
    this.heading.scrollIntoView?.({ block: "nearest" });
  }

  /** The attack-path view shows another path (or none). */
  pathChanged(pathId: string | undefined): void {
    if (pathId === this.pathId) return;
    this.pathId = pathId;
    this.problems = [];
    this.confirmingDiscard = false;
    this.render();
    this.ensureContext();
  }

  /** Another project, version or example is shown. */
  targetChanged(): void {
    const target = this.host.target();
    const key = target ? `${target.projectId}\u0000${target.version.id}` : "";
    this.names = new ReviewNames(target?.report, target?.views.graph);
    if (key !== this.targetKey) {
      this.targetKey = key;
      this.contextRequests.cancel();
      this.context = { status: "idle" };
      this.problems = [];
      this.blocked = undefined;
      this.confirmingDiscard = false;
    }
    this.render();
    this.ensureContext();
  }

  /** All unsaved changes in the open project. */
  get unsavedCount(): number {
    const target = this.host.target();
    if (!target) return 0;
    let count = 0;
    for (const draft of this.drafts.get(target.projectId)?.values() ?? []) count += draftChangeCount(draft);
    return count;
  }

  /** Unsaved changes in every project opened since the app started, kept in memory only. */
  get unsavedEverywhere(): number {
    let count = 0;
    for (const project of this.drafts.values()) for (const draft of project.values()) count += draftChangeCount(draft);
    return count;
  }

  get isSaving(): boolean {
    return this.saving;
  }

  handleChange(target: Element | null): void {
    if (!target) return;
    if (target === this.routeSelect) {
      this.selectRoute(this.routeSelect.value);
      return;
    }
    const field = target.getAttribute("data-review-field");
    const id = target.getAttribute("data-target");
    if (!field || !id) return;
    const value = (target as HTMLInputElement).value;
    if (field === "verdict" && !(target as HTMLInputElement).checked) return;
    this.edit(field, id, value, target.getAttribute("data-category"));
  }

  handleInput(target: Element | null): void {
    const field = target?.getAttribute("data-review-field");
    const id = target?.getAttribute("data-target");
    if (!target || !id || (field !== "rationale" && field !== "annotation")) return;
    this.edit(field, id, (target as HTMLTextAreaElement).value, null);
  }

  handleClick(target: Element | null): void {
    const button = target?.closest?.("[data-review-action]");
    const action = button?.getAttribute("data-review-action");
    if (!button || !action) return;
    if (action === "save") void this.save();
    else if (action === "discard") this.discard();
    else if (action === "load-version") void this.loadVersion(button.getAttribute("data-version"));
    else if (action === "refresh-versions") void this.host.refreshVersions();
    else if (action === "retry") this.reload();
    else if (action === "review") this.host.showReview();
    else if (action === "start-project") this.host.startProjectFromExample();
    else if (action === "focus-field") {
      const field = button.getAttribute("data-field");
      const element = field ? (this.body as HTMLElement & ParentNode).querySelector?.<HTMLElement>(`#${field}`) : null;
      element?.focus();
    }
  }

  async save(): Promise<void> {
    if (this.saving) return;
    const target = this.host.target();
    const state = this.context;
    if (!target || !target.editable || state.status !== "ready" || state.context.revision !== target.version.id) {
      this.announce("Saving works only on the current version, once its review has loaded.");
      return;
    }
    if (this.blocked) {
      this.announce(this.blocked);
      return;
    }
    const draft = this.currentDraft(false);
    if (!draft || draft.empty) {
      this.announce("There are no unsaved changes to save.");
      return;
    }
    const context = state.context;
    const plan = planSave(context, draft, REVIEW_MATRIX);
    if (plan.problems.length > 0) {
      this.problems = plan.problems;
      this.renderBody();
      this.showProblems(plan.problems);
      return;
    }
    if (plan.changes === 0) {
      this.announce("Nothing here can be saved: the unsaved changes are for items this version no longer has.");
      return;
    }
    const saved = snapshot(draft);
    this.saving = true;
    this.problems = [];
    this.outcome = undefined;
    this.confirmingDiscard = false;
    this.clearAlert();
    this.announce(`Saving a new version from ${versionLabel(target.version)}…`);
    this.renderBody();
    this.renderActions();
    // The project bar disables the version selector and Close while a save runs.
    this.host.unsavedChanged(this.unsavedCount);
    let views: RevisionViews;
    try {
      views = await this.client.saveModelChanges(plan.request);
    } catch (error) {
      this.saving = false;
      this.saveFailed(error, target);
      this.renderBody();
      this.renderActions();
      this.host.unsavedChanged(this.unsavedCount);
      return;
    }
    clearSaved(draft, saved);
    if (draft.empty) this.drafts.get(target.projectId)?.delete(routeKey(draft.threatId, draft.routeId));
    else draft.baseRevision = views.revision;
    const before = routeRisk(context.calculated_risk, context.threat.id, context.route.id);
    const after = routeRisk(views.risk, context.threat.id, context.route.id);
    const risk = after.map((entry, index) => riskValues(entry.route?.derived_risk, before[index]?.route?.derived_risk)).join("; ");
    this.saving = false;
    this.host.unsavedChanged(this.unsavedCount);
    try {
      await this.host.saved(views);
    } catch (error) {
      this.showAlert(html`<p>The new version ${views.revision} was saved, but the app could not show it: ${message(error)}. Reload the version list to see it.</p>
<button type="button" class="review-secondary" data-review-action="refresh-versions">Reload the version list</button>`);
      this.render();
      return;
    }
    const shown = this.host.target();
    const name = shown && shown.version.id === views.revision ? versionLabel(shown.version) : `version ${views.revision}`;
    this.outcome = {
      revision: views.revision,
      text: `Saved as ${name}. The report, attack paths, graph and risk now show ${name}. Recalculated risk for this route: ${risk || "not calculated"}.`,
    };
    this.render();
    this.announce(this.outcome.text);
  }

  private saveFailed(error: unknown, target: ReviewTarget): void {
    const kept = "Your changes are kept.";
    if (!(error instanceof ReviewApiError)) {
      this.showAlert(html`<p>The save failed unexpectedly: ${message(error)}. Nothing was saved. ${kept} Try again.</p>`);
      return;
    }
    switch (error.kind) {
      case "conflict": {
        const newer = error.details.currentRevision;
        const name = newer ? revisionName(target.versions, newer) : "a newer version";
        this.showAlert(html`<p>${name} was saved after ${versionLabel(target.version)}, the version you are editing, so nothing was saved and no version was overwritten. ${kept} Load the newer version, check your changes against it, then save again.</p>
${newer ? html`<button type="button" class="review-secondary" data-review-action="load-version" data-version="${newer}">Load ${name}</button>`
    : html`<button type="button" class="review-secondary" data-review-action="refresh-versions">Reload the version list</button>`}`);
        return;
      }
      case "validation": {
        const fields = error.details.fields ?? [];
        this.showAlert(html`<p>The engine refused the save: ${error.message} ${kept}</p>${fields.length ? html`<ul>${fields.map((item) => html`<li>${fieldName(item.field)}: ${item.message}</li>`)}</ul>` : ""}`);
        this.alert.focus();
        return;
      }
      case "permission":
        this.blocked = `This session cannot make this change: ${error.message}`;
        this.showAlert(html`<p>${this.blocked} Nothing was saved. ${kept} The app does not retry as another reviewer.</p>
<button type="button" class="review-secondary" data-review-action="retry">Reload the review and its permissions</button>`);
        return;
      case "not_found":
        this.showAlert(html`<p>This project version is no longer available: ${error.message} ${kept}</p>
<button type="button" class="review-secondary" data-review-action="refresh-versions">Reload the version list</button>`);
        return;
      case "unavailable":
        this.blocked = `Saving is not available: ${error.message}`;
        this.showAlert(html`<p>${this.blocked} ${kept}</p>
<button type="button" class="review-secondary" data-review-action="retry">Reload the review</button>`);
        return;
      case "malformed":
        this.showAlert(html`<p>The engine answered, but the app could not read its answer, so it cannot tell whether a new version was saved. ${kept} Reload the version list before saving again; a second save of an already saved version is refused, never stored twice.</p>
<button type="button" class="review-secondary" data-review-action="refresh-versions">Reload the version list</button>`);
        return;
      case "save_failure":
        this.showAlert(html`<p>${error.message} Nothing was saved. ${kept} Try Save New Version again.</p>`);
        return;
      case "network":
        this.showAlert(html`<p>${error.message} Nothing was saved. ${kept} Check that tmodel's engine is running, then try again.</p>`);
        return;
      default:
        this.showAlert(html`<p>The engine reported an unexpected failure: ${error.message} ${kept} Try again.</p>`);
    }
  }

  private async loadVersion(versionId: string | null): Promise<void> {
    if (!versionId || this.saving) return;
    this.clearAlert();
    this.announce(`Loading ${revisionName(this.host.target()?.versions, versionId)}…`);
    const loaded = await this.host.loadVersion(versionId);
    if (loaded) this.announce(`${revisionName(this.host.target()?.versions, versionId)} is shown. Your unsaved changes are kept; check them before saving.`);
  }

  private discard(): void {
    const draft = this.currentDraft(false);
    if (!draft || draft.empty || this.saving) return;
    if (!this.confirmingDiscard) {
      this.confirmingDiscard = true;
      this.discardButton.textContent = "Confirm discard";
      this.announce(`Press Confirm discard to discard ${draftChangeCount(draft)} unsaved ${draftChangeCount(draft) === 1 ? "change" : "changes"} on this route.`);
      return;
    }
    const target = this.host.target();
    if (target) this.drafts.get(target.projectId)?.delete(routeKey(draft.threatId, draft.routeId));
    this.confirmingDiscard = false;
    this.problems = [];
    this.clearAlert();
    this.host.unsavedChanged(this.unsavedCount);
    this.render();
    this.announce("Unsaved changes on this route were discarded.");
  }

  private reload(): void {
    this.blocked = undefined;
    this.context = { status: "idle" };
    this.clearAlert();
    this.render();
    this.ensureContext();
  }

  private selectRoute(routeId: string): void {
    if (!this.routes.some((route) => route.id === routeId)) return;
    this.routeId = routeId;
    if (this.pathId) this.routeChoices.set(this.pathId, routeId);
    this.problems = [];
    this.confirmingDiscard = false;
    this.outcome = undefined;
    this.render();
    this.ensureContext();
  }

  private edit(field: string, id: string, value: string, category: string | null): void {
    const state = this.context;
    const target = this.host.target();
    if (state.status !== "ready" || this.saving || !target?.editable) return;
    const context = state.context;
    const draft = this.currentDraft(true);
    if (!draft) return;
    const unsavedBefore = draftChangeCount(draft);
    if (field === "verdict" || field === "rationale" || field === "annotation") setReviewField(context, draft, id, field, value);
    else if (field === "feasibility") {
      if (value !== "" && !(FEASIBILITY_VALUES as readonly string[]).includes(value)) return;
      setFeasibility(context, draft, id, (value || null) as FeasibilityValue | null);
    } else if (field === "impact") {
      if (!category || !(IMPACT_CATEGORIES as readonly string[]).includes(category)) return;
      if (value !== "" && !(SEVERITY_VALUES as readonly string[]).includes(value)) return;
      setImpact(context, draft, id, category as ImpactCategory, (value || null) as SeverityValue | null);
    } else return;
    if (draft.empty) this.drafts.get(target.projectId)?.delete(routeKey(draft.threatId, draft.routeId));
    // A fixed field loses its error at once; the rest stay until the next save.
    const kind = field as DraftProblem["field"];
    const before = this.problems.length;
    this.problems = this.problems.filter((problem) => !(problem.target === id && problem.field === kind));
    if (this.problems.length !== before) this.clearFieldError(id, kind);
    this.confirmingDiscard = false;
    this.outcome = undefined;
    this.renderChanges();
    this.renderActions();
    // Route labels say which routes have unsaved changes; redraw them only when that flips.
    if ((unsavedBefore === 0) !== draft.empty) this.renderRouteOptions();
    this.host.unsavedChanged(this.unsavedCount);
  }

  private clearFieldError(targetId: string, field: string): void {
    const state = this.context;
    if (state.status !== "ready") return;
    const index = field === "feasibility"
      ? state.context.route.rating_paths.indexOf(targetId)
      : state.context.assertions.findIndex((assertion) => assertion.id === targetId);
    if (index < 0) return;
    const id = field === "feasibility" ? `review-p${index}-feasibility` : `review-a${index}-${field}`;
    const root = this.body as HTMLElement & ParentNode;
    root.querySelector?.<HTMLElement>(`#${id}-error`)?.setAttribute("hidden", "");
    root.querySelector?.<HTMLElement>(`#${id}`)?.removeAttribute("aria-invalid");
    if (this.problems.length === 0) this.clearAlert();
  }

  private currentDraft(create: boolean): RouteDraft | undefined {
    const target = this.host.target();
    const state = this.context;
    if (!target || state.status !== "ready") return undefined;
    const key = routeKey(state.context.threat.id, state.context.route.id);
    let project = this.drafts.get(target.projectId);
    if (!project && create) {
      project = new Map();
      this.drafts.set(target.projectId, project);
    }
    let draft = project?.get(key);
    if (!draft && create && project) {
      draft = new RouteDraft(state.context.threat.id, state.context.route.id, state.context.revision);
      project.set(key, draft);
    }
    return draft;
  }

  private draftFor(threatId: string, routeId: string): RouteDraft | undefined {
    const target = this.host.target();
    return target ? this.drafts.get(target.projectId)?.get(routeKey(threatId, routeId)) : undefined;
  }

  private ensureContext(): void {
    const target = this.host.target();
    const route = this.routes.find((candidate) => candidate.id === this.routeId);
    if (this.mode !== "review" || !target || !route || !this.client.hasSession) return;
    const key = `${target.projectId}\u0000${target.version.id}\u0000${route.threatId}\u0000${route.id}`;
    if ((this.context.status === "ready" || this.context.status === "loading") && this.context.key === key) return;
    const request = this.contextRequests.begin();
    this.context = { status: "loading", key };
    this.renderBody();
    this.renderActions();
    void this.client.getReviewContext({
      model_id: target.projectId,
      revision: target.version.id,
      matrix: REVIEW_MATRIX,
      threat_id: route.threatId,
      route_id: route.id,
    }, request.signal).then((context) => {
      if (!this.contextRequests.isCurrent(request)) return;
      this.contextRequests.complete(request);
      this.context = { status: "ready", key, context };
      this.render();
    }, (error: unknown) => {
      if (isAbort(error) || !this.contextRequests.isCurrent(request)) return;
      this.contextRequests.complete(request);
      this.context = { status: "failed", key, error };
      this.render();
    });
  }

  private render(): void {
    const target = this.host.target();
    const example = this.host.example();
    if (!target) {
      const show = Boolean(example) && this.host.projectsAvailable();
      this.element.hidden = !show;
      this.element.classList.remove("is-reviewing");
      this.routeRow.hidden = true;
      this.actions.hidden = true;
      this.changes.replaceChildren();
      this.targetLine.textContent = "";
      this.body.innerHTML = show ? html`<p>This example is read-only. Start a project from it to review its attack paths, rate them and save versions; the example itself is never changed.</p>
<button type="button" class="review-secondary" data-review-action="start-project">Start a project from this example</button>`.value : "";
      return;
    }
    this.element.hidden = false;
    this.element.classList.toggle("is-reviewing", this.mode === "review");
    this.computeRoutes(target);
    const editable = target.editable;
    this.targetLine.textContent = `${target.projectName} · ${versionLabel(target.version)}${target.kind === "file" ? " (read-only)" : editable ? " (Current)" : " (older version, read-only)"}`;
    if (this.mode === "view") {
      this.routeRow.hidden = true;
      this.actions.hidden = true;
      this.changes.replaceChildren();
      const unsaved = this.routes.reduce((total, route) => total + draftChangeCount(this.draftFor(route.threatId, route.id)), 0);
      this.body.innerHTML = editable && this.client.hasSession
        ? html`<p>Review this path's proposals and ratings in Review &amp; Edit.${unsaved ? html` This path has ${unsaved} unsaved ${unsaved === 1 ? "change" : "changes"}.` : ""}</p>
<button type="button" class="review-secondary" data-review-action="review">Review this path</button>`.value
        : html`<p>${editable ? "Reviewing needs a verified review session, which this app does not have." : readOnlyReason(target)}</p>`.value;
      return;
    }
    this.routeRow.hidden = this.routes.length === 0;
    this.actions.hidden = !editable;
    this.renderRouteOptions();
    this.renderBody();
    this.renderChanges();
    this.renderActions();
  }

  private computeRoutes(target: ReviewTarget): void {
    const path = target.report.attackPaths.find((row) => row.id === this.pathId);
    const threatId = path?.threat?.id;
    const seen = new Set<string>();
    const routes: RouteChoice[] = [];
    for (const assessment of target.views.risk.assessments) {
      if (!path || assessment.threat !== threatId) continue;
      for (const route of assessment.routes) {
        if (seen.has(route.id) || !(route.rating_paths.includes(path.id) || (route as { authored_path?: string | null }).authored_path === path.id)) continue;
        seen.add(route.id);
        routes.push({ id: route.id, threatId: assessment.threat, label: route.steps.map((step) => this.names.of(step)).join(" → ") });
      }
    }
    this.routes = routes.map((route, index) => ({ ...route, label: `Route ${index + 1} of ${routes.length}: ${route.label}` }));
    const remembered = this.pathId ? this.routeChoices.get(this.pathId) : undefined;
    this.routeId = routes.some((route) => route.id === remembered) ? remembered
      : routes.some((route) => route.id === this.routeId) ? this.routeId : routes[0]?.id;
  }

  private renderRouteOptions(): void {
    this.routeSelect.innerHTML = html`${this.routes.map((route) => {
      const unsaved = draftChangeCount(this.draftFor(route.threatId, route.id));
      return html`<option value="${route.id}"${route.id === this.routeId ? html` selected` : ""}>${route.label}${unsaved ? " (unsaved changes)" : ""}</option>`;
    })}`.value;
    this.routeSelect.value = this.routeId ?? "";
    this.routeSelect.disabled = this.saving || this.routes.length < 2;
  }

  private renderBody(): void {
    const target = this.host.target();
    this.body.setAttribute("aria-busy", String(this.context.status === "loading"));
    if (!target) return;
    const current = currentOf(target.versions);
    const notice = target.editable ? "" : target.kind === "file"
      ? html`<div class="review-notice"><p>${readOnlyReason(target)}</p></div>`
      : html`<div class="review-notice"><p>${readOnlyReason(target)}</p>
${current ? html`<button type="button" class="review-secondary" data-review-action="load-version" data-version="${current.id}">View the current version</button>` : ""}</div>`;
    if (!this.client.hasSession) {
      this.body.innerHTML = html`${notice}<p>Reviewing needs a verified review session from the desktop app, which it does not have, so this version is read-only.</p>`.value;
      return;
    }
    if (!this.pathId) {
      this.body.innerHTML = html`${notice}<p>Choose an attack path above to review it.</p>`.value;
      return;
    }
    if (this.routes.length === 0) {
      this.body.innerHTML = html`${notice}<p>The engine computed no route for this path in ${versionLabel(target.version)}, so there is nothing to review here.</p>`.value;
      return;
    }
    const state = this.context;
    if (state.status === "idle" || state.status === "loading") {
      this.body.innerHTML = html`${notice}<p class="review-loading">Loading the review for this route…</p>`.value;
      return;
    }
    if (state.status === "failed") {
      this.body.innerHTML = html`${notice}${contextFailure(state.error)}`.value;
      return;
    }
    const context = state.context;
    const draft = this.draftFor(context.threat.id, context.route.id);
    const allowed = Object.entries(context.permitted_actions).some(([name, value]) => name !== "accept_proposal" && value);
    const stale = draft && draft.baseRevision !== context.revision
      ? html`<p class="review-flag">These unsaved changes were made on ${revisionName(target.versions, draft.baseRevision)}. This is ${versionLabel(target.version)}: check them against it before saving.</p>` : "";
    const readOnly = target.editable && !allowed
      ? html`<p class="review-notice">This session can read this version but cannot review or rate it.</p>` : "";
    const outcome = this.outcome ? html`<p class="review-saved">${this.outcome.text}</p>` : "";
    this.body.innerHTML = html`${notice}${readOnly}${stale}${outcome}`.value + renderReviewContext({
      context,
      draft,
      names: this.names,
      versions: target.versions,
      editable: target.editable,
      saving: this.saving,
      problems: this.problems,
    });
  }

  private renderChanges(): void {
    const state = this.context;
    if (state.status !== "ready" || this.mode !== "review") {
      this.changes.innerHTML = "";
      return;
    }
    const draft = this.draftFor(state.context.threat.id, state.context.route.id);
    const lines = changeLines(state.context, draft, this.names);
    const others = this.unsavedCount - draftChangeCount(draft);
    this.changes.innerHTML = html`${lines.length ? html`<p class="review-changes-count"><strong>${lines.length} unsaved ${lines.length === 1 ? "change" : "changes"}</strong> on this route</p><ul>${lines.map((line) => html`<li>${line}</li>`)}</ul>` : html`<p class="review-changes-count">No unsaved changes on this route.</p>`}
${others > 0 ? html`<p class="review-help">${others} more unsaved ${others === 1 ? "change is" : "changes are"} kept on other routes of this project.</p>` : ""}`.value;
  }

  private renderActions(): void {
    const draft = this.currentDraft(false);
    const ready = this.context.status === "ready";
    const canSave = ready && !this.saving && !this.blocked && Boolean(draft && !draft.empty);
    this.saveButton.setAttribute("aria-disabled", String(!canSave));
    this.saveButton.textContent = this.saving ? "Saving…" : "Save New Version";
    this.saveButton.setAttribute("aria-busy", String(this.saving));
    this.discardButton.hidden = !draft || draft.empty;
    this.discardButton.disabled = this.saving;
    if (!this.confirmingDiscard) this.discardButton.textContent = "Discard changes";
    this.routeSelect.disabled = this.saving || this.routes.length < 2;
  }

  private showProblems(problems: readonly DraftProblem[]): void {
    const state = this.context;
    if (state.status !== "ready") return;
    const context = state.context;
    const fieldId = (problem: DraftProblem) => {
      if (problem.field === "feasibility") return `review-p${context.route.rating_paths.indexOf(problem.target)}-feasibility`;
      if (problem.field === "impact") return `review-s${context.risk_scores.findIndex((score) => score.id === problem.target)}-safety`;
      const index = context.assertions.findIndex((assertion) => assertion.id === problem.target);
      return problem.field === "verdict" ? `review-a${index}-verdict-accepted` : `review-a${index}-${problem.field}`;
    };
    this.showAlert(html`<p>Fix ${problems.length === 1 ? "this problem" : `these ${problems.length} problems`} before saving. Nothing was sent, and your changes are kept.</p>
<ul>${problems.map((problem) => html`<li><button type="button" class="review-link" data-review-action="focus-field" data-field="${fieldId(problem)}">${problem.message}</button></li>`)}</ul>`);
    this.alert.focus();
  }

  private showAlert(markup: { value: string }): void {
    this.alert.innerHTML = markup.value;
    this.alert.hidden = false;
    this.status.textContent = "";
  }

  private clearAlert(): void {
    this.alert.innerHTML = "";
    this.alert.hidden = true;
  }

  private announce(text: string): void {
    this.status.textContent = text;
  }
}

function readOnlyReason(target: ReviewTarget): string {
  return target.kind === "file"
    ? "This threat model file is open read-only. Start a project from it to review it and save versions; the file itself is never changed."
    : `You are viewing ${versionLabel(target.version)}, an older version. Reviewing and saving work only on the current version, so this view is read-only.`;
}

function currentOf(versions: ProjectVersions): ProjectVersion | undefined {
  return versions.versions.find((version) => version.current);
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function fieldName(field: string): string {
  const names: Readonly<Record<string, string>> = {
    rationale: "Rationale", annotation: "Annotation", verdict: "Decision", assertion_id: "Proposal",
    review_id: "Your review", attack_path_id: "Attack path", rating: "Feasibility", risk_score_id: "Risk assessment",
    values: "Impact", model: "Model", request: "Request", threat_id: "Threat", route_id: "Route",
  };
  if (field.startsWith("values.")) return `${names.values} (${field.slice(7)})`;
  return names[field] ?? field;
}

function contextFailure(error: unknown) {
  if (!(error instanceof ReviewApiError)) {
    return html`<p class="review-flag">The review could not be loaded: ${message(error)}.</p><button type="button" class="review-secondary" data-review-action="retry">Try again</button>`;
  }
  switch (error.kind) {
    case "unavailable":
      return html`<p>Reviewing is not available: ${error.message} This version stays read-only.</p>`;
    case "permission":
      return html`<p>This session cannot open reviews for this project: ${error.message} This version stays read-only.</p>`;
    case "not_found":
      return html`<p class="review-flag">This version or route is no longer available: ${error.message}</p><button type="button" class="review-secondary" data-review-action="refresh-versions">Reload the version list</button>`;
    case "validation":
      return html`<p class="review-flag">The engine cannot review this route: ${error.message}</p>`;
    default:
      return html`<p class="review-flag">The review could not be loaded: ${error.message}</p><button type="button" class="review-secondary" data-review-action="retry">Try again</button>`;
  }
}
