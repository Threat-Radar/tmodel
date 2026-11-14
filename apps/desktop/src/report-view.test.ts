import { describe, expect, it, vi } from "vitest";
import mvp02 from "./fixtures/report-input-mvp-02.json";
import { buildModelReport } from "./model-report";
import type { ModelReportInput } from "./model-types";
import { ModelReportView } from "./report-view";

const input = mvp02 as unknown as ModelReportInput;

class FakeElement {
  textContent = "";
  className = "";
  hidden = false;
  innerHTML = "";
  children: unknown[] = [];
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
}

function harness() {
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
    { openPath, retry: retryCallback },
  );
  return { view, status, content, retry, openPath, retryCallback };
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
