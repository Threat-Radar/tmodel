// Read-only SDL view (DL-0043): one SDL model from the engine's GET /sdl, shown as the
// same sections as the "tmodel SDL" page. Selections show their review state with the
// app's review-status rules; nothing here can accept or change anything (PROC-0002).
import type { EngineState } from "./engine";
import { LatestRequestGuard } from "./request-guard";
import { reviewStatePresentation } from "./review-status";
import type { SdlDataProvider, SdlDecision, SdlLink, SdlModel, SdlView } from "./sdl-types";

export interface SdlViewElements {
  modelSelect: HTMLSelectElement;
  status: HTMLElement;
  content: HTMLElement;
}

type Doc = Pick<Document, "createElement">;

export const STATUS_LABELS: Readonly<Record<string, string>> = {
  complete: "Done",
  in_progress: "In progress",
  planned: "Gap / planned",
  accepted_risk: "Risk accepted",
  not_applicable: "Not applicable",
};

export function sdlViewElements(): SdlViewElements {
  const get = <T extends HTMLElement>(id: string): T => {
    const element = document.getElementById(id);
    if (!element) throw new Error(`Missing required SDL element #${id}`);
    return element as T;
  };
  return { modelSelect: get("sdl-model-select"), status: get("sdl-status"), content: get("sdl-content") };
}

/** A model-select option value: `file` or `file#program`. */
export function modelOptions(models: readonly SdlModel[]): { value: string; label: string }[] {
  const options: { value: string; label: string }[] = [];
  for (const model of models) {
    if (model.error) continue;
    const programs = model.programs ?? [];
    if (programs.length <= 1) options.push({ value: model.file, label: programs[0]?.name ?? model.file });
    else for (const p of programs) options.push({ value: `${model.file}#${p.id}`, label: `${p.name} (${model.file})` });
  }
  return options;
}

/** Only absolute http(s) links are rendered as links; anything else is text. */
export function safeHref(href: string | undefined | null): string | undefined {
  if (!href) return undefined;
  try {
    const url = new URL(href);
    return url.protocol === "https:" || url.protocol === "http:" ? url.href : undefined;
  } catch {
    return undefined;
  }
}

export class SdlProgramView {
  private readonly guard = new LatestRequestGuard();
  private loaded = false;

  constructor(
    private readonly provider: SdlDataProvider,
    private readonly elements: SdlViewElements,
    private readonly doc: Doc = document,
  ) {
    elements.modelSelect.addEventListener("change", () => void this.showSelected());
  }

  activate(): void {
    if (!this.loaded) void this.load();
  }

  async engineStateChanged(state: EngineState): Promise<void> {
    if (state.kind === "connected" && !this.loaded) await this.load();
  }

  async load(): Promise<void> {
    const request = this.guard.begin();
    this.elements.status.textContent = "Loading SDL models…";
    try {
      const models = await this.provider.listModels(request.signal);
      if (!this.guard.isCurrent(request)) return;
      const options = modelOptions(models);
      this.elements.modelSelect.replaceChildren(...options.map((o) => {
        const option = this.doc.createElement("option");
        option.value = o.value;
        option.textContent = o.label;
        return option;
      }));
      this.loaded = true;
      if (options.length === 0) {
        this.elements.status.textContent = "No SDL models found (spec/vectors/sdl-*.yaml).";
        return;
      }
      this.elements.modelSelect.value = options[0].value;
      await this.showSelected();
    } catch (error) {
      if (this.guard.isCurrent(request)) this.elements.status.textContent = `Unable to load SDL models: ${message(error)}`;
    } finally {
      this.guard.complete(request);
    }
  }

  async showSelected(): Promise<void> {
    const [file, program] = this.elements.modelSelect.value.split("#");
    if (!file) return;
    const request = this.guard.begin();
    this.elements.status.textContent = `Loading ${file}…`;
    try {
      const view = await this.provider.getView(file, program, request.signal);
      if (!this.guard.isCurrent(request)) return;
      this.render(view);
      this.elements.status.textContent = `${view.awaiting_review.length} selections awaiting human review · ${view.proposal}`;
    } catch (error) {
      if (this.guard.isCurrent(request)) {
        this.elements.content.replaceChildren();
        this.elements.status.textContent = `Unable to load ${file}: ${message(error)}`;
      }
    } finally {
      this.guard.complete(request);
    }
  }

