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
  type AttackPathOption,
} from "./attack-path";
import { DevelopmentFixtureProvider } from "./graph-fixture";
import { graphLayoutForSize, incrementalGraphLayoutForSize } from "./graph-layout";
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
  GraphNode,
  GraphPropertyValue,
  GraphResponse,
} from "./graph-types";
import { LatestRequestGuard } from "./request-guard";

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

  constructor(
    private readonly provider: GraphDataProvider = new DevelopmentFixtureProvider(),
    private readonly documentRoot: Document = document,
  ) {}

  async start(): Promise<void> {
    const graph = await this.provider.getInitialGraph();
    this.requiredElement("data-source-notice").textContent = graph.notice ?? this.provider.metadata.notice;
    this.renderLegend();
    this.renderGraph();
    await this.loadGraphResponse(graph);
    this.renderAttackPathOptions(await this.provider.getAttackPaths());
    this.renderAttackPathStatus();
    const initialSelection = graph.focusId ?? this.state.nodes[0]?.id;
    if (initialSelection) this.handleSelection(initialSelection);
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
            "background-color": (element) => TYPE_COLORS[element.data("domainType")] ?? "#64748b",
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
    if (!nodeId || !this.cy) return;
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
    status.textContent = `${this.provider.metadata.label} path for ${shortId(option.goalId)} from ${fileName(option.sourceFile)} · ${reviewLabel}`;
    status.classList.add(option.result.review.reviewed ? "is-reviewed" : "is-unreviewed");
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
    if (!this.cy) return;
    const controller = new AbortController();
    const displayToken = Symbol("graph-loading-display");
    this.loadingDisplayToken = displayToken;
    const setCurrentProgress = (message: string) => {
      if (this.loadingDisplayToken === displayToken) this.setLoadingProgress(message);
    };
    const cancelFromExternalSignal = () => controller.abort();
    externalSignal?.addEventListener("abort", cancelFromExternalSignal, { once: true });
    if (externalSignal?.aborted) controller.abort();
    const responseSize = response.nodes.length + response.edges.length;
    let showProgress = responseSize > DEFAULT_GRAPH_BATCH_SIZE;
    setCurrentProgress(showProgress ? "Loading graph…" : "");

    let result: GraphLoadResult;
    try {
      result = await this.loader.load(
        response,
        (batch) => {
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
      if (this.loadingDisplayToken === displayToken) {
        this.loadingDisplayToken = undefined;
        this.setLoadingProgress("");
      }
    }
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
        this.keepNodesInViewport(newNodes, visibleExtent);
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

  private positionNewNodes(
    newNodes: NodeCollection,
    previousNodeIds: ReadonlySet<string>,
    fallbackAnchorId?: string,
  ): void {
    if (!this.cy) return;
    const slotsByAnchor = new Map<string, number>();
    const extent = this.cy.extent();
    const viewportCenter = { x: (extent.x1 + extent.x2) / 2, y: (extent.y1 + extent.y2) / 2 };
    newNodes.forEach((node) => {
      const anchorId = this.connectedPreviousNodeId(node.id(), previousNodeIds)
        ?? (fallbackAnchorId && previousNodeIds.has(fallbackAnchorId) ? fallbackAnchorId : undefined);
      const anchor = anchorId ? this.cy?.getElementById(anchorId) : undefined;
      const anchorPosition = anchor?.length ? anchor.position() : viewportCenter;
      const slotKey = anchorId ?? "__graph-origin__";
      const slot = slotsByAnchor.get(slotKey) ?? 0;
      slotsByAnchor.set(slotKey, slot + 1);
      const ring = Math.floor(slot / 8);
      const centerAngle = Math.atan2(
        viewportCenter.y - anchorPosition.y,
        viewportCenter.x - anchorPosition.x,
      );
      const fanStep = slot === 0 ? 0 : Math.ceil(slot / 2) * (Math.PI / 4) * (slot % 2 ? 1 : -1);
      const angle = centerAngle + fanStep;
      const radius = 120 + ring * 80;
      node.position({
        x: anchorPosition.x + Math.cos(angle) * radius,
        y: anchorPosition.y + Math.sin(angle) * radius,
      });
    });
  }

  private keepNodesInViewport(
    nodes: NodeCollection,
    extent: { x1: number; y1: number; x2: number; y2: number },
  ): void {
    const padding = 48;
    const bounds = nodes.boundingBox({ includeLabels: true });
    const availableWidth = extent.x2 - extent.x1 - padding * 2;
    const availableHeight = extent.y2 - extent.y1 - padding * 2;
    const shiftForAxis = (
      lower: number,
      upper: number,
      extentLower: number,
      extentUpper: number,
      available: number,
    ) => {
      if (upper - lower > available) {
        return (extentLower + extentUpper - lower - upper) / 2;
      }
      if (lower < extentLower + padding) return extentLower + padding - lower;
      if (upper > extentUpper - padding) return extentUpper - padding - upper;
      return 0;
    };
    nodes.shift({
      x: shiftForAxis(bounds.x1, bounds.x2, extent.x1, extent.x2, availableWidth),
      y: shiftForAxis(bounds.y1, bounds.y2, extent.y1, extent.y2, availableHeight),
    });
  }

  private connectedPreviousNodeId(
    nodeId: string,
    previousNodeIds: ReadonlySet<string>,
  ): string | undefined {
    for (const edge of this.state.edges) {
      if (edge.source === nodeId && previousNodeIds.has(edge.target)) return edge.target;
      if (edge.target === nodeId && previousNodeIds.has(edge.source)) return edge.source;
    }
    return undefined;
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
      list.append(item);
    }
  }

  private renderLegend(): void {
    const legend = this.requiredElement("type-legend");
    legend.replaceChildren();
    for (const [type, color] of Object.entries(TYPE_COLORS)) {
      const item = this.documentRoot.createElement("li");
      const swatch = this.documentRoot.createElement("span");
      swatch.className = "legend-swatch";
      swatch.style.backgroundColor = color;
      item.append(swatch, this.documentRoot.createTextNode(type));
      legend.append(item);
    }
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

function shortId(id: string): string {
  return id.includes(":") ? id.slice(id.indexOf(":") + 1) : id;
}
