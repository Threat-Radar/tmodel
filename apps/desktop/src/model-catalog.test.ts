import { describe, expect, it, vi } from "vitest";
import {
  chooseModel,
  EngineModelCatalogProvider,
  MODEL_STORAGE_KEY,
  ModelPicker,
  modelOptionGroups,
  modelSummaryLine,
  modelReviewLabel,
  readRememberedModel,
  rememberModel,
  requestedModel,
  syncModelUrl,
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

  it.each([
    ["model=tcu&file=other.yaml", "tcu"],
    ["model=&file=tcu.yaml", "tcu.yaml"],
    ["model=%20&file=%20tcu.yaml%20", "tcu.yaml"],
    ["model=%20&file=", undefined],
  ])("reads nonempty model references from %s", (query, expected) => {
    expect(requestedModel(new URLSearchParams(query))).toBe(expected);
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

describe("shareable model URLs", () => {
  it("writes the stable model id, preserves other parameters and removes the developer file switch", () => {
    const history = { replaceState: vi.fn() };
    const href = syncModelUrl(
      MODELS[1],
      "https://threat-radar.github.io/tmodel/app/?file=old.yaml&graphSource=fixture",
      history,
    );
    expect(href).toBe("https://threat-radar.github.io/tmodel/app/?graphSource=fixture&model=mvp-02-automotive-ecu");
    expect(history.replaceState).toHaveBeenCalledWith(null, "", new URL(href));
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
    const disclosure = new FakeElement("details");
    const label = new FakeElement("span");
    const summary = new FakeElement("p");
    const picker = new ModelPicker(
      select as unknown as HTMLSelectElement,
      status as unknown as HTMLElement,
      { disclosure: disclosure as unknown as HTMLDetailsElement, label: label as unknown as HTMLElement, summary: summary as unknown as HTMLElement },
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
    expect(summary.textContent).toContain("Core example · 2 threats");
    expect(label.textContent).toBe("1/2 accepted");
    expect(disclosure.hidden).toBe(false);
    expect(disclosure.open).toBe(false);
    // Opening a model does not hide that another file failed to load.
    expect(status.textContent).toContain("Could not load: bad.yaml (bad)");

    select.value = "tv-hardware-brake-ecu.yaml";
    select.dispatch("change");
    expect(changed).toHaveBeenCalledWith(MODELS[2]);
  });
});

describe("model picker without load problems", () => {
  it("keeps routine summary out of the header status line", () => {
    const select = new FakeElement("select");
    const status = new FakeElement("p");
    const disclosure = new FakeElement("details");
    const label = new FakeElement("span");
    const summary = new FakeElement("p");
    const picker = new ModelPicker(
      select as unknown as HTMLSelectElement,
      status as unknown as HTMLElement,
      { disclosure: disclosure as unknown as HTMLDetailsElement, label: label as unknown as HTMLElement, summary: summary as unknown as HTMLElement },
      () => undefined,
      { createElement: (tag: string) => new FakeElement(tag) } as unknown as Document,
    );
    picker.setModels({ count: 1, models: [MODELS[0]], problems: [] });
    expect(status.textContent).toBe("");
    picker.show(MODELS[0]);
    expect(status.textContent).toBe("");
    expect(summary.textContent).toBe(modelSummaryLine(MODELS[0]));
    picker.waiting("Waiting");
    expect(disclosure.hidden).toBe(true);
  });
});

it("distinguishes an unreviewed proposal from a model with no accepted threat reviews", () => {
  const model = MODELS[0];
  const zeroAccepted = { ...model, reviewed_threats: 0, counts: { threats: 2 } };
  expect(modelReviewLabel({ ...zeroAccepted, kind: "proposal" })).toBe("Unreviewed");
  expect(modelReviewLabel(zeroAccepted)).toBe("0/2 accepted");
  expect(modelReviewLabel({ ...zeroAccepted, counts: {} })).toBe("No threats");
});

class FakeElement {
  children: FakeElement[] = [];
  textContent = "";
  label = "";
  value = "";
  disabled = false;
  hidden = false;
  open = false;
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
