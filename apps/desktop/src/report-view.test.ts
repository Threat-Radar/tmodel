import { describe, expect, it, vi } from "vitest";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import { buildModelReport } from "./model-report";
import type { ModelReportInput } from "./model-types";
import { ModelReportView } from "./report-view";
import riskFixture from "./fixtures/risk-mvp-02.json";
import { parseRiskCalculation, RISK_MATRIX, type RiskCalculation } from "./risk-calculation";

const input = mvp02 as unknown as ModelReportInput;

class FakeElement {
  textContent = "";
  className = "";
  hidden = false;
  innerHTML = "";
  children: unknown[] = [];
  value = "";
  disabled = false;
  readonly queries = new Map<string, FakeElement>();
  readonly attributes = new Map<string, string>();
  private readonly listeners = new Map<string, ((event: unknown) => void)[]>();

  addEventListener(type: string, listener: (event: unknown) => void): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  dispatch(type: string, event: unknown = {}): void {
    for (const listener of this.listeners.get(type) ?? []) listener(event);
  }

  replaceChildren(): void {
    this.children = [];
    this.innerHTML = "";
  }

  querySelector(selector: string): FakeElement | null { return this.queries.get(selector) ?? null; }
  setAttribute(name: string, value: string): void { this.attributes.set(name, value); }
}

function harness(calculateRisk?: (file: string, matrix: string) => Promise<RiskCalculation>) {
  const status = new FakeElement();
  const content = new FakeElement();
  const retry = new FakeElement();
  const openPath = vi.fn();
  const retryCallback = vi.fn();
  const view = new ModelReportView(
    {
      status: status as unknown as HTMLElement,
      content: content as unknown as HTMLElement,
      retry: retry as unknown as HTMLButtonElement,
    },
    { openPath, retry: retryCallback, calculateRisk },
  );
  const matrix = new FakeElement();
  const result = new FakeElement();
  const calculate = new FakeElement();
  content.queries.set("[data-risk-matrix]", matrix);
  content.queries.set("[data-risk-result]", result);
  content.queries.set("[data-calculate-risk]", calculate);
  const clickCalculate = () => content.dispatch("click", {
    target: { closest: (selector: string) => selector === "[data-calculate-risk]" ? calculate : null },
  });
  return { view, status, content, retry, openPath, retryCallback, matrix, result, calculate, clickCalculate };
}

// A click target inside the report: `closest` finds the "Open in path view" button.
function clickTarget(pathId: string | null) {
  return {
    target: {
      closest: (selector: string) => (selector === "[data-open-path]" && pathId !== null
        ? { getAttribute: (name: string) => (name === "data-open-path" ? pathId : null) }
        : null),
    },
  };
}

describe("model report view (#208)", () => {
  it("says it is loading a model and clears the previous report", () => {
    const { view, status, content } = harness();
    content.innerHTML = "<p>old report</p>";
    view.loading(input.model);
    expect(status).toMatchObject({ textContent: `Loading ${input.model.title}…`, hidden: false, className: "report-status is-pending" });
    expect(content.innerHTML).toBe("");
    expect(view.currentReport).toBeUndefined();
  });

  it("shows the shared renderer's report with Open in path view buttons, and hides the status", () => {
    const { view, status, content, retry } = harness();
    const report = buildModelReport(input);
    view.show(report);
    expect(view.currentReport).toBe(report);
    expect(content.innerHTML).toContain(`<h2 id="report-title">${input.model.title.replace(/&/g, "&amp;")}</h2>`);
    expect(content.innerHTML).toContain("data-open-path=");
    expect(content.innerHTML).not.toMatch(/<script/i);
    expect(status).toMatchObject({ textContent: "", hidden: true, className: "report-status is-ready" });
    expect(retry.hidden).toBe(true);
  });

  it("opens a path from its button and ignores clicks elsewhere in the report", () => {
    const { content, openPath } = harness();
    content.dispatch("click", clickTarget("attack-path:remote-diag-injection"));
    content.dispatch("click", clickTarget(null));
    expect(openPath).toHaveBeenCalledTimes(1);
    expect(openPath).toHaveBeenCalledWith("attack-path:remote-diag-injection");
  });

  it("shows a failure with Retry, and Retry calls back", () => {
    const { view, status, content, retry, retryCallback } = harness();
    view.show(buildModelReport(input));
    view.failed("Could not open the model: engine stopped");
    expect(status).toMatchObject({ textContent: "Could not open the model: engine stopped", hidden: false, className: "report-status is-error" });
    expect(content.innerHTML).toBe("");
    expect(view.currentReport).toBeUndefined();
    expect(retry.hidden).toBe(false);
    retry.dispatch("click");
    expect(retryCallback).toHaveBeenCalledTimes(1);
  });

  it("hides Retry again once the next model is loading", () => {
    const { view, retry } = harness();
    view.failed("Could not list the example models");
    view.waiting("Waiting for the local engine…");
    expect(retry.hidden).toBe(true);
  });
});

