// Application tabs, synchronized with the URL hash.
// The Model Report is the default view.
export type AppView = "report" | "paths" | "graph" | "library" | "sdl";

export interface NavigationView {
  view: AppView;
  button: HTMLButtonElement;
  panel: HTMLElement;
  /** Called each time the view becomes the active one. */
  activated(): void;
}

export class AppNavigation {
  private current?: AppView;

  constructor(
    private readonly views: readonly NavigationView[],
    private readonly location: Pick<Location, "hash"> = window.location,
    hashEvents: Pick<EventTarget, "addEventListener"> = window,
  ) {
    if (views.length === 0) throw new Error("AppNavigation needs at least one view");
    for (const [index, { view, button }] of views.entries()) {
      button.addEventListener("click", () => this.activate(view));
      button.addEventListener("keydown", (event) => this.handleTabKey(event, index));
    }
    hashEvents.addEventListener("hashchange", () => this.activate(this.viewForHash(this.location.hash), false));
  }

  get currentView(): AppView | undefined {
    return this.current;
  }

  start(): void {
    this.activate(this.viewForHash(this.location.hash), false);
  }

  activate(view: AppView, updateHash = true): void {
    const target = this.views.find((candidate) => candidate.view === view) ?? this.views[0];
    const changed = this.current !== target.view;
    this.current = target.view;
    for (const candidate of this.views) {
      const active = candidate === target;
      candidate.panel.hidden = !active;
      setTabState(candidate.button, active);
    }
    if (updateHash) this.location.hash = `#${target.view}`;
    if (changed) target.activated();
  }

  private viewForHash(hash: string): AppView {
    const requested = hash.replace(/^#/, "");
    return this.views.find((candidate) => candidate.view === requested)?.view ?? this.views[0].view;
  }

  private handleTabKey(event: KeyboardEvent, currentIndex: number): void {
    const count = this.views.length;
    let nextIndex: number | undefined;
    if (event.key === "ArrowRight") nextIndex = (currentIndex + 1) % count;
    else if (event.key === "ArrowLeft") nextIndex = (currentIndex - 1 + count) % count;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = count - 1;
    if (nextIndex === undefined) return;
    event.preventDefault();
    const { view, button } = this.views[nextIndex];
    this.activate(view);
    button.focus();
  }
}

function setTabState(button: HTMLButtonElement, active: boolean): void {
  button.setAttribute("aria-selected", String(active));
  button.tabIndex = active ? 0 : -1;
}
