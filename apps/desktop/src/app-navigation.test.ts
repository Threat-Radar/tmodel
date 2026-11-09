import { describe, expect, it, vi } from "vitest";
import { AppNavigation, type AppView } from "./app-navigation";
import type { EngineState } from "./engine";
import { GraphStartup } from "./graph-startup";

const VIEWS: readonly AppView[] = ["library", "graph", "sdl"];

describe("application navigation", () => {
  it("defaults to Library and initializes each view only when selected", () => {
    const harness = navigationHarness("");
    harness.navigation.start();
    expect(harness.panel("library").hidden).toBe(false);
    for (const view of ["graph", "sdl"] as const) {
      expect(harness.panel(view).hidden).toBe(true);
      expect(harness.activated(view)).not.toHaveBeenCalled();
    }
    expect(harness.activated("library")).toHaveBeenCalledTimes(1);

    harness.button("sdl").click();
    expect(harness.panel("sdl").hidden).toBe(false);
    expect(harness.panel("library").hidden).toBe(true);
    expect(harness.activated("sdl")).toHaveBeenCalledTimes(1);
    expect(harness.location.hash).toBe("#sdl");

    harness.button("graph").click();
    harness.button("sdl").click();
    expect(harness.activated("sdl")).toHaveBeenCalledTimes(2);
    expect(harness.activated("graph")).toHaveBeenCalledTimes(1);
  });

  it("starts in the view the URL hash names, and in Library for an unknown hash", () => {
    const sdl = navigationHarness("#sdl");
    sdl.navigation.start();
    expect(sdl.panel("sdl").hidden).toBe(false);
    expect(sdl.button("sdl").getAttribute("aria-selected")).toBe("true");
    expect(sdl.navigation.currentView).toBe("sdl");

    const unknown = navigationHarness("#nope");
    unknown.navigation.start();
    expect(unknown.panel("library").hidden).toBe(false);
  });

  it("does not reactivate when the active tab is clicked again", () => {
    const harness = navigationHarness("");
    harness.navigation.start();
    harness.button("library").click();
    harness.button("library").click();
    expect(harness.activated("library")).toHaveBeenCalledTimes(1);
  });

  it("moves focus and activates tabs with Arrow keys, Home, and End", () => {
    const harness = navigationHarness("");
    harness.navigation.start();
    harness.button("library").keydown("ArrowRight");
    expect(harness.button("graph").focused).toBe(true);
    expect(harness.button("graph").tabIndex).toBe(0);
    expect(harness.button("library").tabIndex).toBe(-1);
    harness.button("graph").keydown("End");
    expect(harness.panel("sdl").hidden).toBe(false);
    harness.button("sdl").keydown("ArrowRight");
    expect(harness.panel("library").hidden).toBe(false);
    harness.button("library").keydown("ArrowLeft");
    expect(harness.button("sdl").focused).toBe(true);
    harness.button("sdl").keydown("Home");
    expect(harness.button("library").focused).toBe(true);
  });

  it("synchronizes Back and Forward hash changes without writing another hash", () => {
    const harness = navigationHarness("#library");
    harness.navigation.start();
    harness.hashEvents.navigate("#sdl");
    expect(harness.panel("sdl").hidden).toBe(false);
    expect(harness.location.hash).toBe("#sdl");
    harness.hashEvents.navigate("#sdl");
    expect(harness.activated("sdl")).toHaveBeenCalledTimes(1);
  });

  it("starts the graph only once and resizes it across repeated view switches", async () => {
    const start = vi.fn(async () => undefined);
    const resize = vi.fn();
    const startup = new GraphStartup({ start, onWaiting: vi.fn(), onFailure: vi.fn() }, false);
    const harness = navigationHarness("", {
      graph: () => {
        if (startup.started) resize();
        else void startup.startNow();
      },
    });
    harness.navigation.start();
    harness.button("graph").click();
    await settle();
    harness.button("library").click();
    harness.button("graph").click();
    harness.button("sdl").click();
    harness.button("graph").click();
    expect(start).toHaveBeenCalledTimes(1);
    expect(resize).toHaveBeenCalledTimes(2);
  });

  it("starts a visible graph when the engine recovers after startup", async () => {
    const start = vi.fn(async () => undefined);
    const startup = new GraphStartup({ start, onWaiting: vi.fn(), onFailure: vi.fn() });
    let engineState: EngineState = { kind: "unreachable", error: "connection refused" };
    const harness = navigationHarness("", {
      graph: () => void startup.engineStateChanged(engineState),
    });
    harness.navigation.start();
    harness.button("graph").click();
    await settle();
    expect(start).not.toHaveBeenCalled();
    engineState = { kind: "connected", health: { status: "ok", engine: "tmodel", version: "0.1.0" } };
    await startup.engineStateChanged(engineState);
    expect(start).toHaveBeenCalledTimes(1);
  });
});

function navigationHarness(
  initialHash: string,
  overrides: Partial<Record<AppView, () => void>> = {},
) {
  const buttons: FakeButton[] = [];
  const entries = VIEWS.map((view, index) => {
    const button = new FakeButton(buttons);
    buttons.push(button);
    return {
      view,
      button,
      panel: { hidden: index !== 0 } as HTMLElement,
      spy: vi.fn(),
    };
  });
  const location = { hash: initialHash };
  const hashEvents = new FakeHashEvents(location);
  const navigation = new AppNavigation(entries.map((entry) => ({
    view: entry.view,
    button: entry.button as unknown as HTMLButtonElement,
    panel: entry.panel,
    activated: () => {
      entry.spy();
      overrides[entry.view]?.();
    },
  })), location as Location, hashEvents);
  const find = (view: AppView) => entries.find((entry) => entry.view === view) as (typeof entries)[number];
  return {
    navigation,
    button: (view: AppView) => find(view).button,
    panel: (view: AppView) => find(view).panel,
    activated: (view: AppView) => find(view).spy,
    location,
    hashEvents,
  };
}

class FakeButton {
  tabIndex = 0;
  focused = false;
  private readonly attributes = new Map<string, string>();
  private readonly listeners = new Map<string, Array<(event: Event) => void>>();

  constructor(private readonly group: readonly FakeButton[]) {}

  addEventListener(type: string, listener: EventListenerOrEventListenerObject): void {
    const callbacks = this.listeners.get(type) ?? [];
    callbacks.push((event) => typeof listener === "function"
      ? listener(event)
      : listener.handleEvent(event));
    this.listeners.set(type, callbacks);
  }

  click(): void {
    this.dispatch(new Event("click"));
  }

  keydown(key: string): void {
    const event = new Event("keydown", { cancelable: true });
    Object.defineProperty(event, "key", { value: key });
    this.dispatch(event);
  }

  focus(): void {
    for (const button of this.group) button.focused = false;
    this.focused = true;
  }

  setAttribute(name: string, value: string): void {
    this.attributes.set(name, value);
  }

  getAttribute(name: string): string | null {
    return this.attributes.get(name) ?? null;
  }

  private dispatch(event: Event): void {
    for (const listener of this.listeners.get(event.type) ?? []) listener(event);
  }
}

class FakeHashEvents extends EventTarget {
  constructor(private readonly location: { hash: string }) {
    super();
  }

  navigate(hash: string): void {
    this.location.hash = hash;
    this.dispatchEvent(new Event("hashchange"));
  }
}

async function settle(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
}