describe("risk calculation controls (#63)", () => {
  const response = parseRiskCalculation(riskFixture, input.model.file, RISK_MATRIX);

  it("requires an explicit selection, then displays a fresh result on each calculation", async () => {
    const request = vi.fn(async () => structuredClone(response));
    const h = harness(request);
    h.view.show(buildModelReport(input));
    h.clickCalculate();
    expect(request).not.toHaveBeenCalled();
    expect(h.result.textContent).toContain("Select a matrix profile");
    h.matrix.value = RISK_MATRIX;
    h.clickCalculate();
    await vi.waitFor(() => expect(h.result.innerHTML).toContain("Safety: 5"));
    expect(request).toHaveBeenCalledWith(input.model.file, RISK_MATRIX);
    expect(h.calculate.disabled).toBe(false);
    expect(h.result.attributes.get("aria-busy")).toBe("false");
    h.clickCalculate();
    await vi.waitFor(() => expect(request).toHaveBeenCalledTimes(2));
  });

  it("clears previous scores on failure and allows retry", async () => {
    const request = vi.fn<() => Promise<RiskCalculation>>()
      .mockResolvedValueOnce(response).mockRejectedValueOnce(new Error("engine unavailable"))
      .mockResolvedValueOnce(response);
    const h = harness(request);
    h.view.show(buildModelReport(input));
    h.matrix.value = RISK_MATRIX;
    h.clickCalculate();
    await vi.waitFor(() => expect(h.result.innerHTML).toContain("Safety: 5"));
    h.clickCalculate();
    await vi.waitFor(() => expect(h.result.textContent).toContain("engine unavailable"));
    expect(h.result.innerHTML).toBe("");
    expect(h.calculate.disabled).toBe(false);
    h.clickCalculate();
    await vi.waitFor(() => expect(h.result.innerHTML).toContain("Safety: 5"));
  });

  it("does not display a late result after another model starts loading", async () => {
    let resolve!: (value: RiskCalculation) => void;
    const request = new Promise<RiskCalculation>((done) => { resolve = done; });
    const h = harness(() => request);
    h.view.show(buildModelReport(input));
    h.matrix.value = RISK_MATRIX;
    h.clickCalculate();
    expect(h.calculate.disabled).toBe(true);
    h.view.loading({ ...input.model, file: "other.yaml" });
    h.result.innerHTML = "new model";
    resolve(response);
    await request;
    await Promise.resolve();
    expect(h.result.innerHTML).toBe("new model");
  });

  it("keeps the chosen matrix and automatically refreshes for the next model", async () => {
    const request = vi.fn(async () => structuredClone(response));
    const h = harness(request);
    h.view.show(buildModelReport(input));
    expect(request).not.toHaveBeenCalled();
    h.matrix.value = RISK_MATRIX;
    h.clickCalculate();
    await vi.waitFor(() => expect(h.result.innerHTML).toContain("Safety: 5"));
    const next = structuredClone(input);
    next.model.file = "other.yaml";
    h.view.loading(next.model);
    h.matrix.value = ""; // A new select element starts empty when the report is rebuilt.
    h.view.show(buildModelReport(next));
    expect(h.matrix.value).toBe(RISK_MATRIX);
    await vi.waitFor(() => expect(request).toHaveBeenLastCalledWith("other.yaml", RISK_MATRIX));
    expect(request).toHaveBeenCalledTimes(2);
  });

  it("remembers a selection without calculating and allows clearing it", () => {
    const request = vi.fn(async () => structuredClone(response));
    const h = harness(request);
    h.view.show(buildModelReport(input));
    const change = () => h.content.dispatch("change", {
      target: { matches: (selector: string) => selector === "[data-risk-matrix]" },
    });
    h.matrix.value = RISK_MATRIX;
    change();
    h.view.loading(input.model);
    h.matrix.value = "";
    h.view.show(buildModelReport(input));
    expect(request).toHaveBeenCalledTimes(1);
    h.result.innerHTML = "previous calculation";
    h.matrix.value = "";
    change();
    expect(h.result.innerHTML).toBe("");
    h.view.loading(input.model);
    h.view.show(buildModelReport(input));
    expect(h.matrix.value).toBe("");
    expect(request).toHaveBeenCalledTimes(1);
  });

  it("ignores the previous model's result after the automatic refresh finishes", async () => {
    let finishOld!: (value: RiskCalculation) => void;
    const old = new Promise<RiskCalculation>((resolve) => { finishOld = resolve; });
    const request = vi.fn<() => Promise<RiskCalculation>>()
      .mockReturnValueOnce(old).mockResolvedValueOnce(response);
    const h = harness(request);
    h.view.show(buildModelReport(input));
    h.matrix.value = RISK_MATRIX;
    h.clickCalculate();
    h.view.loading(input.model);
    h.view.show(buildModelReport(input));
    await vi.waitFor(() => expect(h.result.innerHTML).toContain("Safety: 5"));
    const fresh = h.result.innerHTML;
    finishOld({ ...response, assessments: [], count: 0 });
    await old;
    await Promise.resolve();
    expect(h.result.innerHTML).toBe(fresh);
    expect(h.calculate.disabled).toBe(false);
    expect(h.matrix.disabled).toBe(false);
  });
});
