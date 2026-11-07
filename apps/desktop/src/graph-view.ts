import { savedViewPresentation } from "./graph-saved-views";
import cytoscape, {
  type Core,
  type ElementDefinition,
  type Layouts,
  type NodeCollection,
} from "cytoscape";
import {
  attackPathOptionsForResponses,
  attackPathPresentation,
  attackPathReviewLabel,
  attackPathReviewState,
  type AttackPathOption,
} from "./attack-path";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { graphLayoutForSize, incrementalGraphLayoutForSize } from "./graph-layout";
import {
  PLACEMENT_OPTIONS,
  findPlacement,
  isClearPlacement,
  type Box,
  type PlacementRequest,
  type PlacementScene,
  type SceneEdge,
  type SceneNode,
} from "./graph-placement";
import {
  DEFAULT_GRAPH_BATCH_SIZE,
  ProgressiveGraphLoader,
  type GraphLoadResult,
} from "./graph-loader";
import {
  mergeGraph,
  relationshipsForNode,
  selectNode,
  toCytoscapeEdgeElement,
  toCytoscapeNodeElement,
  type GraphState,
} from "./graph-model";
import type {
  GraphDataProvider,
  GraphEdge,
  GraphNode,
  GraphPropertyValue,
  GraphResponse,
} from "./graph-types";
import { LatestRequestGuard } from "./request-guard";
import {
  REVIEW_STATE_KINDS,
  REVIEW_STATE_LABELS,
  relationshipReviewState,
  type ReviewStateKind,
} from "./review-status";

const TYPE_COLORS: Readonly<Record<string, string>> = {
  Product: "#2563eb",
  Component: "#0f766e",
  Vulnerability: "#dc2626",
  Weakness: "#ea580c",
  AttackPattern: "#9333ea",
  ThreatInstance: "#be123c",
  AttackPath: "#4f46e5",
  AttackStep: "#7c3aed",
};
// Node types outside TYPE_COLORS are drawn with this color and share one
// "Other types" legend entry.
const OTHER_TYPE_COLOR = "#64748b";
// Placement time per batch before the remaining nodes use a short search, so
// expanding a dense large graph cannot freeze the window.
const PLACEMENT_BUDGET_MS = 250;
// A saved view loads at most this many missing objects' neighborhoods (DL-0046).
const SAVED_VIEW_LOAD_LIMIT = 60;

// Relationships backed by an Assertion are styled by their review state with
// both a color and a line pattern. Structural relationships keep the neutral
// default edge style.
const REVIEW_STATE_EDGE_STYLES: Readonly<Record<ReviewStateKind, {
  color: string;
  dashPattern?: number[];
}>> = {
  accepted: { color: "#15803d" },
  proposed: { color: "#b45309", dashPattern: [7, 4] },
  changes_requested: { color: "#c2410c", dashPattern: [10, 3, 2, 3] },
  rejected: { color: "#b91c1c", dashPattern: [2, 3] },
  unknown: { color: "#6b7280", dashPattern: [14, 4, 2, 4, 2, 4] },
};

export class KnowledgeGraphView {
  private state: GraphState = { nodes: [], edges: [] };
  private cy?: Core;
  private readonly loader = new ProgressiveGraphLoader();
  private loadingDisplayToken?: symbol;
  private readonly expansionRequests = new LatestRequestGuard();
  private readonly attackPathRequests = new LatestRequestGuard();
  private readonly nodeButtons = new Map<string, HTMLButtonElement>();
  private availableAttackPaths: AttackPathOption[] = [];
  private activeAttackPath?: AttackPathOption;
  private incrementalLayout?: Layouts;
  private incrementalLayoutCleanup?: () => void;
  private visible = false;
  private fitOnVisibleResize = false;
  private disposed = false;
  // Aborted on dispose, so a graph load still in progress stops at its next batch.
  private readonly lifetime = new AbortController();

  constructor(
    private readonly provider: GraphDataProvider = new DevelopmentFixtureProvider(),
    private readonly documentRoot: Document = document,
  ) {}

  async start(): Promise<void> {
    try {
      await this.startGraph();
    } catch (error) {
      // A replaced view's failure is no one's to report: its replacement owns
      // the source notice and the Retry graph button now (#208 model switch).
      if (this.disposed) return;
      throw error;
    }
  }

  private async startGraph(): Promise<void> {
    const graph = await this.provider.getInitialGraph();
    // A view disposed while its graph loaded (another model was chosen) must
    // not draw into the canvas, or fill the controls, its replacement now owns.
    // The same check follows every later wait in this start.
    if (this.disposed) return;
    const notice = this.requiredElement("data-source-notice");
    notice.textContent = graph.notice ?? this.provider.metadata.notice;
    notice.classList.remove("is-error");
    // A retried start reuses the existing Cytoscape instance and listeners.
    if (!this.cy) {
      this.renderLegend();
      this.renderGraph();
    }
    this.renderWholeModelControl();
    await this.loadGraphResponse(graph);
    if (this.disposed) return;
    const initialSelection = this.state.selectedNodeId ?? graph.focusId ?? this.state.nodes[0]?.id;
    if (initialSelection) this.handleSelection(initialSelection);
    await this.loadAttackPaths();
  }

  setVisible(visible: boolean): void {
    this.visible = visible;
  }

