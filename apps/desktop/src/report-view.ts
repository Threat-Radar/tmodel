// The app's Model report view (#208): the shared report renderer, placed in the
// report panel, with "Open in path view" buttons wired to the attack-path view.

import type { ModelReport } from "./model-report";
import type { ModelSummary } from "./model-types";
import { renderModelReport } from "./report-render";
import { renderRiskCalculation, type RiskCalculation } from "./risk-calculation";

export interface ReportViewElements {
  status: HTMLElement;
  content: HTMLElement;
  retry: HTMLButtonElement;
}

export class ModelReportView {
  private report?: ModelReport;
  private riskRequest = 0;

  constructor(
    private readonly elements: ReportViewElements,
    private readonly callbacks: {
      openPath(pathId: string): void;
      retry(): void;
      calculateRisk?(file: string, matrix: string): Promise<RiskCalculation>;
    },
  ) {
    elements.content.addEventListener("click", (event) => {
      const button = (event.target as Element | null)?.closest?.("[data-open-path]");
      const pathId = button?.getAttribute("data-open-path");
      if (pathId) callbacks.openPath(pathId);
      const calculate = (event.target as Element | null)?.closest?.("[data-calculate-risk]");
      if (calculate) void this.calculateRisk();
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
    this.riskRequest++;
    this.report = undefined;
    this.elements.content.replaceChildren();
    this.setStatus(`Loading ${model.title}…`, "pending");
  }

  failed(message: string): void {
    this.riskRequest++;
    this.report = undefined;
    this.elements.content.replaceChildren();
    this.setStatus(message, "error");
    this.elements.retry.hidden = false;
  }

  show(report: ModelReport): void {
    this.riskRequest++;
    this.report = report;
    // Every model value is escaped by the shared renderer (safe-html.ts); the
    // markup has no script, no event handler attribute and no external URL.
    this.elements.content.innerHTML = renderModelReport(report, {
      interactive: true,
      riskCalculation: Boolean(this.callbacks.calculateRisk),
    });
    this.setStatus("", "ready");
  }

  private async calculateRisk(): Promise<void> {
    const report = this.report;
    const calculate = this.callbacks.calculateRisk;
    const matrix = this.elements.content.querySelector<HTMLSelectElement>("[data-risk-matrix]");
    const result = this.elements.content.querySelector<HTMLElement>("[data-risk-result]");
    const button = this.elements.content.querySelector<HTMLButtonElement>("[data-calculate-risk]");
    if (!report || !calculate || !matrix || !result || !button) return;
    const request = ++this.riskRequest;
    result.replaceChildren();
    if (!matrix.value) {
      result.textContent = "Select a matrix profile before calculating risk.";
      return;
    }
    button.disabled = true;
    matrix.disabled = true;
    result.setAttribute("aria-busy", "true");
    result.textContent = "Calculating risk from recorded inputs…";
    try {
      const calculation = await calculate(report.model.file, matrix.value);
      if (this.riskRequest !== request) return;
      result.innerHTML = renderRiskCalculation(calculation, report);
    } catch (error) {
      if (this.riskRequest !== request) return;
      result.textContent = `Could not calculate risk: ${error instanceof Error ? error.message : String(error)}. Try again.`;
    } finally {
      if (this.riskRequest === request) {
        result.setAttribute("aria-busy", "false");
        button.disabled = false;
        matrix.disabled = false;
      }
    }
  }

  private setStatus(message: string, tone: "pending" | "error" | "ready"): void {
    this.elements.status.textContent = message;
    this.elements.status.hidden = message.length === 0;
    this.elements.status.className = `report-status is-${tone}`;
    if (tone !== "error") this.elements.retry.hidden = true;
  }
}
