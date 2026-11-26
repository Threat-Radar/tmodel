import { describe, expect, it, vi } from "vitest";
import fixture from "./fixtures/sdl-01-view.json";
import { modelOptions, safeHref, SdlProgramView, type SdlViewElements } from "./sdl-view";
import type { SdlDataProvider, SdlView } from "./sdl-types";

const VIEW = fixture as unknown as SdlView;

describe("SDL view", () => {
  it("renders the page sections from the engine payload, all selections proposed", async () => {
    const { view, elements } = harness();
    view.activate();
    await settle();

    expect(elements.modelSelect.children).toHaveLength(1);
    expect(elements.status.textContent).toContain(`${VIEW.awaiting_review.length} selections awaiting human review`);
    expect(headings(elements.content)).toEqual([
      VIEW.program.name, "Governing requirement sets", ...VIEW.phases.map((phase) => phase.name),
      "Milestones and gates", "Pending proposals (0)", "Open gaps",
    ]);
    expect(elements.content.children[0].children.map((element) => element.className))
      .toEqual(["", "sdl-product", "sdl-banner"]);
    const tables = find(elements.content, (node) => node.tagName === "table");
    expect(tables.map((table) => table.children[0].children[0].children.map((header) => header.textContent)))
      .toEqual([
        ["Set", "Proposal", "Why", "Decision"],
        ...VIEW.phases.map(() => ["Practice", "Status", "Owner", "Evidence", "Selection"]),
        ["#", "Name", "Kind", "Planned", "Status", "Practices due", "Name review"],
        ["Proposal", "By", "Adds", "Asks", "Review"],
      ]);
    expect(tables.map((table) => table.children[1].children.length)).toEqual([
      VIEW.sets.length, ...VIEW.phases.map((phase) => phase.items.length), VIEW.nodes.length, 0,
    ]);
    expect(find(elements.content, (node) => node.tagName === "button")).toHaveLength(0);
    const chips = find(elements.content, (n) => n.className.startsWith("review-chip"));
    expect(chips.length).toBeGreaterThan(0);
    expect(chips.every((c) => c.className === "review-chip review-proposed")).toBe(true);
    expect(find(elements.content, (n) => n.tagName === "a").every((a) => a.getAttribute("href")?.startsWith("https://"))).toBe(true);
  });

  it("shows an accepted selection as accepted and keeps untrusted text as text", async () => {
    const accepted: SdlView = structuredClone(VIEW);
    accepted.sets[0].decision = { state: "accepted", label: "Accepted by sponsor", by: "sponsor" };
    accepted.sets[0].name = "<img src=x onerror=alert(1)>";
    const { view, elements } = harness(accepted);
    view.activate();
    await settle();
    expect(find(elements.content, (n) => n.className === "review-chip review-accepted")).toHaveLength(1);
    expect(find(elements.content, (n) => n.textContent === "<img src=x onerror=alert(1)>")).toHaveLength(1);
  });

  it("lists pending tmodel propose records as proposed, never accepted", async () => {
    const withProposal: SdlView = structuredClone(VIEW);
    withProposal.proposals = [{
      id: "proposal:20261107T120000Z-abc", state: "proposed", by: "AI agent", at: "2026-11-07T12:00:00Z",
      generated_by: "example agent", rationale: "Add secrets management",
      objects: [{ collection: "sdl_practices", id: "sdl-practice:secrets-management", name: "Keep secrets out" }],
      assertions: [{ id: "assertion:x", predicate: "selects_practice", object: "sdl-practice:secrets-management", name: "" }],
    }];
    const { view, elements } = harness(withProposal);
    view.activate();
    await settle();
    expect(headings(elements.content)).toContain("Pending proposals (1)");
    const section = find(elements.content, (n) => n.className === "sdl-section sdl-proposals")[0];
    const chips = find(section, (n) => n.className.startsWith("review-chip"));
    expect(chips.map((c) => c.className)).toEqual(["review-chip review-proposed"]);
    expect(find(section, (n) => n.textContent === "selects_practice → sdl-practice:secrets-management")).toHaveLength(1);
  });

  it("replaces the sections when the SDL model changes and ignores an earlier response", async () => {
    let resolveEarlier!: (view: SdlView) => void;
    const earlier = new Promise<SdlView>((resolve) => { resolveEarlier = resolve; });
    const newer = structuredClone(VIEW);
    newer.program.name = "Second program";
    const getView = vi.fn<SdlDataProvider["getView"]>(async (_file, program) => {
      if (program === "first") return earlier;
      if (program === "second") return newer;
      return VIEW;
    });
    const { view, elements } = harness(VIEW, false, {
      listModels: async () => [
        { file: VIEW.file },
        { file: "other.yaml", programs: [{ id: "first", name: "First" }, { id: "second", name: "Second" }] },
      ],
      getView,
    });
    view.activate();
    await settle();
    for (const program of ["first", "second"]) {
      elements.modelSelect.value = `other.yaml#${program}`;
      elements.modelSelect.dispatchEvent(new Event("change"));
    }
    await settle();
    expect(getView.mock.calls[1][2]?.aborted).toBe(true);
    expect(headings(elements.content)[0]).toBe("Second program");
    resolveEarlier(VIEW);
    await settle();
    expect(headings(elements.content)[0]).toBe("Second program");
  });

  it("reports an engine error without rendering stale content", async () => {
    const { view, elements } = harness(VIEW, true);
    view.activate();
    await settle();
    expect(elements.status.textContent).toContain("Unable to load sdl-01-tmodel-desktop.yaml: boom");
    expect(elements.content.children).toHaveLength(0);
  });

  it("builds one option per program and refuses non-http links", () => {
    expect(modelOptions([{ file: "a.yaml", programs: [{ id: "p:1", name: "One" }, { id: "p:2", name: "Two" }] },
      { file: "b.yaml", error: "bad" }]).map((o) => o.value)).toEqual(["a.yaml#p:1", "a.yaml#p:2"]);
    expect(safeHref("javascript:alert(1)")).toBeUndefined();
    expect(safeHref("spec/x.yaml")).toBeUndefined();
    expect(safeHref("https://github.com/Threat-Radar/tmodel")).toBe("https://github.com/Threat-Radar/tmodel");
  });
});