  /**
   * Releases the Cytoscape instance, cancels pending work and empties the
   * shared controls, so a view for another model (#208 model picker, or the
   * bookkeeping toggle) takes over the same canvas and controls. A disposed
   * view never writes to them again, even when an older request finishes late.
   */
  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.lifetime.abort();
    this.expansionRequests.cancel();
    this.attackPathRequests.cancel();
    this.stopIncrementalLayout();
    this.cy?.destroy();
    this.cy = undefined;
    this.nodeButtons.clear();
    this.clearSharedControls();
  }

  get isDisposed(): boolean {
    return this.disposed;
  }

  /** The controls this view fills, back to their empty state and with its handlers removed. */
  private clearSharedControls(): void {
    const element = <T extends HTMLElement>(id: string) => this.documentRoot.getElementById(id) as T | null;
    element("node-list")?.replaceChildren();
    const count = element("node-count");
    if (count) count.textContent = "0";
    const notice = element("data-source-notice");
    if (notice) {
      notice.textContent = "";
      notice.classList.remove("is-error");
    }
    const loading = element("graph-loading");
    if (loading) {
      loading.textContent = "";
      loading.hidden = true;
    }
    const select = element<HTMLSelectElement>("attack-path-select");
    if (select) {
      const placeholder = this.documentRoot.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Choose an attack path…";
      select.replaceChildren(placeholder);
      select.onchange = null;
      select.disabled = true;
    }
    const clear = element<HTMLButtonElement>("clear-attack-path");
    if (clear) {
      clear.onclick = null;
      clear.disabled = true;
    }
    const status = element("attack-path-status");
    if (status) {
      status.textContent = "";
      status.className = "path-status";
    }
    const label = element("inspector-label");
    if (label) label.textContent = "Select a node";
    for (const id of ["inspector-type", "inspector-id"]) {
      const value = element(id);
      if (value) value.textContent = "";
    }
    element("property-list")?.replaceChildren();
    element("relationship-list")?.replaceChildren();
    const expand = element<HTMLButtonElement>("expand-node");
    if (expand) {
      expand.onclick = null;
      expand.disabled = true;
      expand.textContent = "Expand neighborhood";
    }
    const showAll = element<HTMLButtonElement>("graph-show-all");
    if (showAll) {
      showAll.onclick = null;
      showAll.disabled = true;
    }
  }

  /**
   * "Show whole model": loads every visible object of the model at once, for a
   * developer who wants the full graph rather than neighbourhoods (#208). Only
   * offered when the provider can list the whole model.
   */
  private renderWholeModelControl(): void {
    const button = this.documentRoot.getElementById("graph-show-all") as HTMLButtonElement | null;
    if (!button) return;
    const supported = typeof this.provider.getWholeGraph === "function";
    button.hidden = !supported;
    button.disabled = !supported;
    button.textContent = "Show whole model";
    button.onclick = supported ? () => void this.showWholeGraph() : null;
  }

  private async showWholeGraph(): Promise<void> {
    const getWholeGraph = this.provider.getWholeGraph?.bind(this.provider);
    if (this.disposed || !this.cy || !getWholeGraph) return;
    const button = this.documentRoot.getElementById("graph-show-all") as HTMLButtonElement | null;
    if (button) button.disabled = true;
    this.expansionRequests.cancel();
    try {
      const response = await getWholeGraph();
      if (this.disposed) return;
      const result = await this.loadGraphResponse(response);
      if (this.disposed || result?.canceled) return;
      this.renderInspector();
      this.applyAttackPathHighlight(this.activeAttackPath);
      if (button) button.textContent = "Whole model shown";
    } catch (error) {
      if (this.disposed) return;
      if (button) button.disabled = false;
      this.loadingDisplayToken = undefined;
      this.setLoadingProgress(`Unable to show the whole model: ${errorMessage(error)}`);
    }
  }

  /** Re-measure the canvas after its view becomes visible, fitting one hidden initial layout. */
  resize(): void {
    if (!this.visible || !this.cy) return;
    this.cy.resize();
    if (this.fitOnVisibleResize) {
      this.cy.fit(undefined, 48);
      this.fitOnVisibleResize = false;
    }
  }

  /**
   * Show a saved KG view (DL-0046): load the view's objects that are not on the
   * canvas yet, then dim everything outside the view. No ids clears the view.
   * Objects a proposed view names but the model does not have yet are skipped.
   */
  async focusSavedView(nodeIds?: readonly string[]): Promise<void> {
    if (!this.cy) return;
    if (!nodeIds || nodeIds.length === 0) {
      this.applySavedViewHighlight();
      return;
    }
    if (this.activeAttackPath) this.clearAttackPath();
    const previousNodeIds = new Set(this.state.nodes.map((node) => node.id));
    const loaded = new Set(previousNodeIds);
    for (const id of nodeIds.slice(0, SAVED_VIEW_LOAD_LIMIT)) {
      if (loaded.has(id)) continue;
      try {
        await this.loadGraphResponse(await this.provider.getNeighborhood(id), false);
      } catch (error) {
        console.warn(`Saved view: cannot load ${id}`, error);
      }
      for (const node of this.state.nodes) loaded.add(node.id);
    }
    if (this.state.nodes.some((node) => !previousNodeIds.has(node.id))) {
      this.runIncrementalGraphLayout(previousNodeIds, this.state.selectedNodeId);
    }
    this.applySavedViewHighlight(nodeIds);
  }

  private applySavedViewHighlight(nodeIds?: readonly string[]): void {
    if (!this.cy) return;
    this.cy.elements().removeClass("view-member view-dimmed");
    if (!nodeIds) return;
    const presentation = savedViewPresentation(this.state, nodeIds);
    for (const id of presentation.memberNodeIds) this.cy.getElementById(id).addClass("view-member");
    for (const id of presentation.dimmedNodeIds) this.cy.getElementById(id).addClass("view-dimmed");
    for (const id of presentation.dimmedEdgeIds) this.cy.getElementById(id).addClass("view-dimmed");
  }

  /** Attack-path discovery failures stay in the path toolbar; the graph remains usable. */
  private async loadAttackPaths(): Promise<void> {
    try {
      const responses = await this.provider.getAttackPaths();
      // An older model's paths arriving after a switch belong to no view.
      if (this.disposed) return;
      this.renderAttackPathOptions(responses);
      this.renderAttackPathStatus();
    } catch (error) {
      if (this.disposed) return;
      console.error("Unable to load attack paths", error);
      this.renderAttackPathOptions([]);
      this.requiredElement<HTMLSelectElement>("attack-path-select").disabled = true;
      const status = this.requiredElement("attack-path-status");
      status.className = "path-status is-error";
      status.textContent = `Unable to load attack paths: ${errorMessage(error)}`;
    }
  }

  private renderGraph(): void {
    this.cy = cytoscape({
      container: this.requiredElement("graph-canvas"),
      elements: [],
      layout: { name: "preset" },
      minZoom: 0.3,
      maxZoom: 2.5,
      style: [
        {
          selector: "node",
          style: {
            "background-color": (element) => TYPE_COLORS[element.data("domainType")] ?? OTHER_TYPE_COLOR,
            label: "data(label)", color: "#172033", "font-size": 7, "font-weight": 600,
            "text-wrap": "wrap", "text-max-width": "76px", "text-valign": "bottom",
            "text-margin-y": 10, "text-background-color": "#f8fafc",
            "text-background-opacity": 0.9, "text-background-padding": "2px",
            width: 28, height: 28, "border-width": 2, "border-color": "#ffffff",
          },
        },
        {
          selector: "edge",
          style: {
            width: 1.7, "line-color": "#94a3b8", "target-arrow-color": "#64748b",
            "target-arrow-shape": "triangle", "curve-style": "bezier", label: "data(label)",
            "source-distance-from-node": 5, "target-distance-from-node": 8,
            "font-size": 5, color: "#526078", "text-background-color": "#ffffff",
            "text-background-opacity": 1, "text-background-padding": "3px",
            "text-background-shape": "roundrectangle", "text-rotation": "autorotate",
            "text-margin-y": -7,
          },
        },
        ...REVIEW_STATE_KINDS.map((kind) => {
          const { color, dashPattern } = REVIEW_STATE_EDGE_STYLES[kind];
          return {
            selector: `edge[reviewState = "${kind}"]`,
            style: {
              "line-color": color, "target-arrow-color": color, color,
              ...(dashPattern
                ? { "line-style": "dashed" as const, "line-dash-pattern": dashPattern }
                : { width: 2.4 }),
            },
          };
        }),
        {
          selector: "node:selected",
          style: {
            "border-width": 5, "border-color": "#facc15", "overlay-color": "#facc15",
            "overlay-opacity": 0.12, "overlay-padding": 8,
          },
        },
        {
          selector: ".path-dimmed",
          style: { opacity: 0.16, "text-opacity": 0.2 },
        },
        {
          selector: "node.path-step",
          style: {
            opacity: 1, "text-opacity": 1, "border-width": 5, "border-color": "#f59e0b",
            "overlay-color": "#fbbf24", "overlay-opacity": 0.14, "overlay-padding": 7,
          },
        },
        {
          selector: "edge.path-edge",
          style: {
            opacity: 1, "text-opacity": 1, width: 4, "line-color": "#f59e0b",
            "target-arrow-color": "#d97706", "arrow-scale": 1.3, "z-index": 20,
          },
        },
        {
          selector: "node.path-step:selected",
          style: {
            "border-width": 6, "border-color": "#facc15", "overlay-color": "#facc15",
            "overlay-opacity": 0.2, "overlay-padding": 8,
          },
        },
        {
          selector: ".view-dimmed",
          style: { opacity: 0.16, "text-opacity": 0.2 },
        },
        {
          selector: "node.view-member",
          style: { "border-width": 4, "border-color": "#0ea5e9" },
        },
        {
          selector: "node.path-dimmed:selected",
          style: {
            opacity: 0.65, "border-width": 6, "border-color": "#facc15",
            "overlay-color": "#facc15", "overlay-opacity": 0.15, "overlay-padding": 8,
          },
        },
      ],
    });
    this.cy.on("tap", "node", (event) => this.handleSelection(event.target.id()));
    this.renderNodeList();
  }

  private handleSelection(nodeId: string): void {
    if (this.disposed) return;
    const previousNodeId = this.state.selectedNodeId;
    const selectedState = selectNode(this.state, nodeId);
    if (selectedState.selectedNodeId !== nodeId) return;
    if (previousNodeId && previousNodeId !== nodeId) this.expansionRequests.cancel();
    this.state = selectedState;
    if (previousNodeId && previousNodeId !== nodeId) {
      this.cy?.getElementById(previousNodeId).unselect();
      this.nodeButtons.get(previousNodeId)?.classList.remove("is-selected");
    }
    this.cy?.getElementById(nodeId).select();
    this.nodeButtons.get(nodeId)?.classList.add("is-selected");
    this.renderInspector();
  }

  private async expandSelection(): Promise<void> {
    const nodeId = this.state.selectedNodeId;
    if (this.disposed || !nodeId || !this.cy) return;
    const request = this.expansionRequests.begin();
    const previousNodeIds = new Set(this.state.nodes.map((node) => node.id));
    try {
      const response = await this.provider.getNeighborhood(nodeId);
      if (!this.expansionRequests.isCurrent(request) || this.state.selectedNodeId !== nodeId) return;
      const inserted = await this.loadGraphResponse(response, false, request.signal);
      if (
        !this.expansionRequests.isCurrent(request)
        || this.state.selectedNodeId !== nodeId
        || inserted?.canceled
      ) return;
      if (inserted && inserted.insertedNodes + inserted.insertedEdges > 0) {
        this.runIncrementalGraphLayout(previousNodeIds, nodeId);
      }
      this.renderInspector();
      this.applyAttackPathHighlight(this.activeAttackPath);
    } catch (error) {
      if (this.expansionRequests.isCurrent(request) && this.state.selectedNodeId === nodeId) {
        this.applyAttackPathHighlight(this.activeAttackPath);
        this.loadingDisplayToken = undefined;
        this.setLoadingProgress(`Unable to expand neighborhood: ${errorMessage(error)}`);
      }
    } finally {
      this.expansionRequests.complete(request);
    }
  }

  private renderAttackPathOptions(response: Awaited<ReturnType<GraphDataProvider["getAttackPaths"]>>): void {
    this.availableAttackPaths = attackPathOptionsForResponses(response);
    const select = this.requiredElement<HTMLSelectElement>("attack-path-select");
    const placeholder = this.documentRoot.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Choose an attack path…";
    select.replaceChildren(placeholder);
    select.disabled = false;
    for (const option of this.availableAttackPaths) {
      const element = this.documentRoot.createElement("option");
      element.value = option.id;
      element.textContent = option.label;
      select.append(element);
    }
    select.onchange = () => void this.selectAttackPath(select.value);
    this.requiredElement<HTMLButtonElement>("clear-attack-path").onclick = () => this.clearAttackPath();
  }

  private async selectAttackPath(optionId: string): Promise<void> {
    if (this.disposed) return;
    const option = this.availableAttackPaths.find((candidate) => candidate.id === optionId);
    if (!option) {
      this.clearAttackPath();
      return;
    }

    const request = this.attackPathRequests.begin();
    const previousNodeIds = new Set(this.state.nodes.map((node) => node.id));
    try {
      for (const stepId of new Set(option.result.steps)) {
        // A loaded step does not prove that all of its directed relationships
        // have been loaded. Request each path step's neighborhood so missing
        // `precedes` edges can be merged without duplicating existing elements.
        const response = await this.provider.getNeighborhood(stepId);
        if (!this.attackPathRequests.isCurrent(request)) return;
        const result = await this.loadGraphResponse(response, false, request.signal);
        if (!this.attackPathRequests.isCurrent(request) || result?.canceled) return;
      }
      if (!this.attackPathRequests.isCurrent(request)) return;
      if (this.state.nodes.some((node) => !previousNodeIds.has(node.id))) {
        this.runIncrementalGraphLayout(previousNodeIds, this.state.selectedNodeId);
      }
      this.activeAttackPath = option;
      this.applyAttackPathHighlight(option);
      this.renderAttackPathStatus(option);
      this.requiredElement<HTMLButtonElement>("clear-attack-path").disabled = false;
    } catch (error) {
      if (this.attackPathRequests.isCurrent(request)) {
        this.requiredElement<HTMLSelectElement>("attack-path-select").value =
          this.activeAttackPath?.id ?? "";
        this.applyAttackPathHighlight(this.activeAttackPath);
        this.renderAttackPathError(error);
      }
    } finally {
      this.attackPathRequests.complete(request);
    }
  }

  private clearAttackPath(): void {
    if (this.disposed) return;
    this.attackPathRequests.cancel();
    this.activeAttackPath = undefined;
    this.applyAttackPathHighlight();
    this.requiredElement<HTMLSelectElement>("attack-path-select").value = "";
    this.requiredElement<HTMLButtonElement>("clear-attack-path").disabled = true;
    this.renderAttackPathStatus();
  }

  private renderAttackPathStatus(option?: AttackPathOption): void {
    const status = this.requiredElement("attack-path-status");
    status.className = "path-status";
    if (!option) {
      status.textContent = this.provider.metadata.notice;
      return;
    }
    const reviewLabel = attackPathReviewLabel(option.result.review);
    const reviewState = attackPathReviewState(option.result.review).kind;
    status.textContent = `${this.provider.metadata.label} path for ${shortId(option.goalId)} from ${fileName(option.sourceFile)} · ${reviewLabel}`;
    status.classList.add(reviewState === "accepted" ? "is-reviewed" : "is-unreviewed");
    if (reviewState === "rejected" || reviewState === "changes_requested") {
      status.classList.add("is-negative");
    }
  }

  private renderAttackPathError(error: unknown): void {
    this.renderAttackPathStatus(this.activeAttackPath);
    const status = this.requiredElement("attack-path-status");
    status.textContent = `Unable to load selected attack path: ${errorMessage(error)} · ${status.textContent ?? ""}`;
    status.classList.add("is-error");
  }

  private applyAttackPathHighlight(option?: AttackPathOption): void {
    if (!this.cy) return;
    this.cy.elements().removeClass("path-step path-edge path-dimmed");
    const presentation = attackPathPresentation(this.state, option?.result);
    for (const id of presentation.dimmedNodeIds) this.cy.getElementById(id).addClass("path-dimmed");
    for (const id of presentation.dimmedEdgeIds) this.cy.getElementById(id).addClass("path-dimmed");
    for (const id of presentation.stepNodeIds) this.cy.getElementById(id).addClass("path-step");
    for (const id of presentation.pathEdgeIds) this.cy.getElementById(id).addClass("path-edge");
  }

  private async loadGraphResponse(
    response: GraphResponse,
    runLayout = true,
    externalSignal?: AbortSignal,
  ): Promise<GraphLoadResult | undefined> {
    if (!this.cy || this.disposed) return;
    const controller = new AbortController();
    const displayToken = Symbol("graph-loading-display");
    this.loadingDisplayToken = displayToken;
    const setCurrentProgress = (message: string) => {
      if (this.loadingDisplayToken === displayToken) this.setLoadingProgress(message);
    };
    const cancelFromExternalSignal = () => controller.abort();
    externalSignal?.addEventListener("abort", cancelFromExternalSignal, { once: true });
    if (externalSignal?.aborted) controller.abort();
    this.lifetime.signal.addEventListener("abort", cancelFromExternalSignal, { once: true });
    const responseSize = response.nodes.length + response.edges.length;
    let showProgress = responseSize > DEFAULT_GRAPH_BATCH_SIZE;
    setCurrentProgress(showProgress ? "Loading graph…" : "");

    let result: GraphLoadResult;
    try {
      result = await this.loader.load(
        response,
        (batch) => {
          if (this.disposed) return;
          this.state = mergeGraph(this.state, {
            source: response.source,
            nodes: batch.nodes,
            edges: batch.edges,
          });
          const elements = [
            ...batch.nodes.map(toCytoscapeNodeElement),
            ...batch.edges.map(toCytoscapeEdgeElement),
          ];
          this.cy?.batch(() => this.cy?.add(elements as ElementDefinition[]));
          this.appendNodeList(batch.nodes);
          this.requiredElement("node-count").textContent = String(this.state.nodes.length);
          if (this.state.selectedNodeId) this.renderInspector();
          if (showProgress) {
            setCurrentProgress(`Loading graph… ${batch.processed} of ${batch.total}`);
          }
        },
        controller.signal,
        (total) => {
          // The loader's plan includes pending edges activated by this page,
          // so it is authoritative even when the raw response itself is small.
          showProgress = total > DEFAULT_GRAPH_BATCH_SIZE;
          setCurrentProgress(showProgress ? `Loading graph… 0 of ${total}` : "");
        },
      );
    } finally {
      externalSignal?.removeEventListener("abort", cancelFromExternalSignal);
      this.lifetime.signal.removeEventListener("abort", cancelFromExternalSignal);
      if (!this.disposed && this.loadingDisplayToken === displayToken) {
        this.loadingDisplayToken = undefined;
        this.setLoadingProgress("");
      }
    }
    if (this.disposed) return { ...result, canceled: true };
    if (!result.canceled) {
      // Batches intentionally skip duplicate nodes. Reconcile their current
      // provider metadata after a successful response so fields such as
      // `expandable` do not remain stale on an already loaded node.
      this.state = mergeGraph(this.state, {
        source: response.source,
        nodes: response.nodes,
        edges: [],
      });
    }
    if (!result.canceled && runLayout && result.insertedNodes + result.insertedEdges > 0) {
      this.runGraphLayout();
    }
    return result;
  }

  private runGraphLayout(preservePositions = false): void {
    if (!this.cy) return;
    if (!this.visible) this.fitOnVisibleResize = true;
    this.cy.layout(graphLayoutForSize(
      this.cy.nodes().length,
      this.cy.edges().length,
      preservePositions,
    )).run();
  }

  private runIncrementalGraphLayout(
    previousNodeIds: ReadonlySet<string>,
    fallbackAnchorId?: string,
  ): void {
    if (!this.cy) return;
    this.stopIncrementalLayout();
    const newNodes = this.cy.nodes().filter((node) => !previousNodeIds.has(node.id()));
    if (newNodes.length === 0) return;

    this.positionNewNodes(newNodes, previousNodeIds, fallbackAnchorId);
    const options = incrementalGraphLayoutForSize(
      this.cy.nodes().length,
      this.cy.edges().length,
    );
    // Large graphs retain their existing grid layout. Newly loaded nodes keep
    // the nearby positions assigned above rather than triggering another
    // whole-graph layout.
    if (!options) return;

    const viewport = { pan: { ...this.cy.pan() }, zoom: this.cy.zoom() };
    const visibleExtent = this.cy.extent();
    const temporarilyLocked = this.cy.nodes().filter(
      (node) => previousNodeIds.has(node.id()) && !node.locked(),
    );
    temporarilyLocked.lock();

    let layout: Layouts | undefined;
    let cleaned = false;
    const cleanup = () => {
      if (cleaned) return;
      cleaned = true;
      temporarilyLocked.unlock();
      try {
        // CoSE does not see edges, arrowheads or edge labels, so move only
        // the new nodes it left overlapping something or out of view.
        this.positionNewNodes(newNodes, previousNodeIds, fallbackAnchorId, {
          keepClearPositions: true,
          visibleExtent,
        });
      } finally {
        try {
          this.cy?.zoom(viewport.zoom);
          this.cy?.pan(viewport.pan);
        } finally {
          if (this.incrementalLayout === layout) {
            this.incrementalLayout = undefined;
            this.incrementalLayoutCleanup = undefined;
          }
        }
      }
    };

    try {
      layout = this.cy.layout(options);
      this.incrementalLayout = layout;
      this.incrementalLayoutCleanup = cleanup;
      layout.one("layoutstop", cleanup);
      layout.run();
    } catch (error) {
      cleanup();
      throw error;
    }
  }

  /**
   * Places new nodes one at a time in free space near the nodes they connect
   * to, treating every already placed node, label, edge, arrowhead and edge
   * label as an obstacle. Previously loaded nodes are never moved.
   */
  private positionNewNodes(
    newNodes: NodeCollection,
    previousNodeIds: ReadonlySet<string>,
    fallbackAnchorId?: string,
    { keepClearPositions = false, visibleExtent }: {
      keepClearPositions?: boolean;
      visibleExtent?: Box;
    } = {},
  ): void {
    const cy = this.cy;
    if (!cy) return;
    const extent = visibleExtent ?? cy.extent();
    const viewportCenter = { x: (extent.x1 + extent.x2) / 2, y: (extent.y1 + extent.y2) / 2 };
    const edgesByNode = new Map<string, GraphEdge[]>();
    for (const edge of this.state.edges) {
      for (const id of [edge.source, edge.target]) edgesByNode.set(id, [...(edgesByNode.get(id) ?? []), edge]);
    }
    const settled = new Set([...previousNodeIds].filter((id) => cy.getElementById(id).length > 0));
    const scene: PlacementScene = { nodes: [], edges: [], bounds: insetBox(extent, 12) };
    for (const id of settled) this.addToPlacementScene(scene, id, settled, edgesByNode, false);
    const neighborsOf = (id: string) => [...new Set(
      (edgesByNode.get(id) ?? []).map((edge) => (edge.source === id ? edge.target : edge.source)),
    )].filter((neighbor) => neighbor !== id && settled.has(neighbor));

    const pending: NodeCollection[number][] = [];
    newNodes.forEach((node) => { pending.push(node); });
    let unresolved = 0;
    const started = performance.now();
    while (pending.length > 0) {
      // Place nodes next to already settled neighbors first, so chains of new
      // nodes grow outward from the existing graph. A group with no link to
      // it starts from its best-connected node, so the rest gather around it.
      const attached = pending.findIndex((node) => neighborsOf(node.id()).length > 0);
      const next = attached >= 0 ? attached : pending.reduce((best, node, index) => (
        (edgesByNode.get(node.id())?.length ?? 0) > (edgesByNode.get(pending[best].id())?.length ?? 0)
          ? index
          : best
      ), 0);
      const [node] = pending.splice(next, 1);
      const neighborIds = neighborsOf(node.id());
      const anchorIds = neighborIds.length > 0
        ? neighborIds
        : fallbackAnchorId && settled.has(fallbackAnchorId) ? [fallbackAnchorId] : [];
      const position = { ...node.position() };
      const request: PlacementRequest = {
        footprint: footprintOf(node.boundingBox({ includeLabels: true, includeOverlays: false }), position),
        anchors: anchorIds.map((id) => ({
          id,
          position: { ...cy.getElementById(id).position() },
          edgeLabel: edgeLabelSize(edgesByNode.get(node.id())?.find((edge) => (
            edge.source === id || edge.target === id
          ))),
        })),
        fallbackCenter: viewportCenter,
      };
      if (!keepClearPositions || !isClearPlacement(position, request, scene)) {
        const overBudget = performance.now() - started > PLACEMENT_BUDGET_MS;
        const result = findPlacement(request, scene, overBudget
          ? { maxRadius: PLACEMENT_OPTIONS.firstRing + PLACEMENT_OPTIONS.ringStep }
          : {});
        node.position(result.position);
        if (result.collisions > 0) unresolved += 1;
      }
      settled.add(node.id());
      this.addToPlacementScene(scene, node.id(), settled, edgesByNode, true);
    }
    if (unresolved > 0 && keepClearPositions) {
      console.warn(`Placed ${unresolved} new graph node(s) with unavoidable overlap; nearby space is full.`);
    }
  }

  /** Adds a settled node and its relationships to other settled nodes. */
  private addToPlacementScene(
    scene: PlacementScene,
    nodeId: string,
    settled: ReadonlySet<string>,
    edgesByNode: ReadonlyMap<string, readonly GraphEdge[]>,
    includeEdgesToSettled: boolean,
  ): void {
    const node = this.sceneNode(nodeId);
    if (node) scene.nodes.push(node);
    for (const edge of edgesByNode.get(nodeId) ?? []) {
      const otherId = edge.source === nodeId ? edge.target : edge.source;
      if (!settled.has(otherId)) continue;
      // Without `includeEdgesToSettled`, each edge is added once, from its
      // source, while building the initial scene.
      if (!includeEdgesToSettled && edge.source !== nodeId) continue;
      const sceneEdge = this.sceneEdge(edge);
      if (sceneEdge) scene.edges.push(sceneEdge);
    }
  }

  private sceneNode(id: string): SceneNode | undefined {
    const node = this.cy?.getElementById(id);
    if (!node?.length) return undefined;
    return {
      id,
      position: { ...node.position() },
      box: plainBox(node.boundingBox({ includeLabels: true, includeOverlays: false })),
    };
  }

  private sceneEdge(edge: GraphEdge): SceneEdge | undefined {
    const source = this.cy?.getElementById(edge.source);
    const target = this.cy?.getElementById(edge.target);
    if (!source?.length || !target?.length) return undefined;
    const element = this.cy?.getElementById(edge.id);
    const label = element?.length
      ? element.boundingBox({ includeNodes: false, includeEdges: false, includeLabels: true, includeOverlays: false })
      : undefined;
    return {
      id: edge.id,
      sourceId: edge.source,
      targetId: edge.target,
      source: { ...source.position() },
      target: { ...target.position() },
      targetRadius: target.width() / 2,
      labelBox: label && label.w > 0 && label.h > 0 ? plainBox(label) : undefined,
    };
  }

  private stopIncrementalLayout(): void {
    const layout = this.incrementalLayout;
    const cleanup = this.incrementalLayoutCleanup;
    this.incrementalLayout = undefined;
    this.incrementalLayoutCleanup = undefined;
    try {
      layout?.stop();
    } finally {
      cleanup?.();
    }
  }

  private renderNodeList(): void {
    const list = this.requiredElement("node-list");
    list.replaceChildren();
    this.nodeButtons.clear();
    this.appendNodeList(this.state.nodes);
    this.requiredElement("node-count").textContent = String(this.state.nodes.length);
  }

  private appendNodeList(nodes: readonly GraphNode[]): void {
    const list = this.requiredElement("node-list");
    for (const node of nodes) {
      const item = this.documentRoot.createElement("li");
      const button = this.documentRoot.createElement("button");
      button.type = "button";
      button.className = "node-list-button";
      button.dataset.nodeId = node.id;
      if (node.id === this.state.selectedNodeId) button.classList.add("is-selected");
      button.addEventListener("click", () => this.handleSelection(node.id));
      button.append(this.textElement("span", node.label, "node-list-label"));
      button.append(this.textElement("span", node.domainType, "type-chip"));
      this.nodeButtons.set(node.id, button);
      item.append(button);
      list.append(item);
    }
  }

  private setLoadingProgress(message: string): void {
    const indicator = this.requiredElement("graph-loading");
    indicator.textContent = message;
    indicator.hidden = message.length === 0;
  }

  private renderInspector(): void {
    const selected = this.state.nodes.find((node) => node.id === this.state.selectedNodeId);
    if (!selected) return;
    this.requiredElement("inspector-label").textContent = selected.label;
    this.requiredElement("inspector-type").textContent = selected.domainType;
    this.requiredElement("inspector-id").textContent = selected.id;
    this.renderProperties(selected);
    this.renderRelationships(selected);
    const expandButton = this.requiredElement<HTMLButtonElement>("expand-node");
    expandButton.disabled = !selected.expandable;
    expandButton.textContent = selected.expandable ? "Expand neighborhood" : "No additional neighbors";
    expandButton.onclick = () => void this.expandSelection();
  }

  private renderProperties(node: GraphNode): void {
    const container = this.requiredElement("property-list");
    container.replaceChildren();
    const entries = Object.entries(node.properties);
    if (entries.length === 0) {
      container.append(this.textElement("p", "No additional properties.", "empty-state"));
      return;
    }
    for (const [key, value] of entries) {
      const row = this.documentRoot.createElement("div");
      row.className = "detail-row";
      row.append(this.textElement("dt", humanize(key)));
      row.append(this.textElement("dd", formatValue(value)));
      container.append(row);
    }
  }

  private renderRelationships(node: GraphNode): void {
    const list = this.requiredElement("relationship-list");
    list.replaceChildren();
    const relationships = relationshipsForNode(this.state, node.id);
    if (relationships.length === 0) {
      list.append(this.textElement("li", "No loaded relationships.", "empty-state"));
      return;
    }
    for (const relationship of relationships) {
      const item = this.documentRoot.createElement("li");
      item.className = "relationship-item";
      const arrow = relationship.direction === "outgoing" ? "→" : "←";
      item.append(this.textElement("span", `${arrow} ${relationship.relationshipType}`, "relationship-type"));
      const button = this.documentRoot.createElement("button");
      button.type = "button";
      button.textContent = relationship.connectedNode?.label ?? relationship.connectedNodeId;
      button.disabled = !relationship.connectedNode;
      button.addEventListener("click", () => this.handleSelection(relationship.connectedNodeId));
      item.append(button);
      this.appendRelationshipReview(item, relationship.properties);
      list.append(item);
    }
  }

  /** Shows the recorded Assertion/Review state of one relationship, if any. */
  private appendRelationshipReview(item: HTMLElement, properties: GraphNode["properties"]): void {
    const review = relationshipReviewState(properties);
    if (!review) return;
    item.classList.add(`review-${review.kind}`);
    const badge = this.textElement("span", review.label, "review-badge");
    badge.prepend(this.lineSwatch(review.kind));
    item.append(badge);
    const raw = [
      `assertion_status: ${review.assertionStatus ?? "not recorded"}`,
      `review_status: ${review.reviewStatus ?? "not recorded"}`,
    ];
    item.append(this.textElement("span", raw.join(" · "), "review-raw"));
    const sources = [properties.assertion_ids, properties.review_ids]
      .filter((value) => value !== undefined && value !== null)
      .map(formatValue)
      .join(" · ");
    if (sources) item.append(this.textElement("span", sources, "review-raw"));
  }

  private renderLegend(): void {
    const legend = this.requiredElement("type-legend");
    legend.replaceChildren();
    const types: [string, string][] = [...Object.entries(TYPE_COLORS), ["Other types", OTHER_TYPE_COLOR]];
    for (const [type, color] of types) {
      const item = this.documentRoot.createElement("li");
      const swatch = this.documentRoot.createElement("span");
      swatch.className = "legend-swatch";
      swatch.style.backgroundColor = color;
      item.append(swatch, this.documentRoot.createTextNode(type));
      legend.append(item);
    }
    // Relationship states follow a divider; their line markers (not dots)
    // and the list's accessible name identify them without a heading.
    const relationshipLegend = this.requiredElement("relationship-legend");
    const divider = this.documentRoot.createElement("li");
    divider.className = "legend-divider";
    divider.setAttribute("aria-hidden", "true");
    const structural = this.documentRoot.createElement("li");
    structural.title = "Relationship with no Assertion or Review record";
    structural.append(this.lineSwatch(), this.documentRoot.createTextNode("Structural"));
    relationshipLegend.replaceChildren(divider, structural);
    for (const kind of REVIEW_STATE_KINDS) {
      const item = this.documentRoot.createElement("li");
      item.title = `Relationship review status: ${REVIEW_STATE_LABELS[kind]}`;
      item.append(this.lineSwatch(kind), this.documentRoot.createTextNode(REVIEW_STATE_LABELS[kind]));
      relationshipLegend.append(item);
    }
  }

  /** A short line drawn with the same color and dash pattern as the graph edge. */
  private lineSwatch(kind?: ReviewStateKind): SVGSVGElement {
    const namespace = "http://www.w3.org/2000/svg";
    const svg = this.documentRoot.createElementNS(namespace, "svg");
    svg.setAttribute("class", "legend-line");
    // Drawn at 1:1 so the dash patterns match the graph edges.
    svg.setAttribute("viewBox", "0 0 20 6");
    svg.setAttribute("aria-hidden", "true");
    const line = this.documentRoot.createElementNS(namespace, "line");
    line.setAttribute("x1", "0");
    line.setAttribute("y1", "3");
    line.setAttribute("x2", "20");
    line.setAttribute("y2", "3");
    const style = kind ? REVIEW_STATE_EDGE_STYLES[kind] : undefined;
    line.setAttribute("stroke", style?.color ?? "#94a3b8");
    line.setAttribute("stroke-width", kind === "accepted" ? "2.4" : "1.7");
    if (style?.dashPattern) line.setAttribute("stroke-dasharray", style.dashPattern.join(" "));
    svg.append(line);
    return svg;
  }

  private textElement(tag: string, text: string, className?: string): HTMLElement {
    const element = this.documentRoot.createElement(tag);
    element.textContent = text;
    if (className) element.className = className;
    return element;
  }

  private requiredElement<T extends HTMLElement = HTMLElement>(id: string): T {
    const element = this.documentRoot.getElementById(id);
    if (!element) throw new Error(`Missing required graph UI element #${id}`);
    return element as T;
  }
}

