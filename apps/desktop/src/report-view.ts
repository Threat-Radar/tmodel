// The app's Model report view (#208): the shared report renderer, placed in the
// report panel, with "Open in path view" buttons wired to the attack-path view.

import type { ModelReport } from "./model-report";
import type { ModelSummary } from "./model-types";
import { renderModelReport } from "./report-render";

export interface ReportViewElements {
  status: HTMLElement;
  content: HTMLElement;
  retry: HTMLButtonElement;
}

export class ModelReportView {
  private report?: ModelReport;

  constructor(
    private readonly elements: ReportViewElements,
    callbacks: { openPath(pathId: string): void; retry(): void },
  ) {
    elements.content.addEventListener("click", (event) => {
      const button = (event.target as Element | null)?.closest?.("[data-open-path]");
      const pathId = button?.getAttribute("data-open-path");
      if (pathId) callbacks.openPath(pathId);
    });
    elements.retry.addEventListener("click", () => callbacks.retry());
  }

  get currentReport(): ModelReport | undefined {
    return this.report;
  }

  waiting(message: string): void {
    this.setStatus(message, "pending");
  }

  loading(model: ModelSummary): void {
    this.report = undefined;
    this.elements.content.replaceChildren();
    this.setStatus(`Loading ${model.title}…`, "pending");
  }

  failed(message: string): void {
    this.report = undefined;
    this.elements.content.replaceChildren();
    this.setStatus(message, "error");
    this.elements.retry.hidden = false;
  }

  show(report: ModelReport): void {
    this.report = report;
    // Every model value is escaped by the shared renderer (safe-html.ts); the
    // markup has no script, no event handler attribute and no external URL.
    this.elements.content.innerHTML = renderModelReport(report, { interactive: true });
    this.setStatus("", "ready");
  }

  private setStatus(message: string, tone: "pending" | "error" | "ready"): void {
    this.elements.status.textContent = message;
    this.elements.status.hidden = message.length === 0;
    this.elements.status.className = `report-status is-${tone}`;
    if (tone !== "error") this.elements.retry.hidden = true;
  }
}
