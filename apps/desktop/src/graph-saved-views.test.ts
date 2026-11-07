import { describe, expect, it } from "vitest";
import fixture from "./fixtures/proposals-mvp-01.json";
import { EngineProposalsDataProvider, parseProposals } from "./engine-proposals-provider";
import {
  savedViewFile,
  savedViewLabel,
  savedViewPresentation,
  SavedViewsPanel,
  type SavedViewElements,
} from "./graph-saved-views";
import type { ProposalsDataProvider, ProposalsResponse, SavedView } from "./proposal-types";

const DATA = parseProposals(fixture);

describe("saved KG views on the Graph tab (DL-0046)", () => {
  it("follows the active model picker choice instead of the startup URL", () => {
    expect(savedViewFile("mvp-02-automotive-ecu.yaml", "mvp-01-software-doc-service.yaml"))
      .toBe("mvp-02-automotive-ecu.yaml");
    expect(savedViewFile(undefined, "mvp-03-hierarchical-system.yaml"))
      .toBe("mvp-03-hierarchical-system.yaml");
    expect(savedViewFile()).toBe("mvp-01-software-doc-service.yaml");
  });

  it("lists the model's views, then proposed ones marked proposed in the label", async () => {
    const { panel, elements } = harness();
    await panel.load();
    const labels = elements.select.children.map((c) => c.textContent);
    expect(labels[0]).toBe("All loaded objects");
    expect(labels).toContain("Papermill attack-path graph");
    expect(labels).toContain("Proposed: XXE threat and its path (not reviewed)");
    expect(elements.select.disabled).toBe(false);
    expect(elements.status.textContent).toContain("hypotheses until the sponsor accepts them");
  });

  it("focuses the graph on a view's objects and reports its review state", async () => {
    const { panel, elements, focused } = harness();
    await panel.load();
    const proposed = DATA.views.find((v) => v.state === "proposed") as SavedView;
    elements.select.value = proposed.id;
    await elements.select.onchange?.();
    await settle();
    expect(focused[focused.length - 1]).toEqual(proposed.node_ids);
    expect(elements.status.textContent).toContain("Proposed: proposed, not accepted");
    expect(elements.status.textContent).toContain(proposed.proposal as string);
    expect(elements.status.classList.contains("is-unreviewed")).toBe(true);
    expect(elements.clear.disabled).toBe(false);
    await elements.clear.onclick?.();
    await settle();
    expect(focused[focused.length - 1]).toBeUndefined();
    expect(elements.clear.disabled).toBe(true);
  });

  it("lists pending proposals with a Proposed chip, edits and removals included", async () => {
    const { panel, elements } = harness();
    await panel.load();
    expect(elements.summary.textContent).toBe(`Pending proposals (${DATA.proposals.length})`);
    const item = elements.list.children[0];
    expect(item.children[0].className).toBe("review-chip review-proposed");
    expect(item.children[0].textContent).toBe("Proposed");
    expect(item.children[1].textContent).toContain("edit component:render-worker (description)");
    expect(item.children[1].textContent).toContain("mitigates → threat-instance:xxe-file-read");
  });

  it("keeps the graph usable when GET /proposals fails", async () => {
    const { panel, elements } = harness(undefined, true);
    await panel.load();
    expect(elements.select.disabled).toBe(true);
    expect(elements.status.textContent).toContain("Saved views unavailable: boom");
  });

  it("does not let an older model's pending response reclaim the shared toolbar", async () => {
    let resolve!: (data: ProposalsResponse) => void;
    const provider: ProposalsDataProvider = {
      getProposals: () => new Promise((done) => { resolve = done; }),
    };
    const { panel, elements } = harness(DATA, false, provider);
    const loading = panel.load();
    panel.dispose();
    resolve(DATA);
    await loading;
    expect(elements.select.disabled).toBe(true);
    expect(elements.select.children.map((child) => child.textContent)).toEqual(["No saved views"]);
    expect(elements.summary.textContent).toBe("Pending proposals (0)");
    expect(elements.list.children).toHaveLength(0);
  });

  it("dims what is outside the view", () => {
    const p = savedViewPresentation({
      nodes: [node("a"), node("b"), node("c")],
      edges: [edge("a", "b"), edge("b", "c")],
    }, ["a", "b"]);
    expect(p.memberNodeIds).toEqual(["a", "b"]);
    expect(p.dimmedNodeIds).toEqual(["c"]);
    expect(p.dimmedEdgeIds).toEqual(["b->c"]);
  });

  it("labels a proposed removal", () => {
    const view = { ...DATA.views[0], state: "proposed_removal" as const };
    expect(savedViewLabel(view)).toBe("Papermill attack-path graph (removal proposed)");
  });
});

describe("engine proposals provider", () => {
  it("asks GET /proposals for a model name, never a path", async () => {
    const seen: URL[] = [];
    const provider = new EngineProposalsDataProvider("http://127.0.0.1:47811/", (async (input: RequestInfo | URL) => {
      seen.push(new URL(String(input)));
      return new Response(JSON.stringify(fixture), { status: 200 });
    }) as typeof fetch);
    const data = await provider.getProposals("/Users/x/spec/vectors/mvp-01-software-doc-service.yaml");
    expect(seen[0].pathname).toBe("/proposals");
    expect(seen[0].searchParams.get("file")).toBe("mvp-01-software-doc-service.yaml");
    expect(data.views.length).toBe(DATA.views.length);
  });

  it("surfaces the engine's error and refuses an unexpected payload", async () => {
    const failing = new EngineProposalsDataProvider(undefined, (async () =>
      new Response(JSON.stringify({ error: "x.yaml: not a model file" }), { status: 400 })) as typeof fetch);
    await expect(failing.getProposals("x.yaml")).rejects.toThrow("not a model file");
    expect(() => parseProposals({ file: "x", proposals: [], views: [{ id: 1 }] })).toThrow("unexpected");
  });
});

function harness(
  data: ProposalsResponse = DATA,
  fail = false,
  provider?: ProposalsDataProvider,
) {
  const focused: (readonly string[] | undefined)[] = [];
  const doc = { createElement: (tag: string) => new FakeElement(tag) } as unknown as Document;
  const elements = {
    select: new FakeElement("select"),
    clear: new FakeElement("button"),
    status: new FakeElement("span"),
    summary: new FakeElement("summary"),
    list: new FakeElement("ul"),
  };
  const panel = new SavedViewsPanel(
    provider ?? { getProposals: async () => { if (fail) throw new Error("boom"); return data; } },
    "mvp-01-software-doc-service.yaml",
    elements as unknown as SavedViewElements,
    async (ids) => { focused.push(ids); },
    doc,
  );
  return { panel, elements, focused };
}

class FakeElement {
  readonly children: FakeElement[] = [];
  textContent = "";
  className = "";
  value = "";
  disabled = false;
  onchange?: () => unknown;
  onclick?: () => unknown;
  private readonly classes = new Set<string>();
  readonly classList = {
    add: (...names: string[]) => names.forEach((n) => this.classes.add(n)),
    contains: (name: string) => this.classes.has(name),
  };
  constructor(readonly tagName: string) {}
  append(...nodes: FakeElement[]): void { this.children.push(...nodes); }
  replaceChildren(...nodes: FakeElement[]): void { this.children.length = 0; this.children.push(...nodes); }
}

function node(id: string) {
  return { id, domainType: "Component", label: id, properties: {} };
}

function edge(source: string, target: string) {
  return { id: `${source}->${target}`, source, target, relationshipType: "uses", properties: {} };
}

async function settle(): Promise<void> {
  for (let i = 0; i < 5; i += 1) await Promise.resolve();
}
