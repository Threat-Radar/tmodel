// Saved KG views and pending proposals on the Graph tab (DL-0046). Read-only: a
// proposed view is shown, clearly marked, but it is accepted only by the sponsor
// (`tmodel accept` in a pull request, PROC-0002), never from the app.
import type { GraphState } from "./graph-model";
import type { ProposalsDataProvider, ProposalsResponse, SavedView } from "./proposal-types";
import { reviewStatePresentation } from "./review-status";
import { changeLabel } from "./sdl-view";

export interface SavedViewElements {
  select: HTMLSelectElement;
  clear: HTMLButtonElement;
  status: HTMLElement;
  summary: HTMLElement;
  list: HTMLElement;
}

export type FocusSavedView = (nodeIds?: readonly string[]) => Promise<void>;

export function savedViewElements(root: Document = document): SavedViewElements {
  const get = <T extends HTMLElement>(id: string): T => {
    const element = root.getElementById(id);
    if (!element) throw new Error(`Missing required saved-view element #${id}`);
    return element as T;
  };
  return {
    select: get("saved-view-select"),
    clear: get("clear-saved-view"),
    status: get("saved-view-status"),
    summary: get("graph-proposals-summary"),
    list: get("graph-proposals-list"),
  };
}

export interface SavedViewPresentation {
  memberNodeIds: string[];
  dimmedNodeIds: string[];
  dimmedEdgeIds: string[];
}

/** Which loaded nodes and edges a saved view keeps bright and which it dims. */
export function savedViewPresentation(
  state: Pick<GraphState, "nodes" | "edges">,
  nodeIds: readonly string[],
): SavedViewPresentation {
  const members = new Set(nodeIds);
  return {
    memberNodeIds: state.nodes.filter((n) => members.has(n.id)).map((n) => n.id),
    dimmedNodeIds: state.nodes.filter((n) => !members.has(n.id)).map((n) => n.id),
    dimmedEdgeIds: state.edges
      .filter((e) => !(members.has(e.source) && members.has(e.target)))
      .map((e) => e.id),
  };
}

/** Option label: proposed views say so in the label itself, not only by color. */
export function savedViewLabel(view: SavedView): string {
  if (view.state === "proposed") return `Proposed: ${view.name} (not reviewed)`;
  if (view.state === "proposed_removal") return `${view.name} (removal proposed)`;
  return view.name;
}

export class SavedViewsPanel {
  private views: SavedView[] = [];

  constructor(
    private readonly provider: ProposalsDataProvider,
    private readonly file: string,
    private readonly elements: SavedViewElements,
    private readonly focus: FocusSavedView,
    private readonly documentRoot: Document = document,
  ) {}

  async load(): Promise<void> {
    let data: ProposalsResponse;
    try {
      data = await this.provider.getProposals(this.file);
    } catch (error) {
      this.views = [];
      this.renderOptions();
      this.elements.select.disabled = true;
      this.elements.status.className = "path-status is-error";
      this.elements.status.textContent = `Saved views unavailable: ${error instanceof Error ? error.message : String(error)}`;
      return;
    }
    this.views = data.views;
    this.renderOptions();
    this.renderProposals(data);
    this.renderStatus();
  }

  private renderOptions(): void {
    const { select, clear } = this.elements;
    const placeholder = this.option("", this.views.length ? "All loaded objects" : "No saved views");
    select.replaceChildren(placeholder);
    for (const view of this.views) select.append(this.option(view.id, savedViewLabel(view)));
    select.disabled = this.views.length === 0;
    select.onchange = () => void this.select(select.value);
    clear.disabled = true;
    clear.onclick = () => void this.select("");
  }

  private async select(id: string): Promise<void> {
    const view = this.views.find((candidate) => candidate.id === id);
    this.elements.select.value = view?.id ?? "";
    this.elements.clear.disabled = !view;
    await this.focus(view?.node_ids);
    this.renderStatus(view);
  }

  private renderStatus(view?: SavedView): void {
    const status = this.elements.status;
    status.className = "path-status";
    if (!view) {
      status.textContent = this.views.some((v) => v.state !== "accepted")
        ? "Proposed views are hypotheses until the sponsor accepts them (PROC-0002)."
        : "";
      return;
    }
    const p = reviewStatePresentation(view.state === "accepted" ? "accepted" : "proposed", null);
    status.classList.add(view.state === "accepted" ? "is-reviewed" : "is-unreviewed");
    const from = view.proposal ? ` · from ${view.proposal}` : "";
    const error = view.error ? ` · ${view.error}` : "";
    status.textContent = `${savedViewLabel(view)} · ${p.label}: ${p.description} · ${view.node_ids.length} objects${from}${error}`;
  }

  private renderProposals(data: ProposalsResponse): void {
    this.elements.summary.textContent = `Pending proposals (${data.proposals.length})`;
    const items = data.proposals.map((p) => {
      const li = this.documentRoot.createElement("li");
      const chip = this.documentRoot.createElement("span");
      const state = reviewStatePresentation("proposed", null);
      chip.className = `review-chip review-${state.kind}`;
      chip.textContent = state.label;
      const text = this.documentRoot.createElement("span");
      const changes = [
        ...p.objects.map((o) => `add ${o.id}`),
        ...(p.changes ?? []).map(changeLabel),
        ...p.assertions.map((a) => `${a.predicate} → ${a.object}`),
      ];
      text.textContent = ` ${p.rationale} (${p.by}, ${p.at}): ${changes.join("; ")}`;
      li.append(chip, text);
      return li;
    });
    this.elements.list.replaceChildren(...items);
  }

  private option(value: string, label: string): HTMLOptionElement {
    const option = this.documentRoot.createElement("option");
    option.value = value;
    option.textContent = label;
    return option;
  }
}
