import { describe, expect, it, vi } from "vitest";
import {
  chooseModel,
  EngineModelCatalogProvider,
  MODEL_STORAGE_KEY,
  ModelPicker,
  modelOptionGroups,
  modelSummaryLine,
  readRememberedModel,
  rememberModel,
} from "./model-catalog";
import type { ModelListResponse, ModelSummary } from "./model-types";

const summary = (id: string, kind: string, kind_label: string, title: string): ModelSummary => ({
  id,
  file: `${id}.yaml`,
  title,
  description: null,
  kind,
  kind_label,
  counts: { threats: 2, attack_paths: 2 },
  reviewed_threats: 1,
});

const MODELS: ModelSummary[] = [
  summary("mvp-01-software-doc-service", "core", "Core example", "Papermill Document Service"),
  summary("mvp-02-automotive-ecu", "core", "Core example", "Telematics Control Unit (TCU)"),
  summary("tv-hardware-brake-ecu", "worked", "Worked example with governance", "Brake ECU"),
];

describe("choosing a model", () => {
  it("prefers the URL's model, then the remembered one, then the first listed", () => {
    expect(chooseModel(MODELS, { requested: "mvp-02-automotive-ecu", remembered: "tv-hardware-brake-ecu.yaml" })?.id)
      .toBe("mvp-02-automotive-ecu");
    expect(chooseModel(MODELS, { requested: "mvp-02-automotive-ecu.yaml" })?.id).toBe("mvp-02-automotive-ecu");
    expect(chooseModel(MODELS, { remembered: "tv-hardware-brake-ecu.yaml" })?.id).toBe("tv-hardware-brake-ecu");
    expect(chooseModel(MODELS)?.id).toBe("mvp-01-software-doc-service");
  });

  it("ignores a model the engine does not list instead of guessing", () => {
    expect(chooseModel(MODELS, { requested: "../secrets.yaml", remembered: "gone.yaml" })?.id)
      .toBe("mvp-01-software-doc-service");
    expect(chooseModel([], { requested: "mvp-01-software-doc-service" })).toBeUndefined();
  });

  it("groups picker options by model family in the engine's order", () => {
    expect(modelOptionGroups(MODELS)).toEqual([
      {
        label: "Core example",
        options: [
          { value: "mvp-01-software-doc-service.yaml", label: "Papermill Document Service" },
          { value: "mvp-02-automotive-ecu.yaml", label: "Telematics Control Unit (TCU)" },
        ],
      },
      { label: "Worked example with governance", options: [{ value: "tv-hardware-brake-ecu.yaml", label: "Brake ECU" }] },
    ]);
    expect(modelSummaryLine(MODELS[1])).toBe("Core example · 2 threats, 1 with an accepted review · 2 attack paths");
  });
});

describe("remembering the model", () => {
  it("stores the last model and survives storage that throws", () => {
    const values = new Map<string, string>();
    const storage = { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => void values.set(key, value) };
    rememberModel("mvp-02-automotive-ecu.yaml", storage);
    expect(values.get(MODEL_STORAGE_KEY)).toBe("mvp-02-automotive-ecu.yaml");
    expect(readRememberedModel(storage)).toBe("mvp-02-automotive-ecu.yaml");

    const broken = {
      getItem: () => { throw new Error("SecurityError"); },
      setItem: () => { throw new Error("QuotaExceededError"); },
    };
    expect(() => rememberModel("x.yaml", broken)).not.toThrow();
    expect(readRememberedModel(broken)).toBeNull();
    expect(readRememberedModel(undefined)).toBeNull();
  });
});

describe("engine model list", () => {
  it("asks the engine's /models route", async () => {
    const response: ModelListResponse = { count: MODELS.length, models: MODELS, problems: [] };
    const fetchMock = vi.fn(async () => new Response(JSON.stringify(response), { status: 200 }));
    const provider = new EngineModelCatalogProvider("http://engine.test/", fetchMock as unknown as typeof fetch);
    await expect(provider.listModels()).resolves.toEqual(response);
    expect(String((fetchMock.mock.calls[0] as unknown[])[0])).toBe("http://engine.test/models");
  });

  it("reports the engine's own error message", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ error: "not found" }), { status: 404 }));
    const provider = new EngineModelCatalogProvider("http://engine.test", fetchMock as unknown as typeof fetch);
    await expect(provider.listModels()).rejects.toThrow("Engine request failed: not found");
  });
});

describe("model picker", () => {
  it("lists models as text, reports load problems and calls back on a change", () => {
    const changed = vi.fn();
    const select = new FakeElement("select") as FakeElement & { value: string; disabled: boolean };
    const status = new FakeElement("p");
    const picker = new ModelPicker(
      select as unknown as HTMLSelectElement,
      status as unknown as HTMLElement,
      changed,
      { createElement: (tag: string) => new FakeElement(tag) } as unknown as Document,
    );
    const hostile = { ...MODELS[0], title: "<img src=x onerror=alert(1)>" };
    picker.setModels({ count: 3, models: [hostile, ...MODELS.slice(1)], problems: [{ file: "bad.yaml", error: "bad" }] });

    expect(select.children.map((group) => group.label)).toEqual(["Core example", "Worked example with governance"]);
    expect(select.children[0].children[0].textContent).toBe("<img src=x onerror=alert(1)>");
    expect(select.children[0].children[0].innerHTML).toBeUndefined();
    expect(select.disabled).toBe(false);
    expect(status.textContent).toBe("Could not load: bad.yaml (bad)");

    picker.show(MODELS[1]);
    expect(select.value).toBe("mvp-02-automotive-ecu.yaml");
    expect(status.textContent).toContain("Core example · 2 threats");
    // Opening a model does not hide that another file failed to load.
    expect(status.textContent).toContain("Could not load: bad.yaml (bad)");

    select.value = "tv-hardware-brake-ecu.yaml";
    select.dispatch("change");
    expect(changed).toHaveBeenCalledWith(MODELS[2]);
  });
});

describe("model picker without load problems", () => {
  it("shows only the opened model's summary", () => {
    const select = new FakeElement("select");
    const status = new FakeElement("p");
    const picker = new ModelPicker(
      select as unknown as HTMLSelectElement,
      status as unknown as HTMLElement,
      () => undefined,
      { createElement: (tag: string) => new FakeElement(tag) } as unknown as Document,
    );
    picker.setModels({ count: 1, models: [MODELS[0]], problems: [] });
    expect(status.textContent).toBe("");
    picker.show(MODELS[0]);
    expect(status.textContent).not.toContain("Could not load");
  });
});

class FakeElement {
  children: FakeElement[] = [];
  textContent = "";
  label = "";
  value = "";
  disabled = false;
  innerHTML: string | undefined;
  private readonly listeners = new Map<string, (() => void)[]>();

  constructor(readonly tagName: string) {}

  append(...children: FakeElement[]): void {
    this.children.push(...children);
  }

  replaceChildren(...children: FakeElement[]): void {
    this.children = children;
  }

  addEventListener(type: string, listener: () => void): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  dispatch(type: string): void {
    for (const listener of this.listeners.get(type) ?? []) listener();
  }
}
