import { describe, expect, it, vi } from "vitest";
import { AppNavigation } from "./app-navigation";
import { syncModelUrl } from "./model-catalog";
import type { ModelListResponse, ModelSummary } from "./model-types";
import {
  configurePreviewChrome,
  openInitialModel,
  PREVIEW_MODEL_WAITING,
  PREVIEW_REPORT_WAITING,
} from "./preview-bootstrap";

const model = (id: string): ModelSummary => ({
  id,
  file: `${id}.yaml`,
  title: id,
  description: null,
  kind: "core",
  kind_label: "Core example",
  counts: { threats: 1, attack_paths: 1 },
  reviewed_threats: 0,
});

const MVP_01 = model("mvp-01-software-doc-service");
const MVP_02 = model("mvp-02-automotive-ecu");

describe("browser preview bootstrap smoke", () => {
  it("shows preview chrome, keeps Library available, and hides unsupported features", () => {
    const element = (hidden = false) => ({ hidden });
    const elements = {
      body: { dataset: {} as DOMStringMap },
      banner: element(true),
      enginePanel: element(),
      sdlTab: element(),
      sdlPanel: element(),
      proposals: element(),
      savedViews: element(),
      libraryTab: element(true),
      modelSelect: { disabled: false, options: [{ textContent: "Waiting for the local engine…" }] },
      modelStatus: { textContent: "" },
      reportStatus: { textContent: "Waiting for the local engine…" },
    };

    configurePreviewChrome(
      elements as unknown as Parameters<typeof configurePreviewChrome>[0],
    );

    expect(elements.banner.hidden).toBe(false);
    expect(elements.enginePanel.hidden).toBe(true);
    expect(elements.sdlTab.hidden).toBe(true);
    expect(elements.sdlPanel.hidden).toBe(true);
    expect(elements.proposals.hidden).toBe(true);
    expect(elements.savedViews.hidden).toBe(true);
    expect(elements.libraryTab.hidden).toBe(false);
    expect(elements.body.dataset.appMode).toBe("browser-preview");
    expect(elements.modelSelect.options[0].textContent).toBe(PREVIEW_MODEL_WAITING);
    expect(elements.modelStatus.textContent).toBe(PREVIEW_MODEL_WAITING);
    expect(elements.reportStatus.textContent).toBe(PREVIEW_REPORT_WAITING);
  });

  it("waits for a delayed catalog before creating the direct-linked graph", async () => {
    const delayed = deferred<ModelListResponse>();
    const requestedFiles: string[] = [];
    const history = { replaceState: vi.fn() };
    const startup = openInitialModel({
      catalog: { listModels: () => delayed.promise },
      requested: MVP_02.id,
      remembered: MVP_01.file,
      setModels: vi.fn(),
      notice: vi.fn(),
      empty: vi.fn(),
      open: async (selected) => {
        // ModelSession.open constructs every model-dependent view before its
        // first await; no default graph may be created before this callback.
        requestedFiles.push(selected.file);
        syncModelUrl(
          selected,
          `https://threat-radar.github.io/tmodel/app/?model=${MVP_02.id}#graph`,
          history,
        );
      },
    });

    await Promise.resolve();
    expect(requestedFiles).toEqual([]);
    delayed.resolve({ count: 2, models: [MVP_01, MVP_02], problems: [] });
    await expect(startup).resolves.toEqual(MVP_02);
    expect(requestedFiles).toEqual([MVP_02.file]);
    expect(requestedFiles).not.toContain(MVP_01.file);
    expect(history.replaceState).toHaveBeenCalledWith(
      null,
      "",
      new URL(`https://threat-radar.github.io/tmodel/app/?model=${MVP_02.id}#graph`),
    );
  });

  it("activates Library and synchronizes the view hash", () => {
    const libraryActivated = vi.fn();
    const graphButton = new FakeButton();
    const libraryButton = new FakeButton();
    const location = { hash: "#graph" };
    const navigation = new AppNavigation([
      {
        view: "graph",
        button: graphButton as unknown as HTMLButtonElement,
        panel: { hidden: true } as HTMLElement,
        activated: vi.fn(),
      },
      {
        view: "library",
        button: libraryButton as unknown as HTMLButtonElement,
        panel: { hidden: true } as HTMLElement,
        activated: libraryActivated,
      },
    ], location as Location, { addEventListener: vi.fn() });

    navigation.start();
    libraryButton.click();

    expect(navigation.currentView).toBe("library");
    expect(location.hash).toBe("#library");
    expect(libraryActivated).toHaveBeenCalledTimes(1);
  });
});

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((accept) => { resolve = accept; });
  return { promise, resolve };
}

class FakeButton {
  tabIndex = 0;
  private readonly listeners = new Map<string, Array<(event: KeyboardEvent) => void>>();

  addEventListener(type: string, listener: (event: KeyboardEvent) => void): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  setAttribute(): void {}

  focus(): void {}

  click(): void {
    for (const listener of this.listeners.get("click") ?? []) listener({} as KeyboardEvent);
  }
}
