export type AppView = "library" | "graph";

export interface NavigationElements {
  libraryButton: HTMLButtonElement;
  graphButton: HTMLButtonElement;
  libraryPanel: HTMLElement;
  graphPanel: HTMLElement;
}

export interface NavigationCallbacks {
  libraryActivated(): void;
  graphActivated(): void;
}

export class AppNavigation {
  private current?: AppView;
  private readonly tabs: readonly (readonly [AppView, HTMLButtonElement])[];

  constructor(
    private readonly elements: NavigationElements,
    private readonly callbacks: NavigationCallbacks,
    private readonly location: Pick<Location, "hash"> = window.location,
    hashEvents: Pick<EventTarget, "addEventListener"> = window,
  ) {
    this.tabs = [
      ["library", elements.libraryButton],
      ["graph", elements.graphButton],
    ];
    for (const [index, [view, button]] of this.tabs.entries()) {
      button.addEventListener("click", () => this.activate(view));
      button.addEventListener("keydown", (event) => this.handleTabKey(event, index));
    }
    hashEvents.addEventListener("hashchange", () => this.activate(viewForHash(this.location.hash), false));
  }

  start(): void {
    this.activate(viewForHash(this.location.hash), false);
  }

  activate(view: AppView, updateHash = true): void {
    const changed = this.current !== view;
    this.current = view;
    const libraryActive = view === "library";
    this.elements.libraryPanel.hidden = !libraryActive;
    this.elements.graphPanel.hidden = libraryActive;
    setTabState(this.elements.libraryButton, libraryActive);
    setTabState(this.elements.graphButton, !libraryActive);
    if (updateHash) this.location.hash = `#${view}`;
    if (!changed) return;
    if (libraryActive) this.callbacks.libraryActivated();
    else this.callbacks.graphActivated();
  }

  private handleTabKey(event: KeyboardEvent, currentIndex: number): void {
    let nextIndex: number | undefined;
    if (event.key === "ArrowRight") nextIndex = (currentIndex + 1) % this.tabs.length;
    else if (event.key === "ArrowLeft") nextIndex = (currentIndex - 1 + this.tabs.length) % this.tabs.length;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = this.tabs.length - 1;
    if (nextIndex === undefined) return;
    event.preventDefault();
    const [view, button] = this.tabs[nextIndex];
    this.activate(view);
    button.focus();
  }
}

function viewForHash(hash: string): AppView {
  return hash === "#graph" ? "graph" : "library";
}

function setTabState(button: HTMLButtonElement, active: boolean): void {
  button.setAttribute("aria-selected", String(active));
  button.tabIndex = active ? 0 : -1;
}
