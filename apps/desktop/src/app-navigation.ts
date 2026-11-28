// Application tabs, synchronized with the URL hash.
// The Model Report is the default view.
export type AppView = "report" | "paths" | "graph" | "library";
export type LibraryView = "records" | "weaknesses" | "attack-patterns" | "requirements" | "sdl";

// Keep the original hashes so bookmarks and links still open the same table.
const LIBRARY_HASHES: Record<LibraryView, string> = {
  records: "library",
  weaknesses: "weaknesses",
  "attack-patterns": "attack-patterns",
  requirements: "requirements",
  sdl: "sdl",
};

export interface NavigationView {
  view: AppView;
  button: HTMLButtonElement;
  panel: HTMLElement;
  /** Called when this tab or its Library view becomes active. */
  activated(libraryView: LibraryView): void;
}

export class AppNavigation {
  private current?: AppView;
  private libraryView: LibraryView = "records";

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
    hashEvents.addEventListener("hashchange", () => this.syncFromHash());
  }

  get currentView(): AppView | undefined {
    return this.current;
  }

  get currentLibraryView(): LibraryView | undefined {
    return this.current === "library" ? this.libraryView : undefined;
  }

  hasDestination(hash: string): boolean {
    return this.destinationForHash(hash) !== undefined;
  }

  start(): void {
    this.syncFromHash();
  }

  activate(view: AppView): void {
    this.apply(view, "records", true);
  }

  activateLibrary(view: LibraryView): void {
    this.apply("library", view, true);
  }

  private apply(view: AppView, libraryView: LibraryView, updateHash: boolean): void {
    const target = this.views.find((candidate) => candidate.view === view) ?? this.views[0];
    const changed = this.current !== target.view
      || (target.view === "library" && this.libraryView !== libraryView);
    this.current = target.view;
    this.libraryView = libraryView;
    for (const candidate of this.views) {
      const active = candidate === target;
      candidate.panel.hidden = !active;
      setTabState(candidate.button, active);
    }
    const hash = target.view === "library" ? LIBRARY_HASHES[libraryView] : target.view;
    if (updateHash) this.location.hash = `#${hash}`;
    if (changed) target.activated(libraryView);
  }

  private syncFromHash(): void {
    const destination = this.destinationForHash(this.location.hash);
    this.apply(destination?.view ?? this.views[0].view, destination?.libraryView ?? "records", false);
  }

  private destinationForHash(hash: string): { view: AppView; libraryView: LibraryView } | undefined {
    const requested = hash.replace(/^#/, "");
    for (const libraryView of Object.keys(LIBRARY_HASHES) as LibraryView[]) {
      if (LIBRARY_HASHES[libraryView] === requested) return { view: "library", libraryView };
    }
    const view = this.views.find((candidate) => candidate.view === requested)?.view;
    if (view) return { view, libraryView: "records" };
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
