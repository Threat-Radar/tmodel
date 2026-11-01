import { describe, expect, it, vi } from "vitest";
import { AppNavigation } from "./app-navigation";
import type { EngineState } from "./engine";
import { GraphStartup } from "./graph-startup";

describe("application navigation", () => {
  it("defaults to Library and initializes each view only when selected", () => {
    const harness = navigationHarness("");

    harness.navigation.start();
    expect(harness.libraryPanel.hidden).toBe(false);
    expect(harness.graphPanel.hidden).toBe(true);
    expect(harness.libraryActivated).toHaveBeenCalledTimes(1);
    expect(harness.graphActivated).not.toHaveBeenCalled();

    harness.graphButton.click();
    expect(harness.graphPanel.hidden).toBe(false);
    expect(harness.graphActivated).toHaveBeenCalledTimes(1);
    expect(harness.location.hash).toBe("#graph");

    harness.libraryButton.click();
    harness.graphButton.click();
    expect(harness.graphActivated).toHaveBeenCalledTimes(2);
    expect(harness.libraryActivated).toHaveBeenCalledTimes(2);
  });

  it("starts in the graph only when the URL hash requests it", () => {
    const harness = navigationHarness("#graph");

    harness.navigation.start();

    expect(harness.graphPanel.hidden).toBe(false);
    expect(harness.libraryPanel.hidden).toBe(true);
    expect(harness.graphActivated).toHaveBeenCalledTimes(1);
    expect(harness.graphButton.getAttribute("aria-selected")).toBe("true");
  });

  it("does not reactivate or duplicate initialization when the active tab is clicked again", () => {
    const harness = navigationHarness("");
    harness.navigation.start();

    harness.libraryButton.click();
    harness.libraryButton.click();

    expect(harness.libraryActivated).toHaveBeenCalledTimes(1);
  });

  it("moves focus and activates tabs with Arrow keys, Home, and End", () => {
    const harness = navigationHarness("");
    harness.navigation.start();

    harness.libraryButton.keydown("ArrowRight");
    expect(harness.graphButton.focused).toBe(true);
    expect(harness.graphButton.getAttribute("aria-selected")).toBe("true");
    expect(harness.graphButton.tabIndex).toBe(0);
    expect(harness.libraryButton.tabIndex).toBe(-1);
    expect(harness.graphPanel.hidden).toBe(false);

    harness.graphButton.keydown("ArrowRight");
    expect(harness.libraryButton.focused).toBe(true);
    expect(harness.libraryPanel.hidden).toBe(false);

    harness.libraryButton.keydown("End");
    expect(harness.graphButton.focused).toBe(true);
    expect(harness.graphPanel.hidden).toBe(false);

    harness.graphButton.keydown("Home");
    expect(harness.libraryButton.focused).toBe(true);
    expect(harness.libraryPanel.hidden).toBe(false);

    harness.libraryButton.keydown("ArrowLeft");
    expect(harness.graphButton.focused).toBe(true);
    expect(harness.graphPanel.hidden).toBe(false);
  });

  it("synchronizes Back and Forward hash changes without writing another hash", () => {
    const harness = navigationHarness("#library");
    harness.navigation.start();
    harness.graphButton.click();
    harness.libraryButton.click();

    harness.hashEvents.navigate("#graph");
    expect(harness.graphPanel.hidden).toBe(false);
    expect(harness.graphButton.getAttribute("aria-selected")).toBe("true");
    expect(harness.location.hash).toBe("#graph");
    expect(harness.graphActivated).toHaveBeenCalledTimes(2);

    harness.hashEvents.navigate("#graph");
    expect(harness.graphActivated).toHaveBeenCalledTimes(2);

    harness.hashEvents.navigate("#library");
    expect(harness.libraryPanel.hidden).toBe(false);
    expect(harness.libraryButton.getAttribute("aria-selected")).toBe("true");
    expect(harness.location.hash).toBe("#library");
    expect(harness.libraryActivated).toHaveBeenCalledTimes(3);
  });

  it("starts the graph only once and resizes it across repeated view switches", async () => {
    const start = vi.fn(async () => undefined);
    const resize = vi.fn();
    const startup = new GraphStartup({
      start,
      onWaiting: vi.fn(),
      onFailure: vi.fn(),
    }, false);
    const harness = navigationHarness("", {
      graphActivated: () => {
        if (startup.started) resize();
        else void startup.startNow();
      },
    });
    harness.navigation.start();

    harness.graphButton.click();
    await settle();
    harness.libraryButton.click();
    harness.graphButton.click();
    harness.libraryButton.click();
    harness.graphButton.click();

    expect(start).toHaveBeenCalledTimes(1);
    expect(resize).toHaveBeenCalledTimes(2);
  });

  it("starts a visible graph when the engine recovers after startup", async () => {
    const start = vi.fn(async () => undefined);
    const startup = new GraphStartup({
      start,
      onWaiting: vi.fn(),
      onFailure: vi.fn(),
    });
    let engineState: EngineState = { kind: "unreachable", error: "connection refused" };
    const harness = navigationHarness("", {
      graphActivated: () => void startup.engineStateChanged(engineState),
    });
    harness.navigation.start();
    harness.graphButton.click();
    await settle();
    expect(start).not.toHaveBeenCalled();

    engineState = {
      kind: "connected",
      health: { status: "ok", engine: "tmodel", version: "0.1.0" },
    };
    await startup.engineStateChanged(engineState);

    expect(start).toHaveBeenCalledTimes(1);
    expect(startup.started).toBe(true);
  });
});

function navigationHarness(
  initialHash: string,
  callbackOverrides: Partial<{ libraryActivated(): void; graphActivated(): void }> = {},
) {
  const buttons: FakeButton[] = [];
  const libraryButton = new FakeButton(buttons);
  const graphButton = new FakeButton(buttons);
  buttons.push(libraryButton, graphButton);
  const libraryPanel = { hidden: false } as HTMLElement;
  const graphPanel = { hidden: true } as HTMLElement;
  const libraryActivated = vi.fn();
  const graphActivated = vi.fn();
  const location = { hash: initialHash };
  const hashEvents = new FakeHashEvents(location);
  const navigation = new AppNavigation({
    libraryButton: libraryButton as unknown as HTMLButtonElement,
    graphButton: graphButton as unknown as HTMLButtonElement,
    libraryPanel,
    graphPanel,
  }, {
    libraryActivated: callbackOverrides.libraryActivated ?? libraryActivated,
    graphActivated: callbackOverrides.graphActivated ?? graphActivated,
  }, location as Location, hashEvents);
  return {
    navigation,
    libraryButton,
    graphButton,
    libraryPanel,
    graphPanel,
    libraryActivated,
    graphActivated,
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