  render(view: SdlView): void {
    const e = this.el.bind(this);
    const sections: HTMLElement[] = [];
    sections.push(e("section", "sdl-summary", [
      e("h2", "", view.program.name),
      e("p", "sdl-product", `${view.product.name}: ${view.product.description}`),
      e("p", "sdl-banner", "Example data, draft. Every selection is a proposal until a human Review accepts it (PROC-0002). Not a conformance claim."),
    ]));

    sections.push(this.table("Governing requirement sets", ["Set", "Proposal", "Why", "Decision"],
      view.sets.map((s) => [this.link({ name: s.name, href: s.link }), s.proposal, s.rationale, this.decision(s.decision)])));

    for (const phase of view.phases) {
      sections.push(this.table(phase.name, ["Practice", "Status", "Owner", "Evidence", "Selection"],
        phase.items.map((it) => [
          e("div", "", [e("strong", "", it.name), e("div", "sdl-small", `MAP-0001 row ${it.row_n}: ${it.row}`),
            ...(it.due.length ? [e("div", "sdl-small", `due: ${it.due.join(", ")}`)] : [])]),
          e("span", `sdl-status sdl-status-${it.status}`, STATUS_LABELS[it.status] ?? it.status),
          it.owner,
          e("ul", "sdl-links", it.evidence.map((ev) => e("li", "", [this.link(ev)]))),
          this.decision(it.decision),
        ]), "sdl-phase"));
    }

    sections.push(this.table("Milestones and gates", ["#", "Name", "Kind", "Planned", "Status", "Practices due", "Name review"],
      view.nodes.map((n) => [String(n.order ?? ""), n.name, n.kind, n.actual ? `${n.planned} / ${n.actual}` : n.planned,
        n.status, String(n.practices), n.name_decision ? this.decision(n.name_decision) : "—"])));

    sections.push(e("section", "sdl-gaps", [e("h3", "", "Open gaps"), e("ul", "", view.gaps.map((g) => e("li", "", g)))]));
    this.elements.content.replaceChildren(...sections);
  }

  private table(title: string, headers: string[], rows: (string | HTMLElement)[][], cls = ""): HTMLElement {
    const e = this.el.bind(this);
    const head = e("tr", "", headers.map((h) => e("th", "", h)));
    const body = rows.map((cells) => e("tr", "", cells.map((c) => e("td", "", [c]))));
    return e("section", `sdl-section ${cls}`.trim(), [e("h3", "", title),
      e("table", "sdl-table", [e("thead", "", [head]), e("tbody", "", body)])]);
  }

  private decision(d: SdlDecision): HTMLElement {
    const p = reviewStatePresentation(d.state, d.state === "proposed" ? null : d.state);
    const chip = this.el("span", `review-chip review-${p.kind}`, p.label);
    chip.setAttribute("title", d.label + (d.why ? `: ${d.why}` : ""));
    return chip;
  }

  private link(l: SdlLink): HTMLElement {
    const href = safeHref(l.href);
    if (!href) return this.el("span", "", l.name);
    const a = this.el("a", "", l.name);
    a.setAttribute("href", href);
    a.setAttribute("target", "_blank");
    a.setAttribute("rel", "noopener noreferrer");
    return a;
  }

  private el(tag: string, className: string, content?: string | (string | HTMLElement)[]): HTMLElement {
    const node = this.doc.createElement(tag);
    if (className) node.className = className;
    if (typeof content === "string") node.textContent = content;
    else if (content) {
      for (const child of content) {
        if (typeof child === "string") {
          const span = this.doc.createElement("span");
          span.textContent = child;
          node.append(span);
        } else node.append(child);
      }
    }
    return node;
  }
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