function harness(view: SdlView = VIEW, fail = false, overrides: Partial<SdlDataProvider> = {}) {
  const provider: SdlDataProvider = {
    listModels: async () => [{ file: "sdl-01-tmodel-desktop.yaml", programs: [{ id: "security-program:tmodel-sdl", name: "tmodel SDL" }] }],
    getView: async () => {
      if (fail) throw new Error("boom");
      return view;
    },
    ...overrides,
  };
  const doc = { createElement: (tag: string) => new FakeElement(tag) } as unknown as Document;
  const elements = {
    modelSelect: new FakeElement("select"),
    status: new FakeElement("div"),
    content: new FakeElement("div"),
  };
  const sdl = new SdlProgramView(provider, elements as unknown as SdlViewElements, doc);
  return { view: sdl, elements };
}

class FakeElement extends EventTarget {
  readonly children: FakeElement[] = [];
  textContent = "";
  className = "";
  value = "";
  private readonly attributes = new Map<string, string>();
  constructor(readonly tagName: string) { super(); }
  append(...nodes: FakeElement[]): void { this.children.push(...nodes); }
  replaceChildren(...nodes: FakeElement[]): void { this.children.length = 0; this.children.push(...nodes); }
  setAttribute(name: string, value: string): void { this.attributes.set(name, value); }
  getAttribute(name: string): string | null { return this.attributes.get(name) ?? null; }
}

function find(root: FakeElement, match: (node: FakeElement) => boolean): FakeElement[] {
  const out: FakeElement[] = [];
  const visit = (n: FakeElement) => { if (match(n)) out.push(n); n.children.forEach(visit); };
  root.children.forEach(visit);
  return out;
}

function headings(root: FakeElement): string[] {
  return find(root, (n) => n.tagName === "h3" || n.tagName === "h2").map((n) => n.textContent);
}

async function settle(): Promise<void> {
  for (let i = 0; i < 5; i += 1) await Promise.resolve();
}