function humanize(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (character) => character.toUpperCase());
}

function formatValue(value: GraphPropertyValue): string {
  if (Array.isArray(value)) return value.join(", ");
  if (value === null) return "—";
  return String(value);
}

function fileName(path: string): string {
  return path.split(/[\\/]/).pop() ?? path;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "unexpected error";
}

// Edge labels use a 5px font with 3px padding (see the edge style above);
// this estimate is close enough to keep new labels off existing nodes.
function edgeLabelSize(edge?: GraphEdge): { width: number; height: number } | undefined {
  if (!edge) return undefined;
  const text = toCytoscapeEdgeElement(edge).data.label;
  return { width: text.length * 3 + 6, height: 12 };
}

function plainBox(box: { x1: number; y1: number; x2: number; y2: number }): Box {
  return { x1: box.x1, y1: box.y1, x2: box.x2, y2: box.y2 };
}

function insetBox(box: Box, amount: number): Box {
  return { x1: box.x1 + amount, y1: box.y1 + amount, x2: box.x2 - amount, y2: box.y2 - amount };
}

function footprintOf(box: Box, position: { x: number; y: number }) {
  return {
    left: position.x - box.x1,
    right: box.x2 - position.x,
    top: position.y - box.y1,
    bottom: box.y2 - position.y,
  };
}

function shortId(id: string): string {
  return id.includes(":") ? id.slice(id.indexOf(":") + 1) : id;
}
